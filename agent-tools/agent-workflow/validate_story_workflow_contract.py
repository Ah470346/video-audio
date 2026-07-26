#!/usr/bin/env python3
"""Static contract checks for the audio-story workflow and anti-template guardrails."""
from __future__ import annotations
import argparse
import sys
from pathlib import Path

REQUIRED_AGENTS = {
    "audio-story-architect.md",
    "audio-story-clarity-check.md",
    "audio-story-completion-gate.md",
    "audio-story-developmental-editor.md",
    "audio-story-performance-analyst.md",
    "audio-story-scene-doctor.md",
    "audio-story-series-continuity.md",
    "audio-story-trend-researcher.md",
}
REQUIRED_MARKERS = {
    ".agents/skills/audio-story-engagement/SKILL.md": [
        "Do Not Sound Like A Writing Template",
        "audio-story-human-life",
        "rerun full-draft development and clarity",
        "mode: post-polish",
        "On the repaired revision",
    ],
    ".agents/skills/audio-story-engagement/references/phoi-hop-skills.md": [
        "Anti-template naturalness",
        "No rule creates a quota",
        "audio-story-human-life",
    ],
    ".agents/agent-specs/audio-story-developmental-editor.md": [
        "AI-Template Stiffness",
        "Anti-Quota Boundary",
        "audio-story-human-life",
        "issued_by: audio-story-developmental-editor",
    ],
    ".agents/agent-specs/audio-story-clarity-check.md": [
        "STAGE: pre-polish | post-polish",
        "issued_by: audio-story-clarity-check",
    ],
    ".agents/agent-specs/audio-story-architect.md": ["Anti-Template Boundary"],
    ".agents/agent-specs/audio-story-scene-doctor.md": ["Do Not Normalize The Story"],
    ".agents/skills/audio-story-literary-texture/SKILL.md": ["Remove Visible Technique", "audio-story-human-life"],
    ".agents/skills/audio-story-final-polish/SKILL.md": [
        "Protect Voice And Remove Template Machinery",
        "pre_polish_development_receipt",
        "issued_by: audio-story-final-polish",
        "Only then rerun this entire final polish",
    ],
    ".agents/skills/audio-story-engagement/references/completion-gate-protocol.md": [
        "protocol_version: 2",
        "rerun full-draft development and clarity",
        "pre_polish_development_receipt",
        "issued_by",
    ],
    ".agents/skills/story-to-audio/SKILL.md": [
        "development, clarity, final-polish, or completion-gate receipts are stale",
        "post-polish development/clarity",
        "independently rerun this final gate",
        "Do not copy or embed the",
    ],
    "tools/prepare_kaggle_voxcpm_job.py": [
        "validate_story_for_render",
        "story changed after gate validation",
        "\"story_gate\": story_gate",
        "default=2",
    ],
    "tools/prepare_kaggle_voxcpm_short_job.py": [
        "validate_story_for_render",
        "\"story_gate\": story_gate",
        "default=2",
    ],
}
FORBIDDEN_MARKERS = {
    ".agents/skills/audio-story-engagement/SKILL.md": [
        "If either post-polish check causes a text repair, rerun final polish, then",
    ],
    ".agents/skills/audio-story-final-polish/SKILL.md": [
        "rerun this entire final polish, then rerun full-draft development and clarity",
    ],
    ".agents/skills/audio-story-engagement/references/completion-gate-protocol.md": [
        "if any repair changes text: final polish again, then rerun full-draft development and clarity",
    ],
    "tools/prepare_kaggle_voxcpm_job.py": [
        'bundle_paths = [*COPY_FILES, "job_inputs", "render_job.json", "build_info.json", ".env"]',
        "shutil.copy2(env_path, job_dir / \".env\")",
        'default=3,\n        help="Extra render attempts',
    ],
    "tools/prepare_kaggle_voxcpm_short_job.py": [
        'bundle_paths = [*COPY_FILES, "job_inputs", "render_job.json", "build_info.json", ".env"]',
        "shutil.copy2(env_path, job_dir / \".env\")",
        'parser.add_argument("--max-verify-retries", type=int, default=3)',
    ],
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    args = parser.parse_args()
    root = Path(args.root).resolve()
    errors: list[str] = []

    if (root / ".agents" / "skills" / "audio-story-human-life").exists():
        errors.append("retired audio-story-human-life skill exists in canonical skills")

    specs = {p.name for p in (root / ".agents" / "agent-specs").glob("*.md")}
    if specs != REQUIRED_AGENTS:
        errors.append(f"agent spec set mismatch: expected={sorted(REQUIRED_AGENTS)} actual={sorted(specs)}")

    skills = {p.parent.name for p in (root / ".agents" / "skills").glob("*/SKILL.md")}
    if len(skills) != 15:
        errors.append(f"expected 15 canonical skills, found {len(skills)}: {sorted(skills)}")

    for rel, markers in REQUIRED_MARKERS.items():
        path = root / rel
        if not path.is_file():
            errors.append(f"missing contract file: {rel}")
            continue
        text = path.read_text(encoding="utf-8")
        for marker in markers:
            if marker not in text:
                errors.append(f"missing marker {marker!r} in {rel}")

    for rel, markers in FORBIDDEN_MARKERS.items():
        path = root / rel
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        for marker in markers:
            if marker in text:
                errors.append(f"forbidden stale marker {marker!r} in {rel}")

    if errors:
        print("WORKFLOW_CONTRACT_FAIL")
        print("\n".join(f"- {e}" for e in errors))
        return 1
    print("WORKFLOW_CONTRACT_OK skills=15 agents=8 protocol=2 retired_human_life=absent")
    return 0


if __name__ == "__main__":
    sys.exit(main())
