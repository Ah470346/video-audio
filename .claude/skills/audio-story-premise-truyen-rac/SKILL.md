---
name: audio-story-premise-truyen-rac
description: |
  Skill TIỀN ĐỀ (premise modifier) cho dòng TRUYỆN RÁC / "TRUYỆN NÃO TÀN" đang hot trên mạng — kiểu truyện mà nhân vật chính hoặc một nhân vật phụ NGU đến mức phi lý ("không có não", "não phẳng", "óc chó"), tình tiết lố bịch, nhưng chính sự vô lý đó kích thích ỨC CHẾ và giữ người nghe dán mắt chờ lúc "sáng mắt / trả giá". Người xem thường bảo nhau "tháo não ra trước khi nghe".
  Đây KHÔNG phải một thể loại — nó là một LỚP TIỀN ĐỀ chồng lên. LUÔN dùng KẾT HỢP ĐỒNG THỜI với: (1) skill nền tảng "audio-story-engagement" VÀ (2) skill thể loại tương ứng (audio-story-genre-drama / -trinh-tham / -kinh-di / -tinh-cam / -hai-huoc). Chồng được cả với "audio-story-premise-biet-truoc" (trùng sinh/hệ thống/xuyên sách + truyện rác).
  Kích hoạt khi prompt của người dùng chứa: "truyện rác", "truyện não tàn", "não phẳng", "không có não", "óc chó", "nhân vật ngu", "ngu không tưởng", "tháo não", "rage bait", "truyện ức chế", "tình tiết lố bịch/phi lý", "drama mạng kiểu ngu", "chồng ngu mẹ chồng ngu", "nữ chính ngu", HOẶC bất kỳ tổ hợp nào như "truyện rác drama", "truyện rác trùng sinh", "kinh dị não tàn"...
---

# Tiền Đề: TRUYỆN RÁC ("tháo não trước khi nghe")

**Đây là một *modifier*, KHÔNG tự đứng một mình.** Khi kích hoạt, chồng các lớp:
1. **Nền** — `audio-story-engagement` (hook, Zeigarnik, pacing, xưng hô, văn phong dứt khoát, an toàn từ vựng). Bất biến.
2. **Thể loại** — skill `audio-story-genre-*` khớp thể loại người dùng nêu. Cung cấp chất liệu xung đột.
3. **Tiền đề (skill này)** — cơ chế "ngu có chủ đích + lố bịch có kiểm soát" để bơm ức chế.
4. *(tùy chọn)* — `audio-story-premise-biet-truoc` nếu prompt có trùng sinh / hệ thống / xuyên sách.

**Bước 0 và Bước 5 của nền giữ nguyên:** vẫn duyệt ý tưởng trước khi viết; "truyện rác drama" vẫn lưu vào `drama/`, "truyện rác trinh thám" vào `trinh-tham/` — tiền đề KHÔNG tạo thư mục riêng. Trong danh sách ý tưởng Bước 0, nêu rõ **ai là nhân vật não tàn** và **cú lố bịch trung tâm** của mỗi ý.

## Vì sao dòng này gây nghiện (dù ai cũng chê)

Nguồn khoái cảm KHÔNG phải sự đồng cảm — mà là **ức chế bị nén rồi được xả**. Bốn dòng chồng lên:
1. **Ức chế = cortisol có chủ đích.** Nhân vật ngu làm điều sai rành rành trước mắt người nghe → người nghe *muốn hét vào tai nhân vật*. Cảm giác bất lực đó chính là thứ giữ họ lại: **họ không nghe để thưởng thức, họ nghe để chờ nhân vật trả giá.**
2. **Ưu thế nhận thức (superiority).** Người nghe luôn thông minh hơn nhân vật — một liều tự tôn miễn phí, tốn không đồng nào công sức. "Tháo não" nghĩa là *không phải suy nghĩ*, và đó là tính năng, không phải lỗi.
3. **Phẫn nộ đạo đức (moral outrage).** Cái ngu luôn đi kèm bất công: kẻ tử tế bị chà đạp vì sự ngu của người khác. Phẫn nộ là cảm xúc lan truyền mạnh nhất trên mạng — nó đẻ ra bình luận, chia sẻ, nghe lại.
4. **Zeigarnik dạng thô:** vòng lặp mở không phải "ai là hung thủ" mà **"bao giờ nó mới sáng mắt?"** — câu hỏi ngứa ngáy đến mức người nghe không tắt được.

