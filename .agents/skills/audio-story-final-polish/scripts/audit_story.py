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
    "hắn",
    "anh ấy",
    "cô ấy",
    "anh ta",
    "cô ta",
    "người đó",
)

META_PATTERNS = (
    re.compile(r"\btrong (?:cuốn )?(?:sách|truyện|tiểu thuyết)\b", re.IGNORECASE),
    re.compile(r"\b(?:kịch bản|cốt truyện|nhân vật gốc|bàn cờ|biến số)\b", re.IGNORECASE),
)


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

    paragraphs = [(m.start(), m.group()) for m in re.finditer(r"(?m)(?:^|\n\s*\n)([^\n].*)", text)]
    pronoun_start = re.compile(
        r"^[\s\"'“‘]*(?:nó|hắn|anh ấy|cô ấy|anh ta|cô ta|người đó)\b",
        re.IGNORECASE,
    )
    for offset, paragraph in paragraphs:
        if pronoun_start.search(paragraph):
            issues.append(
                Issue(
                    "đại-từ-đầu-đoạn",
                    line_number(text, offset),
                    "Đoạn mới mở bằng đại từ; kiểm tra xem tiền ngữ còn đủ gần và chỉ có một đối tượng phù hợp.",
                    compact(paragraph),
                )
            )


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
        count = len(words(match.group(1)))
        if count > 36:
            issues.append(
                Issue(
                    "thoại-quá-dài",
                    line_number(text, match.start()),
                    f"Lượt thoại {count} từ; kiểm tra info-dump, đổi chiến thuật và hành động chen giữa.",
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


def build_report(path: Path, text: str) -> dict[str, object]:
    issues: list[Issue] = []
    audit_long_units(text, issues)
    audit_formulae(text, issues)
    audit_pronouns(text, issues)
    audit_rhythm(text, issues)
    audit_dialogue(text, issues)
    audit_meta_language(text, issues)
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
