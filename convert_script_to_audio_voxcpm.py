# -*- coding: utf-8 -*-
"""Render a Vietnamese story Markdown to audio with VoxCPM2 (OpenBMB).

This is the only supported long-form TTS renderer in this repo. It combines
VoxCPM synthesis with the repo's Vietnamese text normalization, chunk planning,
boundary-aware stitching, ASR verification, speaker similarity checks, retry
recovery, resume state, and final mastering:

  - ASR-based verify: CER, word-similarity, dropped/repeated/inserted-word
    detection, timing anomalies (drag/swallow/tempo/confidence) via
    faster-whisper. VoxCPM ships NO equivalent (README: "No explicit built-in
    verification"), so this is the most load-bearing addition.
  - Speaker-similarity check against the reference clone (resemblyzer).
  - An escalation ladder: on verify failure, re-render with different
    cfg_value/inference_timesteps/seed, keep the best-scoring candidate across
    attempts (never regress to a worse later draw).
  - Sub-split recovery: a chunk that exhausts its retry ladder gets split into
    two smaller pieces, each independently rendered/verified/escalated, then
    stitched back into the parent chunk's slot.
  - Checkpoint/resume: a chunk whose text+params+wav all match the last run is
    skipped, so a crashed or interrupted long render picks back up for free.
  - Two-pass loudnorm mastering (-16 LUFS / -1.5 dBTP by default).
  - Reports: per-chunk verify results, a render-status rollup, and a
    verify-failures review folder (text + audio + defects) for chunks that
    never passed.

VoxCPM's long-form failure mode is voice drift because the reference conditions
only the start of a generation. This renderer handles that by splitting long
stories into short chunks and re-injecting the same reference audio into every
chunk before stitching.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
import os
import re
import shutil
import subprocess
import sys
import time
import traceback
from datetime import datetime, timezone
from difflib import SequenceMatcher
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from voxcpm_story_core import (  # noqa: E402
    DEFAULT_FAST_SWALLOW_DB,
    FasterWhisperSession,
    KNOWN_VOICE_REFTEXT,
    _decode_samples,
    _normalize_for_compare,
    cer_from_words,
    clean_markdown,
    ensure_terminal_punctuation,
    faster_whisper_available,
    normalize_for_tts,
    plan_chunks,
    timing_defects_from_words,
    token_diff_evidence,
    transcribe_word_timestamps,
)
from voxcpm_ctc_probe import DEFAULT_CTC_MODEL, CtcProbeSession, normalize_for_ctc


# ---------------------------------------------------------------------------
# Upstream guidance this script encodes (kept in one place so the defaults are
# auditable against the source that justified them).
# ---------------------------------------------------------------------------
VOXCPM_GUIDANCE = {
    "chunking_is_the_supported_long_form_path": (
        "VoxCPM.generate() has no internal splitter and `voxcpm batch` treats "
        "each input line as an independent generation. Maintainer a710128 in "
        "issues #281 and #222: splitting long text into shorter chunks and "
        "generating them separately is the recommended way to handle long-form."
    ),
    "max_chars": (
        "PR #313 (`generate_long_form`) ships max_chars=55 as the function "
        "default and 120 in the CLI/README examples; the in-repo CosyVoice "
        "splitter (utils/text_normalize.split_paragraph) uses "
        "token_max_n=80 / token_min_n=60 / merge_len=20."
    ),
    "cfg_value": (
        "Issue #222, maintainer: lowering CFG (e.g. 1.5) improves stability and "
        "reduces artifacts in longer generations; raising inference_timesteps "
        "10->20 does not help the degradation."
    ),
    "re_anchor_every_chunk": (
        "Issue #302: prompt/reference conditioning acts only as an INITIAL "
        "anchor, so a long single-pass generation drifts onto its own latents. "
        "Documented workaround: split, re-inject the same prompt/reference "
        "audio for every segment, concatenate."
    ),
    "ultimate_cloning_for_consistency": (
        "Issue #281, maintainer: for stable voice across chunks use a longer "
        "reference audio and the high-fidelity (prompt_wav + prompt_text) "
        "cloning mode. Counter-evidence in #216: prompt-mode can leak the "
        "reference's last syllables into the output, hence --clone_mode."
    ),
    "no_builtin_normalizer_for_vietnamese": (
        "voxcpm.utils.text_normalize.TextNormalizer selects lang='zh' when the "
        "text has Han characters and 'en' otherwise. Vietnamese therefore falls "
        "into the ENGLISH branch (wetext en + inflect), which would spell "
        "numbers as English words. We always pass normalize=False and run the "
        "Vietnamese normalizer instead."
    ),
    "retry_badcase": (
        "generate() defaults retry_badcase=True with "
        "retry_badcase_ratio_threshold=6.0 (audio-duration / text-length). It "
        "is VoxCPM's own only built-in QC and it catches the grossest form of "
        "the Vietnamese EOS-failure gibberish tail reported in issue #352 -- "
        "the ASR-based verify below is what catches the rest."
    ),
    "no_builtin_verify": (
        "README: 'No explicit built-in verification' for text-accuracy/"
        "repetition/omission. verify_chunk() adds ASR-based CER/similarity/"
        "timing/repetition checks, which are pure text-vs-audio comparisons."
    ),
    "escalation_ladder": (
        "Re-render failed chunks with different synthesis params and keep the "
        "best-scoring candidate across attempts, using VoxCPM's own knobs: cfg_value and "
        "inference_timesteps per #222, plus a fresh seed every attempt since "
        "VoxCPM's diffusion-autoregressive decoder is stochastic per draw. "
        "Text-lock failures (repetition/insertions) retry with higher CFG and "
        "smaller subsplits before falling back to softer CFG."
    ),
    "subsplit_recovery": (
        "A chunk that exhausts its ladder is usually failing on specific "
        "content (a proper noun, a hard consonant cluster), not on an engine "
        "bug -- shrinking it and retrying each half independently is a "
        "content-agnostic recovery, unlike the click/edge-fade repairs this "
        "port deliberately drops."
    ),
    "resume": (
        "Checkpoint/resume (chunk text+params+wav hash match -> skip) is "
        "ordinary long-render engineering: chunk text+params+wav hash match -> skip."
    ),
}

DEFAULT_VOICE_NAME = "NGOC HUYEN V2"
DEFAULT_REF_AUDIO = "voice_samples/ngoc_huyen_moi_ref_clone_tu_nhien.wav"
DEFAULT_MODEL = "openbmb/VoxCPM2"
DEFAULT_ASR_MODEL = "large-v3-turbo"

# Boundary -> pause length. These values encode Vietnamese narration rhythm;
# VoxCPM PR #313 independently landed on 180-300 ms for flat inter-segment
# silence, which brackets the sentence/paragraph values here.
DEFAULT_PAUSE_MS = {
    "start": 0,
    "cont": 80,
    "sent": 190,
    "para": 300,
    "scene": 800,
}
EXPRESSIVE_PAUSE_MS = 460

# Escalation ladder for verify-failed chunks. Attempt 0 is always the plain
# --cfg_value/--inference_timesteps args; attempts 1+ cycle through this list.
# See VOXCPM_GUIDANCE["escalation_ladder"].
VOXCPM_RETRY_LADDER = [
    {"cfg_value": 1.6, "inference_timesteps": 14, "reason": "balanced_retry"},
    {"cfg_value": 2.0, "inference_timesteps": 16, "reason": "text_lock"},
    {"cfg_value": 1.2, "inference_timesteps": 10, "reason": "artifact_soften"},
]

TEXT_LOCK_RETRY_LADDER = [
    {"cfg_value": 2.0, "inference_timesteps": 16, "reason": "text_lock_first"},
    {"cfg_value": 1.6, "inference_timesteps": 14, "reason": "balanced_retry"},
    {"cfg_value": 1.2, "inference_timesteps": 10, "reason": "artifact_soften"},
]


def build_parser():
    parser = argparse.ArgumentParser(
        description="Render a Vietnamese story Markdown to audio with VoxCPM2."
    )
    parser.add_argument("--input", "-i", required=True, help="Input Markdown file")
    parser.add_argument("--output_dir", "-o", default="results", help="Output directory")
    parser.add_argument("--model", default=DEFAULT_MODEL, help="HF repo id or local model dir")
    parser.add_argument("--voice_name", default=DEFAULT_VOICE_NAME, help="Clone profile label")
    parser.add_argument("--ref_audio", default=DEFAULT_REF_AUDIO, help="Reference WAV for cloning")
    parser.add_argument(
        "--ref_text",
        default=None,
        help="Exact transcript of --ref_audio. Required by --clone_mode ultimate; "
        "falls back to the KNOWN_VOICE_REFTEXT entry for --voice_name.",
    )
    parser.add_argument(
        "--clone_mode",
        choices=("ultimate", "reference"),
        default="ultimate",
        help="ultimate = prompt_wav + prompt_text + reference_wav (README: maximum "
        "cloning similarity; issue #281: best cross-chunk voice consistency). "
        "reference = reference_wav only, which avoids the prompt-tail leakage of "
        "issue #216 at the cost of similarity.",
    )
    # --- chunk planning (VoxCPM long-form sizing) ---
    parser.add_argument(
        "--max_chunk_chars",
        type=int,
        default=120,
        help="Upper bound per chunk. Default 120 matches the VoxCPM long-form "
        "CLI example and keeps Vietnamese chunks stable in one pass.",
    )
    parser.add_argument("--max_chunk_words", type=int, default=26)
    parser.add_argument(
        "--min_chunk_words",
        type=int,
        default=8,
        help="Merge chunks shorter than this into a neighbour, mirroring "
        "split_paragraph(merge_len=...) upstream. Isolated one-line chunks are "
        "also where issue #357 reports hallucination on short utterances.",
    )
    parser.add_argument(
        "--story_word_limit",
        type=int,
        default=None,
        help="Render only the first N words (smoke runs). Completes the sentence.",
    )
    parser.add_argument("--limit", type=int, default=None, help="Render only the first N chunks")
    parser.add_argument("--pron_dict", default=None, help="JSON pronunciation override dictionary")
    parser.add_argument(
        "--dry_run",
        action="store_true",
        help="Plan and write chunk text + manifest, load no model, render nothing.",
    )

    # --- VoxCPM synthesis ---
    parser.add_argument(
        "--cfg_value",
        type=float,
        default=1.5,
        help="Guidance scale. Default 1.5 rather than the library's 2.0 per the "
        "maintainer's long-generation stability advice in issue #222.",
    )
    parser.add_argument(
        "--inference_timesteps",
        type=int,
        default=10,
        help="CFM steps. Left at the library default: issue #222 reports 10->20 "
        "does not fix long-sequence degradation, it only costs time.",
    )
    parser.add_argument("--seed", type=int, default=20260719, help="Base seed for chunk 0, attempt 0")
    parser.add_argument("--min_len", type=int, default=2)
    parser.add_argument("--max_len", type=int, default=4096)
    parser.add_argument(
        "--retry_badcase",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="VoxCPM's built-in audio/text duration-ratio retry.",
    )
    parser.add_argument("--retry_badcase_max_times", type=int, default=3)
    parser.add_argument("--retry_badcase_ratio_threshold", type=float, default=6.0)
    parser.add_argument(
        "--denoise",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="Run ZipEnhancer over the reference audio. Off: our references are "
        "already clean and the denoiser pulls a ModelScope download.",
    )
    parser.add_argument(
        "--optimize",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="torch.compile the model. Off by default: the compile pass is a "
        "large extra failure surface on a Kaggle T4 for a smoke run.",
    )
    parser.add_argument("--device", default=None, help="cuda / cuda:0 / cpu / mps; None = auto")
    parser.add_argument(
        "--render_workers",
        default="auto",
        help="Parallel chunk render workers. 'auto' uses every visible CUDA GPU; 1 disables parallel render.",
    )
    parser.add_argument(
        "--render_devices",
        default=None,
        help="Comma-separated CUDA device indexes for parallel chunk render, e.g. 0,1. Defaults to all visible GPUs.",
    )
    parser.add_argument(
        "--local_files_only",
        action="store_true",
        help="Do not hit the network when resolving --model.",
    )

    # --- resume / checkpoint ---
    parser.add_argument(
        "--resume",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Skip chunks whose text+params+wav hash all match chunk_state.json.",
    )
    parser.add_argument(
        "--rerender_on_param_change",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Treat a synthesis-param change (cfg/steps/model/voice/...) as "
        "invalidating a chunk's resume eligibility even if its wav is present.",
    )

    # --- verify (ASR CER/similarity/timing + speaker + repetition) ---
    parser.add_argument(
        "--verify_chunks",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Master switch for verify+escalation+subsplit. Off = one render "
        "attempt per chunk, like step 1.",
    )
    parser.add_argument(
        "--verify_asr",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Use faster-whisper word timestamps for text/timing verification.",
    )
    parser.add_argument("--verify_asr_model", default=DEFAULT_ASR_MODEL)
    parser.add_argument("--verify_sample_rate", type=int, default=16000)
    parser.add_argument("--verify_clip_peak", type=float, default=0.98)
    parser.add_argument("--verify_silence_threshold_db", type=float, default=-45.0)
    parser.add_argument("--verify_max_internal_silence_sec", type=float, default=1.8)
    parser.add_argument(
        "--verify_min_wps",
        type=float,
        default=1.5,
        help="Below this words/sec, flag as a hard defect (dragged/truncated read).",
    )
    parser.add_argument(
        "--verify_max_wps",
        type=float,
        default=8.0,
        help="Above this words/sec, flag as a hard defect (rushed/truncated read).",
    )
    parser.add_argument("--verify_similarity_floor", type=float, default=0.94)
    parser.add_argument("--verify_adaptive_floor", type=float, default=0.985)
    parser.add_argument(
        "--verify_similarity_severity",
        choices=["hard", "warn", "off"],
        default="warn",
        help="Severity for the whole-chunk word-similarity-ratio defect. 'warn' "
        "keeps it non-blocking: Vietnamese ASR transcription noise alone can "
        "push this below floor on chunks confirmed correct by ear.",
    )
    parser.add_argument("--verify_max_cer", type=float, default=0.12)
    parser.add_argument("--verify_cer_warn", type=float, default=0.06)
    parser.add_argument(
        "--verify_cer_severity",
        choices=["hard", "warn", "off"],
        default="warn",
        help="CER starts in measure-first warn mode until calibrated on real VoxCPM runs.",
    )
    parser.add_argument(
        "--verify_single_word_severity",
        choices=["hard", "warn", "off"],
        default="hard",
        help="Gate one acoustically absent expected word (Vietnamese words are "
        "syllable-separated, so a one-token deletion must not hide behind a "
        "two-word span threshold).",
    )
    parser.add_argument("--verify_word_probability_floor", type=float, default=0.78)
    parser.add_argument("--verify_word_duration_ratio", type=float, default=2.4)
    parser.add_argument("--verify_min_local_wps", type=float, default=1.6)
    parser.add_argument("--verify_max_local_wps", type=float, default=9.0)
    parser.add_argument("--verify_dropped_words", type=int, default=4)
    parser.add_argument("--verify_drag_ratio", type=float, default=6.0)
    parser.add_argument("--verify_swallow_db", type=float, default=DEFAULT_FAST_SWALLOW_DB)
    parser.add_argument(
        "--verify_ctc_probe",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Read the chunk again with a language-model-free Vietnamese CTC "
        "acoustic model, to catch audio Whisper's decoder normalises away.",
    )
    parser.add_argument("--verify_ctc_model", default=DEFAULT_CTC_MODEL)
    parser.add_argument(
        "--verify_ctc_out_of_text_ms",
        type=int,
        default=120,
        help="Grace after the last (and before the first) aligned word before "
        "CTC-decoded audio counts as out-of-text junk.",
    )
    parser.add_argument(
        "--verify_ctc_out_of_text_chars",
        type=int,
        default=2,
        help="Minimum CTC-decoded characters outside the sentence to hard-fail.",
    )
    parser.add_argument(
        "--verify_ctc_veto_similarity",
        type=float,
        default=0.98,
        help="Context-free CTC word similarity above which a timing/energy "
        "heuristic is treated as a false positive and downgraded to a warning.",
    )
    parser.add_argument(
        "--verify_ctc_single_word_support_similarity",
        type=float,
        default=0.90,
        help="Minimum context-free CTC word similarity required before CTC may "
        "independently confirm a word that Whisper reported as missing.",
    )
    parser.add_argument(
        "--verify_ctc_min_word_score",
        type=float,
        default=0.15,
        help="Fail a chunk when its worst force-aligned word has a mean CTC "
        "posterior below this floor. A localized garble -- one or two syllables "
        "rendered as babble -- barely moves whole-chunk CER or word similarity "
        "(they average the error over every word), but it drives that one "
        "word's acoustic score to ~0. On the 96-chunk "
        "`bo-me-toi-gui-yeu-cau-hoan-tien-tap-1` run the two garbled chunks "
        "scored 0.024/0.031 while every clean chunk stayed >=0.34, so this is "
        "the signal that catches the dilution the aggregate floors miss.",
    )
    parser.add_argument(
        "--verify_ctc_min_word_score_severity",
        choices=["hard", "warn", "off"],
        default="hard",
        help="Severity for the min-word-score floor. `hard` triggers the "
        "render retry ladder (and subsplit) so the garbled chunk is re-rendered.",
    )
    parser.add_argument(
        "--verify_inserted_words",
        type=int,
        default=3,
        help="Minimum inserted-word run to hard-fail. This is what catches "
        "VoxCPM's EOS-failure gibberish tail (issue #352).",
    )
    parser.add_argument("--verify_repeat_max_ngram", type=int, default=4)
    parser.add_argument(
        "--verify_repeat_severity",
        choices=["hard", "warn", "off"],
        default="hard",
        help="Severity for ASR-heard repeated phrases not present in the expected text.",
    )
    parser.add_argument(
        "--verify_speaker_severity",
        choices=["hard", "warn", "off"],
        default="warn",
        help="Severity for speaker-similarity drift against --ref_audio.",
    )
    parser.add_argument("--verify_speaker_warn", type=float, default=0.80)
    parser.add_argument("--verify_speaker_hard", type=float, default=0.70)

    # --- escalation / recovery ---
    parser.add_argument(
        "--max_verify_retries",
        type=int,
        default=2,
        help="Extra render attempts (beyond attempt 0) per chunk via VOXCPM_RETRY_LADDER.",
    )
    parser.add_argument(
        "--verify_subsplit",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Split a chunk that exhausts its retry ladder into two pieces and "
        "recurse (each piece gets its own bounded ladder).",
    )

    # --- mastering ---
    parser.add_argument(
        "--master",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Two-pass ffmpeg loudnorm on the stitched final wav.",
    )
    parser.add_argument("--master_target_lufs", type=float, default=-16.0)
    parser.add_argument("--master_true_peak", type=float, default=-1.5)
    parser.add_argument("--master_lra", type=float, default=11.0)
    parser.add_argument(
        "--keep_premaster",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="Keep the pre-mastering stitched wav alongside the final one.",
    )

    # --- stitching ---
    parser.add_argument("--stitch_cont_pause_ms", type=int, default=DEFAULT_PAUSE_MS["cont"])
    parser.add_argument("--stitch_sent_pause_ms", type=int, default=DEFAULT_PAUSE_MS["sent"])
    parser.add_argument("--stitch_para_pause_ms", type=int, default=DEFAULT_PAUSE_MS["para"])
    parser.add_argument("--stitch_scene_pause_ms", type=int, default=DEFAULT_PAUSE_MS["scene"])
    parser.add_argument("--stitch_expressive_pause_ms", type=int, default=EXPRESSIVE_PAUSE_MS)
    parser.add_argument(
        "--stitch_edge_keep_ms",
        type=int,
        default=30,
        help="Silence left at a chunk edge after trimming, so pauses are exactly "
        "the planned length instead of the planned length plus whatever "
        "silence the model happened to emit.",
    )
    parser.add_argument("--stitch_silence_threshold_db_trim", type=float, default=-45.0)
    parser.add_argument(
        "--keep_chunks",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Keep per-chunk WAVs. Required for --resume and for re-stitching "
        "without a GPU.",
    )
    return parser


# ---------------------------------------------------------------------------
# Text preparation
# ---------------------------------------------------------------------------
def limit_story_words(text, max_words):
    """Cut to ``max_words`` but finish the sentence word N lands in.

    A smoke limit must not invent a sentence fragment that never existed in the
    source; the manifest records the real rendered count so the overrun stays
    explicit.
    """
    if max_words is None or max_words <= 0:
        return text, len(re.findall(r"\S+", text))
    matches = list(re.finditer(r"\S+", text))
    if len(matches) <= max_words:
        return text, len(matches)
    end = matches[max_words - 1].end()
    head = text[:end].rstrip()
    if head.endswith((".", "!", "?", "…", '"', "”", "’")):
        completed = head
    else:
        sentence_end = re.search(r'[.!?…](?:["”’\']+)?(?=\s|$)', text[end:])
        completed_end = end + sentence_end.end() if sentence_end else len(text)
        completed = text[:completed_end].rstrip()
    return completed, len(re.findall(r"\S+", completed))


def assert_chunk_text_integrity(text, chunks):
    """Fail before synthesis if chunk planning lost or reordered source tokens."""
    def tokens(value):
        return re.findall(r"[\wÀ-ỹ]+", value, flags=re.UNICODE)

    expected = tokens(text)
    planned = tokens(" ".join(chunk["text"] for chunk in chunks))
    if planned != expected:
        raise RuntimeError(
            "chunk planner changed normalized source tokens; refusing to render "
            f"({len(expected)} source vs {len(planned)} planned)"
        )


def load_pron_dict(path):
    if not path:
        return None
    return json.loads(Path(path).read_text(encoding="utf-8"))


def prepare_chunks(args):
    raw = Path(args.input).read_text(encoding="utf-8")
    cleaned = clean_markdown(raw)
    limited, word_count = limit_story_words(cleaned, args.story_word_limit)
    normalized = normalize_for_tts(limited, pron_dict=load_pron_dict(args.pron_dict))
    planned = plan_chunks(
        normalized,
        args.max_chunk_chars,
        args.max_chunk_words,
        min_words=args.min_chunk_words,
    )
    assert_chunk_text_integrity(normalized, planned)
    if args.limit:
        planned = planned[: args.limit]
    chunks = [
        {
            "id": f"{index:04d}",
            "index": index,
            "text": chunk["text"],
            "sep_before": chunk["sep_before"],
            "chars": len(chunk["text"]),
            "words": len(chunk["text"].split()),
        }
        for index, chunk in enumerate(planned)
    ]
    return normalized, word_count, chunks


def subsplit_chunk(chunk, args, aggressive=False):
    """Split one failing chunk into 2+ smaller pieces for independent retry.

    See VOXCPM_GUIDANCE["subsplit_recovery"]. Prefer plan_chunks at half the
    size caps, then fall back to a raw word-count midpoint split when the chunk
    is already a single unsplittable sentence.
    """
    if aggressive:
        char_cap = max(40, args.max_chunk_chars // 3)
        word_cap = max(4, args.max_chunk_words // 3)
    else:
        char_cap = max(60, args.max_chunk_chars // 2)
        word_cap = max(6, args.max_chunk_words // 2)
    pieces = plan_chunks(chunk["text"], char_cap, word_cap, min_words=0)
    if len(pieces) <= 1:
        words = chunk["text"].split()
        if len(words) < 4:
            return []
        midpoint = len(words) // 2
        pieces = [
            {"text": ensure_terminal_punctuation(" ".join(words[:midpoint])), "sep_before": "start"},
            {"text": ensure_terminal_punctuation(" ".join(words[midpoint:])), "sep_before": "cont"},
        ]
    rows = []
    for index, piece in enumerate(pieces):
        rows.append(
            {
                "id": f"{chunk['id']}__s{index + 1}",
                "index": chunk["index"],
                "text": piece["text"],
                "sep_before": "start" if index == 0 else "cont",
                "chars": len(piece["text"]),
                "words": len(piece["text"].split()),
            }
        )
    return rows


def target_pause_ms(prev_chunk, next_chunk, args):
    """Pause length for the boundary that runs INTO ``next_chunk``."""
    if prev_chunk is None:
        return 0
    sep = next_chunk.get("sep_before", "sent")
    if sep == "start":
        return 0
    if sep == "scene":
        return args.stitch_scene_pause_ms
    if sep == "cont":
        return args.stitch_cont_pause_ms
    # An expressive terminal earns more air than a flat full stop, but only when
    # the boundary is a real sentence/paragraph break -- never mid-sentence.
    tail = prev_chunk["text"].rstrip().rstrip('"”’\'')
    if tail.endswith(("?", "!", "…")):
        return args.stitch_expressive_pause_ms
    if sep == "para":
        return args.stitch_para_pause_ms
    return args.stitch_sent_pause_ms


# ---------------------------------------------------------------------------
# Audio helpers (numpy in-process; no ffmpeg concat, so the pcm format of every
# joined buffer is identical by construction and cannot be doubled by joining
# mismatched sample formats via `ffmpeg concat -c copy`)
# ---------------------------------------------------------------------------
def trim_edges(wav, sample_rate, threshold_db, keep_ms):
    """Trim leading/trailing silence down to exactly ``keep_ms``."""
    import numpy as np

    if wav.size == 0:
        return wav
    threshold = 10.0 ** (threshold_db / 20.0)
    loud = np.nonzero(np.abs(wav) > threshold)[0]
    if loud.size == 0:
        return wav
    keep = max(0, int(sample_rate * keep_ms / 1000.0))
    start = max(0, int(loud[0]) - keep)
    end = min(wav.size, int(loud[-1]) + 1 + keep)
    return wav[start:end]


def stitch(chunks, wavs, sample_rate, args):
    import numpy as np

    pieces = []
    report = []
    prev = None
    for chunk, wav in zip(chunks, wavs):
        trimmed = trim_edges(
            wav, sample_rate, args.stitch_silence_threshold_db_trim, args.stitch_edge_keep_ms
        )
        pause_ms = target_pause_ms(prev, chunk, args)
        if pause_ms > 0:
            pieces.append(np.zeros(int(sample_rate * pause_ms / 1000.0), dtype=np.float32))
        pieces.append(trimmed.astype(np.float32, copy=False))
        report.append(
            {
                "id": chunk["id"],
                "sep_before": chunk["sep_before"],
                "pause_ms": pause_ms,
                "raw_sec": round(wav.size / sample_rate, 4),
                "trimmed_sec": round(trimmed.size / sample_rate, 4),
            }
        )
        prev = chunk
    return np.concatenate(pieces) if pieces else np.zeros(0, dtype=np.float32), report


# ---------------------------------------------------------------------------
# QC primitives local to the VoxCPM renderer.
# ---------------------------------------------------------------------------
def add_defect(result, kind, severity, message, payload=None):
    defect = {"type": kind, "severity": severity, "message": message}
    if payload:
        defect["payload"] = payload
    result["defects"].append(defect)
    if severity == "hard":
        result["status"] = "fail"


def longest_silence_seconds(samples, sample_rate, threshold_db):
    threshold = 10 ** (threshold_db / 20.0)
    longest = 0
    current = 0
    for sample in samples:
        if abs(float(sample)) <= threshold:
            current += 1
            longest = max(longest, current)
        else:
            current = 0
    return longest / float(sample_rate)


# ---------------------------------------------------------------------------
# Context-free CTC probe
#
# Whisper decodes with a language model, so a locally distorted word is
# repaired from sentence context and the transcript looks clean. Everything
# below reads the same audio with a Vietnamese wav2vec2 CTC model, which is
# frame-synchronous and has no LM, and therefore reports what is acoustically
# present. Measured on the 80-chunk `anh-ky-don-ly-hon` render:
#
#   0038  tail junk `neo lua mũ n hốt` after the last word -> caught here,
#         and it is the only chunk of 80 with out-of-text audio (no false
#         positives on the other 79).
#   0071  QC hard-failed `swallowed 'khi'` on a timing/energy heuristic while
#         the CTC read is exact -> vetoed here.
#   0043  reported as `Tôi tôi muốn nói`; the CTC read is `còn` with posterior
#         0.994, and scoring the minimal pair over that window gives
#         logP(tôi) - logP(còn) = -26 nats. The audio is correct. The real
#         cause is script-level: chunks 0041/0042/0043 all open with
#         `Tôi muốn nói,`, which reads as a stutter when heard back to back.
#         No acoustic QC can catch that, because nothing is wrong with the
#         acoustics; it is caught during drafting/polish instead (see
#         audio-story-engagement and audio-story-final-polish).
# ---------------------------------------------------------------------------
def canonicalize_ctc_spoken_number_variants(text):
    """Canonicalize safe Vietnamese number variants for acoustic comparison.

    After ``mươi``, ``mốt/lăm/tư`` and ``một/năm/bốn`` are normal spoken
    alternatives.  Mapping both the expected sentence and the context-free CTC
    transcript to the same forms prevents forced alignment from assigning a
    near-zero score to a correctly spoken numeric variant.
    """
    tokens = str(text or "").split()
    replacements = {"một": "mốt", "năm": "lăm", "bốn": "tư"}
    for index in range(1, len(tokens)):
        if tokens[index - 1] == "mươi":
            tokens[index] = replacements.get(tokens[index], tokens[index])
    return " ".join(tokens)


def ctc_supports_missing_span(diff_evidence, ctc_metrics, minimum_similarity=0.90):
    """Whether independent CTC evidence contains Whisper's missing span."""
    if not ctc_metrics.get("available"):
        return False
    similarity = ctc_metrics.get("ctc_similarity")
    if not isinstance(similarity, (int, float)) or similarity < minimum_similarity:
        return False

    missing = canonicalize_ctc_spoken_number_variants(
        normalize_for_ctc(diff_evidence.get("longest_missing_text", ""))
    ).split()
    heard = canonicalize_ctc_spoken_number_variants(
        normalize_for_ctc(ctc_metrics.get("ctc_text", ""))
    ).split()
    if not missing:
        return False
    width = len(missing)
    return any(heard[index:index + width] == missing for index in range(len(heard) - width + 1))


