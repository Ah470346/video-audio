# Tiến Độ Pipeline Audio Ngắn VoxCPM

Ngày ghi chú: 2026-07-20

## Mục Tiêu

Tạo một pipeline riêng cho kịch bản ngắn đọc biểu cảm, tách bạch với pipeline
truyện dài/audiobook hiện tại.

Yêu cầu chính:

- Kịch bản ngắn dùng được giọng clone Adam.
- Có thể điều khiển biểu cảm/nhịp đọc bằng style tag.
- Tuyệt đối không ảnh hưởng pipeline truyện dài.
- Khi push Kaggle, cả job dài và job ngắn đều phải dùng Kaggle Dataset cache,
  không tải model VoxCPM từ Hugging Face trong render bình thường.

## Ranh Giới Bắt Buộc Với Audio Dài

Pipeline kịch bản ngắn phải được coi là một nhánh riêng. Mọi thay đổi phục vụ
`@style`, short expressive, kéo chữ, voice acting, hoặc thử nghiệm biểu cảm
**tuyệt đối không được làm đổi hành vi mặc định của audio dài**.

Các nguyên tắc không được phá:

- Không thêm `--control` vào `convert_script_to_audio_voxcpm.py` của audio dài.
- Không để `@style` được parse bởi pipeline audio dài.
- Không đổi default long-form: `clone_mode=ultimate`, chunk dài, resume, verify,
  retry/subsplit, và mastering của audio dài.
- Không đổi logic resume/hash của audio dài chỉ để phục vụ style tag.
- Không bật/tắt worker/QC của audio dài theo nhu cầu của kịch bản ngắn.
- Nếu cần tính năng mới cho short pipeline, ưu tiên tạo file riêng hoặc wrapper
  riêng như `convert_short_script_to_audio_voxcpm.py`.
- Trước khi push hoặc render production, phải kiểm tra lại bằng search rằng
  `--control`, `@style`, và `style_control` chỉ xuất hiện trong short pipeline,
  short prepare, tài liệu, hoặc test tương ứng.

Lệnh kiểm tra nhanh:

```bash
rg -n -e "--control|@style|style_control" \
  convert_script_to_audio_voxcpm.py \
  tools/prepare_kaggle_voxcpm_job.py \
  convert_short_script_to_audio_voxcpm.py \
  tools/prepare_kaggle_voxcpm_short_job.py
```

Kỳ vọng:

- `convert_script_to_audio_voxcpm.py` và `tools/prepare_kaggle_voxcpm_job.py`
  không có `--control` hoặc parser `@style`.
- Logic style chỉ nằm ở `convert_short_script_to_audio_voxcpm.py` và
  `tools/prepare_kaggle_voxcpm_short_job.py`.

## File Đã Tạo Hoặc Cập Nhật

### Pipeline ngắn

- `convert_short_script_to_audio_voxcpm.py`
  - Entry point riêng cho kịch bản ngắn.
  - Import renderer dài `convert_script_to_audio_voxcpm.py` để dùng lại core
    render, normalize, chunking, QC, stitching, mastering.
  - Tự parse `@style`.
  - Chèn style thành `(style)text` ngay trước khi gọi VoxCPM.
  - Ép `--render_workers 1` để tránh mất monkeypatch qua multiprocessing spawn.
  - Ép `--no-resume` để tránh reuse nhầm audio khi đổi style.

- `tools/prepare_kaggle_voxcpm_short_job.py`
  - Prepare Kaggle job riêng cho short expressive.
  - Default voice: `adam`.
  - Default clone mode: `reference`.
  - Default control:
    `expressive Vietnamese dramatic short-form narration, emotional emphasis, natural pauses, clear articulation`
  - Bundle `convert_short_script_to_audio_voxcpm.py` cùng renderer/core chung.

### Launcher Kaggle

- `convert_script_to_audio_voxcpm_kaggle.py`
  - Đã sửa để manifest có thể chỉ định `render_script`.
  - Job dài vẫn chạy `convert_script_to_audio_voxcpm.py`.
  - Job ngắn chạy `convert_short_script_to_audio_voxcpm.py`.
  - Đã sửa logic tìm dataset cache linh hoạt hơn:
    - `/kaggle/input/voxcpm2-snapshot`
    - `/kaggle/input/tts-and-qc-models`
    - `/kaggle/input/tts_and_qc_models`
    - mọi thư mục con trong `/kaggle/input`

