---
name: audio-story-final-polish
description: Mandatory final manuscript-editing pass for every Vietnamese audio story being returned as final, production-ready, packaged, exported, or rendered. Run only after the current full draft has clean developmental and clarity receipts. It does not run for bounded local edits unless the user explicitly requests full-manuscript release validation. Its first craft task is preserving human irregularity while removing systematic AI-template stiffness. It repairs logic, motivation, dialogue, xưng hô, natural Vietnamese, one-listen clarity, rhythm, and TTS readiness without changing approved intent. It emits a protocol-v2 receipt but never declares completion; the output still requires post-polish full-draft development, clarity, and completion gate.
---

# Audio Story Final Polish

Edit the manuscript itself. Preserve approved premise, main genre, POV, ending, voice, and protected roughness. Do not add techniques, details, dialogue, twists, motifs, or emotional beats merely to satisfy a checklist.

Use the base skill and its active references, especially `phoi-hop-skills.md`, `van-xuoi-chuyen-nghiep.md`, `hoi-thoai-mot-giong-va-nhip-cau.md`, and `completion-gate-protocol.md`.

## Scope

Do not run this skill for a bounded edit to an existing manuscript. Return that edit as `UNVERIFIED DRAFT` after only proportionate local checking. Run this skill only for the release workflow.

## Entry Gate

Require both receipts for the current revision/hash:
- clean complete full-draft `DEVELOPMENT_RECEIPT` in `mode: developmental`, issued by `audio-story-developmental-editor`;
- clean complete full-draft `CLARITY_RECEIPT` in `stage: pre-polish`, issued by `audio-story-clarity-check`.

If either is missing, stale, partial, invalid, or has blocking findings, return `POLISH_BLOCKED`.

## Pass 0 — Protect Voice And Remove Template Machinery

Before editing, record protected strengths: useful fragments, silence, asymmetry, plain lines, colloquial roughness, deliberate repetition, delayed understanding, and relationship-specific awkwardness.

Then find systematic—not isolated—machine signatures:
- repeated paragraph theses, aphorisms, teaser endings, or explain-after-impact lines;
- equal polish and self-knowledge across characters;
- balanced slogan exchanges and paired metaphors;
- compulsory gestures, objects, body symptoms, or “lived detail” inserts;
- scenes repaired into identical trigger-choice-consequence presentation;
- mechanical sentence variation, short-line runs, or recurring prestige shells;
- repeated emotional restatement and complete closure of every beat.

Repair by deletion, compression, plain naming, restored omission, relationship-specific wording, or a more exact existing fact. Do not “humanize” with additional props. Never recreate `audio-story-human-life`.

## Pass 1 — Lock Facts

Record privately premise, POV, setting, ending, user constraints, timeline, knowledge, relationships/`xưng hô`, evidence/promises, rules, protected strengths, and audio-risk passages.

## Pass 2 — Logic, Momentum, And Scene Life

Check only meaningful scene functions; do not force every scene through a visible formula.

Repair:
- events without cause, access, evidence, or motivated choice;
- scenes entering too early through routine logistics or leaving before consequence;
- repeated scene functions, accusation loops, reveal restatement, and empty interruption;
- decisive choices summarized while routine movement is dramatized;
- forgotten consequences and unsupported twists.

A quiet absorption scene may remain when it changes the next action, relationship, or interpretation.

## Pass 3 — Character And Emotion

Check goal, options, motive, cost, agency, evidence limits, adaptive opposition, and emotional residue. Preserve delayed or incomplete reactions. Use direct emotion, thought, silence, action, later consequence, or no added sentence according to character—not a compulsory gesture.

## Pass 4 — Dialogue And `Xưng Hô`

Keep exact speech when wording matters. Check speaker ownership by ear, age/rank/intimacy/context, exposition, slogan exchanges, decorative action beats, and motivated address shifts. Preserve practical replies, fragments, interruption, failed articulation, and silence when clear.

## Pass 5 — Prose And Rhythm

Repair by meaning unit:
- unclear actor/action/object or pronoun;
- false connectors, unsupported abstraction, semantic under-landing;
- translated syntax/collocation;
- repeated prestige shells, reveal restatement, generic choreography;
- mechanical `subject + small action` runs and identical openings;
- overloaded syntax and breathless quotes;
- regularized sentence variation that sounds edited by rule.

Keep plain or rough lines when they work. Do not lengthen every fragment, shorten every long sentence, or decorate every emotion.

## Pass 6 — Genre, Peak, And Ending

Verify main genre reward, fair setup, peak convergence and room, character-caused climax, payment of plot/emotional questions, and a changed lived state. Remove moral summaries, unnecessary callback explanations, and unprepared sequel hooks.

## Pass 7 — Audio/TTS

Simulate continuous listening for scene orientation, names/pronouns/speakers, breath resets, spoken forms of consequential tokens, and absence of unsupported markup. Text readiness does not certify engine pronunciation.

## Receipt

After editing:
1. increment revision if bytes changed;
2. compute output SHA-256;
3. move the validated input `development_receipt` and `clarity_receipt` into `pre_polish_development_receipt` and `pre_polish_clarity_receipt`, still bound to their original revision/hash;
4. clear the current `development_receipt`, `clarity_receipt`, and `completion_gate_receipt` slots so only fresh post-polish checks can repopulate them;
5. write:

```text
FINAL_POLISH_RECEIPT
protocol_version: 2
issued_by: audio-story-final-polish
status: completed
input_revision: <revision received>
input_sha256: <hash received>
output_revision: <current revision>
output_sha256: <current hash>
```

## Exit Gate

On the polished output run:
- full-draft `audio-story-developmental-editor` in `mode: post-polish`;
- full-draft `audio-story-clarity-check` in `stage: post-polish`.

If either post-polish check leads to a text repair, increment revision and invalidate the current final chain. On that repaired revision, rerun developmental review in `mode: developmental` and clarity in `stage: pre-polish` until both are clean. Only then rerun this entire final polish followed by both post-polish checks. Never copy a receipt to a different revision/hash.
