---
name: product-review-youth-trend-language
description: |
  MANUAL-ONLY. Live-researched trend-language and high-humor scripting skill for Vietnamese SHORT-FORM PRODUCT content: product reviews, kịch bản giới thiệu/quảng cáo sản phẩm, TikTok/Reels/Shorts scripts, social-commerce videos, livestream cutdowns, UGC-style reviews, and creator voice-over scripts.
  Use ONLY when the user explicitly asks for trend/teencode/Gen Z language in a PRODUCT or commercial script, for example "viết kịch bản review sản phẩm có teencode", "kịch bản giới thiệu sản phẩm bắt trend", "content TikTok bán hàng dùng từ hot", "làm cho Gen Z hơn", "kịch bản ngắn quảng cáo có từ xu hướng", or an equivalent request. Never self-trigger.
  If the request is a STORY or fiction script, use `audio-story-youth-trend-language` instead.
  This skill MUST research current slang, meme structures, platform language, and niche trends before writing. It permits higher trend density than audio fiction but requires authentic product evidence, verified claims, natural creator voice, platform fit, TTS/performance clarity, sponsorship transparency, and strict anti-spam controls.
---

# Product Review Youth Trend Language

Use this skill to create Vietnamese product-review and product-introduction scripts that feel current, funny, energetic, culturally fluent, and native to short-form social platforms — **when the user has explicitly asked for that trend-language treatment**.

Unlike audio fiction, product review may use trend language more frequently because the format is short, the audience expects entertainment, the creator voice is foregrounded, rapid pattern changes hold attention, and comment/meme culture is part of the viewing experience.

However:

> More trend language does not mean more random slang.

The goal is:

> Build a high-energy review where trend phrasing amplifies a real observation, visible demonstration, specific benefit, honest limitation, or comic creator reaction.

The product must remain understandable after every trend phrase is removed.

## 0. Activation Rules (Read First)

This skill is **manual-only**.

Activate when the request contains an explicit trend-language intent word — `teencode`, `tiếng lóng`, `slang`, `từ trend`, `bắt trend`, `hot trend`, `từ xu hướng`, `Gen Z`, `genz`, `meme`, `nói lái`, `viral`, `viral hook`, `nói kiểu giới trẻ` — applied to a product or commercial target: `review sản phẩm`, `giới thiệu sản phẩm`, `quảng cáo`, `bán hàng`, `content TikTok`, `Reels`, `Shorts`, `livestream`, `affiliate`, `UGC`, `kịch bản ngắn` for a product, `chốt đơn`.

Do **not** activate for a fiction/story request (route to `audio-story-youth-trend-language`), for plain product copy with no trend intent, or automatically after any other task.

If the target is ambiguous (for example `kịch bản ngắn` with no subject), ask one short routing question before doing research.

## 1. Coordination Contract

Use with:

- product-fact research (whatever source the user provides);
- the platform and audience brief;
- brand voice;
- ad/commercial-content policy;
- safety and prohibited-claims rules;
- TTS or creator-performance normalization;
- final factual verification.

**In this repo:** if the finished script will be rendered to audio, the render path is `story-to-audio` (Kaggle VoxCPM). Apply section 20 before handing the script over — spoken-token normalization is this skill's responsibility for product scripts, because `audio-story-final-polish` is a fiction skill and must not be used to edit a commercial script.

This skill controls: current slang and meme language; humorous review phrasing; playful Vietnamese-English; `nói lái`; current hook formats; trend-shaped transitions; reaction language; running gags; playful CTA language; trend density; freshness and expiry.

This skill does **not** control or authorize: product performance claims; medical claims; pricing accuracy; warranty; ingredients; technical specifications; safety claims; legal compliance; sponsorship disclosure. Those require separate verification.

## 2. Non-Negotiable Truthfulness

Trend language must never disguise weak evidence.

Do not fabricate: personal use; duration of testing; before-and-after results; customer reviews; laboratory results; certifications; scarcity; discounts; stock levels; delivery times; warranty; competitor comparisons; income or health outcomes.

Do not write:

- `mình dùng 30 ngày` unless verified;
- `100% hết mụn` without valid evidence and permission;
- `ai dùng cũng hợp`;
- `cháy hàng toàn quốc` without current data;
- `rẻ nhất thị trường` without a current comparison;
- `bác sĩ khuyên dùng` without a verified endorsement.