def ctc_probe_metrics(chunk_text, wav_path, args, ctc_probe):
    """Measure a chunk with the CTC acoustic model.

    Returns ``(metrics, defects)``. ``metrics['veto']`` is True when the
    context-free read matches the expected text closely enough that a
    timing/energy anomaly should be treated as a heuristic false positive.
    """
    if not args.verify_ctc_probe:
        return {"enabled": False}, []
    if ctc_probe is None or not ctc_probe.load():
        error = ctc_probe.error if ctc_probe is not None else "probe not constructed"
        return (
            {"enabled": True, "available": False, "error": error},
            [("ctc_probe", "warn", f"CTC probe unavailable: {error}", {})],
        )

    expected = canonicalize_ctc_spoken_number_variants(normalize_for_ctc(chunk_text))
    emissions = ctc_probe.emissions(wav_path)
    if emissions is None:
        return (
            {"enabled": True, "available": False, "error": ctc_probe.error},
            [("ctc_probe", "warn", f"CTC probe failed: {ctc_probe.error}", {})],
        )

    heard_raw = ctc_probe.greedy_text(emissions)
    heard = canonicalize_ctc_spoken_number_variants(normalize_for_ctc(heard_raw))
    similarity = SequenceMatcher(None, expected.split(), heard.split()).ratio()
    metrics = {
        "enabled": True,
        "available": True,
        "ctc_text": heard_raw,
        "ctc_compare_text": heard,
        "ctc_similarity": round(similarity, 4),
        "veto": similarity >= args.verify_ctc_veto_similarity,
    }

    aligned = ctc_probe.align(emissions, expected)
    if not aligned:
        metrics["aligned"] = False
        return metrics, []
    metrics["aligned"] = True
    worst_word = min(aligned, key=lambda row: row["score"])
    metrics["min_word_score"] = worst_word["score"]
    metrics["min_word"] = {
        "word": worst_word["word"],
        "start": worst_word["start"],
        "end": worst_word["end"],
        "score": worst_word["score"],
    }

    grace = max(0, int(round(args.verify_ctc_out_of_text_ms / 1000.0 * ctc_probe.frames_per_sec)))
    head = ctc_probe.greedy_text(emissions, 0, max(0, aligned[0]["start_frame"] - grace))
    tail = ctc_probe.greedy_text(emissions, aligned[-1]["end_frame"] + grace, None)
    metrics["out_of_text"] = {"head": head, "tail": tail}

    defects = []
    # A near-zero worst-word posterior is the localized-garble signal that whole
    # chunk CER / word similarity dilute away: on `bo-me-toi...tap-1`, chunks
    # 0002 (`tôi nghe` -> babble) and 0082 (`kê` -> `cây`) scored 0.024/0.031
    # here yet passed every aggregate floor as a mere warning, so both shipped
    # without a re-render. This gate escalates them to a real failure.
    min_word_severity = getattr(args, "verify_ctc_min_word_score_severity", "hard")
    min_word_floor = getattr(args, "verify_ctc_min_word_score", 0.15)
    if min_word_severity != "off" and worst_word["score"] < min_word_floor:
        defects.append(
            (
                "ctc_min_word_score",
                min_word_severity,
                f"CTC word {worst_word['word']!r} at "
                f"{worst_word['start']:.2f}-{worst_word['end']:.2f}s scored "
                f"{worst_word['score']:.3f} < {min_word_floor:.3f} "
                f"(near-zero acoustic support; this word's audio is garbled)",
                dict(metrics["min_word"]),
            )
        )
    for position, text in (("head", head), ("tail", tail)):
        if len(text.replace(" ", "")) >= args.verify_ctc_out_of_text_chars:
            defects.append(
                (
                    "ctc_out_of_text_audio",
                    "hard",
                    f"CTC decoded {text!r} in the {position} outside the sentence",
                    {
                        "position": position,
                        "text": text,
                        "boundary_sec": (
                            aligned[0]["start"] if position == "head" else aligned[-1]["end"]
                        ),
                    },
                )
            )
    return metrics, defects




