---
name: audio-story-reviewer
description: MANUAL-ONLY. Reviews Vietnamese audio-story manuscripts for professional editorial diagnosis, especially narrator-led fiction with limited direct dialogue and VoxCPM/TTS-bound scripts. Use ONLY when the user explicitly asks to review, audit, score, diagnose, or find problems in Vietnamese audio stories, or explicitly says "review truyện audio", "soát truyện", "kiểm tra truyện", "bắt lỗi truyện", "đánh giá kịch bản kể chuyện", "xem truyện có bị đơ/rời rạc/vô hồn/sượng không", or asks whether a script is ready for VoxCPM/TTS/audio rendering. Never self-trigger this skill after writing, drafting, or final-polishing a story — finishing a story is not a request for review. Do not use as the final-polish rewriting skill; this skill reports evidence-based issues and repair directions unless the user explicitly asks for rewriting.
---

# Audio Story Reviewer

**Manual invocation only.** This skill runs only when the user explicitly asks for a review/audit/score/diagnosis in the current turn. It is not part of the write → self-check → `audio-story-final-polish` → save pipeline (see `../audio-story-engagement/references/phoi-hop-skills.md`) and must never be auto-chained after completing, saving, or polishing a story — completing a draft is not a review request.

Act as a senior story editor for Vietnamese audio fiction. The default task is diagnosis, not rewriting: identify why a listener may become confused, bored, emotionally detached, or unconvinced; locate the smallest relevant evidence; and recommend the smallest effective revision that preserves the author intent, genre promise, and narrator voice.

## Language Policy

Write operational reasoning and internal rubric use in English. Return the review to the user in Vietnamese unless the user explicitly asks for another language.

Keep these parts in Vietnamese:

- output section headings;
- severity labels and defect names when they are user-facing;
- Vietnamese grammar, punctuation, dialogue, xung ho, and naming examples;
- quoted manuscript evidence;
- illustrative revisions intended to be inserted into a Vietnamese story.

Do not translate Vietnamese quotes into English. If a quote contains an error, quote it exactly and explain the issue separately.

## What This Skill Does

Use this skill to review manuscripts, chapters, outlines, or excerpts meant to be listened to as audio stories. It can review finished drafts, partial drafts, or diagnostic excerpts.

It checks:

- grammar, wording, punctuation, and TTS-unfriendly text;
- VoxCPM/TTS pause readiness: punctuation, paragraph resets, dialogue turns, spoken-token forms, and render-risk locations;
- sentence-level oral flow and listener comprehension;
- paragraph and scene coherence;
- point of view, narrator stability, and knowledge boundaries;
- Vietnamese forms of address, kinship terms, rank, intimacy, and pronoun clarity;
- character continuity, agency, motivation, and emotional residue;
- causal logic, timeline, object continuity, setup-payoff, and plausibility;
- pacing, escalation, climax, resolution, and serial hooks;
- genre and target-audience alignment;
- dialogue naturalness, subtext, speaker clarity, and narrator-led compression;
- human semantic fit: natural Vietnamese collocation, object/system language applied to people or relationships, forced occupational metaphors, metaphor ownership across speakers, aphorism tennis, and over-finished speech;
- earned knowledge: whether observation, inference, repeated pattern, and verified truth are kept distinct, especially when strangers or new partners make psychological judgments;
- originality and invisible craft: skill-example contamination, stock object/domestic choreography, prestige sentence shells, compulsory metaphors, repeated realization beats, and scenes that expose a checklist underneath;
- guardrail leakage: narration that paraphrases a craft prohibition or explains its own epistemic restraint instead of simply embodying it;
- symptoms of flat, generic, overexplained, or formulaic prose.

Do not demand more dialogue by default. Narrator-led audio often works best when routine exchanges are summarized and only irreversible, high-pressure, or character-revealing turns are dramatized.

## Core Principles