Humor cannot turn uncertainty into fact.

For sponsored, gifted, or affiliate content: preserve required disclosure, do not hide the commercial relationship inside a joke, and keep the piece recognizable as commercial content.

## 3. Mandatory Live Research

Before using current slang, meme formats, viral audio wording, comment templates, or trend hooks, browse the live web with `WebSearch`/`WebFetch`, or `agent-browser read <url>` for a specific page.

Research separately for:

1. general Vietnamese youth language;
2. the product category;
3. the target platform;
4. the intended audience;
5. the current week/month;
6. controversy and expiry risk.

User-provided examples are candidates, not approvals. A term may be popular generally but wrong for skincare, electronics, food, home appliances, fashion, parenting, finance, health, luxury, or gaming.

If live browsing is unavailable, say so, drop fast memes, and write with durable conversational humor instead.

## 4. Research Window

```text
Viral hook / meme syntax:      prefer the last 7-30 days.
Current slang:                 prefer the last 30-90 days.
Product-category trend:        prefer the last 14-90 days.
Durable platform language:     confirm active use within the last 6-12 months.
Legacy meme used for nostalgia: verify the audience still recognizes it.
```

Recheck fast trends immediately before publication when possible. Do not rely on a page that merely refreshes its date while describing an old trend.

## 5. Source Hierarchy

**Strong:** current TikTok Creative Center; current creator videos and comments; current Reels/Shorts/Threads/Facebook posts; the original viral source; social-listening reports; current niche communities; current product-review creators; current platform business guidance; recent campaign analysis.

**Supporting:** recent Vietnamese journalism; youth publications; marketing-industry publications; trend explainers with origin and real examples.

**Weak:** undated slang lists; copied SEO glossaries; product pages pretending a term is trending; pages with no real usage; AI-generated trend lists; one creator's isolated phrase.

Use at least two independent signals for a fast trend.

## 6. Research Protocol

### Step 1 — Lock the brief

```text
Product:
Category:
Verified facts:
Target buyer:
Platform:
Video length:
Creator persona:
Tone:
Humor level:
Trend density:
Commercial relationship:
CTA:
Forbidden claims:
Output: text script only, or script + audio render?
```

### Step 2 — Search current language

```text
Vietnamese TikTok slang <current year>
từ lóng Gen Z Việt <current month>
<category> + TikTok trend Việt Nam
<category> + review phrases
"<candidate term>" nghĩa là gì / nguồn gốc / tranh cãi / hết trend
```

### Step 3 — Observe real syntax

Collect more than words: sentence openings, reaction patterns, pacing, ironic reversals, comment-style phrasing, current comparison structures, self-roast forms, CTA language, transitions, and how creators introduce evidence.

### Step 4 — Build a trend bank

```text
Trend unit:
Type:
Meaning:
Status:
Evidence date:
Platform:
Audience:
Niche fit:
Humor function:
Product bridge:
Unsafe use:
TTS spoken form:
Expiry:
```

### Step 5 — Remove forced candidates

Delete any trend with no natural bridge to a problem, demo, sensory reaction, feature, use scenario, limitation, price-value judgment, or CTA.

## 7. Trend Unit Types

A `trend unit` is broader than a slang word.

- **Current slang** — for example `sít rịt`, `flex`, `red flag`, `out meta`, `ngoan xinh yêu`, or any currently verified term.
- **Durable youth vocabulary** — `crush`, `toxic`, `chữa lành`, `tiểu tam`, `trà xanh`, `vibe`, `deal`, `visual`. Verify current tone and saturation.
- **Vietnamese-English play** — Vietnamese phonetic English; English noun with Vietnamese syntax; deliberately formal English in an ordinary situation; ironic workplace language; creator-community jargon.
- **`Nói lái` and phonetic wordplay** — `rồi em nhớ`, `nhíu em nhớ`, `gét gô`, and similar current wordplay. Research before use.
- **Meme syntax** — a recognizable sentence pattern without copying a full viral line.
- **Comment-section voice** — mock warning, exaggerated confession, self-roast, playful accusation, invitation to debate.
- **Hyperbole** — comic exaggeration that is obviously non-literal and never a factual performance claim.
- **Running gag** — one phrase or object returning with escalation.
- **Mock genre** — courtroom, breakup, job interview, detective case, emergency meeting, royal decree, sports commentary, family intervention. Product information must stay clear.

