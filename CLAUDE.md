## Tools — Always Use

### agent-browser
For ALL web browser interactions — opening URLs, clicking, filling forms,
taking screenshots, reading page content, running accessibility snapshots —
always use the `agent-browser` CLI. Never use Playwright, Puppeteer, or
Selenium directly. Prefer `agent-browser snapshot` for page understanding
and `agent-browser read <url>` for fetching agent-readable text.

Before the first browser task in a new machine/session, verify readiness with:
`command -v agent-browser`, `agent-browser --version`, and confirm
`agent-browser install` has already completed.

Reference: https://github.com/vercel-labs/agent-browser

<!-- codebase-memory-mcp:start -->
# Codebase Knowledge Graph (codebase-memory-mcp)

This project uses codebase-memory-mcp to maintain a knowledge graph of the codebase.
ALWAYS prefer MCP graph tools over grep/glob/file-search for code discovery.
If the project is not indexed yet, run `index_repository(repo_path="/Users/truongdv/Documents/projects/video-audio", mode="fast", persistence=true)` first.

## Priority Order
1. `search_graph` — find functions, classes, routes, variables by pattern
2. `trace_path` — trace who calls a function or what it calls
3. `get_code_snippet` — read specific function/class source code
4. `query_graph` — run Cypher queries for complex patterns
5. `get_architecture` — high-level project summary

## When to fall back to grep/glob
- Searching for string literals, error messages, config values
- Searching non-code files (Dockerfiles, shell scripts, configs)
- When MCP tools return insufficient results

## Examples
- Find a handler: `search_graph(name_pattern=".*OrderHandler.*")`
- Who calls it: `trace_path(function_name="OrderHandler", direction="inbound")`
- Read source: `get_code_snippet(qualified_name="pkg/orders.OrderHandler")`
- Check readiness: `index_status(project="Users-truongdv-Documents-projects-video-audio")`

## Keeping the graph up to date
The graph does NOT auto-update on file edits. It refreshes in two ways:
1. `auto_index` (machine-local config, not repo-portable): `codebase-memory-mcp config set auto_index true` re-indexes on each new MCP session if the repo changed.
2. A tracked pre-commit hook in `.githooks/pre-commit` re-indexes and re-stages `.codebase-memory/` on every commit, so pushed artifacts stay fresh for other machines. **One-time setup per machine/clone** (git does not auto-apply hooks from a tracked folder): run `git config core.hooksPath .githooks` once after cloning.
<!-- codebase-memory-mcp:end -->

## Cross-runtime canonical mapping — required

- Canonical story skills live under `.agents/skills/<skill-name>/`.
- Canonical custom-agent specifications live under `.agents/agent-specs/*.md`.
- Codex wrappers live under `.codex/agents/*.toml` and must reference the canonical spec.
- Claude mirrors live under `.claude/skills/` and `.claude/agents/`; generate them with `python3 agent-tools/agent-workflow/sync_claude_from_agents.py --root .`.
- After every skill or subagent change, run `python3 agent-tools/agent-workflow/validate_claude_codex_parity.py --root .`.
- Never update only Claude or only Codex. A parity failure blocks treating the project configuration as complete.
- Also run `python3 agent-tools/agent-workflow/validate_story_workflow_contract.py --root .`; anti-template contract failure blocks completion.


## Audio Story Anti-Template Invariant

For all story writing and editing, after safety, explicit user intent, causality, and one-listen clarity, prioritize preventing rigid, uniform, over-finished AI-template prose.

- Never restore or emulate `audio-story-human-life`; it was retired because mandatory “life detail” checks made stories stiff.
- No skill or agent may create quotas for hooks, scene beats, dialogue, details, gestures, metaphors, sentence lengths, or emotional reactions.
- Preserve useful roughness, plain lines, fragments, silence, asymmetry, delayed understanding, and relationship-specific awkwardness when clear and causal.
- Diagnose textual symptoms, not whether an author used AI.
- `No change needed` and protected strengths are valid results.

