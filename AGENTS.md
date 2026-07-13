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
---
name: audio-story-engagement
description: Bộ nguyên tắc nền tảng (base) để viết kịch bản truyện audio hấp dẫn, gây nghiện cho người nghe bằng các cơ chế tâm lý học (dopamine loop, Zeigarnik, phần thưởng biến thiên, mirror neurons, pacing...). LUÔN sử dụng skill này mỗi khi người dùng yêu cầu "tạo/viết một câu truyện", "viết kịch bản truyện audio", "viết truyện drama/ngoại tình/trinh thám/kinh dị/tình cảm...", hoặc bất kỳ yêu cầu sáng tác truyện kể nào — bất kể thể loại. Skill này KHÔNG quy định thể loại; nó quy định CÁCH TƯ DUY và CẤU TRÚC để câu truyện giữ chân người nghe từ đầu đến cuối.
---

# Audio Story Engagement — Nền Tảng Tâm Lý Cho Kịch Bản Truyện Audio

## Mục đích

Skill này biến mọi yêu cầu tạo truyện (ví dụ: *"tạo cho tôi một câu truyện drama thể loại ngoại tình"*) thành một kịch bản audio được thiết kế có chủ đích để **kích hoạt dopamine liên tục** trong não người nghe. Dopamine không phải hóa chất của niềm vui — nó là hóa chất của **sự khao khát và kỳ vọng**. Nhiệm vụ của bạn (agent) không phải là "kể một câu chuyện hay", mà là **thiết kế một chuỗi phần thưởng tâm lý** khiến người nghe không thể tắt.

Nguyên tắc tối thượng: **Mỗi phút audio phải trả lời câu hỏi "tại sao người nghe KHÔNG được tắt ngay lúc này?"** Nếu không trả lời được, đoạn đó phải viết lại.

### Quy tắc xưng hô & bối cảnh (BẮT BUỘC)
Kể truyện ở **ngôi thứ nhất** để tạo cảm giác thân mật, như đang nghe một người kể lại bí mật của chính họ. TUYỆT ĐỐI không đặt tên riêng cho nhân vật và không dùng địa danh có thật.
- **Nhân vật:** gọi bằng đại từ quan hệ với người kể — *tôi, chồng tôi, vợ tôi, người yêu tôi, bạn tôi, bố tôi, mẹ tôi, con tôi, chị tôi, sếp tôi, hàng xóm của tôi...* Nếu cần phân biệt nhiều người cùng vai, dùng đặc điểm thay tên (*người đàn ông đó, cô gái ở quán cà phê, gã đàn ông lạ mặt*).
- **Địa điểm:** dùng cách gọi chung — *nhà tôi, phòng tôi, làng tôi, khu phố tôi, thành phố tôi đang sống, công ty tôi, quán quen của chúng tôi...* Không dùng "Hà Nội", "Sài Gòn" hay bất kỳ tên địa danh thật nào.
- Cách xưng hô này giúp người nghe dễ tự đặt mình vào vị trí nhân vật (tăng mirror neurons và oxytocin ở Kỹ thuật 4 và 7), vì không có cái tên lạ nào chen giữa họ và câu chuyện.

### Văn phong: DỨT KHOÁT, HIỆN ĐẠI — KHÔNG SẾN (BẮT BUỘC — lớp lọc áp lên MỌI kỹ thuật bên dưới)

Đây là bộ lọc chạy ĐÈ lên toàn bộ skill. Mọi kỹ thuật phía dưới (tả cơ thể ở Kỹ thuật 4, zoom cận cảnh, pacing câu dài ở Kỹ thuật 5, nội tâm ở Kỹ thuật 10...) đều phải đi qua lớp lọc này TRƯỚC khi được giữ lại. Mặc định của văn phong là: **ít chữ, câu gọn, chi tiết cụ thể, để cảm xúc lộ ra qua hành động — không tô vẽ, không than vãn, không hoa mỹ.** Người nghe hiện đại tin vào sự tiết chế; họ bỏ đi ngay khi ngửi thấy "sến". Sến giết sự hấp dẫn nhanh hơn cả cốt truyện dở.

**Bốn quy tắc cứng:**
1. **Cắt, đừng tô.** Mỗi câu mô tả phải trả lời được: *"Câu này có đẩy truyện tiến tới, tăng tò mò, hoặc tăng căng thẳng không?"* Nếu chỉ để cho "đẹp" hoặc cho "buồn" → xóa. Ưu tiên **hành động + thoại + tiết lộ** hơn tả khung cảnh và tả cảm xúc. Truyện phải đẩy tò mò và cao trào LIÊN TIẾP — mọi câu tả kéo nhịp chùng xuống mà không trả về điều gì là câu cần cắt.
2. **Cấm ẩn dụ cảm xúc sáo mòn.** Không "trái tim tan vỡ thành ngàn mảnh", "nước mắt lăn dài trên gò má", "nỗi đau như dao cứa / xát muối", "bầu trời như sụp đổ", "thế giới của tôi vỡ vụn", "con tim thổn thức". Đây là dấu hiệu sến số một. Thay bằng một chi tiết cụ thể, khô: *"Tôi đặt bát cơm xuống. Không ăn nữa."*
3. **Không than, không kể lể cảm xúc.** Cấm câu cảm thán rao giảng nỗi lòng ("Trời ơi, sao số phận nghiệt ngã với tôi đến thế!", "Lòng tôi đau như cắt", "Đời tôi coi như chấm hết"). Nhân vật hiện đại nuốt cảm xúc vào trong; để một hành động nhỏ nói thay. Người nghe tự thấy đau — đừng đau hộ họ.
4. **Một chi tiết đắt hơn ba chi tiết đẹp.** Chọn MỘT chi tiết cảm giác chính xác rồi dừng. Chồng chất tính từ/trạng từ ("khẽ khàng, nhẹ nhàng, chầm chậm, run rẩy") làm câu nhão. Gạch bớt tính từ; giữ lại danh từ và động từ mạnh.

**Bảng đối chiếu SẾN → DỨT KHOÁT:**

| Sến (xóa) | Dứt khoát (giữ) |
|---|---|
| *"Nước mắt tôi tuôn rơi như mưa, trái tim tan nát từng mảnh."* | *"Tôi không khóc. Tôi chỉ thấy tay mình lạnh."* |
| *"Anh ấy nhìn tôi bằng ánh mắt trìu mến vô bờ bến."* | *"Anh nhìn tôi lâu hơn bình thường đúng một giây."* |
| *"Lòng tôi quặn thắt trong nỗi cô đơn tột cùng của kiếp người."* | *"Căn phòng chỉ còn tiếng tủ lạnh chạy."* |
| *"Tôi đau đớn khôn nguôi, đau đến xé nát tâm can."* | *"Tôi đọc lại tin nhắn ba lần. Rồi tắt máy."* |

**Phép thử cuối:** viết xong, đọc lại và gạch mọi câu "nghe như lời một bài bolero". Nếu một câu có thể bê nguyên sang 10 truyện khác mà không đổi gì → nó sáo, viết lại cho cụ thể vào đúng tình huống này. Tiết chế không phải là lạnh lùng — chi tiết càng khô, cú đau càng thật.

---

## QUY TRÌNH BẮT BUỘC KHI NHẬN YÊU CẦU TẠO TRUYỆN

Khi nhận prompt kiểu "tạo cho tôi một câu truyện [thể loại X]", KHÔNG viết ngay. Thực hiện tuần tự:

