# -*- coding: utf-8 -*-
"""Shared VoxCPM text normalization, chunk planning, and audio QC helpers."""

import array
import json
import math
import os
import re
import select
import shutil
import subprocess
import sys
import tempfile
import unicodedata
from difflib import SequenceMatcher

try:
    import numpy as np
except ImportError:  # a stdlib fallback keeps swallowed-syllable checks active
    np = None

DEFAULT_FAST_SWALLOW_DB = -10.0

class FasterWhisperSession:
    """In-process faster-whisper backend (Linux/CUDA, e.g. Kaggle).

    Mirrors ``MLXWhisperSession``'s interface so ``transcribe_word_timestamps``
    can drive either. Unlike ``StrictVerifierSession`` (which shells out to a
    fixed VoxCPM venv), this runs in the current interpreter, so it works
    wherever ``faster_whisper`` is importable. Uses CUDA when available for
    speed, else CPU int8. ``model`` may be a HF id or a local ct2 model dir
    (for fully offline use).
    """

    def __init__(self, device_index=0):
        self._model = None
        self._model_name = None
        self.device = None
        self.compute_type = None
        # Lets callers pin this session to one GPU (e.g. cuda:1) so multiple
        # sessions can run ASR concurrently across GPUs instead of
        # serializing on a single device. Ignored on the CPU fallback.
        self.device_index = device_index

    def _resolve_device(self):
        try:
            import torch
            if torch.cuda.is_available():
                return "cuda", "float16"
        except Exception:
            pass
        return "cpu", "int8"

    def _load(self, model_name):
        if self._model is not None and self._model_name == model_name:
            return self._model
        from faster_whisper import WhisperModel
        self.device, self.compute_type = self._resolve_device()
        kwargs = {"device": self.device, "compute_type": self.compute_type}
        if self.device == "cuda":
            kwargs["device_index"] = self.device_index
        self._model = WhisperModel(model_name, **kwargs)
        self._model_name = model_name
        return self._model

    def transcribe(self, audio, model, word_timestamps=False):
        try:
            whisper_model = self._load(model)
            segments, info = whisper_model.transcribe(
                os.path.abspath(audio),
                language="vi",
                beam_size=5,
                word_timestamps=True,
                vad_filter=True,
                condition_on_previous_text=False,
            )
            payload = {"text": "", "segments": [], "language": info.language}
            texts = []
            for segment in segments:
                texts.append(segment.text)
                payload["segments"].append({
                    "start": segment.start,
                    "end": segment.end,
                    "text": segment.text,
                    "words": [
                        {
                            "word": word.word,
                            "start": word.start,
                            "end": word.end,
                            "probability": word.probability,
                        }
                        for word in (segment.words or [])
                    ],
                })
            payload["text"] = " ".join(texts).strip()
            return payload
        except Exception:
            return None

    def close(self):
        self._model = None

    def __enter__(self):
        return self

    def __exit__(self, _exc_type, _exc, _traceback):
        self.close()

KNOWN_VOICE_REFTEXT = {
    "NGOC HUYEN V2": (
        "Giữa buổi chiều Hà Nội, những cơn gió nhẹ lướt qua hàng cây mang theo "
        "hương hoa sữa thoảng trong không khí. Cô mỉm cười như vừa nhớ lại một "
        "câu chuyện rất xa."
    ),
    "THUY NGUYEN": (
        "Không biết có phải như mọi người nói, gái một con trông mòn con mắt "
        "không, mà mình thấy khi đẻ con, ai cũng khen mình ngon đẹp hẳn ra."
    ),
    "giọng-audio": (
        "Anh sẽ cưới ai? Không ai cả. Anh ngáp một cái, sống một mình. Tại sao? "
        "Một mình vẫn ổn mà, biết đặt đồ ăn, biết dùng máy giặt. Tôi nhìn anh, "
        "vậy anh có thể đi đón Tiểu Điền tan học không? Cả người anh khựng lại "
        "trong thoáng chốc. Sau đó, anh nói ra câu nói mà đến tận bây giờ tôi "
        "vẫn không thể quên. Điều duy nhất khiến anh còn lưu luyến ở em là vì em "
        "đã sinh cho..."
    ),
}

def _decode_samples(wav_path, sample_rate=16000):
    """Mono float samples via ffmpeg. The chunks are float32 WAV, which the
    stdlib wave module refuses ('unknown format: 3'), and ffmpeg is already a
    hard dependency here."""
    try:
        raw = subprocess.run(
            ["ffmpeg", "-v", "error", "-i", wav_path, "-f", "f32le",
             "-ac", "1", "-ar", str(sample_rate), "-"],
            check=True, capture_output=True).stdout
    except (subprocess.CalledProcessError, OSError):
        return None
    if np is not None:
        return np.frombuffer(raw, dtype=np.float32)
    samples = array.array("f")
    samples.frombytes(raw)
    if sys.byteorder != "little":
        samples.byteswap()
    return samples

_ASR_DOT_TIME_RE = re.compile(r"\b(\d{1,2})\.(\d{2})\b(?!\d)")

_ASR_PHONE_RE = re.compile(r"\b0\d[\d .]{5,}\d\b")

def _canonicalize_asr_orthography(text):
    # Only a leading zero, never a grouped amount: "1.500.000" must stay one
    # quantity, while "0912 345 678" is one identifier written with spaces.
    text = _ASR_PHONE_RE.sub(lambda m: re.sub(r"[ .]", "", m.group(0)), text)
    return _ASR_DOT_TIME_RE.sub(r"\1h\2", text)

DEFAULT_ACRONYM_DICT = {
    "TP.HCM": "thành phố Hồ Chí Minh",
    "TP. HCM": "thành phố Hồ Chí Minh",
    "TPHCM": "thành phố Hồ Chí Minh",
    "HCM": "Hồ Chí Minh",
    "TP.": "thành phố",
    "UBND": "ủy ban nhân dân",
    "CSGT": "cảnh sát giao thông",
    "CMND": "chứng minh nhân dân",
    "CCCD": "căn cước công dân",
    "NXB": "nhà xuất bản",
    "PGS.": "phó giáo sư",
    "ThS.": "thạc sĩ",
    "GS.": "giáo sư",
    "TS.": "tiến sĩ",
    "BS.": "bác sĩ",
    "KS.": "kỹ sư",
    "LS.": "luật sư",
    "BV": "bệnh viện",
    "ĐH": "đại học",
    "VN": "Việt Nam",
    # "a đê en", not "a dê en": D is named "dê", but in this (northern) voice
    # "dê" and "giê" (G) are homophones, and the take rendered from "a dê en"
    # came back from Whisper as "A.G.N.". "a đê en" is also what a Vietnamese
    # speaker actually says for ADN, and it round-trips as "ADN".
    "ADN": "a đê en",
    "DNA": "đi en ây",
    "USB": "u ét bê",
    "ATM": "a tê em",
    "GPS": "giê pê ét",
    "SMS": "ét em ét",
    "PDF": "pê đê ép",
    "CEO": "xi i âu",
    "KPI": "ca pi ai",
    "SOS": "ét ô ét",
    "VIP": "víp",
    "TV": "ti vi",
    "PC": "pi xi",
    "CV": "xi vi",
    "MC": "em xi",
    "IT": "ai ti",
    "PR": "pi a",
    "WC": "vê xê",
}

_FRACTION_RE = re.compile(r"(?<![\d./])(\d{1,3})\s*/\s*(\d{1,3})(?![\d./])")

_FULL_DATE_RE = re.compile(r"\b(\d{1,2})\s*([/-])\s*(\d{1,2})\s*\2\s*(\d{4})\b")

_ID_NUMBER_RE = re.compile(r"(?<![\d.,])(0\d+|\d{8,})(?!\d|[.,]\d)")

_NUMBER_RE = re.compile(r"-?\d{1,3}(?:\.\d{3})+(?:,\d+)?|-?\d+(?:,\d+)?")

