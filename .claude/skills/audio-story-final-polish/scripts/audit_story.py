#!/usr/bin/env python3
"""Flag surface-level stiffness in a Vietnamese story draft.

This linter is intentionally advisory. It locates passages that deserve a
human/agent read-aloud pass; it does not decide whether a literary choice is
wrong and never rewrites the source file.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from dataclasses import asdict, dataclass
from difflib import SequenceMatcher
from pathlib import Path


WORD_RE = re.compile(r"[0-9A-Za-zÀ-ỹĐđ]+(?:[-'][0-9A-Za-zÀ-ỹĐđ]+)*", re.UNICODE)
SENTENCE_RE = re.compile(r"[^.!?…\n]+(?:[.!?…]+|$)", re.UNICODE)

FORMULA_PATTERNS = {
    "không phải vì... mà vì...": re.compile(
        r"không phải vì.{0,140}?mà vì", re.IGNORECASE | re.DOTALL
    ),
    "tôi biết... nhưng tôi không biết...": re.compile(
        r"tôi biết.{0,140}?nhưng tôi không biết", re.IGNORECASE | re.DOTALL
    ),
    "điều ... không ngờ": re.compile(
        r"điều (?:mà )?(?:tôi|anh|cô|hắn|bà|ông).{0,60}?không ngờ",
        re.IGNORECASE,
    ),
    "mọi thứ chỉ mới bắt đầu": re.compile(
        r"mọi (?:chuyện|thứ).{0,30}?(?:mới|chỉ mới) bắt đầu", re.IGNORECASE
    ),
    "không ai biết/ngờ rằng": re.compile(
        r"không ai (?:biết|ngờ)(?: được)? rằng", re.IGNORECASE
    ),
    "và rồi": re.compile(r"\bvà rồi\b", re.IGNORECASE),
}

# Câu suy tưởng trừu tượng làm dáng sâu sắc (false-profundity reflection): vươn
# tới chiều sâu bằng trừu tượng, nghịch lý hoặc phủ định thay vì hình ảnh/hành
# động cụ thể. Đây là MỘT LỚP LỖI, không phải một câu; các mẫu dưới đây chỉ là
# lưới bắt vài hình dạng hay gặp, KHÔNG bao trọn cả lớp — biến thể chữ mới sẽ
# lọt, và phần khái quát thật nằm ở bài one-listen test trong SKILL.md +
# diagnosis-and-repair.md. Ca thật bị than "khó hiểu và rời rạc":
# "đó là cách duy nhất tôi biết để giữ một người đã không còn ở lại".
ABSTRACT_CLOSER_PATTERNS = {
    "cách/điều duy nhất ... để ...": re.compile(
        r"(?:cách|điều) duy nhất[^.!?…\n]{0,50}?\bđể\b", re.IGNORECASE
    ),
    "một [người/điều/thứ] ... nghịch-lý": re.compile(
        r"\bmột (?:người|điều|thứ|kẻ|khoảng)\b[^.!?…\n]{0,45}?"
        r"(?:đã không còn|chưa từng|mình chưa|không bao giờ)\b",
        re.IGNORECASE,
    ),
    "không có ... nào để ...": re.compile(
        r"không có \w+(?: \w+){0,2} nào để\b", re.IGNORECASE
    ),
    "nạn nhân của (trừu tượng)": re.compile(
        r"nạn nhân của (?:đúng|chính|mỗi|chỉ)\b", re.IGNORECASE
    ),
    "sổ/ngăn trong đầu (meta tự quy chiếu)": re.compile(
        # Chỉ bắt dạng "sổ/ngăn TINH THẦN" (trong đầu/lòng/tim, không tên), tránh
        # ghi sổ theo nghĩa đen của nhân vật làm nghề sổ sách.
        r"sổ trong (?:đầu|lòng)"
        r"|ngăn (?:không tên|trong (?:lòng|tim|đầu))"
        r"|(?:một )?(?:ngăn|ô|góc|hộc) không tên"
        r"|(?:ghi|khắc|cất) (?:nó |chuyện đó )?vào (?:lòng|tim)",
        re.IGNORECASE,
    ),
    "không tên / chưa gọi được tên": re.compile(
        r"(?:cảm giác|thứ|điều|nỗi|khoảng)\s+(?:gì đó\s+)?(?:không|chưa)\s+"
        r"(?:có\s+)?tên\b|chưa (?:bao giờ|từng) gọi (?:được )?(?:thành )?tên",
        re.IGNORECASE,
    ),
}

# Đánh giá trừu tượng / lời bình meta không nêu tiêu chí cụ thể. Khác
# ABSTRACT_CLOSER_PATTERNS, lớp này thường nằm giữa cảnh và có thể hoàn toàn
# đúng ngữ pháp, không nghịch lý, không làm dáng. Ca thật cần bắt:
# "Câu ấy đúng ngữ pháp, an toàn và không có chút đời sống nào."
# Đây chỉ là cảnh báo định vị: một cụm có thể hợp lệ nếu câu/cảnh đã nêu rõ
# mục tiêu, tiêu chí và bằng chứng.
ABSTRACT_EVALUATION_PATTERNS = {
    "an toàn nhưng không nêu khỏi điều gì": re.compile(
        r"\b(?:câu(?!\s+chuyện\b)|đoạn|lời|cách nói|câu trả lời|phần trả lời|phương án|kịch bản)"
        r"\b[^.!?…\n]{0,65}\ban toàn\b(?!\s+hơn\b)",
        re.IGNORECASE,
    ),
    "đời sống/sức sống làm tiêu chí mơ hồ": re.compile(
        r"\b(?:câu(?!\s+chuyện\b)|đoạn|lời|cách nói|câu trả lời|phần trả lời|chi tiết|cảnh|"
        r"nhân vật|mối quan hệ)\b[^.!?…\n]{0,75}\b(?:không có (?:chút )?"
        r"đời sống|có đời sống|thiếu sức sống|có sức sống)\b",
        re.IGNORECASE,
    ),
    "trọng lượng/chiều sâu/độ thật không có bằng chứng": re.compile(
        r"\b(?:câu(?!\s+chuyện\b)|đoạn|lời|cách nói|câu trả lời|cảnh|nhân vật|"
        r"mối quan hệ|khoảnh khắc)\b[^.!?…\n]{0,75}\b(?:có|thiếu|không có|"
        r"đủ)\s+(?:trọng lượng|chiều sâu|độ thật|ý nghĩa)\b",
        re.IGNORECASE,
    ),
    "thật/chân thật dùng như nhãn biên tập": re.compile(
        r"\b(?:câu(?!\s+chuyện\b)|đoạn|lời|cách nói|câu trả lời|cảnh|nhân vật|"
        r"mối quan hệ|khoảnh khắc)\b[^.!?…\n]{0,65}\b(?:đủ thật|(?:rất |quá |"
        r"đủ )?chân thật)\b",
        re.IGNORECASE,
    ),
}

EMOTION_WORDS = (
    "đau đớn",
    "tuyệt vọng",
    "sợ hãi",
    "tức giận",
    "bàng hoàng",
    "nhẹ nhõm",
    "hạnh phúc",
    "đau khổ",
    "phẫn nộ",
    "kinh hãi",
)

PRONOUNS = (
    "nó",
    "họ",
    "hắn",
    "anh ấy",
    "cô ấy",
    "anh ta",
    "cô ta",
    "người đó",
    "thứ đó",
    "cái đó",
    "việc ấy",
    "việc đó",
    "chuyện ấy",
    "chuyện đó",
    "điều ấy",
    "điều đó",
)

# Các từ nối này tiêu thụ một tiền đề đã có trong diễn ngôn. Bản audit chỉ
# định vị để đọc lại; người biên tập vẫn phải quyết định tiền đề có thật hay
# không. Ca lỗi thật cần bắt: "Chỉ là nó chưa hề hứa..." — vừa thiếu tiền ngữ
# rõ cho "nó", vừa giả định một lời hứa/khẳng định trước đó chưa từng xuất hiện.
PRESUPPOSITION_OPENINGS = {
    "chỉ là": re.compile(r"^[\s\"'“‘]*(?:chỉ là)\b", re.IGNORECASE),
    "vì vậy/do đó/bởi vậy": re.compile(
        r"^[\s\"'“‘]*(?:vì vậy|do đó|bởi vậy)\b", re.IGNORECASE
    ),
    "sau mỗi lần": re.compile(r"^[\s\"'“‘]*sau mỗi lần\b", re.IGNORECASE),
}

META_PATTERNS = (
    re.compile(r"\btrong (?:cuốn )?(?:sách|truyện|tiểu thuyết)\b", re.IGNORECASE),
    re.compile(r"\b(?:kịch bản|cốt truyện|nhân vật gốc|bàn cờ|biến số)\b", re.IGNORECASE),
)

# Hiệu chỉnh trên bản render 80 chunk của `anh-ky-don-ly-hon`: 3 từ / 2 câu
# báo đúng đoạn có vấn đề và không báo nhầm chỗ nào khác trong cả truyện.
REPEATED_OPENING_WORDS = 3
REPEATED_OPENING_RUN = 2
# So khớp mờ: cùng từ mở câu và trùng >= 3 trong 4 từ đầu (theo thứ tự) thì
# vẫn tính là mở đầu lặp. Ca thật: "Tôi muốn nói / Tôi rất muốn nói / Tôi còn
# muốn nói" — từ chêm ("rất", "còn") ngắn, không trọng âm, bị tai người nuốt
# mất, người nghe vẫn báo là máy lắp dù audio đo lại hoàn toàn đúng chữ.
REPEATED_OPENING_FUZZY_WINDOW = 4
REPEATED_OPENING_FUZZY_MATCH = 3

TTS_TOKEN_PATTERNS = {
    "giờ-số": re.compile(r"\b\d{1,2}\s*(?:[hH:])\s*\d{0,2}\b"),
    "ngày-tháng-số": re.compile(r"\b\d{1,2}/\d{1,2}(?:/\d{2,4})?\b"),
    "phần-trăm-ký-hiệu": re.compile(r"\b\d+(?:[.,]\d+)?\s*%"),
    "ký-hiệu-thô": re.compile(r"[@#&=+]"),
    "viết-tắt-in-hoa": re.compile(r"\b[A-ZĐ]{2,}(?:[-/][A-ZĐ0-9]{2,})?\b"),
}

# This is an advisory semantic-domain locator, not a ban on individual words.
# It catches human/relationship targets placed close to repair/object/system
# vocabulary so the editor can run the semantic-fit gate. Some deliberate
# metaphors will be valid and should be kept after review.
HUMAN_RELATIONSHIP_RE = re.compile(
    r"\b(?:(?:cuộc\s+)?hôn nhân|mối quan hệ|tình cảm|tình yêu|vợ chồng|gia đình)\b",
    re.IGNORECASE,
)
OBJECT_SYSTEM_RE = re.compile(
    r"\b(?:hỏng|sửa(?:\s+chữa|\s+cho\s+đúng)?|đồ vật|linh kiện|lắp ráp|"
    r"vận hành(?:\s+sai)?|lỗi hệ thống|gỡ lỗi|quy trình)\b",
    re.IGNORECASE,
)

# A narrow locator for epistemic overreach: a very short acquaintance is
# followed by certainty about a hidden, repeated, or lifelong inner pattern.
# It intentionally requires both sides; isolated "mới quen" or "nhận ra" is
# not enough. Editorial judgment still decides whether unusual evidence earns
# the claim or retrospective narration changes the knowledge level.
INSTANT_INSIGHT_PATTERNS = {
    "mới quen/gặp đã chẩn đoán điều giấu kín": re.compile(
        r"(?:mới|vừa)\s+(?:gặp|quen|biết)(?:\s+nhau)?"
        r"[^.!?…\n]{0,180}?\b(?:đã|liền)\b"
        r"[^.!?…\n]{0,80}?\b(?:chỉ đúng|nhìn thấu|hiểu rõ|biết rõ|nhận ra)\b"
        r"[^.!?…\n]{0,100}?\b(?:thói quen|bản chất|vết thương|nỗi sợ|"
        r"điều[^.!?…\n]{0,30}?(?:giấu|che)|cố giấu)\b",
        re.IGNORECASE,
    ),
    "chưa đầy thời gian ngắn đã hiểu điều sâu kín": re.compile(
        r"(?:chưa đầy|chỉ sau)\s+(?:\w+\s+){0,3}?(?:phút|giờ|ngày|buổi)"
        r"[^.!?…\n]{0,180}?\b(?:đã|liền)\b"
        r"[^.!?…\n]{0,80}?\b(?:chỉ đúng|nhìn thấu|hiểu rõ|biết rõ|nhận ra)\b"
        r"[^.!?…\n]{0,100}?\b(?:thói quen|bản chất|vết thương|nỗi sợ|"
        r"điều[^.!?…\n]{0,30}?(?:giấu|che)|cố giấu)\b",
        re.IGNORECASE,
    ),
}

# These are not banned objects. The patterns target ready-made choreography,
# not mere presence, and ask the editor to run object-presence + scene-origin
# tests. A single legitimate occurrence may be kept.
STOCK_CHOREOGRAPHY_PATTERNS = {
    "chỉnh đồ ăn/uống cho ngay ngắn": re.compile(
        r"\b(?:xoay|chỉnh|xếp|đặt)\b[^.!?…\n]{0,35}?"
        r"\b(?:đũa|bát|chén|cốc|ly|đĩa)\b[^.!?…\n]{0,30}?"
        r"\b(?:thẳng|ngay ngắn|đúng chỗ|thẳng hàng)\b",
        re.IGNORECASE,
    ),
    "đạo cụ cầm tay làm nhịp cảm xúc": re.compile(
        r"\b(?:úp|siết|nắm chặt|đặt mạnh|miết|gấp)\b[^.!?…\n]{0,22}?"
        r"\b(?:điện thoại|tờ giấy|chìa khóa|mép giấy|tay áo|vạt áo)\b"
        r"|\b(?:điện thoại|tờ giấy|chìa khóa)\b[^.!?…\n]{0,18}?"
        r"\b(?:úp xuống|bị siết|được đặt mạnh|được gấp)\b",
        re.IGNORECASE,
    ),
    "đọc lặp để biểu diễn choáng": re.compile(
        r"\bđọc\b[^.!?…\n]{0,40}?\b(?:hai|ba|2|3)\s+lần\b"
        r"|\blần thứ\s+(?:hai|ba)\b[^.!?…\n]{0,35}?\b(?:đọc|chữ|dòng|giấy|màn hình)\b",
        re.IGNORECASE,
    ),
    "lau chỗ đã sạch": re.compile(
        r"\blau\b[^.!?…\n]{0,45}?\b(?:đã sạch|không có bụi|sạch rồi)\b",
        re.IGNORECASE,
    ),
    "chỉnh trang phục thay cảm xúc": re.compile(
        r"\b(?:kéo|vuốt|chỉnh|miết)\b[^.!?…\n]{0,25}?"
        r"\b(?:tay áo|cổ áo|vạt áo|gấu áo)\b",
        re.IGNORECASE,
    ),
}

CADENCE_RESIDUE_PATTERNS = {
    "không trả lời ngay": (re.compile(r"\bkhông trả lời ngay\b", re.IGNORECASE), 2),
    "lần đầu tiên": (re.compile(r"\blần đầu tiên\b", re.IGNORECASE), 3),
    "tôi nhận ra": (re.compile(r"\btôi nhận ra\b", re.IGNORECASE), 4),
    "chỉ khác là": (re.compile(r"\bchỉ khác là\b", re.IGNORECASE), 2),
    "thêm một giây": (re.compile(r"\b(?:lâu|nhìn|dừng)[^.!?…\n]{0,30}?thêm một giây\b", re.IGNORECASE), 2),
}

GUARDRAIL_LEAK_PATTERNS = {
    "nghề nghiệp không cho phép hiểu mọi thứ": re.compile(
        r"\b(?:nghề nghiệp|công việc|làm nghề[^.!?…\n]{0,35}?)\b"
        r"[^.!?…\n]{0,55}?\b(?:không khiến|không có nghĩa)\b"
        r"[^.!?…\n]{0,45}?\b(?:biết mọi thứ|hiểu mọi người|đọc vị|nhìn thấu)\b",
        re.IGNORECASE,
    ),
    "tự giải thích đây chỉ là suy đoán viết văn": re.compile(
        r"\b(?:đây|điều đó|nhận định ấy)\b[^.!?…\n]{0,35}?"
        r"\b(?:chỉ là|mới là)\s+(?:một\s+)?(?:suy đoán|phỏng đoán|diễn giải)\b",
        re.IGNORECASE,
    ),
}


@dataclass
class Issue:
    category: str
    line: int
    message: str
    excerpt: str


def words(text: str) -> list[str]:
    return WORD_RE.findall(text)


def line_number(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def compact(text: str, limit: int = 150) -> str:
    value = re.sub(r"\s+", " ", text).strip()
    return value if len(value) <= limit else value[: limit - 1].rstrip() + "…"


def sentence_records(text: str) -> list[tuple[int, str, int]]:
    records = []
    for match in SENTENCE_RE.finditer(text):
        sentence = match.group().strip()
        if sentence:
            records.append((line_number(text, match.start()), sentence, len(words(sentence))))
    return records


def audit_long_units(text: str, issues: list[Issue]) -> None:
    for line, sentence, count in sentence_records(text):
        if count > 42:
            issues.append(
                Issue(
                    "câu-quá-dài",
                    line,
                    f"{count} từ; thử tách hiện tại, nguyên nhân và hệ quả thành các nhịp riêng.",
                    compact(sentence),
                )
            )

    offset = 0
    for paragraph in re.split(r"\n\s*\n", text):
        if not paragraph.strip():
            offset += len(paragraph)
            continue
        count = len(words(paragraph))
        if count > 140:
            issues.append(
                Issue(
                    "đoạn-quá-dày",
                    line_number(text, offset),
                    f"{count} từ; kiểm tra xem đoạn đang trộn nhiều thời điểm hoặc chức năng.",
                    compact(paragraph),
                )
            )
        found = text.find(paragraph, offset)
        offset = (found if found >= 0 else offset) + len(paragraph)


def audit_formulae(text: str, issues: list[Issue]) -> None:
    for label, pattern in FORMULA_PATTERNS.items():
        matches = list(pattern.finditer(text))
        threshold = 2 if label in {"và rồi", "không ai biết/ngờ rằng"} else 1
        if len(matches) <= threshold:
            continue
        for match in matches[:8]:
            issues.append(
                Issue(
                    "khuôn-lặp",
                    line_number(text, match.start()),
                    f"Khuôn “{label}” xuất hiện {len(matches)} lần; chỉ giữ khi mỗi lần có chức năng riêng.",
                    compact(match.group()),
                )
            )

    for term in EMOTION_WORDS:
        matches = list(re.finditer(rf"\b{re.escape(term)}\b", text, re.IGNORECASE))
        if len(matches) >= 3:
            first = matches[0]
            issues.append(
                Issue(
                    "nhãn-cảm-xúc-lặp",
                    line_number(text, first.start()),
                    f"“{term}” xuất hiện {len(matches)} lần; rà xem có thể thay một số lần bằng phản ứng/hệ quả riêng không.",
                    compact(text[first.start() : first.start() + 150]),
                )
            )


def audit_abstract_closers(text: str, issues: list[Issue]) -> None:
    """Bắt câu suy tưởng trừu tượng/nghịch lý làm dáng sâu sắc.

    Đây là lưới bắt vài hình dạng hay gặp của MỘT LỚP LỖI, không phải toàn bộ
    lớp: biến thể chữ mới sẽ lọt, nên còn phải chạy one-listen test trong
    SKILL.md cho mọi câu suy tưởng. Khác các khuôn lặp, chỉ một câu như vậy cũng
    đáng đọc lại nên không cần ngưỡng lặp. Cảnh báo định vị: gọi tên đối tượng cụ
    thể, giữ hình ảnh/hành động, bỏ câu diễn giải; đừng thay một trừu tượng bằng
    trừu tượng mượt hơn.
    """
    flagged = 0
    for label, pattern in ABSTRACT_CLOSER_PATTERNS.items():
        for match in pattern.finditer(text):
            if flagged >= 12:
                return
            issues.append(
                Issue(
                    "chốt-trừu-tượng",
                    line_number(text, match.start()),
                    f"Mẫu “{label}” dễ thành câu suy tưởng trừu tượng/nghịch lý làm "
                    "dáng sâu sắc, nghe một lần thấy rời rạc; gọi tên đối tượng cụ "
                    "thể, giữ hình ảnh/hành động, bỏ câu diễn giải. Đây chỉ là một "
                    "hình dạng của cả lớp lỗi — chạy thêm one-listen test cho mọi "
                    "câu suy tưởng. Xem references/diagnosis-and-repair.md, mục "
                    "“False-Profundity Abstract Closer”.",
                    compact(text[max(0, match.start() - 30) : match.end() + 60]),
                )
            )
            flagged += 1


def audit_abstract_evaluations(text: str, issues: list[Issue]) -> None:
    """Định vị lời bình đánh giá nhưng có thể đang giấu tiêu chí của tác giả.

    Không cấm từ trừu tượng. Cảnh báo yêu cầu người biên tập trả lời đủ ba câu:
    đang đánh giá cái gì, nhãn đó nghĩa là gì trong cảnh này, và chi tiết/hệ
    quả nào chứng minh. Thiếu hai câu trả lời thì phải unpack hoặc cắt.
    """
    flagged_spans: set[tuple[int, int]] = set()
    for label, pattern in ABSTRACT_EVALUATION_PATTERNS.items():
        for match in pattern.finditer(text):
            span = (match.start(), match.end())
            if any(start <= match.start() < end for start, end in flagged_spans):
                continue
            flagged_spans.add(span)
            issues.append(
                Issue(
                    "đánh-giá-trừu-tượng",
                    line_number(text, match.start()),
                    f"Mẫu “{label}” có thể đúng ngữ pháp nhưng giấu tiêu chí. "
                    "Nói rõ: (1) đối tượng nào đang bị đánh giá, (2) nhãn đó "
                    "nghĩa là gì trong cảnh này, (3) chi tiết hoặc hệ quả nào "
                    "chứng minh. Thiếu hai ý thì unpack thành lỗi/hành vi/hệ quả "
                    "cụ thể hoặc cắt. Xem references/diagnosis-and-repair.md, "
                    "mục “Abstract Evaluation Without Concrete Meaning”.",
                    compact(text[max(0, match.start() - 35) : match.end() + 70]),
                )
            )
            if len(flagged_spans) >= 12:
                return


def audit_pronouns(text: str, issues: list[Issue]) -> None:
    flagged_sentences: set[tuple[int, int]] = set()
    for term in PRONOUNS:
        matches = list(re.finditer(rf"\b{re.escape(term)}\b", text, re.IGNORECASE))
        if term == "nó" and matches:
            for match in matches[:12]:
                stops_before = [text.rfind(mark, 0, match.start()) for mark in ".!?…\n"]
                start = max(stops_before) + 1
                stops_after = [text.find(mark, match.end()) for mark in ".!?…\n"]
                valid_stops = [position for position in stops_after if position >= 0]
                end = min(valid_stops) + 1 if valid_stops else len(text)
                sentence = text[start:end].strip()
                is_risky = (
                    len(words(sentence)) >= 30
                    or sentence.count(",") >= 2
                    or bool(re.search(r"\b(?:chính|vì|tin) nó\b", sentence, re.IGNORECASE))
                )
                if not is_risky or (start, end) in flagged_sentences:
                    continue
                flagged_sentences.add((start, end))
                issues.append(
                    Issue(
                        "đại-từ-cần-nghe-lại",
                        line_number(text, match.start()),
                        "Kiểm tra tiền ngữ và sắc thái của “nó”; thay bằng quan hệ/tên nếu tai có thể hiểu nhầm hoặc sắc thái quá lạnh.",
                        compact(sentence),
                    )
                )

    paragraphs = [
        (m.start(1), m.group(1))
        for m in re.finditer(r"(?m)(?:^|\n\s*\n)([^\n].*)", text)
    ]
    pronoun_start = re.compile(
        r"^[\s\"'“‘]*(?:(?:chỉ là|nhưng|thế nhưng|tuy vậy|dù vậy|vì vậy|do đó|bởi vậy)\s+)?"
        r"(?:nó|họ|hắn|anh ấy|cô ấy|anh ta|cô ta|người đó|thứ đó|cái đó|việc ấy|việc đó|chuyện ấy|chuyện đó|điều ấy|điều đó)\b",
        re.IGNORECASE,
    )
    for offset, paragraph in paragraphs:
        if pronoun_start.search(paragraph):
            issues.append(
                Issue(
                    "đại-từ-đầu-đoạn",
                    line_number(text, offset),
                    "Đoạn mới mở bằng đại từ/từ trỏ, có thể đứng sau một từ nối; nói thành tiếng danh từ mà nó thay thế. Nếu không có đúng một tiền ngữ đã được định danh và đúng vai trò, phải gọi tên đối tượng.",
                    compact(paragraph),
                )
            )


def audit_presupposition_openings(text: str, issues: list[Issue]) -> None:
    """Định vị từ nối mở câu cần một tiền đề đã được nói rõ.

    Không kết luận tự động rằng từ nối sai. Cảnh báo buộc lượt đọc lạnh phải
    phát biểu được tiền đề; nếu chỉ tác giả biết nó trong dàn ý thì văn bản vẫn
    thiếu thông tin.
    """
    flagged = 0
    for line, sentence, _ in sentence_records(text):
        for label, pattern in PRESUPPOSITION_OPENINGS.items():
            if not pattern.search(sentence):
                continue
            issues.append(
                Issue(
                    "tiền-đề-cần-nghe-lại",
                    line,
                    f"Câu mở bằng “{label}”; nói rõ mệnh đề/nguyên nhân/lần xảy ra trước mà từ nối này dựa vào. Nếu không thể chỉ ra từ văn bản, thêm setup tối thiểu hoặc bỏ từ nối.",
                    compact(sentence),
                )
            )
            flagged += 1
            if flagged >= 12:
                return
            break


def audit_rhythm(text: str, issues: list[Issue]) -> None:
    records = sentence_records(text)
    first_words = []
    for line, sentence, _ in records:
        tokens = [token.lower() for token in words(sentence)]
        first_words.append((line, tokens[0] if tokens else "", sentence))

    run_start = 0
    for index in range(1, len(first_words) + 1):
        same = index < len(first_words) and first_words[index][1] == first_words[run_start][1]
        if same:
            continue
        run_len = index - run_start
        word = first_words[run_start][1] if run_start < len(first_words) else ""
        if run_len >= 4 and word:
            line, _, sentence = first_words[run_start]
            issues.append(
                Issue(
                    "mở-câu-lặp",
                    line,
                    f"{run_len} câu liên tiếp mở bằng “{word}”; rà nhịp và điểm nhìn, không đảo câu máy móc.",
                    compact(sentence),
                )
            )
        run_start = index

    for index in range(0, max(0, len(records) - 5)):
        window = records[index : index + 6]
        lengths = [item[2] for item in window]
        if min(lengths) >= 4 and max(lengths) - min(lengths) <= 3:
            issues.append(
                Issue(
                    "nhịp-đều",
                    window[0][0],
                    f"6 câu có độ dài gần như nhau ({min(lengths)}-{max(lengths)} từ); nghe lại để tránh nhịp máy.",
                    compact(" ".join(item[1] for item in window[:2])),
                )
            )
            break


def audit_dialogue(text: str, issues: list[Issue]) -> None:
    quote_re = re.compile(r"[“\"]([^”\"\n]+)[”\"]")
    for match in quote_re.finditer(text):
        inner = match.group(1).strip()
        count = len(words(inner))
        if inner and inner[-1] not in ".!?…," and count >= 4:
            issues.append(
                Issue(
                    "thoại-thiếu-dấu-kết",
                    line_number(text, match.start()),
                    "Lượt thoại không kết bằng . ? ! hoặc …; TTS có thể nối nhịp sang phần sau.",
                    compact(match.group()),
                )
            )
        if count > 36:
            issues.append(
                Issue(
                    "thoại-quá-dài",
                    line_number(text, match.start()),
                    f"Lượt thoại {count} từ; kiểm tra info-dump, đổi chiến thuật và hành động chen giữa.",
                    compact(match.group()),
                )
            )

    for match in re.finditer(r"(?m)^[ \t]*[-–—][ \t]*\S.*", text):
        issues.append(
            Issue(
                "thoại-gạch-đầu-dòng",
                line_number(text, match.start()),
                "Dòng mở bằng gạch ngang; với VoxCPM-bound story, kiểm tra có nên đổi sang ngoặc kép và tách lượt thoại rõ hơn.",
                compact(match.group()),
            )
        )

    offset = 0
    for paragraph in re.split(r"\n\s*\n", text):
        if not paragraph.strip():
            offset += len(paragraph)
            continue
        quote_count = len(re.findall(r"[“\"][^”\"\n]+[”\"]", paragraph))
        if quote_count >= 2:
            found = text.find(paragraph, offset)
            issues.append(
                Issue(
                    "nhiều-thoại-cùng-đoạn",
                    line_number(text, found if found >= 0 else offset),
                    f"{quote_count} cụm thoại trong một đoạn; nếu là nhiều người nói, tách mỗi lượt sang đoạn riêng để TTS reset.",
                    compact(paragraph),
                )
            )
            offset = (found if found >= 0 else offset) + len(paragraph)
        else:
            found = text.find(paragraph, offset)
            offset = (found if found >= 0 else offset) + len(paragraph)


def audit_human_semantic_fit(text: str, issues: list[Issue]) -> None:
    for line, sentence, _ in sentence_records(text):
        if HUMAN_RELATIONSHIP_RE.search(sentence) and OBJECT_SYSTEM_RE.search(sentence):
            issues.append(
                Issue(
                    "cơ-khí-hóa-quan-hệ",
                    line,
                    "Danh từ chỉ quan hệ đứng cùng từ vựng đồ vật/sửa chữa/hệ thống; "
                    "đây chỉ là cảnh báo để chạy kiểm tra category fit, collocation và "
                    "quyền sở hữu ẩn dụ, không phải lệnh cấm từ.",
                    compact(sentence),
                )
            )

    dialogue_matches = list(re.finditer(r"[“\"]([^”\"\n]+)[”\"]", text))
    for previous, current in zip(dialogue_matches, dialogue_matches[1:]):
        if current.start() - previous.end() > 320:
            continue
        previous_line = previous.group(1)
        current_line = current.group(1)
        if not (
            OBJECT_SYSTEM_RE.search(previous_line)
            and OBJECT_SYSTEM_RE.search(current_line)
            and (
                HUMAN_RELATIONSHIP_RE.search(previous_line)
                or HUMAN_RELATIONSHIP_RE.search(current_line)
            )
        ):
            continue
        issues.append(
            Issue(
                "thoại-chung-trường-ẩn-dụ",
                line_number(text, previous.start()),
                "Hai lượt thoại gần nhau cùng dùng trường đồ vật/sửa chữa cho quan hệ; "
                "kiểm tra aphorism tennis, metaphor contagion và xem mỗi người có đang "
                "nói bằng mục đích/ngôn ngữ riêng hay không.",
                compact(f"{previous.group()} {current.group()}"),
            )
        )


def audit_earned_insight(text: str, issues: list[Issue]) -> None:
    flagged_spans: list[tuple[int, int]] = []
    for label, pattern in INSTANT_INSIGHT_PATTERNS.items():
        for match in list(pattern.finditer(text))[:8]:
            if any(match.start() < end and start < match.end() for start, end in flagged_spans):
                continue
            flagged_spans.append((match.start(), match.end()))
            issues.append(
                Issue(
                    "thấu-hiểu-chưa-được-kiếm",
                    line_number(text, match.start()),
                    f"Mẫu “{label}” có thể biến một quan sát ngắn thành sự thật tâm lý sâu. "
                    "Tách rõ điều đã thấy, suy đoán hiện tại, khuôn mẫu cần thời gian, và sự thật cần bằng chứng/lời thú nhận; hạ độ chắc hoặc dời kết luận nếu chưa đủ.",
                    compact(match.group()),
                )
            )


def audit_stock_choreography(text: str, issues: list[Issue]) -> None:
    for label, pattern in STOCK_CHOREOGRAPHY_PATTERNS.items():
        for match in list(pattern.finditer(text))[:8]:
            issues.append(
                Issue(
                    "đạo-cụ-cảm-xúc-mẫu",
                    line_number(text, match.start()),
                    f"Mẫu “{label}” thường là biên đạo cảm xúc có sẵn. Chạy object-presence và scene-origin test; chỉ giữ nếu vật/động tác bắt buộc bởi địa điểm, công việc, lịch sử hoặc hệ quả của chính cảnh.",
                    compact(match.group()),
                )
            )

    for label, (pattern, threshold) in CADENCE_RESIDUE_PATTERNS.items():
        matches = list(pattern.finditer(text))
        if len(matches) < threshold:
            continue
        first = matches[0]
        issues.append(
            Issue(
                "nhịp-văn-mẫu-lặp",
                line_number(text, first.start()),
                f"Cụm/nhịp “{label}” xuất hiện {len(matches)} lần; rà xem đây là giọng riêng có chủ ý hay tàn dư khuôn kết luận/phản ứng lặp.",
                compact(text[first.start() : first.start() + 150]),
            )
        )

    final_zone = int(len(text) * 0.70)
    for match in re.finditer(r"\b(?:lần đầu tiên|lần này|chỉ khác là)\b", text, re.IGNORECASE):
        if match.start() < final_zone:
            continue
        sentence_start = max(text.rfind(mark, 0, match.start()) for mark in ".!?…\n") + 1
        following = [text.find(mark, match.end()) for mark in ".!?…\n"]
        following = [position for position in following if position >= 0]
        sentence_end = min(following) + 1 if following else len(text)
        issues.append(
            Issue(
                "chốt-cung-bậc-mẫu",
                line_number(text, match.start()),
                "Cụm đánh dấu thay đổi xuất hiện gần cuối truyện/cảnh; xóa nhãn và kiểm tra xem hành vi/hệ quả tự nó đã cho thấy cung bậc chưa. Chỉ giữ khi tính 'lần đầu/lần này' là dữ kiện thời gian thật sự cần.",
                compact(text[sentence_start:sentence_end]),
            )
        )


def audit_guardrail_leakage(text: str, issues: list[Issue]) -> None:
    for label, pattern in GUARDRAIL_LEAK_PATTERNS.items():
        for match in list(pattern.finditer(text))[:8]:
            issues.append(
                Issue(
                    "lộ-lời-skill",
                    line_number(text, match.start()),
                    f"Mẫu “{label}” có thể đang kể lại luật viết thay vì sống trong cảnh. Enforce giới hạn bằng mức thông tin thực sự được kể; cắt lời tự biện hộ nếu nhân vật không có lý do nội truyện để nghĩ như vậy.",
                    compact(match.group()),
                )
            )


def audit_meta_language(text: str, issues: list[Issue]) -> None:
    matches = [match for pattern in META_PATTERNS for match in pattern.finditer(text)]
    if len(matches) > 4:
        matches.sort(key=lambda item: item.start())
        first = matches[0]
        issues.append(
            Issue(
                "meta-dày",
                line_number(text, first.start()),
                f"Có {len(matches)} lần nhắc sách/truyện/kịch bản/biến số; với tiền đề biết trước, cân nhắc chứng minh bằng lựa chọn thay vì nhắc cơ chế.",
                compact(text[first.start() : first.start() + 170]),
            )
        )


def audit_tts_readiness(text: str, issues: list[Issue]) -> None:
    for match in re.finditer(r"(?<=[.,!?;:])(?=[^\s\d.,!?;:\"'”’)\]])", text):
        start = max(0, match.start() - 80)
        end = min(len(text), match.start() + 80)
        issues.append(
            Issue(
                "dấu-câu-dính-chữ",
                line_number(text, match.start()),
                "Dấu câu không có khoảng trắng sau nó; TTS có thể đọc thành một token liền.",
                compact(text[start:end]),
            )
        )

    for match in re.finditer(r"\.{4,}|…{2,}", text):
        issues.append(
            Issue(
                "dấu-lửng-lặp",
                line_number(text, match.start()),
                "Dấu lửng lặp quá mức; dùng ba chấm hoặc một dấu … khi thật sự cần nhịp ngập ngừng.",
                compact(text[max(0, match.start() - 70) : match.end() + 70]),
            )
        )

    for label, pattern in TTS_TOKEN_PATTERNS.items():
        matches = list(pattern.finditer(text))
        for match in matches[:12]:
            issues.append(
                Issue(
                    "tts-token-cần-nghe-lại",
                    line_number(text, match.start()),
                    f"Mẫu “{label}” có thể cần viết theo dạng đọc hoặc kiểm thử VoxCPM.",
                    compact(text[max(0, match.start() - 70) : match.end() + 70]),
                )
            )

    for line, sentence, count in sentence_records(text):
        comma_count = sentence.count(",")
        if count >= 28 and comma_count >= 4:
            issues.append(
                Issue(
                    "câu-nhiều-nhịp-phẩy",
                    line,
                    f"{count} từ với {comma_count} dấu phẩy; nghe lại xem nên tách thành các nhịp câu/đoạn rõ hơn.",
                    compact(sentence),
                )
            )


def openings_sound_alike(first: str, second: str) -> bool:
    """Hai câu liền nhau có mở đầu 'nghe như một' hay không.

    Trùng hệt REPEATED_OPENING_WORDS từ đầu thì chắc chắn có. Ngoài ra còn
    tính cả trường hợp cùng từ mở câu và trùng >= REPEATED_OPENING_FUZZY_MATCH
    trong REPEATED_OPENING_FUZZY_WINDOW từ đầu theo thứ tự: từ chêm ngắn không
    trọng âm ("rất", "còn", "cũng"...) không đủ cứu đôi tai đã bị câu trước mồi
    sẵn. Dạng danh sách có nhãn ("Ngày thứ nhất: ...") được miễn — nhãn mang
    trọng âm và dấu hai chấm mang nhịp ngắt, tai người theo được.
    """
    tokens_first = [token.lower() for token in words(first)[:REPEATED_OPENING_FUZZY_WINDOW]]
    tokens_second = [token.lower() for token in words(second)[:REPEATED_OPENING_FUZZY_WINDOW]]
    if (
        len(tokens_first) < REPEATED_OPENING_WORDS
        or len(tokens_second) < REPEATED_OPENING_WORDS
    ):
        return False
    if ":" in first[:40] and ":" in second[:40]:
        return False
    if tokens_first[:REPEATED_OPENING_WORDS] == tokens_second[:REPEATED_OPENING_WORDS]:
        return True
    if tokens_first[0] != tokens_second[0]:
        return False
    matcher = SequenceMatcher(a=tokens_first, b=tokens_second, autojunk=False)
    matched = sum(block.size for block in matcher.get_matching_blocks())
    return matched >= REPEATED_OPENING_FUZZY_MATCH


def audit_repeated_openings(text: str, issues: list[Issue]) -> None:
    """Bắt các câu liên tiếp mở đầu giống hệt nhau.

    Trên trang giấy đây là điệp ngữ có chủ ý. Nghe liên tiếp bằng giọng đọc thì
    người nghe lại tưởng máy bị lắp. Đã xảy ra thật: ba câu liên tiếp mở đầu
    bằng “Tôi muốn nói,” bị báo là lỗi render, trong khi đo lại cho thấy audio
    hoàn toàn đúng. Không tầng QC âm thanh nào bắt được, và render lại cũng
    không sửa được — chỉ sửa được ở văn bản.
    """
    records = sentence_records(text)
    index = 0
    while index < len(records):
        opening = " ".join(words(records[index][1])[:REPEATED_OPENING_WORDS]).lower()
        if len(opening.split()) < REPEATED_OPENING_WORDS:
            index += 1
            continue
        end = index
        while end + 1 < len(records) and openings_sound_alike(
            records[end][1], records[end + 1][1]
        ):
            end += 1
        run = end - index + 1
        if run >= REPEATED_OPENING_RUN:
            issues.append(
                Issue(
                    "mở-đầu-lặp-liên-tiếp",
                    records[index][0],
                    f"{run} câu liên tiếp mở đầu bằng “{opening}”; đọc thành tiếng "
                    "sẽ nghe như giọng đọc bị lắp. Nếu điệp ngữ có chủ ý thì giữ "
                    "cụm neo và đổi cách dẫn vào nó ở mỗi câu; nếu lặp do vô "
                    "tình thì viết lại hẳn phần mở đầu. Xem "
                    "references/diagnosis-and-repair.md, mục “Consecutive "
                    "Sentences Open With The Same Words”.",
                    compact(records[index][1]),
                )
            )
        index = end + 1


def build_report(path: Path, text: str) -> dict[str, object]:
    issues: list[Issue] = []
    audit_long_units(text, issues)
    audit_formulae(text, issues)
    audit_abstract_closers(text, issues)
    audit_abstract_evaluations(text, issues)
    audit_pronouns(text, issues)
    audit_presupposition_openings(text, issues)
    audit_rhythm(text, issues)
    audit_dialogue(text, issues)
    audit_human_semantic_fit(text, issues)
    audit_earned_insight(text, issues)
    audit_stock_choreography(text, issues)
    audit_guardrail_leakage(text, issues)
    audit_meta_language(text, issues)
    audit_tts_readiness(text, issues)
    audit_repeated_openings(text, issues)
    issues.sort(key=lambda issue: (issue.line, issue.category))

    counts = Counter(issue.category for issue in issues)
    return {
        "file": str(path),
        "words": len(words(text)),
        "sentences": len(sentence_records(text)),
        "issue_counts": dict(sorted(counts.items())),
        "issues": [asdict(issue) for issue in issues],
    }


def print_text_report(report: dict[str, object]) -> None:
    print(f"Tệp: {report['file']}")
    print(f"Quy mô: {report['words']} từ, {report['sentences']} câu")
    issue_counts = report["issue_counts"]
    if not issue_counts:
        print("Không phát hiện tín hiệu bề mặt đáng chú ý.")
        print("Vẫn phải chạy các lượt nhân quả, động cơ, cảm xúc và xưng hô trong SKILL.md.")
        return

    print("\nTổng hợp tín hiệu:")
    for category, count in issue_counts.items():
        print(f"- {category}: {count}")

    print("\nVị trí cần nghe lại:")
    for item in report["issues"]:
        print(f"- dòng {item['line']} [{item['category']}]: {item['message']}")
        print(f"  {item['excerpt']}")

    print("\nLưu ý: đây là cảnh báo định vị, không phải kết luận văn học hay lệnh thay tự động.")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Dò các tín hiệu bề mặt khiến truyện tiếng Việt dễ đơ hoặc khó nghe."
    )
    parser.add_argument("story", type=Path, help="Tệp truyện UTF-8 (.md hoặc .txt).")
    parser.add_argument("--json", action="store_true", help="Xuất báo cáo JSON.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        text = args.story.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        print(f"Không đọc được {args.story}: {exc}", file=sys.stderr)
        return 2

    report = build_report(args.story, text)
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print_text_report(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
