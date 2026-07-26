#!/usr/bin/env python3
"""Fail when canonical .agents assets and Claude/Codex runtime mappings diverge."""
from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Iterable

TEXT_SUFFIXES = {".md", ".txt", ".json", ".toml", ".py", ".sh", ".yaml", ".yml"}
WRITABLE_AGENT_STEMS = {"audio-story-scene-doctor"}


def build_replacements(specs: Iterable[Path]) -> tuple[tuple[str, str], ...]:
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


def expected_claude_spec(text: str, replacements: tuple[tuple[str, str], ...]) -> str:
    return transform(text, replacements).replace("Follow `.agents/skills/", "Follow `.claude/skills/")


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    args = parser.parse_args()
    root = Path(args.root).expanduser().resolve()
    errors: list[str] = []

    canonical_skills = root / ".agents" / "skills"
    claude_skills = root / ".claude" / "skills"
    canonical_specs = root / ".agents" / "agent-specs"
    claude_agents = root / ".claude" / "agents"
    codex_agents = root / ".codex" / "agents"

    for path in (canonical_skills, claude_skills, canonical_specs, claude_agents, codex_agents):
        if not path.is_dir():
            errors.append(f"missing directory: {path}")

    if errors:
        print("PARITY_FAIL")
        print("\n".join(f"- {e}" for e in errors))
        return 1

    specs = sorted(canonical_specs.glob("*.md"))
    if not specs:
        errors.append("no canonical agent specs found")
        replacements: tuple[tuple[str, str], ...] = ()
    else:
        replacements = build_replacements(specs)

    source_skill_dirs = {p.parent.name for p in canonical_skills.glob("*/SKILL.md")}
    target_skill_dirs = {p.parent.name for p in claude_skills.glob("*/SKILL.md")}
    for name in sorted(source_skill_dirs - target_skill_dirs):
        errors.append(f"Claude skill mirror missing: {name}")
    for name in sorted(target_skill_dirs - source_skill_dirs):
        errors.append(f"Claude has non-canonical skill: {name}")

    for src in canonical_skills.rglob("*"):
        rel = src.relative_to(canonical_skills)
        if "_legacy-long-form" in rel.parts or src.is_dir():
            continue
        dst = claude_skills / rel
        if not dst.is_file():
            errors.append(f"Claude skill file missing: {rel}")
            continue
        if src.suffix.lower() in TEXT_SUFFIXES:
            expected = transform(read(src), replacements)
            actual = read(dst)
            if actual != expected:
                errors.append(f"Claude skill mirror stale: {rel}")

    expected_claude_names = {p.name for p in specs}
    actual_claude_names = {p.name for p in claude_agents.glob("*.md")}
    for name in sorted(expected_claude_names - actual_claude_names):
        errors.append(f"Claude agent missing: {name}")
    for name in sorted(actual_claude_names - expected_claude_names):
        errors.append(f"Claude has non-canonical agent: {name}")

    expected_codex_names = {f"{p.stem.replace('-', '_')}.toml" for p in specs}
    actual_codex_names = {p.name for p in codex_agents.glob("*.toml")}
    for name in sorted(expected_codex_names - actual_codex_names):
        errors.append(f"Codex agent wrapper missing: {name}")
    for name in sorted(actual_codex_names - expected_codex_names):
        errors.append(f"Codex has non-canonical agent wrapper: {name}")

    for spec in specs:
        spec_text = read(spec)
        stem = spec.stem
        if not re.search(rf"^name:\s*{re.escape(stem)}\s*$", spec_text, re.MULTILINE):
            errors.append(f"canonical agent frontmatter name mismatch: {spec.name}")

        expected_permission = "acceptEdits" if stem in WRITABLE_AGENT_STEMS else "plan"
        if not re.search(rf"^permissionMode:\s*{re.escape(expected_permission)}\s*$", spec_text, re.MULTILINE):
            errors.append(f"canonical agent permissionMode mismatch: {spec.name}")

        claude_path = claude_agents / spec.name
        if claude_path.is_file() and read(claude_path) != expected_claude_spec(spec_text, replacements):
            errors.append(f"Claude agent mirror stale: {spec.name}")

        codex_name = stem.replace("-", "_")
        codex_path = codex_agents / f"{codex_name}.toml"
        if not codex_path.is_file():
            continue
        toml = read(codex_path)
        if not re.search(rf'^name\s*=\s*"{re.escape(codex_name)}"\s*$', toml, re.MULTILINE):
            errors.append(f"Codex agent name mismatch: {codex_path.name}")
        canonical_ref = f".agents/agent-specs/{spec.name}"
        if canonical_ref not in toml:
            errors.append(f"Codex agent does not reference canonical spec: {codex_path.name}")

        expected_sandbox = "workspace-write" if stem in WRITABLE_AGENT_STEMS else "read-only"
        if f'sandbox_mode = "{expected_sandbox}"' not in toml:
            errors.append(f"Codex agent sandbox mismatch ({expected_sandbox} required): {codex_path.name}")

    if errors:
        print("PARITY_FAIL")
        print("\n".join(f"- {e}" for e in errors))
        return 1

    print(f"PARITY_OK skills={len(source_skill_dirs)} agents={len(specs)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