_PER_RE = re.compile(
    r"\s*/\s*(tháng|năm|ngày|tuần|giờ|phút|giây|người|lần|cái|con|suất)"
    r"(?![\wÀ-ỹ])",
    re.IGNORECASE,
)

_RANGE_RE = re.compile(r"(?<![\d/-])(\d+)\s*[-–]\s*(\d+)(?![\d/-])")

_ROMAN_LEAD = (r"(?:thế\s+kỷ|thế\s+kỉ|chương|phần|quyển|tập|khóa|khoá|lớp|"
               r"kỳ|kì|đợt|mục|điều|khoản|thứ|loại|cấp|đời)")

_ROMAN_RE = re.compile(
    rf"(?i:({_ROMAN_LEAD}))\s+(M{{0,3}}(?:CM|CD|D?C{{0,3}})(?:XC|XL|L?X{{0,3}})"
    r"(?:IX|IV|V?I{0,3}))(?![\wÀ-ỹ])"
)

_DATE_LEAD = r"(?:ngày|mùng|mồng|hôm|sáng|trưa|chiều|tối|đêm|vào|từ|đến|lúc)"

_SHORT_DATE_RE = re.compile(rf"(?i:({_DATE_LEAD}))\s+(\d{{1,2}})\s*/\s*(\d{{1,2}})\b")

_SYMBOL_MAP = {
    "%": " phần trăm ",
    "‰": " phần nghìn ",
    "&": " và ",
    "@": " a còng ",
    "€": " euro ",
    "$": " đô la ",
    "£": " bảng ",
    "¥": " yên ",
    "₫": " đồng ",
    "°": " độ ",
    "×": " nhân ",
    "÷": " chia ",
    "=": " bằng ",
    "±": " cộng trừ ",
    "№": " số ",
}

_TIME_HM_RE = re.compile(r"\b(\d{1,2})\s*(?:h|:|g(?:iờ)?)\s*(\d{2})\b")

_TIME_H_RE = re.compile(r"\b(\d{1,2})h(?![\wÀ-ỹ])")

_UNIT_MAP = [
    ("km/h", "ki lô mét trên giờ"),
    ("m/s", "mét trên giây"),
    ("m2", "mét vuông"),
    ("m3", "mét khối"),
    ("kg", "ki lô gam"),
    ("km", "ki lô mét"),
    ("cm", "xăng ti mét"),
    ("mm", "mi li mét"),
    ("ml", "mi li lít"),
    ("gb", "ghi ga bai"),
    ("mb", "mê ga bai"),
    ("kb", "ki lô bai"),
    ("vnđ", "đồng"),
    ("vnd", "đồng"),
    ("usd", "đô la Mỹ"),
    ("m", "mét"),
    ("đ", "đồng"),
    # "50k" (năm mươi nghìn) is common enough in this register to be worth the
    # rare "4K" it misreads; it only fires when attached to the digits.
    ("k", "nghìn"),
]

_UNIT_RE = re.compile(
    r"(?<![\wÀ-ỹ])(-?\d[\d.,]*)\s*(" + "|".join(
        re.escape(unit) for unit, _ in _UNIT_MAP
    ) + r")(?![\wÀ-ỹ])",
    re.IGNORECASE,
)

_VI_UNITS = ["không", "một", "hai", "ba", "bốn", "năm", "sáu", "bảy", "tám", "chín"]

def _read_three_digits(number, prepend_zero_hundred):
    hundreds, remainder = divmod(number, 100)
    tens, units = divmod(remainder, 10)
    words = []

    if hundreds > 0 or prepend_zero_hundred:
        words.append(_VI_UNITS[hundreds])
        words.append("trăm")

    if tens == 0:
        if units > 0 and (hundreds > 0 or prepend_zero_hundred):
            words.append("lẻ")
            words.append(_VI_UNITS[units])
        elif units > 0:
            words.append(_VI_UNITS[units])
    elif tens == 1:
        words.append("mười")
        if units == 5:
            words.append("lăm")
        elif units > 0:
            words.append(_VI_UNITS[units])
    else:
        words.append(_VI_UNITS[tens])
        words.append("mươi")
        if units == 1:
            words.append("mốt")
        elif units == 5:
            words.append("lăm")
        elif units > 0:
            words.append(_VI_UNITS[units])

    return words

def number_to_vietnamese(number):
    """Convert a non-negative integer to Vietnamese words."""
    if number == 0:
        return "không"

    scales = ["", "nghìn", "triệu", "tỷ"]
    groups = []
    while number > 0:
        number, group = divmod(number, 1000)
        groups.append(group)

    words = []
    highest = len(groups) - 1
    for idx in range(highest, -1, -1):
        group = groups[idx]
        if group == 0:
            continue
        words.extend(_read_three_digits(group, prepend_zero_hundred=idx != highest))
        if scales[idx]:
            words.append(scales[idx])

    return " ".join(words)

def _spell_int(value):
    return number_to_vietnamese(int(value))

def _read_date(match):
    day, _sep, month, year = match.groups()
    if not (1 <= int(day) <= 31 and 1 <= int(month) <= 12):
        return match.group(0)
    return (f" {_spell_int(day)} tháng {_spell_int(month)} "
            f"năm {_spell_int(year)} ")

def _read_short_date(match):
    lead, day, month = match.groups()
    if not (1 <= int(day) <= 31 and 1 <= int(month) <= 12):
        return match.group(0)
    return f"{lead} {_spell_int(day)} tháng {_spell_int(month)} "

def _read_time_hm(match):
    hour, minute = match.groups()
    if not (int(hour) <= 23 and int(minute) <= 59):
        return match.group(0)
    return f" {_spell_int(hour)} giờ {_spell_int(minute)} "

_UNIT_LOOKUP = {unit: spoken for unit, spoken in _UNIT_MAP}

def _spell_number_token(token):
    """Turn a numeric token (possibly with grouping/decimal) into VI words."""
    sign = ""
    if token.startswith("-"):
        sign = "âm "
        token = token[1:]

    # Vietnamese convention: '.' groups thousands, ',' is the decimal separator.
    integer_part, _, decimal_part = token.partition(",")
    integer_part = integer_part.replace(".", "")

    if not integer_part.isdigit():
        return None

    words = number_to_vietnamese(int(integer_part))
    if decimal_part and decimal_part.isdigit():
        words += " phẩy " + " ".join(_VI_UNITS[int(d)] for d in decimal_part)
    return sign + words

def _read_unit(match):
    quantity, unit = match.groups()
    spelled = _spell_number_token(quantity)
    if spelled is None:
        return match.group(0)
    return f" {spelled} {_UNIT_LOOKUP[unit.lower()]} "

_ROMAN_VALUES = [("M", 1000), ("CM", 900), ("D", 500), ("CD", 400),
                 ("C", 100), ("XC", 90), ("L", 50), ("XL", 40),
                 ("X", 10), ("IX", 9), ("V", 5), ("IV", 4), ("I", 1)]

def _roman_to_int(numeral):
    value, index = 0, 0
    for symbol, amount in _ROMAN_VALUES:
        while numeral.startswith(symbol, index):
            value += amount
            index += len(symbol)
    return value

def apply_acronym_dict(text, acronym_dict):
    """Expand known Latin acronyms, longest key first and case-sensitively."""
    for term in sorted(acronym_dict, key=len, reverse=True):
        # A key ending in "." consumes that dot; one that does not must still
        # not fire inside a longer word ("TV" in "TVs", "VN" in "VNese").
        tail = "" if term.endswith(".") else r"(?![\wÀ-ỹ])"
        pattern = re.compile(r"(?<![\wÀ-ỹ])" + re.escape(term) + tail)
        text = pattern.sub(acronym_dict[term], text)
    return text

def spell_digits(token):
    """Read a digit run one digit at a time, the way a phone number is said."""
    return " ".join(_VI_UNITS[int(char)] for char in token if char.isdigit())

