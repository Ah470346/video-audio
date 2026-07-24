# VoxCPM Style Tags Cho Kịch Bản Ngắn

Tài liệu này tổng hợp cách dùng style/control instruction cho VoxCPM2 trong
pipeline kịch bản ngắn của repo.

Quan trọng: VoxCPM2 không có danh sách tag cố định kiểu SSML. Docs chính thức
mô tả `--control` là chỉ dẫn bằng ngôn ngữ tự nhiên, hoặc đặt trong ngoặc tròn
trước text theo mẫu `(control instruction)Nội dung cần đọc`. Vì vậy các tag
dưới đây là bộ quy ước của repo để viết nhất quán, không phải enum chính thức
của VoxCPM.

Nguồn chính thức:

- https://voxcpm.readthedocs.io/en/latest/usage_guide.html
- https://voxcpm.readthedocs.io/en/latest/reference/api.html
- https://voxcpm.readthedocs.io/en/latest/models/voxcpm2.html
- https://voxcpm.readthedocs.io/en/latest/cookbook.html
- https://voxcpm.readthedocs.io/en/latest/reference/changelog.html

## Cách Viết Trong Kịch Bản Ngắn

Dùng `@style` trên một dòng riêng. Style áp dụng cho các dòng sau nó cho đến
`@style` tiếp theo.

```text
@style slow, fearful, trembling
Đừừng...
đừng mở cánh cửa đó.

@style angry, firm
Anh nói lại xem.
Ai cho phép em làm vậy?

@style off
Tôi im lặng nhìn anh.
```

- `@style default`: quay về style mặc định của pipeline ngắn.
- `@style off`: tắt style control cho đoạn sau.
- Khuyến nghị mỗi `@style` chỉ dùng 1-3 tag/cụm tag để VoxCPM bám tốt hơn.
- Nên dùng tiếng Anh cho tag/control vì ví dụ chính thức của docs dùng tiếng Anh
  và tiếng Trung; tiếng Việt có thể thử, nhưng không nên coi là ổn định bằng.

## Nguyên Tắc Mapping

Pipeline ngắn sẽ biến:

```text
@style slow, fearful
Đừừng...
```

thành text đưa vào VoxCPM:

```text
(slow, fearful)Đừừng...
```

Dòng `@style` không bị đọc thành tiếng và không nằm trong expected text của QC.

## Tag Nhịp Độ

| Tag | Giải thích | Dùng khi |
| --- | --- | --- |
| `slow` | Đọc chậm, có khoảng trống hơn | Cần căng thẳng, buồn, nhấn mạnh |
| `slightly slower` | Chậm nhẹ, ít rủi ro hơn `slow` | Muốn thêm diễn cảm nhưng vẫn tự nhiên |
| `fast` | Đọc nhanh | Cần gấp gáp, hoảng hốt, tranh cãi |
| `slightly faster` | Nhanh nhẹ | Cần nâng tempo mà không bị vỡ nhịp |
| `urgent` | Giọng gấp, thôi thúc | Cảnh nguy hiểm, tin xấu, câu lệnh |
| `hesitant` | Ngập ngừng, do dự | Nhân vật sợ, đau lòng, chưa dám nói |
| `measured` | Đọc điềm tĩnh, cân nhắc | Kể chuyện nghiêm túc, đọc phân tích |
| `deliberate` | Nhấn từng chữ có chủ ý | Câu đe dọa, câu kết luận, lời thú tội |

## Tag Cảm Xúc

| Tag | Giải thích | Dùng khi |
| --- | --- | --- |
| `emotional` | Có cảm xúc rõ hơn mặc định | Đoạn cao trào chung |
| `sad` | Buồn, trầm | Mất mát, chia tay, hối tiếc |
| `broken` | Vỡ vụn, nghe như sắp sụp đổ | Khóc nghẹn, bị phản bội, tiết lộ đau lòng |
| `angry` | Giận dữ | Đối đầu, bị lừa dối, tranh cãi |
| `restrained anger` | Kiềm nén giận dữ | Giận nhưng không quát, nguy hiểm hơn |
| `fearful` | Sợ hãi | Kinh dị, bị đe dọa, phát hiện sự thật |
| `tense` | Căng thẳng | Trước twist, khi nghe tiếng động lạ |
| `anxious` | Lo lắng, bồn chồn | Chờ kết quả, che giấu bí mật |
| `cheerful` | Vui, sáng | Cảnh nhẹ nhàng, mở đầu ấm áp |
| `warm` | Ấm áp, gần gũi | Lời an ủi, yêu thương, hội tụ |
| `cold` | Lạnh, ít cảm xúc | Nhân vật tàn nhẫn, xa cách |
| `tender` | Dịu dàng | Tình cảm, chăm sóc, tha thứ |
| `melancholic` | Buồn man mác | Hồi ức, kết buồn, nỗi nhớ |
| `passionate` | Đầy nhiệt huyết | Thổ lộ, tranh luận, lời hứa mạnh |

## Tag Cách Nói