def duplicate_text_defect(expected_text, words, args):
    """Detect ASR-heard repeated phrases or inserted extra words.

    This is what catches VoxCPM's EOS-failure gibberish tail (issue #352): the
    model keeps generating past the end of the intended text, so the ASR
    transcript has a run of words with no match in ``expected_text``.
    """
    expected = _normalize_for_compare(expected_text).split()
    heard = _normalize_for_compare(" ".join(word.get("word", "") for word in words)).split()
    if not heard:
        return None

    repeated_phrase = None
    for ngram_size in range(args.verify_repeat_max_ngram, 0, -1):
        if len(heard) < ngram_size * 2:
            continue
        for index in range(len(heard) - ngram_size * 2 + 1):
            left = heard[index:index + ngram_size]
            right = heard[index + ngram_size:index + ngram_size * 2]
            if left == right:
                phrase = " ".join(left)
                expected_joined = " ".join(expected)
                doubled = f"{phrase} {phrase}"
                if doubled not in expected_joined:
                    repeated_phrase = f"repeated phrase {doubled!r}"
                    break
        if repeated_phrase:
            break

    matcher = SequenceMatcher(None, expected, heard)
    inserted = []
    for tag, _i1, _i2, j1, j2 in matcher.get_opcodes():
        if tag == "insert" and (j2 - j1) >= args.verify_inserted_words:
            inserted.append(" ".join(heard[j1:j2]))
    if inserted:
        return "hard", f"inserted extra words {inserted[0]!r}"
    if repeated_phrase:
        if args.verify_repeat_severity == "off":
            return None
        return args.verify_repeat_severity, repeated_phrase
    return None


