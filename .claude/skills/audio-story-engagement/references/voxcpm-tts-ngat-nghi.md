# VoxCPM/TTS Pause And Dialogue Readiness

Use this reference when drafting or polishing Vietnamese audio stories that will be rendered through VoxCPM or another TTS engine. The goal is not theatrical markup; the goal is plain Vietnamese prose whose punctuation, paragraphing, and dialogue turns give the voice engine enough structure to breathe naturally.

## Baseline Contract

- Write the saved story as pure story text. Do not insert SSML, `[pause]`, `[breath]`, `[whisper]`, SFX, BGM, chapter labels, or production notes unless the user explicitly requests production markup and the target engine supports it.
- Treat punctuation as a prosody map, not decoration. TTS systems commonly use punctuation to infer pauses and intonation; unsupported marks or visual-only formatting can be ignored or spoken wrongly.
- For this repo's VoxCPM path, plain Vietnamese matters. VoxCPM has no Vietnamese pronunciation lexicon in the local pipeline, so raw digits, `/`, `:`, bare Latin letters, acronyms, and unusual symbols can cause mispronunciation, compressed timing, or swallowed syllables. Write consequential tokens the way they should be heard.
- The renderer/stitcher distinguishes sentence endings, expressive endings, paragraph breaks, and dialogue-like chunks. Give it clean paragraph breaks and closed dialogue turns instead of dense visual prose.

## Pause Hierarchy For Vietnamese Audio Prose

- **Comma `,`**: short breath. Use for lists, fronted adverbial phrases, inserted clauses, and a soft hinge between related clauses. If a sentence needs more than two or three major comma breaths, consider splitting it.
- **Period `.`**: complete thought and firmer stop. Use it when the listener needs to process, when an emotional beat lands, or when a short spoken line should not rush into the next idea.
- **Question mark `?`**: real question and question intonation. Do not write a question as a period just because the speaker is calm.
- **Exclamation mark `!`**: strong energy. Use sparingly; repeated exclamations flatten intensity and can make TTS overperform.
- **Ellipsis `...` or `…`**: trailing thought, hesitation, or unfinished feeling. Use three dots or one ellipsis only. Do not use ellipses as a default suspense button.
- **Colon `:`**: introduce a direct quote, list, or explanation. Avoid raw time formats such as `19:45`; write `bảy giờ bốn mươi lăm tối` or `mười chín giờ bốn mươi lăm` according to context.
- **Semicolon `;`**: valid on the page but subtle in audio. In fiction narration, prefer a period or comma unless the balanced relationship is truly useful.
- **Dash `-`, `–`, `—`**: do not rely on dashes for pause control in VoxCPM-bound pure story. The local normalizer may convert set-off dashes to comma-like pauses and strip line-leading dialogue dashes. Prefer quotation marks, sentence breaks, paragraph breaks, or an action beat.

## Smart Dialogue Pause Mechanism

Before keeping a direct exchange, decide what each turn does: pressure, refuse, confess, hide, probe, bargain, soothe, threaten, or withdraw. Then shape the line for the ear.

1. Give each speaker turn its own listening unit. In multi-speaker scenes, use a new paragraph for every speaker turn.
2. Keep one quoted turn short enough to say in one breath unless the character is intentionally rambling under pressure. Around 18-25 Vietnamese words is comfortable; 36+ words deserves a reread and likely a split.
3. Use sentence breaks inside dialogue when emotion or logic changes: `"Không. Em nghe anh nói hết."` carries a stronger stop than `"Không, em nghe anh nói hết."`
4. Use an action beat as a natural pause only when it changes meaning, identifies the speaker, or reveals subtext. Do not attach decorative gestures to every line.
5. Do not place rapid-fire quoted lines from different speakers in one paragraph. TTS may read them as one voice stream.
6. For interruption, do not depend on a dash alone. Use an unfinished line plus action or response: `"Em chưa từng..."` Cánh cửa sau lưng tôi mở ra. Or let the next speaker cut in with a new paragraph.
7. Let silence have content. Instead of `[pause]`, use a paragraph break plus something the listener can feel: a cup set down, a name not answered, a door left open.
8. Re-anchor speaker identity more often than page fiction when three or more people are present. A name, relationship noun, or meaningful action beat can prevent the listener from losing the turn order.

