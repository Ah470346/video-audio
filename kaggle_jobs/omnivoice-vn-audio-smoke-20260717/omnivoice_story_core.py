# -*- coding: utf-8 -*-
import argparse
import array
import json
import math
import os
import re
import select
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import unicodedata
from difflib import SequenceMatcher

try:
    import numpy as np
except ImportError:  # a stdlib fallback keeps swallowed-syllable checks active
    np = None


class VerificationUnavailableError(RuntimeError):
    """Raised when requested audio verification cannot actually run."""


class AudioQualityError(RuntimeError):
    """Raised when every allowed render attempt still fails strict QA."""


SENTENCE_END_RE = re.compile(r'(?<=[.!?。！？…])["”’\']?\s+')

# ---------------------------------------------------------------------------
# OmniVoice locations / voice catalog
# ---------------------------------------------------------------------------
K2FSA_OMNIVOICE_ROOT = os.environ.get(
    "K2FSA_OMNIVOICE_ROOT",
    os.path.expanduser("~/k2fsa-omnivoice311"),
)
OMNIVOICE_HOME = os.environ.get(
    "OMNIVOICE_HOME",
    os.path.expanduser("~/k2fsa-omnivoice-data"),
)
VOICES_DIR = os.path.join(OMNIVOICE_HOME, "voices")
OMNIVOICE_DB = os.path.join(OMNIVOICE_HOME, "omnivoice.db")
OMNIVOICE_BIN = os.path.join(
    K2FSA_OMNIVOICE_ROOT,
    ".venv",
    "bin",
    "omnivoice-infer-batch",
)
OMNIVOICE_VENV_BIN = os.path.join(K2FSA_OMNIVOICE_ROOT, ".venv", "bin")

DEFAULT_VOICE = "NGOC HUYEN V2"