### Bước 0 — TÌM & ĐỀ XUẤT Ý TƯỞNG CHO NGƯỜI DÙNG DUYỆT (BẮT BUỘC, LÀM ĐẦU TIÊN — CỔNG CHẶN)
Ngay khi nhận yêu cầu tạo truyện kèm thể loại (ví dụ *"viết cho tôi một truyện drama ngoại tình"*), **TRƯỚC KHI làm Bước 1 và trước khi viết bất kỳ câu truyện nào**, phải:
1. **Tìm trên mạng** các ý tưởng / mô-típ / chủ đề nội dung đang đặc sắc, hot, gây bàn tán cho đúng thể loại người dùng yêu cầu (xem mục *"KỸ NĂNG TÌM Ý TƯỞNG TRÊN MẠNG & QUY TRÌNH DUYỆT"* ngay bên dưới để biết cách search và chắt lọc).
2. **Chắt lọc thành 3–5 ý tưởng sơ bộ**, mỗi ý gồm: một tiêu đề/hook gợi ý + một logline 1–2 câu + điểm xoáy (twist/mô-típ) khiến nó hấp dẫn.
3. **Trình danh sách cho người dùng chọn** và **DỪNG LẠI chờ người dùng duyệt** — không tự ý viết tiếp.
4. Chỉ khi người dùng **chốt một ý** (hoặc yêu cầu trộn/chỉnh/thay ý khác) mới đi tiếp **Bước 1**.
> Đây là CỔNG CHẶN: bỏ qua Bước 0 và viết luôn cả kịch bản là lỗi nghiêm trọng (lãng phí công, dễ trật ý người dùng). Ngoại lệ duy nhất: người dùng đã tự mô tả sẵn cốt truyện/ý tưởng cụ thể — khi đó chỉ cần xác nhận nhanh rồi đi tiếp, không cần đề xuất lại.

### Bước 1 — Xác định "Câu Hỏi Trung Tâm" (Central Dramatic Question)
Trước khi viết chữ nào, phải chốt được MỘT câu hỏi lớn xuyên suốt mà người nghe khao khát biết đáp án. Câu hỏi này là "món nợ" bạn treo với người nghe từ phút đầu và chỉ trả đầy đủ ở phút cuối.
- Drama ngoại tình → *"Liệu tôi có phát hiện ra toàn bộ sự thật không, và khi biết, tôi sẽ làm gì?"*
- Trinh thám → *"Ai là hung thủ, và tại sao người đó phải chết?"*
- Câu hỏi phải chứa **hậu quả cá nhân** (ai đó sẽ mất gì) chứ không chỉ là thông tin.

### Bước 2 — Thiết kế "Bản Đồ Dopamine" (Dopamine Map)
Phác nhanh (trong đầu hoặc dạng outline) chuỗi các điểm kích thích trước khi viết:
1. **Hook mở đầu** (0–30 giây đầu): khoảnh khắc gây sốc/tò mò nhất
2. Danh sách **3–7 vòng lặp mở** (open loops) sẽ gieo và thời điểm đóng từng vòng
3. Danh sách **các cú twist** và vị trí của chúng (tránh dồn hết vào cuối)
4. Chu kỳ **hy vọng ↔ tuyệt vọng** của nhân vật chính (ít nhất 3 lần đảo chiều)
5. Điểm đặt **khoảnh khắc "Aha!"** và các chi tiết foreshadow tương ứng

### Bước 3 — Viết theo các kỹ thuật ở phần dưới
### Bước 4 — Tự kiểm tra bằng Checklist cuối file trước khi trả kết quả
### Bước 5 — Lưu kịch bản vào thư mục thể loại tương ứng (BẮT BUỘC)
Sau khi hoàn thành và tự kiểm tra kịch bản đạt yêu cầu, bạn PHẢI lưu kịch bản đó dưới định dạng `.md` vào đúng thư mục thể loại tương ứng tại `/Users/truongdv/Documents/projects/video-audio/kich-ban/`:
- Drama: `/Users/truongdv/Documents/projects/video-audio/kich-ban/drama/`
- Trinh thám: `/Users/truongdv/Documents/projects/video-audio/kich-ban/trinh-tham/`
- Kinh dị: `/Users/truongdv/Documents/projects/video-audio/kich-ban/kinh-di/`
- Tình cảm: `/Users/truongdv/Documents/projects/video-audio/kich-ban/tinh-cam/`
- Hài hước: `/Users/truongdv/Documents/projects/video-audio/kich-ban/hai-huoc/`

*Quy tắc đặt tên file:* `ten-kich-ban-viet-thuong-khong-dau.md` (dùng dấu gạch ngang để phân cách các từ, ví dụ: `chong-toi-ngoai-tinh.md`). File lưu phải chứa toàn bộ nội dung kịch bản hoàn chỉnh.

**Quy tắc nội dung file — THUẦN TRUYỆN, KHÔNG METADATA (BẮT BUỘC):**
File kịch bản xuất ra PHẢI chỉ chứa nội dung truyện thuần túy — tức là văn bản mà người đọc/giọng AI có thể đọc thẳng từ đầu đến cuối mà không cần bỏ qua bất kỳ dòng nào. Cụ thể:
- ❌ **CẤM** đặt tiêu đề dạng heading markdown (`# Tiêu đề truyện`) ở đầu file.
- ❌ **CẤM** đặt metadata (thể loại, ngôi kể, số chữ, thời lượng, hướng dẫn đọc...) — những thông tin này KHÔNG thuộc về nội dung truyện.
- ❌ **CẤM** dùng dấu ngăn cách (`---`, `***`, `===`) giữa các phần/hồi — chuyển cảnh phải được thể hiện bằng chính lời văn (xuống dòng trắng là đủ).
- ❌ **CẤM** chèn thẻ SFX/BGM dạng `[SFX: ...]`, `[BGM: ...]`, tên hồi/chương dạng heading (`### HỒI 1: ...`) — trừ khi người dùng **chủ động yêu cầu** kịch bản có lớp chỉ dẫn sản xuất.
- ✅ File bắt đầu bằng **câu đầu tiên của truyện** — chính là hook mở đầu.
- ✅ File kết thúc bằng **câu cuối cùng của truyện** — không có "HẾT", không có lời bình ngoài truyện.
- ✅ Nếu cần ghi chú cho người sản xuất (giọng đọc, nhịp, tông...), đặt trong một file riêng hoặc trả lời riêng cho người dùng — KHÔNG trộn vào file kịch bản.

---

## KỸ NĂNG TÌM Ý TƯỞNG TRÊN MẠNG & QUY TRÌNH DUYỆT (BƯỚC 0 CHI TIẾT)

**Tại sao bắt buộc:** viết cả một kịch bản dài rồi mới biết người dùng không thích ý tưởng là lãng phí lớn. Đề xuất ý tưởng trước vừa để người dùng cầm lái, vừa để bơm vào truyện những mô-típ tươi mới, đang được quan tâm ngoài đời thay vì công thức sáo mòn trong đầu agent. Ý tưởng lấy từ mạng chỉ là **nguyên liệu cảm hứng** — luôn xào nấu, ghép lai, đổi bối cảnh thành cái của riêng mình; TUYỆT ĐỐI không sao chép một truyện có thật/của tác giả cụ thể, không giữ tên riêng, không giữ địa danh thật (tôn trọng "Quy tắc xưng hô & bối cảnh").

### 1. Tìm kiếm trên mạng (bắt buộc thử trước khi tự nghĩ)
- Dùng công cụ tìm kiếm web (`WebSearch`) để quét nhanh xu hướng; khi cần đọc kỹ một trang, dùng `agent-browser read <url>` để lấy nội dung dạng văn bản (theo quy tắc công cụ của dự án — không tự mở Playwright/Puppeteer/Selenium).
- Mỗi lần đề xuất, chạy **2–4 truy vấn** ở các góc khác nhau rồi tổng hợp; đừng dừng ở một kết quả.
- Ưu tiên nguồn phản ánh **cái người ta đang thực sự nghe/đọc/bàn**: các kênh truyện audio/podcast, kênh YouTube kể chuyện, diễn đàn tâm sự, mạng xã hội (bài "trend", bình luận nhiều), các bài tổng hợp mô-típ (tropes) và danh sách "truyện hay nhất" của thể loại.
- Gợi ý hướng truy vấn theo thể loại (dịch thêm sang tiếng Anh khi muốn quét nguồn quốc tế):
  - **Drama/ngoại tình:** "câu chuyện drama gia đình gây sốc", "tình huống ngoại tình plot twist", "trending affair story reddit", "family secret story ideas".
  - **Trinh thám:** "vụ án bí ẩn cốt truyện hay", "murder mystery plot twist ideas", "locked room mystery hook".
  - **Kinh dị:** "truyện kinh dị gây ám ảnh", "creepypasta ideas trending", "urban legend horror hook".
  - **Tình cảm:** "mô-típ ngôn tình được yêu thích", "romance trope ideas", "second chance love story".
  - **Hài hước:** "tình huống hài dở khóc dở cười", "funny relatable story ideas", "satire skit premise".