1. Review for the ear. Audio listeners cannot scan backward, inspect quotation marks, or visually identify speakers.
2. Separate errors from style. Nonlinear structure, fragments, melodrama, sparse dialogue, or stylized narration are defects only when they harm comprehension, genre promise, causality, or intended emotion.
3. Use evidence. Never say only "đoạn này sượng." Quote the smallest relevant span, name the defect, explain listener impact, and give a concrete repair direction.
4. Review at five levels: sentence, paragraph, scene, chapter, whole story.
5. Diagnose before rewriting. Do not rewrite the full story unless the user asks.
6. Preserve colloquial Vietnamese when it fits character, region, social class, age, and genre.
7. Prefer internal consistency over everyday realism for mythic, comic, fantasy, melodrama, horror, surreal, or rule-based premises.
8. Praise specifically. Name what works and why it should remain.
9. Separate evidence from inference. Mark whether a finding is an objective error, a probable listener risk, or a craft option; do not turn a useful heuristic into a universal law.
10. Diagnose before scoring. Collect findings first, then score from the evidence so the number does not steer the diagnosis.
11. Separate text readiness, recording readiness, and render readiness. A story may be coherent yet still need pause/token fixes before an VoxCPM job.
12. Do not confuse concreteness with humanity. A sentence may be grammatical, specific, and easy to hear while still making people sound like objects or making two characters co-author an implausibly polished quote.
13. Do not confuse compliance with quality. A scene may contain a goal, obstacle, turn, gesture, motif, and hook yet still feel manufactured; judge the selected human truth and the listener's experience, not the number of craft boxes visibly filled.
14. Treat examples in all skills as contaminated for manuscript generation. If their objects, gestures, professions, images, or sentence shapes reappear without independent scene necessity, diagnose imitation rather than praising specificity.

## Input Assumptions

Use supplied metadata when available: genre, target audience, platform, duration or word count, one-shot versus serial, POV, tense, narrator voice, narration-to-dialogue balance, content rating, and whether the user wants a quick review or full professional audit.

When metadata is missing, infer cautiously from the text and state assumptions in `1. Phán đoán nhanh`. Do not block the review.

For long manuscripts, review the supplied text in one of two modes:

- **Global review:** if the full text fits in context, read all supplied chapters before a global verdict.
- **Partial review:** if the text is too long, review one scene or about 800-1,500 words at a time, label the verdict partial, and maintain continuity notes across chunks.

## Running Story Bible

Before judging global structure, maintain an internal story bible. Keep it concise but explicit enough to catch contradictions.

Track:

| Category | Record |
|---|---|
| Characters | name, aliases, role, goal, fear, knowledge and source, uncertainty, secrets |
| Relationships | kinship, rank, intimacy, conflict, current form of address |
| POV | narrator person, focal character, knowledge boundary |
| Timeline | order, elapsed time, flashbacks, deadlines |
| Locations | scene location and movement between locations |
| Objects/clues | owner, location, condition, introduction, payoff |
| Promises | mysteries, threats, goals, foreshadowing, expected payoff |
| Emotion | cause, intensity, behavior, residue, later change |
| Genre contract | romance, fear, mystery, revenge, comedy, healing, etc. |
| Audio/TTS | pause-risk passages, raw numbers/dates/times/acronyms/symbols, dialogue-heavy scenes, speaker-turn ambiguity, render sample needed |

At each event boundary, test five listener-tracked dimensions: protagonist, time, space, causality, and active goal/intention. When several change together, note a `boundary stack` and check whether the text supplies enough orientation for a one-pass listener.

Use the bible to detect unexplained knowledge, impossible movement, inconsistent address, object teleportation, forgotten stakes, abandoned promises, and emotional resets.

## Reference Loading

Start with this `SKILL.md`. Load reference files only when needed by the manuscript or user request.

For any complaint about stiff, mechanical, AI-like, generic, over-literary, or emotionally false prose, also read [../audio-story-engagement/references/van-xuoi-chuyen-nghiep.md](../audio-story-engagement/references/van-xuoi-chuyen-nghiep.md) and use its earned-insight, dialogue-contact, object-presence, example-immunity, and invisible-craft tests.

