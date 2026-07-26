#!/usr/bin/env python3
"""Calculate the Audio Story Reviewer weighted rubric.

Input is a JSON object mapping category slugs to raw scores from 0 to 5 in
0.5-point increments. Run with --template to print a fillable JSON template.

The arithmetic band does not certify recording readiness. Use --readiness-gate
for unresolved blocking defects.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Category:
    slug: str
    label: str
    weight: int


CATEGORIES: tuple[Category, ...] = (
    Category("grammar", "Grammar, wording, punctuation", 8),
    Category("sentence_flow", "Sentence flow and oral rhythm", 8),
    Category("scene_coherence", "Scene coherence and transitions", 9),
    Category("pov_narrator", "POV and narrator consistency", 7),
    Category("forms_of_address", "Forms of address and relationships", 7),
    Category("character_agency", "Character continuity, motivation, agency", 7),
    Category("causality", "Causal logic and plausibility", 12),
    Category("pacing", "Pacing, escalation, climax, resolution", 12),
    Category("emotion", "Emotional authenticity and human texture", 10),
    Category("dialogue", "Dialogue naturalness and function", 7),
    Category("genre", "Genre and target alignment", 7),
    Category("audio_clarity", "Audio clarity, listenability, and TTS readiness", 6),
)


def load_scores(path: str | None) -> dict[str, float]:
    if path:
        raw = Path(path).read_text(encoding="utf-8")
    else:
        raw = sys.stdin.read()
    data = json.loads(raw)
    if not isinstance(data, dict):
        raise SystemExit("Input must be a JSON object.")
    return {str(key): float(value) for key, value in data.items()}


def validate(scores: dict[str, float]) -> None:
    valid = {category.slug for category in CATEGORIES}
    unknown = sorted(set(scores) - valid)
    if unknown:
        raise SystemExit(f"Unknown category slug(s): {', '.join(unknown)}")
    missing = [category.slug for category in CATEGORIES if category.slug not in scores]
    if missing:
        raise SystemExit(f"Missing category slug(s): {', '.join(missing)}")
    out_of_range = [slug for slug, score in scores.items() if score < 0 or score > 5]
    if out_of_range:
        raise SystemExit(f"Scores must be between 0 and 5: {', '.join(out_of_range)}")
    invalid_increment = [
        slug for slug, score in scores.items() if abs(score * 2 - round(score * 2)) > 1e-9
    ]
    if invalid_increment:
        raise SystemExit(
            "Scores must use 0.5-point increments: " + ", ".join(invalid_increment)
        )


def score_band(total: float) -> str:
    if total >= 90:
        return "ready after light polish"
    if total >= 75:
        return "strong draft; targeted revision"
    if total >= 60:
        return "substantial revision before recording"
    return "rebuild major foundations"


def render_markdown(scores: dict[str, float], readiness_gates: list[str]) -> str:
    lines = [
        "| Category | Raw /5 | Weight | Weighted |",
        "|---|---:|---:|---:|",
    ]
    total = 0.0
    for category in CATEGORIES:
        raw = scores[category.slug]
        weighted = raw / 5 * category.weight
        total += weighted
        lines.append(
            f"| {category.label} | {raw:g} | {category.weight} | {weighted:.1f} |"
        )
    lines.append(f"| **Total** |  | **100** | **{total:.1f}** |")
    lines.append("")
    lines.append(f"Arithmetic band: {score_band(total)}.")
    if readiness_gates:
        lines.append(
            "Recording readiness: not ready while these gates remain unresolved: "
            + ", ".join(readiness_gates)
            + "."
        )
    else:
        lines.append(
            "Recording readiness: no blocking gate supplied; verify P0/P1 gates separately."
        )
    return "\n".join(lines)


def template() -> str:
    return json.dumps({category.slug: 3 for category in CATEGORIES}, ensure_ascii=False, indent=2)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("scores_json", nargs="?", help="Path to JSON scores. Reads stdin if omitted.")
    parser.add_argument("--template", action="store_true", help="Print a fillable JSON template.")
    parser.add_argument(
        "--readiness-gate",
        action="append",
        default=[],
        choices=(
            "p0",
            "central-causality",
            "climax",
            "ending",
            "speaker-identity",
            "essential-pronunciation",
            "tts-pause-structure",
            "tts-token-risk",
        ),
        help="Record an unresolved defect that blocks recording; may be repeated.",
    )
    args = parser.parse_args()

    if args.template:
        print(template())
        return 0

    scores = load_scores(args.scores_json)
    validate(scores)
    print(render_markdown(scores, args.readiness_gate))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
