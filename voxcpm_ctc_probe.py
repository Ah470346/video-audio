# -*- coding: utf-8 -*-
"""Context-free CTC probe for VoxCPM chunk QC.

Whisper decodes with a language model, so it repairs a locally distorted word
from sentence context: chunk ``0043`` rendered ``Tôi còn muốn nói`` audibly
closer to ``Tôi tôi muốn nói`` yet full-context ASR still transcribed ``còn``.
Any QC layer built on that transcript is blind to the defect by construction.

This module reads the audio again with a Vietnamese wav2vec2 CTC acoustic
model. CTC is frame-synchronous and carries no language model, so its greedy
output reports what is acoustically present rather than what is linguistically
plausible. Three measurements come out of a single forward pass:

``greedy_text``
    Context-free transcript. Non-speech junk after the sentence surfaces here
    as gibberish (chunk ``0038``), and a clean match is positive evidence that
    a timing/energy heuristic false-fired (chunk ``0071``).
``align``
    CTC Viterbi forced alignment giving per-word frame spans and posteriors.
``sequence_logprob``
    Exact CTC forward score of a label sequence over a frame window. Two
    hypotheses scored over the *same* window are directly comparable
    probabilities, which yields a threshold-free likelihood ratio instead of a
    hand-tuned score floor.

Only ``torch`` and ``transformers`` are required, both of which VoxCPM already
installs. Deliberately no whisperx: its Vietnamese entry
(``nguyenvulebinh/wav2vec2-base-vi``) is a ``Wav2Vec2ForPreTraining``
checkpoint with no CTC head, so ``Wav2Vec2ForCTC`` loads it with a randomly
initialised ``lm_head`` and every alignment score it reports is noise.
"""

import math
import re
import unicodedata

DEFAULT_CTC_MODEL = "nguyenvulebinh/wav2vec2-base-vietnamese-250h"
CTC_SAMPLE_RATE = 16000
NEG_INF = -1e30