def defect_types(result):
    return {defect.get("type") for defect in result.get("defects", [])}


def has_text_lock_defect(result):
    if not result:
        return False
    types = defect_types(result)
    if "repetition" in types:
        return True
    return any(
        "inserted extra words" in str(defect.get("message", ""))
        for defect in result.get("defects", [])
    )


def retry_ladder_for_result(result):
    return TEXT_LOCK_RETRY_LADDER if has_text_lock_defect(result) else VOXCPM_RETRY_LADDER


def candidate_quality_key(result, source_penalty=0):
    """Lexicographic quality rank; lower is always safer to publish.

    A retry is allowed to replace the current WAV only when it improves this
    key, so a later stochastic attempt can never overwrite a better earlier
    take.
    """
    metrics = result.get("metrics", {})
    defects = result.get("defects", [])
    hard_count = sum(defect.get("severity") == "hard" for defect in defects)
    warning_count = sum(defect.get("severity") == "warn" for defect in defects)
    longest_missing = int((metrics.get("asr_token_diff") or {}).get("longest_missing", 0) or 0)
    cer = metrics.get("asr_cer")
    cer = float(cer) if isinstance(cer, (int, float)) else 1.0
    similarity = metrics.get("asr_word_similarity")
    similarity = float(similarity) if isinstance(similarity, (int, float)) else 0.0
    ctc_metrics = metrics.get("ctc_probe") or {}
    ctc_similarity = ctc_metrics.get("ctc_similarity")
    ctc_similarity = float(ctc_similarity) if isinstance(ctc_similarity, (int, float)) else 0.0
    ctc_min_word_score = ctc_metrics.get("min_word_score")
    ctc_min_word_score = (
        float(ctc_min_word_score) if isinstance(ctc_min_word_score, (int, float)) else 0.0
    )
    speaker_similarity = metrics.get("speaker_similarity")
    speaker_similarity = (
        float(speaker_similarity) if isinstance(speaker_similarity, (int, float)) else 0.0
    )
    return (
        1 if result.get("status") != "ok" else 0,
        longest_missing,
        hard_count,
        cer,
        -similarity,
        warning_count,
        -ctc_similarity,
        -ctc_min_word_score,
        int(source_penalty),
        -speaker_similarity,
    )


class SpeakerSimilarityChecker:
    def __init__(self, ref_audio):
        self.available = False
        self.error = None
        self.encoder = None
        self.ref_embedding = None
        try:
            from resemblyzer import VoiceEncoder, preprocess_wav

            self.preprocess_wav = preprocess_wav
            self.encoder = VoiceEncoder()
            self.ref_embedding = self.encoder.embed_utterance(preprocess_wav(Path(ref_audio)))
            self.available = True
        except Exception as exc:
            self.error = str(exc)

    def similarity(self, path):
        if not self.available:
            return None
        embedding = self.encoder.embed_utterance(self.preprocess_wav(Path(path)))
        numerator = float(sum(float(a) * float(b) for a, b in zip(self.ref_embedding, embedding)))
        left = math.sqrt(sum(float(a) ** 2 for a in self.ref_embedding))
        right = math.sqrt(sum(float(b) ** 2 for b in embedding))
        return numerator / max(left * right, 1e-12)


def verify_chunk(
    chunk, wav, sample_rate, wav_path, args, transcriber, speaker_checker,
    ctc_probe=None,
):
    """Score one rendered chunk with pure text-vs-audio checks.

    This function intentionally avoids VoxCPM internals; it verifies the audio
    artifact after synthesis through ASR, timing, and speaker-similarity checks.
    """
    import numpy as np

    result = {"id": chunk["id"], "path": wav_path, "status": "ok", "defects": [], "metrics": {}}

    duration = wav.size / sample_rate if sample_rate else 0.0
    words = chunk["words"]
    wps = words / duration if duration > 0 else 0.0
    result["metrics"].update(
        {"duration_sec": round(duration, 4), "words": words, "words_per_sec": round(wps, 3)}
    )
    if duration <= 0.05:
        add_defect(result, "empty_audio", "hard", "rendered audio is empty or near-empty")
        return result
    if wps < args.verify_min_wps or wps > args.verify_max_wps:
        add_defect(
            result,
            "speech_rate",
            "hard",
            f"{wps:.2f} words/sec outside [{args.verify_min_wps}, {args.verify_max_wps}]",
        )

    peak = float(np.max(np.abs(wav))) if wav.size else 0.0
    result["metrics"]["peak"] = round(peak, 6)
    if peak >= args.verify_clip_peak:
        add_defect(result, "clipping", "hard", f"peak {peak:.3f} is near clipping")

    samples = _decode_samples(wav_path, args.verify_sample_rate)
    if samples is not None and len(samples):
        silence = longest_silence_seconds(samples, args.verify_sample_rate, args.verify_silence_threshold_db)
        result["metrics"]["longest_silence_sec"] = round(silence, 3)
        if silence >= args.verify_max_internal_silence_sec:
            add_defect(result, "long_silence", "hard", f"internal silence gap {silence:.2f}s")

    if speaker_checker is not None and speaker_checker.available and args.verify_speaker_severity != "off":
        try:
            score = speaker_checker.similarity(wav_path)
        except Exception as exc:
            score = None
            add_defect(result, "speaker_check", "info", f"speaker check failed: {exc}")
        result["metrics"]["speaker_similarity"] = score
        if score is not None:
            if score < args.verify_speaker_hard:
                severity = "hard" if args.verify_speaker_severity == "hard" else "warn"
                add_defect(result, "speaker_drift", severity, f"speaker similarity {score:.3f} < {args.verify_speaker_hard:.3f}")
            elif score < args.verify_speaker_warn:
                add_defect(result, "speaker_drift", "warn", f"speaker similarity {score:.3f} < {args.verify_speaker_warn:.3f}")

    if not args.verify_asr:
        add_defect(result, "asr", "warn", "ASR text/timing scan disabled")
        return result
    if transcriber is None:
        add_defect(result, "asr", "warn", "ASR unavailable; text/timing scan skipped")
        return result

    payload_words_pair = transcribe_word_timestamps(wav_path, args.verify_asr_model, transcriber=transcriber)
    if payload_words_pair is None:
        add_defect(result, "asr", "hard", "ASR failed")
        return result
    _payload, asr_words = payload_words_pair

    cer = cer_from_words(chunk["text"], asr_words)
    diff_evidence = token_diff_evidence(chunk["text"], asr_words)
    result["metrics"]["asr_cer"] = cer
    result["metrics"]["asr_word_similarity"] = diff_evidence["similarity"]
    result["metrics"]["asr_token_diff"] = diff_evidence
    if args.verify_cer_severity != "off" and cer > args.verify_max_cer:
        add_defect(result, "asr_cer", args.verify_cer_severity, f"ASR CER {cer:.3f} exceeds {args.verify_max_cer:.3f}")
    elif args.verify_cer_severity != "off" and cer > args.verify_cer_warn:
        add_defect(result, "asr_cer", "warn", f"ASR CER {cer:.3f} exceeds warning floor {args.verify_cer_warn:.3f}")

    ctc_metrics, ctc_defects = ctc_probe_metrics(chunk["text"], wav_path, args, ctc_probe)
    result["metrics"]["ctc_probe"] = ctc_metrics

    if args.verify_single_word_severity != "off" and diff_evidence["longest_missing"] == 1:
        ctc_supports_word = ctc_supports_missing_span(
            diff_evidence,
            ctc_metrics,
            getattr(args, "verify_ctc_single_word_support_similarity", 0.90),
        )
        if ctc_supports_word:
            payload = {
                **diff_evidence,
                "ctc_support": {
                    "ctc_text": ctc_metrics.get("ctc_text"),
                    "ctc_similarity": ctc_metrics.get("ctc_similarity"),
                },
            }
            add_defect(
                result,
                "asr_ctc_disagreement",
                "warn",
                f"Whisper omitted {diff_evidence['longest_missing_text']!r}, "
                "but independent CTC evidence contains it",
                payload,
            )
        else:
            add_defect(
                result,
                "single_word_omission",
                args.verify_single_word_severity,
                f"ASR found one acoustically absent expected word "
                f"({diff_evidence['longest_missing_text']!r})",
                diff_evidence,
            )

    for kind, severity, message, payload in ctc_defects:
        add_defect(result, kind, severity, message, payload)

    score, timing_reason = timing_defects_from_words(
        wav_path,
        chunk["text"],
        asr_words,
        args.verify_asr_model,
        swallow_db=args.verify_swallow_db,
        similarity_floor=args.verify_similarity_floor,
        adaptive_floor=args.verify_adaptive_floor,
        word_probability_floor=args.verify_word_probability_floor,
        word_duration_ratio=args.verify_word_duration_ratio,
        min_local_wps=args.verify_min_local_wps,
        max_local_wps=args.verify_max_local_wps,
        dropped_words=args.verify_dropped_words,
        drag_ratio=args.verify_drag_ratio,
        retry_text_mismatch=True,
        retry_timing_anomalies=True,
        retry_empty_asr=True,
        similarity_severity=args.verify_similarity_severity,
    )
    result["metrics"]["asr_score"] = score
    timing_text = str(timing_reason or "")
    result["metrics"]["asr_timing_reason"] = timing_text or None
    if timing_reason is None or not timing_text.startswith("ok"):
        # `swallowed`/`local tempo` come from an energy-and-duration heuristic.
        # Chunk 0071 hard-failed `swallowed 'khi'` while both Whisper and a
        # context-free CTC read transcribed the sentence exactly, which is what
        # a false positive looks like. An independent acoustic model that reads
        # every expected word outranks the heuristic that says one is missing.
        vetoable = timing_reason is not None and any(
            marker in timing_text for marker in ("swallowed", "local tempo")
        )
        severity = "warn" if vetoable and ctc_metrics.get("veto") else "hard"
        add_defect(
            result,
            "text_timing",
            severity,
            timing_reason or "ASR timing check failed",
            {"ctc_veto": bool(ctc_metrics.get("veto"))} if severity == "warn" else None,
        )
    elif "warnings:" in timing_text:
        add_defect(result, "text_timing", "warn", timing_text)

    repeated = duplicate_text_defect(chunk["text"], asr_words, args)
    if repeated:
        severity, message = repeated
        add_defect(result, "repetition", severity, message)

    return result


# ---------------------------------------------------------------------------
# Reference / model
# ---------------------------------------------------------------------------
def sha256_file(path):
    digest = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def sha256_text(value):
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def git_build_identity():
    def run_git(*parts):
        proc = subprocess.run(
            ["git", *parts],
            cwd=Path(__file__).resolve().parent,
            capture_output=True,
            text=True,
            check=False,
        )
        return proc.stdout.strip() if proc.returncode == 0 else None

    status = run_git("status", "--porcelain")
    return {"commit": run_git("rev-parse", "HEAD"), "dirty": bool(status)}


