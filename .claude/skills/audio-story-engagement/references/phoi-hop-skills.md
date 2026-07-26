# Audio Story Skill Coordination

This file is the authority when several audio-story skills or subagents run together.

## Priority

Use this order when instructions conflict:

1. Safety and non-instructional handling of sensitive content.
2. The user's latest explicit requirement and approved creative choices.
3. Factual/causal consistency, human truth, and one-listen clarity.
4. Anti-template naturalness: do not turn the manuscript into rigid, uniform, over-finished AI prose.
5. Fail-closed revision/receipt protocol.
6. Main genre promise and active premise rules.
7. Optional style, trend language, motifs, packaging, and examples.

A plain sentence that is true to the character beats a clever or “complete” sentence that weakens the person. No rule creates a quota. `No change needed` is valid. Preserve intentional roughness, silence, asymmetry, fragments, and uneven attention when they remain clear and causal.

`audio-story-human-life` is retired and must not be recreated, mirrored, referenced as active, or replaced by an equivalent mandatory life-detail checklist.

## Roles and Non-Overlap

### `audio-story-trend-researcher` — user-opt-in pre-writing researcher
Owns current market evidence and broad opportunity territories only. For an opted-in story request, it receives exactly one selected platform (`TikTok`, `Facebook`, or `YouTube`) and one selected format (`video dài (trên 5 phút)` or `Short (30-90 giây)`). It never creates a concrete premise, plot, character, title, hook, or publishing package.

### `audio-story-engagement` — always-active main writer
Owns concrete ideation, story contract, causality, character agency, narrator-led default, anti-template prose, Vietnamese `xưng hô`, drafting, revision state, and output status.

### `audio-story-architect` — optional structural handoff
Use only when complexity, length, episodic continuity, investigation, multiple timelines, ensemble knowledge, or special rules justify it. It maps a selected direction and never writes prose, selects a new premise, or issues receipts. Its fields are descriptive, not mandatory beats.

### One `audio-story-genre-*` — main genre
Owns the audience promise, genre scene engine, peak, payoff, and genre-breaking mistakes. Secondary genres contribute selectively and never steal the ending.

### `audio-story-premise-*` — only when triggered
Owns special knowledge, world/mechanism rules, limits, divergence, and costs. Premise never replaces character choice or genre payoff.

### `audio-story-youth-trend-language` — manual only
Owns only researched contemporary slang/wordplay and spoken form. It never repairs plot, emotion, character, or pacing.

### `audio-story-series-continuity` — optional factual continuity
Use only for episodic/shared-world risk. It checks persistent canon and proposes a bible patch. It never judges entertainment, edits prose, or issues receipts.

### `audio-story-developmental-editor` — mandatory read-only manuscript gate
Owns whole-story promise, propulsion, scene-state progression, agency, adaptive opposition, differentiation, emotional residue, predictability/fairness, setup/payoff, peak, ending, audio memory load, and systematic AI-template stiffness. It diagnoses with evidence and emits `DEVELOPMENT_RECEIPT`; it never edits.

It must not demand a uniform scene formula, regular twist cadence, more dialogue, more description, or generic “lived detail.” It routes the smallest responsible repair.

### `audio-story-scene-doctor` — bounded repair writer
Runs only on named findings and named scenes/ranges. It may compress, dramatize, or rebuild that scope while preserving protected roughness and approved choices. It updates revision/hash and invalidates stale receipts; it never issues quality receipts or beautifies the full manuscript.

### `audio-story-literary-texture` — optional surface repair
Use only when a causally sound passage remains generic, over-explained, or rhythmically flat. It may delete, reorder attention, choose a more exact fact, or use one owned image. It must not add ornamental realism, compulsory metaphors, or a new “human-life” checklist.

### `audio-story-clarity-check` — read-only first-hearing checker
Targeted mode is optional. Full-draft mode is mandatory in `stage: pre-polish` before final polish and `stage: post-polish` after final polish. It owns local actor/referent/speaker/semantic-landing/syntax/cadence failures only.