- Trong lúc quét, chú ý nhặt: mô-típ đang hot, cú twist lạ, tình huống đời thường dễ đồng cảm, "điểm đau" xã hội đang được bàn — đây là mỏ ý tưởng.

### 2. Chắt lọc thành 3–5 ý tưởng
Mỗi ý tưởng trình bày gọn theo mẫu:
- **Tên/hook gợi ý:** một tiêu đề mở vòng lặp (theo Kỹ thuật 1), không tiết lộ hết ruột.
- **Logline (1–2 câu):** ai + tình huống bất thường + điều đang bị đe dọa.
- **Điểm xoáy:** cú twist hoặc mô-típ trung tâm khiến ý này khác biệt/hấp dẫn.

Các ý tưởng phải **khác nhau rõ rệt** về góc tiếp cận (đừng đưa 4 biến thể của cùng một tình huống), để người dùng có lựa chọn thật.

### 3. Trình bày & chờ duyệt (CỔNG CHẶN)
- Đưa danh sách đánh số, ngắn gọn, dễ liếc; hỏi thẳng: *"Bạn muốn triển khai ý nào? (hoặc trộn/đổi/thêm ý)"*.
- **Dừng lại, chờ phản hồi.** Không viết Câu Hỏi Trung Tâm hay bất kỳ đoạn truyện nào cho tới khi người dùng chốt.
- Nếu người dùng chưa nêu độ dài / một tập hay nhiều tập, có thể hỏi gộp luôn ở bước này cho tiện.
- Nếu người dùng muốn trộn nhiều ý hoặc điều chỉnh: cập nhật lại logline đã chốt trong một câu để xác nhận, rồi mới sang Bước 1.

### 4. Khi không tìm được / không dùng được web
Nếu công cụ web không khả dụng hoặc không ra kết quả hữu ích: vẫn PHẢI tự đề xuất 3–5 ý tưởng từ kiến thức của mình và trình cho người dùng duyệt như trên — **không bao giờ bỏ qua cổng duyệt**. Nói rõ với người dùng rằng các ý này dựa trên kinh nghiệm chung thay vì tra cứu mới.

---

## KỸ THUẬT 1: HOOK MỞ ĐẦU — 30 GIÂY SINH TỬ

**Nguyên lý:** Người nghe audio quyết định ở lại hay rời đi trong 8–30 giây đầu. Não bộ chỉ cấp "ngân sách chú ý" khi phát hiện điều bất thường, nguy hiểm, hoặc bí ẩn.

**Cách áp dụng:**
- **Mở giữa hành động (in medias res):** KHÔNG BAO GIỜ mở đầu bằng giới thiệu lý lịch, thời tiết, hay bối cảnh chung chung. Mở ngay tại khoảnh khắc căng thẳng nhất hoặc gần đỉnh điểm, rồi mới quay ngược kể lại.
  - ❌ *"Tôi năm nay 32 tuổi, sống ở thành phố này đã lâu, chồng tôi là một người đàn ông hiền lành..."*
  - ✅ *"Chiếc nhẫn cưới nằm trong túi áo khoác của chồng tôi. Vấn đề là — nó không phải nhẫn của tôi."*
- **Ba dạng hook mạnh nhất cho audio:**
  1. **Câu tuyên bố nghịch lý:** một câu tự mâu thuẫn buộc não phải xử lý. (*"Ngày tôi biết chồng ngoại tình cũng là ngày hạnh phúc nhất đời tôi."*)
  2. **Cảnh giữa khủng hoảng:** thả người nghe vào giữa một tình huống đã bùng nổ.
  3. **Lời thú nhận trực tiếp:** ngôi thứ nhất thú nhận điều cấm kỵ, tạo cảm giác được nghe bí mật.
- Sau hook, **treo nó lại** và quay về kể từ đầu. Hook trở thành lời hứa: "nghe tiếp đi, bạn sẽ hiểu tại sao đến được khoảnh khắc đó."
- **Tiêu đề là cú hook số 0:** người nghe gặp TIÊU ĐỀ trước khi gặp câu đầu tiên. Nếu người dùng cần tiêu đề, đề xuất tiêu đề chứa một nghịch lý hoặc một câu hỏi ngầm (*"Chồng tôi khóc trong đám tang của người phụ nữ tôi chưa từng gặp"*) thay vì tiêu đề mô tả chung chung (*"Câu chuyện ngoại tình"*). Tránh tiêu đề tiết lộ hết ruột — tiêu đề phải mở một vòng lặp, không đóng.
- **Câu đầu tiên phải tự đứng được:** nếu tách riêng câu mở đầu ra khỏi truyện, nó vẫn phải khiến người lạ muốn nghe câu thứ hai. Viết xong, thử đọc riêng câu đầu — nếu nó nhạt, viết lại trước khi làm bất cứ điều gì khác.

---

## KỸ THUẬT 2: HIỆU ỨNG ZEIGARNIK — HỆ THỐNG VÒNG LẶP MỞ (OPEN LOOPS)

**Nguyên lý:** Não bộ ghi nhớ và bị ám ảnh bởi việc chưa hoàn thành mạnh hơn nhiều so với việc đã kết thúc. Một câu hỏi chưa có đáp án tạo ra "cơn ngứa nhận thức" — người nghe ở lại để được gãi.

**Cách áp dụng chi tiết:**
- **Vận hành nhiều vòng lặp cùng lúc, so le nhau.** Đây là điểm cốt lõi mà người viết non tay bỏ qua: không bao giờ để chỉ còn MỘT câu hỏi mở. Quy tắc: **trước khi đóng một vòng lặp, phải mở một vòng lặp mới.** Khi trả lời "ai gửi tin nhắn nặc danh?", ngay trong cảnh đó phải gieo "nhưng tại sao người đó lại biết mật khẩu điện thoại?"
- **Phân tầng vòng lặp theo 3 cấp:**
  - *Vòng lặp lớn* (Câu Hỏi Trung Tâm): mở ở phút đầu, đóng ở hồi kết.
  - *Vòng lặp trung* (bí ẩn phụ, quan hệ nhân vật): sống qua 2–4 phân đoạn.
  - *Vòng lặp nhỏ* (căng thẳng trong cảnh): mở và đóng trong cùng một cảnh để tạo phần thưởng tức thì.
- **Nhỏ giọt manh mối:** mỗi lần chạm vào một bí ẩn, chỉ hé lộ 10–20% thông tin mới. Đủ để người nghe cảm thấy tiến triển, không đủ để thỏa mãn.
- **Cliffhanger cuối mỗi chương/phân đoạn — nhưng phải XOAY VÒNG loại cliffhanger.** Nếu chương nào cũng kết bằng "nguy hiểm thể xác" (súng chĩa vào đầu, xe lao xuống vực), đến lần thứ 5 người nghe sẽ thấy bị thao túng và chai lỳ. Xoay vòng giữa 4 loại:
  1. **Cắt trước đỉnh điểm:** dừng ngay trước khi sự thật được phơi bày (cánh cửa sắp mở).
  2. **Tiết lộ chấn động:** kết chương bằng thông tin đảo ngược mọi hiểu biết ("người phụ nữ trong ảnh... là em gái tôi").
  3. **Ngã ba quyết định:** nhân vật đứng trước lựa chọn mà người nghe thật sự không đoán được sẽ chọn gì.
  4. **Mầm họa mới:** vấn đề cũ vừa giải quyết xong, một hiểm họa mới nhú lên ở câu cuối.