def normalize_vietnamese_numerals(text, acronym_dict=None):
    """Rewrite numerals, dates, times, units and acronyms as spoken Vietnamese.

    Order is load-bearing: each rule consumes a pattern the next one would
    otherwise misread. Dates claim their slashes before the fraction rule sees
    them, ranges claim their dash before the generic number rule reads it as a
    minus, and units claim their digits while those digits are still digits.
    """
    if acronym_dict is None:
        acronym_dict = DEFAULT_ACRONYM_DICT

    text = _FULL_DATE_RE.sub(_read_date, text)
    text = _SHORT_DATE_RE.sub(_read_short_date, text)
    text = _TIME_HM_RE.sub(_read_time_hm, text)
    text = _TIME_H_RE.sub(
        lambda m: f" {_spell_int(m.group(1))} giờ " if int(m.group(1)) <= 23
        else m.group(0), text
    )
    text = _RANGE_RE.sub(
        lambda m: f" {_spell_int(m.group(1))} đến {_spell_int(m.group(2))} ", text
    )
    text = _PER_RE.sub(lambda m: f" mỗi {m.group(1)}", text)
    text = _FRACTION_RE.sub(
        lambda m: f" {_spell_int(m.group(1))} phần {_spell_int(m.group(2))} ", text
    )
    text = _UNIT_RE.sub(_read_unit, text)
    text = _ID_NUMBER_RE.sub(lambda m: f" {spell_digits(m.group(1))} ", text)
    text = _ROMAN_RE.sub(
        lambda m: f"{m.group(1)} {number_to_vietnamese(_roman_to_int(m.group(2)))}",
        text,
    )
    text = apply_acronym_dict(text, acronym_dict)

    for symbol, spoken in _SYMBOL_MAP.items():
        text = text.replace(symbol, spoken)

    # Whatever digits are left are plain quantities.
    def _num_sub(match):
        spelled = _spell_number_token(match.group(0))
        return f" {spelled} " if spelled is not None else match.group(0)

    return _NUMBER_RE.sub(_num_sub, text)

def _normalize_for_compare(text):
    text = unicodedata.normalize("NFC", text)
    # Case-sensitive acronyms must expand before the lower-casing below.
    text = normalize_vietnamese_numerals(_canonicalize_asr_orthography(text))
    text = re.sub(r"[^\wÀ-ỹ\s]", " ", text.lower())
    return re.sub(r"\s+", " ", text).strip()

def cer_from_words(expected_text, words):
    """Vietnamese character error rate after normalizing both ASR sides."""
    expected = _normalize_for_compare(expected_text)
    heard = _normalize_for_compare(" ".join(word.get("word", "") for word in words))
    if not expected:
        return 0.0 if not heard else 1.0
    previous = list(range(len(heard) + 1))
    for row_index, expected_char in enumerate(expected, start=1):
        current = [row_index]
        for col_index, heard_char in enumerate(heard, start=1):
            current.append(min(
                current[-1] + 1,
                previous[col_index] + 1,
                previous[col_index - 1] + (expected_char != heard_char),
            ))
        previous = current
    return previous[-1] / len(expected)

def clean_markdown(text):
    """
    Cleans markdown formatting to leave only text for TTS.
    """
    # Remove metadata lines like *Thể loại...* or ---
    text = re.sub(r'^\*Thể loại.*$', '', text, flags=re.MULTILINE)
    text = re.sub(r'^---.*$', '', text, flags=re.MULTILINE)

    # Remove bold/italic markdown symbols
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    text = re.sub(r'\*(.*?)\*', r'\1', text)
    text = re.sub(r'_(.*?)_', r'\1', text)

    # Normalize line endings first so we can preserve paragraph rhythm.
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    paragraphs = []
    for raw_paragraph in re.split(r"\n\s*\n+", text):
        lines = [re.sub(r"\s+", " ", line).strip() for line in raw_paragraph.split("\n")]
        paragraph = " ".join(line for line in lines if line)
        if paragraph:
            paragraphs.append(paragraph)

    return "\n\n".join(paragraphs).strip()

def ensure_terminal_punctuation(text):
    """Give each chunk a closing mark so prosody resolves (fewer trailing artifacts)."""
    stripped = text.rstrip()
    # Clause splitting deliberately leaves a comma/semicolon/colon at a
    # continuation boundary.  Appending a full stop produced malformed `,.`
    # text in the actual v3 plan; the clause mark is already an audible and
    # valid terminal cue for this render fragment.
    if stripped and stripped[-1] not in ".!?…,:;\"'”’":
        return stripped + "."
    return stripped

def faster_whisper_available():
    try:
        import importlib.util
        return importlib.util.find_spec("faster_whisper") is not None
    except Exception:
        return False

def apply_pronunciation_dict(text, pron_dict):
    if not pron_dict:
        return text
    for term, spoken in pron_dict.items():
        pattern = re.compile(r"(?<![\wÀ-ỹ])" + re.escape(term) + r"(?![\wÀ-ỹ])", re.IGNORECASE)
        def replacement(match):
            rendered = spoken
            if (
                term[:1].islower()
                and match.group(0)[:1].isupper()
                and rendered[:1].islower()
            ):
                rendered = rendered[0].upper() + rendered[1:]
            return rendered
        text = pattern.sub(replacement, text)
    return text

def clarify_punctuation(text):
    """Leave only punctuation VoxCPM can turn into prosody.

    Anything else is either read aloud as a word or silently ignored, and a mark
    that is ignored is worse than one that is absent: the clause it was meant to
    break runs on, and a long unbroken clause is where the tempo drifts.
    """
    # A dash opening a line is a dialogue/list marker, not speech.
    text = re.sub(r"^[ \t]*[-–—]+[ \t]*", "", text, flags=re.MULTILINE)
    # A dash set off by spaces is parenthetical: it is a comma out loud.
    text = re.sub(r"\s+[-–—]+\s+", ", ", text)
    # An em/en dash is parenthetical even unspaced ("hôn—trước"), and it is the
    # one mark this repo's scripts actually use (30 occurrences).
    text = re.sub(r"\s*[–—]+\s*", ", ", text)
    # A plain hyphen, by contrast, joins one word ("cà-phê"). Digits are already
    # claimed by the range rule, so this only ever touches letters.
    text = re.sub(r"(?<=[^\W\d_])-(?=[^\W\d_])", " ", text)
    # Parentheses carry no prosody of their own, so the aside is delivered flat
    # and glued to its neighbours; commas make it an audible aside.
    text = re.sub(r"\s*[(\[]\s*", ", ", text)
    text = re.sub(r"\s*[)\]]\s*", ", ", text)
    # Any surviving slash would be voiced; the words around it are the content.
    text = re.sub(r"\s*/\s*", " ", text)
    # Punctuation that ran together after the rewrites above.
    text = re.sub(r",\s*(?=[.,!?;:…])", "", text)
    text = re.sub(r"(?<=[.!?…])\s*,", "", text)
    # A mark with no space after it reads as one long token.
    return re.sub(r"(?<=[.,!?;:])(?=[^\s\d.,!?;:\"'”’)\]])", " ", text)

def strip_uncommon_characters(text):
    """Drop characters the model cannot voice (emoji, control chars, exotic symbols)."""
    result = []
    for ch in text:
        if ch in "\n\t":
            result.append(ch)
            continue
        category = unicodedata.category(ch)
        # Keep letters, marks (Vietnamese diacritics), numbers, spaces, and the
        # punctuation we explicitly rely on. Drop symbols/emoji/control chars.
        if category[0] in ("L", "M", "N", "Z"):
            result.append(ch)
        elif ch in ".,!?;:…\"'-":
            result.append(ch)
        else:
            result.append(" ")
    return "".join(result)

