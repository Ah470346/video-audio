#!/usr/bin/env python3
"""Kaggle-only wrapper for the local OmniVoice render pipeline.

This file is intentionally separate from convert_script_to_audio_k2fsa.py.
It runs on Kaggle, installs any missing packages, then calls the same local
render script with explicit CLI arguments so the local workflow stays untouched.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import importlib
import importlib.metadata
import json
import os
import platform
import re
import shutil
import socket
import subprocess
import sys
import tarfile
import zipfile
from io import BytesIO
from pathlib import Path

EMBEDDED_BUNDLE_B64 = None
EMBEDDED_BUNDLE_SHA256 = None
EMBEDDED_BUNDLE_DIRNAME = "job_bundle"
PACKAGE_IMPORT_NAMES = {
    "huggingface_hub": ("huggingface_hub",),
    "huggingface-hub": ("huggingface_hub",),
    "pydub": ("pydub",),
    "safetensors": ("safetensors",),
    "sentencepiece": ("sentencepiece",),
    "soundfile": ("soundfile",),
    "transformers": ("transformers",),
}
RUNTIME_MODULES = (
    "omnivoice",
    "huggingface_hub",
    "pydub",
    "safetensors",
    "soundfile",
    "torchaudio",
    "transformers",
)


def build_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", default="render_job.json")
    return parser


def append_log(log_file, message):
    print(message)
    if log_file is None:
        return
    with open(log_file, "a", encoding="utf-8") as fh:
        fh.write(message + "\n")


def apply_local_pythonpath(paths):
    for path in reversed([p for p in paths if p]):
        path_str = str(path)
        if path_str not in sys.path:
            sys.path.insert(0, path_str)


def run(cmd, cwd=None, env=None, log_file=None):
    print("Running:", " ".join(cmd))
    if log_file is None:
        subprocess.run(cmd, cwd=cwd, env=env, check=True)
        return

    with open(log_file, "a", encoding="utf-8") as fh:
        fh.write("$ " + " ".join(cmd) + "\n")
        fh.flush()
        proc = subprocess.Popen(
            cmd,
            cwd=cwd,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )
        assert proc.stdout is not None
        for line in proc.stdout:
            print(line, end="")
            fh.write(line)
        return_code = proc.wait()
        if return_code != 0:
            raise subprocess.CalledProcessError(return_code, cmd)


def package_name_from_spec(spec):
    if "://" in spec or spec.startswith("git+"):
        return None
    base = re.split(r"[<>=!~]", spec, maxsplit=1)[0]
    return base.split("[", 1)[0].strip() or None


def find_installed_module(spec):
    package_name = package_name_from_spec(spec)
    if not package_name:
        return None, None, None
    import_names = PACKAGE_IMPORT_NAMES.get(package_name.lower(), (package_name.replace("-", "_"),))
    for module_name in import_names:
        try:
            module = importlib.import_module(module_name)
        except Exception:
            continue
        version = getattr(module, "__version__", None)
        if version is None:
            try:
                version = importlib.metadata.version(package_name)
            except importlib.metadata.PackageNotFoundError:
                version = "unknown"
        return package_name, module_name, version
    return package_name, None, None


def install_packages(packages, log_file=None):
    if not packages:
        append_log(log_file, "No extra pip packages requested by manifest.")
        return

    missing = []
    for spec in packages:
        package_name, module_name, version = find_installed_module(spec)
        if module_name:
            append_log(log_file, f"Using preinstalled package for {spec}: {module_name} ({version})")
            continue
        missing.append(spec)
        if package_name:
            append_log(log_file, f"Package missing on image, will try pip install: {spec}")
        else:
            append_log(log_file, f"Package requires explicit pip install: {spec}")

    if not missing:
        append_log(log_file, "All manifest packages already available; skipping pip install.")
        return

    run([sys.executable, "-m", "pip", "install", *missing], log_file=log_file)


def check_binary(name):
    path = shutil.which(name)
    if not path:
        raise SystemExit(f"Required binary not found on Kaggle image: {name}")
    print(f"{name}: {path}")


def preflight_environment(log_file):
    print(f"Platform: {platform.platform()}")
    print(f"Python: {sys.version.split()[0]}")
    check_binary("ffmpeg")

    import torch

    print(f"torch: {torch.__version__}")
    if not torch.cuda.is_available():
        raise SystemExit("CUDA is not available. Enable a Kaggle GPU accelerator before running this job.")

    device_count = torch.cuda.device_count()
    names = [torch.cuda.get_device_name(i) for i in range(device_count)]
    print(f"CUDA devices: {device_count} -> {names}")

    with open(log_file, "a", encoding="utf-8") as fh:
        fh.write(f"Platform: {platform.platform()}\n")
        fh.write(f"Python: {sys.version.split()[0]}\n")
        fh.write(f"torch: {torch.__version__}\n")
        fh.write(f"CUDA devices: {device_count} -> {names}\n")


def require_runtime_modules(log_file):
    missing = []
    for module_name in RUNTIME_MODULES:
        try:
            module = importlib.import_module(module_name)
        except Exception as exc:
            missing.append((module_name, str(exc)))
            continue
        version = getattr(module, "__version__", "unknown")
        append_log(log_file, f"Runtime module OK: {module_name} ({version})")

    if not missing:
        return

    details = "; ".join(f"{module}: {error}" for module, error in missing)
    raise SystemExit(
        "Required Python runtime modules are missing or failed to import on this Kaggle image. "
        f"Details: {details}"
    )


def ensure_host_resolves(hostname, log_file):
    try:
        resolved = sorted({entry[4][0] for entry in socket.getaddrinfo(hostname, 443, proto=socket.IPPROTO_TCP)})
    except socket.gaierror as exc:
        raise SystemExit(
            f"Could not resolve {hostname}. Kaggle Internet appears unavailable. "
            f"Enable Internet or bundle the model locally. Original error: {exc}"
        ) from exc
    append_log(log_file, f"{hostname} resolves to: {resolved}")


def localize_model(render_args, env, manifest, log_file):
    if not manifest.get("preload_model", True):
        return render_args

    if "--model" not in render_args:
        return render_args

    model_index = render_args.index("--model") + 1
    model_ref = render_args[model_index]
    if os.path.exists(model_ref):
        return render_args

    hf_home = Path("/kaggle/working/hf_cache")
    hf_home.mkdir(parents=True, exist_ok=True)
    env["HF_HOME"] = str(hf_home)
    env.setdefault("HUGGINGFACE_HUB_CACHE", str(hf_home / "hub"))
    ensure_host_resolves("huggingface.co", log_file)

    from huggingface_hub import snapshot_download

    local_model_dir = snapshot_download(repo_id=model_ref, cache_dir=str(hf_home))
    updated_args = list(render_args)
    updated_args[model_index] = local_model_dir
    print(f"Model cached at: {local_model_dir}")
    with open(log_file, "a", encoding="utf-8") as fh:
        fh.write(f"Model ref: {model_ref}\n")
        fh.write(f"Model cached at: {local_model_dir}\n")
    return updated_args


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


def materialize_embedded_bundle():
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
    print(f"Embedded bundle materialized at: {bundle_dir}")
    return bundle_dir


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
    log_file.write_text("", encoding="utf-8")
    install_packages(manifest.get("pip_packages", []), log_file=log_file)

    env = os.environ.copy()
    tool_dir = job_dir / "tools" / "omnivoice_no_edge_fade"
    vendor_dir = job_dir / "vendor"
    existing_pythonpath = env.get("PYTHONPATH")
    pythonpath_entries = [str(tool_dir)]
    if vendor_dir.exists():
        pythonpath_entries.append(str(vendor_dir))
    if existing_pythonpath:
        pythonpath_entries.append(existing_pythonpath)
    env["PYTHONPATH"] = os.pathsep.join(pythonpath_entries)
    apply_local_pythonpath([vendor_dir, tool_dir])
    infer_batch = job_dir / "vendor" / "bin" / "omnivoice-infer-batch"
    if infer_batch.exists():
        env["K2FSA_OMNIVOICE_INFER_BATCH"] = str(infer_batch)
    require_runtime_modules(log_file)
    preflight_environment(log_file)

    render_args = manifest.get("render_args", [])
    if not render_args:
        raise SystemExit("render_job.json is missing render_args")
    render_args = localize_model(render_args, env, manifest, log_file)

    run(
        [sys.executable, "convert_script_to_audio_k2fsa.py", *render_args],
        cwd=job_dir,
        env=env,
        log_file=log_file,
    )
    zip_outputs(job_dir, manifest["zip_name"], manifest["zip_paths"])


if __name__ == "__main__":
    main()