# ref_text = transcript of the reference clip. A correct transcript sharply
# improves alignment (fewer dropped/garbled words). The OmniVoice DB stores an
# empty ref_text for some cloned voices, so we keep verified transcripts here
# as a fallback (matched case-insensitively by voice name).
KNOWN_VOICE_REFTEXT = {
    "NGOC HUYEN V2": (
        "Giữa buổi chiều Hà Nội, những cơn gió nhẹ lướt qua hàng cây mang theo "
        "hương hoa sữa thoảng trong không khí. Cô mỉm cười như vừa nhớ lại một "
        "câu chuyện rất xa."
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

# num_step presets. Decoding time is linear in num_step: on an M1 the same text
# takes ~306s at 32 steps, ~161s at 16, ~108s at 8.
#
# num_step is a floor, not the dropped-word fix. Below 16 the chunk is under-
# decoded and words genuinely garble even with position sampling stabilised:
# clause-scored, chunk 0012 at num_step=8 fell to 0.899 (4/6 samples < 0.965),
# while at num_step=16 it stayed >=0.996 (6/6). Above 16 buys a slightly milder
# tail but not fewer defects. The dropped-word control is --position_temperature
# (see that arg). A controlled 2026-07 benchmark at 16 steps found 10/13 clean at
# 0.0, 10/13 at 1.0, and 25/25 at 2.0 across repeated hard-chunk samples. Thus
# 16 steps + position_temperature 2.0 is the current measured sweet spot and is
# about 2x faster than 32 steps.
#
# But do not read that as "clean in one pass, no checking needed" — an earlier
# version of this comment did, and it was wrong. position_temperature=0.0 makes
# the decode deterministic, which removes the RANDOMNESS of dropped words, not
# the words. A chunk that decodes wrong is then wrong on every render (verified
# bit-identical), so re-rendering it unchanged can never help and only a check
# finds it: 1 of 13 real chunks silently lost an 8-word span this way. Hence
# --fast_verify is on by default, and retries draw another sample before raising
# position_temperature further.
#
# Beware of measuring any of this with a whole-chunk ASR round-trip: it rates a
# garbled chunk as ~0.99 because whisper's language model repairs the broken
# words from surrounding context before you ever see them. asr_similarity
# isolates clauses to defeat that. (A dropped SPAN is the exception — it is too
# big to repair, which is why the cheap timing_defects pass can catch that one
# class without isolation.)
QUALITY_PRESETS = {"high": 32, "balanced": 16, "fast": 8}


# ---------------------------------------------------------------------------
# Vietnamese text preprocessing for TTS
# ---------------------------------------------------------------------------
# OmniVoice is zero-shot and has no Vietnamese pronunciation lexicon: it has no
# phoneme input for this language (upstream documents pronunciation override for
# zh/en only), so anything that is not plain Vietnamese prose is guessed from the
# raw character sequence. Digits, "/", ":", a bare "h" and Latin acronyms are
# where that guess goes wrong, and a wrong guess is not a contained
# mispronunciation: the model budgets the wrong amount of time for the token and
# compresses or swallows the syllables around it to catch up. That is the "nuốt
# chữ / loạn nhịp" heard in long-form output, so the cheapest place to fix it is
# here, before the model ever sees the text.
#
# Every rule below was written against a measured defect. Fed to the previous
# normalizer, these real inputs reached OmniVoice as:
#   "3-5 lần"        -> "ba âm năm lần"              (dash parsed as minus)
#   "ngày 12/5/2024" -> "mười hai / năm / hai nghìn…" (slash left in)
#   "7h30"           -> "bảy h ba mươi"              (bare Latin letter)
#   "19:45"          -> "mười chín: bốn mươi lăm"    (colon = pause mid-clause)
#   "0912345678"     -> "chín trăm mười hai triệu…"  (phone read as a quantity)
#   "250.000đ"       -> "hai trăm năm mươi nghìn đ"  (orphan unit letter)
#   "1/3"            -> "một / ba"
#   "TS. Nguyễn"     -> "TS. Nguyễn"                 (also a false sentence end)
#   "ADN" / "USB" / "MC"                             (left raw for the model to guess)
#
# The expansions are shared with _normalize_for_compare so the ASR verifier
# scores the same words the model was asked to say. Skipping that makes every
# normalized chunk look like a mismatch and burns real render time on retries.
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


_NUMBER_RE = re.compile(r"-?\d{1,3}(?:\.\d{3})+(?:,\d+)?|-?\d+(?:,\d+)?")


def spell_digits(token):
    """Read a digit run one digit at a time, the way a phone number is said."""
    return " ".join(_VI_UNITS[int(char)] for char in token if char.isdigit())


def _spell_int(value):
    return number_to_vietnamese(int(value))


# Dates. The three-part form is unambiguous, so it is always a date. The
# two-part form is not — "1/3" is both mùng 1 tháng 3 and one third — so it is
# only read as a date behind a word that forces that meaning; everything else
# falls through to the fraction rule below.
_DATE_LEAD = r"(?:ngày|mùng|mồng|hôm|sáng|trưa|chiều|tối|đêm|vào|từ|đến|lúc)"
_FULL_DATE_RE = re.compile(r"\b(\d{1,2})\s*([/-])\s*(\d{1,2})\s*\2\s*(\d{4})\b")
_SHORT_DATE_RE = re.compile(rf"(?i:({_DATE_LEAD}))\s+(\d{{1,2}})\s*/\s*(\d{{1,2}})\b")

# Times. Minutes are required to be two digits so a score ("2:1") is not read as
# a clock time; hour/minute are range-checked for the same reason.
_TIME_HM_RE = re.compile(r"\b(\d{1,2})\s*(?:h|:|g(?:iờ)?)\s*(\d{2})\b")
_TIME_H_RE = re.compile(r"\b(\d{1,2})h(?![\wÀ-ỹ])")

# "3-5 lần". Must run before the generic number rule, which reads the dash of
# the second operand as a minus sign ("ba âm năm").
_RANGE_RE = re.compile(r"(?<![\d/-])(\d+)\s*[-–]\s*(\d+)(?![\d/-])")

_FRACTION_RE = re.compile(r"(?<![\d./])(\d{1,3})\s*/\s*(\d{1,3})(?![\d./])")

# "15 triệu/tháng" -> "mỗi tháng". Only a closed list of period nouns, because a
# slash between two arbitrary words means "or" as often as it means "per".
_PER_RE = re.compile(
    r"\s*/\s*(tháng|năm|ngày|tuần|giờ|phút|giây|người|lần|cái|con|suất)"
    r"(?![\wÀ-ỹ])",
    re.IGNORECASE,
)

# A digit run that is an identifier rather than a quantity. A leading zero says
# so outright; otherwise Vietnamese writes money grouped ("1.500.000"), so an
# ungrouped run this long is a phone/account/ID number, while a bare 4-digit
# year stays a number. The lookahead rejects a "." or "," only when a digit
# follows it, so that a group separator still blocks a match while the period
# ending the sentence does not.
_ID_NUMBER_RE = re.compile(r"(?<![\d.,])(0\d+|\d{8,})(?!\d|[.,]\d)")

# Longest first: "m2" must win over "m", "kg" over "k".
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
_UNIT_LOOKUP = {unit: spoken for unit, spoken in _UNIT_MAP}

# Roman numerals are only expanded behind a word that makes them a numeral.
# Unguarded, "I" and "V" are ordinary initials and get destroyed.
_ROMAN_LEAD = (r"(?:thế\s+kỷ|thế\s+kỉ|chương|phần|quyển|tập|khóa|khoá|lớp|"
               r"kỳ|kì|đợt|mục|điều|khoản|thứ|loại|cấp|đời)")
_ROMAN_RE = re.compile(
    rf"(?i:({_ROMAN_LEAD}))\s+(M{{0,3}}(?:CM|CD|D?C{{0,3}})(?:XC|XL|L?X{{0,3}})"
    r"(?:IX|IV|V?I{0,3}))(?![\wÀ-ỹ])"
)
_ROMAN_VALUES = [("M", 1000), ("CM", 900), ("D", 500), ("CD", 400),
                 ("C", 100), ("XC", 90), ("L", 50), ("XL", 40),
                 ("X", 10), ("IX", 9), ("V", 5), ("IV", 4), ("I", 1)]

# Latin acronyms, matched CASE-SENSITIVELY and only from this list. Both halves
# of that rule matter. Case-sensitive because several expansions collide with
# real Vietnamese words in lower case ("ai", "ca", "vi"), and list-only because
# Vietnamese scripts use ALL CAPS for emphasis — a generic all-caps speller
# turns "Tôi KHÔNG đồng ý" into spelled-out letters. Unknown acronyms are left
# alone (the previous behaviour) rather than guessed at; extend the list through
# --pron_dict, which is applied first and therefore overrides any entry here.
#
# A Vietnamese expansion is preferred to letter-spelling wherever one exists
# (TP -> "thành phố"), since real words are what the model is trained to say.
# Keys carrying a trailing dot are expanded WITH the dot: left in place, "TS."
# also reads as a sentence boundary and splits the chunk mid-name.
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

# Common tokens OmniVoice tends to mispronounce. Extend via --pron_dict JSON.
DEFAULT_PRON_DICT = {
    # OmniVoice consistently hardens Vietnamese d in ``dao/Dao`` to đ
    # (both independent ASRs hear ``đao/đau``).  ``giao`` is the same /zaw/
    # pronunciation in the northern reference voice, while prompting the
    # model to produce the correct soft consonant.  Case is restored by
    # apply_pronunciation_dict so names remain detectable as proper nouns.
    "dao": "giao",
    "wifi": "goai phai",
    "wi-fi": "goai phai",
    "email": "i meo",
    "e-mail": "i meo",
    "app": "áp",
    "ok": "ô kê",
    "okay": "ô kê",
    "video": "vi đê ô",
    "clip": "cờ líp",
    "livestream": "lai sờ trim",
    "online": "on lai",
    "offline": "óp lai",
    "smartphone": "sờ mát phôn",
    "internet": "in tơ nét",
}


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


def apply_acronym_dict(text, acronym_dict):
    """Expand known Latin acronyms, longest key first and case-sensitively."""
    for term in sorted(acronym_dict, key=len, reverse=True):
        # A key ending in "." consumes that dot; one that does not must still
        # not fire inside a longer word ("TV" in "TVs", "VN" in "VNese").
        tail = "" if term.endswith(".") else r"(?![\wÀ-ỹ])"
        pattern = re.compile(r"(?<![\wÀ-ỹ])" + re.escape(term) + tail)
        text = pattern.sub(acronym_dict[term], text)
    return text


def _roman_to_int(numeral):
    value, index = 0, 0
    for symbol, amount in _ROMAN_VALUES:
        while numeral.startswith(symbol, index):
            value += amount
            index += len(symbol)
    return value


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


def _read_unit(match):
    quantity, unit = match.groups()
    spelled = _spell_number_token(quantity)
    if spelled is None:
        return match.group(0)
    return f" {spelled} {_UNIT_LOOKUP[unit.lower()]} "


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


def clarify_punctuation(text):
    """Leave only punctuation OmniVoice can turn into prosody.

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
    Normalize text so OmniVoice mispronounces/skips fewer words:
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


# ---------------------------------------------------------------------------
# Chunking
# ---------------------------------------------------------------------------
def split_paragraph_into_sentences(paragraph):
    return [sentence.strip() for sentence in SENTENCE_END_RE.split(paragraph) if sentence.strip()]


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


def is_standalone_dialogue(text):
    stripped = text.strip()
    if len(stripped) > 120:
        return False
    return (
        (stripped.startswith('"') and stripped.endswith('"'))
        or (stripped.startswith("“") and stripped.endswith("”"))
        or (stripped.startswith("'") and stripped.endswith("'"))
    )


def _within_limits(text, max_chars, max_words):
    return len(text) <= max_chars and len(text.split()) <= max_words


def ensure_terminal_punctuation(text):
    """Give each chunk a closing mark so prosody resolves (fewer trailing artifacts)."""
    stripped = text.rstrip()
    if stripped and stripped[-1] not in ".!?…\"'”’":
        return stripped + "."
    return stripped


def split_text_into_chunks(text, max_chars, max_words):
    if max_chars <= 0:
        return [text]

    pieces = []
    current = ""

    paragraphs = [paragraph.strip() for paragraph in re.split(r"\n\s*\n+", text) if paragraph.strip()]
    for paragraph in paragraphs:
        sentences = []
        for sentence in split_paragraph_into_sentences(paragraph):
            sentences.extend(split_long_sentence(sentence, max_chars, max_words))

        for sentence in sentences:
            if not current:
                current = sentence
                continue

            candidate = f"{current} {sentence}"
            if _within_limits(candidate, max_chars, max_words):
                current = candidate
            else:
                pieces.append(current)
                current = sentence

        if current:
            pieces.append(current)
            current = ""

    chunks = []
    current = ""
    for piece in pieces:
        if is_standalone_dialogue(piece):
            if current:
                chunks.append(current)
                current = ""
            chunks.append(piece)
            continue

        if not current:
            current = piece
            continue

        candidate = f"{current}\n\n{piece}"
        if _within_limits(candidate, max_chars, max_words) and not is_standalone_dialogue(current):
            current = candidate
        else:
            chunks.append(current)
            current = piece

    if current:
        chunks.append(current)

    chunks = [ensure_terminal_punctuation(chunk) for chunk in chunks if chunk.strip()]
    return chunks or [ensure_terminal_punctuation(text)]


# ---------------------------------------------------------------------------
# Voice resolution (OmniVoice DB lookup by name)
# ---------------------------------------------------------------------------
def resolve_voice(name):
    """Return (ref_audio_abs_path, ref_text) for a voice profile name."""
    ref_audio = None
    ref_text = None

    if os.path.exists(OMNIVOICE_DB):
        try:
            conn = sqlite3.connect(f"file:{OMNIVOICE_DB}?mode=ro", uri=True)
            row = conn.execute(
                "SELECT ref_audio_path, ref_text FROM voice_profiles "
                "WHERE lower(name) = lower(?) ORDER BY created_at DESC LIMIT 1",
                (name,),
            ).fetchone()
            conn.close()
            if row:
                audio_path, db_ref_text = row
                if audio_path:
                    ref_audio = audio_path if os.path.isabs(audio_path) else os.path.join(VOICES_DIR, audio_path)
                if db_ref_text and db_ref_text.strip():
                    ref_text = db_ref_text.strip()
        except sqlite3.Error as exc:
            print(f"Warning: could not read voice from OmniVoice DB: {exc}")

    if ref_text is None:
        for known_name, known_text in KNOWN_VOICE_REFTEXT.items():
            if known_name.lower() == name.lower():
                ref_text = known_text
                break

    return ref_audio, ref_text


# ---------------------------------------------------------------------------
# Audio probing / quality validation
# ---------------------------------------------------------------------------
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


def probe_mean_volume(path):
    """Return (mean_dB, max_dB); very low values indicate a silent/failed render."""
    try:
        out = subprocess.run(
            ["ffmpeg", "-hide_banner", "-i", path, "-af", "volumedetect",
             "-f", "null", "-"],
            capture_output=True, text=True,
        )
        log = out.stderr
        mean = re.search(r"mean_volume:\s*(-?\d+(?:\.\d+)?) dB", log)
        peak = re.search(r"max_volume:\s*(-?\d+(?:\.\d+)?) dB", log)
        return (
            float(mean.group(1)) if mean else -999.0,
            float(peak.group(1)) if peak else -999.0,
        )
    except (subprocess.CalledProcessError, ValueError):
        return -999.0, -999.0


def expected_duration_seconds(text, speed):
    # ~15 characters per second of Vietnamese narration is a loose midpoint.
    return max(len(text) / 15.0 / max(speed, 0.1), 0.5)


# OmniVoice normalizes every chunk to the RMS of the same reference clip, so a
# healthy run lands all chunks within roughly a decibel of each other. A chunk
# that decodes to noise/mumble instead of speech comes out far quieter while
# still sitting well above any absolute silence gate (observed: -31 dB mean when
# the good chunks were at -18 dB). Comparing against the run's own median is what
# catches those; an absolute threshold does not.
VOLUME_OUTLIER_DB = 8.0


def probe_chunk_stats(path):
    """Probe duration + levels once; returns None when the file is unusable."""
    if not os.path.exists(path) or os.path.getsize(path) < 1024:
        return None
    mean_db, max_db = probe_mean_volume(path)
    return {"duration": probe_duration(path), "mean_db": mean_db, "max_db": max_db}


def validate_chunk_audio(path, text, speed, stats=None, reference_db=None):
    """Cheap sanity checks. Returns (ok, reason)."""
    if stats is None:
        stats = probe_chunk_stats(path)
    if stats is None:
        return False, "missing or empty"

    duration = stats["duration"]
    if duration < 0.35:
        return False, f"too short ({duration:.2f}s)"

    expected = expected_duration_seconds(text, speed)
    if duration > expected * 2.6:
        return False, f"too long ({duration:.1f}s vs ~{expected:.1f}s expected)"
    if duration < expected * 0.4:
        return False, f"suspiciously short ({duration:.1f}s vs ~{expected:.1f}s expected)"

    mean_db, max_db = stats["mean_db"], stats["max_db"]
    if max_db < -30.0 or mean_db < -55.0:
        return False, f"near-silent (mean {mean_db:.0f} dB, peak {max_db:.0f} dB)"

    if reference_db is not None and mean_db < reference_db - VOLUME_OUTLIER_DB:
        return False, (f"far quieter than the rest of the run "
                       f"(mean {mean_db:.0f} dB vs {reference_db:.0f} dB median)")

    return True, "ok"


def median(values):
    ordered = sorted(values)
    if not ordered:
        return None
    middle = len(ordered) // 2
    if len(ordered) % 2:
        return ordered[middle]
    return (ordered[middle - 1] + ordered[middle]) / 2.0


# ---------------------------------------------------------------------------
# Optional ASR verification (word-error detection via whisper round-trip)
# ---------------------------------------------------------------------------
# Whisper is a language model as much as an acoustic one. Handed a whole chunk,
# it repairs a garbled word from the surrounding sentences and reports text the
# TTS never actually said: a chunk that pronounced "là biết trước" as "là biết
# chứng" transcribed back as flawless text, similarity 1.000, because the next
# sentence happened to repeat "biết trước". Whole-chunk ASR therefore cannot see
# dropped or mangled words at all — it certifies them as perfect. Cutting the
# chunk into single clauses and transcribing each one alone takes that context
# away, and the same clause comes back as "Là biết chứng."
#
# Cuts land in the MIDDLE of a silence gap. Slicing at word boundaries instead
# shaves the leading consonant off the next word ("không" -> "khung") and
# invents errors that were never in the audio.
ISOLATION_MIN_GAP = 0.16


# Whisper writes what it hears back in ORTHOGRAPHY, and picks the spelling
# freely: the one phone number rendered from "không chín một hai…" came back as
# "0912345678" on one take and "0912 345 678" on the next, and "bảy giờ ba mươi"
# came back as "7.30". These fold those spellings into the forms
# normalize_vietnamese_numerals already reads.
#
# They run over BOTH sides of the comparison, which is what makes them safe to
# be this blunt: the job here is only to make two transcripts of the same speech
# agree, and nothing here can change what the model is asked to say.
_ASR_PHONE_RE = re.compile(r"\b0\d[\d .]{5,}\d\b")
_ASR_DOT_TIME_RE = re.compile(r"\b(\d{1,2})\.(\d{2})\b(?!\d)")


def _canonicalize_asr_orthography(text):
    # Only a leading zero, never a grouped amount: "1.500.000" must stay one
    # quantity, while "0912 345 678" is one identifier written with spaces.
    text = _ASR_PHONE_RE.sub(lambda m: re.sub(r"[ .]", "", m.group(0)), text)
    return _ASR_DOT_TIME_RE.sub(r"\1h\2", text)


def _normalize_for_compare(text):
    text = unicodedata.normalize("NFC", text)
    # Case-sensitive acronyms must expand before the lower-casing below.
    text = normalize_vietnamese_numerals(_canonicalize_asr_orthography(text))
    text = re.sub(r"[^\wÀ-ỹ\s]", " ", text.lower())
    return re.sub(r"\s+", " ", text).strip()


def sanitize_proxy_env():
    """Remove IPv6 no_proxy entries that httpx parses as invalid URLs on macOS."""
    os.environ["no_proxy"] = "localhost,127.0.0.1"
    os.environ["NO_PROXY"] = "localhost,127.0.0.1"


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


# This worker deliberately lives in the OmniVoice environment: that environment
# owns torch, faster-whisper and the CTC aligner, while the small controller
# script is also expected to run with the macOS system Python.  Keeping the
# heavyweight models in one persistent child avoids reloading several GB for
# every retry candidate.
_STRICT_VERIFY_WORKER_CODE = r'''
import json
import sys

_ctc = None
_faster = {}


def align(request):
    global _ctc
    import torch
    from ctc_forced_aligner import (
        generate_emissions,
        get_alignments,
        get_spans,
        load_alignment_model,
        load_audio,
        postprocess_results,
        preprocess_text,
    )

    model_name = request["model"]
    if _ctc is None or _ctc[0] != model_name:
        model, tokenizer = load_alignment_model(
            "cpu", model_path=model_name, dtype=torch.float32
        )
        _ctc = (model_name, model, tokenizer)
    _name, model, tokenizer = _ctc
    audio = load_audio(request["audio"], model.dtype, model.device)
    emissions, stride = generate_emissions(
        model, audio, batch_size=int(request.get("batch_size", 1))
    )
    tokens, text_starred = preprocess_text(
        request["text"], romanize=True, language="vie"
    )
    segments, scores, blank = get_alignments(emissions, tokens, tokenizer)
    spans = get_spans(tokens, segments, blank)
    return postprocess_results(text_starred, spans, stride, scores)


def transcribe(request):
    from faster_whisper import WhisperModel

    model_name = request["model"]
    model = _faster.get(model_name)
    if model is None:
        model = WhisperModel(
            model_name,
            device="cpu",
            compute_type="int8",
            cpu_threads=int(request.get("cpu_threads", 4)),
        )
        _faster[model_name] = model
    segments, info = model.transcribe(
        request["audio"],
        language="vi",
        beam_size=5,
        word_timestamps=True,
        vad_filter=True,
        condition_on_previous_text=False,
        clip_timestamps=request.get("clip_timestamps", "0"),
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


for line in sys.stdin:
    try:
        request = json.loads(line)
        if request.get("op") == "align":
            payload = align(request)
        elif request.get("op") == "transcribe":
            payload = transcribe(request)
        else:
            raise ValueError("unknown strict-verifier operation")
        response = {"ok": True, "payload": payload}
    except Exception as exc:
        response = {"ok": False, "error": f"{type(exc).__name__}: {exc}"}
    print(json.dumps(response, ensure_ascii=False), flush=True)
'''


class StrictVerifierSession:
    """Persistent CTC forced-aligner plus independent faster-whisper ASR."""

    def __init__(self, timeout=1800.0):
        self.timeout = timeout
        self.process = None
        self.last_error = None

    def _start(self):
        python_bin = os.path.join(OMNIVOICE_VENV_BIN, "python")
        if not os.path.exists(python_bin):
            self.last_error = f"verification Python not found: {python_bin}"
            return False
        env = os.environ.copy()
        env["no_proxy"] = "localhost,127.0.0.1"
        env["NO_PROXY"] = "localhost,127.0.0.1"
        env["HF_HUB_DISABLE_PROGRESS_BARS"] = "1"
        env["TOKENIZERS_PARALLELISM"] = "false"
        try:
            self.process = subprocess.Popen(
                [python_bin, "-u", "-c", _STRICT_VERIFY_WORKER_CODE],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                text=True,
                encoding="utf-8",
                env=env,
                bufsize=1,
            )
        except OSError as exc:
            self.last_error = f"{type(exc).__name__}: {exc}"
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

    def _request(self, request):
        encoded = json.dumps(request, ensure_ascii=False)
        for _attempt in range(2):
            if self.process is None and not self._start():
                continue
            try:
                self.process.stdin.write(encoded + "\n")
                self.process.stdin.flush()
                ready, _, _ = select.select(
                    [self.process.stdout], [], [], self.timeout
                )
                if not ready:
                    raise TimeoutError("strict verifier timed out")
                line = self.process.stdout.readline()
                if not line:
                    raise BrokenPipeError("strict verifier exited")
                response = json.loads(line)
                if response.get("ok"):
                    self.last_error = None
                    return response.get("payload")
                self.last_error = response.get("error", "unknown worker error")
            except (
                BrokenPipeError, OSError, TimeoutError, ValueError,
                json.JSONDecodeError,
            ) as exc:
                self.last_error = f"{type(exc).__name__}: {exc}"
            self._stop()
        return None

    def align(self, audio, text, model, batch_size=1):
        return self._request({
            "op": "align",
            "audio": os.path.abspath(audio),
            "text": text,
            "model": model,
            "batch_size": batch_size,
        })

    def transcribe(self, audio, model, cpu_threads=4, clip_timestamps=None):
        request = {
            "op": "transcribe",
            "audio": os.path.abspath(audio),
            "model": model,
            "cpu_threads": cpu_threads,
        }
        if clip_timestamps:
            request["clip_timestamps"] = clip_timestamps
        return self._request(request)


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
        python_bin = os.path.join(OMNIVOICE_VENV_BIN, "python")
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


def _whisper_bin():
    mlx_bin = os.path.join(OMNIVOICE_VENV_BIN, "mlx_whisper")
    if os.path.exists(mlx_bin):
        return mlx_bin
    return shutil.which("mlx_whisper")


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


# A spoken digit string comes back as ONE token: the ten syllables of "không
# chín một hai ba bốn năm sáu bảy tám" are returned as a single "0912345678"
# carrying the timestamps of all four seconds. Every per-word timing rule here
# reads that as one impossibly long, impossibly slow word — measured at 10.7x
# the chunk median, on audio that was word-perfect. It is one token, not one
# word, so no per-word rule may judge it.
_COLLAPSED_NUMERAL_RE = re.compile(r"\d\d")


def _is_collapsed_numeral(word):
    return bool(_COLLAPSED_NUMERAL_RE.search(word.get("word", "")))


def isolation_windows(words, duration, min_gap=ISOLATION_MIN_GAP):
    """Split points at the midpoint of each silence gap, so no phoneme is clipped."""
    cuts = [0.0]
    for current, following in zip(words, words[1:]):
        if following["start"] - current["end"] >= min_gap:
            cuts.append((current["end"] + following["start"]) / 2.0)
    cuts.append(duration)
    return [(start, end) for start, end in zip(cuts, cuts[1:]) if end - start > 0.25]


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


# A syllable this far under its chunk's median peak is mumbled, not unstressed.
# Calibrated on the 13 rendered chunks of the sample story, measured with the
# function above rather than a reference implementation: the two chunks with an
# audible defect scored -14.0 (0012) and -8.5 (0048, the one reported by ear),
# and the eleven healthy ones spanned -5.6..-2.3. Nothing lands in between, so
# -7.0 sits in the middle of a 2.9 dB empty gap.
#
# Calibrate any change to this against swallowed_syllable itself. The threshold
# was first set from librosa's rms, whose centred framing reads ~2 dB lower on
# the same audio; carried over unchanged it put the cut on the wrong side of
# 0048 and the check silently passed the defect it was written for.
SWALLOW_DB = -7.0

# The calibrated -7 dB cut is useful for forensic spot checks, but it is too
# eager as the default long-form retry gate. The normal render path now retries
# only stronger swallowed-syllable evidence unless the caller opts back in.
DEFAULT_FAST_SWALLOW_DB = -10.0


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


def similarity_from_words(expected_text, words):
    heard = _normalize_for_compare(
        " ".join(word.get("word", "") for word in words)
    )
    expected = _normalize_for_compare(expected_text)
    if not expected:
        return 1.0 if not heard else 0.0
    return SequenceMatcher(None, expected, heard).ratio()


def timing_defects_from_words(
        wav_path, expected_text, words, model, swallow_db=DEFAULT_FAST_SWALLOW_DB,
        transcriber=None, adaptive=False, similarity_floor=0.94,
        adaptive_floor=0.985, word_probability_floor=0.78,
        word_duration_ratio=2.4, min_local_wps=1.6, max_local_wps=9.0,
        dropped_words=4, drag_ratio=6.0, payload=None, chunk_span=None,
        retry_text_mismatch=False, retry_timing_anomalies=False,
        retry_empty_asr=False):
    """Score one expected chunk using word timings from an existing ASR pass."""
    if not words:
        if retry_empty_asr:
            return 0.0, "ASR heard no words in chunk"
        return 1.0, "ok (ASR heard no words in chunk; warning only)"

    expected = _normalize_for_compare(expected_text).split()
    heard = _normalize_for_compare(
        " ".join(w.get("word", "") for w in words)
    ).split()
    matcher = SequenceMatcher(None, expected, heard)
    similarity = matcher.ratio()

    dropped, dropped_text = 0, ""
    for tag, i1, i2, _j1, _j2 in matcher.get_opcodes():
        if tag == "delete" and (i2 - i1) > dropped:
            dropped, dropped_text = i2 - i1, " ".join(expected[i1:i2])

    timed = [w for w in words if not _is_collapsed_numeral(w)]
    spans = [w["end"] - w["start"] for w in timed]
    typical = median(spans)
    drag, dragged_word = 0.0, ""
    for word, span in zip(timed, spans):
        if typical and span / typical > drag:
            drag, dragged_word = span / typical, word["word"].strip()

    faults = []
    warnings = []
    if dropped >= dropped_words:
        message = f"dropped {dropped} words ({dropped_text!r})"
        (faults if retry_text_mismatch else warnings).append(message)
    if drag > drag_ratio:
        message = f"dragged {dragged_word!r} {drag:.1f}x median"
        (faults if retry_timing_anomalies else warnings).append(message)
    if similarity < similarity_floor:
        message = f"word similarity {similarity:.3f}"
        (faults if retry_text_mismatch else warnings).append(message)

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
        if retry_timing_anomalies:
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
        if retry_timing_anomalies:
            faults.append(message)
            boundary = max_local_wps if kind == "fast" else min_local_wps
            tempo_penalty = abs(rate - boundary) * 0.01
        else:
            warnings.append(message)

    penalty = 0.0
    swallowed = swallowed_syllable(wav_path, words)
    if swallowed is not None and swallowed[0] < swallow_db:
        deviation, word, at = swallowed
        faults.append(f"swallowed {word!r} at {at:.1f}s ({deviation:.1f} dB "
                      "under median)")
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
            (faults if retry_text_mismatch else warnings).append(message)

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


def payload_words(payload):
    return [
        word
        for segment in payload.get("segments", [])
        for word in segment.get("words", [])
        if "start" in word and "end" in word
    ]


def normalized_tokens(text):
    return _normalize_for_compare(text).split()


def word_tokens_with_indices(words):
    tokens = []
    indices = []
    for index, word in enumerate(words):
        for token in normalized_tokens(word.get("word", "")):
            tokens.append(token)
            indices.append(index)
    return tokens, indices


def _target_token_bounds(prefix_text, target_text):
    start = len(normalized_tokens(prefix_text))
    end = start + len(normalized_tokens(target_text))
    return start, end


def _matching_asr_token_bounds(reference_tokens, asr_tokens, target_start, target_end):
    matcher = SequenceMatcher(None, reference_tokens, asr_tokens, autojunk=False)
    matched = []
    for ref_start, asr_start, size in matcher.get_matching_blocks():
        if size <= 0:
            continue
        ref_end = ref_start + size
        overlap_start = max(ref_start, target_start)
        overlap_end = min(ref_end, target_end)
        if overlap_start >= overlap_end:
            continue
        for ref_index in range(overlap_start, overlap_end):
            matched.append(asr_start + (ref_index - ref_start))
    if not matched:
        return None
    return min(matched), max(matched)


def _fuzzy_target_token_bounds(target_tokens, asr_tokens, min_ratio=0.72):
    if not target_tokens or not asr_tokens:
        return None
    target_len = len(target_tokens)
    min_len = max(1, int(target_len * 0.75))
    max_len = min(len(asr_tokens), max(target_len + 6, int(target_len * 1.25)))
    best = None
    for length in range(min_len, max_len + 1):
        for start in range(0, len(asr_tokens) - length + 1):
            candidate = asr_tokens[start:start + length]
            ratio = SequenceMatcher(
                None, target_tokens, candidate, autojunk=False
            ).ratio()
            if best is None or ratio > best[0]:
                best = (ratio, start, start + length - 1)
    if best is None or best[0] < min_ratio:
        return None
    return best[1], best[2]


def context_target_span_from_words(
        render_text, prefix_text, target_text, words,
        pad_start=0.06, pad_end=0.08, min_ratio=0.72):
    """Locate target_text inside a context-rendered audio transcript."""
    reference_tokens = normalized_tokens(render_text)
    target_tokens = normalized_tokens(target_text)
    asr_tokens, token_word_indices = word_tokens_with_indices(words)
    if not reference_tokens or not target_tokens or not asr_tokens:
        return None

    target_start, target_end = _target_token_bounds(prefix_text, target_text)
    token_bounds = _matching_asr_token_bounds(
        reference_tokens, asr_tokens, target_start, target_end
    )
    if token_bounds is not None:
        candidate = asr_tokens[token_bounds[0]:token_bounds[1] + 1]
        direct_ratio = SequenceMatcher(
            None, target_tokens, candidate, autojunk=False
        ).ratio()
        if direct_ratio < min_ratio:
            token_bounds = None
    if token_bounds is None:
        token_bounds = _fuzzy_target_token_bounds(
            target_tokens, asr_tokens, min_ratio=min_ratio
        )
    if token_bounds is None:
        return None

    first_word = token_word_indices[token_bounds[0]]
    last_word = token_word_indices[token_bounds[1]]
    start = max(0.0, float(words[first_word]["start"]) - pad_start)
    end = float(words[last_word]["end"]) + pad_end
    if end <= start:
        return None
    return start, end


def transcribe_word_timestamps(wav_path, model, transcriber=None):
    mlx_bin = _whisper_bin()
    if not mlx_bin:
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


def chunk_audio_spans(entries, chunk_path):
    spans = []
    cursor = 0.0
    for entry in entries:
        duration = probe_duration(chunk_path(entry["id"]))
        spans.append({
            "id": entry["id"],
            "start": cursor,
            "end": cursor + duration,
            "duration": duration,
        })
        cursor += duration
    return spans


def chunk_audio_spans_from_paths(entries, audio_paths):
    spans = []
    cursor = 0.0
    for entry, path in zip(entries, audio_paths):
        duration = probe_duration(path)
        spans.append({
            "id": entry["id"],
            "start": cursor,
            "end": cursor + duration,
            "duration": duration,
        })
        cursor += duration
    return spans


def assign_words_to_chunk_spans(words, spans, boundary_slack=0.05):
    by_chunk = {span["id"]: [] for span in spans}
    if not spans:
        return by_chunk

    span_index = 0
    for word in words:
        midpoint = (word["start"] + word["end"]) / 2.0
        while span_index < len(spans) - 1 and midpoint >= spans[span_index]["end"]:
            span_index += 1
        span = spans[span_index]
        if span["start"] - boundary_slack <= midpoint < span["end"] + boundary_slack:
            by_chunk[span["id"]].append(word)
    return by_chunk


def review_assembled_audio(
        audio_path, entries, spans, args, transcriber=None,
        return_details=False):
    """Verify the concatenated audio once, then map defects back to chunks."""
    transcribed = transcribe_word_timestamps(
        audio_path, args.verify_model, transcriber=transcriber
    )
    if transcribed is None:
        raise VerificationUnavailableError(
            "assembled-audio verification failed; refusing to accept unchecked audio"
        )
    _payload, words = transcribed
    if not words:
        raise VerificationUnavailableError(
            "assembled-audio ASR returned no words; refusing to accept unchecked audio"
        )

    entry_by_id = {entry["id"]: entry for entry in entries}
    words_by_chunk = assign_words_to_chunk_spans(words, spans)
    results = {}
    for span in spans:
        cid = span["id"]
        entry = entry_by_id[cid]
        chunk_words = words_by_chunk.get(cid, [])
        if args.verify:
            score = similarity_from_words(entry["text"], chunk_words)
            reason = f"assembled ASR similarity {score:.3f}"
        elif args.fast_verify:
            score, reason = timing_defects_from_words(
                audio_path, entry["text"], chunk_words, args.verify_model,
                swallow_db=args.swallow_db, transcriber=transcriber,
                adaptive=args.adaptive_verify,
                similarity_floor=args.fast_similarity_floor,
                adaptive_floor=args.verify_threshold,
                word_probability_floor=args.word_probability_floor,
                word_duration_ratio=args.word_duration_ratio,
                min_local_wps=args.min_local_wps,
                max_local_wps=args.max_local_wps,
                dropped_words=args.dropped_words,
                drag_ratio=args.drag_ratio,
                retry_text_mismatch=args.retry_text_mismatch,
                retry_timing_anomalies=args.retry_timing_anomalies,
                retry_empty_asr=args.retry_empty_asr,
                chunk_span=(span["start"], span["end"]),
            )
            if score is None:
                raise VerificationUnavailableError(
                    f"{cid}: assembled fast verification failed ({reason}); "
                    "refusing to accept unchecked audio"
                )
        else:
            score, reason = 1.0, "ok"
        results[cid] = (score, reason)
    if return_details:
        return results, words_by_chunk
    return results


def transcript_evidence(expected_text, heard_text):
    """Return token-level mismatch evidence suitable for model consensus.

    A similarity number alone cannot distinguish one ASR spelling mistake from
    a missing sentence.  Keeping the opcode evidence lets the strict gate ask
    whether independent recognizers changed the same expected word or inserted
    the same unexpected word.
    """
    expected = _normalize_for_compare(expected_text).split()
    heard = _normalize_for_compare(heard_text).split()
    heard = canonicalize_protected_name_tokens(expected_text, heard)
    matcher = SequenceMatcher(None, expected, heard, autojunk=False)
    changed_expected = []
    changed_heard = []
    insertions = []
    longest_delete = 0
    longest_insert = 0
    operations = []
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            continue
        expected_part = expected[i1:i2]
        heard_part = heard[j1:j2]
        operations.append({
            "tag": tag,
            "expected": " ".join(expected_part),
            "heard": " ".join(heard_part),
        })
        if tag in ("delete", "replace"):
            changed_expected.extend(expected_part)
        if tag in ("insert", "replace"):
            changed_heard.extend(heard_part)
        if tag == "insert":
            insertions.extend(heard_part)
            longest_insert = max(longest_insert, len(heard_part))
        if tag == "delete":
            longest_delete = max(longest_delete, len(expected_part))
    return {
        "similarity": matcher.ratio(),
        "changed_expected": sorted(set(changed_expected)),
        "changed_heard": sorted(set(changed_heard)),
        "insertions": sorted(set(insertions)),
        "longest_delete": longest_delete,
        "longest_insert": longest_insert,
        "operations": operations,
    }


def protected_terms(text):
    """Names and multi-word proper nouns that must survive ASR verification."""
    # Unicode ranges such as À-Ỹ contain lowercase Vietnamese code points too;
    # using them in a regex made ``Cố Dao được`` look like a three-word proper
    # name.  Python's isupper() handles the alphabet correctly.  Punctuation
    # breaks a run, so a capitalized sentence start cannot join the next name.
    word_matches = list(re.finditer(r"\b[^\W\d_]+\b", text, re.UNICODE))
    runs = []
    current = []
    previous = None
    for match in word_matches:
        word = match.group(0)
        joined_by_space = (
            previous is not None
            and not text[previous.end():match.start()].strip()
        )
        if word[0].isupper():
            if current and joined_by_space:
                current.append(word)
            else:
                if len(current) >= 2:
                    runs.append(current)
                current = [word]
        else:
            if len(current) >= 2:
                runs.append(current)
            current = []
        previous = match
    if len(current) >= 2:
        runs.append(current)

    titles = {"ông", "bà", "cô", "anh", "chị", "bố", "mẹ", "bác", "tiến sĩ"}
    # A sentence-leading noun/adverb may be followed immediately by a proper
    # name (``Mặt Cố Dao trắng đi``).  Capitalization alone makes that look
    # like one three-word entity.  Strip only common grammatical leads; never
    # strip an arbitrary first token because genuine Vietnamese names often
    # contain three words (``Cố Minh Trạch``).
    sentence_leads = {
        "ánh", "bên", "cả", "dưới", "giọng", "khi", "lúc", "mặt",
        "mắt", "ngay", "ngoài", "nhưng", "nước", "sau", "tay", "trong",
        "trên", "trước", "từ", "ở",
    }
    terms = set()
    for run in runs:
        normalized = _normalize_for_compare(" ".join(run[:4]))
        pieces = normalized.split()
        if len(pieces) > 2 and pieces[0] in titles:
            pieces = pieces[1:]
        if len(pieces) > 2 and pieces[0] in sentence_leads:
            pieces = pieces[1:]
        normalized = " ".join(pieces)
        if normalized:
            terms.add(normalized)
    return sorted(terms)


def _protected_name_phonetic_word(word):
    """Fold only spelling mergers that are homophones in the reference voice."""
    word = _normalize_for_compare(word)
    if word.startswith("gi") and len(word) > 2:
        return "d" + word[2:]
    if word.startswith("tr") and len(word) > 2:
        return "ch" + word[2:]
    return word


def canonicalize_protected_name_tokens(expected_text, heard_tokens):
    """Map ASR homophone spellings back to the expected proper-name spelling.

    Hanoi speech merges d/gi and tr/ch.  Whisper can therefore write a
    correctly spoken ``Cố Giao`` as ``Cố Dao``, or ``Trạch`` as ``Chạch``.
    This folding is deliberately restricted to detected multi-word names and
    never merges d with đ, so the measured ``Dao`` -> ``Đao`` defect still
    fails strict QA.
    """
    result = list(heard_tokens)
    for term in protected_terms(expected_text):
        expected = term.split()
        expected_key = [_protected_name_phonetic_word(word) for word in expected]
        for start in range(0, len(result) - len(expected) + 1):
            candidate = result[start:start + len(expected)]
            candidate_key = [
                _protected_name_phonetic_word(word) for word in candidate
            ]
            if candidate_key == expected_key:
                result[start:start + len(expected)] = expected
    return result


def missing_protected_terms(expected_text, heard_text):
    heard_tokens = _normalize_for_compare(heard_text).split()
    heard_tokens = canonicalize_protected_name_tokens(
        expected_text, heard_tokens
    )
    heard = f" {' '.join(heard_tokens)} "
    return [
        term for term in protected_terms(expected_text)
        if f" {term} " not in heard
    ]


def split_ctc_alignment(entries, aligned_words):
    """Map forced-alignment words back by the exact known transcript order."""
    expected_total = sum(len(entry["text"].split()) for entry in entries)
    if len(aligned_words) != expected_total:
        raise VerificationUnavailableError(
            "CTC alignment returned "
            f"{len(aligned_words)} words for {expected_total} expected words; "
            "refusing to score a shifted alignment"
        )
    by_chunk = {}
    cursor = 0
    for entry in entries:
        count = len(entry["text"].split())
        by_chunk[entry["id"]] = aligned_words[cursor:cursor + count]
        cursor += count
    return by_chunk


def ctc_alignment_evidence(
        words, mean_floor=-1.70, word_floor=-4.0,
        critical_floor=-8.0, consecutive_bad_words=2):
    """Classify strong acoustic/text disagreement from CTC log scores.

    A single Vietnamese name can score poorly even when spoken correctly, so
    one ordinary low word is diagnostic only.  A very low chunk mean, a run of
    bad neighbouring words, or one catastrophic score is the fail signal.
    Those shapes are what missing clauses create when forced alignment tries to
    squeeze words that were never spoken into the remaining waveform.
    """
    scores = [float(word.get("score", float("-inf"))) for word in words]
    if not scores or any(not math.isfinite(score) for score in scores):
        return {
            "failed": True,
            "mean_score": None,
            "min_score": None,
            "max_bad_run": 0,
            "bad_words": [],
            "reason": "CTC returned no finite word scores",
        }
    bad_words = []
    max_run = 0
    run = 0
    for word, score in zip(words, scores):
        if score <= word_floor:
            run += 1
            max_run = max(max_run, run)
            bad_words.append({
                "word": word.get("text", word.get("word", "")),
                "score": score,
            })
        else:
            run = 0
    mean_score = sum(scores) / len(scores)
    min_score = min(scores)
    reasons = []
    if mean_score <= mean_floor:
        reasons.append(f"mean {mean_score:.2f} <= {mean_floor:.2f}")
    if max_run >= consecutive_bad_words:
        reasons.append(
            f"{max_run} consecutive words <= {word_floor:.1f}"
        )
    if min_score <= critical_floor:
        reasons.append(f"minimum {min_score:.2f} <= {critical_floor:.2f}")
    return {
        "failed": bool(reasons),
        "mean_score": mean_score,
        "min_score": min_score,
        "max_bad_run": max_run,
        "bad_words": bad_words,
        "reason": "; ".join(reasons) if reasons else "ok",
    }


def _isolated_corroborated_tokens(evidence, key):
    """Require isolated ASR to confirm a mismatch from either full-file ASR.

    Both full-file recognizers use the same chunk time boundaries, so timestamp
    drift can assign the same neighbouring word to both.  The independently cut
    span is the boundary-safe witness.  CTC severe failures remain hard failures
    without this consensus because they detect acoustically absent text.
    """
    if len(evidence) < 3:
        return []
    isolated = set(evidence[-1].get(key, []))
    full_file = set()
    for item in evidence[:-1]:
        full_file.update(item.get(key, []))
    return sorted(isolated & full_file)


def review_strict_final_audio(
        audio_path, entries, spans, args, primary_results,
        primary_words_by_chunk, mlx_transcriber, strict_session):
    """Multi-signal, fail-closed review of the exact publish candidate."""
    expected_text = " ".join(
        entry["text"].replace("\n", " ") for entry in entries
    )
    aligned_words = strict_session.align(
        audio_path,
        expected_text,
        args.ctc_align_model,
        batch_size=args.ctc_batch_size,
    )
    if aligned_words is None:
        raise VerificationUnavailableError(
            "CTC forced alignment failed: "
            f"{strict_session.last_error or 'unknown error'}. Install "
            "requirements-strict-verification.txt; unchecked audio will not be published."
        )
    ctc_by_chunk = split_ctc_alignment(entries, aligned_words)
    span_by_id = {span["id"]: span for span in spans}
    uses_fast_verify = args.fast_verify and not args.verify
    preliminary = {}
    secondary_ids = set()
    clip_timestamps = []
    for entry in entries:
        cid = entry["id"]
        primary_score, primary_reason = primary_results[cid]
        primary_words = primary_words_by_chunk.get(cid, [])
        primary_heard = " ".join(
            word.get("word", "") for word in primary_words
        )
        primary_evidence = transcript_evidence(entry["text"], primary_heard)
        ctc_evidence = ctc_alignment_evidence(
            ctc_by_chunk[cid],
            mean_floor=args.ctc_mean_score_floor,
            word_floor=args.ctc_word_score_floor,
            critical_floor=args.ctc_critical_score_floor,
            consecutive_bad_words=args.ctc_consecutive_bad_words,
        )
        primary_failed = not verification_passed(
            primary_score, primary_reason, args.verify, uses_fast_verify,
            args.verify_threshold,
        )
        preliminary[cid] = {
            "primary_score": primary_score,
            "primary_reason": primary_reason,
            "primary_words": primary_words,
            "primary_heard": primary_heard,
            "primary": primary_evidence,
            "primary_failed": primary_failed,
            "ctc": ctc_evidence,
        }
        # Large-v3 is the expensive corroborating witness.  Run it only where
        # MLX, CTC, or a protected name warrants a second opinion; clean spans
        # have already passed two independent signal families.
        if (
            primary_failed
            or ctc_evidence["failed"]
            or bool(ctc_evidence["bad_words"])
            or primary_evidence["similarity"] < args.strict_similarity_floor
        ):
            secondary_ids.add(cid)
            span = span_by_id[cid]
            clip_timestamps.extend([span["start"], span["end"]])

    secondary_by_chunk = {}
    if clip_timestamps:
        secondary_payload = strict_session.transcribe(
            audio_path, args.secondary_verify_model,
            cpu_threads=args.secondary_verify_threads,
            clip_timestamps=clip_timestamps,
        )
        if not secondary_payload:
            raise VerificationUnavailableError(
                "independent faster-whisper verification failed: "
                f"{strict_session.last_error or 'unknown error'}; "
                "unchecked audio will not be published"
            )
        secondary_words = payload_words(secondary_payload)
        if not secondary_words:
            raise VerificationUnavailableError(
                "independent faster-whisper returned no words for all suspect "
                "spans; unchecked audio will not be published"
            )
        secondary_by_chunk = assign_words_to_chunk_spans(
            secondary_words, spans
        )

    strict_results = {}
    details = {}
    acoustic_markers = (
        "swallowed ", "dragged ", "uncertain ", "local tempo ",
    )

    for entry in entries:
        cid = entry["id"]
        initial = preliminary[cid]
        primary_score = initial["primary_score"]
        primary_reason = initial["primary_reason"]
        primary_words = initial["primary_words"]
        primary_heard = initial["primary_heard"]
        primary_evidence = initial["primary"]
        primary_failed = initial["primary_failed"]
        ctc_evidence = initial["ctc"]
        secondary_chunk_words = secondary_by_chunk.get(cid, [])
        secondary_heard = " ".join(
            word.get("word", "") for word in secondary_chunk_words
        )
        secondary_evidence = transcript_evidence(
            entry["text"],
            secondary_heard if cid in secondary_ids else entry["text"],
        )
        secondary_evidence["skipped_clean"] = cid not in secondary_ids
        protected_missing = sorted(set(
            missing_protected_terms(entry["text"], primary_heard)
            + (
                missing_protected_terms(entry["text"], secondary_heard)
                if cid in secondary_ids else []
            )
        ))
        suspect = (
            primary_failed
            or ctc_evidence["failed"]
            or secondary_evidence["similarity"] < args.strict_similarity_floor
            or secondary_evidence["longest_delete"] >= args.strict_dropped_words
            or bool(protected_missing)
        )

        isolated_heard = None
        isolated_evidence = None
        if suspect:
            span = span_by_id[cid]
            isolated_heard = clause_asr_transcript_span(
                audio_path, args.verify_model, primary_words,
                span["start"], span["end"], transcriber=mlx_transcriber,
            )
            if isolated_heard is None:
                raise VerificationUnavailableError(
                    f"{cid}: isolated final-artifact ASR failed; "
                    "unchecked audio will not be published"
                )
            isolated_evidence = transcript_evidence(
                entry["text"], isolated_heard
            )

        evidence = [primary_evidence, secondary_evidence]
        if isolated_evidence is not None:
            evidence.append(isolated_evidence)
        corroborated_expected = _isolated_corroborated_tokens(
            evidence, "changed_expected"
        )
        corroborated_insertions = _isolated_corroborated_tokens(
            evidence, "insertions"
        )
        reasons = []
        if any(marker in primary_reason for marker in acoustic_markers):
            reasons.append(f"acoustic defect: {primary_reason}")
        if ctc_evidence["failed"]:
            reasons.append(f"CTC alignment: {ctc_evidence['reason']}")
        if isolated_evidence is not None:
            if isolated_evidence["similarity"] < args.strict_similarity_floor:
                reasons.append(
                    "isolated ASR similarity "
                    f"{isolated_evidence['similarity']:.3f} < "
                    f"{args.strict_similarity_floor:.3f}"
                )
            if isolated_evidence["longest_delete"] >= args.strict_dropped_words:
                reasons.append(
                    "isolated ASR dropped at least "
                    f"{isolated_evidence['longest_delete']} expected words"
                )
        if corroborated_expected:
            reasons.append(
                "independent verifiers changed the same expected token(s): "
                + ", ".join(corroborated_expected[:8])
            )
        if corroborated_insertions:
            reasons.append(
                "independent verifiers heard the same insertion(s): "
                + ", ".join(corroborated_insertions[:8])
            )
        if isolated_heard is not None:
            repeated_missing_names = set(
                missing_protected_terms(entry["text"], isolated_heard)
            ) & set(protected_missing)
            if repeated_missing_names:
                reasons.append(
                    "protected term mismatch: "
                    + ", ".join(sorted(repeated_missing_names))
                )

        scores = [primary_score, secondary_evidence["similarity"]]
        if isolated_evidence is not None:
            scores.append(isolated_evidence["similarity"])
        score = min(scores)
        passed = not reasons
        reason = (
            f"ok (strict final {score:.3f})"
            if passed else "; ".join(dict.fromkeys(reasons))
        )
        strict_results[cid] = (score, reason)
        details[cid] = {
            "passed": passed,
            "score": score,
            "reason": reason,
            "primary_reason": primary_reason,
            "primary": primary_evidence,
            "secondary": secondary_evidence,
            "isolated": isolated_evidence,
            "isolated_heard": isolated_heard,
            "ctc": ctc_evidence,
        }
    return strict_results, details


# ---------------------------------------------------------------------------
# OmniVoice invocation
# ---------------------------------------------------------------------------
def build_entry(chunk_id, text, args):
    entry = {
        "id": chunk_id,
        "text": text,
        "language_id": args.language,
        "speed": args.speed,
    }
    if args.ref_audio:
        entry["ref_audio"] = args.ref_audio
    # ref_text is a required field in OmniVoice's JSONL reader; always emit it.
    entry["ref_text"] = args.ref_text if args.ref_text is not None else ""
    return entry


def _word_limited_tail(text, max_words):
    words = text.replace("\n", " ").split()
    if max_words <= 0 or len(words) <= max_words:
        return text.strip()
    return " ".join(words[-max_words:])


def _word_limited_head(text, max_words):
    words = text.replace("\n", " ").split()
    if max_words <= 0 or len(words) <= max_words:
        return text.strip()
    return " ".join(words[:max_words])


def _context_piece(text, max_words, tail):
    if not text:
        return ""
    piece = _word_limited_tail(text, max_words) if tail else _word_limited_head(
        text, max_words
    )
    return ensure_terminal_punctuation(piece.strip()) if piece.strip() else ""


def context_render_parts(entries, entry_id, args):
    index_by_id = {entry["id"]: index for index, entry in enumerate(entries)}
    index = index_by_id[entry_id]
    entry = entries[index]
    previous_text = entries[index - 1]["text"] if index > 0 else ""
    next_text = entries[index + 1]["text"] if index + 1 < len(entries) else ""
    prefix = _context_piece(previous_text, args.context_preroll_words, tail=True)
    suffix = _context_piece(next_text, args.context_postroll_words, tail=False)
    parts = [part for part in (prefix, entry["text"], suffix) if part.strip()]
    return {
        "id": entry_id,
        "prefix": prefix,
        "target": entry["text"],
        "suffix": suffix,
        "render_text": " ".join(parts),
    }


def build_context_render_entries(entries, pending_ids, args, direct_ids=None):
    direct_ids = set(direct_ids or ())
    parts_by_id = {}
    render_entries = []
    for cid in pending_ids:
        if cid in direct_ids:
            target = next(entry["text"] for entry in entries if entry["id"] == cid)
            parts = {
                "id": cid,
                "prefix": "",
                "target": target,
                "suffix": "",
                "render_text": target,
                "direct": True,
            }
        else:
            parts = context_render_parts(entries, cid, args)
        parts_by_id[cid] = parts
        render_entries.append(build_entry(cid, parts["render_text"], args))
    return render_entries, parts_by_id


def extract_audio_span(input_path, output_path, start, end):
    if end <= start:
        return False
    temp_output = f"{output_path}.tmp.wav"
    try:
        subprocess.run(
            [
                "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
                "-ss", f"{start:.3f}", "-to", f"{end:.3f}",
                "-i", input_path,
                "-ac", "1", "-ar", "24000", "-c:a", "pcm_f32le",
                temp_output,
            ],
            check=True,
        )
        os.replace(temp_output, output_path)
        return True
    except (subprocess.CalledProcessError, OSError):
        if os.path.exists(temp_output):
            os.unlink(temp_output)
        return False


def materialize_context_render(
        context_path, output_path, parts, args, transcriber=None):
    if parts.get("direct"):
        try:
            shutil.copy2(context_path, output_path)
            return True, "direct retry (context alignment bypassed)"
        except OSError:
            return False, "could not copy direct retry render"
    transcribed = transcribe_word_timestamps(
        context_path, args.verify_model, transcriber=transcriber
    )
    if transcribed is None:
        return False, "context ASR failed"
    _payload, words = transcribed
    span = context_target_span_from_words(
        parts["render_text"], parts["prefix"], parts["target"], words,
        pad_start=args.context_cut_pad_start,
        pad_end=args.context_cut_pad_end,
        min_ratio=args.context_min_alignment,
    )
    if span is None:
        return False, "could not align context render to target chunk"
    if not extract_audio_span(context_path, output_path, span[0], span[1]):
        return False, "could not cut context render"
    return True, f"context cut {span[0]:.2f}-{span[1]:.2f}s"


def materialize_context_renders(
        pending_ids, context_dir, output_dir, parts_by_id, args, transcriber=None):
    failures = []
    for cid in pending_ids:
        context_path = os.path.join(context_dir, f"{cid}.wav")
        output_path = os.path.join(output_dir, f"{cid}.wav")
        if not os.path.exists(context_path):
            print(f"  ! {cid}: missing context render")
            failures.append(cid)
            continue
        ok, reason = materialize_context_render(
            context_path, output_path, parts_by_id[cid], args,
            transcriber=transcriber,
        )
        if not ok:
            print(f"  ! {cid}: {reason}")
            failures.append(cid)
    return failures


def write_jsonl(entries, path):
    with open(path, "w", encoding="utf-8") as fh:
        for entry in entries:
            fh.write(json.dumps(entry, ensure_ascii=False) + "\n")


def read_jsonl_texts(path):
    """Read the previous chunk text before a resume run overwrites its JSONL."""
    texts = {}
    if not os.path.exists(path):
        return texts
    try:
        with open(path, "r", encoding="utf-8") as fh:
            for line in fh:
                if not line.strip():
                    continue
                entry = json.loads(line)
                if "id" in entry and "text" in entry:
                    texts[entry["id"]] = entry["text"]
    except (OSError, ValueError, json.JSONDecodeError):
        return {}
    return texts


def write_qa_report(path, status, audio_path, attempts, details, error=None):
    """Atomically record why a candidate was published or rejected."""
    payload = {
        "status": status,
        "audio": os.path.abspath(audio_path) if audio_path else None,
        "attempts": attempts,
        "failed_chunks": sorted(
            cid for cid, item in details.items() if not item.get("passed")
        ),
        "chunks": details,
    }
    if error:
        payload["error"] = str(error)
    temporary = f"{path}.tmp"
    with open(temporary, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    os.replace(temporary, path)


def publish_verified_candidate(candidate_path, output_path, details):
    """Atomically publish only when every strict-QA chunk passed."""
    failed = [
        cid for cid, item in details.items() if not item.get("passed", False)
    ]
    if failed:
        raise AudioQualityError(
            "refusing to publish candidate with failed chunks: "
            + ", ".join(sorted(failed))
        )
    if not details:
        raise AudioQualityError(
            "refusing to publish candidate without a QA decision"
        )
    if not os.path.exists(candidate_path):
        raise AudioQualityError(
            "verified candidate disappeared before publication"
        )
    os.replace(candidate_path, output_path)


def retry_position_temperature(base, attempt):
    """Choose a retry temperature that produces a genuinely different take.

    The measured best baseline is 2.0. Retry 1 samples 2.0 again (stochastic),
    then later retries increase diversity to 3.0, 4.0, ... . A user-selected
    higher base is never lowered. attempt==0 always keeps the requested base.
    """
    if attempt <= 0:
        return base
    return max(base, min(3.0, float(attempt + 1)))


def verification_passed(score, reason, verify, fast_verify, threshold):
    """Return whether a reviewed take is safe to accept.

    Fast verification reports a diagnostic score so failed takes can still be
    ranked against one another. That score is not its pass/fail signal: a
    dragged or swallowed syllable can retain 1.000 ASR similarity. Only an
    explicit ``ok`` result means the fast checks found no defect.
    """
    if verify:
        return score >= threshold
    if fast_verify:
        return score > 0 and reason.startswith("ok")
    return score > 0


def resume_start_attempt(failed_existing, missing, max_retries):
    """Count a rejected existing take as the baseline attempt during resume."""
    if failed_existing and not missing and max_retries > 0:
        return 1
    return 0


def run_omnivoice(jsonl_path, chunk_dir, args, run_env, position_temperature=None):
    cmd = [
        OMNIVOICE_BIN,
        "--test_list", jsonl_path,
        "--res_dir", chunk_dir,
        "--lang_id", args.language,
        "--model", args.model,
    ]

    num_step = args.num_step if args.num_step is not None else QUALITY_PRESETS[args.quality]
    if position_temperature is None:
        position_temperature = args.position_temperature
    optional_args = {
        "--num_step": num_step,
        "--position_temperature": position_temperature,
        "--batch_size": args.batch_size,
        "--batch_duration": args.batch_duration,
        "--nj_per_gpu": args.nj_per_gpu,
        "--warmup": args.warmup,
        "--audio_chunk_duration": args.audio_chunk_duration,
        "--audio_chunk_threshold": args.audio_chunk_threshold,
    }
    for option, value in optional_args.items():
        if value is not None:
            cmd.extend([option, str(value)])

    subprocess.run(cmd, check=True, env=run_env)


# ---------------------------------------------------------------------------
# Concatenation
# ---------------------------------------------------------------------------
def ffmpeg_concat_escape(path):
    return str(path).replace("'", "'\\''")


def concatenate_audio_files(audio_paths, output_path, work_dir):
    concat_list_path = os.path.join(work_dir, "concat.txt")
    with open(concat_list_path, "w", encoding="utf-8") as f:
        for audio_path in audio_paths:
            f.write(f"file '{ffmpeg_concat_escape(os.path.abspath(audio_path))}'\n")

    cmd = [
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
        "-f", "concat", "-safe", "0", "-i", concat_list_path,
        "-c", "copy", output_path,
    ]
    subprocess.run(cmd, check=True)


def _rms_db(value):
    return 20.0 * math.log10(max(value, 1e-10))


def _speech_frame_levels(samples, sample_rate, start_s, end_s,
                         frame_ms=30, hop_ms=10):
    if samples is None:
        return []
    start = max(0, int(start_s * sample_rate))
    end = min(len(samples), int(end_s * sample_rate))
    frame = max(1, int(frame_ms * sample_rate / 1000))
    hop = max(1, int(hop_ms * sample_rate / 1000))
    if end - start < frame:
        return []

    levels = []
    if np is not None:
        segment = samples[start:end]
        count = 1 + (len(segment) - frame) // hop
        for index in range(count):
            lo = index * hop
            window = segment[lo:lo + frame]
            rms = float(np.sqrt(np.mean(np.square(window, dtype=np.float64))))
            levels.append(_rms_db(rms))
    else:
        for lo in range(start, end - frame + 1, hop):
            window = samples[lo:lo + frame]
            rms = math.sqrt(sum(float(x) * float(x) for x in window) / frame)
            levels.append(_rms_db(rms))
    if not levels:
        return []
    gate = max(max(levels) - 32.0, -48.0)
    return [level for level in levels if level >= gate]


def _speech_frame_levels_with_times(samples, sample_rate, start_s, end_s,
                                    frame_ms=50, hop_ms=25):
    if samples is None:
        return []
    start = max(0, int(start_s * sample_rate))
    end = min(len(samples), int(end_s * sample_rate))
    frame = max(1, int(frame_ms * sample_rate / 1000))
    hop = max(1, int(hop_ms * sample_rate / 1000))
    if end - start < frame:
        return []

    rows = []
    if np is not None:
        segment = samples[start:end]
        count = 1 + (len(segment) - frame) // hop
        for index in range(count):
            lo = index * hop
            window = segment[lo:lo + frame]
            rms = float(np.sqrt(np.mean(np.square(window, dtype=np.float64))))
            rows.append((start_s + lo / sample_rate, _rms_db(rms)))
    else:
        for lo in range(start, end - frame + 1, hop):
            window = samples[lo:lo + frame]
            rms = math.sqrt(sum(float(x) * float(x) for x in window) / frame)
            rows.append((lo / sample_rate, _rms_db(rms)))
    if not rows:
        return []
    gate = max(max(level for _time, level in rows) - 32.0, -48.0)
    return [(time, level) for time, level in rows if level >= gate]


def _median_speech_db(samples, sample_rate, start_s, end_s):
    levels = _speech_frame_levels(samples, sample_rate, start_s, end_s)
    return median(levels) if levels else None


def _window_rms_db(samples, sample_rate, start_s, end_s):
    start = max(0, int(start_s * sample_rate))
    end = min(len(samples), int(end_s * sample_rate))
    if end <= start:
        return None
    segment = samples[start:end]
    if np is not None:
        rms = float(np.sqrt(np.mean(np.square(segment, dtype=np.float64))))
    else:
        rms = math.sqrt(sum(float(x) * float(x) for x in segment) / len(segment))
    return _rms_db(rms)


def opening_level_adjustment(path, head_window=0.8, body_window=2.4,
                             min_gain_db=1.5, max_gain_db=7.0,
                             release=0.9, attack_window=0.45,
                             attack_min_gain_db=1.5,
                             attack_max_gain_db=7.0,
                             attack_release=0.65,
                             attack_extra_gain_db=3.0,
                             sample_rate=16000):
    """Return (gain_db, release_seconds) for a quiet chunk opening."""
    samples = _decode_samples(path, sample_rate)
    if samples is None or len(samples) < int(0.8 * sample_rate):
        return 0.0, release
    duration = len(samples) / sample_rate
    head = _median_speech_db(samples, sample_rate, 0.0, min(head_window, duration))
    body_start = min(head_window, duration)
    body_end = min(duration, body_start + body_window)
    body = _median_speech_db(samples, sample_rate, body_start, body_end)
    if head is None or body is None:
        return 0.0, release
    needed = body - head
    if needed >= min_gain_db:
        return min(needed, max_gain_db), release

    # A chunk can have a very short dip right at the opening while the rest of
    # the first 0.8s is already fine. Measure this window as raw RMS so a brief
    # gap between syllables still counts; speech-frame medians hide that dip.
    attack = _window_rms_db(samples, sample_rate, 0.0, min(attack_window, duration))
    if attack is None:
        return 0.0, release
    attack_need = body - attack
    if attack_need >= attack_min_gain_db:
        return min(attack_need + attack_extra_gain_db, attack_max_gain_db), attack_release
    return 0.0, release


def leading_silence_trim_seconds(path, max_trim=0.18, keep=0.0,
                                 min_trim=0.025, sample_rate=16000):
    """Return a conservative leading-silence trim for a stitch-only file."""
    if max_trim <= 0.0:
        return 0.0
    samples = _decode_samples(path, sample_rate)
    if samples is None:
        return 0.0
    duration = len(samples) / sample_rate
    rows = _speech_frame_levels_with_times(
        samples, sample_rate, 0.0, min(0.6, duration),
        frame_ms=30, hop_ms=10,
    )
    if not rows:
        return 0.0
    onset, _level = rows[0]
    trim = min(max_trim, max(0.0, onset - keep))
    return trim if trim >= min_trim else 0.0


def trailing_silence_trim_seconds(path, max_trim=0.20, keep=0.0,
                                  min_trim=0.025, sample_rate=16000):
    """Return a conservative trailing-silence trim for a stitch-only file."""
    if max_trim <= 0.0:
        return 0.0
    samples = _decode_samples(path, sample_rate)
    if samples is None:
        return 0.0
    duration = len(samples) / sample_rate
    start = max(0.0, duration - 0.8)
    rows = _speech_frame_levels_with_times(
        samples, sample_rate, start, duration,
        frame_ms=30, hop_ms=10,
    )
    if not rows:
        return 0.0
    last_time, _level = rows[-1]
    last_speech_end = last_time + 0.03
    trim = min(max_trim, max(0.0, duration - (last_speech_end + keep)))
    return trim if trim >= min_trim else 0.0


def opening_level_gain_db(path, head_window=0.8, body_window=2.4,
                          min_gain_db=2.0, max_gain_db=5.0,
                          sample_rate=16000):
    """Gain needed to keep a chunk opening from dipping below its body."""
    gain, _release = opening_level_adjustment(
        path, head_window=head_window, body_window=body_window,
        min_gain_db=min_gain_db, max_gain_db=max_gain_db,
        sample_rate=sample_rate,
    )
    return gain


def apply_opening_gain(path, output, gain_db, release, trim_seconds=0.0,
                       trim_end_seconds=0.0,
                       sample_rate=24000):
    samples = _decode_samples(path, sample_rate)
    if samples is None:
        return False
    gain = 10 ** (gain_db / 20.0)
    count = min(len(samples), max(1, int(release * sample_rate)))
    if np is not None:
        adjusted = np.array(samples, dtype=np.float32, copy=True)
        envelope = 1.0 + (gain - 1.0) * (
            1.0 - np.arange(count, dtype=np.float32) / float(count)
        )
        adjusted[:count] *= envelope
        np.clip(adjusted, -0.98, 0.98, out=adjusted)
        raw = adjusted.astype(np.float32).tobytes()
    else:
        adjusted = array.array("f", samples)
        for index in range(count):
            factor = 1.0 + (gain - 1.0) * (1.0 - index / float(count))
            value = adjusted[index] * factor
            adjusted[index] = max(-0.98, min(0.98, value))
    trim_samples = min(len(adjusted), max(0, int(trim_seconds * sample_rate)))
    if trim_samples:
        adjusted = adjusted[trim_samples:]
    trim_end_samples = min(len(adjusted), max(0, int(trim_end_seconds * sample_rate)))
    if trim_end_samples:
        adjusted = adjusted[:-trim_end_samples]
    raw = adjusted.astype(np.float32).tobytes() if np is not None else adjusted.tobytes()
    subprocess.run(
        [
            "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
            "-f", "f32le", "-ar", str(sample_rate), "-ac", "1", "-i", "-",
            "-c:a", "pcm_f32le", output,
        ],
        input=raw,
        check=True,
    )
    return True


def prepare_stitch_audio_files(audio_paths, work_dir, args):
    """Return paths to audio files with quiet chunk openings gently leveled."""
    if not args.stitch_leveling:
        return audio_paths

    stitch_dir = os.path.join(work_dir, ".stitch")
    os.makedirs(stitch_dir, exist_ok=True)
    stitched = []
    boosts = []
    trims = []
    tail_trims = []
    for path in audio_paths:
        gain_db, release = opening_level_adjustment(
            path,
            head_window=args.stitch_head_window,
            body_window=args.stitch_body_window,
            min_gain_db=args.stitch_min_gain_db,
            max_gain_db=args.stitch_max_gain_db,
            release=args.stitch_release,
            attack_window=args.stitch_attack_window,
            attack_min_gain_db=args.stitch_attack_min_gain_db,
            attack_max_gain_db=args.stitch_attack_max_gain_db,
            attack_release=args.stitch_attack_release,
            attack_extra_gain_db=args.stitch_attack_extra_gain_db,
        )
        trim_seconds = (
            leading_silence_trim_seconds(
                path,
                max_trim=args.stitch_max_trim,
                keep=args.stitch_trim_keep,
            )
            if args.stitch_trim_leading_silence else 0.0
        )
        trim_end_seconds = (
            trailing_silence_trim_seconds(
                path,
                max_trim=args.stitch_max_tail_trim,
                keep=args.stitch_tail_trim_keep,
            )
            if args.stitch_trim_trailing_silence else 0.0
        )
        if gain_db <= 0.0 and trim_seconds <= 0.0 and trim_end_seconds <= 0.0:
            stitched.append(path)
            continue
        output = os.path.join(stitch_dir, os.path.basename(path))
        if apply_opening_gain(
                path, output, gain_db, max(release, 0.05),
                trim_seconds=trim_seconds,
                trim_end_seconds=trim_end_seconds):
            stitched.append(output)
            if gain_db > 0.0:
                boosts.append(gain_db)
            if trim_seconds > 0.0:
                trims.append(trim_seconds)
            if trim_end_seconds > 0.0:
                tail_trims.append(trim_end_seconds)
        else:
            stitched.append(path)

    if boosts:
        print(
            f"Stitch leveling: boosted {len(boosts)} chunk opening(s), "
            f"max {max(boosts):.1f} dB."
        )
    if trims:
        print(
            f"Stitch trimming: trimmed {len(trims)} leading silence(s), "
            f"max {max(trims) * 1000:.0f} ms."
        )
    if tail_trims:
        print(
            f"Stitch trimming: trimmed {len(tail_trims)} trailing silence(s), "
            f"max {max(tail_trims) * 1000:.0f} ms."
        )
    return stitched


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="Convert Markdown script to Audio using OmniVoice")
    parser.add_argument("--input", "-i", required=True, help="Input Markdown file path")
    parser.add_argument("--output_dir", "-o", default="/Users/truongdv/Documents/projects/video-audio/results", help="Output directory for audio files")
    parser.add_argument("--model", "-m", default="k2-fsa/OmniVoice", help="Model checkpoint path or HF repo id")
    parser.add_argument("--language", "-l", default="vi", help="Language ID (e.g. 'vi', 'en')")

    parser.add_argument("--voice", default=DEFAULT_VOICE, help="Voice profile name to look up in the OmniVoice DB (default: NGOC HUYEN V2).")
    parser.add_argument("--ref_audio", "-r", default=None, help="Override reference audio path (otherwise resolved from --voice).")
    parser.add_argument("--ref_text", "-t", default=None, help="Override reference transcript (otherwise resolved from --voice).")

    parser.add_argument("--speed", "-s", type=float, default=1.0,
                        help="Reading speed multiplier. Leave at 1.0. Moving away from the "
                        "reference clip's own pace degrades pronunciation sharply — slowing down "
                        "to 0.92, to give each syllable more room, garbled 6/6 samples (one down "
                        "to 0.72 similarity) where 1.0 garbled 2/6 on the same text.")
    parser.add_argument("--max_chunk_chars", type=int, default=420, help="Maximum characters per chunk. Use 0 to disable chunking.")
    parser.add_argument("--max_chunk_words", type=int, default=60, help="Maximum words per chunk (shorter chunks reduce OmniVoice word errors).")
    parser.add_argument("--pron_dict", default=None,
                        help="Path to a JSON file of {term: spoken_form} pronunciation "
                        "overrides. Applied before every built-in rule, so it also "
                        "overrides the built-in reading of an acronym, and is the place "
                        "to teach the script an acronym it does not know.")
    parser.add_argument("--keep_chunks", action="store_true", help="Keep intermediate chunk WAV files after creating the final audio.")
    parser.add_argument("--context_preroll", action=argparse.BooleanOptionalAction,
                        default=True,
                        help="Render each chunk with a short tail from the previous chunk and "
                        "a preview of the next chunk, then cut the target chunk back out with "
                        "Whisper word timestamps. This prevents the first real word after a "
                        "boundary from being the model's cold-start word.")
    parser.add_argument("--context_preroll_words", type=int, default=24,
                        help="Maximum previous-chunk words to prepend as TTS context.")
    parser.add_argument("--context_postroll_words", type=int, default=12,
                        help="Maximum next-chunk words to append as TTS context, then discard.")
    parser.add_argument("--context_cut_pad_start", type=float, default=0.06,
                        help="Seconds kept before the first aligned target word when cutting "
                        "a context render.")
    parser.add_argument("--context_cut_pad_end", type=float, default=0.08,
                        help="Seconds kept after the last aligned target word when cutting "
                        "a context render.")
    parser.add_argument("--context_min_alignment", type=float, default=0.90,
                        help="Minimum fuzzy token-alignment score accepted when cutting "
                        "a context render.")
    parser.add_argument("--keep_context_renders", action="store_true",
                        help="Keep .context WAV renders for debugging context cuts.")
    parser.add_argument("--stitch_leveling", action=argparse.BooleanOptionalAction,
                        default=True,
                        help="Before concatenation, gently lift chunk openings whose speech RMS "
                        "starts much lower than the chunk body. This smooths the audible volume "
                        "dip at chunk boundaries. Use --no-stitch_leveling for a raw concat.")
    parser.add_argument("--stitch_head_window", type=float, default=0.8,
                        help="Seconds at the start of each chunk used to measure opening level.")
    parser.add_argument("--stitch_body_window", type=float, default=2.4,
                        help="Seconds after the opening window used as the chunk-body reference.")
    parser.add_argument("--stitch_min_gain_db", type=float, default=1.5,
                        help="Only level a chunk opening when it is at least this many dB below "
                        "the body.")
    parser.add_argument("--stitch_max_gain_db", type=float, default=7.0,
                        help="Maximum opening boost applied by stitch leveling.")
    parser.add_argument("--stitch_release", type=float, default=0.9,
                        help="Seconds for the opening boost to fade back to normal volume.")
    parser.add_argument("--stitch_attack_window", type=float, default=0.45,
                        help="Seconds at the raw start of each chunk used to catch very short "
                        "opening dips that speech-frame medians can hide.")
    parser.add_argument("--stitch_attack_min_gain_db", type=float, default=1.5,
                        help="Only apply the short attack fix when the first raw opening window "
                        "is at least this many dB below the body.")
    parser.add_argument("--stitch_attack_max_gain_db", type=float, default=7.0,
                        help="Maximum boost for the short attack fix.")
    parser.add_argument("--stitch_attack_extra_gain_db", type=float, default=3.0,
                        help="Extra boost added to detected short attack dips before capping.")
    parser.add_argument("--stitch_attack_release", type=float, default=0.65,
                        help="Seconds for the short attack boost to fade back to normal volume.")
    parser.add_argument("--stitch_trim_leading_silence", action=argparse.BooleanOptionalAction,
                        default=True,
                        help="Trim tiny leading silences from stitch-only chunk copies before "
                        "concatenation. Original chunk WAV files are not modified.")
    parser.add_argument("--stitch_max_trim", type=float, default=0.18,
                        help="Maximum seconds of leading silence to trim from each stitch copy.")
    parser.add_argument("--stitch_trim_keep", type=float, default=0.0,
                        help="Seconds of cushion to keep before detected speech when trimming.")
    parser.add_argument("--stitch_trim_trailing_silence", action=argparse.BooleanOptionalAction,
                        default=True,
                        help="Trim tiny trailing silences from stitch-only chunk copies before "
                        "concatenation, keeping a small cushion after detected speech.")
    parser.add_argument("--stitch_max_tail_trim", type=float, default=0.20,
                        help="Maximum seconds of trailing silence to trim from each stitch copy.")
    parser.add_argument("--stitch_tail_trim_keep", type=float, default=0.0,
                        help="Seconds of cushion to keep after detected speech when trimming.")
    parser.add_argument("--dry_run", action="store_true", help="Only generate the JSONL and print chunk info; do not run OmniVoice.")
    parser.add_argument("--limit", type=int, default=None,
                        help="Render only the first N chunks. For testing settings without paying "
                        "for the whole story; skips concatenation.")
    parser.add_argument("--only", default=None,
                        help="Render only these chunks, by 1-based index or id suffix, comma "
                        "separated (e.g. '40,73' or '0040'). Skips concatenation.")

    # Quality-control / anti-error mechanisms
    parser.add_argument("--max_retries", type=int, default=6,
                        help="Re-render chunks that fail validation, up to this many extra passes. "
                        "If any chunk still fails, the final WAV is not published.")
    parser.add_argument("--resume", action="store_true", help="Reuse existing valid chunk WAVs instead of re-rendering them.")
    parser.add_argument("--verify", action="store_true",
                        help="Verify the assembled audio with Whisper, map mismatched spans back "
                        "to chunk IDs, then retry all failed chunks together.")
    parser.add_argument("--fast_verify", action=argparse.BooleanOptionalAction,
                        default=True,
                        help="Adaptive quality gate: one Whisper pass over the assembled audio "
                        "catches strong word mismatches, low-confidence stretched words, "
                        "swallowed audio, and local tempo bursts, then maps failures back to "
                        "chunk IDs. Only ambiguous scores pay for clause-isolated ASR when "
                        "--adaptive_verify is enabled. On by default; use --no-fast_verify only "
                        "for unchecked previews.")
    parser.add_argument("--adaptive_verify", action=argparse.BooleanOptionalAction,
                        default=True,
                        help="For borderline assembled-audio ASR results, run the slower clause "
                        "probe inside that chunk span before deciding whether to retry.")
    parser.add_argument("--fast_similarity_floor", type=float, default=0.94,
                        help="Assembled-audio chunk similarity below this is a strong failure; "
                        "scores between this and --verify_threshold use adaptive clause ASR when "
                        "--adaptive_verify is enabled.")
    parser.add_argument("--word_probability_floor", type=float, default=0.78,
                        help="Whisper probability floor used with --word_duration_ratio to detect "
                        "a context-repaired but acoustically malformed word.")
    parser.add_argument("--word_duration_ratio", type=float, default=2.4,
                        help="A low-confidence word must also last at least this many times the "
                        "chunk median before it triggers a retry.")
    parser.add_argument("--min_local_wps", type=float, default=1.6,
                        help="Retry a five-word window slower than this many words/second.")
    parser.add_argument("--max_local_wps", type=float, default=9.0,
                        help="Retry a five-word window faster than this many words/second.")
    parser.add_argument("--dropped_words", type=int, default=1,
                        help="Retry when the assembled transcript appears to drop at least "
                        "this many consecutive expected words.")
    parser.add_argument("--drag_ratio", type=float, default=6.0,
                        help="Retry only when one word timestamp is this many times the chunk "
                        "median duration.")
    parser.add_argument("--retry_text_mismatch", action=argparse.BooleanOptionalAction,
                        default=True,
                        help="In fast verify, treat ASR text mismatch/dropped words as retry "
                        "signals. On by default; the strict final gate corroborates these with "
                        "forced alignment and an independent ASR before publication.")
    parser.add_argument("--retry_timing_anomalies", action=argparse.BooleanOptionalAction,
                        default=True,
                        help="In fast verify, treat low-confidence stretched words, dragged "
                        "timestamps, and local tempo bursts as retry signals. On by default.")
    parser.add_argument("--retry_empty_asr", action=argparse.BooleanOptionalAction,
                        default=True,
                        help="In fast verify, retry a chunk when the assembled-audio ASR maps no "
                        "words into its time span. On by default; empty evidence can never pass QA.")
    parser.add_argument("--verify_threshold", type=float, default=0.985,
                        help="ASR similarity at or above which a chunk is accepted immediately. "
                        "Below it the chunk is re-rendered and the best-scoring attempt kept — it "
                        "is NOT a pass/fail line, because no absolute one exists: a chunk's score "
                        "floor depends on its own text (proper names like 'Đường Hàn' cost more "
                        "similarity than a real dropped word does), so scores are only meaningful "
                        "compared against other attempts at the SAME chunk.")
    parser.add_argument("--verify_model", default="mlx-community/whisper-large-v3-turbo", help="mlx_whisper model used for --verify.")
    parser.add_argument("--strict_final_verify", action=argparse.BooleanOptionalAction,
                        default=True,
                        help="Verify the exact post-stitch publish candidate with CTC forced "
                        "alignment, independent faster-whisper ASR, and isolated MLX ASR. "
                        "Enabled by default; failures prevent creation of the final WAV.")
    parser.add_argument(
        "--ctc_align_model",
        default="MahmoudAshraf/mms-300m-1130-forced-aligner",
        help="Multilingual CTC model used to force-align the known transcript.",
    )
    parser.add_argument("--ctc_batch_size", type=int, default=1,
                        help="CTC emission batch size; 1 avoids memory spikes on Apple Silicon.")
    parser.add_argument("--ctc_mean_score_floor", type=float, default=-1.70,
                        help="Fail a chunk when its mean CTC log score is at or below this value.")
    parser.add_argument("--ctc_word_score_floor", type=float, default=-4.0,
                        help="CTC word score used to detect a run of acoustically absent words.")
    parser.add_argument("--ctc_critical_score_floor", type=float, default=-8.0,
                        help="One CTC word at or below this score is a hard alignment failure.")
    parser.add_argument("--ctc_consecutive_bad_words", type=int, default=2,
                        help="Number of adjacent low-scoring CTC words that hard-fails a chunk.")
    parser.add_argument(
        "--secondary_verify_model",
        default="Systran/faster-whisper-large-v3",
        help="Independent CTranslate2 Whisper model used by strict final verification.",
    )
    parser.add_argument("--secondary_verify_threads", type=int, default=4,
                        help="CPU threads for the independent faster-whisper verifier.")
    parser.add_argument("--strict_similarity_floor", type=float, default=0.94,
                        help="Minimum isolated token similarity accepted by strict final QA.")
    parser.add_argument("--strict_dropped_words", type=int, default=2,
                        help="Hard-fail an isolated ASR deletion of this many expected words.")
    parser.add_argument("--swallow_db", type=float, default=DEFAULT_FAST_SWALLOW_DB,
                        help="Fast-verify threshold for a word peak relative to its chunk median "
                        f"(default: {DEFAULT_FAST_SWALLOW_DB:g} dB). Raise it to make swallowed-syllable "
                        "detection more sensitive, lower it to reduce false positives for a "
                        "different cloned voice.")

    # Speed / OmniVoice tuning
    parser.add_argument("--quality", choices=list(QUALITY_PRESETS.keys()), default="balanced",
                        help="Speed/quality preset controlling num_step (high=32, balanced=16, "
                        "fast=8); decoding time is linear in it. 'balanced' (16) is the default "
                        "because it retained high clause-isolated ASR quality at about half the "
                        "time of 'high'. Do NOT drop "
                        "to 'fast' (8): that under-decodes and garbles words even at low "
                        "position_temperature (measured down to 0.899). Overridden by "
                        "--num_step.")
    parser.add_argument("--num_step", type=int, default=None, help="OmniVoice decoding steps (overrides --quality).")
    parser.add_argument("--position_temperature", type=float, default=2.0,
                        help="Randomness in WHICH masked positions OmniVoice commits each decoding "
                        "step (the model's own default is 5.0). This — not num_step or "
                        "class_temperature (already 0/greedy) — controls run-to-run variation. "
                        "Controlled 16-step benchmark on the same 13 real chunks: 0.0 passed "
                        "10/13, 1.0 passed 10/13, while 2.0 passed 25/25 across the full sample "
                        "and two independent repeats of the six hardest chunks. Therefore 2.0 is "
                        "the measured default. 0.0 remains reproducible but deterministically "
                        "drops an 8-word span in chunk 0004. Keep --fast_verify enabled: 2.0 is "
                        "stochastic, so a future bad take must be detected and re-sampled. Retries "
                        "sample 2.0 again, then raise to 3.0 for extra diversity.")
    parser.add_argument("--batch_size", type=int, default=1,
                        help="OmniVoice fixed batch size. KEEP THIS AT 1. Batching several chunks "
                        "into one generate() call corrupts some of them: OmniVoice pads a batch to "
                        "its longest member, and the short members reliably decode to noise instead "
                        "of speech. It is reproducible, not random, so retrying never rescues those "
                        "chunks. On Apple Silicon a single chunk already saturates the GPU, so "
                        "batching buys no speed either — batch_size=1 measured slightly FASTER than "
                        "2 and 6. Values >1 trade correctness for nothing.")
    parser.add_argument("--batch_duration", type=float, default=None,
                        help="OmniVoice max total duration per batch (seconds). Ignored entirely "
                        "while --batch_size > 0, which is the mode this script uses.")
    parser.add_argument("--nj_per_gpu", type=int, default=1,
                        help="OmniVoice worker processes per GPU. Each worker loads its own ~3GB "
                        "copy of the model, and on a single MPS GPU they just queue behind each "
                        "other: 2 workers measured ~2%% faster while cutting free RAM to ~21%% on a "
                        "16GB M1. 1 is the right value on Apple Silicon.")
    parser.add_argument("--warmup", type=int, default=0, help="OmniVoice warmup runs (0 is fastest for one-off jobs).")
    parser.add_argument("--audio_chunk_duration", type=float, default=None, help="OmniVoice internal audio chunk duration in seconds.")
    parser.add_argument("--audio_chunk_threshold", type=float, default=None, help="OmniVoice internal threshold for audio chunking in seconds.")

    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"Error: File '{args.input}' not found.")
        sys.exit(1)

    # Resolve the voice (ref_audio + ref_text) unless explicitly overridden.
    resolved_audio, resolved_text = resolve_voice(args.voice)
    if args.ref_audio is None:
        args.ref_audio = resolved_audio
    if args.ref_text is None:
        args.ref_text = resolved_text

    if args.ref_audio and not os.path.exists(args.ref_audio):
        print(f"Warning: reference audio not found: {args.ref_audio}")
    print(f"Voice: {args.voice}")
    print(f"  ref_audio: {args.ref_audio}")
    print(f"  ref_text : {'<set>' if args.ref_text else '<empty>'}")

    os.makedirs(args.output_dir, exist_ok=True)

    with open(args.input, "r", encoding="utf-8") as f:
        md_content = f.read()

    clean_text = clean_markdown(md_content)
    if not clean_text:
        print("Error: Extracted text is empty.")
        sys.exit(1)

    # Always on: OmniVoice has no Vietnamese pronunciation lexicon, so raw
    # digits/dates/units/acronyms are guessed from characters and come out
    # wrong ("ADN" -> "aden"). There is no unchecked-preview path around this
    # step, unlike --no-fast_verify for the audio-side checks.
    pron_dict = dict(DEFAULT_PRON_DICT)
    if args.pron_dict:
        with open(args.pron_dict, "r", encoding="utf-8") as fh:
            pron_dict.update(json.load(fh))
    clean_text = normalize_for_tts(clean_text, pron_dict)

    chunks = split_text_into_chunks(clean_text, args.max_chunk_chars, args.max_chunk_words)
    print(f"Text length: {len(clean_text)} characters")
    print(f"Generated {len(chunks)} chunk(s) (max_chars={args.max_chunk_chars}, max_words={args.max_chunk_words})")

    base_name = os.path.splitext(os.path.basename(args.input))[0]
    chunk_dir = os.path.join(args.output_dir, f"{base_name}_chunks")
    os.makedirs(chunk_dir, exist_ok=True)
    jsonl_path = os.path.join(chunk_dir, f"{base_name}.jsonl")
    previous_texts = read_jsonl_texts(jsonl_path)

    all_entries = [
        build_entry(f"{base_name}_{index:04d}", chunk, args)
        for index, chunk in enumerate(chunks, start=1)
    ]
    entries = list(all_entries)

    # A subset render is a test of settings, not a deliverable, so it never
    # concatenates: the final wav would silently be a fragment of the story.
    subset = args.limit is not None or args.only is not None
    if args.only:
        wanted = {token.strip().lstrip("0") or "0" for token in args.only.split(",")}
        entries = [entry for index, entry in enumerate(entries, start=1)
                   if str(index) in wanted or entry["id"].rsplit("_", 1)[1].lstrip("0") in wanted]
        if not entries:
            print(f"Error: --only '{args.only}' matched none of the {len(chunks)} chunks.")
            sys.exit(1)
    if args.limit is not None:
        entries = entries[:args.limit]
    if subset:
        # Keep the full-run JSONL intact so a later resume still sees every chunk.
        jsonl_path = os.path.join(chunk_dir, f"{base_name}_subset.jsonl")
        print(f"Subset render: {len(entries)} chunk(s) -> {', '.join(e['id'] for e in entries)}")
        print("Final audio will NOT be concatenated (subset renders are for testing).")

    write_jsonl(entries, jsonl_path)
    print(f"Generated JSONL file at: {jsonl_path}")

    if args.dry_run:
        for entry in entries:
            preview = entry["text"][:90].replace("\n", " ")
            suffix = "..." if len(entry["text"]) > 90 else ""
            print(f"{entry['id']}: {len(entry['text'])} chars | {preview}{suffix}")
        return

    if not os.path.exists(OMNIVOICE_BIN):
        print(f"Error: OmniVoice executable not found at {OMNIVOICE_BIN}")
        sys.exit(1)

    # Verification is a safety feature, so never silently turn it into a no-op.
    # Older code accepted every chunk when mlx_whisper was missing or crashed,
    # which looked like a successful checked render but provided no protection.
    uses_fast_verify = args.fast_verify and not args.verify
    needs_whisper = (
        args.verify or uses_fast_verify or args.context_preroll
        or args.strict_final_verify
    )
    if needs_whisper and not _whisper_bin():
        print("Error: mlx_whisper is required for verification/context preroll. "
              "Install it, use --no-fast_verify for unchecked previews, or "
              "use --no-context_preroll to render raw chunk starts.")
        sys.exit(1)
    # Fix macOS no_proxy IPv6 httpx parsing bug by cleaning env. This must be
    # done on os.environ itself, not just the run_env copy: the whisper
    # subprocesses in asr_similarity (--verify) inherit os.environ, and an "::1"
    # entry makes httpx raise InvalidURL, so asr_similarity returns None and
    # verification silently no-ops (every chunk "passes" unverified).
    sanitize_proxy_env()
    run_env = os.environ.copy()
    asr_session = MLXWhisperSession() if needs_whisper else None
    strict_session = StrictVerifierSession() if args.strict_final_verify else None

    entry_by_id = {entry["id"]: entry for entry in entries}
    chunk_path = lambda cid: os.path.join(chunk_dir, f"{cid}.wav")
    context_dir = os.path.join(chunk_dir, ".context")

    def run_reference_db():
        """Median chunk loudness across the whole run, to spot quiet outliers."""
        levels = []
        for entry in entries:
            stats = probe_chunk_stats(chunk_path(entry["id"]))
            if stats is not None and stats["mean_db"] > -55.0:
                levels.append(stats["mean_db"])
        # Below a handful of chunks the median is too noisy to judge against.
        return median(levels) if len(levels) >= 4 else None

    # Re-rendering is a genuine fix here: sampling is stochastic, so the same
    # text garbles different words (or none) each attempt. Scores are still only
    # comparable between attempts at the SAME chunk, so keep every attempt's
    # score and, when none clears the accept bar, fall back to the best one
    # rather than the last.
    best_dir = os.path.join(chunk_dir, ".best")
    best_score = {}
    best_rank = {}

    def bank_attempt(cid, accepted, score):
        rank = (int(accepted), score)
        if rank > best_rank.get(cid, (-1, -2.0)) and os.path.exists(chunk_path(cid)):
            best_rank[cid] = rank
            best_score[cid] = score
            os.makedirs(best_dir, exist_ok=True)
            shutil.copy2(chunk_path(cid), os.path.join(best_dir, f"{cid}.wav"))

    def score_chunk_file(cid, reference_db):
        """Cheap file-level health check before the assembled ASR pass."""
        entry = entry_by_id[cid]
        path = chunk_path(cid)
        ok, reason = validate_chunk_audio(path, entry["text"], args.speed,
                                          reference_db=reference_db)
        if not ok:
            return -1.0, reason
        return 1.0, "ok"

    def review_chunk_files(candidate_ids, bank_ok=False):
        """Return chunks whose WAV file is missing, silent, or duration-broken."""
        retry = []
        reference_db = run_reference_db()
        for cid in candidate_ids:
            score, reason = score_chunk_file(cid, reference_db)
            accepted = score > 0
            if bank_ok:
                bank_attempt(cid, accepted, score)
            if not accepted:
                print(f"  ! {cid}: {reason}")
                retry.append(cid)
        return retry

    def review_asr_results(results):
        """Bank assembled-audio verification results and return failed chunks."""
        retry = []
        for entry in entries:
            cid = entry["id"]
            score, reason = results[cid]
            accepted = (
                reason.startswith("ok")
                if args.strict_final_verify
                else verification_passed(
                    score, reason, args.verify, uses_fast_verify,
                    args.verify_threshold,
                )
            )
            bank_attempt(cid, accepted, score)
            if not accepted:
                print(f"  ! {cid}: {reason}")
                retry.append(cid)
        return retry

    def restore_best_attempts():
        """Put each chunk's best-scoring attempt back on disk."""
        for cid in best_score:
            banked = os.path.join(best_dir, f"{cid}.wav")
            if os.path.exists(banked):
                shutil.copy2(banked, chunk_path(cid))
        shutil.rmtree(best_dir, ignore_errors=True)

    print("Starting OmniVoice inference...")
    qa_details = {}
    qa_report_path = os.path.join(args.output_dir, f"{base_name}.qa.json")
    candidate_path = os.path.join(chunk_dir, f".{base_name}.candidate.wav")
    try:
        all_ids = [entry["id"] for entry in entries]
        output_path = os.path.join(args.output_dir, f"{base_name}.wav")
        pending_ids = list(all_ids)
        direct_context_ids = set()
        attempt = 0
        if args.resume:
            missing = [
                cid for cid in all_ids
                if (
                    not os.path.exists(chunk_path(cid))
                    or previous_texts.get(cid) != entry_by_id[cid]["text"]
                )
            ]
            skipped = len(all_ids) - len(missing)
            if skipped:
                print(f"Resume: reusing {skipped} existing chunk(s).")
            stale = [
                cid for cid in missing
                if os.path.exists(chunk_path(cid))
                and previous_texts.get(cid) != entry_by_id[cid]["text"]
            ]
            if stale:
                print(
                    f"Resume: re-rendering {len(stale)} stale chunk(s) whose "
                    "saved text no longer matches."
                )
            pending_ids = missing

        while True:
            if pending_ids:
                render_dir = chunk_dir
                if args.context_preroll:
                    os.makedirs(context_dir, exist_ok=True)
                    render_dir = context_dir
                    render_entries, context_parts = build_context_render_entries(
                        all_entries, pending_ids, args,
                        direct_ids=direct_context_ids,
                    )
                    suffix = "context" if attempt == 0 else "context_retry"
                    run_list = os.path.join(chunk_dir, f"{base_name}_{suffix}.jsonl")
                    write_jsonl(render_entries, run_list)
                elif attempt == 0 and len(pending_ids) == len(entries):
                    run_list = jsonl_path
                    context_parts = {}
                else:
                    run_list = os.path.join(chunk_dir, f"{base_name}_retry.jsonl")
                    write_jsonl([entry_by_id[cid] for cid in pending_ids], run_list)
                    context_parts = {}
                pos_temp = retry_position_temperature(args.position_temperature, attempt)
                label = "render" if attempt == 0 else f"retry {attempt} (pos_temp={pos_temp:g})"
                print(f"[{label}] generating {len(pending_ids)} chunk(s)...")
                run_omnivoice(run_list, render_dir, args, run_env, position_temperature=pos_temp)

                if args.context_preroll:
                    print("Cutting context renders back to target chunks...")
                    context_failures = materialize_context_renders(
                        pending_ids, context_dir, chunk_dir, context_parts, args,
                        transcriber=asr_session,
                    )
                    if context_failures:
                        pending_ids = context_failures
                        direct_context_ids.update(context_failures)
                        if attempt >= args.max_retries:
                            for cid in context_failures:
                                qa_details[cid] = {
                                    "passed": False,
                                    "score": 0.0,
                                    "reason": "context render could not be aligned/cut",
                                }
                            raise AudioQualityError(
                                "context rendering still fails after retry limit"
                            )
                        attempt += 1
                        continue

            chunk_audio_paths = [chunk_path(entry["id"]) for entry in entries]
            missing_audio = [
                path for path in chunk_audio_paths if not os.path.exists(path)
            ]
            if missing_audio:
                print("Some chunk files are still missing after render:")
                for path in missing_audio:
                    print(f"- {path}")
                pending_ids = [
                    os.path.splitext(os.path.basename(path))[0]
                    for path in missing_audio
                ]
            else:
                file_failures = review_chunk_files(
                    all_ids, bank_ok=not (args.verify or uses_fast_verify)
                )
                if file_failures:
                    pending_ids = file_failures
                else:
                    stitch_paths = prepare_stitch_audio_files(
                        chunk_audio_paths, chunk_dir, args
                    )
                    concatenate_audio_files(
                        stitch_paths, candidate_path, chunk_dir
                    )
                    if args.verify or uses_fast_verify or args.strict_final_verify:
                        spans = chunk_audio_spans_from_paths(entries, stitch_paths)
                        print("Verifying exact post-stitch candidate audio...")
                        reviewed = review_assembled_audio(
                            candidate_path, entries, spans, args,
                            transcriber=asr_session,
                            return_details=args.strict_final_verify,
                        )
                        if args.strict_final_verify:
                            primary_results, primary_words_by_chunk = reviewed
                            print(
                                "Running strict CTC + independent ASR + "
                                "isolated-ASR final gate..."
                            )
                            asr_results, qa_details = review_strict_final_audio(
                                candidate_path, entries, spans, args,
                                primary_results, primary_words_by_chunk,
                                asr_session, strict_session,
                            )
                        else:
                            asr_results = reviewed
                            qa_details = {
                                cid: {
                                    "passed": verification_passed(
                                        score, reason, args.verify,
                                        uses_fast_verify,
                                        args.verify_threshold,
                                    ),
                                    "score": score,
                                    "reason": reason,
                                }
                                for cid, (score, reason) in asr_results.items()
                            }
                        pending_ids = review_asr_results(asr_results)
                    else:
                        pending_ids = []
                        qa_details = {
                            entry["id"]: {
                                "passed": True,
                                "score": 1.0,
                                "reason": "verification disabled",
                            }
                            for entry in entries
                        }

            if not pending_ids:
                break
            if attempt >= args.max_retries:
                print(
                    f"Error: {len(pending_ids)} chunk(s) still fail QA after "
                    f"{args.max_retries + 1} attempts. The final WAV will not "
                    "be published:"
                )
                for cid in pending_ids:
                    print(f"  - {cid} (best score {best_score.get(cid, -1):.3f})")
                write_qa_report(
                    qa_report_path, "failed", candidate_path,
                    attempt + 1, qa_details,
                    error="retry limit reached with unresolved audio defects",
                )
                restore_best_attempts()
                if os.path.exists(candidate_path):
                    os.unlink(candidate_path)
                raise AudioQualityError(
                    "strict audio QA failed; see " + qa_report_path
                )
            attempt += 1

        # The current on-disk chunks are exactly the set that passed together.
        # Restoring an earlier merely "best" take here was the old publication
        # hole: it changed the audio after verification.  Discard the bank and
        # publish the already-verified candidate byte-for-byte instead.
        shutil.rmtree(best_dir, ignore_errors=True)

        if not args.keep_context_renders:
            shutil.rmtree(context_dir, ignore_errors=True)

        if subset:
            write_qa_report(
                qa_report_path, "passed_subset", candidate_path,
                attempt + 1, qa_details,
            )
            if os.path.exists(candidate_path):
                os.unlink(candidate_path)
            print(
                f"\nSubset render passed strict QA. {len(entries)} chunk(s) "
                f"in: {chunk_dir}"
            )
            return

        publish_verified_candidate(candidate_path, output_path, qa_details)
        write_qa_report(
            qa_report_path, "passed", output_path, attempt + 1, qa_details
        )

        if not args.keep_chunks:
            shutil.rmtree(chunk_dir)

        print(f"\nSuccess! Audio saved at: {output_path}")
        print(f"Strict QA report: {qa_report_path}")
    except AudioQualityError as e:
        restore_best_attempts()
        if os.path.exists(candidate_path):
            os.unlink(candidate_path)
        write_qa_report(
            qa_report_path, "failed", None,
            attempt + 1, qa_details, error=e,
        )
        print(f"Error: {e}")
        sys.exit(2)
    except VerificationUnavailableError as e:
        restore_best_attempts()
        if os.path.exists(candidate_path):
            os.unlink(candidate_path)
        write_qa_report(
            qa_report_path, "verification_unavailable", None,
            attempt + 1, qa_details, error=e,
        )
        print(f"Error: {e}")
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        restore_best_attempts()
        if os.path.exists(candidate_path):
            os.unlink(candidate_path)
        print(f"Error occurred while running OmniVoice: {e}")
        sys.exit(1)
    finally:
        if asr_session is not None:
            asr_session.close()
        if strict_session is not None:
            strict_session.close()


if __name__ == "__main__":
    main()