### `audio-story-final-polish` — mandatory last content editor
Runs only when current developmental and clarity receipts are clean. It preserves protected roughness, removes systematic machine signatures, and performs the smallest line/logic/audio edits. Its changes invalidate input receipts.

### `audio-story-completion-gate` — mandatory read-only release gate
Runs after final polish plus current clean post-polish development and clarity receipts. It verifies protocol-v2 sidecar state and validator output. It alone can issue `GATE_PASS`.

### `audio-story-reviewer` — manual only
Runs only when the user asks for review/audit/score. It diagnoses and prioritizes but cannot replace development, clarity, polish, or completion receipts.

### `audio-story-platform-packaging` — post-gate derived assets
Owns titles, cover/thumbnail concepts, captions, descriptions, clip boundaries, CTAs, platform variants, and experiments. It never edits the canonical story.

### `story-to-audio`
Owns rendering only and requires a protocol-v2 final gate.

### `audio-story-performance-analyst` — optional post-publication analyst
Uses real evidence to separate topic, packaging, opening, story, clarity, pacing, audio/TTS, distribution, and policy hypotheses. It never edits or issues receipts.

## Revision Rules

- Story text stays pure; state lives in sibling `<story>.gate.json`.
- New and migrated manifests use `protocol_version: 2`.
- Increment revision after every byte-changing story edit and recompute SHA-256.
- A receipt is valid only for its exact revision/hash and mode.
- No component may copy a receipt to another revision. Final polish preserves validated input receipts only as historical `pre_polish_*` evidence bound to their original revision/hash.
- Working drafts may be saved or shown only as `UNVERIFIED DRAFT`.
- Missing tools, required subagents, or validator means the manuscript cannot be called complete.
- Packaging files are derived artifacts and record source revision/hash plus a stable variant ID.

## Standard Workflow

1. Before `audio-story-engagement` starts, ask: `Bạn có muốn sử dụng nghiên cứu xu hướng mạng xã hội cho truyện này không?` unless the prompt has already answered clearly.
2. If the answer is no, decline trend research, skip the researcher and begin `audio-story-engagement` immediately. Do not ask about platform or format.
3. If the answer is yes, ask for one platform in this exact set: `TikTok`, `Facebook`, `YouTube`.
4. Once the platform is set, ask for one format: `video dài (trên 5 phút)` or `Short (30-90 giây)`.
5. Reuse any clear answer already supplied in the user's prompt, and ask only for the first missing answer. Normalize `fb` to `Facebook`, `ytb`/`yt` to `YouTube`, `dài`/`long`/`>5p` to `video dài (trên 5 phút)`, and `short`/`30-90s` to `Short (30-90 giây)`. Do not lock a story contract, generate directions, or draft while an opted-in answer or research handoff is pending.
6. Invoke `audio-story-trend-researcher` only after the opted-in platform and format are both set. Pass `RESEARCH_MODE: story_intake`, the exact selection, and relevant story context; use its report as constraints, not a plot.
7. Lock listener contract, main genre, POV, setting, length, plot question, emotional question, ending, and anti-template risks.
8. Add only premise/lexical skills triggered by the brief.
9. Use architect only when complexity warrants it; never force it onto a simple story.
10. Draft with the smallest active set and no quotas.
11. Run full-draft development; repair only supported findings; rerun development after any edit.
12. Use literary texture only for causally sound generic passages; rerun development after any edit.
13. Run full-draft clarity in `stage: pre-polish`; after any edit, rerun full-draft development and clarity.
14. Run final polish.
15. Run post-polish full-draft development and full-draft clarity in `stage: post-polish`.
16. If either post-polish check leads to text changes, invalidate the current final chain; on the repaired revision rerun developmental review and `stage: pre-polish` clarity until clean, then rerun final polish and both post-polish checks.
17. Run completion gate and validator.
18. Save/return/package/render as final only when protocol-v2 receipts match current revision/hash.
19. Use packaging after gate and performance analysis only after real publication data exists.

Do not stack every available component. Use the smallest set that serves the story, but never omit mandatory production gates. The absence of a technique is not a defect.
