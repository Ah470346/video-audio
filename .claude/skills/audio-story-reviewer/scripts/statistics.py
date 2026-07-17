#!/usr/bin/env python3
"""Surface statistics for a Vietnamese audio-story manuscript.

This script is advisory. It highlights passages that may deserve a listening
pass; it does not determine whether a literary choice is wrong.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path


WORD_RE = re.compile(r"[0-9A-Za-zÀ-ỹĐđ]+(?:[-'][0-9A-Za-zÀ-ỹĐđ]+)*", re.UNICODE)
SENTENCE_RE = re.compile(r"[^.!?…\n]+(?:[.!?…]+|$)", re.UNICODE)
DIALOGUE_RE = re.compile(r'["“][^"”]{2,}["”]|^\s*[-–]\s+\S+', re.MULTILINE)
SYMBOL_RE = re.compile(r"(?:https?://|www\.|[@#&%]|[A-Z]{2,}\b|\d+/\d+/\d+|\d+[.,]?\d*\s?(?:%|kg|km|cm|m2|m3|USD|VND))")

FORMULA_PATTERNS = {
    "khong-phai-vi-ma-vi": re.compile(r"không phải vì.{0,160}?mà vì", re.I | re.S),
    "toi-biet-nhung": re.compile(r"tôi biết.{0,160}?nhưng tôi không biết", re.I | re.S),
    "dieu-khong-ngo": re.compile(
        r"điều (?:mà )?(?:tôi|anh|cô|hắn|bà|ông|nó).{0,80}?không ngờ",
        re.I,
    ),
    "moi-chuyen-moi-bat-dau": re.compile(
        r"mọi (?:chuyện|thứ).{0,40}?(?:mới|chỉ mới) bắt đầu",
        re.I,
    ),
    "khong-ai-biet-rang": re.compile(r"không ai (?:biết|ngờ)(?: được)? rằng", re.I),
}

PRONOUNS = (
    "nó",
    "hắn",
    "anh ấy",
    "cô ấy",
    "anh ta",
    "cô ta",
    "người đó",
)


@dataclass
class Flag:
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
    records: list[tuple[int, str, int]] = []
    for match in SENTENCE_RE.finditer(text):
        sentence = match.group().strip()
        if sentence:
            records.append((line_number(text, match.start()), sentence, len(words(sentence))))
    return records


def repeated_sentence_openings(sentences: list[tuple[int, str, int]], limit: int = 7) -> list[Flag]:
    starts: list[tuple[str, int, str]] = []
    for line, sentence, _ in sentences:
        tokens = [token.lower() for token in words(sentence)[:3]]
        if tokens:
            starts.append((" ".join(tokens), line, sentence))
    counts = Counter(start for start, _, _ in starts)
    flags: list[Flag] = []
    for start, count in counts.most_common():
        if count >= limit:
            first = next((line, sentence) for s, line, sentence in starts if s == start)
            flags.append(
                Flag(
                    "repeated-opening",
                    first[0],
                    f"Sentence opening appears {count} times: {start}",
                    compact(first[1]),
                )
            )
    return flags


def collect_flags(text: str) -> list[Flag]:
    flags: list[Flag] = []
    sentences = sentence_records(text)

    for line, sentence, count in sentences:
        if count > 42:
            flags.append(
                Flag(
                    "long-sentence",
                    line,
                    f"{count} words; heuristic flag only—inspect clause load, referents, and oral spine.",
                    compact(sentence),
                )
            )

    for paragraph in re.finditer(r"(?:^|\n\n)(.+?)(?=\n\n|\Z)", text, re.S):
        value = paragraph.group(1).strip()
        if not value:
            continue
        count = len(words(value))
        if count > 150:
            flags.append(
                Flag(
                    "long-paragraph",
                    line_number(text, paragraph.start(1)),
                    f"{count} words; heuristic flag only—inspect beat unity and audio orientation.",
                    compact(value),
                )
            )

    for name, pattern in FORMULA_PATTERNS.items():
        for match in pattern.finditer(text):
            flags.append(
                Flag(
                    "formulaic-phrase",
                    line_number(text, match.start()),
                    f"Formula-like pattern: {name}",
                    compact(match.group()),
                )
            )

    for pronoun in PRONOUNS:
        pattern = re.compile(rf"\b{re.escape(pronoun)}\b", re.I)
        for match in pattern.finditer(text):
            window_start = max(0, match.start() - 120)
            window_end = min(len(text), match.end() + 120)
            window = text[window_start:window_end]
            if len(pattern.findall(window)) >= 3:
                flags.append(
                    Flag(
                        "pronoun-cluster",
                        line_number(text, match.start()),
                        f"Repeated pronoun near this point: {pronoun}",
                        compact(window),
                    )
                )
                break

    for match in SYMBOL_RE.finditer(text):
        flags.append(
            Flag(
                "tts-risk",
                line_number(text, match.start()),
                "Number, symbol, abbreviation, or URL may need pronunciation handling.",
                compact(match.group()),
            )
        )

    flags.extend(repeated_sentence_openings(sentences))
    return sorted(flags, key=lambda flag: (flag.line, flag.category))


def metrics(text: str) -> dict[str, object]:
    sentence_data = sentence_records(text)
    word_count = len(words(text))
    sentence_lengths = [count for _, _, count in sentence_data]
    dialogue_matches = DIALOGUE_RE.findall(text)
    dialogue_words = sum(len(words(match)) for match in dialogue_matches)
    paragraphs = [p for p in re.split(r"\n\s*\n", text) if p.strip()]
    avg_sentence = round(sum(sentence_lengths) / len(sentence_lengths), 1) if sentence_lengths else 0
    dialogue_ratio = round(dialogue_words / word_count, 3) if word_count else 0
    return {
        "words": word_count,
        "sentences": len(sentence_data),
        "paragraphs": len(paragraphs),
        "avg_sentence_words": avg_sentence,
        "max_sentence_words": max(sentence_lengths) if sentence_lengths else 0,
        "dialogue_word_ratio_estimate": dialogue_ratio,
    }


def render_markdown(text: str) -> str:
    data = metrics(text)
    flags = collect_flags(text)
    lines = [
        "# Audio Story Surface Statistics",
        "",
        "| Metric | Value |",
        "|---|---:|",
    ]
    for key, value in data.items():
        lines.append(f"| {key} | {value} |")
    lines.append("")
    lines.append("## Advisory Flags")
    if not flags:
        lines.append("")
        lines.append("No surface flags found. This does not prove the manuscript is ready.")
    else:
        lines.append("")
        lines.append("| Line | Category | Message | Excerpt |")
        lines.append("|---:|---|---|---|")
        for flag in flags[:80]:
            excerpt = flag.excerpt.replace("|", "\\|")
            lines.append(f"| {flag.line} | {flag.category} | {flag.message} | {excerpt} |")
        if len(flags) > 80:
            lines.append(f"|  |  | {len(flags) - 80} more flags omitted. |  |")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manuscript", help="Path to a Vietnamese story manuscript.")
    parser.add_argument("--json", action="store_true", help="Print JSON instead of markdown.")
    args = parser.parse_args()

    text = Path(args.manuscript).read_text(encoding="utf-8")
    if args.json:
        print(
            json.dumps(
                {"metrics": metrics(text), "flags": [asdict(flag) for flag in collect_flags(text)]},
                ensure_ascii=False,
                indent=2,
            )
        )
    else:
        print(render_markdown(text))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