> **Con dao hai lưỡi:** ức chế KHÔNG có lối thoát = người nghe bỏ đi trong tức giận, không quay lại. Ranh giới giữa "gây nghiện" và "rác thật" nằm ở **hợp đồng ngầm: mọi ức chế đều được xả, và xả xứng đáng.** Toàn bộ skill xoay quanh việc bơm ức chế mà vẫn giữ lời hứa đó.

## Hợp đồng ngầm với người nghe — LUẬT SỐ MỘT

Ngay từ hook, người nghe phải **tin rằng cú trả giá sẽ đến**. Không phải biết *khi nào* hay *như thế nào* — chỉ cần chắc chắn *sẽ có*. Cách gieo lời hứa đó:
- **Mở bằng flash-forward hậu quả:** câu đầu tiên là mảnh của cảnh trả giá ("Ngày mẹ chồng tôi quỳ xuống trước cửa nhà tôi, trời đang mưa."), rồi mới quay về kể từ đầu. Người nghe chịu đựng được 20 phút ngu vì đã thấy trước đích đến.
- **Hoặc mở bằng tuyên bố lạnh của người kể:** "Chồng tôi tin em gái tôi hơn tin tôi. Tôi để anh ta tin — đến tận ngày anh ta không còn gì để tin nữa."
- **Đồng hồ đếm ngược:** cài một mốc cụ thể (ngày ký giấy tờ, ngày xét nghiệm về, ngày đám cưới) để ức chế có đường ray, không lửng lơ.

> Đây là **ràng buộc CỨNG** của dòng này, không phải lựa chọn thẩm mỹ: ràng buộc mở đầu của tiền đề THẮNG bảng chọn theo thể loại trong `audio-story-engagement/references/mo-dau.md` (xem mục 4–5 file đó). Thiếu lời hứa này, ức chế thành rage bait thuần.

**Phép thử:** ở bất kỳ phút nào, hỏi *"người nghe có còn tin cú xả sẽ đến không?"* — nếu bắt đầu nghi ngờ, cài ngay một **micro-payoff** (mục Nhịp).

## Ba vai bắt buộc

- **KẺ NÃO TÀN** (chính hoặc phụ). Ngu một cách *nhất quán*, không ngu ngẫu nhiên. Xem "Luật của cái ngu".
- **KẺ LỢI DỤNG CÁI NGU.** Nhân vật tỉnh táo, ác, biết chính xác phải bấm nút nào. Đây là kẻ **biến sự ngu thành bất công** — không có nó, truyện chỉ là một người ngốc nghếch vô hại, không ai ức chế. *Đây là nhân vật quan trọng nhất của dòng truyện rác.*
- **NGƯỜI TỈNH TÁO BỊ VÙI** — thường là người kể ngôi 1, đại diện của người nghe. Nói đúng, không ai tin. Sự bất lực của họ = sự bất lực của người nghe. **Vũ khí chính của dòng này.**

> Biến thể: nếu **chính người kể là kẻ não tàn** (kiểu "tôi đã ngu như thế nào"), giọng kể phải là **giọng hối hận nhìn lại** ("Lúc đó tôi tin lời cô ta. Tôi của bây giờ muốn tát tôi của lúc đó") — vừa cho phép ngu tối đa, vừa giữ được lời hứa trả giá ngay trong giọng kể. Đây là biến thể an toàn nhất.

