# Render Checkpoint: first_1000_words

Updated: 2026-07-17

## Muc tieu dang lam

Chay lai tu dau pipeline render audio cho story:

- Input: `kich-ban/drama/thien-kim-gia-thue-toi-dong-vai-thien-kim-that.md`
- Gioi han: `--story_word_limit 1000`
- Script: `convert_script_to_audio_k2fsa.py`
- Voice: `NGOC HUYEN V2`

## Phat hien quan trong

Da tim ra loi goc khien OmniVoice chet som:

- `OmniVoice.from_pretrained(..., device_map="mps", dtype=torch.float16)` bi crash khi load weights tren MPS.
- Thu nghiem toi gian ngoai script cung bi loi.
- `device_map="mps", dtype=torch.float32` load thanh cong.
- `device_map="cpu", dtype=torch.float32` cung load thanh cong.

## Cach da sua

Da sua shim local tai:

- `tools/omnivoice_no_edge_fade/sitecustomize.py`

Shim nay hien dang lam 2 viec:

1. Tat edge fade/pad cua OmniVoice.
2. Neu OmniVoice chay tren `mps` va yeu cau `torch.float16`, tu dong doi sang `torch.float32`.

Bien moi truong danh dau khi override dtype:

- `K2FSA_OMNIVOICE_MPS_SAFE_DTYPE_ACTIVE=float32`

## Trang thai run dang do

Da xoa bo cu `first_1000_words` roi chay lai tu dau.

Lenh da chay:

```bash
python3 convert_script_to_audio_k2fsa.py \
  --input kich-ban/drama/thien-kim-gia-thue-toi-dong-vai-thien-kim-that.md \
  --story_word_limit 1000 \
  --no-resume
```

Sau khi fix MPS, full render da chay duoc va da sinh ra chunk WAV.

Trang thai luc tam dung:

- Tong chunk du kien: `32`
- Chunk da render xong: `18`
- Process da duoc dung thu cong tam thoi
- Log hien tai ket thuc voi `SIGTERM` do dung chu dong, khong phai crash moi

## Artifact hien co

- Thu muc chunk:
  `results/thien-kim-gia-thue-toi-dong-vai-thien-kim-that_first_1000_words_k2fsa_ngoc_huyen_v2_chunks`
- Log:
  `results/thien-kim-gia-thue-toi-dong-vai-thien-kim-that_first_1000_words_k2fsa_ngoc_huyen_v2_render.log`

Chua co file final WAV vi run chua di het:

- Chua concat final
- Chua co `*_chunk_verify.json` cho full run nay
- Chua quan sat duoc vong QA/retry day du cua 32 chunk

## Cach tiep tuc sau nay

Neu muon di tiep tu cho dang do, uu tien dung resume:

```bash
python3 convert_script_to_audio_k2fsa.py \
  --input kich-ban/drama/thien-kim-gia-thue-toi-dong-vai-thien-kim-that.md \
  --story_word_limit 1000 \
  --resume
```

Ky vong khi resume:

- Bo qua 18 chunk WAV da co
- Render tiep cac chunk con lai
- Sau do chay `verify_chunks`
- Neu chunk nao fail hard thi se retry theo `max_verify_retries=1`
- Neu qua verify thi moi stitch pause va concat final WAV

## Neu can chay lai sach tu dau

Xoa cac artifact lien quan den bo `first_1000_words` roi chay lai voi `--no-resume`.

## Ghi chu cho lan tiep theo

- Neu muon xem hanh vi QA/retry that su, nen tiep tuc bang `--resume` tu moc hien tai.
- Muc tieu tiep theo la lay duoc:
  - danh sach chunk fail verify pass 1
  - chunk nao bi retry
  - chunk nao van fail sau retry
  - file `*_chunk_verify.json`
  - danh gia audio final sau stitch pause