## Consecutive Sentences That Open Alike

Watch for this while drafting, not only during final polish: two or more sentences in a row that begin with the same words. On the page this can be anaphora, but a chunk-based renderer resets prosody at the start of every chunk, so an identical opening lands after a fresh reset each time and a listener hears the synthesizer repeating itself rather than a rhetorical device. This has produced a real false bug report in production: a listener flagged a rendered chunk as broken, and measuring the audio showed the render matched the script exactly. Re-rendering could not have fixed it, because nothing was wrong with the audio.

This check is chunk-size-independent. A render pipeline never reorders sentences, so any two sentences that end up spoken back to back are exactly two adjacent sentences in the manuscript, regardless of which chunk file each one lands in. Judging repetition at the sentence level while drafting is sufficient; there is no separate boundary case to watch for.

Decide in the moment whether the repetition is doing work:

- **Building toward a payoff** (a refusal, a reveal, an escalation): keep the anchor phrase that carries the device, but change the **first word** of each sentence — drop the subject, front an adverb, invert the clause. The variation must sit at the sentence opening, where the chunk reset puts the stress.
- **Accidental**: rewrite the opening outright. There is nothing to preserve.

**Inserting a short unstressed word after the same first word is not enough.** This was tried in production: `Tôi muốn nói / Tôi rất muốn nói / Tôi còn muốn nói`. Two independent renders were measured word-perfect (CTC likelihood ratio over 25 nats in favor of the scripted word, Whisper CER 0.0), and the listener still reported the audio as broken — hearing "tôi tôi muốn nói". The inserted word (`rất`, `còn`) is a short unstressed function word wedged between a chunk-initial stressed `Tôi` and the anchor; an ear already primed by the previous sentences swallows it. The variation must be the first word the listener hears after the prosody reset.

Quick repair — same anchor kept, sentence-initial word varied:

Risky (even the second version fails aurally, despite differing at word two):

> Tôi muốn nói, người báo cho ông nội không phải tôi.
>
> Tôi rất muốn nói, Hạ Uyển không ra nước ngoài vì bị ép, cô ấy đi vì đã nhận tiền từ một người đàn ông khác.
>
> Tôi còn muốn nói, ngày anh uống say đến mức chảy máu dạ dày ở lối thoát hiểm khách sạn, người gọi xe cấp cứu là tôi, người ở ngoài phòng cấp cứu cả đêm cũng là tôi.

Audio-ready (anchor `muốn nói` kept in all three; the openings are `Tôi` / `Muốn` / `Càng` — three different onsets and vowels, so each sentence announces itself as new while the device still escalates):

> Tôi muốn nói, người báo cho ông nội không phải tôi.
>
> Muốn nói cả chuyện Hạ Uyển không ra nước ngoài vì bị ép, cô ấy đi vì đã nhận tiền từ một người đàn ông khác.
>
> Càng muốn nói, ngày anh uống say đến mức chảy máu dạ dày ở lối thoát hiểm khách sạn, người gọi xe cấp cứu là tôi, người ở ngoài phòng cấp cứu cả đêm cũng là tôi.

When repetition is itself the content of a diary, list, or count, give each entry an audible label such as a date, ordinal, location, or speaker before the repeated anchor. Generate the entries from the manuscript; do not copy emotional diary content from a skill example.

## TTS-Friendly Tokens

Write for the intended spoken form when a token matters:

- Dates: `ngày mười hai tháng năm`, not `12/5`, unless the production normalizer has been tested for that exact pattern.
- Times: `bảy giờ ba mươi tối`, not `7h30` or `19:30`.
- Money and units: `hai trăm năm mươi nghìn đồng`, `một mét sáu mươi lăm`.
- Percentages and ratios: `hai mươi phần trăm`, `một phần ba`.
- Phone/account/legal numbers: spell digits or summarize by function if the exact sequence is not story-critical.
- Acronyms: expand on first use when possible: `xét nghiệm ADN`, `căn cước công dân`; if an acronym must remain, add a pronunciation decision outside the pure story when preparing production.
- Foreign names: avoid clusters of similar-sounding names. Repeat relation/title at scene entry if the name is unfamiliar.