## Luật của cái ngu — QUY TẮC VÀNG

Ngu bừa = người nghe không tin và tắt. Ngu có luật = người nghe cay cú và ở lại. Năm luật:

1. **Ngu phải có ĐỘNG CƠ, không phải thiếu IQ.** Không ai tin một người trưởng thành ngu vô cớ. Nhưng ai cũng tin một người bị **thiên kiến làm mù**: sĩ diện, ám ảnh hiếu thảo, sợ cô đơn, tham lam, tự tin thái quá, yêu mù quáng, định kiến "máu mủ thì không hại nhau". Đó là *lý do* để nhân vật bác bỏ bằng chứng ngay trước mũi. **Cái ngu là hệ quả của một nhu cầu tâm lý, không phải của một chỉ số.**
2. **Ngu NHẤT QUÁN một hướng.** Chọn MỘT thiên kiến và ép nhân vật ngu đúng theo trục đó suốt truyện. Người tin em gái mù quáng thì không được đột nhiên sáng suốt ở chuyện khác cùng loại — nhưng vẫn có thể sắc sảo ở việc không dính tới thiên kiến (chuyên môn, công việc). **Đây là thứ tách "nhân vật não tàn" khỏi "lỗi viết".**
3. **Ngu LEO THANG.** Cú ngu đầu nhỏ, có thể thông cảm. Mỗi lần bác bỏ bằng chứng, nhân vật phải **lún sâu hơn để tự bào chữa cho lần trước** — leo thang cam kết. Người nghe thấy vực sâu dần, không hét được. Đây là cách chuyển ức chế thành cấp số nhân.
4. **Ngu phải TỐN GIÁ của người khác.** Ngu tự hại mình = hài. Ngu làm người vô tội mất mát = ức chế. Muốn ức chế mạnh, cái giá phải rơi lên người kể hoặc một người đáng thương (đứa con, người mẹ già, người bạn trung thành).
5. **Bằng chứng luôn nằm ngay trước mặt.** Người nghe phải thấy rõ mồn một sự thật trong khi nhân vật nhìn thẳng vào nó và giải thích trẹo đi. Đây là *dramatic irony* (Kỹ thuật 6 nền) đẩy tới cực hạn — và là động cơ ức chế chính. Không có bằng chứng lộ thiên → không có ức chế, chỉ có hiểu lầm nhạt.

> **Phép thử:** với mỗi cú ngu, hỏi *"nhân vật này sẽ TỰ giải thích hành động của mình thế nào?"* — nếu không có câu trả lời nghe lọt tai (dù ngụy biện), đó là lỗi viết, không phải nhân vật não tàn. Viết lại cho tới khi lời ngụy biện tự nó đứng được.

## Núm vặn LỐ BỊCH — vặn tới đâu

Tình tiết lố bịch là đặc sản, không phải tai nạn. Nhưng lố bịch có luật riêng: **phi lý ở HÀNH VI, không phi lý ở THẾ GIỚI.** Thế giới vẫn vận hành bình thường (bệnh viện vẫn xét nghiệm ra kết quả đúng, tiền vẫn hết khi tiêu, camera vẫn ghi hình) — chỉ có *lựa chọn của nhân vật* là điên rồ. Nếu thế giới cũng tùy tiện, hậu quả mất trọng lượng và người nghe thôi cay cú.

- **Đúng liều:** mẹ chồng đuổi con dâu ra khỏi nhà giữa đêm mưa để nhường phòng cho con gái cưng về chơi một hôm — điên, nhưng nằm trong logic sĩ diện của bà ta.
- **Quá liều (hỏng):** mẹ chồng đốt nhà rồi cả xóm vỗ tay — thế giới đã hùa theo, người nghe thoát ly, hết ức chế.
- **Leo thang lố bịch:** mỗi lần vượt trần trước một nấc, và **luôn kèm phản ứng THẬT từ thế giới** (hàng xóm xì xào, công an mời lên, sếp gọi điện). Chính phản ứng thật giữ neo cho cú lố bịch.
- **Cú lố bịch trung tâm:** mỗi truyện nên có MỘT hành vi lố bịch mang tính biểu tượng để làm tiêu đề và hook (thứ khiến người ta phải kể lại cho bạn bè). Đừng rải mười cú ngang nhau.

