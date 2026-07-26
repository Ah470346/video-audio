#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Short-form expressive VoxCPM2 entrypoint.

Long-form rendering stays in convert_script_to_audio_voxcpm.py. This entrypoint
adds only short-script policy: @style parsing, short chunk defaults, and
VoxCPM2 control instructions for each short chunk.
"""

from __future__ import annotations

import argparse
import copy
import re
import sys
from pathlib import Path

import convert_script_to_audio_voxcpm as renderer


DEFAULT_CONTROL = (
    "expressive Vietnamese dramatic short-form narration, emotional emphasis, "
    "natural pauses, clear articulation"
)

SHORT_EXPRESSIVE_DEFAULT_ARGS = [
    "--clone_mode", "reference",
    "--max_chunk_chars", "80",
    "--max_chunk_words", "14",
    "--min_chunk_words", "3",
    "--cfg_value", "2.0",
    "--inference_timesteps", "16",
    "--retry_badcase_ratio_threshold", "8.0",
    "--stitch_cont_pause_ms", "120",
    "--stitch_sent_pause_ms", "260",
    "--stitch_para_pause_ms", "420",
    "--stitch_scene_pause_ms", "900",
    "--stitch_expressive_pause_ms", "620",
    "--verify_speaker_severity", "warn",
    "--max_verify_retries", "2",
]

STYLE_DIRECTIVE_RE = re.compile(r"^\s*@style(?:\s*:\s*|\s+)?(.*?)\s*$", re.IGNORECASE)
ACTIVE_DEFAULT_CONTROL = DEFAULT_CONTROL


def build_short_parser():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--control", default=DEFAULT_CONTROL)
    return parser


def normalize_style_control(value, default_control):
    style = (value or "").strip()
    if not style or style.lower() in {"default", "reset"}:
        return default_control
    if style.lower() in {"off", "none", "no", "false"}:
        return None
    return style


def parse_style_blocks(text, default_control):
    blocks = []
    current_control = default_control
    current_lines = []

    def flush():
        nonlocal current_lines
        body = "\n".join(current_lines).strip()
        if body:
            blocks.append({"text": body, "style_control": current_control})
        current_lines = []

    for line in text.splitlines():
        match = STYLE_DIRECTIVE_RE.match(line)
        if match:
            flush()
            current_control = normalize_style_control(match.group(1), default_control)
            continue
        current_lines.append(line)
    flush()
    return blocks


def _limited_blocks(blocks, story_word_limit):
    if story_word_limit is None or story_word_limit <= 0:
        total_words = 0
        rows = []
        for block in blocks:
            cleaned = renderer.clean_markdown(block["text"])
            if not cleaned:
                continue
            total_words += len(re.findall(r"\S+", cleaned))
            rows.append({**block, "text": cleaned})
        return rows, total_words

    remaining = story_word_limit
    total_words = 0
    rows = []
    for block in blocks:
        cleaned = renderer.clean_markdown(block["text"])
        if not cleaned:
            continue
        limited, count = renderer.limit_story_words(cleaned, remaining)
        if limited:
            rows.append({**block, "text": limited})
            total_words += count
        remaining -= count
        if remaining <= 0:
            break
    return rows, total_words


def prepare_chunks(args):
    raw = Path(args.input).read_text(encoding="utf-8")
    style_blocks = parse_style_blocks(raw, ACTIVE_DEFAULT_CONTROL)
    limited_blocks, word_count = _limited_blocks(style_blocks, args.story_word_limit)
    pron_dict = renderer.load_pron_dict(args.pron_dict)

    normalized_blocks = []
    rows = []
    for block in limited_blocks:
        normalized = renderer.normalize_for_tts(block["text"], pron_dict=pron_dict)
        if not normalized:
            continue
        planned = renderer.plan_chunks(
            normalized,
            args.max_chunk_chars,
            args.max_chunk_words,
            min_words=args.min_chunk_words,
        )
        renderer.assert_chunk_text_integrity(normalized, planned)
        normalized_blocks.append(normalized)
        for piece in planned:
            if rows and piece["sep_before"] == "start":
                piece = {**piece, "sep_before": "para"}
            rows.append({**piece, "style_control": block["style_control"]})

    if args.limit:
        rows = rows[: args.limit]
    chunks = [
        {
            "id": f"{index:04d}",
            "index": index,
            "text": row["text"],
            "style_control": row["style_control"],
            "sep_before": row["sep_before"],
            "chars": len(row["text"]),
            "words": len(row["text"].split()),
        }
        for index, row in enumerate(rows)
    ]
    return "\n\n".join(normalized_blocks), word_count, chunks


def render_chunk(
    model, chunk, args, ref_audio, ref_text, cfg_value=None, inference_timesteps=None, seed=None,
    prompt_cache=None,
):
    style_control = chunk.get("style_control")
    if not style_control:
        return ORIGINAL_RENDER_CHUNK(
            model, chunk, args, ref_audio, ref_text, cfg_value, inference_timesteps, seed,
            prompt_cache=prompt_cache,
        )
    styled_chunk = copy.copy(chunk)
    styled_chunk["text"] = f"({style_control}){chunk['text']}"
    return ORIGINAL_RENDER_CHUNK(
        model, styled_chunk, args, ref_audio, ref_text, cfg_value, inference_timesteps, seed,
        prompt_cache=prompt_cache,
    )


ORIGINAL_PREPARE_CHUNKS = renderer.prepare_chunks
ORIGINAL_RENDER_CHUNK = renderer.render_chunk


def main(argv=None):
    user_args = sys.argv[1:] if argv is None else list(argv)
    short_args, renderer_args = build_short_parser().parse_known_args(user_args)

    global ACTIVE_DEFAULT_CONTROL
    ACTIVE_DEFAULT_CONTROL = short_args.control
    renderer.prepare_chunks = prepare_chunks
    renderer.render_chunk = render_chunk
    try:
        # Force one worker: the long renderer uses multiprocessing spawn for
        # parallelism, and spawned workers would not inherit this short-only
        # render_chunk override.
        return renderer.main([
            *SHORT_EXPRESSIVE_DEFAULT_ARGS,
            *renderer_args,
            "--render_workers", "1",
            "--no-resume",
        ])
    finally:
        renderer.prepare_chunks = ORIGINAL_PREPARE_CHUNKS
        renderer.render_chunk = ORIGINAL_RENDER_CHUNK


if __name__ == "__main__":
    main()
