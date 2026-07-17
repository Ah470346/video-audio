# Kaggle Render Integration

This repository now includes a simple Kaggle render workflow:

1. Prepare a self-contained Kaggle kernel folder locally.
2. Push that folder to Kaggle and let Kaggle render the audio.
3. Download the output ZIP back into this repo.

## Files

- `tools/prepare_kaggle_render_job.py`
- `convert_script_to_audio_k2fsa_kaggle.py`
- `tools/download_kaggle_kernel_output.py`

## One-time setup

Install the Kaggle CLI locally:

```bash
pip install kaggle
```

Authenticate with Kaggle. The official CLI supports OAuth, `KAGGLE_API_TOKEN`,
or a token file at `~/.kaggle/access_token`.

## Prepare a Kaggle job

Example:

```bash
python3 tools/prepare_kaggle_render_job.py \
  --kernel-id YOUR_KAGGLE_USERNAME/omnivoice-vn-audio-render \
  --title "OmniVoice VN Audio Render" \
  --job-dir kaggle_jobs/omnivoice-vn-audio-render \
  --input kich-ban/drama/thien-kim-gia-thue-toi-dong-vai-thien-kim-that.md \
  --ref-audio /Users/truongdv/Downloads/ngoc_huyen_moi_ref_clone_tu_nhien.wav \
  --story-word-limit 1000 \
  --num-step 32
```

What this does:

- copies the minimum repo files needed for rendering
- copies the story markdown and reference WAV
- generates `render_job.json`
- generates `kernel-metadata.json`
- keeps the local render script untouched and uses a separate Kaggle-only entry file

## Push to Kaggle

```bash
kaggle kernels push -p kaggle_jobs/omnivoice-vn-audio-render --accelerator NvidiaTeslaT4
```

Useful follow-up commands:

```bash
kaggle kernels status YOUR_KAGGLE_USERNAME/omnivoice-vn-audio-render
kaggle kernels output YOUR_KAGGLE_USERNAME/omnivoice-vn-audio-render -p tmp/kaggle-out
```

## Download back into the repo

```bash
python3 tools/download_kaggle_kernel_output.py \
  --kernel YOUR_KAGGLE_USERNAME/omnivoice-vn-audio-render \
  --dest results/kaggle/omnivoice-vn-audio-render \
  --file-pattern ".*\\.(zip|wav|json|log)$" \
  --force
```

By default the downloader also unzips any ZIP files it finds.

## Notes

- `convert_script_to_audio_k2fsa_kaggle.py` is the Kaggle-only entry file.
- The Kaggle wrapper calls `convert_script_to_audio_k2fsa.py` with explicit
  CLI flags so the local render script does not carry Kaggle-specific behavior.
- The prepared Kaggle job defaults to `--runtime_preset upstream_defaults`,
  `--batch_size 2`, `--nj_per_gpu 1`, and `--warmup 0`.
- The prepared Kaggle job bundles the local `omnivoice` package into
  `vendor/omnivoice` and uses a local `vendor/bin/omnivoice-infer-batch`
  wrapper, so the run does not depend on GitHub or PyPI for the OmniVoice
  package itself.
- The prepared Kaggle job disables `verify_asr` because the local pipeline uses
  `mlx_whisper`, which is Apple-specific. Audio-only chunk verification still runs.
- The Kaggle runner only installs dependency packages from PyPI
  (`transformers`, `accelerate`, `librosa`, `soundfile`, etc.).
- The Kaggle job folder is meant to be disposable. Re-run the prepare script
  whenever the story, code, or render flags change.
