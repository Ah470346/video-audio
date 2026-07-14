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
## Audio Story Engagement — skill nền tảng viết truyện audio

Khi người dùng yêu cầu **tạo/viết truyện, viết kịch bản truyện audio** (bất kể thể loại: drama/ngoại tình, trinh thám, kinh dị, tình cảm, hài...), dùng skill `audio-story-engagement`. Đây là skill nền tảng quy định CÁCH TƯ DUY + CẤU TRÚC để giữ chân người nghe (dopamine loop, Zeigarnik, phần thưởng biến thiên, mirror neurons, pacing, oxytocin/cortisol, an toàn từ vựng kiểm duyệt, và quy trình duyệt ý tưởng Bước 0 — CỔNG CHẶN).

- Skill sống tại `.claude/skills/audio-story-engagement/SKILL.md` (mirror: `.agents/skills/audio-story-engagement/`). Chi tiết nặng ở `references/`: bảng từ vựng an toàn (`an-toan-tu-vung.md`), quy trình tìm ý tưởng (`tim-y-tuong.md`), menu kỹ thuật mở đầu (`mo-dau.md`), 10 kỹ thuật đầy đủ (`ky-thuat-chi-tiet.md`) — chỉ nạp khi cần.
- Có thể loại cụ thể → dùng KÈM skill `audio-story-genre-*`; nếu prompt có trùng sinh / hệ thống / xuyên sách → kèm `audio-story-premise-biet-truoc`; nếu prompt có truyện rác / não tàn / nhân vật ngu / tháo não / ức chế → kèm `audio-story-premise-truyen-rac`. Hai premise chồng được với nhau.
- Kịch bản hoàn chỉnh lưu vào `kich-ban/<thể-loại>/ten-viet-thuong-khong-dau.md`, nội dung THUẦN TRUYỆN (không heading/metadata/thẻ SFX trừ khi người dùng chủ động yêu cầu).
<!-- audio-story-engagement-SKILL:end -->