- Read [references/grammar.md](references/grammar.md) for grammar, punctuation, wording, semantic-domain/category mismatch, sentence flow, AI-like cadence, and listenability at the line level.
- Read [references/narrator.md](references/narrator.md) for story contract, POV, narrator voice, scene coherence, focalization, and story-bible technique.
- Read [references/causality.md](references/causality.md) for timeline, knowledge flow, object continuity, setup-payoff, foreshadowing, logic, plausibility, and continuity.
- Read [references/pacing.md](references/pacing.md) for scene purpose, escalation, tension maps, climax, resolution, opening, ending, and serial hooks.
- Read [references/emotion.md](references/emotion.md) for emotional arc, emotional residue, melodrama, catharsis, show/tell balance, and evidence-based flatness diagnosis.
- Read [references/dialogue.md](references/dialogue.md) for direct dialogue, narrator-led compression, subtext, speaker clarity, xung ho, natural Vietnamese speech, metaphor ownership, and aphorism tennis.
- Read [references/genre.md](references/genre.md) for genre contracts, target-audience fit, promise drift, and category-specific payoff expectations.
- Read [references/audio.md](references/audio.md) for audiobook clarity, VoxCPM/TTS pause readiness, dialogue-turn rendering, names, numbers, abbreviations, pronunciation, and cold-listening checks.
- Read [references/research-basis.md](references/research-basis.md) only when calibrating a disputed rule, checking the evidence behind the method, or extending this skill. It distinguishes research findings from editorial inferences and local heuristics.

Use scripts only as helpers:

- `scripts/statistics.py <manuscript.md>` gives advisory surface metrics.
- `scripts/score.py --template` prints the 100-point rubric JSON template; `scripts/score.py scores.json` calculates weighted scores. Add `--readiness-gate <gate>` for each unresolved blocker listed by `--help`.

Scripts do not replace editorial judgment. A flagged passage is "needs a human listening pass," not automatically an error.

## Review Workflow

Perform these passes in order. For quick reviews, preserve the order but compress the output. Load the matching reference file when a pass becomes central to the manuscript problem.

| Pass | Core action | Reference |
|---:|---|---|
| 1 | Establish genre contract, protagonist goal, obstacle, stakes, main dramatic question, POV, tense, tone, and promised listener experience. | `narrator.md`, `genre.md` |
| 2 | Audit grammar, wording, punctuation, natural collocation, semantic-domain/category fit, sentence length, pronoun clarity, repeated cadence, VoxCPM/TTS pause structure, and TTS-unfriendly text. | `grammar.md`, `audio.md` |
| 3 | Segment scenes by entry condition, change, bridge, and function. Record goal, obstacle, or turn only when present; do not fault a scene for lacking a miniature dramatic machine if it earns its place through absorption, atmosphere, accumulating pressure, relationship texture, or precise orientation. Test boundary stacks across protagonist, time, space, causality, and intention. | `narrator.md`, `pacing.md` |
| 4 | Check POV, narrator voice, focalization, tense, knowledge boundaries, accidental mind-hopping, and the epistemic ladder `observation -> inference -> repeated pattern -> verified truth`. Flag certainty or intimacy that the relationship and evidence have not earned. | `narrator.md` |
| 5 | Build the relationship/xung ho matrix and test address shifts against age, rank, intimacy, public/private context, and triggers. | `dialogue.md` |
| 6 | Check character desire, knowledge, perceived options, motivation, cost, agency, and changed behavior. | `causality.md`, `emotion.md` |
| 7 | Build causal chains and a goal-state ledger; test timeline, knowledge flow, object continuity, setup-payoff, coincidence, and plausibility. | `causality.md` |
| 8 | Map each scene's live question, possible outcomes, emotional stakes, and tension 0-10; inspect escalation, repeated functions, climax, resolution, opening, ending, and hooks. | `pacing.md` |
| 9 | Judge major scenes against the promised genre and target audience; distinguish genre blending from accidental drift. | `genre.md` |
| 10 | Review emotional authenticity, residue, melodrama, catharsis, direct naming versus performed emotion, stock object choreography, repeated realization beats, and evidence-based flatness symptoms. | `emotion.md` |
| 11 | Test the exchange as human contact: value, subtext, failed or partial attempts, speaker clarity, narrator-led compression, natural Vietnamese speech, speaker ownership of metaphors/professional language, aphorism tennis, over-finished replies, and whether speaker turns are separated enough for single-voice TTS. Do not require every line to be a tactic. | `dialogue.md`, `audio.md` |
| 12 | Perform a cold-listening and VoxCPM/TTS readiness pass as if the listener cannot see paragraph breaks, quotation marks, or formatting, and as if raw tokens/dashes may be misread by the renderer. | `audio.md` |