def resolve_ref_text(args):
    if args.ref_text is not None:
        return args.ref_text
    for name, text in KNOWN_VOICE_REFTEXT.items():
        if name.lower() == args.voice_name.lower():
            return text
    return None


def load_model(args):
    from voxcpm import VoxCPM

    return VoxCPM.from_pretrained(
        hf_model_id=args.model,
        load_denoiser=args.denoise,
        local_files_only=args.local_files_only,
        optimize=args.optimize,
        device=args.device,
    )


def build_reference_prompt_cache(model, args, ref_audio, ref_text):
    """Build VoxCPM2's reference/prompt cache once per process.

    ``VoxCPM.generate()`` calls ``build_prompt_cache()`` from scratch on
    every invocation, which VAE-encodes the reference wav (twice, under
    --clone_mode ultimate: once as ``reference_wav_path``, once as
    ``prompt_wav_path``). The reference audio never changes within a job, but
    render_and_verify_chunk calls render_chunk up to ``max_verify_retries + 1``
    times per chunk (more under subsplit recovery), so that encode work was
    being redone on every single attempt of every chunk for no reason.

    ``_generate_with_prompt_cache`` only reads the returned dict -- see
    voxcpm/model/voxcpm2.py: ref_audio_feat/audio_feat are pulled out with
    plain dict indexing and every downstream op is ``torch.cat`` into new
    tensors, never an in-place write -- so the same cache is safe to reuse
    across every chunk, attempt, and subsplit for the life of the process.
    Returns None when reuse isn't supported (older VoxCPM1 backend), and
    callers must fall back to the original per-call model.generate() path.
    """
    from voxcpm.model.voxcpm2 import VoxCPM2Model

    if not isinstance(model.tts_model, VoxCPM2Model):
        return None

    actual_ref_path = ref_audio
    if args.denoise and model.denoiser is not None:
        import tempfile

        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
        tmp.close()
        model.denoiser.enhance(ref_audio, output_path=tmp.name)
        actual_ref_path = tmp.name

    kwargs = {"reference_wav_path": actual_ref_path}
    if args.clone_mode == "ultimate":
        kwargs["prompt_wav_path"] = actual_ref_path
        kwargs["prompt_text"] = ref_text
    return model.tts_model.build_prompt_cache(**kwargs)


def render_chunk(
    model, chunk, args, ref_audio, ref_text, cfg_value=None, inference_timesteps=None, seed=None,
    prompt_cache=None,
):
    """One chunk, with the reference re-injected so drift cannot accumulate.

    Issue #302: prompt/reference audio conditions only the START of a
    generation, after which the decoder rides its own latents. Passing the same
    reference into every chunk is the workaround the maintainers describe, and
    it is the whole reason this pipeline chunks rather than sending the story in
    one call.
    """
    # The PyPI release (pinned by prepare_kaggle_voxcpm_job.py) has no `seed`
    # kwarg on generate() -- that only exists on the unreleased GitHub `main`
    # branch we read docs from. Seed manually so behaviour is identical either
    # way and a version bump can't silently go back to unseeded generation.
    import torch

    cfg_value = args.cfg_value if cfg_value is None else cfg_value
    inference_timesteps = args.inference_timesteps if inference_timesteps is None else inference_timesteps
    seed = (args.seed + chunk["index"] * 10000) if seed is None else seed
    torch.manual_seed(seed)
    text = chunk["text"]

    if prompt_cache is not None:
        # Mirrors VoxCPM.generate()/_generate()'s own preprocessing exactly
        # (normalize is always False here, so that branch never runs upstream
        # either -- see VOXCPM_GUIDANCE["no_builtin_normalizer_for_vietnamese"]).
        text = text.replace("\n", " ")
        text = re.sub(r"\s+", " ", text)
        wav, _text_tokens, _audio_feat = model.tts_model.generate_with_prompt_cache(
            target_text=text,
            prompt_cache=prompt_cache,
            cfg_value=cfg_value,
            inference_timesteps=inference_timesteps,
            min_len=args.min_len,
            max_len=args.max_len,
            retry_badcase=args.retry_badcase,
            retry_badcase_max_times=args.retry_badcase_max_times,
            retry_badcase_ratio_threshold=args.retry_badcase_ratio_threshold,
        )
        return wav.squeeze(0).cpu().numpy()

    kwargs = {
        "text": text,
        "cfg_value": cfg_value,
        "inference_timesteps": inference_timesteps,
        "min_len": args.min_len,
        "max_len": args.max_len,
        # Always False: VoxCPM's normalizer has no Vietnamese branch and would
        # route the text through the English one. See VOXCPM_GUIDANCE.
        "normalize": False,
        "denoise": args.denoise,
        "retry_badcase": args.retry_badcase,
        "retry_badcase_max_times": args.retry_badcase_max_times,
        "retry_badcase_ratio_threshold": args.retry_badcase_ratio_threshold,
        "reference_wav_path": ref_audio,
    }
    if args.clone_mode == "ultimate":
        kwargs["prompt_wav_path"] = ref_audio
        kwargs["prompt_text"] = ref_text
    try:
        return model.generate(seed=seed, **kwargs)
    except TypeError:
        return model.generate(**kwargs)


# ---------------------------------------------------------------------------
# Per-chunk render + verify + escalation + subsplit
# ---------------------------------------------------------------------------
def render_and_verify_chunk(
    model, chunk, args, ref_audio, ref_text, transcriber, speaker_checker, ctc_probe,
    chunk_dir, sample_rate,
    seed_base=None,
    prompt_cache=None,
):
    """Render one chunk, verifying and escalating until it passes or the
    retry ladder + subsplit recovery are exhausted. Always returns the
    best-scoring candidate seen (candidate_quality_key), even on final
    failure, so a stubborn chunk still ships its best take rather than
    nothing."""
    import numpy as np
    import soundfile as sf

    if seed_base is None:
        seed_base = args.seed + chunk["index"] * 10000

    attempts_dir = chunk_dir / ".attempts"
    attempts_dir.mkdir(parents=True, exist_ok=True)

    best = None
    last_result = None
    attempts_log = []
    # render_sec/verify_sec split the wall-clock elapsed the caller times
    # around this whole call, so the manifest can show how much of a chunk's
    # time went into GPU generation vs. ASR/CTC/speaker verification.
    render_sec = 0.0
    verify_sec = 0.0
    max_attempts = (args.max_verify_retries + 1) if args.verify_chunks else 1
    for attempt in range(max_attempts):
        ladder_sequence = retry_ladder_for_result(last_result)
        ladder = {} if attempt == 0 else ladder_sequence[(attempt - 1) % len(ladder_sequence)]
        cfg_value = ladder.get("cfg_value", args.cfg_value)
        inference_timesteps = ladder.get("inference_timesteps", args.inference_timesteps)
        seed = seed_base + attempt * 100

        render_started = time.time()
        wav = np.asarray(
            render_chunk(
                model, chunk, args, ref_audio, ref_text, cfg_value, inference_timesteps, seed,
                prompt_cache=prompt_cache,
            ),
            dtype=np.float32,
        )
        render_sec += time.time() - render_started
        attempt_path = attempts_dir / f"{chunk['id']}_attempt{attempt}.wav"
        sf.write(str(attempt_path), wav, sample_rate)

        if args.verify_chunks:
            verify_started = time.time()
            result = verify_chunk(
                chunk, wav, sample_rate, str(attempt_path), args, transcriber, speaker_checker,
                ctc_probe=ctc_probe,
            )
            verify_sec += time.time() - verify_started
        else:
            duration = wav.size / sample_rate if sample_rate else 0.0
            result = {
                "id": chunk["id"], "path": str(attempt_path), "status": "ok", "defects": [],
                "metrics": {
                    "duration_sec": round(duration, 4),
                    "words_per_sec": round(chunk["words"] / duration, 3) if duration > 0 else None,
                },
            }
        key = candidate_quality_key(result)
        attempts_log.append(
            {
                "attempt": attempt, "cfg_value": cfg_value, "inference_timesteps": inference_timesteps,
                "seed": seed, "status": result["status"], "path": str(attempt_path),
                "reason": ladder.get("reason", "base"),
                # Preserve the complete verdict so every retry remains auditable
                # after the Kaggle output bundle is downloaded.
                "candidate_quality_key": list(key),
                "result": copy.deepcopy(result),
            }
        )
        if best is None or key < best["key"]:
            best = {"attempt": attempt, "wav": wav, "path": attempt_path, "result": result, "key": key}
        last_result = result
        if result["status"] != "fail":
            break

    subsplit_event = None
    if best["result"]["status"] == "fail" and args.verify_chunks and args.verify_subsplit:
        ok, subsplit_event, sub_best, sub_timing = try_subsplit_chunk(
            model, chunk, args, ref_audio, ref_text, transcriber, speaker_checker, ctc_probe,
            chunk_dir, sample_rate,
            seed_base=seed_base, aggressive=has_text_lock_defect(best["result"]),
            prompt_cache=prompt_cache,
        )
        render_sec += sub_timing["render_sec"]
        verify_sec += sub_timing["verify_sec"]
        if ok and sub_best is not None and sub_best["key"] < best["key"]:
            best = sub_best

    final_path = chunk_dir / f"{chunk['id']}.wav"
    source_path = best["path"]
    sf.write(str(final_path), best["wav"], sample_rate)
    best = {**best, "source_path": source_path, "path": final_path}
    timing = {"render_sec": round(render_sec, 3), "verify_sec": round(verify_sec, 3)}
    return best, attempts_log, subsplit_event, timing