def normalize_for_ctc(text):
    """Lowercase to the CTC character vocabulary; drop punctuation."""
    text = unicodedata.normalize("NFC", str(text or "")).lower()
    text = re.sub(r"[^0-9a-zà-ỹđ\s]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def _load_audio_16k(wav_path):
    import numpy as np
    import soundfile as sf

    y, sample_rate = sf.read(str(wav_path), dtype="float32", always_2d=False)
    if getattr(y, "ndim", 1) > 1:
        y = y.mean(axis=1)
    if sample_rate != CTC_SAMPLE_RATE:
        from math import gcd

        from scipy.signal import resample_poly

        divisor = gcd(int(sample_rate), CTC_SAMPLE_RATE)
        y = resample_poly(y, CTC_SAMPLE_RATE // divisor, int(sample_rate) // divisor)
    return np.asarray(y, dtype="float32")


class CtcProbeSession:
    """Vietnamese wav2vec2 CTC acoustic model, cached per render worker."""

    def __init__(self, model_name=None, device=None, cache_size=2):
        self.model_name = model_name or DEFAULT_CTC_MODEL
        self.requested_device = device
        self.device = None
        self.model = None
        self.processor = None
        self.blank_id = 0
        self.frames_per_sec = 50.0
        self.available = False
        self.error = None
        self._cache = []
        self._cache_size = max(1, int(cache_size))

    # -- lifecycle ---------------------------------------------------------
    def _resolve_device(self):
        requested = str(self.requested_device or "").strip().lower()
        try:
            import torch

            if requested.startswith("cuda") and torch.cuda.is_available():
                return requested
            if not requested and torch.cuda.is_available():
                return "cuda"
        except Exception:
            pass
        return "cpu"

    def load(self):
        if self.available:
            return True
        if self.error:
            return False
        try:
            import torch
            from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor

            self.processor = Wav2Vec2Processor.from_pretrained(self.model_name)
            model = Wav2Vec2ForCTC.from_pretrained(self.model_name)
            self.device = self._resolve_device()
            self.model = model.to(self.device).eval()
            config = self.model.config
            blank = getattr(config, "pad_token_id", None)
            self.blank_id = 0 if blank is None else int(blank)
            # wav2vec2 base stacks convolutions down to one frame per 20 ms.
            stride = 1
            for value in getattr(config, "conv_stride", ()) or ():
                stride *= int(value)
            self.frames_per_sec = CTC_SAMPLE_RATE / float(stride or 320)
            self._verify_ctc_head()
            self.available = self.error is None
        except Exception as exc:
            self.error = f"{type(exc).__name__}: {exc}"
            self.available = False
        return self.available

    def _verify_ctc_head(self):
        """Reject a checkpoint whose CTC head was never trained.

        ``Wav2Vec2ForCTC.from_pretrained`` silently random-initialises
        ``lm_head`` for a ``Wav2Vec2ForPreTraining`` checkpoint, and the scores
        that follow look plausible while meaning nothing. The architecture
        recorded in the config is the reliable tell.
        """
        architectures = getattr(self.model.config, "architectures", None) or []
        if architectures and not any("ForCTC" in name for name in architectures):
            self.error = (
                f"{self.model_name} is {architectures[0]}, not a CTC checkpoint; "
                "its lm_head would be randomly initialised"
            )

    def close(self):
        self.model = None
        self.processor = None
        self._cache = []
        self.available = False

    # -- emissions ---------------------------------------------------------
    def emissions(self, wav_path):
        """Log-softmax emissions ``[frames, vocab]`` for a whole chunk.

        Cached: a chunk is probed once for the tail and again for every suspect
        word, and decoding plus a forward pass is by far the expensive part.
        """
        if not self.load():
            return None
        key = str(wav_path)
        for index, (cached_key, value) in enumerate(self._cache):
            if cached_key == key:
                self._cache.append(self._cache.pop(index))
                return value
        try:
            import torch

            audio = _load_audio_16k(wav_path)
            if audio.size < 400:
                return None
            with torch.inference_mode():
                inputs = self.processor(
                    audio, sampling_rate=CTC_SAMPLE_RATE, return_tensors="pt"
                )
                logits = self.model(inputs.input_values.to(self.device)).logits[0]
                value = torch.log_softmax(logits.float(), dim=-1).cpu()
        except Exception as exc:
            self.error = f"{type(exc).__name__}: {exc}"
            return None
        self._cache.append((key, value))
        while len(self._cache) > self._cache_size:
            self._cache.pop(0)
        return value

    def frame_of(self, seconds):
        return int(max(0.0, float(seconds)) * self.frames_per_sec)

    def time_of(self, frame):
        return float(frame) / self.frames_per_sec

    # -- tokenisation ------------------------------------------------------
    def token_ids(self, text):
        """Character ids for ``text``; ``None`` when nothing is encodable."""
        normalized = normalize_for_ctc(text)
        if not normalized:
            return None
        vocab = self.processor.tokenizer.get_vocab()
        delimiter = vocab.get("|")
        unknown = vocab.get("<unk>")
        ids = []
        for char in normalized:
            if char == " ":
                if delimiter is not None and ids and ids[-1] != delimiter:
                    ids.append(delimiter)
                continue
            ids.append(vocab.get(char, unknown))
        while ids and ids[-1] == delimiter:
            ids.pop()
        if not ids or any(value is None for value in ids):
            return None
        return ids

    # -- decoding ----------------------------------------------------------
    def greedy_text(self, emissions, start_frame=None, end_frame=None):
        """Context-free transcript of a frame window."""
        if emissions is None:
            return ""
        window = emissions[
            max(0, start_frame or 0) : (
                emissions.shape[0] if end_frame is None else min(emissions.shape[0], end_frame)
            )
        ]
        if window.shape[0] <= 0:
            return ""
        ids = window.argmax(dim=-1).tolist()
        collapsed = []
        previous = None
        for value in ids:
            if value != previous and value != self.blank_id:
                collapsed.append(value)
            previous = value
        if not collapsed:
            return ""
        return normalize_for_ctc(self.processor.tokenizer.decode(collapsed))

    # -- alignment ---------------------------------------------------------
    def align(self, emissions, text):
        """CTC Viterbi forced alignment of ``text``.

        Returns one row per word with ``start``/``end`` seconds and ``score``,
        the mean posterior of the word's own characters over the frames the
        best path assigned to them. ``None`` when the text cannot be aligned
        (for example more characters than frames).
        """
        if emissions is None:
            return None
        ids = self.token_ids(text)
        if not ids:
            return None
        path = _ctc_viterbi_path(emissions, ids, self.blank_id)
        if path is None:
            return None
        vocab = self.processor.tokenizer.get_vocab()
        delimiter = vocab.get("|")
        rows = []
        current = None
        for token_index, token_id in enumerate(ids):
            frames = path.get(token_index)
            if token_id == delimiter:
                if current is not None:
                    rows.append(current)
                    current = None
                continue
            if frames is None:
                continue
            char = self.processor.tokenizer.convert_ids_to_tokens(token_id)
            posterior = sum(
                math.exp(float(emissions[frame][token_id])) for frame in frames
            ) / len(frames)
            if current is None:
                current = {
                    "word": char,
                    "start_frame": frames[0],
                    "end_frame": frames[-1] + 1,
                    "_scores": [posterior],
                }
            else:
                current["word"] += char
                current["end_frame"] = frames[-1] + 1
                current["_scores"].append(posterior)
        if current is not None:
            rows.append(current)
        aligned = []
        for index, row in enumerate(rows):
            scores = row.pop("_scores")
            aligned.append(
                {
                    "index": index,
                    "word": row["word"],
                    "start_frame": row["start_frame"],
                    "end_frame": row["end_frame"],
                    "start": round(self.time_of(row["start_frame"]), 3),
                    "end": round(self.time_of(row["end_frame"]), 3),
                    "score": round(sum(scores) / len(scores), 4),
                }
            )
        return aligned

    # -- hypothesis scoring ------------------------------------------------
    def sequence_logprob(self, emissions, text, start_frame=None, end_frame=None):
        """Exact CTC forward log-probability of ``text`` over a frame window.

        Two hypotheses scored over the same window are probabilities of the
        same conditioning audio, so their difference is a likelihood ratio and
        needs no length normalisation.
        """
        if emissions is None:
            return None
        ids = self.token_ids(text)
        if not ids:
            return None
        lo = max(0, start_frame or 0)
        hi = emissions.shape[0] if end_frame is None else min(emissions.shape[0], end_frame)
        if hi - lo <= 0:
            return None
        return _ctc_forward_logprob(emissions[lo:hi], ids, self.blank_id)


def _ctc_viterbi_path(emissions, token_ids, blank_id):
    """Best CTC alignment path; returns ``{token_index: [frame, ...]}``."""
    import torch

    frames = emissions.shape[0]
    extended = [blank_id]
    origin = [None]
    for index, token_id in enumerate(token_ids):
        extended.append(token_id)
        origin.append(index)
        extended.append(blank_id)
        origin.append(None)
    states = len(extended)
    if frames < len(token_ids):
        return None

    emit = emissions[:, torch.tensor(extended, dtype=torch.long)]
    scores = torch.full((states,), NEG_INF, dtype=torch.float32)
    scores[0] = emit[0][0]
    if states > 1:
        scores[1] = emit[0][1]
    back = torch.zeros((frames, states), dtype=torch.int8)

    # A jump of two is only legal when it skips a blank between two distinct
    # characters; between a repeated character the blank is mandatory.
    skippable = torch.zeros(states, dtype=torch.bool)
    for state in range(2, states):
        skippable[state] = extended[state] != blank_id and extended[state] != extended[state - 2]

    for frame in range(1, frames):
        stay = scores
        shift1 = torch.cat([torch.full((1,), NEG_INF), scores[:-1]])
        shift2 = torch.cat([torch.full((2,), NEG_INF), scores[:-2]])
        shift2 = torch.where(skippable, shift2, torch.full_like(shift2, NEG_INF))
        stacked = torch.stack([stay, shift1, shift2])
        best, choice = stacked.max(dim=0)
        back[frame] = choice.to(torch.int8)
        scores = best + emit[frame]

    state = states - 1 if float(scores[-1]) >= float(scores[-2]) else states - 2
    path = {}
    for frame in range(frames - 1, -1, -1):
        if origin[state] is not None:
            path.setdefault(origin[state], []).append(frame)
        state -= int(back[frame][state])
        if state < 0:
            return None
    for frames_of_token in path.values():
        frames_of_token.reverse()
    if len(path) != len(token_ids):
        # A valid CTC path visits every label state, so a gap here means the
        # backtrack broke rather than that the audio is short.
        return None
    return path


def _ctc_forward_logprob(emissions, token_ids, blank_id):
    """CTC forward algorithm: log P(token_ids | emissions)."""
    import torch

    frames = emissions.shape[0]
    extended = [blank_id]
    for token_id in token_ids:
        extended.append(token_id)
        extended.append(blank_id)
    states = len(extended)
    if frames < len(token_ids):
        return None

    emit = emissions[:, torch.tensor(extended, dtype=torch.long)]
    alpha = torch.full((states,), NEG_INF, dtype=torch.float32)
    alpha[0] = emit[0][0]
    if states > 1:
        alpha[1] = emit[0][1]

    skippable = torch.zeros(states, dtype=torch.bool)
    for state in range(2, states):
        skippable[state] = extended[state] != blank_id and extended[state] != extended[state - 2]

    for frame in range(1, frames):
        shift1 = torch.cat([torch.full((1,), NEG_INF), alpha[:-1]])
        shift2 = torch.cat([torch.full((2,), NEG_INF), alpha[:-2]])
        shift2 = torch.where(skippable, shift2, torch.full_like(shift2, NEG_INF))
        alpha = torch.logsumexp(torch.stack([alpha, shift1, shift2]), dim=0) + emit[frame]

    return float(torch.logsumexp(torch.stack([alpha[-1], alpha[-2]]), dim=0))