## 8. Creator Persona

Trend density should come from a stable creator voice. Lock:

```text
Age signal:
Region:
Occupation or social identity:
Knowledge level:
Humor style:
Energy:
Typical sentence length:
English usage:
Nói lái comfort:
Self-roast level:
Audience relationship:
Favorite comparison source:
Words they never use:
Credibility style:
```

Credibility styles: detail-oriented tester; chaotic but honest friend; beauty enthusiast; skeptical buyer; budget hunter; tech explainer; household problem solver; fashion stylist; food reaction creator.

Do not make every creator use the same "chị đẹp / chốt đơn / đỉnh chóp" voice.

## 9. Density Modes

### Light

For premium, technical, high-trust, mature-audience, or expensive purchases.

```text
30-60 seconds:  2-4 trend touches.
Unfamiliar current terms: at most 1-2.
```

### Medium (default for young audiences)

```text
30-60 seconds:  4-7 trend touches.
60-90 seconds:  5-9 trend touches.
Include at least one clean factual sentence after each dense joke cluster.
```

### High comedy

For inexpensive lifestyle products, novelty items, creator-led entertainment, playful social commerce.

```text
30-60 seconds:  6-10 trend touches, counting meme structures and running-gag returns.
Unfamiliar slang: usually at most 3 unique terms.
Stacked trend layers in one sentence: at most 2.
```

High density means one hook format, one or two current terms, one running gag, one playful CTA, and a repeated structure with variation — not ten unrelated slang words.

## 10. Information-To-Humor Ratio

Default pattern:

```text
Joke or trend hook
-> concrete problem
-> product interaction
-> visible or verifiable evidence
-> comic reaction
-> limitation or buyer fit
-> CTA
```

For every major joke cluster, include at least one of: feature; demonstration; sensory observation; price context; use case; limitation; buyer recommendation; comparison with a verified basis. Humor must not consume the product.

## 11. Short-Form Architecture

### 0-3s — Hook

Surprising result; relatable problem; humorous accusation; current phrase; visual contradiction; strong buyer question.

> Ai thiết kế cái máy này chắc từng bị tóc rụng phản bội.

> Mở hộp giá bình dân mà trúng trải nghiệm sít rịt hay gì?

No unverified claim in the hook.

### 3-8s — Problem

Name one real pain point.

> Túi nhỏ nhưng mình cần mang điện thoại, ví, sạc, son và lòng tự trọng.

### 8-25s — Demo

Show the product doing something. Trend language goes *around* the demonstration, not instead of it.

### 25-40s — Proof and reaction

State what happened: fit, speed, noise, texture, ease, weight, finish, visible result, measured output. Then the comic reaction.

### 40-55s — Limitation and buyer fit

Honest limitation increases trust.

> Nhưng bàn tay lớn thì nút này hơi bé. Không red flag, chỉ là cần thử trước.

### Final seconds — CTA

Natural, consistent with creator voice, no pressure or fake scarcity.

## 12. Hook Research

Research hooks as structures, not lines to copy: current opening rhythm; question vs statement; visual-first vs voice-first; comment-reply format; confession format; mock warning; the "tôi không ngờ..." structure; the current category-specific opening. Transform through the actual product. Never copy a creator's signature wording.

## 13. Humor Engines

Use 1-3 per script.

- **Incongruity** — treat a small feature as if it solved a dramatic life problem.
- **Self-roast** — the creator is the target, never the audience.
  > Sản phẩm không cứu được kỹ năng quản lý thời gian của tôi, nhưng ít nhất cứu được cái bàn.
- **Expectation reversal** — set up one result, reveal another.
- **Mock legal notice** — do not imitate official safety notices for harmful deception.
  > Thông báo khẩn: chiếc hộp này đã chiếm dụng trái phép toàn bộ ngăn kéo.
- **Personification** — keep the actual mechanism clear.
  > Cái nắp này đóng chắc đến mức nó có trust issue.
- **Relationship metaphor** — use carefully; never the default joke.
- **Dramatic overreaction** — clearly non-literal; never convertible into a health or efficacy claim.
- **`Nói lái`** — one punch or callback only.
- **Running gag**:

```text
Hook:        product treated as a suspicious new roommate.
Demo:        the "roommate" performs chores.
Limitation:  the roommate is noisy.
CTA:         decide whether to renew the lease.
```

