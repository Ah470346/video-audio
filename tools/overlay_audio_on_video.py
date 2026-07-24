#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Overlay (replace) audio onto a template video using ffmpeg.

The video's original audio (if any) is discarded and replaced with the
supplied audio file.  The audio duration is always the master:
- If the video is **shorter** than the audio, the video loops.
- If the video is **longer** than the audio, the video is trimmed from
  the beginning to match the audio duration.

Usage:
    python3 tools/overlay_audio_on_video.py \
        --audio  expose/my-story.wav \
        --video  video-mau/template.mp4 \
        --output videos/my-story.mp4

    # Keep video's original audio and mix with the new audio
    python3 tools/overlay_audio_on_video.py \
        --audio  expose/my-story.wav \
        --video  video-mau/template.mp4 \
        --output videos/my-story.mp4 \
        --keep-video-audio --video-audio-volume -30

    # Custom video codec / quality
    python3 tools/overlay_audio_on_video.py \
        --audio  expose/my-story.wav \
        --video  video-mau/template.mp4 \
        --output videos/my-story.mp4 \
        --crf 20
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VIDEO_MAU_DIR = ROOT / "video-mau"
VIDEOS_DIR = ROOT / "videos"
VIDEO_EXTENSIONS = {".mp4", ".mkv", ".mov", ".avi", ".webm", ".flv", ".ts"}
AUDIO_EXTENSIONS = {".wav", ".mp3", ".m4a", ".flac", ".ogg", ".aac"}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Overlay audio onto a template video (replace or mix).",
    )
    parser.add_argument(
        "--audio",
        required=True,
        help="Path to the audio file to overlay onto the video.",
    )
    parser.add_argument(
        "--video",
        required=True,
        help="Path to the template video file.",
    )
    parser.add_argument(
        "--output",
        help="Output path. Defaults to videos/<audio-basename>.mp4.",
    )
    parser.add_argument(
        "--keep-video-audio",
        action="store_true",
        help="Mix new audio with the video's original audio instead of "
             "replacing it entirely.",
    )
    parser.add_argument(
        "--video-audio-volume",
        type=float,
        default=-30,
        help="Volume adjustment (dB) for the video's original audio when "
             "--keep-video-audio is used. Default: -30 dB.",
    )
    parser.add_argument(
        "--crf",
        type=int,
        default=23,
        help="Constant Rate Factor for H.264 encoding (lower = better "
             "quality, larger file). Default: 23.",
    )
    parser.add_argument(
        "--title",
        help="Overlay a static title in the center of the video.",
    )
    parser.add_argument(
        "--title-font-size",
        type=int,
        default=32,
        help="Font size for overlay title. Default: 32.",
    )
    parser.add_argument(
        "--crop-9-16",
        action="store_true",
        help="Crop video to 9:16 vertical aspect ratio.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite output file if it exists.",
    )
    return parser