## Codex local discovery — required

- Launch Codex from this repository root or a descendant inside the same Git repository.
- Repository skills live only under `.agents/skills/<skill-name>/SKILL.md`.
- Project custom agents live only under `.codex/agents/*.toml` and read canonical `.agents/agent-specs/*.md`.
- Deterministic workflow scripts live under `agent-tools/agent-workflow/`.
- If skills or custom agents do not appear, restart Codex; `AGENTS.md` is loaded once per launched session.
- Do not use legacy non-Codex discovery paths.

<!-- audio-story-trend-researcher:start -->
## Audio Story Trend Researcher — user-opt-in social-trend intake

For every Vietnamese fiction-writing request, complete this intake before invoking `audio-story-engagement`, creating a story contract, proposing ideas, or drafting prose:

1. If the prompt does not already give an unambiguous answer, ask: `Bạn có muốn sử dụng nghiên cứu xu hướng mạng xã hội cho truyện này không?`
2. If the user says no, declines, or says trend research is unnecessary, do not ask any platform or duration question. Skip `audio_story_trend_researcher` and begin `audio-story-engagement` immediately.
3. If the user says yes, ask them to select exactly one platform: `TikTok`, `Facebook`, or `YouTube`.
4. After a platform is selected, ask them to select exactly one format: `video dài (trên 5 phút)` or `Short (30-90 giây)`.
5. Treat a clear yes/no, platform, or format already stated in the initial prompt as the answer for that step; ask only for missing answers in this order. Normalize `fb` to `Facebook`, `ytb`/`yt`/`youtube` to `YouTube`, and `dài`/`long`/`>5p` to `video dài (trên 5 phút)`; normalize `short`/`30-90s` to `Short (30-90 giây)`. Do not begin `audio-story-engagement` until the opted-in selection is complete and the research handoff is returned.
6. Then invoke custom agent `audio_story_trend_researcher` from `.claude/agents/audio-story-trend-researcher.md` with the selected platform and format. Pass its `TREND_RESEARCH_REPORT` to `audio-story-engagement` as research boundaries, never as a plot.

The researcher is read-only, must use current sources, and owns market evidence and broad opportunity territories only. It must not create a premise, characters, plot, twist, climax, ending, title, hook, or publishing package. Standalone market-research requests may still invoke it directly, but story-writing intake always follows the sequence above.
<!-- audio-story-trend-researcher:end -->


<!-- audio-story-series-continuity:start -->
## Audio Story Series Continuity — conditional cross-episode canon check

Use custom agent `audio_story_series_continuity` from `.codex/agents/audio_story_series_continuity.toml` only for episodic/shared-world work, recurring casts, multiple timelines/worlds, or persistent state.

- It is read-only and compares the target story with the series bible and canonical episodes.
- It returns `SERIES_CONTINUITY_REPORT` plus `SERIES_BIBLE_PATCH`.
- It never writes prose, edits the bible, judges entertainment quality, or issues release receipts.
<!-- audio-story-series-continuity:end -->

<!-- audio-story-architect:start -->
## Audio Story Architect — conditional structural handoff

Use custom agent `audio_story_architect` from `.codex/agents/audio_story_architect.toml` after a story direction is approved when complexity creates structural risk or the user requests an outline.

- It is read-only and owns only `STORY_ARCHITECTURE_HANDOFF`.
- It may map causality, listener questions, knowledge, scene states, setup/payoff, peak, ending, and audio memory load.
- It must not replace the premise/ending, perform trend research, write manuscript prose, or issue receipts.
<!-- audio-story-architect:end -->

<!-- audio-story-engagement-SKILL:start -->
## Audio Story Engagement — base skill for Vietnamese audio stories

For every Vietnamese fiction-writing task, complete the social-trend intake above first, then use `audio-story-engagement` plus one main genre and only the premise/lexical modifiers actually triggered.