- **Viết cliffhanger phải NGẮN và ĐỘT NGỘT.** Câu cuối chương dùng câu ngắn, cắt phựt. Không giải thích, không tả dài.

---

## KỸ THUẬT 3: PHẦN THƯỞNG BIẾN THIÊN (INTERMITTENT REINFORCEMENT)

**Nguyên lý:** Phần thưởng có thể đoán trước tạo ít dopamine. Phần thưởng KHÔNG đoán trước được tạo dopamine cực đại — đây chính là cơ chế gây nghiện của máy đánh bạc và mạng xã hội.

**Cách áp dụng chi tiết:**
- **Nhận diện và phá khuôn mẫu (trope subversion):** Trước khi viết mỗi tình tiết, tự hỏi: *"Người nghe quen thể loại này sẽ đoán điều gì xảy ra tiếp theo?"* — rồi chọn một trong ba:
  1. Làm đúng kỳ vọng nhưng **sớm hơn dự kiến** (họ tưởng bí mật lộ ở cuối truyện, cho lộ ở giữa truyện → mở ra vùng đất mới không đoán được).
  2. Làm đúng kỳ vọng nhưng **hậu quả ngược chiều** (tôi phát hiện chồng ngoại tình → nhưng thay vì đánh ghen, tôi im lặng và bắt đầu một kế hoạch).
  3. **Đảo vai:** kẻ tưởng là nạn nhân hóa ra là người giật dây.
- **Quy tắc twist hợp lý:** twist chỉ tạo dopamine khi nó **bất ngờ nhưng tất yếu** — nhìn lại thấy mọi manh mối đã có sẵn. Twist từ trên trời rơi xuống (không foreshadow) tạo cảm giác bị lừa, giết chết niềm tin.
- **Chu kỳ hy vọng–tuyệt vọng (nghiêm ngặt):** KHÔNG cho nhân vật chính chuỗi chiến thắng hoặc chuỗi thất bại quá 2 nhịp liên tiếp. Công thức nhịp: *tiến nhỏ → trở ngại mới → tiến nhỏ → sụp đổ lớn → lóe hy vọng → ...* Chính biên độ dao động cảm xúc này khóa chặt sự chú ý, không phải bản thân sự kiện.
- **Chiến thắng phải có giá:** mỗi lần nhân vật đạt được điều gì, bắt họ trả giá bằng thứ khác (biết được sự thật → mất một đồng minh). Điều này khiến ngay cả "phần thưởng" cũng mang mầm bất an.

---

## KỸ THUẬT 4: MIRROR NEURONS — VIẾT ĐỂ CƠ THỂ NGƯỜI NGHE PHẢN ỨNG

**Nguyên lý:** Khi nghe miêu tả chi tiết cảm giác sinh lý của nhân vật, não người nghe **mô phỏng lại chính xác cảm giác đó** (neural coupling). Người nghe không "biết" nhân vật sợ — họ **thấy sợ**.

**Cách áp dụng chi tiết:**
- **Cấm kể tên cảm xúc, bắt buộc tả triệu chứng cơ thể:**
  - ❌ *"Tôi rất sợ hãi."*
  - ✅ *"Hơi thở tôi đứt quãng. Tim nện thịch thịch vào lồng ngực, lấn át cả tiếng bước chân sau lưng tôi."*
  - Bảng quy đổi nhanh: sợ → tim đập/lạnh sống lưng/tay run; ghen → nóng bừng mặt/siết chặt điện thoại/vị đắng trong họng; tội lỗi → không dám nhìn thẳng/nuốt khan; căng thẳng → vai gồng cứng/móng tay bấm vào lòng bàn tay.
  - **Liều lượng (chống sến):** mỗi cảnh chỉ cần MỘT triệu chứng cơ thể đắt, không phải bê cả bảng vào. Và triệu chứng phải KHÔ, cụ thể — *"tim đập nhanh"* được; *"trái tim tôi gào thét trong lồng ngực"* là đã trượt sang sến (chiếu lại lớp lọc văn phong ở đầu skill).
- **Ưu tiên âm thanh trong miêu tả (đặc thù audio):** người nghe đang dùng TAI — miêu tả âm thanh cộng hưởng mạnh nhất: tiếng chìa khóa tra vào ổ, tiếng tin nhắn rung trong đêm, tiếng thở của ai đó ở đầu dây bên kia rồi... tắt máy, sự im lặng đột ngột giữa cuộc cãi vã.
- **Kỹ thuật "zoom cận cảnh" tại khoảnh khắc then chốt:** ở các điểm cảm xúc cao trào, dừng cốt truyện lại, phóng đại một chi tiết cảm giác duy nhất trong 2–3 câu (bàn tay run đến mức không mở nổi khóa điện thoại). Não người nghe cần thời gian để "sống" trong khoảnh khắc. **Nhưng đây là vũ khí HIẾM:** cả truyện chỉ zoom ở 1–2 đỉnh điểm thật sự. Zoom ở mọi beat cảm xúc = sến và làm chùng nhịp; ngoài các đỉnh đó, chạm một nét cơ thể rồi đi tiếp ngay.
- **Đối thoại là bộ đồng bộ hóa:** thời gian nghe thoại ≈ thời gian thực của cảnh, tạo cảm giác "đang có mặt tại đó". Cảnh cao trào cảm xúc nên nặng về thoại + phản ứng cơ thể, nhẹ về dẫn truyện. Thoại phải NGHE tự nhiên khi đọc to — viết xong hãy "đọc thầm bằng tai".
- **Subtext — nhân vật nói MỘT đằng, nghĩ MỘT nẻo:** thoại hay nhất trong drama là khi lời nói và ý thật lệch nhau, buộc người nghe tự đọc ra phần ẩn. Vợ hỏi *"Anh về muộn à?"* với giọng bình thản trong khi tay siết chặt cạnh bàn — người nghe hiểu ngay đây không phải câu hỏi giờ giấc. Càng ít nói thẳng cảm xúc trong thoại, người nghe càng phải "nghiêng người vào" để giải mã, và chính sự tham gia đó giữ chân họ. Tránh thoại "nói toạc" mọi thứ nhân vật đang cảm thấy.
- **Ngắt lời, im lặng, câu bỏ lửng:** người thật không nói trọn câu khi xúc động. Dùng câu ngắt giữa chừng (*"Em tưởng anh đã—"*), khoảng lặng thay câu trả lời, và những từ đệm ngập ngừng để thoại nghe như thật. Một câu hỏi bị đáp lại bằng im lặng còn nặng hơn mọi lời thú nhận.

---

## KỸ THUẬT 5: LÀM CHỦ NHỊP ĐỘ (PACING) DÀNH RIÊNG CHO AUDIO

**Nguyên lý:** Thính giác cực nhạy với nhịp điệu. Nhịp câu văn chi phối trực tiếp nhịp tim người nghe. Nhịp đều đều — dù nhanh hay chậm — đều gây chai lỳ; **sự tương phản** mới giữ não tỉnh táo.

