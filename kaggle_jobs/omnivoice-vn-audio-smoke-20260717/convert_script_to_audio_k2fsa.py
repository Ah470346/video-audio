#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Render a Vietnamese story with k2-fsa/OmniVoice.

This is intentionally separate from omnivoice_story_core.py.  The Studio
pipeline has many tuned safety/QA settings; this script keeps the same story
preparation shape (clean markdown -> normalize Vietnamese TTS text -> chunk ->
JSONL -> batch render -> concat).  It defaults to a Mac-safe execution preset
for an M1/16GB machine, with an opt-in switch for upstream k2-fsa defaults.
"""

import argparse
import json
import math
import os
import re
import shutil
import subprocess
import sys
from contextlib import nullcontext
from datetime import datetime, timezone
from pathlib import Path
from statistics import median as statistics_median

from omnivoice_story_core import (
    DEFAULT_PRON_DICT,
    DEFAULT_FAST_SWALLOW_DB,
    KNOWN_VOICE_REFTEXT,
    MLXWhisperSession,
    _decode_samples,
    _normalize_for_compare,
    _whisper_bin,
    clean_markdown,
    concatenate_audio_files,
    normalize_for_tts,
    probe_chunk_stats,
    split_text_into_chunks,
    timing_defects_from_words,
    transcribe_word_timestamps,
    validate_chunk_audio,
    write_jsonl,
)


DEFAULT_VOICE_NAME = "NGOC HUYEN V2"
DEFAULT_REF_AUDIO = "/Users/truongdv/Downloads/ngoc_huyen_moi_ref_clone_tu_nhien.wav"
DEFAULT_OMNIVOICE_ROOT = os.environ.get(
    "K2FSA_OMNIVOICE_ROOT",
    os.path.expanduser("~/k2fsa-omnivoice311"),
)
DEFAULT_OMNIVOICE_BIN = os.path.join(
    DEFAULT_OMNIVOICE_ROOT,
    ".venv",
    "bin",
    "omnivoice-infer-batch",
)
DEFAULT_ASR_MODEL = "mlx-community/whisper-large-v3-turbo"
MAC_SAFE_DEFAULTS = {
    "batch_size": 1,
    "nj_per_gpu": 1,
    "warmup": 0,
}


def find_omnivoice_bin(explicit_path=None):
    candidates = []
    if explicit_path:
        candidates.append(explicit_path)
    env_path = os.environ.get("K2FSA_OMNIVOICE_INFER_BATCH")
    if env_path:
        candidates.append(env_path)
    candidates.append(DEFAULT_OMNIVOICE_BIN)
    path_bin = shutil.which("omnivoice-infer-batch")
    if path_bin:
        candidates.append(path_bin)
    for candidate in candidates:
        if candidate and os.path.exists(candidate) and os.access(candidate, os.X_OK):
            return candidate
    return None


def write_voice_profile(path, args, ref_text):
    profile = {
        "name": args.voice_name,
        "engine": "k2-fsa/OmniVoice",
        "model": args.model,
        "ref_audio": os.path.abspath(args.ref_audio),
        "ref_text": ref_text,
        "language_id": args.language,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "note": (
            "Voice clone profile for k2-fsa OmniVoice. The batch JSONL uses "
            "this reference audio/text directly."
        ),
    }
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(profile, fh, ensure_ascii=False, indent=2)


def select_entries(entries, limit=None, only=None):
    selected = list(entries)
    if only:
        wanted = {token.strip().lstrip("0") or "0" for token in only.split(",")}
        selected = [
            entry
            for index, entry in enumerate(selected, start=1)
            if str(index) in wanted
            or entry["id"].rsplit("_", 1)[1].lstrip("0") in wanted
        ]
    if limit is not None:
        selected = selected[:limit]
    return selected


def expected_chunk_paths(entries, chunk_dir):
    return [os.path.join(chunk_dir, f"{entry['id']}.wav") for entry in entries]


def chunk_path(entry, chunk_dir):
    return os.path.join(chunk_dir, f"{entry['id']}.wav")


def existing_good_wavs(entries, chunk_dir):
    good = []
    for entry in entries:
        path = chunk_path(entry, chunk_dir)
        if os.path.exists(path) and os.path.getsize(path) > 4096:
            good.append(entry["id"])
    return set(good)


def apply_runtime_preset(args):
    if args.runtime_preset == "upstream_defaults":
        return

    for name, value in MAC_SAFE_DEFAULTS.items():
        if getattr(args, name) is None:
            setattr(args, name, value)


def runtime_settings(args):
    keys = [
        "runtime_preset",
        "batch_size",
        "nj_per_gpu",
        "warmup",
        "num_step",
        "position_temperature",
        "guidance_scale",
        "t_shift",
        "audio_chunk_duration",
        "audio_chunk_threshold",
        "story_word_limit",
        "omnivoice_no_edge_fade",
        "verify_chunks",
        "verify_asr",
        "max_verify_retries",
        "stitch_pause",
    ]
    return {key: getattr(args, key) for key in keys}


def run_k2fsa_omnivoice(jsonl_path, chunk_dir, args):
    cmd = [
        args.omnivoice_bin,
        "--model",
        args.model,
        "--test_list",
        jsonl_path,
        "--res_dir",
        chunk_dir,
    ]

    # In upstream_defaults mode, unset knobs are omitted so they come from
    # k2-fsa/OmniVoice itself.  In mac_safe mode, apply_runtime_preset sets only
    # resource-control knobs: generation quality defaults still come from k2-fsa
    # unless the caller overrides them explicitly.
    if args.lang_id_arg:
        cmd.extend(["--lang_id", args.language])

    override_map = {
        "--num_step": args.num_step,
        "--guidance_scale": args.guidance_scale,
        "--t_shift": args.t_shift,
        "--position_temperature": args.position_temperature,
        "--class_temperature": args.class_temperature,
        "--layer_penalty_factor": args.layer_penalty_factor,
        "--audio_chunk_duration": args.audio_chunk_duration,
        "--audio_chunk_threshold": args.audio_chunk_threshold,
        "--batch_duration": args.batch_duration,
        "--batch_size": args.batch_size,
        "--nj_per_gpu": args.nj_per_gpu,
        "--warmup": args.warmup,
    }
    for option, value in override_map.items():
        if value is not None:
            cmd.extend([option, str(value)])

    bool_override_map = {
        "--denoise": args.denoise,
        "--preprocess_prompt": args.preprocess_prompt,
        "--postprocess_output": args.postprocess_output,
    }
    for option, value in bool_override_map.items():
        if value is not None:
            cmd.extend([option, "True" if value else "False"])

    env = None
    if args.omnivoice_no_edge_fade:
        env, shim_dir = omnivoice_no_edge_fade_env(args.omnivoice_bin)
        verify_omnivoice_no_edge_fade(args.omnivoice_bin, env)
        print(f"OmniVoice edge fade disabled via PYTHONPATH shim: {shim_dir}")

    print("Running:", " ".join(cmd))
    subprocess.run(cmd, check=True, env=env)


def omnivoice_no_edge_fade_env(omnivoice_bin):
    shim_dir = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "tools",
        "omnivoice_no_edge_fade",
    )
    env = os.environ.copy()
    env["K2FSA_OMNIVOICE_NO_EDGE_FADE"] = "1"
    env["PYTHONPATH"] = (
        shim_dir
        if not env.get("PYTHONPATH")
        else shim_dir + os.pathsep + env["PYTHONPATH"]
    )
    return env, shim_dir


def python_for_omnivoice_bin(omnivoice_bin):
    bin_dir = os.path.dirname(os.path.abspath(omnivoice_bin))
    candidate = os.path.join(bin_dir, "python")
    return candidate if os.path.exists(candidate) else sys.executable


def verify_omnivoice_no_edge_fade(omnivoice_bin, env):
    check_code = """
