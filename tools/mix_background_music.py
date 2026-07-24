#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Mix background music into a voice audio file.

The music is looped/trimmed to match the voice duration and mixed at a
low volume so it never overpowers the narration.

Usage:
    python3 tools/mix_background_music.py \
        --voice  audio/my-story.wav \
        --music  musics/hai_yu_ni_full.wav \
        --output expose/my-story.wav

    # Optional: adjust music volume (default -20 dB below voice)
    python3 tools/mix_background_music.py \
        --voice  audio/my-story.wav \
        --music  musics/hai_yu_ni_full.wav \
        --output expose/my-story.wav \
        --music-volume -20

    # Optional: fade-in / fade-out durations in seconds
    python3 tools/mix_background_music.py \
        --voice  audio/my-story.wav \
        --music  musics/hai_yu_ni_full.wav \
        --output expose/my-story.wav \
        --fade-in 3 --fade-out 5
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MUSICS_DIR = ROOT / "musics"
EXPOSE_DIR = ROOT / "expose"
AUDIO_EXTENSIONS = {".wav", ".mp3", ".m4a", ".flac", ".ogg", ".aac"}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Mix background music into a voice audio file at low volume.",
    )
    parser.add_argument(
        "--voice",
        required=True,
        help="Path to the main voice/narration audio file.",
    )
    parser.add_argument(
        "--music",
        required=True,
        help="Path to the background music file.",
    )
    parser.add_argument(
        "--output",
        help="Output path. Defaults to expose/<voice-basename>.",
    )
    parser.add_argument(
        "--music-volume",
        type=float,
        default=-20,
        help="Music volume adjustment in dB relative to the voice "
             "(negative = quieter). Default: -20 dB.",
    )
    parser.add_argument(
        "--fade-in",
        type=float,
        default=2.0,
        help="Music fade-in duration in seconds. Default: 2.",
    )
    parser.add_argument(
        "--fade-out",
        type=float,
        default=4.0,
        help="Music fade-out duration in seconds. Default: 4.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite output file if it exists.",
    )
    return parser


def get_duration_seconds(ffmpeg_bin: str, audio_path: Path) -> float:
    """Return the duration of an audio file in seconds via ffprobe."""
    ffprobe = shutil.which("ffprobe")
    if not ffprobe:
        raise RuntimeError("ffprobe not found. Install ffmpeg (includes ffprobe).")
    result = subprocess.run(
        [
            ffprobe,
            "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            str(audio_path),
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    return float(result.stdout.strip())


def list_music_files(musics_dir: Path) -> list[Path]:
    """List all audio files in the musics directory."""
    if not musics_dir.is_dir():
        return []
    files = sorted(
        p for p in musics_dir.iterdir()
        if p.is_file() and p.suffix.lower() in AUDIO_EXTENSIONS
    )
    return files


def mix_audio(
    voice_path: Path,
    music_path: Path,
    output_path: Path,
    music_volume_db: float,
    fade_in: float,
    fade_out: float,
    force: bool,
) -> None:
    """Mix voice and background music using ffmpeg.

    Strategy:
    1. Loop the music track to cover the full voice duration.
    2. Apply volume reduction to the music.
    3. Apply fade-in at the start and fade-out at the end of the music.
    4. Mix the two streams together.
    5. Output the mixed audio.
    """
    ffmpeg_bin = shutil.which("ffmpeg")
    if not ffmpeg_bin:
        raise RuntimeError("ffmpeg not found. Install ffmpeg before mixing audio.")

    if output_path.exists() and not force:
        raise FileExistsError(
            f"Output exists: {output_path}. Pass --force to overwrite."
        )

    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Get voice duration for the music fade-out calculation
    voice_duration = get_duration_seconds(ffmpeg_bin, voice_path)

    # Build the complex filter:
    # [0:a] = voice (pass through)
    # [1:a] = music -> loop to cover duration -> trim to voice length
    #       -> volume down -> fade in/out -> mix with voice
    fade_out_start = max(0, voice_duration - fade_out)

    # The music filter chain:
    # aloop: loop enough times to cover voice duration
    # atrim: cut to exact voice duration
    # volume: reduce music volume
    # afade: fade in at start, fade out at end
    music_filter = (
        f"[1:a]aloop=loop=-1:size=2e+09,"
        f"atrim=duration={voice_duration:.4f},"
        f"asetpts=PTS-STARTPTS,"
        f"volume={music_volume_db}dB,"
        f"afade=t=in:st=0:d={fade_in:.2f},"
        f"afade=t=out:st={fade_out_start:.4f}:d={fade_out:.2f}"
        f"[music];"
        f"[0:a][music]amix=inputs=2:duration=first:dropout_transition=0"
    )

    cmd = [
        ffmpeg_bin,
        "-y" if force else "-n",
        "-hide_banner",
        "-loglevel", "error",
        "-i", str(voice_path),
        "-i", str(music_path),
        "-filter_complex", music_filter,
        "-ac", "1",       # mono output (audiobook standard)
        "-ar", "24000",   # 24kHz sample rate (match VoxCPM output)
        str(output_path),
    ]
    subprocess.run(cmd, check=True)


def main() -> int:
    args = build_parser().parse_args()

    voice_path = Path(args.voice).resolve()
    music_path = Path(args.music).resolve()

    if not voice_path.is_file():
        print(f"Error: voice audio not found: {voice_path}", file=sys.stderr)
        return 2

    if not music_path.is_file():
        print(f"Error: music file not found: {music_path}", file=sys.stderr)
        return 2

    # Default output path
    if args.output:
        output_path = Path(args.output).resolve()
    else:
        output_path = EXPOSE_DIR / voice_path.name

    mix_audio(
        voice_path=voice_path,
        music_path=music_path,
        output_path=output_path,
        music_volume_db=args.music_volume,
        fade_in=args.fade_in,
        fade_out=args.fade_out,
        force=args.force,
    )

    print(f"Voice audio : {voice_path}")
    print(f"Music       : {music_path}")
    print(f"Music volume: {args.music_volume:+g} dB")
    print(f"Fade in/out : {args.fade_in}s / {args.fade_out}s")
    print(f"Output      : {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
