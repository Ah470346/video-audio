#!/usr/bin/env python3
"""Mirror canonical .agents audio assets into Claude Code's official .claude layout."""
from __future__ import annotations

import argparse
import shutil
from pathlib import Path
from typing import Iterable

TEXT_SUFFIXES = {".md", ".txt", ".json", ".toml", ".py", ".sh", ".yaml", ".yml"}


def build_replacements(specs: Iterable[Path]) -> tuple[tuple[str, str], ...]:
    """Build runtime mappings from canonical spec filenames.

    Paths must be replaced before bare identifiers; otherwise replacing
    ``audio_story_x`` first would leave a broken ``.codex/agents/audio-story-x.toml``
    path in Claude mirrors.
    """
    stems = sorted({p.stem for p in specs})
    path_pairs = [
        (f".codex/agents/{stem.replace('-', '_')}.toml", f".claude/agents/{stem}.md")
        for stem in stems
    ]
    name_pairs = [(stem.replace("-", "_"), stem) for stem in stems]
    return tuple(path_pairs + name_pairs)


def transform(text: str, replacements: tuple[tuple[str, str], ...]) -> str:
    for old, new in replacements:
        text = text.replace(old, new)
    return text


def copy_text(src: Path, dst: Path, replacements: tuple[tuple[str, str], ...]) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(transform(src.read_text(encoding="utf-8"), replacements), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    args = parser.parse_args()

    root = Path(args.root).expanduser().resolve()
    source_skills = root / ".agents" / "skills"
    target_skills = root / ".claude" / "skills"
    source_specs = root / ".agents" / "agent-specs"
    target_agents = root / ".claude" / "agents"

    if not source_skills.is_dir():
        raise SystemExit(f"missing {source_skills}")
    if not source_specs.is_dir():
        raise SystemExit(f"missing {source_specs}")

    specs = sorted(source_specs.glob("*.md"))
    if not specs:
        raise SystemExit(f"no canonical agent specs in {source_specs}")
    replacements = build_replacements(specs)

    if target_skills.exists():
        shutil.rmtree(target_skills)
    target_skills.mkdir(parents=True)

    for src in source_skills.rglob("*"):
        rel = src.relative_to(source_skills)
        if "_legacy-long-form" in rel.parts:
            continue
        dst = target_skills / rel
        if src.is_dir():
            dst.mkdir(parents=True, exist_ok=True)
        elif src.suffix.lower() in TEXT_SUFFIXES:
            copy_text(src, dst, replacements)
        else:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)

    if target_agents.exists():
        shutil.rmtree(target_agents)
    target_agents.mkdir(parents=True)

    for src in specs:
        text = transform(src.read_text(encoding="utf-8"), replacements).replace(
            "Follow `.agents/skills/", "Follow `.claude/skills/"
        )
        (target_agents / src.name).write_text(text, encoding="utf-8")

    skill_count = sum(1 for _ in source_skills.glob("*/SKILL.md"))
    print(f"CLAUDE_LAYOUT_SYNCED skills={skill_count} agents={len(specs)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
