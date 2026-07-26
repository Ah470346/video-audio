# Audio Story Agent Workflow Tools

Canonical content lives in `.agents/`; Claude mirrors and Codex wrappers must stay in parity.

Run after every skill, agent, wrapper, protocol, or workflow change:

```bash
python3 agent-tools/agent-workflow/sync_claude_from_agents.py --root .
python3 agent-tools/agent-workflow/validate_claude_codex_parity.py --root .
python3 agent-tools/agent-workflow/validate_story_workflow_contract.py --root .
```

Production manuscripts use protocol version 2 and require one traceable chain:
clean pre-polish development/clarity receipts, final polish whose input matches
those receipts, current post-polish development/clarity receipts, and a
completion-gate receipt. Every receipt names its designated issuer and exact
revision/SHA-256.

The static contract validator also prevents accidental restoration of the retired `audio-story-human-life` skill and checks that anti-template guardrails remain present across all writing/editing layers.

Both Kaggle prepare scripts rerun `validate_story_gate.py --mode final` before
creating a job directory. Direct prepare calls therefore fail closed unless
`--allow-user-bypass` and a non-empty `--bypass-reason` are supplied. Prepared
jobs record gate evidence in `render_job.json`; repository `.env` files are
never copied into the bundle.

Run regression tests with:

```bash
python3 -m unittest discover -s tests -v
```