| Tag | Giải thích | Dùng khi |
| --- | --- | --- |
| `dramatic narration` | Kể chuyện kịch tính | Trailer, twist, drama ngắn |
| `short-form narration` | Hợp clip ngắn, nhịp gọn | TikTok/Reels/Shorts |
| `storytelling` | Kể chuyện tự nhiên | Narrator dẫn truyện |
| `whispering` | Thì thầm | Bí mật, cảnh đêm, kinh dị |
| `mysterious` | Bí ẩn | Mở đầu vụ án, dấu hiệu lạ |
| `suspenseful` | Tạo hồi hộp | Trước khi lật bài |
| `confessional` | Như đang thú nhận | Đọc nhật ký, lời kể thật lòng |
| `threatening` | Đe dọa | Phản diện, tối hậu thư |
| `pleading` | Cầu xin | Xin đừng bỏ đi, xin tha thứ |
| `commanding` | Ra lệnh, áp đảo | Nhân vật quyền lực |
| `conversational` | Tự nhiên như nói chuyện | Thoại đời thường |
| `narrator voice` | Giọng người dẫn chuyện | Phần kể ngoài lời thoại |

## Tag Lực Giọng Và Chất Giọng

| Tag | Giải thích | Dùng khi |
| --- | --- | --- |
| `firm` | Chắc, đứng vững | Câu khẳng định, cần uy |
| `soft` | Mềm, nhẹ | An ủi, tình cảm |
| `low voice` | Giọng thấp | Đe dọa, bí mật, nghiêm trọng |
| `low-pitched` | Âm vực thấp hơn | Giọng nam trầm, không khí nặng |
| `raspy` | Hơi khàn, rám | Mệt mỏi, từng trải, bị thương |
| `clear articulation` | Phát âm rõ | Câu quan trọng, tên riêng, thông tin cần chính xác |
| `magnetic` | Cuốn hút | Narrator hấp dẫn, mở đầu quyến rũ |
| `gentle` | Nhẹ nhàng | Đoạn tình cảm, chăm sóc |
| `sharp` | Sắc, gắt | Chất vấn, nói lời đau |
| `trembling` | Run run | Sợ hãi, khóc, sốc |

## Tag Cường Độ

| Tag | Giải thích | Dùng khi |
| --- | --- | --- |
| `subtle` | Nhẹ, không làm quá | Cần diễn cảm vừa phải |
| `intense` | Mạnh, đầy áp lực | Cao trào, bị phát hiện |
| `quietly intense` | Nhỏ nhưng căng | Đe dọa nhỏ giọng, nói trong phòng kín |
| `shouting` | Hét/lớn tiếng | Cao trào rất mạnh; dùng ít vì dễ méo |
| `controlled` | Kiểm soát | Nhân vật lý trí, lạnh lùng |
| `explosive` | Bùng nổ | Tức giận đột ngột, plot twist |

## Combo Khuyên Dùng

| Combo | Hiệu ứng | Ví dụ dùng |
| --- | --- | --- |
| `slow, fearful, trembling` | Sợ hãi, ngập ngừng, run | Kinh dị, câu "Đừng..." |
| `slow, sad, broken` | Đau lòng, vỡ vụn | Chia tay, mất con, bị phản bội |
| `cold, low voice, threatening` | Lạnh và nguy hiểm | Phản diện nói nhỏ |
| `angry, firm, sharp` | Giận và cắt | Chất vấn, đối đầu |
| `warm, gentle, tender` | Dịu dàng | An ủi, tình cảm |
| `urgent, fast, anxious` | Gấp và lo | Báo tin xấu, chạy trốn |
| `mysterious, slow, suspenseful` | Bí ẩn, hồi hộp | Mở đầu vụ án/kinh dị |
| `confessional, soft, melancholic` | Thú nhận nhẹ, buồn | Đọc thư, đọc nhật ký |
| `dramatic narration, intense` | Kịch tính mạnh | Trailer, twist cuối |
| `measured, clear articulation` | Rõ ràng, điềm tĩnh | Thông tin quan trọng |

## Khuyến Nghị Cho Kịch Bản Ngắn

| Mục đích | Style nên dùng |
| --- | --- |
| Mở đầu gây móc câu | `mysterious, slow, suspenseful` |
| Câu shock/twist | `dramatic narration, intense` |
| Nhân vật cầu xin | `pleading, sad, trembling` |
| Nhân vật tức giận | `angry, firm, sharp` |
| Nhân vật lạnh lùng | `cold, controlled, low voice` |
| Câu cần nghe rõ | `measured, clear articulation` |
| Kể chuyện mặc định | `expressive Vietnamese dramatic short-form narration, emotional emphasis, natural pauses, clear articulation` |

## Điều Nên Tránh

- Không viết style sau câu như `Đừng...(emotion)`. VoxCPM có thể coi đó là text
  lạ hoặc hiểu không ổn định.
- Không nhồi quá nhiều tag: `sad, angry, happy, fast, slow, shouting,
  whispering` sẽ mâu thuẫn.
- Không dùng `shouting` quá nhiều; dễ bị chói, vỡ giọng, hoặc méo âm.
- Không dùng style control với ultimate/prompt-text cloning. Docs API nói
  `--control` không dùng chung với `--prompt-text`; pipeline ngắn dùng
  reference-only cloning để giữ khả năng điều khiển style.

