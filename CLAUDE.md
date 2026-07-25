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

When the user asks to **create/write a story or write an audio-story script** in any genre (drama/adultery, mystery, horror, romance, comedy, etc.), use `audio-story-engagement`. This base skill defines expectation and reward design, choice-consequence causality, motivation, pacing, POV, Vietnamese address forms (`xưng hô`), contextual safety, VoxCPM/TTS-ready pauses and dialogue turns, and the **mandatory idea/opening approval gates**: before drafting any story prose, present 3-5 plot ideas and then 3-4 opening options, stopping for the user's choice at each gate. A detailed premise or phrases like "bạn tự tìm ý tưởng"/"làm phong phú cốt truyện" do NOT waive these gates — only an explicit no-approval instruction ("không cần hỏi", "cứ viết luôn") does. Do not treat neuroscience labels such as dopamine, oxytocin, mirror neurons, or Zeigarnik as buttons or laws for retention.

- Skill location: `.claude/skills/audio-story-engagement/SKILL.md` (mirror: `.agents/skills/audio-story-engagement/`). Heavy details live in `references/`: safety wording (`an-toan-tu-vung.md`), idea research (`tim-y-tuong.md`), opening menu (`mo-dau.md`), VoxCPM/TTS pause readiness (`voxcpm-tts-ngat-nghi.md`), and the full 10 techniques (`ky-thuat-chi-tiet.md`). Load only when needed.
- Coordinate all audio-story skills through `audio-story-engagement/references/phoi-hop-skills.md`: safety, factuality, and logic are hard boundaries; within those boundaries, the user's latest request wins over defaults; base controls workflow; premise controls mechanism; main genre controls payoff; `audio-story-final-polish` runs last without changing approved premise/ending.
- The mandatory professional-prose gate is `audio-story-engagement/references/van-xuoi-chuyen-nghiep.md`: separate observation/inference/pattern/truth; judge dialogue by the whole exchange rather than forcing every line into a tactic; let scenes earn value without exposing `goal-obstacle-turn` machinery; treat every skill example as contaminated source material; and reject stock domestic/object choreography used as fake interiority.
- **Anti-abstraction gate + clarity subagent (mandatory):** never write over-abstracted sentences (`câu trừu tượng hóa quá mức`) where concept nouns or pseudo-philosophy replace the concrete event (e.g. `tôi mới biết tên của một văn bản không nói cho tôi biết mình đã nhận món nợ nào`); every depth-reaching sentence must pass the literal-translation (`dịch sang nghĩa đen`) and dishwashing tests — class definition and repair pattern in `audio-story-engagement/references/cau-van-truu-tuong.md`. While drafting, after each 500-1000-word segment (at a sentence boundary), run the clarity-check subagent — Claude Code: `audio-story-clarity-check` (`.claude/agents/audio-story-clarity-check.md`); Codex: `audio_story_clarity_check` (`.codex/agents/audio-story-clarity-check.toml`) — apply its `REWRITE` findings immediately before drafting the next segment, and run it once more on the full draft before `audio-story-final-polish`.
- If a concrete genre is present, use the matching `audio-story-genre-*` skill as well. If the prompt includes `trùng sinh`, `hệ thống`, or `xuyên sách`, also use `audio-story-premise-biet-truoc`. If it asks for `truyện rác`, `não tàn`, foolish characters, `tháo não`, or rage-bait frustration, also use `audio-story-premise-truyen-rac`. Premise modifiers can stack.
- Save completed scripts to `kich-ban/<the-loai>/ten-viet-thuong-khong-dau.md`; file content must be PURE STORY, with no headings, metadata, or SFX tags unless the user explicitly requests production cues.
<!-- audio-story-engagement-SKILL:end -->

<!-- audio-story-final-polish-SKILL:start -->
## Audio Story Final Polish — mandatory final pass

After the agent completes **any story or audio-story script**, always use `audio-story-final-polish` as the final content pass, even if the user did not ask for review or polish.

- Order: `audio-story-engagement` + relevant genre/premise skills -> their self-checks -> `audio-story-final-polish` -> save/return the story.
- Skill location: `.claude/skills/audio-story-final-polish/SKILL.md` (mirror: `.agents/skills/audio-story-final-polish/`).
- The skill must repair scene logic, causality, motivation, plot depth, emotion, dialogue, `xưng hô`, pronouns, read-aloud rhythm, and VoxCPM/TTS pause readiness; it must not only swap words or split sentences.
- If any story content changes after the final pass, run the skill again from the beginning. If the user asks only for analysis, report issues but do not edit the file.
<!-- audio-story-final-polish-SKILL:end -->

<!-- audio-story-literary-texture-SKILL:start -->
## Audio Story Literary Texture — POV prose surface (all genres)

When a story in **any** genre is clear but the prose feels generic, over-literal, or interchangeable, use `audio-story-literary-texture` to shape POV imagery, metaphor, motif, sentence rhythm, and acoustic language so it sounds as if only this narrator could tell it this way. This is a cross-genre craft pass, not a genre or premise.

- Skill location: `.claude/skills/audio-story-literary-texture/SKILL.md` (mirror: `.agents/skills/audio-story-literary-texture/`).
- Placement: run it **after a causally clear draft exists and before `audio-story-final-polish`**. Never run it before a clear draft — draft action and causality first, then add texture only where it changes meaning.
- Boundaries: it operates inside the base skill's firm-modern-prose / anti-`sến` default; base clarity and restraint win ties. It must not obscure fair clues, hide missing motive, break one-listen clarity, or add ornament for its own sake. Coordinate through `audio-story-engagement/references/phoi-hop-skills.md`.
<!-- audio-story-literary-texture-SKILL:end -->

