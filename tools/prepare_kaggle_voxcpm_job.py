#!/usr/bin/env python3
"""Prepare a self-contained Kaggle kernel folder for VoxCPM2 rendering.

The job attaches a Kaggle Dataset cache for VoxCPM2 plus QC model snapshots
when available, while keeping internet enabled as a fallback for Python
packages or a missing cache. The story Markdown and selected reference WAV ride
inside the embedded bundle.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import math
import shutil
import subprocess
import sys
import tarfile
from array import array
from datetime import datetime, timezone
from io import BytesIO
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from voxcpm_ctc_probe import DEFAULT_CTC_MODEL  # noqa: E402

DEFAULT_VOICE_KEY = "ngoc_huyen"
DEFAULT_MODEL_DATASET_SOURCE = "ah470346/voxcpm2-snapshot"
VOICE_PRESETS = {
    "ngoc_huyen": {
        "voice_name": "NGOC HUYEN V2",
        "ref_audio": "voice_samples/ngoc_huyen_moi_ref_clone_tu_nhien.wav",
    },
    "adam": {
        "voice_name": "ADAM",
        "ref_audio": "voice_samples/adam_dominant_firm_ref_10p795_18p857.wav",
    },
    "thuy_nguyen": {
        "voice_name": "THUY NGUYEN",
        "ref_audio": "voice_samples/download_no_bgm_full_sentence_123p73_129p82_voxcpm.wav",
    },
}
COPY_FILES = [
    "convert_script_to_audio_voxcpm.py",
    "voxcpm_story_core.py",
    "voxcpm_ctc_probe.py",
]
# Pinned so a Kaggle rerun renders the same audio as the run it is compared
# against. voxcpm pulls torch/torchaudio/librosa itself; Kaggle already ships a
# CUDA torch, so it is deliberately not pinned here. faster-whisper (ASR verify)
# and resemblyzer (speaker-similarity verify) are the two QC dependencies
# convert_script_to_audio_voxcpm.py imports from voxcpm_story_core / defines
# locally. These are optional at import time but required whenever their
# matching verify defaults are in effect.
#
# Deliberately NOT whisperx. It pins faster-whisper==1.0.0 and
# ctranslate2==4.4.0, which contradict the faster-whisper pin above, so a
# single `pip install` of both fails to resolve and takes the whole kernel down
# before the first chunk renders. It also drags in pyannote.audio==3.1.1. The
# CTC probe (voxcpm_ctc_probe.py) needs only torch + transformers, both of
# which voxcpm already installs.
DEFAULT_PIP_PACKAGES = [
    "faster-whisper==1.2.1",
    "resemblyzer==0.1.4",
]
# voxcpm's declared deps (gradio, modelscope, datasets, funasr, spaces,
# argbind, wetext, addict) are its gradio-demo/training extras, never
# imported by the render path this pipeline uses (VoxCPM.from_pretrained /
# .generate only touches torch/torchaudio/transformers/librosa/safetensors/
# einops/pydantic, all already on Kaggle's base image). Installed with
# --no-deps in the launcher so those ~150MB of unused packages are never
# pulled down.
DEFAULT_PIP_PACKAGES_NO_DEPS = [
    "voxcpm==2.0.3",
]


def build_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("--kernel-id", required=True, help="Kaggle kernel id, e.g. username/slug")
    parser.add_argument("--title", required=True, help="Kaggle kernel title")
    parser.add_argument("--job-dir", required=True, help="Folder to push with kaggle kernels push")
    parser.add_argument("--input", required=True, help="Story markdown path")
    parser.add_argument("--voice", choices=sorted(VOICE_PRESETS), default=DEFAULT_VOICE_KEY)
    parser.add_argument("--voice-name", default=None, help="Override the clone profile label")
    parser.add_argument("--ref-audio", default=None, help="Override the reference WAV")
    parser.add_argument("--ref-text", default=None, help="Override the reference transcript")
    parser.add_argument("--model", default="openbmb/VoxCPM2")
    parser.add_argument("--clone-mode", choices=("ultimate", "reference"), default="ultimate")

    parser.add_argument("--story-word-limit", type=int, default=None)
    parser.add_argument("--max-chunk-chars", type=int, default=120)
    parser.add_argument("--max-chunk-words", type=int, default=26)
    parser.add_argument("--min-chunk-words", type=int, default=8)

    parser.add_argument("--cfg-value", type=float, default=1.5)
    parser.add_argument("--inference-timesteps", type=int, default=10)
    parser.add_argument("--seed", type=int, default=20260719)
    parser.add_argument("--retry-badcase", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--optimize", action=argparse.BooleanOptionalAction, default=False)
    parser.add_argument("--denoise", action=argparse.BooleanOptionalAction, default=False)
    parser.add_argument(
        "--render-workers",
        default="auto",
        help="Parallel chunk render workers passed to VoxCPM renderer. 'auto' uses all visible CUDA GPUs.",
    )
    parser.add_argument(
        "--render-devices",
        default=None,
        help="Comma-separated CUDA device indexes for parallel render, e.g. 0,1.",
    )
    parser.add_argument("--resume", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument(
        "--verify-chunks",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Master switch for ASR/speaker verify + escalation ladder + subsplit recovery.",
    )
    parser.add_argument("--verify-asr", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--verify-asr-model", default="large-v3-turbo")
    parser.add_argument("--verify-speaker-severity", choices=("hard", "warn", "off"), default="warn")
    parser.add_argument("--verify-ctc-probe", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--verify-ctc-model", default=DEFAULT_CTC_MODEL)
    parser.add_argument("--max-verify-retries", type=int, default=3)
    parser.add_argument("--verify-subsplit", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--master", action=argparse.BooleanOptionalAction, default=True)

    parser.add_argument(
        "--profile-gpu",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="Sample nvidia-smi utilization/memory every 2s during render into "
        "gpu_util.csv, packaged in the output zip. For the Cách-3 question: "
        "is the GPU idle enough during single-worker render to justify a "
        "shared-QC multi-worker/GPU layout? Off by default; negligible "
        "overhead when on.",
    )
    parser.add_argument("--private", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--enable-internet", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--machine-shape", default="NvidiaTeslaT4")
    parser.add_argument("--dataset-source", action="append", default=[DEFAULT_MODEL_DATASET_SOURCE])
    parser.add_argument("--pip-package", action="append", default=[])
    return parser


def resolve_voice_args(args):
    preset = VOICE_PRESETS[args.voice]
    if args.voice_name is None:
        args.voice_name = preset["voice_name"]
    if args.ref_audio is None:
        args.ref_audio = str(ROOT / preset["ref_audio"])


def write_json(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def sha256_file(path):
    digest = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def check_reference_audio(path):
    """Fail fast when a voice-clone reference is unsuitable.

    VoxCPM reference quality is load-bearing: issue #244 traces start-of-audio
    distortion to a reference that does not end cleanly, and issue #281's answer
    to cross-chunk voice drift is 'use a longer reference audio'.
    """
    path = Path(path).expanduser().resolve()
    if not path.is_file():
        raise SystemExit(f"Reference audio not found: {path}")
    try:
        probe = subprocess.run(
            [
                "ffprobe", "-v", "error", "-select_streams", "a:0",
                "-show_entries", "stream=sample_rate,channels,duration:format=duration",
                "-of", "json", str(path),
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        payload = json.loads(probe.stdout)
        stream = (payload.get("streams") or [{}])[0]
        duration = float(stream.get("duration") or payload.get("format", {}).get("duration") or 0.0)
        sample_rate = int(stream.get("sample_rate") or 0)
        channels = int(stream.get("channels") or 0)
        decoded = subprocess.run(
            ["ffmpeg", "-v", "error", "-i", str(path), "-map", "0:a:0", "-ac", "1",
             "-f", "f32le", "pipe:1"],
            check=True,
            capture_output=True,
        ).stdout
        samples = array("f")
        samples.frombytes(decoded)
    except (OSError, subprocess.CalledProcessError, ValueError, json.JSONDecodeError) as exc:
        raise SystemExit(f"Reference audio could not be decoded: {path}: {exc}") from exc
    if not samples:
        raise SystemExit(f"Reference audio contains no decodable samples: {path}")

    peak = max(abs(float(sample)) for sample in samples)
    rms = math.sqrt(sum(float(sample) ** 2 for sample in samples) / len(samples))
    rms_dbfs = 20.0 * math.log10(max(rms, 1e-12))
    silence_threshold = 10 ** (-50.0 / 20.0)
    silence_ratio = sum(abs(float(sample)) <= silence_threshold for sample in samples) / len(samples)
    # Trailing silence matters on its own: a reference clipped mid-word is the
    # #244 distortion trigger, while a long dead tail wastes prompt context.
    tail_silence = 0
    for sample in reversed(samples):
        if abs(float(sample)) > silence_threshold:
            break
        tail_silence += 1
    tail_silence_sec = tail_silence / sample_rate if sample_rate else 0.0

    problems = []
    if not 3.0 <= duration <= 30.0:
        problems.append(f"duration {duration:.2f}s is outside 3-30s")
    if channels != 1:
        problems.append(f"channels={channels}, expected mono")
    if sample_rate < 16000:
        problems.append(f"sample_rate={sample_rate}, expected >=16000")
    if peak >= 0.98:
        problems.append(f"peak={peak:.4f}, expected <0.98 (not clipped)")
    if silence_ratio >= 0.40:
        problems.append(f"silence_ratio={silence_ratio:.1%}, expected <40%")
    if rms_dbfs < -35.0:
        problems.append(f"RMS={rms_dbfs:.1f} dBFS, expected >=-35 dBFS")
    if problems:
        raise SystemExit(f"Reference audio failed QC: {path}: " + "; ".join(problems))
    return {
        "path": str(path),
        "duration_sec": round(duration, 4),
        "channels": channels,
        "sample_rate": sample_rate,
        "peak": round(peak, 6),
        "silence_ratio": round(silence_ratio, 6),
        "tail_silence_sec": round(tail_silence_sec, 4),
        "rms_dbfs": round(rms_dbfs, 3),
        "sha256": sha256_file(path),
    }


def build_bundle_bytes(job_dir, rel_paths):
    def should_skip(path):
        return "__pycache__" in path.parts or path.suffix in {".pyc", ".pyo"}

    buf = BytesIO()
    with tarfile.open(fileobj=buf, mode="w:gz") as tf:
        for rel_path in rel_paths:
            src = job_dir / rel_path
            if src.is_dir():
                for child in sorted(src.rglob("*")):
                    if child.is_file() and not should_skip(child.relative_to(job_dir)):
                        tf.add(child, arcname=str(child.relative_to(job_dir)))
            elif src.is_file() and not should_skip(Path(rel_path)):
                tf.add(src, arcname=rel_path)
    return buf.getvalue()


def write_embedded_kaggle_entry(job_dir, bundle_bytes, code_file):
    template = (ROOT / "convert_script_to_audio_voxcpm_kaggle.py").read_text(encoding="utf-8")
    bundle_b64 = base64.b64encode(bundle_bytes).decode("ascii")
    bundle_sha = hashlib.sha256(bundle_bytes).hexdigest()
    rendered = template.replace(
        "EMBEDDED_BUNDLE_B64 = None",
        f"EMBEDDED_BUNDLE_B64 = {json.dumps(bundle_b64)}",
        1,
    ).replace(
        "EMBEDDED_BUNDLE_SHA256 = None",
        f"EMBEDDED_BUNDLE_SHA256 = {json.dumps(bundle_sha)}",
        1,
    )
    (job_dir / code_file).write_text(rendered, encoding="utf-8")
    return bundle_sha


def git_build_identity():
    def run_git(*parts):
        proc = subprocess.run(
            ["git", *parts], cwd=ROOT, capture_output=True, text=True, check=False
        )
        return proc.stdout.strip() if proc.returncode == 0 else None

    status = run_git("status", "--porcelain")
    return {"commit": run_git("rev-parse", "HEAD"), "dirty": bool(status)}


def build_info_payload(job_dir, ref_audio, pip_packages, bundle_sha=None):
    tracked = [*COPY_FILES, "render_job.json"]
    return {
        "schema_version": 1,
        "engine": "voxcpm",
        "built_at": datetime.now(timezone.utc).isoformat(),
        "git": git_build_identity(),
        "files_sha256": {
            rel: sha256_file(job_dir / rel) for rel in tracked if (job_dir / rel).is_file()
        },
        "reference_audio_sha256": sha256_file(ref_audio),
        "pip_packages": list(pip_packages),
        "EMBEDDED_BUNDLE_SHA256": bundle_sha or "set-by-launcher-after-extraction",
    }


def kernel_metadata(args, code_file):
    payload = {
        "id": args.kernel_id,
        "title": args.title,
        "code_file": code_file,
        "language": "python",
        "kernel_type": "script",
        "is_private": "true" if args.private else "false",
        "enable_gpu": "true",
        "enable_tpu": "false",
        "enable_internet": "true" if args.enable_internet else "false",
    }
    if args.dataset_source:
        payload["dataset_sources"] = list(args.dataset_source)
    if args.machine_shape:
        payload["machine_shape"] = args.machine_shape
    return payload


def preserve_existing_kernel_identity(path, payload):
    if not path.exists():
        return payload
    try:
        existing = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return payload
    merged = dict(payload)
    for key in ("id_no", "keywords", "kernel_sources", "competition_sources",
                "model_sources", "docker_image"):
        if key in existing:
            merged[key] = existing[key]
    return merged


def render_args(args, input_rel, ref_rel):
    argv = [
        "--input", input_rel,
        "--output_dir", "results",
        "--model", args.model,
        "--voice_name", args.voice_name,
        "--ref_audio", ref_rel,
        "--clone_mode", args.clone_mode,
        "--max_chunk_chars", str(args.max_chunk_chars),
        "--max_chunk_words", str(args.max_chunk_words),
        "--min_chunk_words", str(args.min_chunk_words),
        "--cfg_value", str(args.cfg_value),
        "--inference_timesteps", str(args.inference_timesteps),
        "--seed", str(args.seed),
        "--render_workers", str(args.render_workers),
        "--verify_asr_model", args.verify_asr_model,
        "--verify_speaker_severity", args.verify_speaker_severity,
        "--max_verify_retries", str(args.max_verify_retries),
    ]
    argv.append("--verify_ctc_probe" if args.verify_ctc_probe else "--no-verify_ctc_probe")
    argv += ["--verify_ctc_model", args.verify_ctc_model]
    if args.render_devices:
        argv += ["--render_devices", args.render_devices]
    if args.ref_text:
        argv += ["--ref_text", args.ref_text]
    if args.story_word_limit:
        argv += ["--story_word_limit", str(args.story_word_limit)]
    argv.append("--retry_badcase" if args.retry_badcase else "--no-retry_badcase")
    argv.append("--optimize" if args.optimize else "--no-optimize")
    argv.append("--denoise" if args.denoise else "--no-denoise")
    argv.append("--resume" if args.resume else "--no-resume")
    argv.append("--verify_chunks" if args.verify_chunks else "--no-verify_chunks")
    argv.append("--verify_asr" if args.verify_asr else "--no-verify_asr")
    argv.append("--verify_subsplit" if args.verify_subsplit else "--no-verify_subsplit")
    argv.append("--master" if args.master else "--no-master")
    return argv


def main():
    args = build_parser().parse_args()
    resolve_voice_args(args)
    reference_qc = check_reference_audio(args.ref_audio)

    job_dir = Path(args.job_dir).resolve()
    job_dir.mkdir(parents=True, exist_ok=True)
    for rel_path in COPY_FILES:
        dst = job_dir / rel_path
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / rel_path, dst)

    input_name = Path(args.input).name
    ref_name = Path(args.ref_audio).name
    (job_dir / "job_inputs").mkdir(parents=True, exist_ok=True)
    shutil.copy2(Path(args.input).resolve(), job_dir / "job_inputs" / input_name)
    shutil.copy2(Path(args.ref_audio).resolve(), job_dir / "job_inputs" / ref_name)
    input_rel = f"job_inputs/{input_name}"
    ref_rel = f"job_inputs/{ref_name}"
    env_path = ROOT / ".env"
    if env_path.is_file():
        shutil.copy2(env_path, job_dir / ".env")

    pip_packages = list(DEFAULT_PIP_PACKAGES) + list(args.pip_package)
    pip_packages_no_deps = list(DEFAULT_PIP_PACKAGES_NO_DEPS)
    all_pip_packages = pip_packages_no_deps + pip_packages
    output_stem = Path(args.input).stem
    if args.story_word_limit:
        output_stem = f"{output_stem}_first_{args.story_word_limit}_words"
    zip_paths = ["results", "kaggle_render.log", "build_info.json"]
    if args.profile_gpu:
        zip_paths.append("gpu_util.csv")
    manifest = {
        "engine": "voxcpm",
        "pip_packages": pip_packages,
        "pip_packages_no_deps": pip_packages_no_deps,
        "model_id": args.model,
        "ctc_model_id": args.verify_ctc_model if args.verify_ctc_probe else None,
        "render_args": render_args(args, input_rel, ref_rel),
        "render_script": "convert_script_to_audio_voxcpm.py",
        "zip_name": f"{output_stem}_voxcpm_kaggle_output.zip",
        "zip_paths": zip_paths,
        "profile_gpu": args.profile_gpu,
        "reference_audio_qc": reference_qc,
    }
    write_json(job_dir / "render_job.json", manifest)
    write_json(
        job_dir / "build_info.json",
        build_info_payload(job_dir, args.ref_audio, all_pip_packages),
    )

    code_file = "convert_script_to_audio_voxcpm_kaggle.py"
    metadata_path = job_dir / "kernel-metadata.json"
    metadata = preserve_existing_kernel_identity(metadata_path, kernel_metadata(args, code_file))
    write_json(metadata_path, metadata)

    bundle_paths = [*COPY_FILES, "job_inputs", "render_job.json", "build_info.json", ".env"]
    bundle_bytes = build_bundle_bytes(job_dir, bundle_paths)
    bundle_sha = write_embedded_kaggle_entry(job_dir, bundle_bytes, code_file=metadata["code_file"])
    # Keep the source-side artifact exact too; the launcher writes this same
    # value into the extracted copy, since a tarball cannot contain its own digest.
    write_json(
        job_dir / "build_info.json",
        build_info_payload(job_dir, args.ref_audio, all_pip_packages, bundle_sha=bundle_sha),
    )

    print(f"Prepared Kaggle job folder: {job_dir}")
    print(f"Kernel id      : {args.kernel_id}")
    print(f"Voice          : {args.voice_name} ({args.clone_mode} cloning)")
    print(f"Reference      : {reference_qc['duration_sec']}s @ {reference_qc['sample_rate']} Hz, "
          f"tail silence {reference_qc['tail_silence_sec']}s")
    print(f"Bundle sha256  : {bundle_sha}")
    print(f"Push with: kaggle kernels push -p {job_dir} --accelerator {args.machine_shape}")


if __name__ == "__main__":
    main()
