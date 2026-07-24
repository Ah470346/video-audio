# QC changes for chunks 0038 / 0043 / 0071

## What was actually wrong

Three chunks of the `anh-ky-don-ly-hon` 1500-word render were reported as
defective. Measuring them established that they are three different problems,
and only one of them is a rendering defect.

| Chunk | Report | Verdict |
|---|---|---|
| `0038` | strange sound at the end | **Real defect.** Junk audio after the sentence that ASR never turns into words. |
| `0043` | heard as `Tôi tôi muốn nói` | **Not an audio defect.** The audio says `còn`. The script repeats an opening. |
| `0071` | QC hard-failed `swallowed 'khi'` | **False positive.** An energy heuristic fired on audio that is correct. |

## Why the transcript could not settle it

Whisper decodes with a language model, so a locally distorted word is repaired
from sentence context. `0043` transcribed as `Tôi còn muốn nói` with CER 0.000
and similarity 1.000 while a listener heard something else, so the transcript
alone could neither confirm nor refute the report.

The fix is to read the audio again with a model that has **no** language model:
a Vietnamese wav2vec2 CTC acoustic model
(`nguyenvulebinh/wav2vec2-base-vietnamese-250h`). CTC is frame-synchronous and
carries no linguistic prior, so its greedy output reports what is acoustically
present rather than what is plausible.

Implemented in `voxcpm_ctc_probe.py`. It needs only `torch` and
`transformers`, both of which VoxCPM already installs. Three measurements come
from one forward pass per chunk: a context-free transcript, a CTC Viterbi
forced alignment with per-word posteriors, and an exact CTC forward score for
any label sequence over any frame window.

## Findings, measured over all 80 chunks

### `0038` — real, and now caught

The context-free read of the audio after the last aligned word is:

```text
neo lua mũ n hốt
```

VoxCPM appended sound that is not in the script. Whisper dropped it because it
is not plausible Vietnamese; CTC transcribes it because it does not care.

This is the **only** chunk of 80 with audio outside the sentence — one
detection, zero false positives on the other 79.

### `0043` — the audio is correct

Forced alignment puts `còn` at 0.46-0.54 s with posterior **0.994**. Scoring
the minimal pair over exactly that window:

```text
logP('còn') = -15.84
logP('tôi') = -41.95
->  log-likelihood ratio tôi/còn = -26.11 nats
```

The audio is `còn` by a factor of about 2x10^11. Across all 12 occurrences of
`còn` in the render, this one scores 0.994 against a median of 0.999.

The real cause is in the script:

```text
0041 | Tôi muốn nói, người báo cho ông nội không phải tôi.
0042 | Tôi muốn nói, Hạ Uyển không ra nước ngoài vì bị ép, ...
0043 | Tôi còn muốn nói, ngày anh uống say ...
```

Three consecutive sentences opening the same way. On the page that is
anaphora; heard back to back it registers as a stutter. No acoustic QC can
catch this and re-rendering cannot fix it, so `scan_repeated_openings` runs
once over the chunk plan and reports it as a note for the writer. Measured at
3 words / run of 2, it reports the `0041-0042` passage and nothing else in the
whole render.

### `0071` — false positive, now vetoed

The energy-and-duration heuristic called `khi` swallowed. The context-free CTC
read of that chunk is exact, including `khi ấy`. When an independent acoustic
model reads every expected word, it outranks a heuristic claiming one is
missing: `swallowed` and `local tempo` are downgraded to warnings, and the
warning stays in the report for audit. Text-mismatch and omission defects are
never vetoed.

39 of 80 chunks are veto-eligible, so the veto is selective rather than a
blanket amnesty.

## Why whisperx was removed

The earlier revision added `whisperx==3.2.0` for forced alignment. Two
independent blockers:

**The Vietnamese alignment model has no CTC head.** WhisperX maps `vi` to
`nguyenvulebinh/wav2vec2-base-vi`, whose config records
`architectures: ["Wav2Vec2ForPreTraining"]`. Loading that with
`Wav2Vec2ForCTC` silently random-initialises `lm_head`, so every alignment
score it produced was noise — and hard-fail required exactly those scores as
evidence.

**The install cannot resolve.** whisperx 3.2.0 requires
`faster-whisper==1.0.0` and `ctranslate2==4.4.0`, contradicting the
`faster-whisper==1.2.1` pin in the same list. Verified:

```text
ERROR: Cannot install faster-whisper==1.2.1 and whisperx==3.2.0 because these
package versions have conflicting dependencies.
ERROR: ResolutionImpossible
```

The Kaggle runner installs all packages in one `pip install` and raises on a
non-zero exit, so the kernel would have died before rendering a single chunk.

`voxcpm_ctc_probe.py` loads its model directly and checks the checkpoint
architecture at load time, refusing a non-CTC checkpoint instead of reporting
random numbers.

## Resume hashing split

`params_sha` previously mixed synthesis parameters with QC thresholds, so
tuning one floor invalidated every chunk and forced a full GPU re-render of
audio that had not changed. It is now `render_sha` (model, cfg, timesteps,
seed, reference) and `qc_sha` (every `verify_*`), stored separately per chunk.

## Kept from the previous revision

Retry ladder with text-lock ordering, ASR-heard repetition hard by default,
subsplit publishing when all subchunks pass, and preserved `.attempts/` WAVs
are unchanged. The energy-based tail scan is kept as a second opinion but
downgraded to a warning when the CTC probe read the tail and found nothing
there, since it cannot distinguish an artifact from the voiced decay of a
Vietnamese final nasal.

## Verification

`tests/test_voxcpm_story_core.py` — 23 tests, all passing. The CTC forward
algorithm is checked against `torch.nn.functional.ctc_loss` and agrees to
1e-3. Every number in this document was measured against the real chunk WAVs
in `results/kaggle_voxcpm_full_voxcpm-vn-audio-smoke-20260719/`.

## Open item

The tail-artifact energy thresholds in `voxcpm_story_core.py` were never
calibrated, and `DEFAULT_TAIL_ARTIFACT_GRACE_MS = 80` is short given that
Whisper tends to place a word's end early. The CTC veto limits the damage, but
the thresholds themselves are still guesses.
