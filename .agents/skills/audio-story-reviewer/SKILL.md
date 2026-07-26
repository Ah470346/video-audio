---
name: audio-story-reviewer
description: MANUAL-ONLY senior editorial review for Vietnamese audio fiction. Use only when the user explicitly asks to review, audit, score, diagnose, or assess recording/TTS readiness. It reviews story, character, causality, prose, dialogue, genre, and one-listen audio clarity. It diagnoses and prioritizes; it rewrites only when explicitly requested.
---

# Audio Story Reviewer

Return the review in Vietnamese unless the user asks otherwise. Diagnose from manuscript evidence; do not turn preferences into universal errors.

Use:
- `../audio-story-engagement/references/van-xuoi-chuyen-nghiep.md`
- `../audio-story-engagement/references/hoi-thoai-mot-giong-va-nhip-cau.md`
- `references/grammar.md`, `references/dialogue.md`, or `references/audio.md` only when that area is central.

Do not auto-run `audio-story-clarity-check` in a review-only task. The reviewer can identify the same symptom in context and owns severity/readiness judgment.

## Review Principles

- Review for the ear: listeners cannot scan backward or see formatting.
- Separate objective error, probable listener risk, and optional craft choice.
- Quote the smallest relevant evidence.
- Preserve genre, narrator voice, colloquial language, and deliberate ambiguity.
- Do not demand more dialogue, more twists, more description, or more metaphors by default.
- Do not accuse the author of using AI; name textual symptoms.
- Praise specifically and preserve what works.
- Diagnose before scoring or rewriting.

## Compact Story Bible

Track only what is needed:
- characters, aliases, goals, knowledge, secrets;
- relationships and `xưng hô`;
- POV and knowledge boundary;
- timeline, locations, objects/evidence;
- open promises and genre contract;
- emotional cause and residue;
- audio-risk passages.

## Review Passes

### 1. Contract and structure
Identify main genre, central question, protagonist goal, stakes, main opposition, peak, ending, and promised listener reward. Check whether scenes build toward and pay them.

### 2. Logic and knowledge
Check cause-and-choice chains, timeline, access, evidence scope, world rules, object continuity, setup/payoff, and what each character can know.

### 3. Character and emotion
Check agency, motive, available alternatives, responsibility, distinct relationships, earned intimacy/insight, reaction timing, and lasting consequences.

### 4. Prose and rhythm
Check natural Vietnamese, collocation, referents, abstraction, sentence landing, overloaded syntax, choppy action-report runs, repetitive prestige shells, generic details, and visible craft machinery.

### 5. Dialogue and `xưng hô`
Check value of direct speech, separate voices, exposition, subtext, address forms, speaker-chain clarity after stripping formatting, over/under-tagging, decorative action beats, and polished slogan exchanges.

### 6. Genre, peak, ending, audio
Check genre-specific payoff, fairness/rules, peak amplitude, closure, scene orientation, spoken tokens, punctuation, speaker turns, and recording/render blockers.

## Severity

- **Blocker:** core identity, chronology, causality, climax, ending, or speaker ownership cannot be followed.
- **Major:** materially weakens belief, emotion, genre payoff, or recording readiness.
- **Moderate:** repeated friction that reduces flow or distinctiveness.
- **Minor:** local wording/punctuation issue.
- **Option:** valid alternative, not a defect.

## Finding Format

For each important finding:

```text
[Mức độ] Tên lỗi
Dẫn chứng:
Tác động khi nghe:
Vì sao xảy ra:
Hướng sửa nhỏ nhất:
Ví dụ minh họa: <only when useful>
```

Useful defect labels include:
- unclear actor/referent;
- formatting-dependent speaker;
- speaker-chain ambiguity;
- over-tagging / decorative action beat;
- dangling semantic landing;
- mechanical fragment cadence;
- overloaded sentence;
- address drift;
- unearned knowledge;
- causal gap;
- evidence overclaim;
- emotional reset;
- genre promise drift;
- over-finished/AI-like cadence.

## Default Output

1. **Phán đoán nhanh:** genre, strengths, main risk, assumptions.
2. **Ba đến năm ưu tiên sửa:** ordered by impact.
3. **Lỗi có dẫn chứng:** only meaningful findings, grouped by level.
4. **Điểm mạnh cần giữ.**
5. **Trạng thái sẵn sàng:**
   - text readiness;
   - recording readiness;
   - VoxCPM/render readiness.
6. **Kết luận:** ready / light polish / targeted revision / substantial revision / not ready.

Provide a 100-point score only when the user asks for scoring. When scoring, use:
- story/causality 20;
- character/emotion 20;
- genre/structure/payoff 15;
- prose/natural Vietnamese 15;
- dialogue/`xưng hô` 10;
- one-listen audio/TTS 15;
- originality/invisible craft 5.

A high score cannot override a readiness blocker.