## Vòng lặp mở đặc thù

1. **"Bao giờ nó mới sáng mắt?"** — vòng lớn, thay thế Câu Hỏi Trung Tâm kiểu bí ẩn. Mỗi lần suýt sáng rồi lại mù = một vòng nhỏ đóng-mở.
2. **"Nó sẽ trả giá bằng gì?"** — người nghe biết *sẽ có* trả giá, nhưng không biết hình dạng. Đây mới là bí ẩn thật của truyện rác.
3. **"Người tỉnh táo chịu được đến bao giờ?"** — điểm giới hạn của người kể. Khi họ gãy, truyện chuyển hồi.
4. **"Kẻ lợi dụng có bị lộ không?"** — vòng trinh thám thu nhỏ; cho người nghe hy vọng rồi cắt.
5. **"Lần này có ai tin không?"** — mỗi lần người kể đưa bằng chứng là một vòng cực ngắn, và câu trả lời "không" là cú ức chế rẻ nhất, mạnh nhất.

## Nhịp: nén dài, xả đúng — và micro-payoff

Truyện rác **nén lâu hơn** mọi dòng khác, nên rủi ro mất người nghe cũng cao nhất. Cân bằng:
- **Micro-payoff mỗi 3–5 phút.** Một liều nhỏ để giữ hợp đồng: người kể đáp trả một câu chí mạng; kẻ ác lỡ lời trước mặt người thứ ba; nhân vật ngu bị quê nhẹ; một người ngoài cuộc nói đúng thay người nghe ("Chị điên à?"). Không giải quyết gì, chỉ **chứng minh vũ trụ truyện vẫn còn công lý**.
- **Nhân vật đồng minh của người nghe:** một vai phụ nói thẳng điều người nghe đang nghĩ. Đây là van xả áp rẻ nhất và hiệu quả nhất của dòng này.
- **Đại xả (payoff lớn) phải TƯƠNG XỨNG với tổng ức chế đã nén.** Nén 20 phút mà chỉ được một lời xin lỗi = lừa người nghe. Cú xả phải: công khai (có khán giả), không thể chối (bằng chứng lộ diện), và **để kẻ ngu tự tay phá mình** bằng chính thiên kiến đã ngu suốt truyện — đó là kết thỏa mãn nhất, vì nó biến cái ngu thành lưỡi dao quay ngược.
- **Sau đại xả, cắt nhanh.** Kéo dài cảnh hả hê làm nó nhạt. Giữ đúng luật nền: không quá 2 nhịp thắng/thua liên tiếp.

## Quan hệ với các luật nền — cái gì được nới, cái gì KHÔNG

Dòng này cố tình đi ngược vài nguyên tắc viết chuẩn. Ghi rõ để không nới nhầm:

| Luật nền | Trạng thái trong truyện rác |
|---|---|
| "Nhân vật phải chủ động" | **NỚI** cho kẻ não tàn (bị thiên kiến dắt mũi) — nhưng **người kể vẫn phải chủ động ra quyết định** ở bước ngoặt, nếu không truyện chết. |
| "Phản diện phải có logic riêng" | **GIỮ, đổi hình:** kẻ lợi dụng có logic sắc; kẻ não tàn có *ngụy biện* nhất quán. Không ai được ác/ngu vô cớ. |
| "Twist bất ngờ nhưng tất yếu" | **NỚI biên độ**: tình tiết được phép lố, nhưng hậu quả vẫn phải theo nhân quả. |
| Văn phong dứt khoát, không sến | **GIỮ CỨNG.** Ngu là ở nhân vật, không phải ở câu văn. |
| Xưng hô ngôi 1, người thân gọi bằng quan hệ | **GIỮ CỨNG.** |
| An toàn từ vựng kiểm duyệt | **GIỮ CỨNG** — dòng này dễ dính "rage bait" nên càng phải sạch từ. |
| Mirror neurons — tả, không kể cảm xúc | **GIỮ CỨNG.** Ức chế phải đến từ *sự việc*, không từ việc người kể than "tôi ức chế quá". |