**Cách áp dụng chi tiết:**
- **Cảnh cao trào / hành động / đối đầu:** câu ngắn. Động từ mạnh. Chủ ngữ + động từ, cắt bỏ trạng từ. Có thể dùng câu cụt một hai từ. (*"Cửa bật mở. Chồng tôi đứng đó. Tay cầm điện thoại của tôi."*)
- **Cảnh lắng đọng / u ám / gieo rắc bất an:** câu dài hơn, nhiều mệnh đề nối nhau, từ tượng thanh êm và rợn (rì rào, lạo xạo, văng vẳng), để không khí ngấm dần vào người nghe. **Cảnh báo:** "dài hơn" là so với cảnh cao trào, KHÔNG phải cái cớ để viết hoa mỹ, lê thê. Câu dài vẫn phải đọc-một-hơi-được và vẫn phải gieo/đẩy một điều gì đó (một manh mối, một linh cảm, một vòng lặp) — không dừng lại chỉ để tả cảnh cho "thơ". Nghi ngờ thì cắt ngắn.
- **Quy tắc tương phản:** sau tối đa 3–4 đoạn cùng một nhịp, PHẢI đổi nhịp. Sau cao trào dồn dập, cho một nhịp thở ngắn (một câu tĩnh lặng) — chính nhịp thở này làm cú sốc kế tiếp mạnh gấp đôi.
- **Im lặng là vũ khí:** trong kịch bản audio, chỉ dẫn khoảng ngừng ([ngừng 2 giây], xuống dòng tách đoạn) trước câu thoại quan trọng nhất. Khoảng lặng trước "Anh có điều muốn nói với em" đáng giá hơn mười câu miêu tả.
- **Đổi "chất liệu" mỗi 2–3 phút nghe:** luân phiên thoại → hành động → nội tâm → miêu tả. Không để bất kỳ chất liệu nào kéo dài quá lâu, đặc biệt là nội tâm độc thoại (dễ ru ngủ nhất trong audio).
- **Tương phản cả TÔNG cảm xúc, không chỉ nhịp câu:** một truyện chỉ toàn căng thẳng u ám sẽ khiến người nghe tê liệt cảm xúc y như nhịp đều. Cài xen những khoảnh khắc dịu, ấm, thậm chí một chút hài hước chua chát trước hoặc sau cao trào — chính vùng sáng làm vùng tối sâu hơn. Nỗi đau đặt cạnh một khoảnh khắc hạnh phúc ngắn ngủi đau gấp bội so với nỗi đau nối tiếp nỗi đau.

---

## KỸ THUẬT 6: SETUP–PAYOFF & KHOẢNH KHẮC "AHA!"

**Nguyên lý:** Não bộ tận hưởng cực độ cảm giác chiến thắng khi TỰ MÌNH ghép nối được các mảnh thông tin. Khi người nghe đoán ra sự thật ngay trước khi nhân vật nhận ra, não tự thưởng dopamine cho sự nhạy bén của chính họ.

**Cách áp dụng chi tiết:**
- **Gieo chi tiết "vô thưởng vô phạt":** mọi twist lớn cần 2–3 hạt giống được gieo từ trước, ngụy trang thành chi tiết đời thường (chồng dạo này hay để điện thoại úp mặt xuống bàn; mùi nước hoa lạ thoảng qua bị đổ cho đồng nghiệp). Nguyên tắc ngụy trang: đặt hạt giống **giữa cảnh**, gắn với hành động khác, không bao giờ đặt ở cuối câu/cuối đoạn (vị trí cuối = đèn pha chiếu vào).
- **Quy tắc "gieo 3 lần":** chi tiết quan trọng xuất hiện 3 lần trước khi phát nổ — lần 1 lướt qua, lần 2 hơi lạ, lần 3 phát nổ thành sự thật. Người nghe sẽ có cảm giác *"trời ơi, mình đã nghe thấy nó từ đầu!"*
- **Cho người nghe đi trước nhân vật nửa bước:** thiết kế để người nghe đoán ra sự thật khoảng 10–20 giây TRƯỚC nhân vật. Sớm hơn → sốt ruột; muộn hơn → mất phần thưởng "mình thông minh". Kỹ thuật: cho người nghe thấy một manh mối mà nhân vật bỏ lỡ (dramatic irony), rồi để nhân vật tiến dần về phía sự thật.
- **Vòng tròn khép kín (callback):** cho hình ảnh/câu thoại ở phần đầu quay lại ở phần cuối với ý nghĩa hoàn toàn mới. Câu nói ngọt ngào ở phút đầu trở thành câu mỉa mai cay đắng ở phút cuối. Não thưởng dopamine khi nhận ra khuôn mẫu khép vòng.

---

## KỸ THUẬT 7: NEO CẢM XÚC — KHIẾN NGƯỜI NGHE "CÓ CỔ PHẦN" TRONG CÂU CHUYỆN (OXYTOCIN)

**Nguyên lý:** Dopamine giữ sự tò mò, nhưng oxytocin — hóa chất của gắn kết — mới khiến người nghe QUAN TÂM chuyện gì xảy ra với nhân vật. Tò mò không có quan tâm = người nghe bỏ đi khi biết đáp án. Tò mò + quan tâm = người nghe ở lại đến cùng.

**Cách áp dụng chi tiết:**
- **Trao "cổ phần cảm xúc" trong 2 phút đầu:** trước khi tai họa ập xuống, cho người nghe thấy nhân vật chính có ít nhất MỘT điều đáng quý sắp bị đe dọa (một người mẹ tần tảo, một ước mơ đang gần thành, một đứa con). Mất mát chỉ đau khi người nghe biết thứ sắp mất đáng giá thế nào.
- **Nhân vật phải muốn một điều cụ thể, khẩn thiết:** mọi cảnh, nhân vật chính phải ĐANG MUỐN điều gì đó và bị cản trở. Nhân vật không có mong muốn = cảnh chết.
- **Khuyết điểm tạo gắn kết:** nhân vật hoàn hảo không kích hoạt mirror neurons. Cho nhân vật chính điểm yếu con người (cả tin, sĩ diện, hèn nhát đúng lúc cần dũng cảm) — người nghe gắn bó với người giống mình, không phải người hơn mình.
- **Phản diện phải có logic riêng:** kẻ phản bội/phản diện tin rằng mình có lý do chính đáng. Phản diện "ác vì ác" làm câu chuyện rẻ tiền; phản diện có lý làm người nghe day dứt — và day dứt là thứ khiến họ nghĩ về câu chuyện sau khi đã tắt audio.
- **Đặt nhân vật vào song đề (dilemma), không chỉ khó khăn:** khó khăn = cần vượt qua; song đề = phải CHỌN giữa hai điều đều mất mát (nói ra sự thật thì gia đình tan vỡ, im lặng thì tự phản bội chính mình). Song đề buộc người nghe tự hỏi *"nếu là mình, mình chọn gì?"* — mức độ tham gia nhận thức cao nhất.

---

## KỸ THUẬT 8: LIỀU LƯỢNG CĂNG THẲNG (CORTISOL) & LEO THANG

**Nguyên lý:** Cortisol — hormone căng thẳng — là tín hiệu "chú ý, có điều quan trọng". Nhưng cortisol liên tục không nghỉ khiến người nghe kiệt sức và phòng thủ; căng thẳng phải được **liều lượng hóa** và **leo thang có kiểm soát**.

**Cách áp dụng chi tiết:**
- **Leo thang cược (stakes):** mỗi hồi, thứ nhân vật có thể mất phải LỚN HƠN hồi trước: thể diện → hôn nhân → tài sản/con cái → nhân phẩm/mạng sống. Nếu cược không tăng, câu chuyện đang giậm chân dù sự kiện vẫn diễn ra.
- **Nhịp thở sau sốc:** sau mỗi cú sốc lớn, cho 30–60 giây nghe "hạ nhiệt" (một cảnh nhỏ dịu hơn, một khoảnh khắc đời thường) — không phải để nghỉ, mà để **nạp lại độ nhạy** cho cú sốc tiếp theo, và trong lúc hạ nhiệt vẫn gieo hạt giống cho vòng lặp mới.
- **Đồng hồ đếm ngược:** khi câu chuyện chùng, thêm giới hạn thời gian ("trước khi bố mẹ hai bên gặp nhau cuối tuần này", "trước khi kết quả xét nghiệm được gửi về nhà"). Deadline biến căng thẳng mơ hồ thành căng thẳng đo đếm được.

