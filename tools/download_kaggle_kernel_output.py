#!/usr/bin/env python3
"""Download Kaggle kernel outputs into this repository."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path


def build_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("--kernel", required=True, help="Kaggle kernel ref, e.g. username/slug")
    parser.add_argument("--dest", required=True, help="Destination folder inside the repo")
    parser.add_argument("--file-pattern", default=".*", help="Regex passed to kaggle kernels output")
    parser.add_argument("--unzip", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--force", action="store_true")
    return parser


def main():
    args = build_parser().parse_args()
    kaggle_bin = shutil.which("kaggle")
    if not kaggle_bin:
        print("Error: kaggle CLI not found. Install with `pip install kaggle`.", file=sys.stderr)
        return 1

    dest = Path(args.dest).resolve()
    dest.mkdir(parents=True, exist_ok=True)

    cmd = [
        kaggle_bin,
        "kernels",
        "output",
        args.kernel,
        "-p",
        str(dest),
        "--file-pattern",
        args.file_pattern,
    ]
    if args.force:
        cmd.append("-o")

    print("Running:", " ".join(cmd))
    subprocess.run(cmd, check=True)

    if args.unzip:
        for path in dest.glob("*.zip"):
            unzip_dir = dest / path.stem
            unzip_dir.mkdir(parents=True, exist_ok=True)
            with zipfile.ZipFile(path) as zf:
                zf.extractall(unzip_dir)
            print(f"Unzipped: {path} -> {unzip_dir}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