def normalize_for_tts(text, pron_dict=None, acronym_dict=None):
    """
    Normalize text so VoxCPM mispronounces/skips fewer words:
    unicode NFC, spoken-form rewrites for numerals/dates/times/units/acronyms,
    pronunciation dictionary, punctuation cleanup, and junk-character stripping.
    """
    text = unicodedata.normalize("NFC", text)

    # Normalize quotes/ellipsis so prosody is predictable. Dashes are handled in
    # clarify_punctuation, after the numeral rules have claimed theirs.
    text = text.replace("“", '"').replace("”", '"').replace("‘", "'").replace("’", "'")
    text = re.sub(r"\.{3,}", "…", text)
    text = re.sub(r"…{2,}", "…", text)

    # First, so a user override beats the built-in reading of the same term.
    text = apply_pronunciation_dict(text, pron_dict)
    text = normalize_vietnamese_numerals(text, acronym_dict)
    text = clarify_punctuation(text)
    text = strip_uncommon_characters(text)

    # Collapse repeated punctuation and whitespace introduced above.
    text = re.sub(r"([!?,;:])\1{1,}", r"\1", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r" *\n *", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"\s+([.,!?;:…])", r"\1", text)
    return text.strip()

def _within_limits(text, max_chars, max_words):
    return len(text) <= max_chars and len(text.split()) <= max_words

def _merge_short_chunks(chunks, max_chars, max_words, min_words):
    """Merge chunks shorter than ``min_words`` into an adjacent chunk.

    Isolated short chunks (a bare name or a two-word line of dialogue) make the
    VoxCPM ``RuleDurationEstimator`` hit its low-duration floor, which
    over-allocates time and forces the model to stretch the speech into a
    dragged, too-slow read. Merging them into a neighbor keeps every chunk above
    the floor. Never exceeds the max limits; a short chunk wedged between two
    already-full neighbors is left as-is rather than breaking the caps. The
    merged chunk keeps the ``sep_before`` of whichever text ends up first, since
    that is the boundary the stitcher still has to voice.
    """
    if min_words <= 0 or len(chunks) <= 1:
        return chunks
    merged = [dict(chunk) for chunk in chunks]
    changed = True
    while changed and len(merged) > 1:
        changed = False
        for i, chunk in enumerate(merged):
            if len(chunk["text"].split()) >= min_words:
                continue
            prev_join = f"{merged[i - 1]['text']}\n\n{chunk['text']}" if i > 0 else None
            next_join = f"{chunk['text']}\n\n{merged[i + 1]['text']}" if i < len(merged) - 1 else None
            if prev_join is not None and _within_limits(prev_join, max_chars, max_words):
                merged[i - 1]["text"] = prev_join
                del merged[i]
                changed = True
                break
            if next_join is not None and _within_limits(next_join, max_chars, max_words):
                chunk["text"] = next_join
                del merged[i + 1]
                changed = True
                break
            # neither neighbor can absorb it without exceeding caps: leave as-is
    return merged

def _classify_boundary(prev_piece, next_piece):
    if next_piece["starts_mid"]:
        return "cont"
    if next_piece["para_index"] != prev_piece["para_index"]:
        return "scene" if next_piece["scene_before"] else "para"
    return "sent"

_NUMBER_WORDS = {
    "không", "một", "hai", "ba", "bốn", "năm", "sáu", "bảy", "tám", "chín",
    "mười", "trăm", "nghìn", "triệu", "tỷ", "phẩy", "phần", "tháng", "giờ", "đồng",
}

def _difficulty_scale(text):
    """Return a conservative 0.6-1.0 packing scale for difficult narration."""
    stripped = text.strip()
    if not stripped:
        return 1.0
    chars = max(len(stripped), 1)
    words = re.findall(r"[\wÀ-ỹ]+", stripped, flags=re.UNICODE)
    clause_density = len(re.findall(r"[,;:]|\b(?:nhưng|mà|vì|nên|nếu|khi|rồi)\b", stripped, re.IGNORECASE)) * 100.0 / chars
    proper_names = sum(
        1 for index, word in enumerate(words)
        if index > 0 and len(word) > 1 and word[:1].isupper() and not word.isupper()
    )
    number_tokens = sum(word.lower() in _NUMBER_WORDS for word in words)
    sentence_lengths = [len(piece.strip()) for piece in re.split(r"[.!?…]+", stripped) if piece.strip()]
    longest_sentence = max(sentence_lengths, default=0)
    penalty = min(0.16, max(0.0, clause_density - 1.5) * 0.035)
    penalty += min(0.10, proper_names * 0.025)
    penalty += min(0.10, number_tokens * 0.0125)
    if longest_sentence > 220:
        penalty += min(0.14, (longest_sentence - 220) / 900.0)
    return max(0.6, min(1.0, 1.0 - penalty))

def is_standalone_dialogue(text):
    stripped = text.strip()
    if len(stripped) > 120:
        return False
    return (
        (stripped.startswith('"') and stripped.endswith('"'))
        or (stripped.startswith("“") and stripped.endswith("”"))
        or (stripped.startswith("'") and stripped.endswith("'"))
    )

def _pack_pieces_into_chunks(pieces, max_chars, max_words, adaptive=False):
    """Pack pieces into chunks (legacy phase 2), tagging each boundary."""
    groups = []
    current = []
    current_text = ""
    for piece in pieces:
        if is_standalone_dialogue(piece["text"]):
            if current:
                groups.append(current)
                current = []
                current_text = ""
            groups.append([piece])
            continue
        if not current:
            current = [piece]
            current_text = piece["text"]
            continue
        candidate = f"{current_text}\n\n{piece['text']}"
        scale = min(_difficulty_scale(item["text"]) for item in [*current, piece]) if adaptive else 1.0
        effective_chars = max(1, int(max_chars * scale))
        effective_words = max(1, int(max_words * scale))
        if _within_limits(candidate, effective_chars, effective_words) and not is_standalone_dialogue(current_text):
            current.append(piece)
            current_text = candidate
        else:
            groups.append(current)
            current = [piece]
            current_text = piece["text"]
    if current:
        groups.append(current)

    chunks = []
    prev_last = None
    for group in groups:
        sep = "start" if prev_last is None else _classify_boundary(prev_last, group[0])
        chunks.append({
            "text": "\n\n".join(piece["text"] for piece in group),
            "sep_before": sep,
        })
        prev_last = group[-1]
    return chunks

def _pack_units_into_pieces(units, max_chars, max_words):
    """Pack units into pieces without crossing paragraphs (legacy phase 1)."""
    pieces = []
    state = {"text": "", "meta": None, "para": None}

    def flush():
        if state["text"]:
            pieces.append({**state["meta"], "text": state["text"]})
        state["text"] = ""
        state["meta"] = None

    def start(unit):
        state["text"] = unit["text"]
        state["meta"] = {
            "para_index": unit["para_index"],
            "scene_before": unit["scene_before"],
            "starts_mid": unit["mid"],
        }
        state["para"] = unit["para_index"]

    for unit in units:
        if state["text"] and unit["para_index"] != state["para"]:
            flush()
        if not state["text"]:
            start(unit)
            continue
        candidate = f"{state['text']} {unit['text']}"
        if _within_limits(candidate, max_chars, max_words):
            state["text"] = candidate
        else:
            flush()
            start(unit)
    flush()
    return pieces

SCENE_DIVIDER_RE = re.compile(r"^[\s*_=~•·⁂—–]{3,}$")

def _is_scene_divider(paragraph):
    stripped = paragraph.strip()
    if not stripped or len(stripped) > 12:
        return False
    if not SCENE_DIVIDER_RE.match(stripped):
        return False
    return any(ch in stripped for ch in "*_=~⁂")