def get_duration_seconds(path: Path) -> float:
    """Return the duration of a media file in seconds via ffprobe."""
    ffprobe = shutil.which("ffprobe")
    if not ffprobe:
        raise RuntimeError("ffprobe not found. Install ffmpeg (includes ffprobe).")
    result = subprocess.run(
        [
            ffprobe,
            "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            str(path),
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    return float(result.stdout.strip())


def list_video_files(video_dir: Path) -> list[Path]:
    """List all video files in the video-mau directory."""
    if not video_dir.is_dir():
        return []
    files = sorted(
        p for p in video_dir.iterdir()
        if p.is_file() and p.suffix.lower() in VIDEO_EXTENSIONS
    )
    return files


def overlay_audio(
    audio_path: Path,
    video_path: Path,
    output_path: Path,
    keep_video_audio: bool,
    video_audio_volume_db: float,
    crf: int,
    force: bool,
    title: str | None = None,
    title_font_size: int = 32,
    crop_9_16: bool = False,
) -> None:
    """Replace or mix audio onto a video using ffmpeg.

    Strategy:
    Audio duration is the master.  If the video is shorter, it loops.
    If the video is longer, it is trimmed to audio length (from the start).
    3. Encode with H.264 (libx264) + AAC.
    """
    full_ffmpeg = Path("/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg")
    if full_ffmpeg.is_file():
        ffmpeg_bin = str(full_ffmpeg)
    else:
        ffmpeg_bin = shutil.which("ffmpeg")

    if not ffmpeg_bin:
        raise RuntimeError("ffmpeg not found. Install ffmpeg before processing.")

    if output_path.exists() and not force:
        raise FileExistsError(
            f"Output exists: {output_path}. Pass --force to overwrite."
        )

    output_path.parent.mkdir(parents=True, exist_ok=True)

    audio_duration = get_duration_seconds(audio_path)
    video_duration = get_duration_seconds(video_path)

    # Calculate how many times the video needs to loop
    if video_duration > 0 and audio_duration > video_duration:
        import math
        loop_count = math.ceil(audio_duration / video_duration) - 1
    else:
        loop_count = 0

    temp_title_file = None
    try:
        filters = []
        if crop_9_16:
            filters.append("crop='2*trunc(ih*9/32):ih'")

        if title:
            formatted_title = title.replace("\\n", "\n")
            if "\n" not in formatted_title:
                words = formatted_title.strip().split()
                if len(words) == 5:
                    formatted_title = " ".join(words[:3]) + "\n" + " ".join(words[3:])
                elif len(words) > 2 and len(formatted_title) > 16:
                    mid = len(words) // 2
                    formatted_title = " ".join(words[:mid]) + "\n" + " ".join(words[mid:])

            temp_title_file = output_path.parent / f"{output_path.stem}_title_temp.txt"
            temp_title_file.write_text(formatted_title, encoding="utf-8")
            textfile_path = str(temp_title_file.resolve()).replace("\\", "/").replace(":", "\\:")
            drawtext = (
                f"drawtext=textfile='{textfile_path}':x=(w-text_w)/2:y=(h-text_h)/2:"
                f"font='Arial':fontsize={title_font_size}:fontcolor=white:borderw=2:bordercolor=black:"
                f"box=1:boxcolor=black@0.55:boxborderw=20:line_spacing=12:text_align=center"
            )
            filters.append(drawtext)

        vf_filter = ",".join(filters)

        if keep_video_audio:
            # Mix: keep original video audio at reduced volume + new audio
            if vf_filter:
                filter_complex = (
                    f"[0:v]{vf_filter}[vout];"
                    f"[0:a]volume={video_audio_volume_db}dB[vaud];"
                    f"[vaud][1:a]amix=inputs=2:duration=longest:dropout_transition=0[aout]"
                )
                maps = ["-map", "[vout]", "-map", "[aout]"]
            else:
                filter_complex = (
                    f"[0:a]volume={video_audio_volume_db}dB[vaud];"
                    f"[vaud][1:a]amix=inputs=2:duration=longest:dropout_transition=0"
                )
                maps = []
            cmd = [
                ffmpeg_bin,
                "-y" if force else "-n",
                "-hide_banner",
                "-loglevel", "error",
                "-stream_loop", str(loop_count),
                "-i", str(video_path),
                "-i", str(audio_path),
                "-filter_complex", filter_complex,
                *maps,
                "-c:v", "libx264",
                "-crf", str(crf),
                "-preset", "medium",
                "-c:a", "aac",
                "-b:a", "192k",
                "-t", f"{audio_duration:.4f}",
                "-movflags", "+faststart",
                str(output_path),
            ]
        else:
            # Replace: discard original video audio, use only the new audio
            if vf_filter:
                filter_complex = f"[0:v]{vf_filter}[vout]"
                maps = ["-map", "[vout]", "-map", "1:a:0"]
                cmd = [
                    ffmpeg_bin,
                    "-y" if force else "-n",
                    "-hide_banner",
                    "-loglevel", "error",
                    "-stream_loop", str(loop_count),
                    "-i", str(video_path),
                    "-i", str(audio_path),
                    "-filter_complex", filter_complex,
                    *maps,
                    "-c:v", "libx264",
                    "-crf", str(crf),
                    "-preset", "medium",
                    "-c:a", "aac",
                    "-b:a", "192k",
                    "-t", f"{audio_duration:.4f}",
                    "-movflags", "+faststart",
                    str(output_path),
                ]
            else:
                cmd = [
                    ffmpeg_bin,
                    "-y" if force else "-n",
                    "-hide_banner",
                    "-loglevel", "error",
                    "-stream_loop", str(loop_count),
                    "-i", str(video_path),
                    "-i", str(audio_path),
                    "-map", "0:v:0",
                    "-map", "1:a:0",
                    "-c:v", "libx264",
                    "-crf", str(crf),
                    "-preset", "medium",
                    "-c:a", "aac",
                    "-b:a", "192k",
                    "-t", f"{audio_duration:.4f}",
                    "-movflags", "+faststart",
                    str(output_path),
                ]

        print(f"Running ffmpeg (loop={loop_count}, duration={audio_duration:.1f}s)...")
        subprocess.run(cmd, check=True)
    finally:
        if temp_title_file:
            temp_title_file.unlink(missing_ok=True)


def main() -> int:
    args = build_parser().parse_args()

    audio_path = Path(args.audio).resolve()
    video_path = Path(args.video).resolve()

    if not audio_path.is_file():
        print(f"Error: audio file not found: {audio_path}", file=sys.stderr)
        return 2

    if not video_path.is_file():
        print(f"Error: video file not found: {video_path}", file=sys.stderr)
        return 2

    # Default output path
    if args.output:
        output_path = Path(args.output).resolve()
    else:
        output_path = VIDEOS_DIR / f"{audio_path.stem}.mp4"

    overlay_audio(
        audio_path=audio_path,
        video_path=video_path,
        output_path=output_path,
        keep_video_audio=args.keep_video_audio,
        video_audio_volume_db=args.video_audio_volume,
        crf=args.crf,
        force=args.force,
        title=args.title,
        title_font_size=args.title_font_size,
        crop_9_16=args.crop_9_16,
    )

    print(f"Audio       : {audio_path}")
    print(f"Video       : {video_path}")
    print(f"Keep v-audio: {args.keep_video_audio}")
    print(f"CRF         : {args.crf}")
    if args.title:
        print(f"Title       : {args.title}")
    print(f"Output      : {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