### Hướng dẫn skill/agent

- `.agents/skills/story-to-audio/SKILL.md`
- `.claude/skills/story-to-audio/SKILL.md`
- `AGENTS.md`
- `CLAUDE.md`
- `.agents/AGENTS.md`

Đã cập nhật để:

- Prompt có "ngắn", "kịch bản ngắn", "đọc biểu cảm", "nhấn nhá",
  "kéo dài chữ", hoặc short-form thì dùng pipeline ngắn.
- Trước mỗi lần push Kaggle phải chạy Dataset Cache Gate.
- Cả truyện dài và kịch bản ngắn đều phải attach `ah470346/voxcpm2-snapshot`.

### Tài liệu style tag

- `VOXCPM_STYLE_TAGS.md`
  - Giải thích rằng VoxCPM không có tag cố định kiểu SSML.
  - Các tag trong repo là bộ quy ước dựa trên natural-language control
    instruction của VoxCPM.
  - Có bảng tag, combo khuyên dùng, ví dụ `@style`, và cảnh báo cần tránh.

### Test

- `tests/test_voxcpm_story_core.py`
  - Test short prepare default dùng Adam/reference/control.
  - Test short prepare cũng attach dataset source mặc định.
  - Test launcher tìm dataset theo alias title `tts-and-qc-models`.
  - Test long renderer không nhận `--control`.
  - Test parser `@style` tách metadata, không để `@style` vào spoken text.

## Cú Pháp Kịch Bản Ngắn

Ví dụ:

```text
@style cheerful, conversational
Các bạn nghe mình nhóóó....

@style urgent, anxious
Đừừng....

đừng tin ai hết.

@style off
Tôi im lặng nhìn cái điện thoại.
```

Quy tắc:

- `@style ...` áp dụng cho các dòng sau nó cho tới `@style` tiếp theo.
- `@style default` quay về style mặc định.
- `@style off` tắt style control cho đoạn sau.
- Mỗi style chỉ nên có 1-3 tag/cụm tag.
- Dùng tiếng Anh cho tag để bám sát cách docs VoxCPM mô tả control instruction.

## Config Hiện Tại Của Pipeline Ngắn

Short expressive default:

```bash
--clone_mode reference
--max_chunk_chars 80
--max_chunk_words 14
--min_chunk_words 3
--cfg_value 2.0
--inference_timesteps 16
--retry_badcase_ratio_threshold 8.0
--stitch_cont_pause_ms 120
--stitch_sent_pause_ms 260
--stitch_para_pause_ms 420
--stitch_scene_pause_ms 900
--stitch_expressive_pause_ms 620
--verify_speaker_severity warn
--max_verify_retries 3
--render_workers 1
--no-resume
```

Lý do dùng `clone_mode=reference`:

- Docs/API của VoxCPM cho biết style control không dùng chung với
  prompt-text/ultimate cloning.
- Muốn biểu cảm thì phải ưu tiên controllable reference cloning.

## Trạng Thái Worker Và QC

Hiện tại kịch bản ngắn dùng **1 worker**.

Lý do:

- `@style` hiện được thực hiện bằng short wrapper override tạm
  `prepare_chunks` và `render_chunk`.
- Renderer dài dùng multiprocessing `spawn` khi multi-worker.
- Worker con có thể không nhận monkeypatch từ process cha.
- Vì vậy short wrapper ép `--render_workers 1` để đảm bảo style không bị mất.

QC hiện tại của kịch bản ngắn:

- ASR verify
- CTC probe
- speaker similarity
- retry/subsplit
- mastering

Nhưng tất cả chạy trong cùng một process chính, không chia đều trên 2 CUDA.

Truyện dài vẫn có thể dùng multi-worker/nhiều CUDA theo renderer dài.

## Dataset Cache Gate

Trước mọi lần `kaggle kernels push`, dù job dài hay job ngắn, phải chạy gate:

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

Kaggle log đúng nên có dòng tương tự:

```text
Using Kaggle Dataset snapshot for openbmb/VoxCPM2: ...
```

Nếu thấy:

```text
Fetching ... files
Model snapshot ready: /root/.cache/huggingface/...
```