def _paragraph_blocks(text):
    """Split into rendered paragraphs, tagging scene breaks.

    Divider-only paragraphs (``* * *``/``⁂``) are dropped from the spoken text
    and instead mark the FOLLOWING paragraph as a scene break, so the stitcher
    can open a longer pause there.
    """
    blocks = []
    para_index = 0
    scene_pending = False
    for raw in re.split(r"\n\s*\n+", text):
        stripped = raw.strip()
        if not stripped:
            continue
        if _is_scene_divider(stripped):
            scene_pending = True
            continue
        blocks.append((para_index, scene_pending, stripped))
        para_index += 1
        scene_pending = False
    return blocks

def split_long_sentence(sentence, max_chars, max_words=None):
    def within_limits(value):
        return (len(value) <= max_chars
                and (max_words is None or max_words <= 0
                     or len(value.split()) <= max_words))

    if within_limits(sentence):
        return [sentence]

    parts = re.split(r"(?<=[,;:])\s+", sentence)
    chunks = []
    current = ""

    for part in parts:
        if not current:
            current = part
            continue

        candidate = f"{current} {part}"
        if within_limits(candidate):
            current = candidate
        else:
            chunks.append(current)
            current = part

    if current:
        chunks.append(current)

    # Very long comma-free text still needs a hard fallback.
    final_chunks = []
    for chunk in chunks:
        if within_limits(chunk):
            final_chunks.append(chunk)
            continue

        words = chunk.split()
        current = ""
        for word in words:
            candidate = f"{current} {word}".strip()
            if within_limits(candidate):
                current = candidate
            else:
                if current:
                    final_chunks.append(current)
                current = word
        if current:
            final_chunks.append(current)

    return final_chunks

SENTENCE_END_RE = re.compile(r'(?<=[.!?。！？…])["”’\']?\s+')

def split_paragraph_into_sentences(paragraph):
    return [sentence.strip() for sentence in SENTENCE_END_RE.split(paragraph) if sentence.strip()]

def _sentence_units(text, max_chars, max_words):
    """Flatten text into sentence-sized units carrying paragraph/continuation tags."""
    units = []
    for para_index, scene_before, paragraph in _paragraph_blocks(text):
        first_unit_in_para = True
        for sentence in split_paragraph_into_sentences(paragraph):
            for frag_index, fragment in enumerate(split_long_sentence(sentence, max_chars, max_words)):
                units.append({
                    "text": fragment,
                    "para_index": para_index,
                    "scene_before": scene_before and first_unit_in_para,
                    "mid": frag_index > 0,
                })
                first_unit_in_para = False
    return units

def plan_chunks(text, max_chars, max_words, min_words=0, adaptive=False):
    """Chunk text and tag each chunk with its boundary type (``sep_before``).

    Returns ``[{"text", "sep_before"}, ...]``. ``split_text_into_chunks``
    delegates here; the extra metadata lets the stitcher place silence by
    narrative role (mid-sentence continuation, sentence, paragraph, scene) so
    pauses land rhythmically instead of after every chunk. Sizing is identical
    to the legacy chunker — only the boundary tags are new.
    """
    if max_chars <= 0:
        return [{"text": text, "sep_before": "start"}]

    units = _sentence_units(text, max_chars, max_words)
    pieces = _pack_units_into_pieces(units, max_chars, max_words)
    chunks = _pack_pieces_into_chunks(pieces, max_chars, max_words, adaptive=adaptive)
    chunks = _merge_short_chunks(chunks, max_chars, max_words, min_words)
    chunks = [
        {"text": ensure_terminal_punctuation(chunk["text"]), "sep_before": chunk["sep_before"]}
        for chunk in chunks
        if chunk["text"].strip()
    ]
    if not chunks:
        return [{"text": ensure_terminal_punctuation(text), "sep_before": "start"}]
    chunks[0]["sep_before"] = "start"
    return chunks

_COLLAPSED_NUMERAL_RE = re.compile(r"\d\d")

def _is_collapsed_numeral(word):
    return bool(_COLLAPSED_NUMERAL_RE.search(word.get("word", "")))

def _run_whisper(
        mlx_bin, wav_path, model, tmp, word_timestamps=False, transcriber=None):
    """Transcribe one file; returns the parsed payload, or None on failure."""
    if transcriber is not None:
        payload = transcriber.transcribe(wav_path, model, word_timestamps)
        if payload is not None:
            return payload if word_timestamps else payload.get("text", "")

    fmt = "json" if word_timestamps else "txt"
    cmd = [mlx_bin, wav_path, "--model", model, "--language", "vi",
           "--output-dir", tmp, "--output-name", "asr", "--output-format", fmt]
    if word_timestamps:
        cmd += ["--word-timestamps", "True"]
    out_path = os.path.join(tmp, f"asr.{fmt}")
    # MLX occasionally exits during model/device startup in a long audit even
    # though the next fresh process succeeds. Retry once before declaring the
    # verifier unavailable; acceptance still fails closed if both attempts fail.
    for _attempt in range(2):
        try:
            subprocess.run(cmd, check=True, capture_output=True, text=True)
            break
        except (subprocess.CalledProcessError, OSError):
            if os.path.exists(out_path):
                os.unlink(out_path)
    else:
        return None
    if not os.path.exists(out_path):
        return None
    with open(out_path, "r", encoding="utf-8") as fh:
        return json.load(fh) if word_timestamps else fh.read()

VOXCPM_TTS_ROOT = os.environ.get(
    "VOXCPM_TTS_ROOT",
    os.path.expanduser("~/voxcpm-tts"),
)

VOXCPM_TTS_VENV_BIN = os.path.join(VOXCPM_TTS_ROOT, ".venv", "bin")

def _whisper_bin():
    mlx_bin = os.path.join(VOXCPM_TTS_VENV_BIN, "mlx_whisper")
    if os.path.exists(mlx_bin):
        return mlx_bin
    return shutil.which("mlx_whisper")

ISOLATION_MIN_GAP = 0.16

def isolation_windows(words, duration, min_gap=ISOLATION_MIN_GAP):
    """Split points at the midpoint of each silence gap, so no phoneme is clipped."""
    cuts = [0.0]
    for current, following in zip(words, words[1:]):
        if following["start"] - current["end"] >= min_gap:
            cuts.append((current["end"] + following["start"]) / 2.0)
    cuts.append(duration)
    return [(start, end) for start, end in zip(cuts, cuts[1:]) if end - start > 0.25]

def probe_duration(path):
    try:
        out = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "csv=p=0", path],
            check=True, capture_output=True, text=True,
        )
        return float(out.stdout.strip())
    except (subprocess.CalledProcessError, ValueError):
        return 0.0

def clause_asr_transcript(wav_path, model, transcriber=None, payload=None):
    """Return a clause-isolated transcript, or None when verification fails."""
    mlx_bin = _whisper_bin()
    if not mlx_bin:
        return None

    with tempfile.TemporaryDirectory() as tmp:
        if payload is None:
            payload = _run_whisper(
                mlx_bin, wav_path, model, tmp, word_timestamps=True,
                transcriber=transcriber,
            )
        if not payload:
            return None
        words = [word for segment in payload.get("segments", [])
                 for word in segment.get("words", [])]
        if not words:
            return None

        pieces = []
        for index, (start, end) in enumerate(
                isolation_windows(words, probe_duration(wav_path))):
            snippet = os.path.join(tmp, f"clause{index}.wav")
            try:
                subprocess.run(
                    ["ffmpeg", "-v", "error", "-y", "-i", wav_path,
                     "-ss", f"{start:.3f}", "-to", f"{end:.3f}", snippet],
                    check=True, capture_output=True,
                )
            except subprocess.CalledProcessError:
                return None
            clause_dir = os.path.join(tmp, f"c{index}")
            os.makedirs(clause_dir, exist_ok=True)
            text = _run_whisper(
                mlx_bin, snippet, model, clause_dir, transcriber=transcriber
            )
            if text is None:
                return None
            pieces.append(text.strip())

    if not pieces:
        return None
    return " ".join(pieces)

