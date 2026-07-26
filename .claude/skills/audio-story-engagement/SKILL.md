---
name: audio-story-engagement
description: |
  Base skill for all Vietnamese audio-story fiction. Always use for writing, expanding, rewriting, or completing narrative fiction. Owns the story contract, causality, character agency, narrator-led prose, anti-template naturalness, one-listen clarity, TTS-ready text, workflow, and fail-closed completion state. Combine with one main genre skill and only the premise/lexical modifiers actually triggered.
---

# Audio Story Engagement

Write Vietnamese fiction that a listener can understand in one pass and experience as human, natural, specific, and worth retelling.

Follow:
- [references/phoi-hop-skills.md](references/phoi-hop-skills.md)
- [references/van-xuoi-chuyen-nghiep.md](references/van-xuoi-chuyen-nghiep.md)
- [references/hoi-thoai-mot-giong-va-nhip-cau.md](references/hoi-thoai-mot-giong-va-nhip-cau.md)
- [references/premise-originality.md](references/premise-originality.md)
- [references/listener-propulsion.md](references/listener-propulsion.md)
- [references/character-voice-lived-detail.md](references/character-voice-lived-detail.md)
- [references/completion-gate-protocol.md](references/completion-gate-protocol.md)

## First Craft Priority — Do Not Sound Like A Writing Template

After safety, user intent, causality, and one-listen clarity, protect the manuscript from AI-like uniformity.

- No checklist creates a quota.
- Do not make every scene use the same beat order, every paragraph land on a thesis, every character speak with equal polish, or every emotion receive a gesture and explanation.
- Preserve useful roughness, fragments, silence, practical speech, uneven attention, delayed understanding, and plain sentences when they belong to the person and moment.
- A scene may be quiet, transitional, observational, or unresolved when it changes the lived state or prepares a necessary choice.
- `No change needed` is a valid editorial result.
- Never activate or recreate `audio-story-human-life`; its former checklist-driven role is intentionally retired because it made prose rigid. Human specificity now comes from character-owned choice, voice, attention, consequence, and evidence—not from mandatory “life details.”

## Project Defaults

Unless the user says otherwise:
- first-person narration;
- modern China / Vietnamese `truyện dịch` register;
- Chinese-style Hán-Việt names and matching institutions;
- narrator-led single-voice audio, not multi-actor drama;
- pure Vietnamese story text for VoxCPM/TTS.

The setting may be Chinese, but sentence order, collocation, emotional logic, and spoken rhythm must remain natural Vietnamese rather than translated syntax.

User instructions override these defaults within safety, logic, and one-listen clarity.

## Social Trend Research Intake

Before using this skill's Story Contract, ideation, or drafting rules for a new Vietnamese fiction request, complete the social-trend intake in [references/phoi-hop-skills.md](references/phoi-hop-skills.md).

- Ask whether the user wants social-media trend research unless they have already given an unambiguous answer.
- If they decline, skip trend research and begin this skill immediately.
- If they opt in, collect one platform (`TikTok`, `Facebook`, or `YouTube`) and then one format (`video dài (trên 5 phút)` or `Short (30-90 giây)`) before invoking `audio-story-trend-researcher`.
- Do not lock the story contract, propose directions, or draft until the opted-in research handoff is returned.
- Treat answers already present in the original prompt as settled; ask only for the missing step. Normalize `fb` to `Facebook`, `ytb`/`yt` to `YouTube`, `dài`/`long`/`>5p` to `video dài (trên 5 phút)`, and `short`/`30-90s` to `Short (30-90 giây)`.

## Story Contract

Before drafting, lock only what matters:

```text
Target listener, format, and promised reward:
Main genre:
POV, narrator distance, setting, and length:
Plot question:
Emotional question:
Protagonist goal, fear, and meaningful choice:
Main opposition/pressure:
Ending type or required outcome:
Premise rules and knowledge limits, if any:
One main peak:
Likely stop-listening and AI-template risks:
```

Do not manufacture missing fields when the brief already supplies them. Ask for approval only when the user requests options or when a major creative decision truly cannot be inferred. A detailed brief is enough to proceed.

For open-ended idea requests, propose a few genuinely different directions before drafting. For direct writing requests, choose a defensible direction and write.

## Map Before Drafting

Create the smallest internal map that prevents real risk:
- cause-and-choice chain;
- listener question ledger and planned payments;
- what each major character knows and from where;
- relationship and `xưng hô` state;
- character voice fingerprints only for major speakers;
- promises/clues that need payoff;
- scene sequence, scene-state changes, and one main peak;
- emotional residue that must survive later scenes;
- special rules, limits, and consequences;
- high-risk audio passages: multi-speaker dialogue, dense reveals, similar names, tokens;
- likely genericity: scenes, gestures, objects, reactions, or sentence shapes that could be moved unchanged into another story.

This map is descriptive, not a screenplay form. Do not fill every field for every scene. Every important scene must provide story value, but it need not display a visible formula.

Use `audio-story-architect` only for complex, long-form, episodic, multi-threaded, investigation, special-mechanism, or high-memory-load work. It is optional for straightforward stories and never writes prose.

## Drafting Rules

### Narrator is the spine
Use narration to orient scenes, compress routine communication, connect cause to consequence, and carry psychology. Keep direct dialogue when exact wording matters.

### Character and causality
Give major characters goals beyond the plot function, uneven knowledge, agency, and motivated mistakes. Outcomes follow choices and established rules.

### Human variation, not decorative realism
Let detail come from the current goal, work, money, body, status, relationship, place, and consequence. Do not add meals, keys, phones, rain, documents, body symptoms, domestic chores, or small gestures merely to make a scene seem “lived in.”

### One-listen clarity
The listener may infer emotion, motive, subtext, and mystery answers. They must not guess basic identity, actor, object, location, action method, or causal premise.