## English, Teencode, And Trend Tokens

Modern-set stories often contain English loanwords, workplace/platform vocabulary, or youth slang: `inbox`, `deal`, `crush`, `flex`, `red flag`, `livestream`, `OK`, `email`. On the page these read fine. Through VoxCPM they are bare Latin strings with no Vietnamese pronunciation entry, so they are commonly read letter by letter, given an English-looking guess, compressed, or dropped entirely — and the surrounding chunk timing shifts with them.

Every English-origin, acronym, or stylized-teencode token that survives into the saved story file must already be written the way it should be heard. Choose one repair per token:

1. **Vietnamese phonetic respelling** — when Vietnamese speakers already say it that way and the respelling stays recognizable by ear.

   | Written token | Spoken form in the story file |
   |---|---|
   | `inbox` | `in bốc` |
   | `livestream` | `lai sờ trim` |
   | `comment` | `còm men` |
   | `Facebook` | `phây búc` |
   | `TikTok` | `tích tóc` |
   | `email` | `i meo` |
   | `OK` | `ô kê` |
   | `app` | `áp` |
   | `video` | `vi đê ô` |

2. **A plain Vietnamese equivalent** — when the respelling would look strange, unreadable, or ambiguous: `inbox` -> `nhắn tin riêng`, `deal` -> `giá hời`, `review` -> `đánh giá`, `link` -> `đường dẫn`, `check` -> `kiểm tra`.

3. **Keep the original spelling only** when the term is a settled loanword already rendered correctly in a verified test, and record it outside the story file as a render concern.

Rules:

- decide the spoken form before rendering; never leave the choice to the renderer;
- keep one form per term across the whole story so the voice stays consistent;
- do not respell a token into something a reader cannot recognize — if the phonetic form is unreadable, use option 2;
- when a joke depends on the original sound (`gét gô` from `let's go`, `sít rịt` from `secret`), the phonetic Vietnamese spelling **is** the correct written form; add a plain anchor line nearby if the meaning could be missed by ear;
- strip emoji, hashtags, `@` handles, and platform UI text from spoken prose; describe them instead;
- avoid digit substitutions inside words; the engine reads the digit literally.

## Quick Repairs

Page-readable but rushed:

> "Khoan em chưa nói xong anh đừng ký tờ đó."

Audio-ready:

> "Khoan. Em chưa nói xong."
>
> Tôi đặt tay lên mép tờ giấy. "Anh đừng ký vội."

Two speakers in one stream:

> "Ra ngoài." "Không." "Tôi bảo cô ra ngoài."

Audio-ready:

> "Ra ngoài."
>
> "Không."
>
> Anh hạ giọng. "Tôi bảo cô ra ngoài."

Visual token that can break rhythm:

> Tin nhắn gửi lúc 19:45, kèm mã hồ sơ ADN số 03/2024.

Audio-ready:

> Tin nhắn gửi lúc bảy giờ bốn mươi lăm tối, kèm mã hồ sơ xét nghiệm ADN đầu tháng tư năm đó.

## Final Listening Checklist

- Are terminal punctuation marks present and intentional?
- Can every sentence be understood in one hearing without scanning backward?
- Do paragraph breaks mark thought turns, speaker turns, scene shifts, or emotional resets?
- Can every direct line be assigned to a speaker and spoken in a believable breath? Across the exchange, is there enough value or pressure without forcing each line into a tactic?
- Are multi-person scenes clear if quotation marks disappear from the listener's mind?
- Are numbers, dates, times, acronyms, symbols, and foreign names written or prepared for the way they should be spoken?
- Are ellipses, exclamation marks, colons, semicolons, and dashes used for real function rather than visual flavor?
- Is there at least one dialogue-heavy sample worth rendering/listening before committing a long VoxCPM job?
- Do two or more consecutive sentences open with the same words? If deliberate, does each reach the shared anchor a different way; if accidental, has the opening been rewritten?
