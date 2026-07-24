#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Helper module for cropping video and adding subtitles."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path

COLOR_MAP = {
    "yellow": "&H0000FFFF",
    "white": "&H00FFFFFF",
    "cyan": "&H00FFFF00",
}


def convert_seconds_to_srt_time(seconds: float) -> str:
    """Convert float seconds to SRT time format HH:MM:SS,mmm."""
    hrs = int(seconds // 3600)
    mins = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    msecs = int(round((seconds - int(seconds)) * 1000))
    if msecs == 1000:
        msecs = 0
        secs += 1
        if secs == 60:
            secs = 0
            mins += 1
            if mins == 60:
                mins = 0
                hrs += 1
    return f"{hrs:02d}:{mins:02d}:{secs:02d},{msecs:03d}"


def find_manifest_by_video_name(video_path: Path, search_dir: Path) -> Path | None:
    """Search search_dir recursively for the manifest JSON matching the video stem."""
    video_stem = video_path.stem
    # Handle matching variations (e.g. video file might have or not have suffixes)
    # Search for files matching *<stem>*_manifest.json
    matches = list(search_dir.rglob(f"*{video_stem}*_manifest.json"))
    if not matches:
        # Fallback: check if the stem has spaces/hyphens that need stripping, or match parts
        cleaned_stem = video_stem.replace("_9_16", "").replace("_vertical", "")
        matches = list(search_dir.rglob(f"*{cleaned_stem}*_manifest.json"))

    if not matches:
        return None

    # If multiple matches, return the most recently modified one
    matches.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return matches[0]


def generate_srt_from_manifest(manifest_path: Path, srt_path: Path) -> None:
    """Generate an SRT subtitle file from a VoxCPM manifest JSON."""
    with open(manifest_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if "chunks" not in data or "stitch" not in data:
        raise ValueError("Invalid manifest format: 'chunks' and 'stitch' fields are required.")

    chunks_by_id = {c["id"]: c for c in data["chunks"]}
    stitch_report = data["stitch"]

    srt_lines = []
    current_time = 0.0

    for idx, item in enumerate(stitch_report):
        chunk_id = item["id"]
        pause_ms = item["pause_ms"]
        trimmed_sec = item["trimmed_sec"]

        # Start time of this chunk
        start_time = current_time + (pause_ms / 1000.0)
        end_time = start_time + trimmed_sec

        chunk = chunks_by_id.get(chunk_id)
        if not chunk:
            current_time = end_time
            continue

        text = chunk["text"].strip()
        # Clean text: replace multiple spaces/newlines, join lines nicely
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        cleaned_text = " ".join(lines)

        # Break text into max two lines if too long (optional, but let's keep it clean)
        # For vertical videos, we want to wrap lines if they exceed ~40 characters
        wrapped_lines = []
        words = cleaned_text.split()
        current_line = []
        for word in words:
            current_line.append(word)
            if len(" ".join(current_line)) > 35:
                wrapped_lines.append(" ".join(current_line[:-1]))
                current_line = [word]
        if current_line:
            wrapped_lines.append(" ".join(current_line))
        
        display_text = "\n".join(wrapped_lines)

        start_str = convert_seconds_to_srt_time(start_time)
        end_str = convert_seconds_to_srt_time(end_time)

        srt_lines.append(f"{idx + 1}")
        srt_lines.append(f"{start_str} --> {end_str}")
        srt_lines.append(display_text)
        srt_lines.append("")  # Empty separator

        current_time = end_time

    with open(srt_path, "w", encoding="utf-8") as f:
        f.write("\n".join(srt_lines) + "\n")


def crop_and_burn_subtitles(
    input_path: Path,
    output_path: Path,
    srt_path: Path,
    font_size: int = 22,
    color: str = "yellow",
    alignment: int = 2,
    margin_v: int = 120,
    crf: int = 23,
    force: bool = True,
) -> None:
    # First check for keg-only ffmpeg-full from homebrew
    full_ffmpeg = Path("/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg")
    if full_ffmpeg.is_file():
        ffmpeg_bin = str(full_ffmpeg)
    else:
        ffmpeg_bin = shutil.which("ffmpeg")
    
    if not ffmpeg_bin:
        raise RuntimeError("ffmpeg not found. Please install ffmpeg.")

    if not input_path.is_file():
        raise FileNotFoundError(f"Input video not found: {input_path}")
    if not srt_path.is_file():
        raise FileNotFoundError(f"Subtitle file not found: {srt_path}")

    if output_path.exists() and not force:
        raise FileExistsError(f"Output file exists: {output_path}. Use force=True to overwrite.")

    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Get color code (defaulting to yellow)
    color_code = COLOR_MAP.get(color.lower(), COLOR_MAP["yellow"])

    # To avoid subtitle path escaping problems in ffmpeg's filters across platforms,
    # we run the ffmpeg subprocess with cwd set to the directory containing the SRT file,
    # and pass the relative SRT filename to the subtitles filter.
    srt_filename = srt_path.name
    cwd = srt_path.parent

    # Build the ffmpeg filter chain.
    # 1. Crop to 9:16 (centered): w=2*trunc(ih*9/32), h=ih
    # 2. Burn subtitles with styled look
    # Alignments: 2 = bottom-center, 10 = middle-center, 6 = top-center
    style = (
        f"FontName=Arial,FontSize={font_size},"
        f"PrimaryColour={color_code},OutlineColour=&H00000000,Outline=2,"
        f"MarginV={margin_v},Alignment={alignment}"
    )

    filter_complex = f"crop='2*trunc(ih*9/32):ih',subtitles=f={srt_filename}:force_style='{style}'"

    cmd = [
        ffmpeg_bin,
        "-y" if force else "-n",
        "-hide_banner",
        "-loglevel", "error",
        "-i", str(input_path.resolve()),
        "-vf", filter_complex,
        "-c:v", "libx264",
        "-crf", str(crf),
        "-preset", "medium",
        "-c:a", "copy",  # Copy the audio track directly (fast and lossless)
        str(output_path.resolve()),
    ]

    print(f"Running ffmpeg to crop 9:16 and burn subtitles...")
    print(f"Subtitles relative file: {srt_filename} (cwd: {cwd})")
    print(f"Output video: {output_path}")

    # Run ffmpeg with cwd set to the subtitle file's folder
    subprocess.run(cmd, cwd=str(cwd), check=True)


def crop_and_add_title(
    input_path: Path,
    output_path: Path,
    title: str,
    font_size: int = 36,
    color: str = "white",
    crf: int = 23,
    force: bool = True,
) -> None:
    """Crop video to 9:16 and overlay a static title in the center."""
    ffmpeg_bin = shutil.which("ffmpeg")
    # First check for keg-only ffmpeg-full from homebrew
    full_ffmpeg = Path("/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg")
    if full_ffmpeg.is_file():
        ffmpeg_bin = str(full_ffmpeg)
    
    if not ffmpeg_bin:
        raise RuntimeError("ffmpeg not found. Please install ffmpeg.")

    if not input_path.is_file():
        raise FileNotFoundError(f"Input video not found: {input_path}")

    if output_path.exists() and not force:
        raise FileExistsError(f"Output file exists: {output_path}. Use force=True to overwrite.")

    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Let's write the title to a temporary text file in the output directory
    # to avoid subtitle/text escaping problems in ffmpeg's filters
    temp_title_file = output_path.parent / f"{output_path.stem}_title_temp.txt"
    temp_title_file.write_text(title, encoding="utf-8")

    # In ffmpeg filters, we must escape colons and backslashes for the textfile path
    textfile_path = str(temp_title_file.resolve()).replace("\\", "/").replace(":", "\\:")

    # Build the drawtext filter
    # Centered: x=(w-text_w)/2, y=(h-text_h)/2
    # Semi-transparent box, outline border
    drawtext_filter = (
        f"drawtext=textfile='{textfile_path}':x=(w-text_w)/2:y=(h-text_h)/2:"
        f"font='Arial':fontsize={font_size}:fontcolor={color}:borderw=2:bordercolor=black:"
        f"box=1:boxcolor=black@0.4:boxborderw=20"
    )

    filter_complex = f"crop='2*trunc(ih*9/32):ih',{drawtext_filter}"

    cmd = [
        ffmpeg_bin,
        "-y" if force else "-n",
        "-hide_banner",
        "-loglevel", "error",
        "-i", str(input_path.resolve()),
        "-vf", filter_complex,
        "-c:v", "libx264",
        "-crf", str(crf),
        "-preset", "medium",
        "-c:a", "copy",  # Copy the audio track directly (fast and lossless)
        str(output_path.resolve()),
    ]

    print(f"Running ffmpeg to crop 9:16 and overlay static title...")
    print(f"Title: {title!r}")
    print(f"Output video: {output_path}")

    try:
        subprocess.run(cmd, check=True)
    finally:
        # Clean up the temporary title file
        temp_title_file.unlink(missing_ok=True)

