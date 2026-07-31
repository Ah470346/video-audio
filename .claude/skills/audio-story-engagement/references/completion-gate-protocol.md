# Audio Story Completion Gate Protocol — Version 2

This protocol makes release completion fail closed and adds an independent developmental gate without turning craft guidance into a prose template.

## Bounded Edit Exception

Do not run this protocol merely because a user requests a bounded local edit. Update the sidecar revision and SHA-256, clear receipts made stale by the text change, and return `UNVERIFIED DRAFT`. Run the complete protocol only when the user asks for a final, production-ready, packaged, exported, rendered, or full-manuscript-validated result.

## Migration

- New sidecars use `protocol_version: 2`.
- A version-1 sidecar is legacy and cannot pass the version-2 validator.
- Migrate by preserving the current story/revision/hash and removing stale receipts. Run full-draft development in `mode: developmental` and clarity in `stage: pre-polish` until clean, then run final polish followed by post-polish full-draft development and clarity. Never relabel a version-1 receipt as version 2.

## Artifacts

For `story.md`, maintain pure story text plus sibling `story.gate.json`. Metadata never enters spoken text.

## Revision and Hash

- Start at revision 1.
- Increment after every story-text byte change, including punctuation or whitespace.
- Compute SHA-256 from exact story bytes.
- Every receipt names its designated issuer plus one revision, hash, protocol version, scope, and mode/stage where applicable.
- Any later text change invalidates old receipts as approval for the current text. Final polish may retain its validated input development/clarity receipts only as historical `pre_polish_*` evidence bound to the old revision/hash; they never approve the polished output.

## Required Sequence

```text
Draft
  -> full-draft development (developmental) until clean
  -> optional bounded scene repair or literary texture
  -> after any edit: development again
  -> full-draft clarity (pre-polish) until clean
  -> after any edit: rerun full-draft development and clarity
  -> final polish
  -> full-draft development (post-polish) until clean
  -> full-draft clarity (post-polish) until clean
  -> if any repair changes text:
       developmental + pre-polish clarity until clean
       then final polish again
       then post-polish development + clarity
  -> completion gate
  -> final save/return/package/render
```

Targeted clarity checks never replace full-draft checks. Architect and series-continuity reports are useful handoffs, not release receipts.

## Sidecar Schema

```json
{
  "protocol_version": 2,
  "story_path": "story.md",
  "current_revision": 6,
  "current_sha256": "...",
  "pre_polish_development_receipt": {
    "protocol_version": 2,
    "issued_by": "audio-story-developmental-editor",
    "scope": "full-draft",
    "mode": "developmental",
    "revision": 5,
    "sha256": "...",
    "status": "clean",
    "coverage": "complete",
    "total_blockers": 0,
    "total_major_findings": 0,
    "total_moderate_findings": 0
  },
  "pre_polish_clarity_receipt": {
    "protocol_version": 2,
    "issued_by": "audio-story-clarity-check",
    "scope": "full-draft",
    "stage": "pre-polish",
    "revision": 5,
    "sha256": "...",
    "status": "clean",
    "total_findings": 0,
    "continuity_gaps": [],
    "coverage": "complete"
  },
  "development_receipt": {
    "protocol_version": 2,
    "issued_by": "audio-story-developmental-editor",
    "scope": "full-draft",
    "mode": "post-polish",
    "revision": 6,
    "sha256": "...",
    "status": "clean",
    "coverage": "complete",
    "total_blockers": 0,
    "total_major_findings": 0,
    "total_moderate_findings": 0,
    "protected_strengths": [],
    "continuity_assumptions": []
  },
  "clarity_receipt": {
    "protocol_version": 2,
    "issued_by": "audio-story-clarity-check",
    "scope": "full-draft",
    "stage": "post-polish",
    "revision": 6,
    "sha256": "...",
    "status": "clean",
    "total_findings": 0,
    "continuity_gaps": [],
    "coverage": "complete"
  },
  "final_polish_receipt": {
    "protocol_version": 2,
    "issued_by": "audio-story-final-polish",
    "status": "completed",
    "input_revision": 5,
    "input_sha256": "...",
    "output_revision": 6,
    "output_sha256": "..."
  },
  "completion_gate_receipt": {
    "protocol_version": 2,
    "status": "pass",
    "revision": 6,
    "sha256": "...",
    "gate_agent": "audio-story-completion-gate",
    "validator_mode": "pre-gate"
  }
}
```

Before the independent gate runs, `completion_gate_receipt` may be absent or pending.

## Gate Preconditions

All must hold:
- story and sidecar exist and resolve to each other;
- manifest uses protocol version 2;
- current file SHA-256 equals `current_sha256`;
- pre-polish development and clarity receipts are clean, complete, issued by their designated agents, bound to the final-polish input revision/hash, and use `mode: developmental` / `stage: pre-polish`;
- development receipt is full-draft, `mode: post-polish`, clean, complete, current, with zero blockers and zero major findings;
- moderate developmental findings may remain only because the editor explicitly classified them nonblocking;
- clarity receipt is full-draft, `stage: post-polish`, clean, complete, current, with zero findings and no continuity gaps;
- development, clarity, and final-polish receipts name their designated issuers;
- final-polish input revision/hash equals both pre-polish receipts, its output revision/hash equals current revision/hash, and its revision transition is internally valid;
- no story text changed after any current receipt;
- validator exits successfully.

The validator checks evidence state, not literary quality. A clean receipt must come from the designated independent agent; prose claims such as “checked carefully” are not evidence.

## Validator

```bash
python3 agent-tools/agent-workflow/validate_story_gate.py \
  --story <story.md> \
  --manifest <story.gate.json> \
  --mode pre-gate
```

After `GATE_PASS_RECEIPT` is written:

```bash
python3 agent-tools/agent-workflow/validate_story_gate.py \
  --story <story.md> \
  --manifest <story.gate.json> \
  --mode final
```

## Failure and Recovery

- Legacy protocol: migrate; never silently accept it.
- Missing/stale receipt: do not polish, finalize, export, package, or render.
- Development or clarity finding that requires a text change after polish: change revision/hash and invalidate the current final chain; rerun full-draft development in `mode: developmental` plus clarity in `stage: pre-polish` until clean, then rerun final polish and both post-polish checks.
- Validator failure: return exact blockers; never downgrade to a warning.
- Unavailable required subagent or validator: label output `UNVERIFIED DRAFT`.
- No silent bypass.