- Current authority: `.agents/skills/audio-story-engagement/SKILL.md` and `.agents/skills/audio-story-engagement/references/phoi-hop-skills.md`.
- Shared craft references include natural Vietnamese prose, single-voice dialogue, premise originality, listener propulsion, and character voice/lived detail.
- `audio-story-engagement` owns concrete ideation and the audience/story contract; trend research and architecture may inform but never replace that ownership.
- Use `audio_story_architect` only for justified complexity and `audio_story_series_continuity` only for cross-episode state.
- Run mandatory full-draft `audio_story_developmental_editor` before final polish; use `audio_story_scene_doctor` only for explicit bounded findings.
- Run full-draft clarity in `stage: pre-polish` before final polish and fresh post-polish development plus `stage: post-polish` clarity after final polish.
- Maintain sibling `<story>.gate.json` under protocol version 2, increment revision after every text change, and bind every receipt to its designated issuer, revision, and SHA-256. Preserve the clean pre-polish receipts as historical inputs to the final-polish chain.
- Working drafts may be shown only as `UNVERIFIED DRAFT`; they are not production-ready.
- Save pure story text under `kich-ban/<the-loai>/`; never put gate metadata inside the story.
<!-- audio-story-engagement-SKILL:end -->


<!-- audio-story-developmental-editor:start -->
## Audio Story Developmental Editor — mandatory whole-story quality gate

Use custom agent `audio_story_developmental_editor` from `.codex/agents/audio_story_developmental_editor.toml` on every complete production manuscript before final polish and again in post-polish mode.

- It is read-only and must read the complete file and verify SHA-256.
- Its first craft risk is systematic AI-template stiffness. It also owns macro promise, propulsion, scene-state progression, agency, character differentiation, emotional residue, predictability, setup/payoff, peak, ending, and audio memory load.
- It emits `DEVELOPMENT_RECEIPT` protocol version 2 and never edits prose.
- A manual reviewer or clarity receipt cannot substitute for it.
<!-- audio-story-developmental-editor:end -->

<!-- audio-story-scene-doctor:start -->
## Audio Story Scene Doctor — bounded developmental repair

Use custom agent `audio_story_scene_doctor` from `.codex/agents/audio_story_scene_doctor.toml` only with explicit finding IDs and allowed scenes/ranges.

- It may compress, dramatize, or rebuild only the assigned scope and must not normalize, beautify, or “humanize” the rest of the manuscript.
- It must preserve the approved contract and protected strengths.
- Any edit increments revision, recomputes SHA-256, and invalidates stale receipts.
- It never issues development, clarity, polish, or completion receipts.
<!-- audio-story-scene-doctor:end -->

<!-- audio-story-final-polish-SKILL:start -->
## Audio Story Final Polish — mandatory last content editor

Run `audio-story-final-polish` only when the current revision has clean full-draft development and clarity receipts.

- It first protects useful irregularity and removes systematic template machinery; then it may repair momentum, logic, motivation, emotion, dialogue, `xưng hô`, prose rhythm, peak/ending, and TTS readiness within the approved contract.
- It emits `FINAL_POLISH_RECEIPT` protocol version 2 with `issued_by: audio-story-final-polish` plus input/output revision and SHA-256.
- Its edits invalidate prior development and clarity receipts.
- Run fresh post-polish developmental review and full-draft clarity on the polished output.
- If either post-polish check requires a story edit, rerun full-draft development and clarity on the repaired revision before final polish, then rerun post-polish development and final clarity.
- Final polish never marks a manuscript complete by itself.
<!-- audio-story-final-polish-SKILL:end -->

<!-- audio_story_completion_gate:start -->
## Audio Story Completion Gate — mandatory fail-closed release gate

Before a story is returned as final, exported, rendered, or packaged as production-ready:

