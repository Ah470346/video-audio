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


<!-- audio-story-engagement-SKILL:start -->
## Audio Story Engagement — base skill for Vietnamese audio stories

When the user asks to **create/write a story or write an audio-story script** in any genre (drama/adultery, mystery, horror, romance, comedy, etc.), use `audio-story-engagement`. This base skill defines expectation and reward design, choice-consequence causality, motivation, pacing, POV, Vietnamese address forms (`xưng hô`), contextual safety, and idea/opening approval workflow. Do not treat neuroscience labels such as dopamine, oxytocin, mirror neurons, or Zeigarnik as buttons or laws for retention.

- Skill location: `.claude/skills/audio-story-engagement/SKILL.md` (mirror: `.agents/skills/audio-story-engagement/`). Heavy details live in `references/`: safety wording (`an-toan-tu-vung.md`), idea research (`tim-y-tuong.md`), opening menu (`mo-dau.md`), and the full 10 techniques (`ky-thuat-chi-tiet.md`). Load only when needed.
- Coordinate all audio-story skills through `audio-story-engagement/references/phoi-hop-skills.md`: safety, factuality, and logic are hard boundaries; within those boundaries, the user's latest request wins over defaults; base controls workflow; premise controls mechanism; main genre controls payoff; `audio-story-final-polish` runs last without changing approved premise/ending.
- If a concrete genre is present, use the matching `audio-story-genre-*` skill as well. If the prompt includes `trùng sinh`, `hệ thống`, or `xuyên sách`, also use `audio-story-premise-biet-truoc`. If it asks for `truyện rác`, `não tàn`, foolish characters, `tháo não`, or rage-bait frustration, also use `audio-story-premise-truyen-rac`. Premise modifiers can stack.
- Save completed scripts to `kich-ban/<the-loai>/ten-viet-thuong-khong-dau.md`; file content must be PURE STORY, with no headings, metadata, or SFX tags unless the user explicitly requests production cues.
<!-- audio-story-engagement-SKILL:end -->

<!-- audio-story-final-polish-SKILL:start -->
## Audio Story Final Polish — mandatory final pass

After the agent completes **any story or audio-story script**, always use `audio-story-final-polish` as the final content pass, even if the user did not ask for review or polish.

- Order: `audio-story-engagement` + relevant genre/premise skills -> their self-checks -> `audio-story-final-polish` -> save/return the story.
- Skill location: `.claude/skills/audio-story-final-polish/SKILL.md` (mirror: `.agents/skills/audio-story-final-polish/`).
- The skill must repair scene logic, causality, motivation, plot depth, emotion, dialogue, `xưng hô`, pronouns, and read-aloud rhythm; it must not only swap words or split sentences.
- If any story content changes after the final pass, run the skill again from the beginning. If the user asks only for analysis, report issues but do not edit the file.
<!-- audio-story-final-polish-SKILL:end -->

<!-- story-to-audio-SKILL:start -->
## Story To Audio — convert story scripts to audio

When the user asks to **convert a story/script to audio**, **render a story to audio**, or **convert a Markdown story file to audio**, use `story-to-audio`.

- Skill location: `.claude/skills/story-to-audio/SKILL.md` (mirror: `.agents/skills/story-to-audio/`).
- If the user has NOT specified the verification mode, ask briefly: `Bạn muốn dùng fast_verify hay verify?`
- After the user chooses:
  - `fast_verify` -> run `python3 convert_script_to_audio.py -i <input_md> -o results --resume --keep_chunks`
  - `verify` -> run `python3 convert_script_to_audio.py -i <input_md> -o results --resume --keep_chunks --verify`
- If the user already specified `fast_verify` or `verify`, do not ask again; run the matching command.
<!-- story-to-audio-SKILL:end -->