def asr_similarity(
        wav_path, expected_text, model, transcriber=None, payload=None):
    """Clause-isolated ASR round-trip similarity versus expected text."""
    heard = clause_asr_transcript(
        wav_path, model, transcriber=transcriber, payload=payload
    )
    if heard is None:
        return None
    return SequenceMatcher(
        None, _normalize_for_compare(expected_text),
        _normalize_for_compare(heard),
    ).ratio()

def isolation_windows_in_span(words, start, end, min_gap=ISOLATION_MIN_GAP):
    """Split one chunk-sized span at silence gaps inside its word timings."""
    cuts = [start]
    for current, following in zip(words, words[1:]):
        if following["start"] - current["end"] >= min_gap:
            cuts.append((current["end"] + following["start"]) / 2.0)
    cuts.append(end)
    return [(lo, hi) for lo, hi in zip(cuts, cuts[1:]) if hi - lo > 0.25]

def clause_asr_transcript_span(
        wav_path, model, words, start, end, transcriber=None):
    """Clause-isolated transcript for a span inside an assembled audio file."""
    mlx_bin = _whisper_bin()
    if not mlx_bin:
        return None
    duration = probe_duration(wav_path)
    start = max(0.0, start)
    end = min(end, duration) if duration else end
    if end - start <= 0.25:
        return None

    with tempfile.TemporaryDirectory() as tmp:
        pieces = []
        for index, (lo, hi) in enumerate(
                isolation_windows_in_span(words, start, end)):
            snippet = os.path.join(tmp, f"span_clause{index}.wav")
            try:
                subprocess.run(
                    ["ffmpeg", "-v", "error", "-y", "-i", wav_path,
                     "-ss", f"{lo:.3f}", "-to", f"{hi:.3f}", snippet],
                    check=True, capture_output=True,
                )
            except subprocess.CalledProcessError:
                return None
            clause_dir = os.path.join(tmp, f"c{index}")
            os.makedirs(clause_dir, exist_ok=True)
            text = _run_whisper(
                mlx_bin, snippet, model, clause_dir, transcriber=transcriber
            )
            if text is None:
                return None
            pieces.append(text.strip())

    return " ".join(piece for piece in pieces if piece)

def asr_similarity_span(
        wav_path, expected_text, model, words, start, end, transcriber=None):
    """Clause-isolated ASR similarity for one chunk span in assembled audio."""
    heard = clause_asr_transcript_span(
        wav_path, model, words, start, end, transcriber=transcriber
    )
    if heard is None:
        return None
    return SequenceMatcher(
        None, _normalize_for_compare(expected_text),
        _normalize_for_compare(heard),
    ).ratio()

def local_tempo_defect(
        words, window_words=5, min_wps=2.5, max_wps=6.75, split_gap=0.3):
    """Return an implausibly slow/fast local window using VI words per second."""
    if window_words < 2:
        return None
    groups, current = [], []
    for word in words:
        # A collapsed numeral ends the run rather than joining it: its span is
        # many syllables, so any window containing it reads as far too slow.
        if _is_collapsed_numeral(word):
            if current:
                groups.append(current)
                current = []
            continue
        if current and word["start"] - current[-1]["end"] >= split_gap:
            groups.append(current)
            current = []
        current.append(word)
    if current:
        groups.append(current)

    windows = []
    for group in groups:
        for index in range(len(group) - window_words + 1):
            sample = group[index:index + window_words]
            span = sample[-1]["end"] - sample[0]["start"]
            if span > 0:
                windows.append((window_words / span, sample))
    if not windows:
        return None

    fastest = max(windows, key=lambda item: item[0])
    slowest = min(windows, key=lambda item: item[0])
    if fastest[0] > max_wps:
        return "fast", fastest[0], " ".join(
            word["word"].strip() for word in fastest[1]
        )
    if slowest[0] < min_wps:
        return "slow", slowest[0], " ".join(
            word["word"].strip() for word in slowest[1]
        )
    return None

def median(values):
    ordered = sorted(values)
    if not ordered:
        return None
    middle = len(ordered) // 2
    if len(ordered) % 2:
        return ordered[middle]
    return (ordered[middle - 1] + ordered[middle]) / 2.0

def low_confidence_word(
        words, probability_floor=0.88, duration_ratio_floor=1.7,
        expected_text=None):
    """Return a suspicious stretched word, or None.

    Whisper often repairs a malformed word from sentence context, so transcript
    equality alone misses it. On reported chunk 0035 it still emitted ``sẽ``
    but with probability 0.856 and a duration 1.8x the chunk median. Requiring
    both signals avoids retrying ordinary low-confidence proper names.
    """
    spans = [word["end"] - word["start"] for word in words
             if word["end"] > word["start"] and not _is_collapsed_numeral(word)]
    typical = median(spans)
    if not typical:
        return None
    clause_initial = set()
    if expected_text:
        clause_initial = {
            _normalize_for_compare(match.group(1))
            for match in re.finditer(
                r"[,;:]\s*[\"']?([\wÀ-ỹ]+)", expected_text,
                flags=re.IGNORECASE,
            )
        }
    candidates = []
    for index, word in enumerate(words):
        if _is_collapsed_numeral(word):
            continue
        probability = word.get("probability")
        span = word["end"] - word["start"]
        ratio = span / typical
        spoken = _normalize_for_compare(word.get("word", ""))
        # Word timestamps around a real pause often absorb part of that pause,
        # making the first word of a clause look both long and uncertain. That
        # is segmentation noise, not malformed speech; the clause ASR path is
        # responsible for checking those boundaries.
        previous_gap = (
            word["start"] - words[index - 1]["end"] if index else float("inf")
        )
        if (spoken and probability is not None
                and probability < probability_floor
                and ratio >= duration_ratio_floor
                and previous_gap < ISOLATION_MIN_GAP
                and spoken not in clause_initial):
            candidates.append((probability, -ratio, spoken, ratio, word["start"]))
    if not candidates:
        return None
    probability, _negative_ratio, spoken, ratio, start = min(candidates)
    return probability, spoken, ratio, start

def swallowed_syllable(wav_path, words, sample_rate=16000, hop=160, frame=1024):
    """Loudest point of the most under-articulated syllable, in dB vs the
    chunk's own median syllable. Returns (deviation, word, start) or None.

    This is the third defect class, and neither of the other checks can see it:
    the words are all present (so the word-diff is clean) and the timing is
    even (so nothing is dropped or dragged) — the model simply mumbles one
    syllable almost inaudibly and mis-articulates its neighbours for a second
    or two. In chunk 0048 that was "Chỉ", which the user heard as the rhythm
    going off; in the same breath "ký" came out as "ghi".

    Measured by rendering that identical chunk at several temperatures: the
    syllable peaks 10.7 dB BELOW the chunk median at position_temperature=0.0
    but 1.5-2.1 dB ABOVE it at 1.0/3.0/5.0 — a ~13 dB swing on the same word in
    the same sentence, so this is a decode defect and not that word simply being
    unstressed.

    Peak, not mean: a mean over whisper's word window silently includes any
    pause inside it and invents quiet words that are not there (that mistake
    cost an earlier version of this analysis a false finding).

    Compare only within a chunk, never against an absolute dB: chunk loudness
    varies, and a syllable is only 'swallowed' relative to its own neighbours.
    """
    y = _decode_samples(wav_path, sample_rate)
    if y is None or len(y) < frame + hop:
        return None

    # frame-wise RMS in dB via a cumulative sum of squares
    if np is not None:
        power = np.cumsum(np.concatenate(([0.0], np.square(y, dtype=np.float64))))
        count = 1 + (len(y) - frame) // hop
        starts = np.arange(count) * hop
        rms = np.sqrt((power[starts + frame] - power[starts]) / frame)
        db = 20.0 * np.log10(np.maximum(rms, 1e-10))
        max_db = float(db.max())
    else:
        power = [0.0]
        total = 0.0
        for sample in y:
            total += sample * sample
            power.append(total)
        count = 1 + (len(y) - frame) // hop
        db = []
        for index in range(count):
            start = index * hop
            rms = math.sqrt((power[start + frame] - power[start]) / frame)
            db.append(20.0 * math.log10(max(rms, 1e-10)))
        max_db = max(db)
    gate = max_db - 40.0            # keep speech, drop pauses and breaths

    peaks = []
    for word in words:
        lo = int(word["start"] * sample_rate / hop)
        hi = int(word["end"] * sample_rate / hop)
        span = db[lo:hi]
        if np is not None:
            span = span[span > gate]
            peak = float(span.max()) if span.size >= 2 else None
        else:
            speech_frames = [value for value in span if value > gate]
            peak = max(speech_frames) if len(speech_frames) >= 2 else None
        if peak is not None:
            peaks.append((peak, word["word"].strip(),
                          float(word["start"])))
    if len(peaks) < 8:
        return None
    typical = float(np.median([p[0] for p in peaks])) if np is not None else median(
        [p[0] for p in peaks]
    )
    quietest = min(peaks)
    return quietest[0] - typical, quietest[1], quietest[2]

