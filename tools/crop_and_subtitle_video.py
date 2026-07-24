#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CLI script to crop video to 9:16 and add subtitles using the helper module."""

import argparse
import sys
from pathlib import Path

# Add project root to sys.path to ensure we can import tools.video_helper
ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

from tools.video_helper import (
    find_manifest_by_video_name,
    generate_srt_from_manifest,
    crop_and_burn_subtitles,
    crop_and_add_title,
)

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Crop video to 9:16 and burn subtitles or static title."
    )
    parser.add_argument(
        "--video",
        required=True,
        help="Path to the input video file.",
    )
    parser.add_argument(
        "--manifest",
        help="Path to the VoxCPM manifest JSON. If omitted, search results/ directory.",
    )
    parser.add_argument(
        "--output",
        help="Path to output video. Defaults to <input_basename>_9_16.mp4 in the same directory.",
    )
    parser.add_argument(
        "--title",
        help="Overlay a static title in the center of the video instead of subtitles. Use '\\n' for newlines.",
    )
    parser.add_argument(
        "--font-size",
        type=int,
        help="Font size. Defaults to 22 for subtitles, 36 for title.",
    )
    parser.add_argument(
        "--color",
        default="yellow",
        choices=["yellow", "white", "cyan"],
        help="Color of subtitles/title. Default: yellow (for subtitles) or white (for title).",
    )
    parser.add_argument(
        "--alignment",
        type=int,
        default=2,
        help="Subtitle alignment (SSA/ASS format, e.g. 2=bottom center, 10=middle). Default: 2.",
    )
    parser.add_argument(
        "--margin-v",
        type=int,
        default=120,
        help="Vertical margin from the edge in pixels (only for subtitles). Default: 120.",
    )
    parser.add_argument(
        "--crf",
        type=int,
        default=23,
        help="CRF for video encoding (lower quality is higher CRF). Default: 23.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing output files.",
    )

    args = parser.parse_args()

    video_path = Path(args.video).resolve()
    if not video_path.is_file():
        print(f"Error: Video file not found: {video_path}", file=sys.stderr)
        return 1

    # Output paths
    if args.output:
        output_path = Path(args.output).resolve()
    else:
        output_path = video_path.parent / f"{video_path.stem}_9_16.mp4"

    # Overlay static title mode
    if args.title:
        title = args.title.replace("\\n", "\n")
        font_size = args.font_size if args.font_size is not None else 36
        # Title defaults to white if not specified or if color is default yellow
        color = args.color if args.color != "yellow" or "color" in sys.argv else "white"

        print("Cropping video to 9:16 and overlaying static title...")
        try:
            crop_and_add_title(
                input_path=video_path,
                output_path=output_path,
                title=title,
                font_size=font_size,
                color=color,
                crf=args.crf,
                force=args.force,
            )
        except Exception as e:
            print(f"Error processing video: {e}", file=sys.stderr)
            return 1

        print("\nProcess completed successfully!")
        print(f"Video    : {output_path}")
        return 0

    # Subtitle mode
    # Resolve manifest
    if args.manifest:
        manifest_path = Path(args.manifest).resolve()
    else:
        results_dir = ROOT / "results"
        print(f"Searching for manifest JSON matching '{video_path.stem}' in results/ ...")
        manifest_path = find_manifest_by_video_name(video_path, results_dir)
        if not manifest_path:
            print(
                f"Error: Could not find manifest matching '{video_path.stem}' automatically. "
                "Please specify path with --manifest.",
                file=sys.stderr,
            )
            return 1
        print(f"Found manifest: {manifest_path}")

    if not manifest_path.is_file():
        print(f"Error: Manifest file not found: {manifest_path}", file=sys.stderr)
        return 1

    srt_path = output_path.with_suffix(".srt")
    font_size = args.font_size if args.font_size is not None else 22

    # Step 1: Generate SRT
    print("Generating subtitles SRT...")
    try:
        generate_srt_from_manifest(manifest_path, srt_path)
    except Exception as e:
        print(f"Error generating SRT: {e}", file=sys.stderr)
        return 1

    # Step 2: Crop and burn
    print("Cropping video to 9:16 and burning subtitles...")
    try:
        crop_and_burn_subtitles(
            input_path=video_path,
            output_path=output_path,
            srt_path=srt_path,
            font_size=font_size,
            color=args.color,
            alignment=args.alignment,
            margin_v=args.margin_v,
            crf=args.crf,
            force=args.force,
        )
    except Exception as e:
        print(f"Error processing video: {e}", file=sys.stderr)
        return 1

    print("\nProcess completed successfully!")
    print(f"Subtitles: {srt_path}")
    print(f"Video    : {output_path}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