def try_subsplit_chunk(
    model, chunk, args, ref_audio, ref_text, transcriber, speaker_checker,
    ctc_probe, chunk_dir, sample_rate, seed_base, aggressive=False,
    prompt_cache=None,
):
    import numpy as np
    import soundfile as sf

    render_sec = 0.0
    verify_sec = 0.0
    sub_chunks = subsplit_chunk(chunk, args, aggressive=aggressive)
    event = {
        "chunk_id": chunk["id"],
        "sub_ids": [row["id"] for row in sub_chunks],
        "status": "not_split",
        "aggressive": aggressive,
    }
    if len(sub_chunks) <= 1:
        return False, event, None, {"render_sec": render_sec, "verify_sec": verify_sec}

    sub_args = copy.copy(args)
    sub_args.verify_subsplit = False
    sub_args.max_verify_retries = max(1, min(2, args.max_verify_retries))

    sub_wavs, sub_results, subchunk_audits = [], [], []
    for index, sub in enumerate(sub_chunks):
        piece_seed_base = seed_base + 5000 + index * 200
        sub_best, sub_attempts_log, sub_event, piece_timing = render_and_verify_chunk(
            model, sub, sub_args, ref_audio, ref_text, transcriber, speaker_checker, ctc_probe,
            chunk_dir, sample_rate,
            seed_base=piece_seed_base,
            prompt_cache=prompt_cache,
        )
        render_sec += piece_timing["render_sec"]
        verify_sec += piece_timing["verify_sec"]
        sub_wavs.append(sub_best["wav"])
        sub_results.append(sub_best["result"])
        subchunk_audits.append(
            {
                "id": sub["id"],
                "text": sub["text"],
                "attempts": sub_attempts_log,
                "subsplit": sub_event,
                "selected_candidate": {
                    "attempt": sub_best["attempt"],
                    "source_path": str(sub_best["source_path"]),
                    "published_path": str(sub_best["path"]),
                    "candidate_quality_key": list(sub_best["key"]),
                    "result": copy.deepcopy(sub_best["result"]),
                },
            }
        )
        Path(sub_best["path"]).unlink(missing_ok=True)  # scratch; the combined take is what ships

    pieces = []
    for index, wav in enumerate(sub_wavs):
        trimmed = trim_edges(wav, sample_rate, args.stitch_silence_threshold_db_trim, args.stitch_edge_keep_ms)
        if index > 0:
            pieces.append(np.zeros(int(sample_rate * args.stitch_cont_pause_ms / 1000.0), dtype=np.float32))
        pieces.append(trimmed)
    combined = np.concatenate(pieces) if pieces else np.zeros(0, dtype=np.float32)

    combined_path = chunk_dir / ".attempts" / f"{chunk['id']}_subsplit.wav"
    sf.write(str(combined_path), combined, sample_rate)
    if args.verify_chunks:
        verify_started = time.time()
        combined_result = verify_chunk(
            chunk, combined, sample_rate, str(combined_path), args, transcriber, speaker_checker,
            ctc_probe=ctc_probe,
        )
        verify_sec += time.time() - verify_started
    else:
        combined_result = {"id": chunk["id"], "status": "ok", "defects": [], "metrics": {}}

    event["sub_statuses"] = [result["status"] for result in sub_results]
    event["subchunks"] = subchunk_audits
    all_subchunks_ok = all(result["status"] != "fail" for result in sub_results)
    if combined_result["status"] == "fail" and all_subchunks_ok:
        combined_result = copy.deepcopy(combined_result)
        for defect in combined_result.get("defects", []):
            if defect.get("severity") == "hard":
                defect["severity"] = "warn"
        combined_result["status"] = "ok"
        add_defect(
            combined_result,
            "subsplit_parent_verify",
            "warn",
            "published subsplit because every subchunk passed; parent combined verify stayed noisy",
            {"sub_statuses": event["sub_statuses"]},
        )
        event["status"] = "published_subchunks_with_parent_warning"
    else:
        event["status"] = "published" if combined_result["status"] != "fail" else "subchunk_failed"
    best = {
        "attempt": "subsplit", "wav": combined, "path": combined_path, "result": combined_result,
        # Prefer a whole-chunk take when all content/QC evidence is tied.  A
        # subsplit still wins whenever an earlier content metric is better.
        "key": candidate_quality_key(combined_result, source_penalty=1),
    }
    event["combined_candidate"] = {
        "path": str(combined_path),
        "candidate_quality_key": list(best["key"]),
        "result": copy.deepcopy(combined_result),
    }
    return True, event, best, {"render_sec": round(render_sec, 3), "verify_sec": round(verify_sec, 3)}


# ---------------------------------------------------------------------------
# Resume / checkpoint state
# ---------------------------------------------------------------------------
def chunk_state_path(chunk_dir, output_name):
    return chunk_dir / f"{output_name}_chunk_state.json"


def load_chunk_state(path):
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return payload.get("chunks", {}) if isinstance(payload, dict) else {}


def write_chunk_state(path, state):
    payload = {"schema_version": 1, "updated_at": datetime.now(timezone.utc).isoformat(), "chunks": state}
    temp_path = path.with_name(path.name + ".tmp")
    temp_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temp_path.replace(path)


def render_params(args):
    """Parameters that change the audio VoxCPM produces."""
    return {
        "model": args.model,
        "voice_name": args.voice_name,
        "clone_mode": args.clone_mode,
        "cfg_value": args.cfg_value,
        "inference_timesteps": args.inference_timesteps,
        "min_len": args.min_len,
        "max_len": args.max_len,
        "retry_badcase": args.retry_badcase,
        "retry_badcase_max_times": args.retry_badcase_max_times,
        "retry_badcase_ratio_threshold": args.retry_badcase_ratio_threshold,
        "max_verify_retries": args.max_verify_retries,
        "verify_subsplit": args.verify_subsplit,
        "seed": args.seed,
        "ref_audio_sha256": sha256_file(args.ref_audio) if Path(args.ref_audio).is_file() else None,
    }


def qc_params(args):
    """Parameters that change only the verdict on already-rendered audio.

    Kept separate from :func:`render_params` on purpose. Folding QC thresholds
    into one hash meant that tuning a single floor invalidated every chunk and
    forced a full GPU re-render of audio that had not changed. Splitting them
    lets a QC change re-verify existing WAVs instead.
    """
    return {
        "verify_chunks": args.verify_chunks,
        "verify_asr": args.verify_asr,
        "verify_asr_model": args.verify_asr_model,
        "verify_similarity_floor": args.verify_similarity_floor,
        "verify_adaptive_floor": args.verify_adaptive_floor,
        "verify_similarity_severity": args.verify_similarity_severity,
        "verify_max_cer": args.verify_max_cer,
        "verify_cer_warn": args.verify_cer_warn,
        "verify_cer_severity": args.verify_cer_severity,
        "verify_single_word_severity": args.verify_single_word_severity,
        "verify_dropped_words": args.verify_dropped_words,
        "verify_drag_ratio": args.verify_drag_ratio,
        "verify_swallow_db": args.verify_swallow_db,
        "verify_ctc_probe": args.verify_ctc_probe,
        "verify_ctc_model": args.verify_ctc_model,
        "verify_ctc_out_of_text_ms": args.verify_ctc_out_of_text_ms,
        "verify_ctc_out_of_text_chars": args.verify_ctc_out_of_text_chars,
        "verify_ctc_veto_similarity": args.verify_ctc_veto_similarity,
        "verify_ctc_single_word_support_similarity": args.verify_ctc_single_word_support_similarity,
        "verify_ctc_min_word_score": args.verify_ctc_min_word_score,
        "verify_ctc_min_word_score_severity": args.verify_ctc_min_word_score_severity,
        "verify_inserted_words": args.verify_inserted_words,
        "verify_repeat_max_ngram": args.verify_repeat_max_ngram,
        "verify_repeat_severity": args.verify_repeat_severity,
        "verify_speaker_severity": args.verify_speaker_severity,
        "verify_speaker_warn": args.verify_speaker_warn,
        "verify_speaker_hard": args.verify_speaker_hard,
    }


def _sha_of(payload):
    return sha256_text(json.dumps(payload, sort_keys=True, separators=(",", ":")))


def render_sha256(args):
    return _sha_of(render_params(args))


def qc_sha256(args):
    return _sha_of(qc_params(args))


def params_sha256(args):
    return _sha_of({**render_params(args), **qc_params(args)})


def existing_good_chunk_ids(chunks, chunk_dir, output_name, args):
    """Chunk ids whose WAV on disk can be reused as-is.

    A chunk is only reusable when its text, its render parameters, *and* the QC
    policy it was judged under all still match. A QC-only change leaves the
    audio valid but the verdict stale, so those chunks are re-rendered rather
    than trusted; ``--no-rerender_on_param_change`` opts out of both checks.
    """
    if not args.resume:
        return set()
    state = load_chunk_state(chunk_state_path(chunk_dir, output_name))
    current_render_sha = render_sha256(args)
    current_qc_sha = qc_sha256(args)
    good = set()
    for chunk in chunks:
        path = chunk_dir / f"{chunk['id']}.wav"
        row = state.get(chunk["id"], {})
        matches_text = row.get("text_sha") == sha256_text(chunk["text"])
        matches_params = not args.rerender_on_param_change or (
            row.get("render_sha") == current_render_sha
            and row.get("qc_sha") == current_qc_sha
        )
        matches_wav = False
        if path.is_file() and path.stat().st_size > 4096 and matches_text and matches_params:
            matches_wav = not row.get("wav_sha") or row["wav_sha"] == sha256_file(str(path))
        if matches_wav and row.get("qc_status") != "fail":
            good.add(chunk["id"])
    return good


# ---------------------------------------------------------------------------
# Mastering
# ---------------------------------------------------------------------------
def _json_object_from_text(text):
    decoder = json.JSONDecoder()
    starts = [index for index, char in enumerate(text) if char == "{"]
    for start in reversed(starts):
        try:
            payload, _end = decoder.raw_decode(text[start:])
            return payload
        except (ValueError, json.JSONDecodeError):
            continue
    return None


def ffmpeg_loudness_metrics(path):
    try:
        proc = subprocess.run(
            [
                "ffmpeg", "-hide_banner", "-nostats", "-i", str(path),
                "-af", "loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json",
                "-f", "null", "-",
            ],
            capture_output=True, text=True, check=False,
        )
    except OSError:
        return {"lufs": None, "true_peak_db": None, "lra": None}
    payload = _json_object_from_text(proc.stderr)
    if not payload:
        return {"lufs": None, "true_peak_db": None, "lra": None}

    def number(key):
        try:
            value = float(payload.get(key))
            return value if math.isfinite(value) else None
        except (TypeError, ValueError):
            return None

    return {
        "lufs": number("input_i"), "true_peak_db": number("input_tp"), "lra": number("input_lra"),
        "loudness_threshold": number("input_thresh"),
    }


def master_loudnorm_two_pass(input_path, output_path, args, sample_rate):
    target = f"I={args.master_target_lufs}:TP={args.master_true_peak}:LRA={args.master_lra}"
    first = subprocess.run(
        [
            "ffmpeg", "-hide_banner", "-nostats", "-i", str(input_path),
            "-af", f"loudnorm={target}:print_format=json", "-f", "null", "-",
        ],
        capture_output=True, text=True, check=True,
    )
    measured = _json_object_from_text(first.stderr)
    if not measured:
        raise RuntimeError("ffmpeg loudnorm pass 1 did not return measurement JSON")
    measured_args = ":".join(
        [
            f"measured_I={measured['input_i']}", f"measured_TP={measured['input_tp']}",
            f"measured_LRA={measured['input_lra']}", f"measured_thresh={measured['input_thresh']}",
            f"offset={measured['target_offset']}",
        ]
    )
    subprocess.run(
        [
            "ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", str(input_path),
            "-af", f"loudnorm={target}:{measured_args}:linear=true:print_format=json",
            "-ar", str(sample_rate), "-ac", "1", "-c:a", "pcm_s16le", str(output_path),
        ],
        check=True,
    )
    return {
        "enabled": True, "target_lufs": args.master_target_lufs, "target_true_peak": args.master_true_peak,
        "target_lra": args.master_lra, "input": ffmpeg_loudness_metrics(input_path),
        "output": ffmpeg_loudness_metrics(output_path),
    }


