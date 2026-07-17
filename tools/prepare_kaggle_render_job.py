#!/usr/bin/env python3
"""Prepare a self-contained Kaggle kernel folder for OmniVoice rendering."""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import shutil
import tarfile
from io import BytesIO
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OMNIVOICE_ROOT = Path(
    os.environ.get("K2FSA_OMNIVOICE_ROOT", str(Path.home() / "k2fsa-omnivoice311"))
)
DEFAULT_COPY_FILES = [
    "convert_script_to_audio_k2fsa.py",
    "omnivoice_story_core.py",
    "tools/omnivoice_no_edge_fade/sitecustomize.py",
]
DEFAULT_PIP_PACKAGES = [
    "huggingface_hub>=0.24.0",
    "pydub>=0.25.1",
    "safetensors>=0.4.0",
    "sentencepiece>=0.2.0",
    "soundfile>=0.12.1",
    "transformers>=4.55.0",
]


def build_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("--kernel-id", required=True, help="Kaggle kernel id, e.g. username/slug")
    parser.add_argument("--title", required=True, help="Kaggle kernel title")
    parser.add_argument("--job-dir", required=True, help="Output folder to push with kaggle kernels push")
    parser.add_argument("--input", required=True, help="Story markdown path")
    parser.add_argument("--ref-audio", required=True, help="Reference WAV path")
    parser.add_argument("--story-word-limit", type=int, default=None)
    parser.add_argument("--voice-name", default="NGOC HUYEN V2")
    parser.add_argument("--model", default="k2-fsa/OmniVoice")
    parser.add_argument("--num-step", type=int, default=32)
    parser.add_argument("--max-chunk-chars", type=int, default=420)
    parser.add_argument("--max-chunk-words", type=int, default=60)
    parser.add_argument("--batch-size", type=int, default=None)
    parser.add_argument("--machine-shape", default="NvidiaTeslaT4")
    parser.add_argument("--private", action="store_true")
    parser.add_argument("--enable-internet", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument(
        "--extra-render-arg",
        action="append",
        default=[],
        help="Extra argument forwarded to convert_script_to_audio_k2fsa.py",
    )
    return parser


def ensure_parent(path):
    path.parent.mkdir(parents=True, exist_ok=True)


def write_json(path, payload):
    ensure_parent(path)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def copy_into_job(src_rel, job_dir):
    src = ROOT / src_rel
    dst = job_dir / src_rel
    ensure_parent(dst)
    shutil.copy2(src, dst)


def find_local_omnivoice_package():
    site_root = DEFAULT_OMNIVOICE_ROOT / ".venv" / "lib"
    candidates = sorted(site_root.glob("python*/site-packages/omnivoice"))
    for candidate in candidates:
        if candidate.exists():
            return candidate
    raise SystemExit(
        "Could not find local omnivoice package under "
        f"{DEFAULT_OMNIVOICE_ROOT}/.venv/lib/python*/site-packages/omnivoice"
    )


def copy_vendor_omnivoice(job_dir):
    src = find_local_omnivoice_package()
    dst = job_dir / "vendor" / "omnivoice"
    ensure_parent(dst)
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst)


def write_vendor_infer_batch(job_dir):
    script_path = job_dir / "vendor" / "bin" / "omnivoice-infer-batch"
    ensure_parent(script_path)
    script_path.write_text(
        "#!/usr/bin/env python3\n"
        "import sys\n"
        "from omnivoice.cli.infer_batch import main\n"
        "if __name__ == '__main__':\n"
        "    sys.argv[0] = sys.argv[0].removesuffix('.exe')\n"
        "    sys.exit(main())\n",
        encoding="utf-8",
    )
    script_path.chmod(0o755)


def build_bundle_bytes(job_dir, rel_paths):
    buf = BytesIO()
    with tarfile.open(fileobj=buf, mode="w:gz") as tf:
        for rel_path in rel_paths:
            src = job_dir / rel_path
            if src.is_dir():
                for child in sorted(src.rglob("*")):
                    if child.is_file():
                        tf.add(child, arcname=str(child.relative_to(job_dir)))
            elif src.is_file():
                tf.add(src, arcname=rel_path)
    return buf.getvalue()


