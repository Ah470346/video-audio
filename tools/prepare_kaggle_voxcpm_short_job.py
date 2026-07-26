#!/usr/bin/env python3
"""Prepare a gate-validated Kaggle VoxCPM2 job for short expressive scripts."""

from __future__ import annotations

import argparse
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from tools import prepare_kaggle_voxcpm_job as base  # noqa: E402


DEFAULT_KERNEL_ID = "ah470346/voxcpm-vn-short-expressive-render"
DEFAULT_TITLE = "VoxCPM VN Short Expressive Render"
DEFAULT_CONTROL = (
    "expressive Vietnamese dramatic short-form narration, emotional emphasis, "
    "natural pauses, clear articulation"
)
COPY_FILES = [
    "convert_short_script_to_audio_voxcpm.py",
    "convert_script_to_audio_voxcpm.py",
    "voxcpm_story_core.py",
    "voxcpm_ctc_probe.py",
]


def build_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("--kernel-id", default=DEFAULT_KERNEL_ID)
    parser.add_argument("--title", default=DEFAULT_TITLE)
    parser.add_argument("--job-dir", required=True, help="Folder to push with kaggle kernels push")
    parser.add_argument("--input", required=True, help="Short script Markdown path")
    base.add_story_gate_args(parser)
    parser.add_argument("--voice", choices=sorted(base.VOICE_PRESETS), default="adam")
    parser.add_argument("--voice-name", default=None, help="Override the clone profile label")
    parser.add_argument("--ref-audio", default=None, help="Override the reference WAV")
    parser.add_argument("--ref-text", default=None, help="Accepted for compatibility; not needed by reference mode")
    parser.add_argument("--model", default="openbmb/VoxCPM2")
    parser.add_argument("--clone-mode", choices=("reference", "ultimate"), default="reference")
    parser.add_argument("--control", default=DEFAULT_CONTROL)

    parser.add_argument("--story-word-limit", type=int, default=None)
    parser.add_argument("--max-chunk-chars", type=int, default=80)
    parser.add_argument("--max-chunk-words", type=int, default=14)
    parser.add_argument("--min-chunk-words", type=int, default=3)

    parser.add_argument("--cfg-value", type=float, default=2.0)
    parser.add_argument("--inference-timesteps", type=int, default=16)
    parser.add_argument("--seed", type=int, default=20260719)
    parser.add_argument("--retry-badcase", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--retry-badcase-ratio-threshold", type=float, default=8.0)
    parser.add_argument("--optimize", action=argparse.BooleanOptionalAction, default=False)
    parser.add_argument("--denoise", action=argparse.BooleanOptionalAction, default=False)
    parser.add_argument("--render-workers", default="1")
    parser.add_argument("--render-devices", default=None)
    parser.add_argument("--resume", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--verify-chunks", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--verify-asr", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--verify-asr-model", default="large-v3-turbo")
    parser.add_argument("--verify-speaker-severity", choices=("hard", "warn", "off"), default="warn")
    parser.add_argument("--verify-ctc-probe", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--verify-ctc-model", default=base.DEFAULT_CTC_MODEL)
    parser.add_argument("--max-verify-retries", type=int, default=2)
    parser.add_argument("--verify-subsplit", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--master", action=argparse.BooleanOptionalAction, default=True)

    parser.add_argument("--stitch-cont-pause-ms", type=int, default=120)
    parser.add_argument("--stitch-sent-pause-ms", type=int, default=260)
    parser.add_argument("--stitch-para-pause-ms", type=int, default=420)
    parser.add_argument("--stitch-scene-pause-ms", type=int, default=900)
    parser.add_argument("--stitch-expressive-pause-ms", type=int, default=620)

    parser.add_argument("--profile-gpu", action=argparse.BooleanOptionalAction, default=False)
    parser.add_argument("--private", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--enable-internet", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--machine-shape", default="NvidiaTeslaT4")
    parser.add_argument("--dataset-source", action="append", default=[base.DEFAULT_MODEL_DATASET_SOURCE])
    parser.add_argument("--pip-package", action="append", default=[])
    return parser


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
        "--retry_badcase_ratio_threshold", str(args.retry_badcase_ratio_threshold),
        "--stitch_cont_pause_ms", str(args.stitch_cont_pause_ms),
        "--stitch_sent_pause_ms", str(args.stitch_sent_pause_ms),
        "--stitch_para_pause_ms", str(args.stitch_para_pause_ms),
        "--stitch_scene_pause_ms", str(args.stitch_scene_pause_ms),
        "--stitch_expressive_pause_ms", str(args.stitch_expressive_pause_ms),
    ]
    argv.append("--verify_ctc_probe" if args.verify_ctc_probe else "--no-verify_ctc_probe")
    argv += ["--verify_ctc_model", args.verify_ctc_model]
    if args.render_devices:
        argv += ["--render_devices", args.render_devices]
    if args.ref_text:
        argv += ["--ref_text", args.ref_text]
    if args.control:
        argv += ["--control", args.control]
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


def build_info_payload(job_dir, ref_audio, pip_packages, bundle_sha=None):
    tracked = [*COPY_FILES, "render_job.json"]
    return {
        "schema_version": 1,
        "engine": "voxcpm-short-expressive",
        "built_at": datetime.now(timezone.utc).isoformat(),
        "git": base.git_build_identity(),
        "files_sha256": {
            rel: base.sha256_file(job_dir / rel) for rel in tracked if (job_dir / rel).is_file()
        },
        "reference_audio_sha256": base.sha256_file(ref_audio),
        "pip_packages": list(pip_packages),
        "EMBEDDED_BUNDLE_SHA256": bundle_sha or "set-by-launcher-after-extraction",
    }


def main():
    args = build_parser().parse_args()
    story_gate, input_path, story_manifest_path = base.validate_story_for_render(
        args.input,
        manifest_path=args.manifest,
        allow_user_bypass=args.allow_user_bypass,
        bypass_reason=args.bypass_reason,
    )
    if args.control and args.clone_mode == "ultimate":
        raise SystemExit(
            "--control cannot be used with --clone-mode ultimate; short expressive "
            "renders should use --clone-mode reference."
        )
    base.resolve_voice_args(args)
    reference_qc = base.check_reference_audio(args.ref_audio)

    job_dir = Path(args.job_dir).resolve()
    job_dir.mkdir(parents=True, exist_ok=True)
    for rel_path in COPY_FILES:
        dst = job_dir / rel_path
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / rel_path, dst)

    input_name = input_path.name
    ref_name = Path(args.ref_audio).name
    (job_dir / "job_inputs").mkdir(parents=True, exist_ok=True)
    bundled_story = job_dir / "job_inputs" / input_name
    shutil.copy2(input_path, bundled_story)
    if base.sha256_file(bundled_story) != story_gate["story_sha256"]:
        raise SystemExit("story changed after gate validation; refusing to prepare a stale bundle")
    if story_manifest_path.is_file():
        bundled_manifest = job_dir / "job_inputs" / story_manifest_path.name
        shutil.copy2(story_manifest_path, bundled_manifest)
        if base.sha256_file(bundled_manifest) != story_gate["manifest_sha256"]:
            raise SystemExit("story gate manifest changed after validation; refusing to prepare a stale bundle")
    shutil.copy2(Path(args.ref_audio).resolve(), job_dir / "job_inputs" / ref_name)
    input_rel = f"job_inputs/{input_name}"
    ref_rel = f"job_inputs/{ref_name}"

    pip_packages = list(base.DEFAULT_PIP_PACKAGES) + list(args.pip_package)
    pip_packages_no_deps = list(base.DEFAULT_PIP_PACKAGES_NO_DEPS)
    all_pip_packages = pip_packages_no_deps + pip_packages
    output_stem = Path(args.input).stem
    if args.story_word_limit:
        output_stem = f"{output_stem}_first_{args.story_word_limit}_words"
    zip_paths = ["results", "kaggle_render.log", "build_info.json"]
    if args.profile_gpu:
        zip_paths.append("gpu_util.csv")
    manifest = {
        "engine": "voxcpm-short-expressive",
        "pip_packages": pip_packages,
        "pip_packages_no_deps": pip_packages_no_deps,
        "model_id": args.model,
        "ctc_model_id": args.verify_ctc_model if args.verify_ctc_probe else None,
        "render_script": "convert_short_script_to_audio_voxcpm.py",
        "render_args": render_args(args, input_rel, ref_rel),
        "zip_name": f"{output_stem}_voxcpm_short_kaggle_output.zip",
        "zip_paths": zip_paths,
        "profile_gpu": args.profile_gpu,
        "reference_audio_qc": reference_qc,
        "story_gate": story_gate,
    }
    base.write_json(job_dir / "render_job.json", manifest)
    base.write_json(job_dir / "build_info.json", build_info_payload(job_dir, args.ref_audio, all_pip_packages))

    code_file = "convert_script_to_audio_voxcpm_kaggle.py"
    metadata_path = job_dir / "kernel-metadata.json"
    metadata = base.preserve_existing_kernel_identity(
        metadata_path,
        base.kernel_metadata(args, code_file),
    )
    base.write_json(metadata_path, metadata)

    bundle_paths = [*COPY_FILES, "job_inputs", "render_job.json", "build_info.json"]
    bundle_bytes = base.build_bundle_bytes(job_dir, bundle_paths)
    bundle_sha = base.write_embedded_kaggle_entry(job_dir, bundle_bytes, code_file=metadata["code_file"])
    base.write_json(
        job_dir / "build_info.json",
        build_info_payload(job_dir, args.ref_audio, all_pip_packages, bundle_sha=bundle_sha),
    )

    print(f"Prepared short expressive Kaggle job folder: {job_dir}")
    print(f"Kernel id      : {args.kernel_id}")
    print(f"Voice          : {args.voice_name} ({args.clone_mode} cloning)")
    print(f"Story gate     : {story_gate['status']} ({story_gate['story_sha256']})")
    print(f"Control        : {args.control}")
    print(
        f"Reference      : {reference_qc['duration_sec']}s @ {reference_qc['sample_rate']} Hz, "
        f"tail silence {reference_qc['tail_silence_sec']}s"
    )
    print(f"Bundle sha256  : {bundle_sha}")
    print(f"Push with: kaggle kernels push -p {job_dir} --accelerator {args.machine_shape}")


if __name__ == "__main__":
    main()