---

## KỸ THUẬT 9: THIẾT KẾ ÂM THANH & CHỈ DẪN SẢN XUẤT (ĐẶC THÙ AUDIO)

**Nguyên lý:** Đây là truyện AUDIO — âm thanh không phải trang trí, nó là một lớp kể chuyện song song. Một tiếng động đúng lúc truyền tải điều mà cả đoạn văn không làm được, và trực tiếp kích hoạt phản ứng sinh lý (giật mình, rợn người) mà văn bản thuần không đạt tới.

**Cách áp dụng chi tiết:**
- **Chèn chỉ dẫn âm thanh dưới dạng thẻ vuông** để người sản xuất/giọng đọc/công cụ TTS biết xử lý, ví dụ: `[tiếng mưa rào ngoài cửa sổ]`, `[nhạc nền căng thẳng, nhỏ dần]`, `[tiếng chìa khóa tra vào ổ]`, `[im lặng 3 giây]`. Hỏi người dùng (hoặc mặc định) xem họ có cần lớp chỉ dẫn này không; nếu truyện thuần giọng đọc thì lồng âm thanh vào chính lời văn thay vì thẻ.
- **Ba loại âm thanh nên thiết kế có chủ đích:**
  1. *Âm thanh môi trường (ambience):* thiết lập không gian trong 1 câu (tiếng ve, tiếng quạt trần, tiếng phố xá) — đổi ambience là cách rẻ nhất để báo hiệu chuyển cảnh trong audio.
  2. *Âm thanh biến cố (một phát):* tiếng cửa, tiếng ly vỡ, tiếng tin nhắn — đặt đúng khoảnh khắc để tạo cú giật.
  3. *Nhạc nền (score):* dâng lên trước cao trào, tắt phựt ngay tại cú sốc (cắt nhạc đột ngột là một trong những cú sốc audio mạnh nhất).
- **Motif âm thanh gắn với bí ẩn:** gán một âm thanh đặc trưng cho một manh mối (một giai điệu chuông điện thoại lạ, một tiếng ho đặc biệt). Mỗi lần âm thanh đó vang lên, người nghe rùng mình vì nhớ — đây là "gieo 3 lần" bằng âm thanh.
- **Đánh dấu khoảng lặng như một nhịp thật:** trong audio, 2 giây im lặng là một sự kiện. Ghi rõ nơi cần ngừng; đừng để giọng đọc trôi tuột qua khoảnh khắc đáng lẽ phải nghẹn lại.

---

## KỸ THUẬT 10: GIỌNG KỂ — CƠ CHẾ GIỮ CHÂN THẦM LẶNG

**Nguyên lý:** Cốt truyện giữ người nghe tò mò *chuyện gì xảy ra tiếp theo*; nhưng **giọng kể** (narrative voice) mới khiến họ muốn ở lại *bất kể* chuyện gì xảy ra. Trong một truyện dài, sẽ có những đoạn trầm (phát triển nhân vật, cài cắm) mà cốt truyện chùng xuống — nếu người nghe chỉ ở lại vì cốt truyện, những đoạn đó sẽ mất họ. Giọng kể là thứ đỡ lấy các đoạn trầm.

**Cách áp dụng chi tiết:**
- **Cho người kể một giọng riêng, nhất quán:** cách người kể nhìn thế giới — chua chát, ngây thơ, tỉnh táo lạnh lùng, hài hước cay đắng — phải xuyên suốt và ổn định. Một góc nhìn đặc biệt về những chuyện đời thường khiến ngay cả cảnh rót một tách trà cũng đáng nghe.
- **Nội tâm phải sắc, không lải nhải:** ngôi thứ nhất dễ sa vào độc thoại dài lê thê (lỗi ru ngủ số một của audio). Nội tâm chỉ được phép xuất hiện khi nó *tiến triển* điều gì — một nhận ra mới, một mâu thuẫn nội tâm — và phải ngắn, sắc, có nhịp.
- **Quan điểm, không phải camera:** người kể không tường thuật khách quan như máy quay; họ *diễn giải*, phán xét, giấu giếm, tự dối mình. Một người kể ngôi thứ nhất che giấu điều gì đó với chính mình (người kể không đáng tin) là mỏ vàng của thể loại drama — người nghe dần nhận ra sự thật mà người kể không dám thừa nhận.
- **Câu chữ mang khẩu khí người kể:** dùng cách nói, ví von, thói quen ngôn ngữ khớp với con người và hoàn cảnh của người kể (một người bán hàng ngoài chợ không ví von như một giáo sư). Đây cũng là cách gián tiếp khắc họa nhân vật mà không cần tả.

---

## CẤU TRÚC PHÂN ĐOẠN CHO TRUYỆN AUDIO NHIỀU PHẦN

Nếu truyện chia chương/tập, mỗi phân đoạn theo khung sau (mỗi phân đoạn là một "đơn vị dopamine" hoàn chỉnh):

1. **Mở (10%):** móc nối tức thì — hệ quả trực tiếp của cliffhanger trước hoặc một xáo trộn mới. KHÔNG tóm tắt lại dài dòng.
2. **Thân (75%):** ít nhất MỘT tiến triển thật sự của cốt truyện (người nghe phải cảm thấy "câu chuyện đã đi được một bước") + một dao động hy vọng/tuyệt vọng + gieo/tưới ít nhất một hạt giống.
3. **Kết (15%):** cliffhanger (xoay vòng 4 loại ở Kỹ thuật 2). Câu chốt ngắn, sắc, đặt thông tin gây sốc ở những từ CUỐI CÙNG.

**Quy tắc mỗi-phân-đoạn-một-vòng-cung:** mỗi tập phải có vòng cung cảm xúc riêng hoàn chỉnh (một khám phá, một chuyển biến quan hệ, một quyết định) NGOÀI việc treo móc câu — tập chỉ có cliffhanger mà không có sự thỏa mãn nội tại sẽ khiến người nghe kiệt sức và bỏ đi sau vài tập.

**Độ dài & thời lượng (tham khảo):**
- Nếu người dùng không nêu độ dài, hỏi ngắn gọn: một tập hay nhiều tập, và mong muốn dài cỡ nào. Đừng đoán mò một con số rồi viết cả nghìn chữ sai ý.
- Kinh nghiệm chung cho serial: mỗi tập gọn để nghe hết trong một lần (khoảng 5–15 phút nghe / ~1.200–2.500 chữ) tạo hiệu ứng "nghe một mạch"; tập quá dài khiến người nghe trì hoãn, tập quá ngắn thì hụt hẫng.
- **Tính bằng tai, không bằng mắt:** ước lượng thời lượng theo tốc độ đọc (tiếng Việt kể chuyện ~130–160 chữ/phút), vì thứ người dùng cần là số PHÚT audio, không phải số trang.
- **Móc nối đầu tập (recap) cho truyện dài:** nếu nhiều tập cách nhau, chèn 1–2 câu nhắc lại tình huống — nhưng lồng vào cảm xúc/hành động, tuyệt đối không tóm tắt khô khan kiểu "ở tập trước...".

---

## NHỮNG LỖI GIẾT CHẾT SỰ HẤP DẪN (CẤM)

