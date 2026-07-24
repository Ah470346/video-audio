#!/usr/bin/env python3
"""Kaggle-only launcher for the VoxCPM render pipeline.

This file holds NO render logic. Kaggle uploads a single ``code_file``, so the render script, the
shared text core, the story Markdown, and the reference WAV all travel inside
this file as a base64 tar.gz written by tools/prepare_kaggle_voxcpm_job.py.
Editing the render script alone changes nothing on Kaggle until the bundle is
re-embedded and EMBEDDED_BUNDLE_SHA256 moves.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import importlib
import json
import os
import platform
import shutil
import subprocess
import sys
import tarfile
import time
import zipfile
from io import BytesIO
from pathlib import Path

EMBEDDED_BUNDLE_B64 = None
EMBEDDED_BUNDLE_SHA256 = None
EMBEDDED_BUNDLE_DIRNAME = "voxcpm_job_bundle"

PACKAGE_IMPORT_NAMES = {
    "voxcpm": ("voxcpm",),
    "soundfile": ("soundfile",),
    "librosa": ("librosa",),
    "huggingface_hub": ("huggingface_hub",),
    "huggingface-hub": ("huggingface_hub",),
    "wetext": ("wetext",),
    "inflect": ("inflect",),
    "faster-whisper": ("faster_whisper",),
    "resemblyzer": ("resemblyzer",),
}
RUNTIME_MODULES = ("voxcpm", "soundfile", "numpy", "torch")
KAGGLE_DATASET_SLUG = "voxcpm2-snapshot"
KAGGLE_DATASET_ALIASES = (
    "voxcpm2-snapshot",
    "tts-and-qc-models",
    "tts_and_qc_models",
)
MODEL_SNAPSHOT_NAMES = {
    "openbmb/VoxCPM2": "openbmb_voxcpm2",
    "large-v3": "systran_faster_whisper_large_v3",
    "Systran/faster-whisper-large-v3": "systran_faster_whisper_large_v3",
    "large-v3-turbo": "mobiuslabsgmbh_faster_whisper_large_v3_turbo",
    "mobiuslabsgmbh/faster-whisper-large-v3-turbo": "mobiuslabsgmbh_faster_whisper_large_v3_turbo",
    "nguyenvulebinh/wav2vec2-base-vietnamese-250h": "nguyenvulebinh_wav2vec2_base_vietnamese_250h",
}
# faster-whisper "size" names (e.g. "large-v3") are aliases resolved by
# faster_whisper._MODELS, not Hugging Face repo ids. snapshot_download needs
# the real repo, or it 404s (verified against faster-whisper==1.2.1's table:
# large-v3 -> Systran/..., large-v3-turbo -> mobiuslabsgmbh/..., different owners).
ASR_ALIAS_TO_HF_REPO = {
    "large-v3": "Systran/faster-whisper-large-v3",
    "large-v3-turbo": "mobiuslabsgmbh/faster-whisper-large-v3-turbo",
    "large-v2": "Systran/faster-whisper-large-v2",
    "large": "Systran/faster-whisper-large-v3",
    "medium": "Systran/faster-whisper-medium",
    "small": "Systran/faster-whisper-small",
}
MODEL_MARKER_FILES = ("config.json", "model.bin", "model.safetensors", "pytorch_model.bin")


def build_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", default="render_job.json")
    return parser


def append_log(log_file, message):
    print(message, flush=True)
    if log_file is None:
        return
    with open(log_file, "a", encoding="utf-8") as fh:
        fh.write(message + "\n")


def load_env_file(env_path, log_file=None):
    """Load simple KEY=VALUE lines without echoing secret values."""
    env_path = Path(env_path)
    if not env_path.is_file():
        return
    loaded = []
    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip("\"'")
        if not key or key in os.environ:
            continue
        os.environ[key] = value
        loaded.append(key)
    if loaded:
        append_log(log_file, f"Loaded environment keys from {env_path.name}: {', '.join(sorted(loaded))}")


def run(cmd, cwd=None, env=None, log_file=None):
    append_log(log_file, f"$ {' '.join(str(part) for part in cmd)}")
    proc = subprocess.Popen(
        [str(part) for part in cmd],
        cwd=str(cwd) if cwd else None,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )
    for line in proc.stdout:
        append_log(log_file, line.rstrip())
    proc.wait()
    if proc.returncode != 0:
        raise subprocess.CalledProcessError(proc.returncode, cmd)


def preflight_environment(log_file):
    append_log(log_file, f"python   : {sys.version.split()[0]} ({platform.platform()})")
    try:
        import torch

        append_log(log_file, f"torch    : {torch.__version__} cuda={torch.cuda.is_available()}")
        if torch.cuda.is_available():
            for index in range(torch.cuda.device_count()):
                props = torch.cuda.get_device_properties(index)
                append_log(
                    log_file,
                    f"gpu[{index}]   : {props.name} {props.total_memory / 1024 ** 3:.1f} GiB",
                )
    except Exception as exc:  # torch missing is a fatal condition we report later
        append_log(log_file, f"torch    : unavailable ({exc})")


def package_name_from_spec(spec):
    for separator in ("==", ">=", "<=", "~=", ">", "<"):
        if separator in spec:
            return spec.split(separator, 1)[0].strip()
    return spec.strip()


def module_present(spec):
    name = package_name_from_spec(spec)
    for candidate in PACKAGE_IMPORT_NAMES.get(name, (name.replace("-", "_"),)):
        try:
            importlib.import_module(candidate)
            return True
        except Exception:
            continue
    return False


def install_packages(packages, log_file=None, extra_pip_args=()):
    missing = [spec for spec in packages if not module_present(spec)]
    if not missing:
        append_log(log_file, "All pip packages already importable; skipping install.")
        return False
    append_log(log_file, f"Installing: {missing}")
    run([sys.executable, "-m", "pip", "install", "--no-input", *extra_pip_args, *missing], log_file=log_file)
    return True


def require_runtime_modules(log_file):
    broken = []
    for name in RUNTIME_MODULES:
        try:
            importlib.import_module(name)
        except Exception as exc:
            broken.append(f"{name}: {exc}")
    if broken:
        append_log(log_file, "FATAL: runtime modules unavailable:\n  " + "\n  ".join(broken))
        raise SystemExit(1)
    append_log(log_file, f"Runtime modules OK: {', '.join(RUNTIME_MODULES)}")


def safe_extract_tar(tar_path, target_dir):
    target_dir = Path(target_dir).resolve()
    target_dir.mkdir(parents=True, exist_ok=True)
    with tarfile.open(tar_path, mode="r:*") as tf:
        for member in tf.getmembers():
            member_path = (target_dir / member.name).resolve()
            if target_dir != member_path and target_dir not in member_path.parents:
                raise RuntimeError(f"Unsafe tar member path: {member.name}")
        tf.extractall(target_dir)


def usable_model_dir(path, snapshot_name):
    path = Path(path)
    if any((path / marker).exists() for marker in MODEL_MARKER_FILES):
        return path
    nested = path / snapshot_name
    if nested.is_dir() and any((nested / marker).exists() for marker in MODEL_MARKER_FILES):
        return nested
    children = [child for child in path.iterdir() if child.is_dir()] if path.exists() else []
    if len(children) == 1 and any((children[0] / marker).exists() for marker in MODEL_MARKER_FILES):
        return children[0]
    return path


def kaggle_dataset_roots(log_file=None):
    input_root = Path("/kaggle/input")
    if not input_root.exists():
        return []

    roots = []
    seen = set()
    for name in KAGGLE_DATASET_ALIASES:
        path = input_root / name
        if path.is_dir() and path not in seen:
            roots.append(path)
            seen.add(path)
    for path in sorted(input_root.iterdir()):
        if path.is_dir() and path not in seen:
            roots.append(path)
            seen.add(path)
    if log_file is not None:
        append_log(log_file, "Kaggle input roots: " + ", ".join(str(path) for path in roots))
    return roots


def find_snapshot_in_dataset_roots(snapshot_name, log_file=None):
    for dataset_root in kaggle_dataset_roots(log_file):
        direct_path = dataset_root / snapshot_name
        if direct_path.is_dir():
            return dataset_root, direct_path, None

        archive_path = dataset_root / f"{snapshot_name}.tar"
        if archive_path.is_file():
            return dataset_root, None, archive_path

    # Last resort for datasets whose files are nested one extra level.
    input_root = Path("/kaggle/input")
    if input_root.exists():
        for direct_path in sorted(input_root.rglob(snapshot_name)):
            if direct_path.is_dir():
                return direct_path.parent, direct_path, None
        for archive_path in sorted(input_root.rglob(f"{snapshot_name}.tar")):
            if archive_path.is_file():
                return archive_path.parent, None, archive_path
    return None, None, None


def kaggle_dataset_snapshot(model_id, log_file=None):
    snapshot_name = MODEL_SNAPSHOT_NAMES.get(model_id)
    if not snapshot_name:
        return None
    dataset_root, direct_path, archive_path = find_snapshot_in_dataset_roots(snapshot_name, log_file)
    if dataset_root is None:
        append_log(log_file, f"No Kaggle Dataset snapshot found for {model_id} ({snapshot_name})")
        return None

    if direct_path is not None:
        model_dir = usable_model_dir(direct_path, snapshot_name)
        append_log(log_file, f"Using Kaggle Dataset snapshot for {model_id}: {model_dir}")
        return str(model_dir)

    extract_root = Path("/kaggle/working/model_snapshots")
    target_dir = extract_root / snapshot_name
    marker_path = target_dir / ".extracted_from_kaggle_dataset"
    if not marker_path.exists():
        append_log(log_file, f"Extracting Kaggle Dataset snapshot for {model_id}: {archive_path}")
        if target_dir.exists():
            shutil.rmtree(target_dir)
        safe_extract_tar(archive_path, target_dir)
        marker_path.write_text(str(archive_path) + "\n", encoding="utf-8")
    model_dir = usable_model_dir(target_dir, snapshot_name)
    append_log(log_file, f"Using extracted Kaggle Dataset snapshot for {model_id}: {model_dir}")
    return str(model_dir)


def prefetch_model(model_id, log_file, attempts=3):
    """Pull the VoxCPM snapshot before the render so a flaky download fails
    here, loudly, instead of halfway through chunk rendering."""
    if not model_id or Path(model_id).is_dir():
        return model_id
    dataset_path = kaggle_dataset_snapshot(model_id, log_file)
    if dataset_path:
        return dataset_path
    from huggingface_hub import snapshot_download

    repo_id = ASR_ALIAS_TO_HF_REPO.get(model_id, model_id)
    if repo_id != model_id:
        append_log(log_file, f"Resolved faster-whisper alias '{model_id}' -> HF repo '{repo_id}'")

    for attempt in range(1, attempts + 1):
        try:
            path = snapshot_download(repo_id=repo_id)
            append_log(log_file, f"Model snapshot ready: {path}")
            return path
        except Exception as exc:
            append_log(log_file, f"snapshot_download attempt {attempt}/{attempts} failed: {exc}")
            if attempt == attempts:
                raise
            time.sleep(10 * attempt)
    return model_id


def materialize_embedded_bundle(log_file=None):
    if not EMBEDDED_BUNDLE_B64:
        return None

    bundle_dir = Path("/kaggle/working") / EMBEDDED_BUNDLE_DIRNAME
    bundle_dir.mkdir(parents=True, exist_ok=True)
    marker_path = bundle_dir / ".bundle_sha256"
    current_sha = marker_path.read_text(encoding="utf-8").strip() if marker_path.exists() else None
    if current_sha == EMBEDDED_BUNDLE_SHA256:
        return bundle_dir

    payload = base64.b64decode(EMBEDDED_BUNDLE_B64.encode("ascii"))
    actual_sha = hashlib.sha256(payload).hexdigest()
    if EMBEDDED_BUNDLE_SHA256 and actual_sha != EMBEDDED_BUNDLE_SHA256:
        raise SystemExit(
            f"Embedded bundle checksum mismatch: expected {EMBEDDED_BUNDLE_SHA256}, got {actual_sha}"
        )

    for path in bundle_dir.iterdir():
        if path.is_dir():
            shutil.rmtree(path)
        else:
            path.unlink()

    with tarfile.open(fileobj=BytesIO(payload), mode="r:gz") as tf:
        try:
            tf.extractall(bundle_dir, filter="data")
        except TypeError:
            tf.extractall(bundle_dir)

    marker_path.write_text(actual_sha + "\n", encoding="utf-8")
    build_info_path = bundle_dir / "build_info.json"
    if build_info_path.is_file():
        build_info = json.loads(build_info_path.read_text(encoding="utf-8"))
        build_info["EMBEDDED_BUNDLE_SHA256"] = actual_sha
        build_info_path.write_text(
            json.dumps(build_info, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
    append_log(log_file, f"Embedded bundle materialized at: {bundle_dir} (sha {actual_sha[:12]})")
    return bundle_dir


def zip_outputs(job_dir, zip_name, zip_paths):
    zip_path = Path("/kaggle/working") / zip_name
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for rel_path in zip_paths:
            src = job_dir / rel_path
            if src.is_dir():
                for path in src.rglob("*"):
                    if path.is_file():
                        zf.write(path, path.relative_to(job_dir))
            elif src.is_file():
                zf.write(src, src.relative_to(job_dir))
            else:
                print(f"Skip missing output path: {src}")
    print(f"Packed outputs: {zip_path}")


def start_gpu_profiler(job_dir, log_file):
    """Background ``nvidia-smi`` sampler for the Cách-3 shared-QC question:
    is the GPU actually idle enough during single-worker render for extra
    workers/GPU to help, or is it already compute-saturated? Best-effort --
    a missing/broken nvidia-smi must never take down the render itself."""
    csv_path = job_dir / "gpu_util.csv"
    try:
        proc = subprocess.Popen(
            [
                "nvidia-smi",
                "--query-gpu=timestamp,index,utilization.gpu,utilization.memory,memory.used,memory.total",
                "--format=csv",
                "-l", "2",
            ],
            stdout=open(csv_path, "w", encoding="utf-8"),
            stderr=subprocess.STDOUT,
        )
        append_log(log_file, f"GPU profiler started -> {csv_path.name} (pid {proc.pid})")
        return proc
    except Exception as exc:
        append_log(log_file, f"GPU profiler unavailable, skipping: {exc}")
        return None


def stop_gpu_profiler(proc, log_file):
    if proc is None:
        return
    proc.terminate()
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()
    append_log(log_file, "GPU profiler stopped")


def replace_arg_value(render_args, flag, value):
    if not value:
        return render_args
    resolved = list(render_args)
    for index, current in enumerate(resolved):
        if current == flag and index + 1 < len(resolved):
            resolved[index + 1] = str(value)
            return resolved
    return [*resolved, flag, str(value)]


def arg_value(render_args, flag):
    for index, value in enumerate(render_args):
        if value == flag and index + 1 < len(render_args):
            return render_args[index + 1]
    return None


def resolve_model_arg(render_args, model_path):
    """Rewrite --model to the local snapshot path once it is downloaded."""
    return replace_arg_value(render_args, "--model", model_path)


def main():
    args = build_parser().parse_args()
    script_dir = Path(__file__).resolve().parent
    manifest_path = script_dir / args.manifest
    job_dir = script_dir
    if not manifest_path.exists():
        materialized = materialize_embedded_bundle()
        if materialized is not None:
            job_dir = materialized
            manifest_path = job_dir / args.manifest
    if not manifest_path.exists():
        raise SystemExit(f"Manifest not found: {manifest_path}")

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    log_file = job_dir / "kaggle_render.log"
    reexeced = os.environ.get("VOXCPM_RENDER_REEXECED") == "1"
    if reexeced and log_file.exists():
        append_log(log_file, "--- Restarted after package install ---")
    else:
        log_file.write_text("", encoding="utf-8")
    load_env_file(job_dir / ".env", log_file=log_file)

    preflight_environment(log_file)

    # voxcpm's own declared deps include gradio/modelscope/datasets/funasr/
    # spaces/argbind/wetext/addict -- none of which the render path (VoxCPM.
    # from_pretrained/.generate, no gradio demo, no training) ever imports,
    # and Kaggle's base image already has everything voxcpm *does* touch
    # (torch/torchaudio/transformers/librosa/safetensors/einops/pydantic).
    # --no-deps skips ~150MB of dead installs. faster-whisper/resemblyzer
    # install normally: their deps (ctranslate2, onnxruntime, av, webrtcvad)
    # are real runtime requirements not already present on Kaggle.
    installed_a = install_packages(
        manifest.get("pip_packages_no_deps", []), log_file=log_file, extra_pip_args=["--no-deps"]
    )
    installed_b = install_packages(manifest.get("pip_packages", []), log_file=log_file)
    if (installed_a or installed_b) and not reexeced:
        append_log(log_file, "Restarting interpreter so runtime imports use the fresh modules.")
        env = os.environ.copy()
        env["VOXCPM_RENDER_REEXECED"] = "1"
        os.execve(
            sys.executable,
            [sys.executable, str(Path(__file__).resolve()), "--manifest", args.manifest],
            env,
        )

    require_runtime_modules(log_file)

    render_args = manifest.get("render_args", [])
    if not render_args:
        raise SystemExit("render_job.json is missing render_args")

    env = os.environ.copy()
    env.setdefault("HF_HUB_ENABLE_HF_TRANSFER", "0")
    env.setdefault("TOKENIZERS_PARALLELISM", "false")

    # A render failure must never fail the kernel: Kaggle discards the output of
    # an errored version, which would throw away every chunk already rendered.
    render_error = None
    gpu_profiler = None
    try:
        model_path = prefetch_model(manifest.get("model_id"), log_file)
        render_args = resolve_model_arg(render_args, model_path)
        # The CTC probe model is small but fetched lazily on the first chunk;
        # pulling it here means a Hub hiccup surfaces before any GPU time is
        # spent. QC degrades to a warning if it never arrives, so this is not
        # allowed to abort the render.
        ctc_model = manifest.get("ctc_model_id")
        if ctc_model:
            try:
                ctc_model_path = prefetch_model(ctc_model, log_file)
                render_args = replace_arg_value(render_args, "--verify_ctc_model", ctc_model_path)
            except Exception as exc:
                append_log(log_file, f"CTC probe model prefetch failed, QC will warn: {exc}")
        asr_model = arg_value(render_args, "--verify_asr_model")
        if asr_model:
            try:
                asr_model_path = prefetch_model(asr_model, log_file)
                render_args = replace_arg_value(render_args, "--verify_asr_model", asr_model_path)
            except Exception as exc:
                append_log(log_file, f"ASR model prefetch failed, falling back to lazy load: {exc}")
        if manifest.get("profile_gpu"):
            gpu_profiler = start_gpu_profiler(job_dir, log_file)
        render_script = manifest.get("render_script", "convert_script_to_audio_voxcpm.py")
        run(
            [sys.executable, render_script, *render_args],
            cwd=job_dir,
            env=env,
            log_file=log_file,
        )
    except Exception as exc:
        render_error = exc
        append_log(
            log_file,
            f"RENDER FAILED ({type(exc).__name__}: {exc}); packaging partial outputs.",
        )
        results_dir = job_dir / "results"
        results_dir.mkdir(parents=True, exist_ok=True)
        (results_dir / "RENDER_FAILED.json").write_text(
            json.dumps(
                {
                    "status": "render_failed",
                    "error": f"{type(exc).__name__}: {exc}",
                    "note": "Chunk WAVs and reports in this zip are still usable.",
                },
                ensure_ascii=False,
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
    finally:
        stop_gpu_profiler(gpu_profiler, log_file)

    zip_outputs(job_dir, manifest["zip_name"], manifest["zip_paths"])
    if render_error is not None:
        print(f"WARNING: render failed ({render_error}); see kaggle_render.log inside the zip.")


if __name__ == "__main__":
    main()