def write_embedded_kaggle_entry(job_dir, bundle_bytes):
    template = (ROOT / "convert_script_to_audio_k2fsa_kaggle.py").read_text(encoding="utf-8")
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
    (job_dir / "convert_script_to_audio_k2fsa_kaggle.py").write_text(rendered, encoding="utf-8")


def kernel_metadata(args):
    payload = {
        "id": args.kernel_id,
        "title": args.title,
        "code_file": "convert_script_to_audio_k2fsa_kaggle.py",
        "language": "python",
        "kernel_type": "script",
        "is_private": "true" if args.private else "false",
        "enable_gpu": "true",
        "enable_tpu": "false",
        "enable_internet": "true" if args.enable_internet else "false",
    }
    if args.machine_shape:
        payload["machine_shape"] = args.machine_shape
    return payload


def render_args(args):
    story_name = Path(args.input).name
    ref_name = Path(args.ref_audio).name
    output_dir = "results"
    cmd = [
        "--input",
        f"job_inputs/{story_name}",
        "--ref_audio",
        f"job_inputs/{ref_name}",
        "--output_dir",
        output_dir,
        "--voice_name",
        args.voice_name,
        "--model",
        args.model,
        "--runtime_preset",
        "upstream_defaults",
        "--num_step",
        str(args.num_step),
        "--max_chunk_chars",
        str(args.max_chunk_chars),
        "--max_chunk_words",
        str(args.max_chunk_words),
        "--batch_size",
        str(args.batch_size if args.batch_size is not None else 2),
        "--nj_per_gpu",
        "1",
        "--warmup",
        "0",
        "--no-verify_asr",
    ]
    if args.story_word_limit is not None:
        cmd.extend(["--story_word_limit", str(args.story_word_limit)])
    cmd.extend(args.extra_render_arg)
    return cmd


def zip_paths(args):
    base_name = Path(args.input).stem
    voice_slug = "".join(ch.lower() if ch.isalnum() else "_" for ch in args.voice_name).strip("_")
    voice_slug = "_".join(part for part in voice_slug.split("_") if part)
    suffix = f"_first_{args.story_word_limit}_words" if args.story_word_limit else ""
    output_name = f"{base_name}{suffix}_k2fsa_{voice_slug}"
    return [
        "results",
    ], output_name


def main():
    args = build_parser().parse_args()
    job_dir = Path(args.job_dir).resolve()
    job_dir.mkdir(parents=True, exist_ok=True)

    for rel_path in DEFAULT_COPY_FILES:
        copy_into_job(rel_path, job_dir)
    copy_vendor_omnivoice(job_dir)
    write_vendor_infer_batch(job_dir)

    input_dst = job_dir / "job_inputs" / Path(args.input).name
    ref_dst = job_dir / "job_inputs" / Path(args.ref_audio).name
    ensure_parent(input_dst)
    shutil.copy2(Path(args.input).resolve(), input_dst)
    shutil.copy2(Path(args.ref_audio).resolve(), ref_dst)

    zip_rel_paths, output_name = zip_paths(args)
    manifest = {
        "pip_packages": DEFAULT_PIP_PACKAGES,
        "preload_model": True,
        "render_args": render_args(args),
        "zip_name": f"{output_name}_kaggle_output.zip",
        "zip_paths": ["results", "kaggle_render.log"],
    }
    write_json(job_dir / "render_job.json", manifest)
    write_json(job_dir / "kernel-metadata.json", kernel_metadata(args))
    bundle_paths = [
        "convert_script_to_audio_k2fsa.py",
        "omnivoice_story_core.py",
        "tools/omnivoice_no_edge_fade/sitecustomize.py",
        "vendor",
        "job_inputs",
        "render_job.json",
    ]
    bundle_bytes = build_bundle_bytes(job_dir, bundle_paths)
    write_embedded_kaggle_entry(job_dir, bundle_bytes)

    print(f"Prepared Kaggle job folder: {job_dir}")
    print(f"Kernel id: {args.kernel_id}")
    print(f"Push with: kaggle kernels push -p {job_dir} --accelerator {args.machine_shape}")


if __name__ == "__main__":
    main()