## Ma trận kết hợp 5 thể loại

- **× DRAMA (combo phổ biến nhất):** chồng ngu tin em gái/mẹ chồng/nhân tình hơn tin vợ; mẹ chồng thiên vị đến mức phi lý; anh chị em ruột hút máu nhân danh máu mủ. Thiên kiến trục: hiếu thảo mù quáng / sĩ diện. Cú xả kinh điển: sự thật nổ giữa đám đông (giỗ, cưới, họp họ) và kẻ ngu **tự mời cả họ tới xem** mình bị lột mặt.
- **× TRINH THÁM:** nhân vật ngu là người **phá hoại cuộc điều tra** — xóa bằng chứng vì bênh người thân, khai bậy vì sĩ diện. Người nghe biết hung thủ từ sớm, ức chế nằm ở chỗ "sao không ai chịu nhìn?". Twist mạnh: chính cái ngu đó là thứ hung thủ tính toán từ đầu.
- **× KINH DỊ:** kho báu của dòng này — nhân vật mở cánh cửa không được mở, gọi tên không được gọi, ở lại căn nhà mọi người bảo đi. Thiên kiến trục: duy lý cực đoan ("làm gì có ma") hoặc tham (giá thuê rẻ). **Lưu ý:** phải cho nhân vật lý do đủ nghe lọt tai để ở lại (hết tiền, mất việc, con nhỏ), nếu không nỗi sợ tan thành trò cười.
- **× TÌNH CẢM:** yêu mù quáng, nuôi kẻ phản bội bằng chính tay mình, "anh ấy chỉ đang áp lực thôi". Ức chế = nhìn người tử tế bị bào mòn. Cú xả thỏa mãn nhất KHÔNG phải báo thù mà là **người kể dứt áo lạnh lùng**, còn kẻ ngu quay lại cầu xin khi đã muộn.
- **× HÀI HƯỚC:** ở đây cái ngu chuyển từ ức chế sang **cười** — hạ cái giá xuống (không ai mất mát thật), tăng liều lố bịch, để kẻ ngu tự lãnh hậu quả tức thì. Đây là biến thể duy nhất được phép ngu tự hại mà vẫn hay.
- **× TIỀN ĐỀ BIẾT TRƯỚC (chồng 4 lớp):** cực hợp — trùng sinh mà **người khác vẫn ngu y hệt kiếp trước**, còn người kể giờ đã tỉnh. Ức chế đảo chiều thành khoái cảm: người nghe biết trước cái ngu sẽ dẫn tới đâu và chờ xem. Nhớ giữ Quy tắc vàng của skill kia (lợi thế biết trước phải bị phá vỡ).

## Bẫy cần tránh