thì launcher không tìm thấy dataset cache và đang tải từ Hugging Face. Phải sửa
launcher/dataset mount rồi prepare lại job, không tiếp tục coi đó là render chuẩn.

## Job Mẫu Đã Tạo

File kịch bản mẫu:

- `kich-ban/ngan/mau-style-adam-canh-cua-luc-nua-dem.md`

Nội dung hiện tại là độc thoại vui nhộn của Adam, không có đối thoại nhân vật,
có các câu test:

```text
Các bạn nghe mình nhóóó....
Đừừng....
đừng tin ai hết.
```

Đã từng push một version trước khi sửa dataset alias, nên Kaggle log có tải
Hugging Face. Sau đó đã sửa launcher và thêm Dataset Cache Gate. Không push lại
theo yêu cầu mới nhất.

Output của version cũ đã được tải về để nghe thử style:

- Result folder: `results/kaggle_voxcpm_short_mau-style-adam-vui-nhon`
- Source audio: `results/kaggle_voxcpm_short_mau-style-adam-vui-nhon/voxcpm_job_bundle/results/mau-style-adam-canh-cua-luc-nua-dem_voxcpm.wav`
- Processed 1.25x audio: `audio/mau-style-adam-vui-nhon.wav`

Lưu ý: output này **không chứng minh dataset cache đã hoạt động**, vì log của
version đó có `Fetching ... files` và `Model snapshot ready:
/root/.cache/huggingface/...`. Dùng nó để nghe thử giọng/style thôi. Muốn test
dataset cache phải prepare lại, chạy Dataset Cache Gate, rồi push version mới.

Job local mới để test gate, chưa push:

- `kaggle_jobs/mau-style-adam-vui-nhon_dataset-gate_20260720-231545`

Gate đã pass:

```text
dataset cache gate OK
```

## Việc Cần Làm Tiếp

### 1. Quyết định có cần multi-worker cho kịch bản ngắn không

Hiện tại short pipeline ưu tiên đúng style, nên chỉ 1 worker.

Nếu muốn short pipeline dùng 2 CUDA:

- Không nên dựa vào monkeypatch.
- Cần đưa `@style` thành logic chính thức mà worker con đọc được.
- Hướng tốt: short prepare/renderer viết ra chunk manifest có trường
  `style_control`, rồi renderer con nhận chunk metadata và chèn style khi
  generate.
- Sau đó mới bật `--render_workers auto` hoặc `--render_devices 0,1`.

### 2. Push lại job mẫu sau khi gate pass

Khi muốn test tiếp:

1. Prepare lại job short bằng `tools/prepare_kaggle_voxcpm_short_job.py`.
2. Chạy Dataset Cache Gate.
3. Push Kaggle.
4. Kiểm tra log có `Using Kaggle Dataset snapshot for openbmb/VoxCPM2`.
5. Nếu vẫn có `Fetching ... files` cho VoxCPM2 thì dừng và sửa mount/cache.

### 3. Nghe thử kết quả style

Sau khi Kaggle render xong:

- Download output.
- Nghe các đoạn có style khác nhau:
  - `cheerful, conversational`
  - `urgent, anxious`
  - `dramatic narration, intense`
  - `restrained anger, firm`
  - `cheerful, playful`
- Ghi lại tag nào hiệu quả, tag nào yếu hoặc làm méo giọng.
- Cập nhật `VOXCPM_STYLE_TAGS.md` theo kết quả nghe thật.

### 4. Tinh chỉnh kéo chữ

Các token như `Đừừng....`, `nhóóó....` cần nghe thực tế.

Nếu VoxCPM đọc méo:

- Thử giảm kéo chữ: `Đừng...`, `nhó...`
- Thử thay bằng ngắt câu:
  `Đừng...`
  `đừng tin ai hết.`
- Thử dùng style thay cho kéo chữ:
  `@style slow, playful`

## Lệnh Kiểm Tra Đã Chạy

```bash
python3 -m unittest tests.test_voxcpm_story_core.VoxCPMPrepareJobTests tests.test_voxcpm_story_core.VoxCPMShortPrepareJobTests tests.test_voxcpm_story_core.KaggleLauncherTests
```

Kết quả:

```text
Ran 10 tests in 0.003s
OK
```

Skill validate:

```text
Skill is valid!
Skill is valid!
```