1. **Mở đầu bằng lý lịch/bối cảnh** thay vì hành động hoặc bất thường.
2. **Info-dump:** đổ một khối thông tin nền vào một chỗ. Thông tin nền phải được nhỏ giọt qua thoại, hành động, xung đột.
3. **Kể tên cảm xúc** ("cô rất đau khổ") thay vì tả triệu chứng cơ thể.
4. **Đóng hết vòng lặp cùng lúc** giữa truyện → người nghe hết lý do ở lại.
5. **Nhân vật chính thụ động:** mọi bước ngoặt phải đến từ QUYẾT ĐỊNH của nhân vật, không phải trùng hợp. Trùng hợp được phép GÂY RA rắc rối, không được phép GIẢI QUYẾT rắc rối.
6. **Twist không gieo trước** → cảm giác bị lừa.
7. **Cliffhanger một màu** (chương nào cũng nguy hiểm thể xác) → chai lỳ, mất niềm tin.
8. **Nhịp văn đều đều** từ đầu đến cuối, dù đều nhanh hay đều chậm.
9. **Câu văn không đọc to được:** câu quá dài, nhiều mệnh đề lồng nhau khiến giọng đọc hụt hơi và người nghe mất dấu. Viết cho TAI, không viết cho MẮT.
10. **Kết truyện bỏ nợ:** Câu Hỏi Trung Tâm phải được trả lời trọn vẹn; vòng lặp lớn không đóng = phản bội người nghe (khác với chủ đích chừa mầm cho phần sau — mầm mới được phép, nợ cũ thì không).
11. **Độc thoại nội tâm lê thê:** đoạn nội tâm dài không tiến triển gì — lỗi ru ngủ số một của audio. Cắt bớt, chỉ giữ phần sắc.
12. **Thoại "nói toạc":** nhân vật nói thẳng hết mọi cảm xúc và ý định, không còn subtext để người nghe giải mã.
13. **Tông cảm xúc một màu:** căng thẳng/bi thương liên tục không có vùng dịu, khiến người nghe tê liệt cảm xúc.
14. **Sến / hoa mỹ / sáo mòn:** ẩn dụ cảm xúc mòn ("tim tan vỡ", "lệ rơi như mưa", "đau xé tâm can"), câu cảm thán than thân, chồng chất tính từ. Lỗi phá hỏng văn phong hiện đại nhanh nhất — chiếu lại lớp lọc "Văn phong: DỨT KHOÁT" ở đầu skill.
15. **Tả để cho đẹp:** câu mô tả không đẩy truyện, không tăng tò mò/căng thẳng, chỉ tô vẽ khung cảnh hoặc cảm xúc → cắt. Miêu tả phải làm việc, không được ngồi không.
16. **Đau hộ người nghe:** kể lể/khuếch đại cảm xúc thay vì để một chi tiết khô tự gây đau. Tiết chế đánh mạnh hơn gào thét.

---

## CHECKLIST TỰ KIỂM TRA TRƯỚC KHI TRẢ KẾT QUẢ

Trước khi gửi kịch bản cho người dùng, rà lại toàn bộ:

- [ ] **VĂN PHONG:** đọc lại toàn bộ — có câu nào "sến"/sáo mòn/nghe như lời bolero không? Có ẩn dụ cảm xúc mòn (tim tan vỡ, lệ rơi, đau xé lòng) không? → xóa hoặc viết lại cho cụ thể, khô.
- [ ] **VĂN PHONG:** mỗi câu mô tả có đẩy truyện / tăng tò mò / tăng căng thẳng không, hay chỉ tô vẽ cho đẹp? Cắt phần ngồi không.
- [ ] **VĂN PHONG:** câu chữ có dứt khoát, ít chữ, cụ thể — không chồng tính từ/trạng từ, không than vãn kể lể — không?
- [ ] 30 giây đầu có hook đủ mạnh để một người lạ dừng tay lại nghe không?
- [ ] Câu Hỏi Trung Tâm được gieo trong 1–2 phút đầu chưa?
- [ ] Tại MỌI thời điểm, có ít nhất 2 vòng lặp đang mở không?
- [ ] Có ít nhất 3 lần đảo chiều hy vọng ↔ tuyệt vọng không?
- [ ] Twist lớn có ít nhất 2 hạt giống gieo trước (quy tắc gieo 3 lần) không?
- [ ] Cảm xúc được TẢ bằng cơ thể/âm thanh thay vì KỂ tên không?
- [ ] Nhịp câu có tương phản rõ giữa cao trào (câu ngắn) và lắng đọng (câu dài)?
- [ ] Cược có leo thang qua từng hồi không?
- [ ] Mỗi phân đoạn kết bằng cliffhanger, và các cliffhanger có xoay vòng loại không?
- [ ] Nhân vật chính có mong muốn cụ thể, có khuyết điểm, có ra quyết định chủ động không?
- [ ] Có ít nhất một song đề (lựa chọn hai bề đều mất) không?
- [ ] Có callback khép vòng ở phần kết không?
- [ ] Thoại ở các cảnh căng có subtext (nói một đằng nghĩ một nẻo) không, hay đang "nói toạc"?
- [ ] Có tương phản tông cảm xúc (ít nhất một vùng dịu/sáng) chứ không một màu u ám không?
- [ ] Nếu là truyện audio có sản xuất: đã cân nhắc chỉ dẫn âm thanh/khoảng lặng ở các điểm then chốt chưa?
- [ ] Giọng kể có nhất quán và có cá tính riêng không? Nội tâm có bị lê thê không?
- [ ] Đọc to lên: câu chữ có trôi tự nhiên, không hụt hơi không?
- [ ] Câu Hỏi Trung Tâm đã được trả lời trọn vẹn ở kết chưa?
- [ ] **AN TOÀN NỀN TẢNG:** toàn bộ kịch bản đã qua bộ lọc từ vựng an toàn chưa? Còn từ nào trong danh sách cấm (giết, chết, xác, quan tài, tự tử, đâm, chém, máu me...) chưa được thay bằng từ tương đương trong bảng quy đổi không?

Nếu bất kỳ mục nào chưa đạt → sửa trước khi trả kết quả, không hỏi lại người dùng.

---

## QUY TẮC AN TOÀN NỀN TẢNG — TỪ VỰNG CHỐNG KIỂM DUYỆT (BẮT BUỘC)

**Nguyên lý:** Kịch bản truyện audio được sản xuất thành video/audio đăng lên TikTok và YouTube. AI kiểm duyệt của các nền tảng này quét cả giọng đọc (ASR), phụ đề, và text trên video. Các từ ngữ trực diện liên quan đến bạo lực, cái chết, tự hại sẽ khiến video bị **bóp tương tác, hạn chế phân phối, hoặc gỡ bỏ** — dù ngữ cảnh là kể chuyện hư cấu.

**Nguyên tắc tối thượng:** KHÔNG BAO GIỜ dùng từ nhạy cảm trực diện khi có từ thay thế mang sức nặng TƯƠNG ĐƯƠNG hoặc MẠNH HƠN. Từ thay thế phải là từ Hán-Việt trang trọng, từ miêu tả trạng thái cụ thể, hoặc từ mang tính điện ảnh — KHÔNG ĐƯỢC dùng từ nói giảm nói tránh kiểu nhạt nhẽo (ví dụ: "không còn trên đời", "ra đi") vì chúng làm MẤT sức nặng của câu văn. Mục tiêu là câu thay thế phải NGHIỆT NGÃ HƠN hoặc ÍT NHẤT BẰNG bản gốc.

### BẢNG QUY ĐỔI TỪ VỰNG BẮT BUỘC