<!-- youth-trend-language-SKILL:start -->
## Youth Trend Language — MANUAL-ONLY, two skills, route by subject

Two opt-in skills add current Vietnamese youth language (teencode, từ trend, tiếng lóng, meme, `nói lái`, Gen Z speech, playful Vietnamese-English). **Neither may ever self-trigger.** Writing, polishing, reviewing, or rendering something is not a request for trend language.

Activate only when the prompt contains an explicit trend intent — `teencode`, `tiếng lóng`, `slang`, `từ trend`, `bắt trend`, `hot trend`, `từ xu hướng`, `từ khóa hot`, `Gen Z`/`genz`, `meme`, `nói lái`, `viral`, `nói kiểu giới trẻ` — and then route by **what is being written**:

| The prompt is about | Use |
|---|---|
| truyện, truyện audio, kịch bản truyện, nhân vật, drama/ngôn tình/kinh dị/hài/trinh thám | `audio-story-youth-trend-language` |
| review sản phẩm, giới thiệu/quảng cáo sản phẩm, bán hàng, content TikTok/Reels/Shorts, livestream, affiliate, UGC, kịch bản ngắn cho sản phẩm | `product-review-youth-trend-language` |

Example: *"viết truyện audio có teencode/từ trend"* -> story skill. *"viết kịch bản ngắn giới thiệu sản phẩm bắt trend"* -> product skill. If the subject is genuinely ambiguous (for example a bare `kịch bản ngắn`), ask one routing question before researching.

- Skill locations: `.claude/skills/audio-story-youth-trend-language/SKILL.md` and `.claude/skills/product-review-youth-trend-language/SKILL.md` (mirrors under `.agents/skills/`).
- Both skills **must research the live web** before using any time-sensitive term (`WebSearch`/`WebFetch`, or `agent-browser read <url>`). Never select trending slang from memory. If browsing is unavailable, say so and fall back to durable colloquial Vietnamese.
- Story-side placement: after the contract and base character-life calibration are locked, applied during drafting/texture, with `audio-story-final-polish` still last. It is a lexical accent below base clarity, genre payoff, and safety — see `audio-story-engagement/references/phoi-hop-skills.md`.
- Product-side scripts are **not** audio-story files: do not run `audio-story-final-polish` on them and do not save them under `kich-ban/`.
- **VoxCPM render rule (both skills):** any English-origin word, acronym, or stylized teencode token that reaches the render must already be written the way it should be heard — `inbox` -> `in bốc`, `livestream` -> `lai sờ trim`, `TikTok` -> `tích tóc` — or replaced with plain Vietnamese (`inbox` -> `nhắn tin riêng`). `audio-story-final-polish` enforces this for stories; the product skill enforces it for commercial scripts. Details: `audio-story-engagement/references/voxcpm-tts-ngat-nghi.md`, section "English, Teencode, And Trend Tokens".
<!-- youth-trend-language-SKILL:end -->

<!-- story-to-audio-SKILL:start -->
## Story To Audio — Kaggle VoxCPM render

When the user asks to **convert a story/script/Markdown/pasted text to audio** or **render audio**, use `story-to-audio`.

- Skill location: `.claude/skills/story-to-audio/SKILL.md` (mirror: `.agents/skills/story-to-audio/`).
- Unless the user already chose a voice, first ask which clone voice to use: `adam` or `ngoc huyen`.
- After the user chooses, prepare and push the Kaggle job with `tools/prepare_kaggle_voxcpm_job.py --voice adam` or `--voice ngoc_huyen`, using a job dir in `/Users/truongdv/Documents/projects/video-audio/kaggle_jobs` named `<ten-truyen>_<timestamp>` or `<ten-truyen>_<word-limit>_words_<timestamp>` when rendering a word-limited preview, then stop the chat. Do not wait/poll for Kaggle unless the user explicitly asks.
- VoxCPM prepare defaults are audiobook-safe for this repo: `openbmb/VoxCPM2`, `clone_mode=ultimate`, deterministic seed, short external chunks, reference WAV QC, warn-first ASR/speaker QC, retry/sub-split recovery, internet-enabled Kaggle setup, and final mastering. Re-run prepare after every source/config change so the embedded bundle SHA changes.
- Before every Kaggle push, run the dataset cache gate in `.claude/skills/story-to-audio/SKILL.md`: both long and short jobs must attach `ah470346/voxcpm2-snapshot`, embed a launcher that can find `/kaggle/input/tts-and-qc-models`, and avoid Hugging Face model fetches during normal renders.
- When the user later says Kaggle is done (for example: `xong rồi`, `oke rồi`, `done rồi`, or similar), download the full output with `tools/download_kaggle_kernel_output.py` into `/Users/truongdv/Documents/projects/video-audio/results`, extract any zip if needed, run `tools/postprocess_kaggle_audio.py --speed 1.25` on the final mastered audio, save the processed result to `/Users/truongdv/Documents/projects/video-audio/audio/<ten-truyen-dau-vao>.<ext>`, report both paths, and stop.
<!-- story-to-audio-SKILL:end -->

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
