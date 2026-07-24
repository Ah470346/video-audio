#!/usr/bin/env python3
"""Audit already-rendered VoxCPM chunks without re-rendering them."""

import argparse
from difflib import SequenceMatcher
import json
import os
import sys
import time


REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from voxcpm_story_core import (  # noqa: E402
    MLXWhisperSession,
    SWALLOW_DB,
    _normalize_for_compare,
    clause_asr_transcript,
    sanitize_proxy_env,
    timing_defects,
)


def load_entries(path):
    with open(path, "r", encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]


def main():
    parser = argparse.ArgumentParser(
        description="Run fast or clause-isolated TTS checks over existing WAV chunks."
    )
    parser.add_argument("--jsonl", required=True, help="Chunk manifest produced by the TTS script.")
    parser.add_argument("--audio-dir", default=None, help="Directory containing <chunk-id>.wav files.")
    parser.add_argument(
        "--model", default="mlx-community/whisper-large-v3-turbo",
        help="mlx_whisper model used for word timestamps.",
    )
    parser.add_argument("--report", default=None, help="Optional JSON report output path.")
    parser.add_argument(
        "--only", default=None,
        help="Audit only these comma-separated chunk indexes or full IDs (for example: 4,12,48).",
    )
    parser.add_argument(
        "--full", action="store_true",
        help="Use slow clause-isolated ASR instead of the fast timing/dB checks.",
    )
    parser.add_argument(
        "--threshold", type=float, default=0.995,
        help="Pass threshold for --full clause-isolated ASR (default: 0.995).",
    )
    parser.add_argument(
        "--swallow-db", type=float, default=SWALLOW_DB,
        help=f"Swallowed-syllable threshold relative to chunk median (default: {SWALLOW_DB:g} dB).",
    )
    parser.add_argument(
        "--require-all", action="store_true",
        help="Treat manifest entries with no WAV file as failures.",
    )
    args = parser.parse_args()
    sanitize_proxy_env()

    entries = load_entries(args.jsonl)
    if args.only:
        wanted = {token.strip().lstrip("0") or "0" for token in args.only.split(",")}
        entries = [
            entry for entry in entries
            if entry["id"] in wanted
            or (entry["id"].rsplit("_", 1)[-1].lstrip("0") or "0") in wanted
        ]
    audio_dir = args.audio_dir or os.path.dirname(os.path.abspath(args.jsonl))
    results = []
    started = time.monotonic()
    session = MLXWhisperSession()

    for entry in entries:
        wav_path = os.path.join(audio_dir, f"{entry['id']}.wav")
        if not os.path.exists(wav_path):
            if args.require_all:
                results.append({"id": entry["id"], "status": "missing", "reason": "WAV missing"})
                print(f"MISSING {entry['id']}")
            continue

        chunk_started = time.monotonic()
        if args.full:
            heard_text = clause_asr_transcript(
                wav_path, args.model, transcriber=session
            )
            if heard_text is None:
                score = None
                reason = "ASR failed"
            else:
                expected = _normalize_for_compare(entry["text"])
                heard = _normalize_for_compare(heard_text)
                matcher = SequenceMatcher(None, expected, heard)
                score = matcher.ratio()
                differences = []
                for tag, i1, i2, j1, j2 in matcher.get_opcodes():
                    if tag != "equal":
                        differences.append(
                            f"{tag} {expected[i1:i2]!r} -> {heard[j1:j2]!r}"
                        )
                diff_text = "; ".join(differences[:3]) or "none"
                reason = f"clause ASR similarity {score:.3f}; diff: {diff_text}"
        else:
            score, reason = timing_defects(
                wav_path, entry["text"], args.model, args.swallow_db,
                transcriber=session,
            )
        elapsed = time.monotonic() - chunk_started
        if score is None:
            status = "unavailable"
        elif args.full:
            status = "pass" if score >= args.threshold else "fail"
        else:
            status = "pass" if reason.startswith("ok") else "fail"
        result = {
            "id": entry["id"],
            "status": status,
            "score": score,
            "reason": reason,
            "seconds": round(elapsed, 3),
        }
        results.append(result)
        score_text = "n/a" if score is None else f"{score:.3f}"
        print(f"{status.upper():11} {entry['id']} score={score_text} | {reason}")

    session.close()

    counts = {status: sum(item["status"] == status for item in results)
              for status in ("pass", "fail", "missing", "unavailable")}
    report = {
        "jsonl": os.path.abspath(args.jsonl),
        "audio_dir": os.path.abspath(audio_dir),
        "mode": "clause" if args.full else "fast",
        "elapsed_seconds": round(time.monotonic() - started, 3),
        "counts": counts,
        "results": results,
    }
    print(json.dumps({"elapsed_seconds": report["elapsed_seconds"], **counts}, ensure_ascii=False))

    if args.report:
        with open(args.report, "w", encoding="utf-8") as fh:
            json.dump(report, fh, ensure_ascii=False, indent=2)

    if counts["unavailable"]:
        return 2
    if counts["fail"] or counts["missing"]:
        return 1
    if not results:
        print("No WAV files matched the manifest.", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