| Từ nhạy cảm (CẤM dùng) | Từ thay thế an toàn (BẮT BUỘC dùng) | Ghi chú |
|---|---|---|
| **giết** | *đoạt mạng, kết liễu, xuống tay, bức tử, thủ tiêu, ra tay* | "Đoạt mạng" và "kết liễu" nghe lạnh lùng và tàn nhẫn hơn "giết" |
| **chết** | *tắt thở, bỏ mạng, mất mạng, ngừng thở, nhắm mắt* | "Tắt thở" cụ thể và gai người hơn "chết" |
| **cái chết** | *sự ra đi vĩnh viễn, kết cục, hồi kết* | Chọn từ phù hợp ngữ cảnh |
| **xác chết / xác** | *thi thể, thân xác lạnh ngắt* | "Thi thể" vừa trang trọng vừa ám ảnh |
| **quan tài** | *cỗ áo quan, cỗ ván, chiếc hòm gỗ* | "Áo quan" mang hơi hướm tâm linh, rợn hơn |
| **giấy báo tử** | *giấy chứng tử, tờ khai tử* | Từ pháp lý, AI thường bỏ qua |
| **tự tử / tự sát** | *tự kết liễu, tự tay chấm dứt, tìm đến cái kết* | Tránh tuyệt đối "tự tử/tự sát" — nhóm từ bị quét gắt nhất |
| **nhảy cầu / thắt cổ / cắt tay** | *gieo mình, tự dồn mình vào chân tường, tìm đường thoát* | Các từ mô tả cách thức tự hại cụ thể rất dễ bị quét |
| **đâm / chém** | *đâm xuyên, vung nhát dao, phóng lưỡi dao* | Miêu tả hành động thay vì dùng động từ trần |
| **đánh đập / bạo hành** | *thượng cẳng chân hạ cẳng tay, giáng đòn, trút đòn thù* | TikTok rất nhạy cảm với bạo lực gia đình/học đường |
| **sát hại / ám sát / xử tử** | *trừ khử, lấy mạng, tiễn đi* | Từ Hán-Việt hoặc ẩn dụ |
| **máu / máu me** | *vệt đỏ, dòng ấm, chất lỏng sẫm màu* | Miêu tả cảm giác/màu sắc thay vì gọi tên |
| **súng / đạn** | *vũ khí nóng, họng đen ngòm, siết cò* | Tránh nhắc tên vũ khí trực tiếp |
| **thuốc độc / ma túy** | *chất độc, liều thuốc định mệnh, thứ bột trắng* | Nền tảng cấm tuyệt đối chất cấm/chất gây nghiện |
| **ngạt khí / ngạt thở** | *thiếu dưỡng khí, phổi bỏng rát, lồng ngực thắt nghẹn, lịm đi* | Tả triệu chứng cơ thể hoặc trạng thái ngột ngạt |
| **tra tấn** | *hành hạ, dày vò, đày đọa* | Hán-Việt ít bị quét hơn |
| **hiếp dâm** | *cưỡng bức, xâm hại* | Tuyệt đối không dùng trực diện |
| **đám tang / tang lễ** | *ngày tiễn đưa, lễ tiễn biệt, buổi lễ cuối cùng* | Tùy ngữ cảnh |
| **sát nhân / kẻ giết người** | *kẻ xuống tay, hung thủ, kẻ đoạt mạng* | "Hung thủ" là từ pháp lý, rất an toàn |
### QUY TẮC ÁP DỤNG

1. **Lớp lọc tự động:** Khi viết kịch bản, agent PHẢI tự động thay thế mọi từ trong cột "CẤM" bằng từ trong cột "BẮT BUỘC" NGAY KHI VIẾT — không viết xong rồi mới sửa.
2. **Ưu tiên từ mạnh hơn bản gốc:** Khi có nhiều lựa chọn thay thế, LUÔN chọn từ nào nghe NGHIỆT NGÃ, LẠNH LÙNG, hoặc CỤ THỂ hơn. Mục tiêu: câu thay thế phải khiến người đọc/nghe cảm thấy sức nặng KHÔNG HỀ GIẢM.
3. **Ngữ cảnh quyết định:** nếu một từ nhạy cảm xuất hiện trong ngữ cảnh hoàn toàn vô hại (ví dụ: "chết cười", "giết thời gian"), KHÔNG cần thay thế — AI kiểm duyệt đánh giá theo ngữ cảnh tổng thể.
4. **Tiêu đề video cũng phải an toàn:** tiêu đề truyện (hook số 0) là nơi AI quét ĐẦU TIÊN. Tuyệt đối không đặt tiêu đề chứa từ "giết", "chết", "xác", "tự tử".
5. **Không dùng algospeak (viết lách kiểu ch.ết, g!ết)** trong kịch bản — điều này chỉ áp dụng ở khâu làm phụ đề sau sản xuất, không phải trong văn bản kịch bản.

### VÍ DỤ ĐỐI CHIẾU

| ❌ Bản nhạy cảm | ✅ Bản an toàn (mạnh hơn) |
|---|---|
| *"Chồng tôi giết tôi bằng một chiếc xích sắt."* | *"Chồng tôi đoạt mạng tôi bằng một chiếc xích sắt."* |
| *"Tôi đã chết trong nhà kho."* | *"Tôi đã tắt thở trong nhà kho."* |
| *"Không có xác nào trong xe."* | *"Không có thi thể nào trong xe."* |
| *"Một cái chết còn tử tế hơn."* | *"Một sự kết liễu còn tử tế hơn."* |
| *"Kẻ sát nhân đứng ngoài cửa."* | *"Kẻ đoạt mạng đứng ngoài cửa."* |
| *"Tôi nhìn thấy anh ta trong cỗ quan tài."* | *"Tôi nhìn thấy anh ta trong cỗ áo quan."* |

---

## THIẾT KẾ KẾT THÚC ĐỌNG LẠI

Kết thúc quyết định người nghe có nhớ và giới thiệu truyện cho người khác không. Trả lời trọn Câu Hỏi Trung Tâm là mức tối thiểu; để kết đọng lại:
- **Cú twist cuối (nếu có) phải là chốt của foreshadow, không phải cú lừa mới:** cú lật cuối cùng nên khiến người nghe muốn nghe lại từ đầu để soi các manh mối — đó là dấu hiệu twist được cài đúng.
- **Công lý/nhân quả có thể lệch chuẩn nhưng phải có TRỌNG LƯỢNG:** kết có hậu, kết đắng, hay kết nửa vời đều được — miễn nó tương xứng với cái giá nhân vật đã trả. Kết dễ dãi (mọi thứ tự nhiên tốt đẹp) xóa sạch căng thẳng đã dựng.
- **Callback khép vòng:** đóng lại bằng hình ảnh/câu thoại đã mở ở đầu, nay mang nghĩa mới — cho người nghe cú dopamine "khép vòng" cuối cùng.
- **Dư âm ở câu cuối:** câu chốt truyện nên để lại một cảm xúc hoặc một ý nghĩ vang vọng, không giải thích thêm. Dừng đúng lúc, đừng viết thêm một đoạn "bài học rút ra".
- **Chừa mầm ≠ bỏ nợ:** nếu định làm phần tiếp, được phép gieo một vòng lặp MỚI ở câu cuối; nhưng mọi nợ cũ trong tập này vẫn phải trả xong.

---

## GHI CHÚ ÁP DỤNG THEO THỂ LOẠI

Skill này là nền tảng chung. Khi người dùng chỉ định thể loại, giữ nguyên toàn bộ khung trên và chỉ điều chỉnh **chất liệu**:
- **Drama/ngoại tình:** cược = quan hệ, danh dự, con cái; vòng lặp = bí mật và bằng chứng; song đề đạo đức là vũ khí chủ lực; twist mạnh nhất là đảo vai nạn nhân–thủ phạm.
- **Trinh thám:** vòng lặp = manh mối; kỹ thuật gieo 3 lần và "Aha!" là xương sống; mỗi nghi phạm là một vòng lặp trung.
- **Kinh dị:** nhịp độ và âm thanh (Kỹ thuật 4, 5) là chủ lực; nỗi sợ đến từ điều CHƯA thấy — kéo dài vòng lặp mở lâu hơn bình thường.
- **Tình cảm:** dao động hy vọng–tuyệt vọng áp lên khoảng cách giữa hai người; cliffhanger thiên về loại "ngã ba quyết định" và "tiết lộ".

Không hỏi lại người dùng về các chi tiết kỹ thuật này — tự áp dụng. Chỉ hỏi lại khi yêu cầu thiếu thông tin cốt yếu (ví dụ: độ dài mong muốn, một tập hay nhiều tập).

<!-- audio-story-engagement-SKILL:end -->
