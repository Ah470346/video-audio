---
name: audio-story-platform-packaging
description: |
  Package a completed Vietnamese audio story for TikTok, YouTube, YouTube Shorts, and Facebook Reels without editing the canonical manuscript. Use when the user asks for titles, thumbnail concepts, opening-frame text, captions, descriptions, chapters, clip selection, short-form adaptations, platform variants, publishing packages, or A/B test plans. Production packaging requires a valid GATE_PASS; draft packaging must be labeled UNVERIFIED PACKAGING.
---

# Audio Story Platform Packaging

Turn one finished story into platform-specific publishing assets while preserving the manuscript as the source of truth.

This skill owns the **external promise**: title, thumbnail, first frame, teaser selection, caption, description, chapters, clip boundaries, CTA, and experiment plan. `audio-story-engagement` owns the story's internal opening, causality, character, peak, and ending.

## Entry State

For production-ready packaging, require:
- the canonical story path;
- sibling `.gate.json`;
- a current valid `GATE_PASS_RECEIPT`;
- the intended platform and format.

Validate the story gate before creating production assets:

```bash
python3 agent-tools/agent-workflow/validate_story_gate.py \
  --story <story.md> \
  --manifest <story.gate.json> \
  --mode final
```

If the story is not gated, packaging ideas may be explored only as `UNVERIFIED PACKAGING`. Never imply that a draft is ready to publish or render.

## Non-Destructive Rule

Never edit the canonical story or its gate sidecar. Derived cuts, captions, and metadata belong under:

```text
distribution/<story-slug>/<platform>/<variant>/
```

Record the source story revision and SHA-256 in the packaging manifest.

## Shared Packaging Rules

- Promise only what the story actually pays.
- Reveal enough context for a first-time listener; do not depend on a prior part unless explicitly building a series.
- Make variants genuinely different in angle, not synonym swaps.
- Preserve names, relationships, chronology, and factual meaning.
- Do not manufacture outrage, accusations, legal claims, or “true story” framing.
- Do not copy competitor titles, hooks, captions, or visual identity.
- A clip must have a local question, understandable setup, and a payoff or deliberate bridge.
- Do not cut immediately before the promised payoff solely to force a next part.
- Keep on-screen text pronounceable and consistent with the audio when it is also spoken.

## Platform Modules

### YouTube Long Form

Create:
- three distinct title hypotheses;
- three thumbnail concepts with concise thumbnail text;
- opening description lines;
- full description;
- chapters when the format benefits;
- playlist/series placement;
- pinned comment;
- end-screen or next-story bridge;
- an A/B test statement explaining what each variant tests.

Avoid title/thumbnail combinations that attract a different audience than the story serves.

### YouTube Shorts

Create one or more standalone cuts with:
- target duration;
- exact source time/text boundaries;
- first spoken sentence;
- first-frame text;
- micro-question and payoff;
- caption/title;
- bridge to the full story when appropriate.

Do not evaluate success from raw views alone; preserve the variant ID for later analysis.

### TikTok

Create:
- a concise first-frame and first-spoken-line plan;
- one or more duration variants appropriate to the material;
- searchable natural-language caption and spoken keywords;
- comment prompt only when it invites a real judgment, prediction, or personal response;
- series/part structure only when each part has local value;
- cover text and variant ID.

Trend sounds, slang, or meme language require current research and must fit the narrator or packaging context. Invoke `audio-story-trend-researcher` when current opportunity evidence is requested.

### Facebook Reels

Create:
- a self-contained cut or longer reel when the story needs room;
- cover text;
- caption designed for discussion and sharing rather than forced bait;
- audience context;
- an originality note describing what is newly created beyond reposting another platform export.

## Packaging Manifest

Write or return:

```text
PACKAGING_MANIFEST
story_path:
story_revision:
story_sha256:
gate_status: verified | unverified
platform:
format:
variant_id:
target_audience:
promise:
source_boundaries:
title:
thumbnail_or_cover:
first_frame:
first_spoken_line:
caption_or_description:
cta_or_bridge:
experiment_hypothesis:
primary_metric:
secondary_metric:
policy_or_originality_notes:
```

Every published variant needs a stable `variant_id` so `audio-story-performance-analyst` can connect analytics to the exact packaging decision.

## Exit Check

- The external promise matches the actual payoff.
- A cold viewer can understand the clip without visual-format dependence.
- The canonical story and gate were not changed.
- Source boundaries and variant ID are recorded.
- Platform differences are substantive, not copy-paste metadata changes.
- Production assets are labeled verified only when the final gate passes.