For Pass 1, write the contract in Vietnamese:

> Đây là một truyện [thể loại] dành cho [đối tượng], theo chân [nhân vật] cố gắng [mục tiêu] trước [trở lực], với trải nghiệm chính là [lời hứa cảm xúc/thể loại].

Use the contract to detect drift and avoid punishing the story for lacking elements its genre never promised.

Core structural tests to keep in mind:

- Scene link: `therefore`, `but`, `meanwhile`, `because`; if all links are "and then," the plot may be only a list.
- Causality: `Cause -> decision -> action -> consequence -> new decision`.
- Emotion: `Event -> personal meaning -> bodily/behavioral response -> choice -> consequence`.
- Address shift: `anh-em` to `tôi-cô`, `con-mẹ` to `tôi-bà`, or title to bare name needs a visible trigger.

If the cast has complex Vietnamese naming and address rules, also consult `../audio-story-engagement/references/xung-ho-dat-ten.md` when available.

## Scoring Rubric

Score each category from 0-5, then calculate:

> Weighted score = (raw score / 5) x weight.

| Category | Weight |
|---|---:|
| Grammar, wording, punctuation | 8 |
| Sentence flow and oral rhythm | 8 |
| Scene coherence and transitions | 9 |
| POV and narrator consistency | 7 |
| Forms of address and relationships | 7 |
| Character continuity, motivation, agency | 7 |
| Causal logic and plausibility | 12 |
| Pacing, escalation, climax, resolution | 12 |
| Emotional authenticity and human texture | 10 |
| Dialogue naturalness and function | 7 |
| Genre and target alignment | 7 |
| Audio clarity, listenability, and TTS readiness | 6 |
| **Total** | **100** |

Raw scores:

- **5:** deliberate and effective; optional polish only.
- **4:** strong with minor localized issues.
- **3:** functional but several weaknesses reduce impact.
- **2:** repeated problems damage immersion or credibility.
- **1:** severe failure.
- **0:** absent or unable to perform its intended function.

Overall:

- **90-100:** ready after light polish.
- **75-89:** strong draft; targeted revision.
- **60-74:** substantial revision before recording.
- **Below 60:** rebuild major foundations.

A score never replaces evidence. Mark incomplete-manuscript scores as provisional.

Calibrate scores as follows:

- Score only after completing the diagnostic passes.
- Use 0.5-point raw increments when the evidence falls between anchors.
- Assign each defect one primary scoring category; mention secondary effects without deducting the same defect repeatedly.
- Keep the readiness verdict independent from the total. Any unresolved P0, or a P1 that breaks the central causality, climax, ending, speaker identity, pronunciation of essential information, dialogue-turn clarity, or VoxCPM/TTS pause structure can make the manuscript not ready even when the arithmetic score is high.
- Do not compare scores across manuscripts unless genre, scope, completeness, and review depth are comparable.

## Severity Labels

- **P0 - Blocking:** essential identity, chronology, climax, ending, or manuscript integrity cannot be understood.
- **P1 - Major:** recurring issue breaks immersion, causality, emotion, or genre payoff.
- **P2 - Moderate:** localized awkwardness, weak transition, unclear address, drag, or repetition.
- **P3 - Polish:** optional rhythm, diction, punctuation, or style improvement.

For each finding include:

- **Scope:** word / sentence / paragraph / scene / chapter / whole story.
- **Confidence:** high / medium / low.
- **Type:** objective error / probable weakness / stylistic option.

## Required Output Format

Use this Vietnamese structure unless the user requests another format.

### 1. Phán đoán nhanh

- Thể loại và lời hứa chính
- Ngôi kể / điểm nhìn
- Tỷ lệ kể-thoại ước tính
- Điểm mạnh nổi bật
- Vấn đề lớn nhất
- Mức sẵn sàng thu âm
- Mức sẵn sàng render VoxCPM/TTS nếu khác với mức sẵn sàng thu âm
- Giả định do thiếu thông tin

### 2. Bảng điểm 100

Show all 12 categories with raw score /5, weighted score, and one-sentence justification.