def token_diff_evidence(expected_text, words):
    """Return token-level omission evidence without hiding replace+delete runs.

    ``SequenceMatcher`` often represents a real missing phrase followed by one
    ASR spelling change as a single ``replace`` opcode.  For example the broken
    audio ``Giấy siêu âm Kỳ...`` against ``Giấy siêu âm nằm bên phải. Trên tờ
    đơn, Kỷ...`` is ``replace(7 expected -> 1 heard)``, not ``delete(6)``.
    Counting only delete opcodes therefore let a six-word omission pass QC.

    A same-length replacement remains a pronunciation/spelling mismatch, not a
    dropped span.  Only the unmatched length of a replacement contributes to
    ``longest_missing``; this preserves tolerance for Kỷ/Kỳ while recovering
    the six words that are acoustically absent.
    """
    expected = _normalize_for_compare(expected_text).split()
    heard = _normalize_for_compare(
        " ".join(word.get("word", "") for word in words)
    ).split()
    matcher = SequenceMatcher(None, expected, heard, autojunk=False)
    operations = []
    longest_missing = 0
    longest_missing_text = ""
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            continue
        expected_part = expected[i1:i2]
        heard_part = heard[j1:j2]
        missing_count = 0
        missing_part = []
        if tag == "delete":
            missing_count = len(expected_part)
            missing_part = expected_part
        elif tag == "replace" and len(expected_part) > len(heard_part):
            missing_count = len(expected_part) - len(heard_part)
            # SequenceMatcher does not expose an alignment inside a replace
            # block.  The count is exact; this text is diagnostic only.
            missing_part = expected_part[:missing_count]
        operations.append({
            "tag": tag,
            "expected": " ".join(expected_part),
            "heard": " ".join(heard_part),
            "missing_count": missing_count,
        })
        if missing_count > longest_missing:
            longest_missing = missing_count
            longest_missing_text = " ".join(missing_part)
    return {
        "similarity": matcher.ratio(),
        "longest_missing": longest_missing,
        "longest_missing_text": longest_missing_text,
        "operations": operations,
    }

def timing_defects_from_words(
        wav_path, expected_text, words, model, swallow_db=DEFAULT_FAST_SWALLOW_DB,
        transcriber=None, adaptive=False, similarity_floor=0.94,
        adaptive_floor=0.985, word_probability_floor=0.78,
        word_duration_ratio=2.4, min_local_wps=1.6, max_local_wps=9.0,
        dropped_words=4, drag_ratio=6.0, payload=None, chunk_span=None,
        retry_text_mismatch=False, retry_timing_anomalies=False,
        retry_empty_asr=False, similarity_severity=None):
    """Score one expected chunk using word timings from an existing ASR pass.

    ``similarity_severity`` ({"hard","warn","off"}) controls ONLY the whole-chunk
    word-similarity-ratio check, independent of ``retry_text_mismatch`` (which
    still governs the dropped-word-span check). Defaults to None, meaning "follow
    retry_text_mismatch" (old behavior, unchanged for existing callers). The
    module docstring above already notes why these are different-strength
    signals: a contiguous dropped-word span survives three independent signals
    at once and is reliable; the bare similarity ratio is a fuzzy whole-chunk
    score that Vietnamese ASR (esp. faster-whisper on Kaggle) can push below
    floor from transcription noise (spelling/diacritics/tone) alone, on audio a
    human confirms is correct — measured similarity_floor=0.94 flagging chunks
    later confirmed defect-free at 0.750-0.933. Callers with a noisy ASR backend
    should pass similarity_severity="warn" so this fuzzy score cannot hard-fail
    (and burn a re-render) on its own.
    """
    if not words:
        if retry_empty_asr:
            return 0.0, "ASR heard no words in chunk"
        return 1.0, "ok (ASR heard no words in chunk; warning only)"

    diff_evidence = token_diff_evidence(expected_text, words)
    similarity = diff_evidence["similarity"]
    dropped = diff_evidence["longest_missing"]
    dropped_text = diff_evidence["longest_missing_text"]
    asr_exact = similarity == 1.0 and dropped == 0 and not diff_evidence["operations"]

    timed = [w for w in words if not _is_collapsed_numeral(w)]
    spans = [w["end"] - w["start"] for w in timed]
    typical = median(spans)
    drag, dragged_word = 0.0, ""
    for word, span in zip(timed, spans):
        if typical and span / typical > drag:
            drag, dragged_word = span / typical, word["word"].strip()

    similarity_is_fault = (
        retry_text_mismatch if similarity_severity is None
        else similarity_severity == "hard"
    )
    similarity_off = similarity_severity == "off"

    faults = []
    warnings = []
    if dropped >= dropped_words:
        message = f"dropped {dropped} words ({dropped_text!r})"
        (faults if retry_text_mismatch else warnings).append(message)
    if drag > drag_ratio:
        message = f"dragged {dragged_word!r} {drag:.1f}x median"
        (faults if retry_timing_anomalies and not asr_exact else warnings).append(message)
    if not similarity_off and similarity < similarity_floor:
        message = f"word similarity {similarity:.3f}"
        (faults if similarity_is_fault else warnings).append(message)

    confidence_penalty = 0.0
    confidence = low_confidence_word(
        words, word_probability_floor, word_duration_ratio, expected_text
    )
    if confidence is not None:
        probability, word, ratio, at = confidence
        message = (
            f"uncertain {word!r} at {at:.1f}s "
            f"(p={probability:.3f}, duration {ratio:.1f}x median)"
        )
        if retry_timing_anomalies and not asr_exact:
            faults.append(message)
            confidence_penalty = (word_probability_floor - probability) * 0.1
        else:
            warnings.append(message)

    tempo_penalty = 0.0
    tempo = local_tempo_defect(
        words, min_wps=min_local_wps, max_wps=max_local_wps
    )
    if tempo is not None:
        kind, rate, phrase = tempo
        message = f"{kind} local tempo {rate:.2f} words/s ({phrase!r})"
        if retry_timing_anomalies and not asr_exact:
            faults.append(message)
            boundary = max_local_wps if kind == "fast" else min_local_wps
            tempo_penalty = abs(rate - boundary) * 0.01
        else:
            warnings.append(message)

    penalty = 0.0
    swallowed = swallowed_syllable(wav_path, words)
    if swallowed is not None and swallowed[0] < swallow_db:
        deviation, word, at = swallowed
        message = f"swallowed {word!r} at {at:.1f}s ({deviation:.1f} dB under median)"
        if asr_exact:
            warnings.append(message)
        else:
            faults.append(message)
        penalty = (swallow_db - deviation) * 0.01

    local_similarity = None
    if adaptive and not faults and similarity < adaptive_floor:
        if chunk_span is not None:
            local_similarity = asr_similarity_span(
                wav_path, expected_text, model, words,
                chunk_span[0], chunk_span[1], transcriber=transcriber,
            )
        else:
            local_similarity = asr_similarity(
                wav_path, expected_text, model, transcriber=transcriber,
                payload=payload,
            )
        if local_similarity is None:
            return None, "adaptive ASR failed"
        if local_similarity < adaptive_floor:
            message = f"local ASR similarity {local_similarity:.3f}"
            (faults if similarity_is_fault else warnings).append(message)

    score = min(
        similarity,
        local_similarity if local_similarity is not None else similarity,
    ) - penalty - confidence_penalty - tempo_penalty
    if faults:
        return score, "; ".join(faults)
    label = "adaptive fast verify" if local_similarity is not None else "fast verify"
    if warnings:
        return 1.0, f"ok ({label} {score:.3f}; warnings: {'; '.join(warnings)})"
    return score, f"ok ({label} {score:.3f})"