1. require protocol version 2 plus designated-issuer pre-polish development/clarity receipts matching the final-polish input, and clean post-polish development/clarity plus final-polish receipts ending at the same current revision/SHA-256;
2. invoke custom agent `audio_story_completion_gate` from `.codex/agents/audio_story_completion_gate.toml`;
3. run `python3 agent-tools/agent-workflow/validate_story_gate.py --story <story> --manifest <story.gate.json> --mode pre-gate`;
4. record `GATE_PASS_RECEIPT` in the sidecar;
5. run the validator again with `--mode final`.

No receipt, stale hash, unavailable gate, or validator failure means `UNVERIFIED DRAFT`, never final, unless the user explicitly asks to bypass the repository story gate. User bypasses must be stated in the response and must not be silent.
<!-- audio_story_completion_gate:end -->

<!-- audio-story-literary-texture-SKILL:start -->
## Audio Story Literary Texture — POV prose surface (all genres)

When a causally sound story in **any** genre remains generic, sterile, over-literal, or interchangeable, use `audio-story-literary-texture` to shape POV-specific attention, exact fact, emotional ownership, omission, and rhythm. This is a cross-genre craft pass, not a genre or premise.

- Skill location: `.agents/skills/audio-story-literary-texture/SKILL.md` (path: `.agents/skills/audio-story-literary-texture/`).
- Placement: run it after clean developmental structure and before clarity/final polish. If it changes text, rerun full-draft developmental review before clarity.
- Boundaries: it operates inside the base skill's firm-modern-prose / anti-`sến` default; base clarity and restraint win ties. It must not obscure fair clues, hide missing motive, break one-listen clarity, or add ornament for its own sake. Coordinate through `.agents/skills/audio-story-engagement/references/phoi-hop-skills.md`.
<!-- audio-story-literary-texture-SKILL:end -->

<!-- youth-trend-language-SKILL:start -->
## Youth Trend Language — manual-only story skill

Use `.agents/skills/audio-story-youth-trend-language/SKILL.md` only when the user explicitly asks for current slang, teencode, meme wording, Gen Z language, or trend-shaped phrasing in a story. It must research current terms before use and never replaces plot, character, safety, clarity, or final polish.
<!-- youth-trend-language-SKILL:end -->

<!-- audio-story-platform-packaging:start -->
## Audio Story Platform Packaging — derived publishing assets

Use `.agents/skills/audio-story-platform-packaging/SKILL.md` when the user asks for TikTok, YouTube, Shorts, Facebook Reels, titles, thumbnail/cover concepts, captions, descriptions, clip cuts, platform variants, or A/B tests.

- Verified production packaging requires the story's final gate to pass.
- It never edits the canonical story or gate sidecar.
- Save derived assets under `distribution/<story-slug>/<platform>/<variant>/` and record source revision/SHA-256 plus a stable `variant_id`.
- External title/thumbnail/first-frame hooks belong here; internal story opening and payoff remain owned by `audio-story-engagement`.
<!-- audio-story-platform-packaging:end -->

<!-- story-to-audio-SKILL:start -->
## Story To Audio — Kaggle VoxCPM render

When the user asks to render a story, use `story-to-audio`.

- Before the voice question or Kaggle preparation, require sibling `<story>.gate.json` and run `python3 agent-tools/agent-workflow/validate_story_gate.py --story <story> --manifest <story.gate.json> --mode final`; if the user explicitly asks to skip/bypass/override the repository story gate, run the same validator with `--allow-user-bypass --bypass-reason "<short reason>"` and continue after reporting the bypass.
- Both long and short Kaggle prepare scripts independently rerun the final story gate, record gate evidence in `render_job.json`, and fail closed before creating the job unless explicit bypass flags plus a reason are supplied.
- Missing/stale receipts or a nonzero validator exit blocks rendering unless explicit user bypass is active. `story-to-audio` must not repair text; route it back through the story completion workflow when no bypass was requested.
- Skill location: `.agents/skills/story-to-audio/SKILL.md` (path: `.agents/skills/`).
- After gate success, use the selected voice and the existing long/short Kaggle workflow.
- Keep the existing dataset-cache gate before every Kaggle push.
- Never copy or embed the repository `.env` in a Kaggle bundle; use a private Kaggle Secret/environment variable if a future model requires a token.
<!-- story-to-audio-SKILL:end -->