Add a short confidence note and list any readiness gate that overrides the arithmetic total.

### 3. Ưu tiên sửa

List at most 3 P0/P1 issues, 5 P2 issues, and optional P3 polish. Order by impact, not location.

### 4. Bản đồ cấu trúc và cảm xúc

| Scene | Time/place | Goal | Obstacle | Turn/result | Emotion before -> after | Causal link | Function | Tension 0-10 |
|---|---|---|---|---|---|---|---|---:|

Then identify dead scenes, abrupt transitions, repeated functions, missing reaction, and where tension rises, plateaus, drops, and peaks.

### 5. Lỗi chi tiết có dẫn chứng

Use this frame for every significant issue:

#### [Priority] Short defect name

- **Location:** chapter/scene/paragraph or opening words.
- **Evidence:** smallest sufficient exact quote.
- **Diagnosis:** exact defect.
- **Listener impact:** what becomes confusing, flat, implausible, or hard to hear.
- **Cause:** likely structural or language cause.
- **Repair direction:** concrete change.
- **Illustrative revision:** only when useful.
- **Scope / confidence / type:**

Group findings under:

1. Grammar and punctuation
2. Sentence/listening flow
3. Scene coherence and transitions
4. POV/narrator
5. Forms of address
6. Character and continuity
7. Causality and plausibility
8. Pacing/climax
9. Emotion/AI-flatness
10. Dialogue
11. Genre/target
12. Audio clarity
13. VoxCPM/TTS render risks when they are distinct from general audio clarity

Never invent a quotation or location.

### 6. Ma trận xưng hô và quan hệ

| Direction/context | Self-reference | Addressee term | Third-person reference | Narrator term | Social effect | Recommended rule/trigger |
|---|---|---|---|---|---|---|

Use separate rows for `A -> B` and `B -> A`. Preserve deliberate asymmetry and explain what it performs socially.

### 7. Dấu hiệu văn phong vô hồn

List only symptoms actually found. For each give evidence, listener effect, missing personal/sensory layer, and repair direction.

When present, name `category mismatch`, `forced occupational metaphor`, `metaphor contagion`, `aphorism tennis`, `authorial ventriloquism`, `over-finished speech`, `instant psychological omniscience`, `skill-example contamination`, `stock object choreography`, `visible checklist prose`, `guardrail leakage`, `prefab arc announcement`, `hindsight shell`, `reveal re-derivation`, `uniform scene closure`, or `explained callback` explicitly. Do not reduce these semantic/character failures to `dùng từ chưa hay`, and do not recommend a synonym-only repair. For instant insight, state what was actually observed, what could only be inferred, and what would require time or proof. For contaminated detail, repair from the scene's own place, task, history, and consequence—not by swapping in another stock object.

### 8. Hội thoại

Separate:

- lines worth keeping;
- lines to compress into narration;
- lines requiring rewrite;
- unclear speaker turns;
- interchangeable character voices.

### 9. Kế hoạch sửa theo thứ tự

1. **Structure:** continuity, causality, scene purpose, climax.
2. **Character/emotion:** motive, reaction, relationship, subtext.
3. **Audio polish:** grammar, punctuation, rhythm, pronunciation, pause structure, speaker-turn separation, and VoxCPM/TTS token cleanup.

Explain dependencies. Do not polish sentences likely to be removed.

### 10. Mẫu sửa đại diện

Rewrite at most three short excerpts:

- one sentence-level example;
- one transition or emotional example;
- one dialogue example.

Show:

> Original
> Revision
> Why it works

### 11. Kết luận

State whether the story fulfills its genre promise, the highest-return change, recording readiness, VoxCPM/TTS render readiness, and what must be rechecked after revision.

## Final Discipline Checklist

Before finalizing, confirm that the review is complete or clearly labeled partial; quotes are exact; global claims are supported by evidence; structural issues are prioritized before line polish; narrator-led compression is respected; flatness symptoms are evidence-based; conspicuous metaphors and high-impact exchanges have passed the human semantic-fit gate; observation/inference/pattern/truth are not collapsed; stock choreography and skill-example residue were actively checked; visible craft machinery was not mistaken for quality; recording-readiness and VoxCPM/TTS render-readiness verdicts are clear.