import sys
import omnivoice.utils.audio as audio_utils
from omnivoice.models.omnivoice import fade_and_pad_audio as model_fade
ok = (
    audio_utils.fade_and_pad_audio.__name__ == 'no_edge_fade'
    and audio_utils.fade_and_pad_audio.__module__ == 'sitecustomize'
    and model_fade.__name__ == 'no_edge_fade'
    and model_fade.__module__ == 'sitecustomize'
)
print(audio_utils.fade_and_pad_audio.__name__, audio_utils.fade_and_pad_audio.__module__)
print(model_fade.__name__, model_fade.__module__)
raise SystemExit(0 if ok else 2)
"""
    proc = subprocess.run(
        [python_for_omnivoice_bin(omnivoice_bin), "-c", check_code],
        env=env,
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        detail = "\n".join(part for part in (proc.stdout.strip(), proc.stderr.strip()) if part)
        raise RuntimeError(
            "Failed to disable OmniVoice fade_and_pad_audio. "
            f"Self-check output:\n{detail}"
        )


def limit_story_words(text, max_words):
    if max_words is None or max_words <= 0:
        return text, None
    matches = list(re.finditer(r"\S+", text))
    if len(matches) <= max_words:
        return text, len(matches)
    end = matches[max_words - 1].end()
    return text[:end].rstrip(), max_words


def write_normalized_text(path, text, entries):
    chunks_path = path.replace(".txt", "_chunks.txt")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text.rstrip() + "\n")
    with open(chunks_path, "w", encoding="utf-8") as fh:
        for entry in entries:
            fh.write(f"## {entry['id']}\n")
            fh.write(entry["text"].rstrip() + "\n\n")
    return chunks_path


def rms_db(value):
    return 20.0 * math.log10(max(value, 1e-12))


def probe_audio_quality(path, args):
    samples = _decode_samples(path, args.verify_sample_rate)
    if samples is None or len(samples) < 2:
        return None

    count = len(samples)
    duration = count / float(args.verify_sample_rate)
    sumsq = 0.0
    peak = 0.0
    max_jump = 0.0
    diff_sumsq = 0.0
    zero_crossings = 0
    previous = float(samples[0])
    for index, sample in enumerate(samples):
        value = float(sample)
        abs_value = abs(value)
        peak = max(peak, abs_value)
        sumsq += value * value
        if index:
            diff = value - previous
            abs_diff = abs(diff)
            max_jump = max(max_jump, abs_diff)
            diff_sumsq += diff * diff
            if (value >= 0.0) != (previous >= 0.0):
                zero_crossings += 1
        previous = value

    rms = math.sqrt(sumsq / count)
    diff_rms = math.sqrt(diff_sumsq / max(1, count - 1))
    longest_silence = longest_silence_seconds(
        samples, args.verify_sample_rate, args.verify_silence_threshold_db
    )
    impulse = strongest_impulse_window(samples, args)
    return {
        "duration_sec": duration,
        "rms_db": rms_db(rms),
        "peak": peak,
        "peak_db": rms_db(peak),
        "max_sample_jump": max_jump,
        "diff_rms": diff_rms,
        "diff_crest": max_jump / max(diff_rms, 1e-12),
        "zero_crossings_per_sec": zero_crossings / max(duration, 1e-9),
        "longest_silence_sec": longest_silence,
        "impulse": impulse,
    }


def strongest_impulse_window(samples, args):
    sample_rate = args.verify_sample_rate
    window = max(2, int(args.verify_impulse_window_ms * sample_rate / 1000.0))
    hop = max(1, int(args.verify_impulse_hop_ms * sample_rate / 1000.0))
    if len(samples) < window:
        return None

    strongest = None
    for start in range(0, len(samples) - window + 1, hop):
        segment = samples[start:start + window]
        sumsq = 0.0
        diff_sumsq = 0.0
        peak = 0.0
        max_jump = 0.0
        zero_crossings = 0
        previous = float(segment[0])
        for index, sample in enumerate(segment):
            value = float(sample)
            peak = max(peak, abs(value))
            sumsq += value * value
            if index:
                diff = value - previous
                max_jump = max(max_jump, abs(diff))
                diff_sumsq += diff * diff
                if (value >= 0.0) != (previous >= 0.0):
                    zero_crossings += 1
            previous = value
        rms = math.sqrt(sumsq / window)
        diff_rms = math.sqrt(diff_sumsq / max(1, window - 1))
        zcr = zero_crossings / max(window / sample_rate, 1e-9)
        score = max_jump * math.log1p(zcr) * (diff_rms / max(rms, 1e-12))
        row = {
            "start_sec": start / sample_rate,
            "rms_db": rms_db(rms),
            "peak": peak,
            "max_sample_jump": max_jump,
            "diff_rms": diff_rms,
            "diff_crest": max_jump / max(diff_rms, 1e-12),
            "zero_crossings_per_sec": zcr,
            "score": score,
        }
        if strongest is None or row["score"] > strongest["score"]:
            strongest = row
    return strongest


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


def edge_silence_seconds(path, threshold_db, sample_rate):
    samples = _decode_samples(path, sample_rate)
    if samples is None or not len(samples):
        return 0.0, 0.0
    threshold = 10 ** (threshold_db / 20.0)
    leading = 0
    for sample in samples:
        if abs(float(sample)) <= threshold:
            leading += 1
        else:
            break
    trailing = 0
    for sample in reversed(samples):
        if abs(float(sample)) <= threshold:
            trailing += 1
        else:
            break
    return leading / float(sample_rate), trailing / float(sample_rate)


def add_defect(result, kind, severity, message, payload=None):
    defect = {"type": kind, "severity": severity, "message": message}
    if payload:
        defect["payload"] = payload
    result["defects"].append(defect)
    if severity == "hard":
        result["status"] = "fail"


def duplicate_text_defect(expected_text, words, args):
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

    matcher = SequenceMatcherCompat(expected, heard)
    inserted = []
    for tag, _i1, _i2, j1, j2 in matcher.get_opcodes():
        if tag == "insert" and (j2 - j1) >= args.verify_inserted_words:
            inserted.append(" ".join(heard[j1:j2]))
    if inserted:
        return "hard", f"inserted extra words {inserted[0]!r}"
    if repeated_phrase:
        return "warn", repeated_phrase
    return None


class SequenceMatcherCompat:
    def __init__(self, a, b):
        from difflib import SequenceMatcher

        self._matcher = SequenceMatcher(None, a, b)

    def get_opcodes(self):
        return self._matcher.get_opcodes()


def verify_chunk_entry(entry, chunk_dir, args, transcriber=None, asr_available=True):
    path = chunk_path(entry, chunk_dir)
    result = {
        "id": entry["id"],
        "path": path,
        "status": "ok",
        "defects": [],
        "metrics": {},
    }

    stats = probe_chunk_stats(path)
    ok, reason = validate_chunk_audio(
        path, entry["text"], args.verify_expected_speed, stats=stats
    )
    if stats:
        result["metrics"].update(stats)
    if not ok:
        add_defect(result, "basic_audio", "hard", reason)

    quality = probe_audio_quality(path, args)
    if quality is None:
        add_defect(result, "audio_decode", "hard", "could not decode audio samples")
        return result
    result["metrics"].update(quality)

    impulse = quality.get("impulse") or {}
    impulse_jump = impulse.get("max_sample_jump", 0.0)
    impulse_zcr = impulse.get("zero_crossings_per_sec", 0.0)
    if (
        impulse_jump >= args.verify_transient_jump
        and impulse_zcr >= args.verify_transient_zcr
        and impulse.get("rms_db", -120.0) >= args.verify_transient_min_rms_db
    ):
        add_defect(
            result,
            "transient_noise",
            "hard",
            (
                f"impulse-like burst at {impulse['start_sec']:.2f}s "
                f"(jump {impulse_jump:.3f}, zcr {impulse_zcr:.0f}/s)"
            ),
            impulse,
        )

    if quality["peak"] >= args.verify_clip_peak:
        add_defect(
            result,
            "clipping",
            "hard",
            f"peak {quality['peak']:.3f} is near clipping",
        )
    if quality["longest_silence_sec"] >= args.verify_max_internal_silence_sec:
        add_defect(
            result,
            "long_silence",
            "hard",
            f"silence gap {quality['longest_silence_sec']:.2f}s",
        )

    if not args.verify_asr:
        add_defect(result, "asr", "warn", "ASR text/timing scan disabled")
        return result
    if not asr_available:
        add_defect(result, "asr", "warn", "ASR unavailable; text/timing scan skipped")
        return result

    payload_words = transcribe_word_timestamps(
        path, args.verify_asr_model, transcriber=transcriber
    )
    if payload_words is None:
        add_defect(result, "asr", "hard", "ASR failed")
        return result
    _payload, words = payload_words
    result["metrics"]["asr_words"] = len(words)
    score, timing_reason = timing_defects_from_words(
        path,
        entry["text"],
        words,
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
    )
    result["metrics"]["asr_score"] = score
    if timing_reason is None or not str(timing_reason).startswith("ok"):
        add_defect(result, "text_timing", "hard", timing_reason or "ASR timing check failed")
    repeated = duplicate_text_defect(entry["text"], words, args)
    if repeated:
        severity, message = repeated
        add_defect(result, "repetition", severity, message)
    return result


def apply_volume_outlier_checks(results, args):
    db_values = [
        result["metrics"]["rms_db"]
        for result in results
        if isinstance(result.get("metrics", {}).get("rms_db"), (int, float))
    ]
    if len(db_values) < 3:
        return
    median_db = statistics_median(db_values)
    for result in results:
        rms = result.get("metrics", {}).get("rms_db")
        if not isinstance(rms, (int, float)):
            continue
        delta = rms - median_db
        result["metrics"]["run_median_rms_db"] = median_db
        result["metrics"]["run_rms_delta_db"] = delta
        if abs(delta) >= args.verify_volume_hard_db:
            add_defect(
                result,
                "volume_outlier",
                "hard",
                f"chunk RMS {delta:+.1f} dB from run median",
            )
        elif abs(delta) >= args.verify_volume_warn_db:
            add_defect(
                result,
                "volume_outlier",
                "warn",
                f"chunk RMS {delta:+.1f} dB from run median",
            )


def verify_rendered_chunks(entries, chunk_dir, args, output_name):
    if not args.verify_chunks:
        return []

    attempts = []
    asr_available = args.verify_asr and bool(_whisper_bin())
    if args.verify_asr and not asr_available:
        print("Chunk verify: ASR unavailable; running audio-only checks.")

    for attempt in range(args.max_verify_retries + 1):
        print(f"Chunk verify pass {attempt + 1}/{args.max_verify_retries + 1}")
        session_cm = (
            MLXWhisperSession()
            if asr_available and args.verify_reuse_asr_session
            else nullcontext(None)
        )
        with session_cm as transcriber:
            results = [
                verify_chunk_entry(
                    entry,
                    chunk_dir,
                    args,
                    transcriber=transcriber,
                    asr_available=asr_available,
                )
                for entry in entries
            ]
            apply_volume_outlier_checks(results, args)
            failures = [result for result in results if result["status"] == "fail"]
            attempts.append({
                "attempt": attempt,
                "checked": [entry["id"] for entry in entries],
                "failures": [result["id"] for result in failures],
                "results": results,
            })
        print(f"Chunk verify: {len(entries) - len(failures)}/{len(entries)} ok")
        if not failures or attempt >= args.max_verify_retries:
            break

        failed_ids = {result["id"] for result in failures}
        retry_entries = [entry for entry in entries if entry["id"] in failed_ids]
        retry_jsonl = os.path.join(
            chunk_dir,
            f"{output_name}_verify_retry_{attempt + 1}.jsonl",
        )
        write_jsonl(retry_entries, retry_jsonl)
        print(f"Re-rendering {len(retry_entries)} verify-failed chunk(s).")
        run_k2fsa_omnivoice(retry_jsonl, chunk_dir, args)

    return attempts


def write_verify_report(path, attempts):
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(
            {
                "created_at": datetime.now(timezone.utc).isoformat(),
                "attempts": attempts,
            },
            fh,
            ensure_ascii=False,
            indent=2,
        )


def terminal_mark(text):
    stripped = text.rstrip()
    while stripped and stripped[-1] in "\"'”’)]}":
        stripped = stripped[:-1].rstrip()
    return stripped[-1] if stripped else ""


def is_dialogueish(text):
    stripped = text.strip()
    return stripped.startswith(('"', "“", "'")) or stripped.endswith(('"', "”", "'"))


def target_pause_ms(prev_entry, next_entry, args):
    mark = terminal_mark(prev_entry["text"])
    target = args.stitch_base_pause_ms
    if mark == ".":
        target = max(target, args.stitch_sentence_pause_ms)
    elif mark in "?!…":
        target = max(target, args.stitch_expressive_pause_ms)
    if "\n\n" in prev_entry["text"] or "\n\n" in next_entry["text"]:
        target = max(target, args.stitch_paragraph_pause_ms)
    if is_dialogueish(prev_entry["text"]) or is_dialogueish(next_entry["text"]):
        target = max(target, args.stitch_dialogue_pause_ms)
    return target


def write_silence(path, seconds, sample_rate):
    subprocess.run(
        [
            "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
            "-f", "lavfi", "-i", f"anullsrc=r={sample_rate}:cl=mono",
            "-t", f"{seconds:.3f}",
            "-c:a", "pcm_f32le",
            path,
        ],
        check=True,
    )


def prepare_stitch_pause_files(entries, audio_paths, chunk_dir, args, output_name):
    if not args.stitch_pause or len(audio_paths) < 2:
        return audio_paths, []

    stitch_dir = os.path.join(chunk_dir, ".stitch_pause")
    os.makedirs(stitch_dir, exist_ok=True)
    stitched = []
    report = []
    for index, path in enumerate(audio_paths):
        stitched.append(path)
        if index >= len(audio_paths) - 1:
            continue

        next_path = audio_paths[index + 1]
        _lead_prev, trailing_prev = edge_silence_seconds(
            path, args.stitch_silence_threshold_db, args.stitch_sample_rate
        )
        leading_next, _trail_next = edge_silence_seconds(
            next_path, args.stitch_silence_threshold_db, args.stitch_sample_rate
        )
        target_ms = target_pause_ms(entries[index], entries[index + 1], args)
        existing_ms = (trailing_prev + leading_next) * 1000.0
        add_ms = max(0.0, target_ms - existing_ms)
        row = {
            "after": entries[index]["id"],
            "before": entries[index + 1]["id"],
            "target_ms": target_ms,
            "existing_ms": existing_ms,
            "added_ms": 0.0,
        }
        if add_ms >= args.stitch_min_add_pause_ms:
            silence_path = os.path.join(
                stitch_dir,
                f"{output_name}_pause_{index + 1:04d}_{index + 2:04d}.wav",
            )
            write_silence(silence_path, add_ms / 1000.0, args.stitch_sample_rate)
            stitched.append(silence_path)
            row["added_ms"] = add_ms
            row["path"] = silence_path
        report.append(row)
    return stitched, report


def write_stitch_report(path, rows):
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(
            {
                "created_at": datetime.now(timezone.utc).isoformat(),
                "boundaries": rows,
            },
            fh,
            ensure_ascii=False,
            indent=2,
        )


def build_parser():
    parser = argparse.ArgumentParser(
        description="Convert a Markdown story to audio with k2-fsa/OmniVoice."
    )
    parser.add_argument("--input", "-i", required=True, help="Input Markdown file")
    parser.add_argument("--output_dir", "-o", default="results", help="Output directory")
    parser.add_argument("--model", default="k2-fsa/OmniVoice", help="HF model id or local checkpoint")
    parser.add_argument("--language", "-l", default="vi", help="Language ID for JSONL entries")
    parser.add_argument("--voice_name", default=DEFAULT_VOICE_NAME, help="Clone profile name")
    parser.add_argument("--ref_audio", default=DEFAULT_REF_AUDIO, help="Reference WAV for cloning")
    parser.add_argument("--ref_text", default=None, help="Reference transcript override")
    parser.add_argument(
        "--auto_ref_text",
        action="store_true",
        help="Omit ref_text and let k2-fsa OmniVoice auto-transcribe the reference.",
    )
    parser.add_argument("--omnivoice_bin", default=None, help="Path to omnivoice-infer-batch")
    parser.add_argument(
        "--lang_id_arg",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="Also pass --lang_id to the batch CLI. JSONL entries already contain language_id.",
    )
    parser.add_argument("--max_chunk_chars", type=int, default=420)
    parser.add_argument("--max_chunk_words", type=int, default=60)
    parser.add_argument("--pron_dict", default=None, help="JSON pronunciation override dictionary")
    parser.add_argument(
        "--normalize",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Reuse the repository Vietnamese TTS normalization before chunking.",
    )
    parser.add_argument(
        "--resume",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Skip chunk WAVs already present. Enabled by default for long Mac runs.",
    )
    parser.add_argument("--keep_chunks", action="store_true", help="Keep chunk WAVs after concat")
    parser.add_argument("--dry_run", action="store_true", help="Write JSONL/profile only")
    parser.add_argument("--limit", type=int, default=None, help="Render only the first N chunks")
    parser.add_argument("--only", default=None, help="Render comma-separated chunk numbers/ids")
    parser.add_argument(
        "--story_word_limit",
        type=int,
        default=None,
        help="Render only the first N whitespace-delimited words of the cleaned story.",
    )
    parser.add_argument(
        "--omnivoice_no_edge_fade",
        action=argparse.BooleanOptionalAction,
        default=True,
        help=(
            "Disable OmniVoice's hard-coded output fade/pad while rendering chunks "
            "by loading a local PYTHONPATH shim. Existing resumed chunks are not changed."
        ),
    )
    parser.add_argument(
        "--verify_chunks",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Verify rendered chunks for audio artifacts, text loss/repetition, timing, and volume.",
    )
    parser.add_argument("--max_verify_retries", type=int, default=1)
    parser.add_argument(
        "--allow_verify_failures",
        action="store_true",
        help="Publish/concat even when chunk verification still has hard failures.",
    )
    parser.add_argument("--verify_expected_speed", type=float, default=1.0)
    parser.add_argument("--verify_sample_rate", type=int, default=24000)
    parser.add_argument("--verify_silence_threshold_db", type=float, default=-45.0)
    parser.add_argument("--verify_max_internal_silence_sec", type=float, default=1.8)
    parser.add_argument("--verify_clip_peak", type=float, default=0.98)
    parser.add_argument("--verify_transient_jump", type=float, default=0.22)
    parser.add_argument("--verify_transient_zcr", type=float, default=9000.0)
    parser.add_argument("--verify_transient_min_rms_db", type=float, default=-44.0)
    parser.add_argument("--verify_impulse_window_ms", type=float, default=30.0)
    parser.add_argument("--verify_impulse_hop_ms", type=float, default=10.0)
    parser.add_argument("--verify_volume_warn_db", type=float, default=4.0)
    parser.add_argument("--verify_volume_hard_db", type=float, default=7.0)
    parser.add_argument(
        "--verify_asr",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Use MLX Whisper word timestamps for text/timing verification when available.",
    )
    parser.add_argument("--verify_asr_model", default=DEFAULT_ASR_MODEL)
    parser.add_argument("--verify_reuse_asr_session", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--verify_similarity_floor", type=float, default=0.94)
    parser.add_argument("--verify_adaptive_floor", type=float, default=0.985)
    parser.add_argument("--verify_word_probability_floor", type=float, default=0.78)
    parser.add_argument("--verify_word_duration_ratio", type=float, default=2.4)
    parser.add_argument("--verify_min_local_wps", type=float, default=1.6)
    parser.add_argument("--verify_max_local_wps", type=float, default=9.0)
    parser.add_argument("--verify_dropped_words", type=int, default=4)
    parser.add_argument("--verify_drag_ratio", type=float, default=6.0)
    parser.add_argument("--verify_swallow_db", type=float, default=DEFAULT_FAST_SWALLOW_DB)
    parser.add_argument("--verify_inserted_words", type=int, default=3)
    parser.add_argument("--verify_repeat_max_ngram", type=int, default=4)
    parser.add_argument(
        "--stitch_pause",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Insert only the missing silence between chunks before final concat.",
    )
    parser.add_argument("--stitch_sample_rate", type=int, default=24000)
    parser.add_argument("--stitch_silence_threshold_db", type=float, default=-45.0)
    parser.add_argument("--stitch_base_pause_ms", type=float, default=260.0)
    parser.add_argument("--stitch_sentence_pause_ms", type=float, default=340.0)
    parser.add_argument("--stitch_expressive_pause_ms", type=float, default=420.0)
    parser.add_argument("--stitch_paragraph_pause_ms", type=float, default=520.0)
    parser.add_argument("--stitch_dialogue_pause_ms", type=float, default=460.0)
    parser.add_argument("--stitch_min_add_pause_ms", type=float, default=25.0)
    parser.add_argument(
        "--runtime_preset",
        choices=("mac_safe", "upstream_defaults"),
        default="mac_safe",
        help=(
            "mac_safe is the default for Mac M1/16GB: batch_size=1, "
            "nj_per_gpu=1, warmup=0. upstream_defaults omits those overrides "
            "and lets k2-fsa batch aggressively."
        ),
    )

    # Optional generation overrides.  Leave unset to use k2-fsa defaults.
    parser.add_argument("--num_step", type=int, default=None)
    parser.add_argument("--guidance_scale", type=float, default=None)
    parser.add_argument("--t_shift", type=float, default=None)
    parser.add_argument("--position_temperature", type=float, default=None)
    parser.add_argument("--class_temperature", type=float, default=None)
    parser.add_argument("--layer_penalty_factor", type=float, default=None)
    parser.add_argument("--audio_chunk_duration", type=float, default=None)
    parser.add_argument("--audio_chunk_threshold", type=float, default=None)
    parser.add_argument("--batch_duration", type=float, default=None)
    parser.add_argument("--batch_size", type=int, default=None)
    parser.add_argument("--nj_per_gpu", type=int, default=None)
    parser.add_argument("--warmup", type=int, default=None)
    parser.add_argument("--denoise", type=lambda x: x.lower() == "true", default=None)
    parser.add_argument("--preprocess_prompt", type=lambda x: x.lower() == "true", default=None)
    parser.add_argument("--postprocess_output", type=lambda x: x.lower() == "true", default=None)
    return parser


def main():
    args = build_parser().parse_args()
    apply_runtime_preset(args)
    args.omnivoice_bin = find_omnivoice_bin(args.omnivoice_bin)
    if not args.omnivoice_bin:
        print("Error: omnivoice-infer-batch not found.", file=sys.stderr)
        return 1
    if not os.path.exists(args.input):
        print(f"Error: input not found: {args.input}", file=sys.stderr)
        return 1
    if not os.path.exists(args.ref_audio):
        print(f"Error: reference audio not found: {args.ref_audio}", file=sys.stderr)
        return 1

    ref_text = args.ref_text
    if args.auto_ref_text:
        ref_text = None
    elif ref_text is None:
        ref_text = KNOWN_VOICE_REFTEXT.get(args.voice_name)

    os.makedirs(args.output_dir, exist_ok=True)
    base_name = Path(args.input).stem
    word_limit_suffix = (
        f"_first_{args.story_word_limit}_words"
        if args.story_word_limit is not None and args.story_word_limit > 0
        else ""
    )
    output_name = f"{base_name}{word_limit_suffix}_k2fsa_{slugify(args.voice_name)}"
    chunk_dir = os.path.join(args.output_dir, f"{output_name}_chunks")
    os.makedirs(chunk_dir, exist_ok=True)

    with open(args.input, "r", encoding="utf-8") as fh:
        clean_text = clean_markdown(fh.read())
    if not clean_text:
        print("Error: extracted text is empty.", file=sys.stderr)
        return 1
    clean_text, rendered_word_count = limit_story_words(clean_text, args.story_word_limit)

    tts_text = clean_text
    if args.normalize:
        pron_dict = dict(DEFAULT_PRON_DICT)
        if args.pron_dict:
            with open(args.pron_dict, "r", encoding="utf-8") as fh:
                pron_dict.update(json.load(fh))
        tts_text = normalize_for_tts(tts_text, pron_dict)

    chunks = split_text_into_chunks(tts_text, args.max_chunk_chars, args.max_chunk_words)
    all_entries = []
    for index, chunk in enumerate(chunks, start=1):
        entry = {
            "id": f"{output_name}_{index:04d}",
            "text": chunk,
            "language_id": args.language,
            "ref_audio": os.path.abspath(args.ref_audio),
        }
        if ref_text is not None:
            entry["ref_text"] = ref_text
        all_entries.append(entry)

    selected_entries = select_entries(all_entries, args.limit, args.only)
    if not selected_entries:
        print("Error: selected zero chunks.", file=sys.stderr)
        return 1

    subset = args.limit is not None or args.only is not None
    if args.resume:
        done = existing_good_wavs(selected_entries, chunk_dir)
        render_entries = [entry for entry in selected_entries if entry["id"] not in done]
        if done and args.omnivoice_no_edge_fade:
            print(
                "Resume warning: existing chunk WAVs will be reused. "
                "The no-edge-fade self-check only applies before newly rendered chunks. "
                "Use --no-resume if you need to regenerate every chunk with fade_and_pad_audio disabled."
            )
    else:
        render_entries = selected_entries

    plan_jsonl_name = f"{output_name}{'_subset' if subset else ''}.jsonl"
    plan_jsonl_path = os.path.join(chunk_dir, plan_jsonl_name)
    write_jsonl(selected_entries, plan_jsonl_path)
    render_jsonl_path = os.path.join(chunk_dir, f"{output_name}_render.jsonl")
    write_jsonl(render_entries, render_jsonl_path)
    voice_profile_path = os.path.join(chunk_dir, f"{slugify(args.voice_name)}.voice.json")
    write_voice_profile(voice_profile_path, args, ref_text)
    normalized_text_path = os.path.join(chunk_dir, f"{output_name}_normalized.txt")
    normalized_chunks_path = write_normalized_text(normalized_text_path, tts_text, selected_entries)

    print(f"Voice clone: {args.voice_name}")
    print(f"  ref_audio: {os.path.abspath(args.ref_audio)}")
    print(f"  ref_text : {'auto-ASR by OmniVoice' if ref_text is None else '<set>'}")
    if rendered_word_count is not None:
        print(f"Story word limit: first {rendered_word_count} word(s)")
    print(f"Text length: {len(tts_text)} chars")
    print(f"Chunks: {len(chunks)} total, {len(selected_entries)} selected")
    print(f"Plan JSONL: {plan_jsonl_path}")
    print(f"Render JSONL: {render_jsonl_path}")
    print(f"Voice profile: {voice_profile_path}")
    print(f"Normalized text: {normalized_text_path}")
    print(f"Normalized chunks: {normalized_chunks_path}")
    print(f"Runtime settings: {json.dumps(runtime_settings(args), ensure_ascii=False)}")

    if args.dry_run:
        for entry in selected_entries:
            preview = entry["text"][:90].replace("\n", " ")
            suffix = "..." if len(entry["text"]) > 90 else ""
            print(f"{entry['id']}: {len(entry['text'])} chars | {preview}{suffix}")
        return 0

    if render_entries:
        try:
            run_k2fsa_omnivoice(render_jsonl_path, chunk_dir, args)
        except KeyboardInterrupt:
            print("\nInterrupted. Already-rendered chunk WAVs are kept; rerun with --resume.")
            return 130
    else:
        print("Resume: all selected chunks already exist; skipping render.")

    missing = [path for path in expected_chunk_paths(selected_entries, chunk_dir) if not os.path.exists(path)]
    if missing:
        print("Error: missing rendered chunks:", file=sys.stderr)
        for path in missing[:10]:
            print(f"  {path}", file=sys.stderr)
        return 1

    verify_report_path = os.path.join(args.output_dir, f"{output_name}_chunk_verify.json")
    verify_attempts = verify_rendered_chunks(selected_entries, chunk_dir, args, output_name)
    if verify_attempts:
        write_verify_report(verify_report_path, verify_attempts)
        print(f"Chunk verify report: {verify_report_path}")
        final_failures = verify_attempts[-1].get("failures", [])
        if final_failures and not args.allow_verify_failures:
            print(
                f"Error: {len(final_failures)} chunk(s) still failed verification; "
                "not publishing final WAV. Use --allow_verify_failures to concat anyway.",
                file=sys.stderr,
            )
            return 1

    if subset:
        print("Subset render complete; skipping final concatenation.")
        return 0

    output_path = os.path.join(args.output_dir, f"{output_name}.wav")
    audio_paths = expected_chunk_paths(selected_entries, chunk_dir)
    stitch_paths, stitch_rows = prepare_stitch_pause_files(
        selected_entries,
        audio_paths,
        chunk_dir,
        args,
        output_name,
    )
    if stitch_rows:
        stitch_report_path = os.path.join(args.output_dir, f"{output_name}_stitch_pause.json")
        write_stitch_report(stitch_report_path, stitch_rows)
        added = sum(row["added_ms"] for row in stitch_rows)
        print(f"Stitch pause report: {stitch_report_path} ({added:.0f} ms added)")
    concatenate_audio_files(stitch_paths, output_path, chunk_dir)
    print(f"Final audio: {output_path}")

    if not args.keep_chunks:
        print(f"Chunk WAVs kept in: {chunk_dir}")
    return 0


def slugify(value):
    value = value.lower().strip()
    value = re.sub(r"[^a-z0-9]+", "_", value)
    return value.strip("_") or "voice"


if __name__ == "__main__":
    raise SystemExit(main())