## 14. Trend-Product Bridge

Before inserting a phrase, complete:

```text
The trend means:
The product fact or experience is:
The bridge is:
The joke is:
The viewer still learns:
```

Strong bridge: `sít rịt` = a rare/secret surprise; the product is a blind box with a rare variant; the viewer learns this box has a rare hidden design, subject to verified odds if known.

Weak bridge: `sít rịt` for an ordinary phone charger with no surprise, rarity, or reveal.

## 15. `Nói Lái` And Wordplay Rules

One setup, one transformed phrase, an optional plain-language response, then immediate return to product information.

> "Rồi em nhớ."
>
> Rối thật, vì dây sạc cũ quấn thành tổ. Còn sợi này có dây rút nên cất gọn hơn.

Do not chain several `nói lái` phrases, rely only on on-screen spelling, use obscure regional transformations without context, let TTS mispronounce the joke, or use wordplay for safety instructions.

## 16. Slang Function Map

| Function | Suitable trend type |
|---|---|
| Surprise | rare/unexpected language |
| Approval | affectionate or praise phrase |
| Warning | red-flag/toxic style language |
| Urgency | playful action phrase |
| Comparison | meme syntax |
| Buyer identity | community slang |
| Limitation | gentle self-aware label |
| CTA | playful invitation |
| Callback | repeated phrase with escalation |

Do not use an approval term for every feature.

## 17. Examples And Nuance

### `Trà xanh` / `tiểu tam`

Useful mainly for humorous comparison involving colors, competing items, beauty storytelling, or mock relationship skits. Never accuse a real person or brand.

> Màu xanh này nhìn ngoan hiền vậy thôi, lên da nổi hơn cả tiểu tam trong tập cuối.

Comic, but evaluate brand safety and audience taste. Safer alternative:

> Màu xanh này nhìn hiền, lên da lại giành spotlight rất có chiến lược.

### `Ngoan xinh yêu`

Works for cute packaging, soft colors, small accessories, an affectionate creator persona. Do not repeat it for unrelated technical features.

### `Sít rịt`

Best with a blind box, rare variant, hidden compartment, unexpected bonus, or surprising result.

### `Gét gô`

May be legacy or revived depending on live research. Use only when verified current, intentionally nostalgic, or the persona owns older meme language.

### `Nói lái`

A hook, transition, or callback — not a whole script dialect.

## 18. Category Calibration

- **Beauty and skincare** — trend language may be high, claims need care. Distinguish texture, finish, scent, packaging, visible application, and personal reaction from medically meaningful outcomes. No cure claims, guaranteed acne removal, universal suitability, or fabricated dermatologist authority. Never shame skin, weight, age, or features.
- **Fashion** — trend language for fit, styling, versatility, visual, comfort, pocket jokes, social scenarios. Do not misrepresent material, size, or body fit.
- **Food and beverage** — sensory detail, texture, aroma, sweetness, spice, portion, preparation. Do not fabricate ingredients, hygiene, health benefit, or freshness.
- **Technology** — density must not obscure model, compatibility, measured speed, battery, ports, software, limitations. Humor comes after the spec is understandable.
- **Home and lifestyle** — strong fit for problem-solution comedy, personification, before/after, chaos-to-order, running gags.
- **Financial products** — low density. Do not joke away fees, risk, interest, eligibility, terms, or loss. No guaranteed returns.
- **Health, supplements, medical devices** — very low density. Never use slang to make a medical claim feel harmless.
- **Products for children** — do not imitate youth culture in a way that manipulates children. No unsafe challenge language or pressure.

## 19. Platform Calibration

- **TikTok** — fast hook, conversational, sound-aware, current but natural, comment interaction, creator persona, visual demo.
- **Reels** — slightly more polished may work; trend and aesthetic share space; keep caption compatibility.
- **Shorts** — clear topic quickly; searchable product naming; avoid a hook so cryptic the category is unclear.
- **Livestream cutdown** — preserve spontaneous reaction; remove dead air; use a repeated phrase as segment identity; keep price and offer current.
- **Audio-only review** — reduce visual-dependent slang; explain physical results by sound and concrete description; test pronunciation.

## 20. TTS And Performance (VoxCPM Path)