# ---------------------------------------------------------------------------
# Reports
# ---------------------------------------------------------------------------
def write_verify_report(path, per_chunk_records):
    payload = {
        "schema_version": 2,
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "chunks": [
            {
                "id": rec["id"],
                "result": rec["result"],
                "qc_audit": rec.get("qc_audit"),
            }
            for rec in per_chunk_records
        ],
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_render_status(path, chunks, final_wav):
    payload = {
        "schema_version": 1,
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "final_wav": str(final_wav),
        "chunk_count": len(chunks),
        "fail_count": sum(1 for chunk in chunks if chunk.get("qc_status") == "fail"),
        "resumed_count": sum(1 for chunk in chunks if chunk.get("qc_status") == "resumed"),
        "chunks": [
            {
                "id": chunk["id"], "qc_status": chunk.get("qc_status"),
                "words_per_sec": chunk.get("words_per_sec"), "render_attempts": chunk.get("render_attempts"),
            }
            for chunk in chunks
        ],
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def export_verify_failures(output_dir, output_name, per_chunk_records):
    failing = [rec for rec in per_chunk_records if rec["result"]["status"] == "fail"]
    if not failing:
        return None
    review_dir = output_dir / f"{output_name}_verify_failures"
    review_dir.mkdir(parents=True, exist_ok=True)
    for rec in failing:
        row_dir = review_dir / rec["id"]
        row_dir.mkdir(parents=True, exist_ok=True)
        (row_dir / "chunk.txt").write_text(rec["text"] + "\n", encoding="utf-8")
        (row_dir / "result.json").write_text(
            json.dumps(
                {
                    "id": rec["id"],
                    "result": rec["result"],
                    "qc_audit": rec.get("qc_audit"),
                },
                ensure_ascii=False,
                indent=2,
            ) + "\n",
            encoding="utf-8",
        )
        source = Path(rec["wav_path"])
        if source.is_file():
            shutil.copy2(source, row_dir / "published.wav")
    return review_dir


def _cuda_device_count():
    try:
        import torch

        return torch.cuda.device_count() if torch.cuda.is_available() else 0
    except Exception:
        return 0


def _parse_render_devices(value):
    if not value:
        return None
    devices = []
    for part in str(value).split(","):
        item = part.strip()
        if not item:
            continue
        if item.startswith("cuda:"):
            item = item.split(":", 1)[1]
        devices.append(int(item))
    return devices or None


def _available_render_devices(args):
    requested = _parse_render_devices(args.render_devices)
    if requested is not None:
        return requested
    if args.device:
        device = str(args.device).strip().lower()
        if device.startswith("cuda:"):
            return [int(device.split(":", 1)[1])]
        if device not in ("cuda", "auto"):
            return []
    return list(range(_cuda_device_count()))


def resolve_parallel_render_plan(args, render_count):
    if render_count <= 1:
        return 1, []
    devices = _available_render_devices(args)
    raw_workers = str(args.render_workers).strip().lower()
    if raw_workers == "auto":
        workers = len(devices) if devices else 1
    else:
        workers = max(1, int(raw_workers))
    if workers <= 1:
        return 1, devices[:1]
    if not devices:
        print("render workers : 1 (no CUDA devices available for parallel render)")
        return 1, []
    return min(workers, len(devices), render_count), devices[:workers]


def _render_worker(worker_id, device_index, work_queue, args, ref_audio, ref_text, chunk_dir_text, result_queue):
    """Render chunks pulled from a shared ``work_queue`` on one GPU, with its
    own locally-owned FasterWhisper/CTC/speaker QC stack.

    Every worker across every GPU shares the same queue, so whichever GPU
    finishes its current chunk first claims the next one, instead of each
    GPU working through a fixed, statically-assigned half. ``work_queue``
    always has at least ``worker_count`` real items ahead of its sentinels
    (see render_chunks_parallel), so every worker is guaranteed at least one
    chunk before it can see ``None``.
    """
    transcriber = None
    ctc_probe = None
    model = None
    try:
        child_args = copy.copy(args)
        child_args.device = f"cuda:{device_index}"
        os.environ.setdefault("CUDA_DEVICE_ORDER", "PCI_BUS_ID")
        try:
            import torch

            if torch.cuda.is_available():
                torch.cuda.set_device(device_index)
                torch.cuda.reset_peak_memory_stats(device_index)
        except Exception:
            pass

        chunk_dir = Path(chunk_dir_text)
        model = load_model(child_args)
        sample_rate = model.tts_model.sample_rate
        prompt_cache = build_reference_prompt_cache(model, child_args, ref_audio, ref_text)

        speaker_checker = None
        if child_args.verify_chunks and child_args.verify_asr:
            transcriber = FasterWhisperSession(device_index=device_index)
        if child_args.verify_chunks and child_args.verify_ctc_probe:
            ctc_probe = CtcProbeSession(
                model_name=child_args.verify_ctc_model,
                device=child_args.device,
            )
        if child_args.verify_chunks and child_args.verify_speaker_severity != "off":
            speaker_checker = SpeakerSimilarityChecker(ref_audio)
            if not speaker_checker.available:
                result_queue.put(
                    {
                        "type": "log",
                        "worker_id": worker_id,
                        "message": f"speaker check unavailable on cuda:{device_index}: {speaker_checker.error}",
                    }
                )

        while True:
            item = work_queue.get()
            if item is None:
                break
            position, chunk = item
            chunk_started = time.time()
            best, attempts_log, subsplit_event, timing = render_and_verify_chunk(
                model,
                chunk,
                child_args,
                ref_audio,
                ref_text,
                transcriber,
                speaker_checker,
                ctc_probe,
                chunk_dir,
                sample_rate,
                prompt_cache=prompt_cache,
            )
            result_queue.put(
                {
                    "type": "chunk",
                    "worker_id": worker_id,
                    "device": child_args.device,
                    "position": position,
                    "chunk_id": chunk["id"],
                    "sample_rate": sample_rate,
                    "result": best["result"],
                    "attempts_log": attempts_log,
                    "subsplit_event": subsplit_event,
                    "selected_attempt": best["attempt"],
                    "selected_source_path": str(best["source_path"]),
                    "selected_quality_key": list(best["key"]),
                    "elapsed": time.time() - chunk_started,
                    "render_sec": timing["render_sec"],
                    "verify_sec": timing["verify_sec"],
                }
            )
    except BaseException as exc:
        result_queue.put(
            {
                "type": "error",
                "worker_id": worker_id,
                "device": f"cuda:{device_index}",
                "error": f"{type(exc).__name__}: {exc}",
                "traceback": traceback.format_exc(),
            }
        )
    finally:
        if transcriber is not None:
            transcriber.close()
        if ctc_probe is not None:
            ctc_probe.close()
        del model
        try:
            import torch

            if torch.cuda.is_available():
                torch.cuda.empty_cache()
        except Exception:
            pass


def _drain_render_results(result_queue, watch_processes, total_chunks, expected, join_processes=None):
    """Poll ``result_queue`` for chunk/log/error messages until ``expected``
    chunks complete, printing progress. ``watch_processes`` is only used to
    detect a dead process while waiting (e.g. a crashed QC server that would
    otherwise hang a render worker forever); ``join_processes`` (default:
    ``watch_processes``) is what actually gets joined/terminated afterwards --
    shared-QC callers pass the render workers only, since QC servers are
    shut down separately once every worker on their GPU has exited.
    """
    import queue as queue_module

    join_processes = watch_processes if join_processes is None else join_processes
    completed = 0
    rows = []
    terminated_by_us = set()
    try:
        while completed < expected:
            try:
                message = result_queue.get(timeout=5)
            except queue_module.Empty:
                failed = [proc for proc in watch_processes if proc.exitcode not in (None, 0)]
                if failed:
                    raise SystemExit(f"Parallel render worker exited with code {failed[0].exitcode}")
                continue
            if message["type"] == "log":
                print(message["message"])
                continue
            if message["type"] == "error":
                for proc in watch_processes:
                    if proc.is_alive():
                        proc.terminate()
                raise SystemExit(
                    f"Parallel render worker {message['worker_id']} failed on {message['device']}: "
                    f"{message['error']}\n{message['traceback']}"
                )

            completed += 1
            rows.append(message)
            metrics = message["result"].get("metrics", {})
            print(
                f"[{message['position'] + 1}/{total_chunks}] {message['chunk_id']} "
                f"status={message['result']['status']} attempts={len(message['attempts_log'])} "
                f"{metrics.get('duration_sec')}s wps={metrics.get('words_per_sec')} "
                f"wall={message['elapsed']:.1f}s (gpu={message['render_sec']:.1f}s "
                f"verify={message['verify_sec']:.1f}s) {message['device']}"
            )
    finally:
        for proc in join_processes:
            # All ``expected`` chunk results are already in hand by this point
            # (or we're unwinding from a raised exception above), so this is
            # teardown, not the render itself. A worker that just finished its
            # last chunk still has to close its FasterWhisper/CTC-probe
            # sessions and release CUDA state, which can outlast a short
            # timeout under load -- give it real headroom before escalating.
            proc.join(timeout=60)
            if proc.is_alive():
                proc.terminate()
                terminated_by_us.add(proc.pid)
                proc.join(timeout=5)

    for proc in join_processes:
        if proc.pid in terminated_by_us:
            # We're the ones who sent this SIGTERM (exitcode -15), purely
            # because teardown was slow after every expected result was
            # already collected. That's a slow exit, not a render failure --
            # treat it the same as a clean exit rather than aborting the job.
            continue
        if proc.exitcode not in (0, None):
            raise SystemExit(f"Parallel render worker exited with code {proc.exitcode}")
    return rows


def render_chunks_parallel(work_items, args, ref_audio, ref_text, chunk_dir, worker_count, devices, total_chunks):
    """One render worker per active GPU, all pulling from a single shared
    work queue instead of a static per-GPU split. A statically-assigned half
    leaves the faster (or luckier, retry-free) GPU idle at the tail waiting
    for the other one -- the longer the story, the more that idle tail costs.
    """
    import multiprocessing as mp

    ctx = mp.get_context("spawn")
    result_queue = ctx.Queue()
    work_queue = ctx.Queue()
    for item in work_items:
        work_queue.put(item)
    for _ in range(worker_count):
        work_queue.put(None)

    processes = []
    for worker_id, device_index in enumerate(devices[:worker_count]):
        process = ctx.Process(
            target=_render_worker,
            args=(worker_id, device_index, work_queue, args, ref_audio, ref_text, str(chunk_dir), result_queue),
        )
        process.start()
        processes.append(process)

    return _drain_render_results(result_queue, processes, total_chunks, len(work_items))


def main(argv=None):
    args = build_parser().parse_args(argv)
    started = time.time()

    ref_audio = str(Path(args.ref_audio).resolve())
    ref_text = resolve_ref_text(args)
    if args.clone_mode == "ultimate" and not ref_text:
        raise SystemExit(
            "--clone_mode ultimate needs the reference transcript; pass --ref_text "
            f"or add '{args.voice_name}' to KNOWN_VOICE_REFTEXT."
        )
    if not args.dry_run and not Path(ref_audio).is_file():
        raise SystemExit(f"Reference audio not found: {ref_audio}")

    normalized, word_count, chunks = prepare_chunks(args)
    if not chunks:
        raise SystemExit("No chunks planned from input")

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    suffix = f"_first_{args.story_word_limit}_words" if args.story_word_limit else ""
    output_name = f"{Path(args.input).stem}{suffix}_voxcpm"
    chunk_dir = output_dir / f"{output_name}_chunks"
    chunk_dir.mkdir(parents=True, exist_ok=True)

    (output_dir / f"{output_name}_normalized.txt").write_text(normalized.rstrip() + "\n", encoding="utf-8")
    with (chunk_dir / f"{output_name}_chunks.jsonl").open("w", encoding="utf-8") as fh:
        for chunk in chunks:
            fh.write(json.dumps(chunk, ensure_ascii=False) + "\n")

    char_counts = [chunk["chars"] for chunk in chunks]
    print(f"input          : {args.input}")
    print(f"words rendered : {word_count}")
    print(f"chunks         : {len(chunks)}")
    print(
        "chunk chars    : "
        f"min={min(char_counts)} max={max(char_counts)} "
        f"mean={sum(char_counts) / len(char_counts):.1f} (cap {args.max_chunk_chars})"
    )
    print(f"clone mode     : {args.clone_mode} ({args.voice_name})")
    print(f"cfg / steps    : {args.cfg_value} / {args.inference_timesteps}")
    print(f"verify         : {'on' if args.verify_chunks else 'off'} (retries={args.max_verify_retries}, subsplit={args.verify_subsplit})")
    print(f"resume         : {'on' if args.resume else 'off'}")

    manifest_base = {
        "schema_version": 2,
        "engine": "voxcpm",
        "built_at": datetime.now(timezone.utc).isoformat(),
        "git": git_build_identity(),
        "input": str(args.input),
        "output_name": output_name,
        "voice_name": args.voice_name,
        "clone_mode": args.clone_mode,
        "reference_audio_sha256": sha256_file(ref_audio) if Path(ref_audio).is_file() else None,
        "reference_text": ref_text,
        "words_rendered": word_count,
        "chunk_count": len(chunks),
        "chunk_chars": {
            "min": min(char_counts), "max": max(char_counts),
            "mean": round(sum(char_counts) / len(char_counts), 2),
        },
        "args": vars(args),
        "guidance": VOXCPM_GUIDANCE,
        "chunks": chunks,
    }

    if args.dry_run:
        manifest_base["status"] = "dry_run"
        (output_dir / f"{output_name}_manifest.json").write_text(
            json.dumps(manifest_base, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        print(f"dry run: wrote plan for {len(chunks)} chunks, rendered nothing")
        return

    import numpy as np
    import soundfile as sf

    state_path = chunk_state_path(chunk_dir, output_name)
    chunk_state = load_chunk_state(state_path) if args.resume else {}
    good_ids = existing_good_chunk_ids(chunks, chunk_dir, output_name, args)
    print(f"resume         : {len(good_ids)}/{len(chunks)} chunks already good")

    to_render = [chunk for chunk in chunks if chunk["id"] not in good_ids]
    worker_count, render_devices = resolve_parallel_render_plan(args, len(to_render))
    if to_render and args.verify_chunks and args.verify_asr:
        if not faster_whisper_available():
            raise SystemExit(
                "--verify_asr requested but faster-whisper is not installed; "
                "pass --no-verify_asr to skip ASR-based verification."
            )
    if to_render:
        devices_label = ",".join(f"cuda:{device}" for device in render_devices) if render_devices else "single"
        print(f"render workers : {worker_count} ({devices_label})")

    chunk_audio = {}
    per_chunk_records_by_id = {}
    subsplit_events = []
    sample_rate = None

    def apply_render_result(row):
        nonlocal sample_rate
        chunk = chunks[row["position"]]
        row_sample_rate = row["sample_rate"]
        if sample_rate is None:
            sample_rate = row_sample_rate
            print(f"sample rate    : {sample_rate}")
        elif row_sample_rate != sample_rate:
            raise SystemExit(
                f"Rendered chunk {chunk['id']} sample rate {row_sample_rate} != expected {sample_rate}"
            )

        chunk_state[chunk["id"]] = {
            "text_sha": sha256_text(chunk["text"]),
            "render_sha": render_sha256(args),
            "qc_sha": qc_sha256(args),
            "wav_sha": sha256_file(str(chunk_dir / f"{chunk['id']}.wav")),
            "qc_status": row["result"]["status"],
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
        write_chunk_state(state_path, chunk_state)
        if row.get("subsplit_event"):
            subsplit_events.append(row["subsplit_event"])

        metrics = row["result"].get("metrics", {})
        chunk["duration_sec"] = metrics.get("duration_sec")
        chunk["words_per_sec"] = metrics.get("words_per_sec")
        chunk["qc_status"] = row["result"]["status"]
        chunk["render_attempts"] = len(row["attempts_log"])
        chunk["render_sec"] = round(row["elapsed"], 2)
        # GPU-generate vs CPU/GPU-QC split of the wall time above -- lets us
        # tell whether a chunk's time went into VoxCPM generation or into
        # ASR/CTC/speaker verification without re-running anything.
        chunk["render_sec_gpu"] = row.get("render_sec")
        chunk["verify_sec"] = row.get("verify_sec")
        per_chunk_records_by_id[chunk["id"]] = {
            "id": chunk["id"],
            "text": chunk["text"],
            "wav_path": str(chunk_dir / f"{chunk['id']}.wav"),
            "result": row["result"],
            "qc_audit": {
                "attempts": row["attempts_log"],
                "subsplit": row.get("subsplit_event"),
                "selected_candidate": {
                    "attempt": row["selected_attempt"],
                    "source_path": row["selected_source_path"],
                    "published_path": str(chunk_dir / f"{chunk['id']}.wav"),
                    "candidate_quality_key": row["selected_quality_key"],
                    "result": copy.deepcopy(row["result"]),
                },
            },
        }

    work_items = [(position, chunk) for position, chunk in enumerate(chunks) if chunk["id"] not in good_ids]
    if work_items and worker_count > 1:
        for row in render_chunks_parallel(
            work_items, args, ref_audio, ref_text, chunk_dir, worker_count, render_devices, len(chunks)
        ):
            apply_render_result(row)
    elif work_items:
        model = load_model(args)
        sample_rate = model.tts_model.sample_rate
        print(f"sample rate    : {sample_rate}")
        prompt_cache = build_reference_prompt_cache(model, args, ref_audio, ref_text)
        transcriber = None
        speaker_checker = None
        ctc_probe = None
        if args.verify_chunks and args.verify_asr:
            transcriber = FasterWhisperSession()
        if args.verify_chunks and args.verify_ctc_probe:
            ctc_probe = CtcProbeSession(
                model_name=args.verify_ctc_model,
                device=args.device,
            )
        if args.verify_chunks and args.verify_speaker_severity != "off":
            speaker_checker = SpeakerSimilarityChecker(ref_audio)
            if not speaker_checker.available:
                print(f"speaker check unavailable: {speaker_checker.error}")
        try:
            for position, chunk in work_items:
                chunk_started = time.time()
                best, attempts_log, subsplit_event, timing = render_and_verify_chunk(
                    model, chunk, args, ref_audio, ref_text, transcriber, speaker_checker, ctc_probe,
                    chunk_dir, sample_rate,
                    prompt_cache=prompt_cache,
                )
                row = {
                    "position": position,
                    "sample_rate": sample_rate,
                    "result": best["result"],
                    "attempts_log": attempts_log,
                    "subsplit_event": subsplit_event,
                    "selected_attempt": best["attempt"],
                    "selected_source_path": str(best["source_path"]),
                    "selected_quality_key": list(best["key"]),
                    "elapsed": time.time() - chunk_started,
                    "render_sec": timing["render_sec"],
                    "verify_sec": timing["verify_sec"],
                }
                apply_render_result(row)
                metrics = best["result"].get("metrics", {})
                print(
                    f"[{position + 1}/{len(chunks)}] {chunk['id']} status={chunk['qc_status']} "
                    f"attempts={len(attempts_log)} {metrics.get('duration_sec')}s "
                    f"wps={metrics.get('words_per_sec')} wall={row['elapsed']:.1f}s "
                    f"(gpu={row['render_sec']:.1f}s verify={row['verify_sec']:.1f}s)"
                )
        finally:
            if transcriber is not None:
                transcriber.close()
            if ctc_probe is not None:
                ctc_probe.close()

    for position, chunk in enumerate(chunks):
        wav, file_sample_rate = sf.read(str(chunk_dir / f"{chunk['id']}.wav"), dtype="float32")
        if sample_rate is None:
            sample_rate = file_sample_rate
            print(f"sample rate    : {sample_rate}")
        if file_sample_rate != sample_rate:
            raise SystemExit(
                f"Chunk {chunk['id']} sample rate {file_sample_rate} != expected {sample_rate}; "
                "rerun with --no-resume."
            )
        chunk_audio[chunk["id"]] = wav
        if chunk["id"] in good_ids:
            chunk["qc_status"] = "resumed"
            per_chunk_records_by_id[chunk["id"]] = {
                "id": chunk["id"],
                "text": chunk["text"],
                "wav_path": str(chunk_dir / f"{chunk['id']}.wav"),
                "result": {"id": chunk["id"], "status": "resumed", "defects": [], "metrics": {}},
                "qc_audit": {
                    "attempts": [],
                    "subsplit": None,
                    "selected_candidate": {
                        "attempt": "resumed",
                        "source_path": str(chunk_dir / f"{chunk['id']}.wav"),
                        "published_path": str(chunk_dir / f"{chunk['id']}.wav"),
                        "candidate_quality_key": None,
                        "result": {"id": chunk["id"], "status": "resumed", "defects": [], "metrics": {}},
                    },
                },
            }
            print(f"[{position + 1}/{len(chunks)}] {chunk['id']} resumed")

    per_chunk_records = [per_chunk_records_by_id[chunk["id"]] for chunk in chunks]
    failures = [rec for rec in per_chunk_records if rec["result"]["status"] == "fail"]

    ordered_wavs = [chunk_audio[chunk["id"]] for chunk in chunks]
    final_raw, stitch_report = stitch(chunks, ordered_wavs, sample_rate, args)
    artifact_name = output_name if not failures else f"{output_name}_qc_failed_preview"
    premaster_path = output_dir / f"{artifact_name}_premaster.wav"
    sf.write(str(premaster_path), final_raw, sample_rate)

    final_path = output_dir / f"{artifact_name}.wav"
    if args.master:
        mastering_report = master_loudnorm_two_pass(premaster_path, final_path, args, sample_rate)
    else:
        shutil.copy2(premaster_path, final_path)
        mastering_report = {"enabled": False}

    if not args.keep_premaster:
        premaster_path.unlink(missing_ok=True)
    if not args.keep_chunks:
        for path in chunk_dir.glob("*.wav"):
            path.unlink()

    write_verify_report(output_dir / f"{output_name}_verify_report.json", per_chunk_records)
    review_dir = export_verify_failures(output_dir, output_name, per_chunk_records)
    write_render_status(output_dir / f"{output_name}_render_status.json", chunks, final_path)

    speech_sec = sum(chunk.get("duration_sec") or 0.0 for chunk in chunks)
    manifest_base.update(
        {
            "status": "rendered" if not failures else "qc_failed_preview",
            "sample_rate": sample_rate,
            "final_wav": str(final_path),
            "final_duration_sec": round(final_raw.size / sample_rate, 3) if not args.master else None,
            "speech_duration_sec": round(speech_sec, 3),
            "inserted_pause_sec": round(sum(row["pause_ms"] for row in stitch_report) / 1000.0, 3),
            "resumed_chunks": len(good_ids),
            "rendered_chunks": len(to_render),
            "fail_count": len(failures),
            "subsplit_events": subsplit_events,
            "mastering": mastering_report,
            "wall_clock_sec": round(time.time() - started, 1),
            "chunks": chunks,
            "stitch": stitch_report,
        }
    )
    (output_dir / f"{output_name}_manifest.json").write_text(
        json.dumps(manifest_base, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    wps = [chunk["words_per_sec"] for chunk in chunks if chunk.get("words_per_sec")]
    print(f"\nfinal          : {final_path}")
    print(f"resumed/render : {len(good_ids)}/{len(to_render)}")
    print(f"fail count     : {len(failures)}" + (f" (see {review_dir})" if review_dir else ""))
    print(f"wall clock     : {manifest_base['wall_clock_sec']:.0f}s")
    gpu_secs = [chunk["render_sec_gpu"] for chunk in chunks if chunk.get("render_sec_gpu") is not None]
    verify_secs = [chunk["verify_sec"] for chunk in chunks if chunk.get("verify_sec") is not None]
    if gpu_secs or verify_secs:
        total_gpu = sum(gpu_secs)
        total_verify = sum(verify_secs)
        print(
            f"gpu/verify sec : generate={total_gpu:.0f}s verify={total_verify:.0f}s "
            f"(sum of per-chunk render_sec_gpu/verify_sec in the manifest; use this to "
            "gauge how much idle GPU time a shared-QC worker layout could reclaim)"
        )
    if wps:
        wps_sorted = sorted(wps)
        print(
            "words/sec      : "
            f"min={wps_sorted[0]:.2f} median={wps_sorted[len(wps_sorted) // 2]:.2f} "
            f"max={wps_sorted[-1]:.2f}"
        )


if __name__ == "__main__":
    main()
