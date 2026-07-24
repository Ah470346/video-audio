#!/usr/bin/env python3
"""Post-process a Kaggle-rendered final audio file before saving it locally."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AUDIO_EXTENSIONS = {".wav", ".mp3", ".m4a", ".flac", ".ogg", ".aac"}


def build_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("--result-dir", help="Downloaded Kaggle output folder to search")
    parser.add_argument("--input", help="Explicit final/mastered audio path")
    parser.add_argument("--story-slug", required=True, help="Filesystem-safe output name")
    parser.add_argument("--output-dir", default=str(ROOT / "audio"))
    parser.add_argument("--speed", type=float, default=1.25)
    parser.add_argument("--force", action="store_true")
    return parser


def candidate_score(path: Path, story_slug: str) -> tuple[int, int, str]:
    name = path.stem.lower()
    ext_bonus = 20 if path.suffix.lower() == ".wav" else 0
    keyword_bonus = sum(
        bonus
        for keyword, bonus in (
            ("final", 50),
            ("mastered", 45),
            ("master", 40),
            (story_slug.lower(), 25),
        )
        if keyword and keyword in name
    )
    return (keyword_bonus + ext_bonus, path.stat().st_size, str(path))


def find_final_audio(result_dir: Path, story_slug: str) -> Path:
    candidates = [
        path
        for path in result_dir.rglob("*")
        if path.is_file() and path.suffix.lower() in AUDIO_EXTENSIONS
    ]
    if not candidates:
        raise FileNotFoundError(f"No audio files found under {result_dir}")
    return max(candidates, key=lambda path: candidate_score(path, story_slug))


def atempo_filter(speed: float) -> str:
    if speed <= 0:
        raise ValueError("--speed must be greater than 0")

    filters = []
    remaining = speed
    while remaining > 2.0:
        filters.append("atempo=2.0")
        remaining /= 2.0
    while remaining < 0.5:
        filters.append("atempo=0.5")
        remaining /= 0.5
    filters.append(f"atempo={remaining:.8g}")
    return ",".join(filters)


def speed_audio(input_path: Path, output_path: Path, speed: float, force: bool) -> None:
    ffmpeg_bin = shutil.which("ffmpeg")
    if not ffmpeg_bin:
        raise RuntimeError("ffmpeg not found. Install ffmpeg before post-processing audio.")

    if output_path.exists() and not force:
        raise FileExistsError(f"Output exists: {output_path}. Pass --force to overwrite.")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        ffmpeg_bin,
        "-y" if force else "-n",
        "-hide_banner",
        "-loglevel",
        "error",
        "-i",
        str(input_path),
        "-filter:a",
        atempo_filter(speed),
        str(output_path),
    ]
    subprocess.run(cmd, check=True)


def main():
    args = build_parser().parse_args()
    if not args.input and not args.result_dir:
        print("Error: pass either --input or --result-dir.", file=sys.stderr)
        return 2

    input_path = Path(args.input).resolve() if args.input else find_final_audio(
        Path(args.result_dir).resolve(),
        args.story_slug,
    )
    if not input_path.is_file():
        print(f"Error: input audio not found: {input_path}", file=sys.stderr)
        return 2

    output_dir = Path(args.output_dir).resolve()
    output_path = output_dir / f"{args.story_slug}{input_path.suffix.lower()}"
    speed_audio(input_path, output_path, args.speed, args.force)

    print(f"Source audio: {input_path}")
    print(f"Speed: {args.speed:g}x")
    print(f"Saved audio: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