Trend language often fails when read by TTS. In this repo, product scripts rendered through `story-to-audio` hit the same VoxCPM constraint as fiction: there is no Vietnamese pronunciation lexicon for bare Latin words, so English spellings, acronyms, stylized teencode, digit substitutions, emoji, and hashtags get mispronounced, rushed, or swallowed.

Rules for the voice-over text:

- remove raw emoji, hashtags, and platform UI symbols;
- normalize numbers, prices, dates, percentages, and units into spoken Vietnamese: `250k` -> `hai trăm năm mươi nghìn`, `20%` -> `hai mươi phần trăm`;
- avoid digit substitutions that TTS reads literally;
- do not depend on capitalization;
- keep `nói lái` next to its semantic anchor;
- insert natural sentence boundaries;
- test the exact voice before a long render.

For every English-origin or stylized token, pick one:

1. **Vietnamese phonetic respelling** when speakers already say it that way and it stays recognizable: `inbox` -> `in bốc`, `livestream` -> `lai sờ trim`, `comment` -> `còm men`, `Facebook` -> `phây búc`, `TikTok` -> `tích tóc`, `OK` -> `ô kê`, `email` -> `i meo`.
2. **A plain Vietnamese equivalent** when the respelling would be unreadable: `inbox` -> `nhắn tin riêng`, `deal` -> `giá hời`, `link` -> `đường dẫn`.
3. **Keep the English spelling only** when the render has been verified for that token, and record it as a render concern outside the script.

On-screen text and voice-over may differ:

```text
On-screen:   stylized trend spelling.
Voice-over:  TTS-safe pronunciation.
```

Keep their meaning aligned.

## 21. Trend Stacking

At most two layers in one sentence. Layers: one slang term; one meme syntax; one English phrase; one `nói lái`; one hyperbole; one running-gag reference.

Weak:

> Em này ngoan xinh yêu, visual đỉnh chóp, sít rịt, red flag không có, gét gô chốt đơn chị đẹp ơi.

Better:

> Ngoan xinh yêu ở phần nhìn. Còn phần dùng có đáng gét gô chốt đơn không thì test luôn.

Then demonstrate.

## 22. Plain-Language Recovery

```text
Trend line.
Plain product fact.
Demonstration.
Reaction.
```

> Em này nhìn ngoan xinh yêu nhưng lực gió không hiền.
>
> Máy có ba mức. Ở mức cao nhất, tóc ngắn khô nhanh hơn rõ rệt trong lần thử này.
>
> Còn tóc dày thì đừng kỳ vọng phép màu ba phút.

## 23. Honest Limitation As Humor

> Đẹp, nhẹ, đóng nắp chắc. Nhưng ngăn bên trong nhỏ, mang cả thế giới thì em này xin phép nghỉ.

> Khử mùi ổn trong phòng nhỏ. Phòng khách rộng thì nó không phải siêu anh hùng.

Always state the practical implication.

## 24. CTA Language

CTA may be playful but must stay clear: ask viewers to choose; invite a comparison; ask for the next test; direct to verified purchase information; encourage saving the review; disclose affiliate or sponsor context.

Avoid fake countdowns, false scarcity, guilt, shame, guaranteed transformation, and pressure on minors.

> Team bàn gọn hay team để đồ như bãi chiến trường? Bình luận để mình test bản lớn tiếp.

> Đường dẫn mình gắn ở phần mô tả. Đây là link tiếp thị liên kết, giá và ưu đãi nhớ kiểm tra lại tại thời điểm mua.

## 25. Variant Generation

- **Hook variants:** trend-led; problem-led; evidence-led; self-roast; comment-reply.
- **Density variants:** clean/light; medium; high-comedy.
- **Humor variants:** dry; energetic; absurd; relationship metaphor; mock genre.

Choose by product trust requirement, creator persona, platform, audience, and campaign goal. Do not automatically choose the densest version.

## 26. Testing And Iteration

Test the first three seconds, term familiarity, completion rate, comment comprehension, product recall, brand recall, CTA response, negative comments about forced slang, and whether viewers repeat the joke or ask what the product does.

A joke is not successful if viewers remember only the slang. Update the trend bank from real performance; do not infer causality from one viral result.

## 27. Trend Expiry

```text
Research date:
Planned publication date:
Recheck date:
Expected shelf life:
Evergreen replacement:
```

If publication is delayed: recheck fast trends after 14-30 days, replace declining phrases, preserve the script structure, retest TTS. For evergreen listings, prefer durable conversational humor over fast memes.

