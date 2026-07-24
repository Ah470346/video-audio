---
name: story-to-audio
description: |
  Convert Vietnamese story/script Markdown to VoxCPM audio through the Kaggle render pipeline. Use whenever the user asks to turn a story, script, Markdown file, or pasted text into audio, render audio, or push an audio render to Kaggle. Use the short expressive pipeline when the request mentions "ngắn", "kịch bản ngắn", short script, short-form, đọc biểu cảm, nhấn nhá, or expressive delivery.
---

# Story To Audio

Use this workflow for requests like "chuyen xxx thanh audio", "render audio", or "doc kich ban nay ra audio".

When the user says "chuyen/render/doc `<xxx>` thanh audio", treat `<xxx>` as
the story input name. Preserve a filesystem-safe `story_slug` from that name
for output folders and the final copied audio filename.

If the render request includes `--word-limit`, `--story-word-limit`, or an
equivalent instruction to render only the first N words, preserve `word_limit`
for the job folder name and pass it to the prepare script as
`--story-word-limit <N>`.

## Voice Gate

Before preparing or pushing a Kaggle job, ask exactly which clone voice to use
unless the user already named one:

- `adam`
- `ngoc huyen`
- `thuy nguyen`

Map `ngoc huyen`, `ngoc_huyen`, or `ngoc huyen v2` to `--voice ngoc_huyen`. Map `adam` to `--voice adam`. Map `thuy nguyen`, `thúy nguyễn`, `thuy_nguyen`, or `thúy_nguyễn` to `--voice thuy_nguyen`.

## Pipeline Selection

If the render request contains "ngắn", "kịch bản ngắn", "short script",
"short-form", "đọc biểu cảm", "nhấn nhá", "kéo dài chữ", or asks for an
expressive short narration, use the separate short expressive pipeline:

- Prepare with `tools/prepare_kaggle_voxcpm_short_job.py`.
- It bundles `convert_short_script_to_audio_voxcpm.py`, which imports the
  long-form renderer/core but applies short-script defaults.
- Default voice is `adam` when the user does not choose a voice.
- Default cloning mode is `reference`, not `ultimate`, so VoxCPM style control
  can affect emotion, pace, emphasis, and pauses.
- `@style ...` directives are supported only by
  `convert_short_script_to_audio_voxcpm.py`. They apply to following lines
  until the next `@style`, are stripped from spoken text, and are kept out of
  ASR expected text. Use `@style default` to return to the default expressive
  control and `@style off` to disable style control for the following passage.
- Keep chunks shorter and more performative: 80 chars, 14 words, minimum 3
  words, `cfg=2.0`, `inference_timesteps=16`, and the default expressive
  control instruction unless the user provides a different style.

Use the long-story pipeline for ordinary truyện dài/audiobook renders or when
the user prioritizes voice consistency over expressive style control.

## Available Voices

- `ngoc_huyen`: `NGOC HUYEN V2`, reference `voice_samples/ngoc_huyen_moi_ref_clone_tu_nhien.wav`.
- `adam`: `ADAM`, reference `voice_samples/adam_dominant_firm_ref_10p795_18p857.wav`.
- `thuy_nguyen`: `THUY NGUYEN`, reference `voice_samples/download_no_bgm_full_sentence_123p73_129p82_voxcpm.wav`.

## Prepare And Push

After the user chooses the voice:

1. If the input is pasted text, save it as a Markdown file under `kich-ban/` or a suitable subfolder before rendering.
2. Identify the input Markdown for `<xxx>` and keep `story_slug` available for the later download/copy step.
3. Build a timestamp with `date +%Y%m%d-%H%M%S`.
4. Save the Kaggle job bundle under `/Users/truongdv/Documents/projects/video-audio/kaggle_jobs` before pushing:
   - Without a word limit: `kaggle_jobs/<story_slug>_<timestamp>`.
   - With a word limit: `kaggle_jobs/<story_slug>_<word_limit>_words_<timestamp>`.
5. Prepare a Kaggle job with the selected prepare script, passing `--voice <voice_key>` and the computed `--job-dir`.
6. If a word limit was requested, also pass `--story-word-limit <word_limit>`.
7. Push the job with `kaggle kernels push -p <job_dir> --accelerator NvidiaTeslaT4`.
8. Tell the user the kernel id/job dir and then stop the chat. Do not poll or wait for Kaggle unless the user explicitly asks.

Default Kaggle values unless the user asks otherwise:

```bash
python3 tools/prepare_kaggle_voxcpm_job.py \
  --kernel-id ah470346/voxcpm-vn-audio-full-render \
  --title "VoxCPM VN Audio Full Render" \
  --job-dir kaggle_jobs/<story_slug>_<timestamp> \
  --input <input_md> \
  --voice <adam-or-ngoc_huyen-or-thuy_nguyen> \
  --model openbmb/VoxCPM2 \
  --clone-mode ultimate \
  --cfg-value 1.5 \
  --inference-timesteps 10 \
  --seed 20260719 \
  --max-chunk-chars 120 \
  --max-chunk-words 26 \
  --min-chunk-words 8 \
  --verify-chunks \
  --verify-asr \
  --verify-speaker-severity warn \
  --max-verify-retries 2 \
  --verify-subsplit \
  --master \
  --private \
  --enable-internet
```

For short expressive renders, use:

