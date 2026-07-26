#!/usr/bin/env python3
"""Validator for audio-story protocol-v2 completion manifests.

By default this remains fail-closed. Callers may opt into an explicit user
bypass when the user knowingly asks to proceed without the manuscript gate.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

HEX64 = re.compile(r"^[0-9a-f]{64}$")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def resolve_story_from_manifest(manifest_path: Path, value: str) -> Path:
    candidate = Path(value).expanduser()
    return ((manifest_path.parent / candidate) if not candidate.is_absolute() else candidate).resolve()


def require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def obj(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def integer_not_bool(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def receipt_v2(receipt: dict[str, Any], label: str, errors: list[str]) -> None:
    require(receipt.get("protocol_version") == 2, f"{label} receipt must use protocol_version=2", errors)


def print_bypass(story: Path, mode: str, reason: str, errors: list[str]) -> int:
    actual_hash = sha256_file(story)
    print("GATE_VALIDATION_BYPASSED")
    print("bypass_actor=user")
    print(f"bypass_reason={reason}")
    print(f"mode={mode}")
    print(f"sha256={actual_hash}")
    print("bypassed_errors:")
    print("\n".join(f"- {e}" for e in errors))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--story", required=True)
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--mode", choices=("pre-gate", "final"), default="pre-gate")
    parser.add_argument(
        "--allow-user-bypass",
        action="store_true",
        help="Return success despite gate errors when the user explicitly asks to bypass the story gate.",
    )
    parser.add_argument(
        "--bypass-reason",
        default=None,
        help="Required short reason when --allow-user-bypass is used.",
    )
    args = parser.parse_args()

    story = Path(args.story).expanduser().resolve()
    manifest_path = Path(args.manifest).expanduser().resolve()
    errors: list[str] = []
    if args.allow_user_bypass and not (args.bypass_reason or "").strip():
        print("GATE_VALIDATION_FAILED")
        print("- --bypass-reason is required with --allow-user-bypass")
        return 2

    require(story.is_file(), f"story not found: {story}", errors)
    require(manifest_path.is_file(), f"manifest not found: {manifest_path}", errors)
    if errors:
        if args.allow_user_bypass and story.is_file():
            return print_bypass(story, args.mode, args.bypass_reason.strip(), errors)
        print("GATE_VALIDATION_FAILED")
        print("\n".join(f"- {e}" for e in errors))
        return 1

    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        if args.allow_user_bypass:
            return print_bypass(story, args.mode, args.bypass_reason.strip(), [f"invalid manifest JSON: {exc}"])
        print("GATE_VALIDATION_FAILED")
        print(f"- invalid manifest JSON: {exc}")
        return 1

    if not isinstance(manifest, dict):
        errors.append("manifest root must be an object")
        if args.allow_user_bypass:
            return print_bypass(story, args.mode, args.bypass_reason.strip(), errors)
        print("GATE_VALIDATION_FAILED")
        print("\n".join(f"- {e}" for e in errors))
        return 1
    version = manifest.get("protocol_version")
    if version == 1:
        errors.append("legacy protocol_version=1 cannot pass; migrate to protocol version 2 and rerun all current checks")
    else:
        require(version == 2, "protocol_version must be 2", errors)

    story_path_value = manifest.get("story_path")
    require(isinstance(story_path_value, str) and bool(story_path_value), "story_path is required", errors)
    if isinstance(story_path_value, str) and story_path_value:
        manifest_story = resolve_story_from_manifest(manifest_path, story_path_value)
        require(manifest_story == story, f"story_path resolves to {manifest_story}, not {story}", errors)

    revision = manifest.get("current_revision")
    require(integer_not_bool(revision) and revision >= 1, "current_revision must be an integer >= 1", errors)

    actual_hash = sha256_file(story)
    current_hash = manifest.get("current_sha256")
    require(isinstance(current_hash, str) and bool(HEX64.fullmatch(current_hash)), "current_sha256 must be a 64-character hexadecimal SHA-256", errors)
    require(current_hash == actual_hash, f"current_sha256 mismatch: manifest={current_hash!r} actual={actual_hash}", errors)

    polish = obj(manifest.get("final_polish_receipt"))
    require(bool(polish), "final polish receipt is required", errors)
    receipt_v2(polish, "final polish", errors)
    require(polish.get("issued_by") == "audio-story-final-polish", "final polish receipt has unexpected issuer", errors)
    require(polish.get("status") == "completed", "final polish receipt must have status=completed", errors)
    polish_input_revision = polish.get("input_revision")
    polish_input_hash = polish.get("input_sha256")
    require(integer_not_bool(polish_input_revision) and polish_input_revision >= 1, "final polish input_revision must be an integer >= 1", errors)
    require(isinstance(polish_input_hash, str) and bool(HEX64.fullmatch(polish_input_hash)), "final polish input_sha256 must be a 64-character hexadecimal SHA-256", errors)
    require(polish.get("output_revision") == revision, "final polish output revision is stale", errors)
    require(polish.get("output_sha256") == actual_hash, "final polish output hash is stale", errors)
    if integer_not_bool(polish_input_revision) and integer_not_bool(revision):
        require(
            polish_input_revision in (revision, revision - 1),
            "final polish revision transition must keep revision unchanged or increment it by exactly one",
            errors,
        )
        if polish_input_revision == revision:
            require(polish_input_hash == actual_hash, "no-change final polish must preserve the input hash", errors)
        elif polish_input_revision == revision - 1:
            require(polish_input_hash != actual_hash, "changed final polish must produce a different output hash", errors)

    pre_development = obj(manifest.get("pre_polish_development_receipt"))
    require(bool(pre_development), "pre-polish development receipt is required", errors)
    receipt_v2(pre_development, "pre-polish development", errors)
    require(pre_development.get("issued_by") == "audio-story-developmental-editor", "pre-polish development receipt has unexpected issuer", errors)
    require(pre_development.get("scope") == "full-draft", "pre-polish development receipt must have scope=full-draft", errors)
    require(pre_development.get("mode") == "developmental", "pre-polish development receipt must have mode=developmental", errors)
    require(pre_development.get("status") == "clean", "pre-polish development receipt must have status=clean", errors)
    require(pre_development.get("coverage") == "complete", "pre-polish development receipt must have coverage=complete", errors)
    require(pre_development.get("revision") == polish_input_revision, "pre-polish development receipt does not match final polish input revision", errors)
    require(pre_development.get("sha256") == polish_input_hash, "pre-polish development receipt does not match final polish input hash", errors)
    require(pre_development.get("total_blockers") == 0, "pre-polish development receipt must have zero blockers", errors)
    require(pre_development.get("total_major_findings") == 0, "pre-polish development receipt must have zero major findings", errors)
    require(integer_not_bool(pre_development.get("total_moderate_findings")) and pre_development.get("total_moderate_findings") >= 0, "pre-polish development receipt moderate finding count is invalid", errors)

    pre_clarity = obj(manifest.get("pre_polish_clarity_receipt"))
    require(bool(pre_clarity), "pre-polish clarity receipt is required", errors)
    receipt_v2(pre_clarity, "pre-polish clarity", errors)
    require(pre_clarity.get("issued_by") == "audio-story-clarity-check", "pre-polish clarity receipt has unexpected issuer", errors)
    require(pre_clarity.get("scope") == "full-draft", "pre-polish clarity receipt must have scope=full-draft", errors)
    require(pre_clarity.get("stage") == "pre-polish", "pre-polish clarity receipt must have stage=pre-polish", errors)
    require(pre_clarity.get("status") == "clean", "pre-polish clarity receipt must have status=clean", errors)
    require(pre_clarity.get("coverage") == "complete", "pre-polish clarity receipt must have coverage=complete", errors)
    require(pre_clarity.get("revision") == polish_input_revision, "pre-polish clarity receipt does not match final polish input revision", errors)
    require(pre_clarity.get("sha256") == polish_input_hash, "pre-polish clarity receipt does not match final polish input hash", errors)
    require(pre_clarity.get("total_findings") == 0, "pre-polish clarity receipt must have zero findings", errors)
    pre_gaps = pre_clarity.get("continuity_gaps")
    require(pre_gaps in (None, [], "", "none"), "pre-polish clarity receipt has continuity gaps", errors)

    development = obj(manifest.get("development_receipt"))
    require(bool(development), "development receipt is required", errors)
    receipt_v2(development, "development", errors)
    require(development.get("issued_by") == "audio-story-developmental-editor", "development receipt has unexpected issuer", errors)
    require(development.get("scope") == "full-draft", "development receipt must have scope=full-draft", errors)
    require(development.get("mode") == "post-polish", "development receipt must have mode=post-polish", errors)
    require(development.get("status") == "clean", "development receipt must have status=clean", errors)
    require(development.get("coverage") == "complete", "development receipt must have coverage=complete", errors)
    require(development.get("revision") == revision, "development receipt revision is stale", errors)
    require(development.get("sha256") == actual_hash, "development receipt hash is stale", errors)
    require(development.get("total_blockers") == 0, "development receipt must have zero blockers", errors)
    require(development.get("total_major_findings") == 0, "development receipt must have zero major findings", errors)
    require(integer_not_bool(development.get("total_moderate_findings")) and development.get("total_moderate_findings") >= 0, "development receipt moderate finding count is invalid", errors)

    clarity = obj(manifest.get("clarity_receipt"))
    require(bool(clarity), "clarity receipt is required", errors)
    receipt_v2(clarity, "clarity", errors)
    require(clarity.get("issued_by") == "audio-story-clarity-check", "clarity receipt has unexpected issuer", errors)
    require(clarity.get("scope") == "full-draft", "clarity receipt must have scope=full-draft", errors)
    require(clarity.get("stage") == "post-polish", "clarity receipt must have stage=post-polish", errors)
    require(clarity.get("status") == "clean", "clarity receipt must have status=clean", errors)
    require(clarity.get("coverage") == "complete", "clarity receipt must have coverage=complete", errors)
    require(clarity.get("revision") == revision, "clarity receipt revision is stale", errors)
    require(clarity.get("sha256") == actual_hash, "clarity receipt hash is stale", errors)
    require(clarity.get("total_findings") == 0, "clarity receipt must have zero findings", errors)
    gaps = clarity.get("continuity_gaps")
    require(gaps in (None, [], "", "none"), "clarity receipt has continuity gaps", errors)

    if args.mode == "final":
        gate = obj(manifest.get("completion_gate_receipt"))
        require(bool(gate), "completion gate receipt is required", errors)
        receipt_v2(gate, "completion gate", errors)
        require(gate.get("status") == "pass", "completion gate receipt must have status=pass", errors)
        require(gate.get("revision") == revision, "completion gate revision is stale", errors)
        require(gate.get("sha256") == actual_hash, "completion gate hash is stale", errors)
        require(gate.get("gate_agent") == "audio-story-completion-gate", "unexpected gate_agent", errors)
        require(gate.get("validator_mode") == "pre-gate", "completion gate validator_mode must be pre-gate", errors)

    if errors:
        if args.allow_user_bypass:
            return print_bypass(story, args.mode, args.bypass_reason.strip(), errors)
        print("GATE_VALIDATION_FAILED")
        print("\n".join(f"- {e}" for e in errors))
        return 1

    print("GATE_VALIDATION_OK")
    print("protocol_version=2")
    print(f"mode={args.mode}")
    print(f"revision={revision}")
    print(f"sha256={actual_hash}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