## 28. Safety And Brand Risk

Screen for misogyny; body shaming; age shaming; mental-health stigma; regional stereotypes; class contempt; sexual innuendo; harassment; counterfeit implications; competitor defamation; unsafe challenges; medical misinformation; deceptive urgency.

A current phrase can be unsuitable for a brand. Label internally: `SAFE`; `CONTEXT-SENSITIVE`; `BRAND-SENSITIVE`; `HIGH-RISK`; `REJECT`. Never use `HIGH-RISK` or `REJECT` terms.

## 29. Review Schema

```text
Evidence:
Trend symptom:
Current status:
Product bridge:
Creator-fit:
Humor value:
Information loss:
Claim risk:
Brand risk:
TTS risk:
Smallest repair:
```

Symptoms: trend spam; stale phrase; wrong niche; forced youth voice; copied viral line; no product bridge; joke before proof; false hyperbole; repeated CTA cliché; visual-only wordplay; unclear sponsorship; raw English token left for the renderer.

## 30. Common Failure Modes

**Trend salad** — too many unrelated terms. Repair: one trend family, one running gag.

**Product disappears** — funny, but viewers cannot name the feature. Repair: add factual anchors and visible demonstrations.

**Fake authenticity** — claims spontaneous personal experience that did not occur. Repair: use verified observation or neutral demonstration language.

**Stale trend** — an old phrase presented as current. Repair: research again or frame it as nostalgia.

**Copy-paste creator voice** — imitates another creator's signature. Repair: transform through the approved persona.

**Claim hidden in a joke** — "Em này chữa mọi nỗi đau." Even joking, this may imply efficacy. Repair: tie humor to mood or convenience, not medical outcome.

**One-note energy** — every sentence is loud. Repair: alternate hook, plain fact, reaction, pause, punch, limitation.

**TTS slang crash** — the engine misreads phonetic English or digit slang. Repair: normalize the voice-over separately (section 20).

**Audience insult** — the joke targets the buyer's appearance, income, intelligence, or insecurity. Repair: use self-roast, product personification, or situation humor.

## 31. Output Behavior

When planning: include the research date, selected trend units and status, why each term bridges to the product, and claim/TTS risks.

When drafting:

- produce a complete performance-ready Vietnamese script;
- keep verified product facts intact;
- mark optional on-screen text separately only when requested;
- never put research citations inside spoken lines;
- keep sponsor or affiliate disclosure;
- use higher trend density than fiction but keep plain-language recovery;
- protect category-specific safety.

When asked for multiple versions: vary hook, humor engine, and density — do not merely swap one slang word for another.

When asked to "làm cho Gen Z hơn": research current usage, strengthen the creator persona, update syntax and humor; do not indiscriminately add slang.

Save location: product scripts do **not** go into `kich-ban/<the-loai>/` — that path belongs to fiction. Ask the user where to save, or return the script in chat.

## 32. Checklist

- [ ] Did the user explicitly ask for trend language on a product/commercial script?
- [ ] Was current web research completed?
- [ ] Were general and category-specific trends researched separately?
- [ ] Was real usage checked, not only explainer pages?
- [ ] Is each trend unit labeled by status and evidence date?
- [ ] Does each trend connect naturally to a product fact, demo, scenario, or limitation?
- [ ] Is the creator persona stable?
- [ ] Is the density appropriate for product trust and video length?
- [ ] Are there at most two trend layers in one sentence?
- [ ] Does each dense cluster have a plain-language recovery?
- [ ] Is the product understandable without the jokes?
- [ ] Are all claims verified?
- [ ] Is personal experience real or clearly framed?
- [ ] Are limitations included where relevant?
- [ ] Are sponsorship and affiliate disclosures preserved?
- [ ] Is hyperbole obviously non-literal?
- [ ] Are health, finance, child, and safety-sensitive categories treated conservatively?
- [ ] Are harmful stereotypes and insults removed?
- [ ] Is `nói lái` understandable by ear?
- [ ] Does every English-origin or stylized token have a decided spoken form?
- [ ] Are numbers, prices, emoji, and hashtags normalized for the voice-over?
- [ ] Are on-screen spelling and voice-over normalization separated when needed?
- [ ] Is the CTA clear and non-deceptive?
- [ ] Will the trend still be current on the publication date?
- [ ] Does the audience remember the product as well as the joke?