```bash
python3 tools/prepare_kaggle_voxcpm_short_job.py \
  --job-dir kaggle_jobs/<story_slug>_<timestamp> \
  --input <input_md> \
  --voice <adam-or-ngoc_huyen-or-thuy_nguyen> \
  --model openbmb/VoxCPM2 \
  --clone-mode reference \
  --control "expressive Vietnamese dramatic short-form narration, emotional emphasis, natural pauses, clear articulation" \
  --cfg-value 2.0 \
  --inference-timesteps 16 \
  --max-chunk-chars 80 \
  --max-chunk-words 14 \
  --min-chunk-words 3 \
  --retry-badcase-ratio-threshold 8.0 \
  --verify-chunks \
  --verify-asr \
  --verify-speaker-severity warn \
  --max-verify-retries 3 \
  --verify-subsplit \
  --master \
  --private \
  --enable-internet
```

`tools/prepare_kaggle_voxcpm_job.py` attaches the production model cache
dataset by default: `ah470346/voxcpm2-snapshot` (title:
`tts_and_qc_models`). `tools/prepare_kaggle_voxcpm_short_job.py` must do the
same. Long-story and short-expressive jobs must both use this dataset cache for
VoxCPM2, FasterWhisper, and the Vietnamese CTC model. Keep `.env` / `HF_TOKEN`
in the job bundle only as a fallback for missing cache files or future model
additions; do not rely on HF downloads for normal production renders.

For a limited render, use `--job-dir kaggle_jobs/<story_slug>_<word_limit>_words_<timestamp>`
and append `--story-word-limit <word_limit>` to the prepare command.

The prepare tool embeds the story, the selected reference WAV, the VoxCPM
launcher, pinned QC dependencies, and `render_job.json` into the Kaggle bundle.
It defaults to internet-enabled Kaggle runs for PyPI packages and HF fallback,
but model weights should normally come from the attached Kaggle Dataset cache.
It also performs reference WAV QC before packaging, uses warn-first ASR/speaker
checks with retry/sub-split recovery, and runs final mastering when `--master`
is enabled.
Every output should include `build_info.json`, `render_job.json`, the render log,
and the zipped `results/` folder named `<story>_voxcpm_kaggle_output.zip`.

## Required Dataset Cache Gate Before Every Push

Run this gate after prepare and before every `kaggle kernels push`, for both
long-story and short-expressive jobs. Do not push if any check fails.

```bash
python3 - <<'PY'
import json
from pathlib import Path

job_dir = Path("<job_dir>")
metadata = json.loads((job_dir / "kernel-metadata.json").read_text())
manifest = json.loads((job_dir / "render_job.json").read_text())
build = json.loads((job_dir / "build_info.json").read_text())
launcher = (job_dir / "convert_script_to_audio_voxcpm_kaggle.py").read_text()

assert "ah470346/voxcpm2-snapshot" in metadata.get("dataset_sources", []), metadata
assert manifest.get("model_id") == "openbmb/VoxCPM2", manifest.get("model_id")
assert build.get("EMBEDDED_BUNDLE_SHA256") not in (None, "set-by-launcher-after-extraction")
assert "tts-and-qc-models" in launcher and "find_snapshot_in_dataset_roots" in launcher

for spec in manifest.get("pip_packages_no_deps", []) + manifest.get("pip_packages", []):
    assert "==" in spec, spec

print("dataset cache gate OK")
PY
```

Expected Kaggle logs should include lines like `Using Kaggle Dataset snapshot
for openbmb/VoxCPM2`. If logs show `Fetching ... files` for `openbmb/VoxCPM2`,
the cache was not found; fix the launcher/dataset mount before re-pushing.

```bash
kaggle kernels push -p <job_dir> --accelerator NvidiaTeslaT4
```

## When The User Says Kaggle Is Done

When the user later confirms with phrases such as "xong roi", "oke roi",
"done roi", "kaggle xong", or similar, download the full Kaggle output into
`/Users/truongdv/Documents/projects/video-audio/results`.

Use a destination folder that includes the original `story_slug` whenever known:

```bash
python3 tools/download_kaggle_kernel_output.py \
  --kernel ah470346/voxcpm-vn-audio-full-render \
  --dest /Users/truongdv/Documents/projects/video-audio/results/kaggle_voxcpm_full_<story_slug> \
  --file-pattern ".*\\.(zip|wav|json|log)$" \
  --force
```

After downloading:

1. If the output includes a zip, extract it inside the same result folder if it
   is not already extracted.
2. Find the final mastered audio, preferring filenames that contain `final`,
   `master`, `mastered`, or the story slug. Prefer `.wav` over `.mp3` when both
   exist.
3. Create `/Users/truongdv/Documents/projects/video-audio/audio` if needed.
4. Speed the selected final/mastered audio to `1.25x`, then save that processed
   file to `/Users/truongdv/Documents/projects/video-audio/audio/<story_slug>.<ext>`,
   where `<story_slug>` is the filesystem-safe name from the original render
   request and `<ext>` is the source audio extension. Use:

```bash
python3 tools/postprocess_kaggle_audio.py \
  --result-dir /Users/truongdv/Documents/projects/video-audio/results/kaggle_voxcpm_full_<story_slug> \
  --story-slug <story_slug> \
  --speed 1.25 \
  --force
```

5. Report the result folder and processed audio path, then stop.