def payload_words(payload):
    return [
        word
        for segment in payload.get("segments", [])
        for word in segment.get("words", [])
        if "start" in word and "end" in word
    ]

def transcribe_word_timestamps(wav_path, model, transcriber=None):
    mlx_bin = _whisper_bin()
    # A transcriber (MLX or faster-whisper) can serve the request in-process even
    # where the mlx_whisper CLI is absent (e.g. Linux/CUDA on Kaggle).
    if not mlx_bin and transcriber is None:
        return None
    with tempfile.TemporaryDirectory() as tmp:
        payload = _run_whisper(
            mlx_bin, wav_path, model, tmp, word_timestamps=True,
            transcriber=transcriber,
        )
    if not payload:
        return None
    words = payload_words(payload)
    return payload, words

_WHISPER_WORKER_CODE = r'''
import json
import sys

import mlx_whisper

for line in sys.stdin:
    try:
        request = json.loads(line)
        payload = mlx_whisper.transcribe(
            request["audio"],
            path_or_hf_repo=request["model"],
            language="vi",
            word_timestamps=bool(request.get("word_timestamps")),
            verbose=None,
        )
        # Tokens account for most of the JSON but are not used by the verifier.
        for segment in payload.get("segments", []):
            segment.pop("tokens", None)
        response = {"ok": True, "payload": payload}
    except Exception as exc:
        response = {"ok": False, "error": f"{type(exc).__name__}: {exc}"}
    print(json.dumps(response, ensure_ascii=False), flush=True)
'''

class MLXWhisperSession:
    """Persistent mlx-whisper subprocess.

    The CLI starts a fresh Python process and reloads the model for every WAV.
    Keeping one worker alive reduced the measured seven-chunk fast audit from
    40.5s to 25.6s and the clause audit from 147.3s to 73.5s on this M1.
    """

    def __init__(self, timeout=900.0):
        self.timeout = timeout
        self.process = None

    def _start(self):
        python_bin = os.path.join(VOXCPM_TTS_VENV_BIN, "python")
        if not os.path.exists(python_bin):
            return False
        env = os.environ.copy()
        env["no_proxy"] = "localhost,127.0.0.1"
        env["NO_PROXY"] = "localhost,127.0.0.1"
        env["HF_HUB_DISABLE_PROGRESS_BARS"] = "1"
        try:
            self.process = subprocess.Popen(
                [python_bin, "-u", "-c", _WHISPER_WORKER_CODE],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                text=True,
                encoding="utf-8",
                env=env,
                bufsize=1,
            )
        except OSError:
            self.process = None
        return self.process is not None

    def _stop(self):
        process, self.process = self.process, None
        if process is None:
            return
        if process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=2.0)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()

    def close(self):
        self._stop()

    def __enter__(self):
        return self

    def __exit__(self, _exc_type, _exc, _traceback):
        self.close()

    def transcribe(self, audio, model, word_timestamps=False):
        request = json.dumps(
            {
                "audio": os.path.abspath(audio),
                "model": model,
                "word_timestamps": word_timestamps,
            },
            ensure_ascii=False,
        )
        # A worker can occasionally die during MLX/device startup. Restart once;
        # callers still fail closed if both attempts are unavailable.
        for _attempt in range(2):
            if self.process is None and not self._start():
                continue
            try:
                self.process.stdin.write(request + "\n")
                self.process.stdin.flush()
                ready, _, _ = select.select(
                    [self.process.stdout], [], [], self.timeout
                )
                if not ready:
                    raise TimeoutError("mlx-whisper worker timed out")
                line = self.process.stdout.readline()
                if not line:
                    raise BrokenPipeError("mlx-whisper worker exited")
                response = json.loads(line)
                if response.get("ok"):
                    return response.get("payload")
            except (BrokenPipeError, OSError, TimeoutError, ValueError, json.JSONDecodeError):
                pass
            self._stop()
        return None

SWALLOW_DB = -7.0

def sanitize_proxy_env():
    """Remove IPv6 no_proxy entries that httpx parses as invalid URLs on macOS."""
    os.environ["no_proxy"] = "localhost,127.0.0.1"
    os.environ["NO_PROXY"] = "localhost,127.0.0.1"

def timing_defects(
        wav_path, expected_text, model, swallow_db=DEFAULT_FAST_SWALLOW_DB,
        transcriber=None, adaptive=False, similarity_floor=0.94,
        adaptive_floor=0.985, word_probability_floor=0.78,
        word_duration_ratio=2.4, min_local_wps=1.6, max_local_wps=9.0,
        dropped_words=4, drag_ratio=6.0, retry_text_mismatch=False,
        retry_timing_anomalies=False, retry_empty_asr=False):
    """
    Adaptive defect check: one whole-chunk Whisper pass with word timestamps,
    plus clause isolation only for ambiguous scores.

    Returns (similarity, reason), or (None, reason) when whisper is unavailable.

    This catches the *dropped span* defect, which is the one that survives
    position_temperature=0.0 (measured: chunk 0004 of the sample story lost the
    8 words "vị hôn thê của Đường Thức, thiếu gia" on every render, bit-for-bit
    identical, because a deterministic decode fails deterministically).

    A strong dropped span does not need clause isolation. It cannot hide from
    three independent signals at once, whereas an isolated garbled word can:
      - word-level similarity: 0.901 on the broken chunk vs >=0.957 on 12 clean
      - a deleted run of reference words: 8 words vs 0
      - a dragged syllable, since the model stretches a neighbour to fill the
        freed time: 6.2x this chunk's own median vs <=3.4x on the clean ones
    Every threshold below therefore sits in a wide empty gap, not on a cliff.

    Timing GAPS are deliberately not a signal: a dropped span does leave a hole
    (1.12s here), but ordinary paragraph pauses reach 0.8s once
    position_temperature is raised on a retry, so a gap rule fires on healthy
    retries. Use --verify for the slower clause-isolated garble check.
    """
    mlx_bin = _whisper_bin()
    if not mlx_bin:
        return None, "ASR unavailable"

    with tempfile.TemporaryDirectory() as tmp:
        payload = _run_whisper(
            mlx_bin, wav_path, model, tmp, word_timestamps=True,
            transcriber=transcriber,
        )
    if not payload:
        return None, "ASR failed"
    words = [word for segment in payload.get("segments", [])
             for word in segment.get("words", [])]
    if not words:
        return None, "ASR returned no words"
    return timing_defects_from_words(
        wav_path, expected_text, words, model, swallow_db=swallow_db,
        transcriber=transcriber, adaptive=adaptive,
        similarity_floor=similarity_floor, adaptive_floor=adaptive_floor,
        word_probability_floor=word_probability_floor,
        word_duration_ratio=word_duration_ratio,
        min_local_wps=min_local_wps, max_local_wps=max_local_wps,
        dropped_words=dropped_words, drag_ratio=drag_ratio, payload=payload,
        retry_text_mismatch=retry_text_mismatch,
        retry_timing_anomalies=retry_timing_anomalies,
        retry_empty_asr=retry_empty_asr,
    )