<!-- audio-story-performance-analyst:start -->
## Audio Story Performance Analyst — optional post-publication diagnosis

Use custom agent `audio_story_performance_analyst` from `.codex/agents/audio_story_performance_analyst.toml` only when real analytics, retention data, packaging variants, transcripts, or observed behavior are available.

- It is read-only and must normalize current platform metric definitions.
- It separates topic, packaging, opening, architecture, development, story, clarity, pacing, audio/TTS, distribution, and policy hypotheses.
- It proposes one controlled next test and routes work to the correct skill or agent.
- It never edits the story, invents analytics, or issues a gate receipt.
<!-- audio-story-performance-analyst:end -->

<!-- mix-background-music-SKILL:start -->
## Mix Background Music — ghép nhạc nền vào audio

When the user asks to **ghép nhạc**, **mix nhạc**, **thêm nhạc nền**, or **add background music** to an audio file, follow this workflow:

1. **List available music**: Scan `/Users/truongdv/Documents/projects/video-audio/musics` for all audio files (`.wav`, `.mp3`, `.m4a`, `.flac`, `.ogg`, `.aac`) and present them to the user as choices.
2. **User selects music**: Wait for the user to pick one.
3. **Mix**: Run `tools/mix_background_music.py --voice <audio-path> --music musics/<chosen-file> --output expose/<audio-basename> --force`. Default music volume is -20 dB (quiet enough to not overpower narration). The user can request louder/quieter via `--music-volume` (in dB).
4. **Report**: Print the output path in `/Users/truongdv/Documents/projects/video-audio/expose/`.

- Music directory: `/Users/truongdv/Documents/projects/video-audio/musics`
- Output directory: `/Users/truongdv/Documents/projects/video-audio/expose`
- Tool: `tools/mix_background_music.py` (requires ffmpeg)
<!-- mix-background-music-SKILL:end -->

<!-- overlay-audio-on-video-SKILL:start -->
## Overlay Audio on Video — lồng audio vào video mẫu

When the user asks to **lồng audio**, **thêm audio vào video**, **add audio to video**, **ghép audio video**, **overlay audio**, or any similar phrasing that combines an audio file with a template video, follow this workflow:

1. **List available template videos**: Scan `/Users/truongdv/Documents/projects/video-audio/video-mau` for all video files (`.mp4`, `.mkv`, `.mov`, `.avi`, `.webm`, `.flv`, `.ts`) and present them to the user as choices.
2. **User selects video**: Wait for the user to pick one.
3. **Overlay**: Run `tools/overlay_audio_on_video.py --audio <audio-path> --video video-mau/<chosen-file> --output videos/<audio-basename>.mp4 --force`. By default, the video's original audio is **discarded** and replaced entirely with the new audio. Audio duration is the master: the video **loops** if shorter than the audio, or is **trimmed from the beginning** if longer than the audio.
4. **Report**: Print the output path in `/Users/truongdv/Documents/projects/video-audio/videos/`.

- Optional flags the user can request:
  - `--keep-video-audio`: mix the video's original audio at `-30 dB` with the new audio instead of replacing it.
  - `--video-audio-volume <dB>`: adjust the video's original audio volume (only with `--keep-video-audio`).
  - `--crf <value>`: video quality (lower = better, default 23).
- Video template directory: `/Users/truongdv/Documents/projects/video-audio/video-mau`
- Output directory: `/Users/truongdv/Documents/projects/video-audio/videos`
- Tool: `tools/overlay_audio_on_video.py` (requires ffmpeg)
<!-- overlay-audio-on-video-SKILL:end -->