Repeat names, relations, or titles when pronouns become ambiguous. Ear clarity beats fear of repetition.

### Natural prose
Prefer plain exact Vietnamese over ornate or abstract wording. Preserve fragments, slang, direct emotion, silence, asymmetry, and roughness when they belong to the voice. Do not turn every feeling into a gesture, every profession into metaphor, every exchange into balanced slogans, or every scene into a quotable closer.

### Audio/TTS
Use punctuation and paragraphs as a performance map. Separate speaker turns, normalize consequential tokens, and do not depend on visual formatting or unsupported production tags.

## Revision State

For every complete manuscript, maintain a sidecar `<story-name>.gate.json` outside the pure story file.

- Use `protocol_version: 2` for new or migrated sidecars.
- Start `current_revision` at 1.
- Increment it after every story-text change, including one punctuation mark.
- Recompute SHA-256 after every change.
- A receipt is valid only for the exact revision and hash it names.
- Never copy a receipt forward to a changed revision.

Working drafts may be shown or saved, but must be labeled `UNVERIFIED DRAFT`. They are not complete, exportable, or renderable.

## Mandatory Development Checks

`audio-story-developmental-editor` is read-only and owns manuscript-scale quality diagnosis.

- Run full-draft development after the draft and after any scene-doctor, literary-texture, or main-writer change until the current revision has a clean `DEVELOPMENT_RECEIPT` in `mode: developmental`.
- Repeated AI-template stiffness—uniform scene machinery, overly finished dialogue, equal sentence cadence, compulsory gestures, explain-after-impact, or generic reactions—is a major finding when it materially affects the manuscript.
- The editor must cite evidence and route the smallest repair. It may not rewrite, impose quotas, or demand “more life detail.”
- After final polish, run it again in `mode: post-polish` on the polished revision. Only this current post-polish receipt satisfies protocol v2.

## Clarity Checks

`audio-story-clarity-check` is read-only.

- Targeted checks on risky passages are recommended, not quota-driven.
- A full-draft check is mandatory before final polish.
- If it returns findings, adjudicate them, change the manuscript, increment the revision, and rerun full-draft development and clarity until both receipts are clean for the current hash.
- After final polish, run another mandatory full-draft clarity check on the polished output with `stage: post-polish`.
- Any text change after either post-polish check invalidates the current final-polish chain. On the repaired revision, rerun developmental review in `mode: developmental` and clarity in `stage: pre-polish` until both are clean before entering final polish again.

## Fail-Closed Workflow

1. Complete the social-trend intake; when the user opts in, use the returned platform-and-format-specific research handoff.
2. Lock the contract and main genre.
3. Use `audio-story-architect` only when structural complexity justifies it.
4. Draft with the smallest active skill set and no craft quotas.
5. Run targeted clarity checks where useful.
6. Run mandatory full-draft development in `mode: developmental`.
7. Route bounded findings to the main writer or `audio-story-scene-doctor`; use literary texture only for causally sound but generic passages. After any change, rerun full-draft development.
8. Run mandatory full-draft clarity. After any change, rerun full-draft development and clarity.
9. Run `audio-story-final-polish` only when the current development and clarity receipts are clean.
10. On the polished output, run full-draft development in `mode: post-polish` and full-draft clarity in `stage: post-polish`.
11. If either post-polish check causes a text repair, increment revision and invalidate the current final chain. On the repaired revision, rerun full-draft development in `mode: developmental` and clarity in `stage: pre-polish` until clean, then rerun final polish and both post-polish checks.
12. Invoke `audio-story-completion-gate` and run the protocol-v2 validator.
13. Save, return, package, or render as final only after `GATE_PASS` matches the current revision/hash.

If the environment cannot invoke the required subagents or validator, do not claim completion. Return only an `UNVERIFIED DRAFT` and name the unavailable gate.

## Peak and Ending

One scene should carry the highest convergence of established threads, cost, witnesses/opposition, and irreversibility. Give it more room than ordinary scenes.

The ending must answer the plot question and settle the present emotional choice through a changed lived state. Do not add an unprepared twist, moral summary, or sequel hook that leaves the original debt unpaid.

## Safety

For sensitive material, keep the event clear while removing instructional, imitable, romanticized, or shock-only detail. Use [references/an-toan-tu-vung.md](references/an-toan-tu-vung.md) when self-harm, sexual violence, minors, or graphic harm are central.

## Output

For complete scripts, save under:

`/Users/truongdv/Documents/projects/video-audio/kich-ban/<main-genre>/`

Use a lowercase unaccented hyphenated filename. The story file contains story only: no heading, metadata, craft notes, SSML, separators, SFX/BGM, or production directions unless explicitly requested.

Store gate state in the sibling sidecar:

`<story-name>.gate.json`

Do not mark the manuscript final, return it as production-ready, or send it to `story-to-audio` without a valid final gate receipt.

## Final Check

- The manuscript does not read like a visible checklist or AI writing template.
- Plot question, emotional question, peak, and ending are paid.
- Choices cause consequences; world/premise rules hold.
- Characters have agency, distinct relationship-specific voices, and earned knowledge.
- Vietnamese `xưng hô`, collocation, syntax, and register fit.
- Dialogue is worth hearing and speakers remain clear without visual formatting.
- Reflective lines have a recoverable literal meaning.
- Sentence rhythm is varied without compulsory “variety” edits.
- Details arise from this story, not skill examples or generic realism props.
- Tokens and punctuation are TTS-ready.
- Pre-polish development/clarity evidence matches the final-polish input, and current post-polish development, clarity, and final-polish receipts form one designated-issuer protocol-v2 chain.
- Completion gate returned `GATE_PASS` for that same revision/hash.