| Bẫy | Cách tránh |
|-----|-----------|
| Ức chế không có lối xả (rage bait thuần) | Gieo hợp đồng ngầm ở hook; micro-payoff mỗi 3–5 phút; đại xả tương xứng |
| Ngu ngẫu nhiên, mỗi lúc một kiểu | Chọn MỘT thiên kiến trục, ép nhất quán cả truyện |
| Ngu vô cớ, không ngụy biện nổi | Áp phép thử "nhân vật tự giải thích thế nào?" |
| Thế giới cũng phi lý (ai cũng hùa theo kẻ ngu) | Lố bịch ở hành vi, KHÔNG ở thế giới; luôn có phản ứng thật từ ngoài |
| Người kể chỉ biết chịu đựng, thụ động cả truyện | Người kể phải ra ≥2 quyết định chủ động thay đổi cục diện |
| Cú xả rẻ (một lời xin lỗi, một cái tát) | Xả phải công khai + không thể chối + do chính thiên kiến của kẻ ngu gây ra |
| Nhân vật tốt hoàn hảo, chỉ để bị hành | Cho người kể khuyết điểm thật (nhẫn nhịn quá lâu vì sợ mất gia đình) |
| Kéo dài cảnh hả hê | Xả xong cắt nhanh, để dư âm |
| Văn phong cũng "rác" theo | Câu vẫn phải dứt khoát, chi tiết cụ thể — giữ nguyên luật nền |
| Lố bịch dàn trải, không đọng | Một cú lố bịch TRUNG TÂM làm tiêu đề + hook |

## Keyword & mẫu tiêu đề (cho Bước 0 & hook)

**Keyword nhận diện:** truyện rác, não tàn, não phẳng, không có não, óc chó, tháo não, ức chế, rage bait, nhân vật ngu, ngu không tưởng, mù quáng, sáng mắt, trả giá, hiếu thảo mù quáng, bênh con mù quáng, tin người ngoài hơn người nhà, lố bịch, phi lý.

Mẫu tiêu đề: *"Chồng tôi tin em gái tôi hơn tin kết quả xét nghiệm"* · *"Mẹ chồng đuổi tôi ra đường lúc nửa đêm để dành phòng cho con gái cưng về chơi một hôm"* · *"Cả nhà bảo tôi vu oan. Ba tháng sau, họ mang cái đơn đó tới xin tôi ký"* · *"Tôi nói sự thật 27 lần. Không ai tin. Lần thứ 28 tôi im lặng — và để họ tự tìm ra."*

## Checklist bổ sung tiền đề (sau checklist nền + checklist genre)

- [ ] Đã áp đủ các lớp (nền + genre đúng thể loại + tiền đề này, và `biet-truoc` nếu prompt có)?
- [ ] **Hợp đồng ngầm** được gieo trong hook — người nghe tin chắc cú trả giá sẽ đến?
- [ ] Kẻ não tàn có MỘT thiên kiến trục rõ ràng, ngu nhất quán theo trục đó?
- [ ] Mỗi cú ngu đều có lời ngụy biện tự đứng được (qua phép thử "nhân vật tự giải thích thế nào")?
- [ ] Cái ngu LEO THANG (mỗi lần lún sâu hơn để bào chữa cho lần trước)?
- [ ] Bằng chứng luôn lộ thiên trước mắt người nghe (dramatic irony cực hạn)?
- [ ] Có đủ BA vai: kẻ não tàn, kẻ lợi dụng cái ngu, người tỉnh táo bị vùi?
- [ ] Cái giá của sự ngu rơi lên người vô tội (không phải chỉ kẻ ngu tự hại — trừ biến thể hài)?
- [ ] Lố bịch ở HÀNH VI, thế giới vẫn phản ứng thật? Có MỘT cú lố bịch trung tâm?
- [ ] Có micro-payoff mỗi 3–5 phút (đồng minh nói thay người nghe, kẻ ác lỡ lời...)?
- [ ] Đại xả tương xứng tổng ức chế: công khai, không thể chối, do chính thiên kiến kẻ ngu gây ra? Cắt nhanh sau đó?
- [ ] Người kể vẫn CHỦ ĐỘNG ≥2 quyết định bước ngoặt (không thụ động cả truyện)?
- [ ] Văn phong / xưng hô / an toàn từ vựng vẫn giữ CỨNG theo nền (không nới)?
- [ ] Đã lưu file vào đúng thư mục THỂ LOẠI (không tạo thư mục riêng cho tiền đề)?
