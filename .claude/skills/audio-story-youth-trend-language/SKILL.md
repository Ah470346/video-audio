---
name: audio-story-youth-trend-language
description: |
  MANUAL-ONLY. Live-researched youth-language layer for contemporary Vietnamese AUDIO STORIES and fiction scripts: current slang, teencode, meme phrasing, playful Vietnamese-English pronunciation, `nói lái`, and wordplay used as a precise accent for hooks, banter, comedy, social-media scenes, and memorable turns.
  Use ONLY when the user explicitly asks for trend words, teencode, slang, meme/viral phrasing, `nói lái`, or Gen Z-style language in a STORY. Never self-trigger for ordinary story writing, polishing, or reviewing. Route product/commercial scripts to `product-review-youth-trend-language`.
  MUST research the live web before selecting any time-sensitive term. Never replace character voice, causality, emotion, genre payoff, safety, or VoxCPM/TTS readiness.
---

# Audio Story Youth Trend Language

Use this skill when a contemporary Vietnamese audio story targets young listeners and the **user has explicitly asked** for language that feels socially current, playful, recognizable, and memorable.

The goal is not to make every character talk like a TikTok caption.

The goal is:

> Use a small amount of current language at the exact place where it reveals age, relationship, social environment, defensive humor, attraction, embarrassment, status, or cultural belonging.

Trend language is volatile. A phrase that feels alive today may feel forced, outdated, or incomprehensible months later.

Therefore:

> **Never select time-sensitive slang from memory alone. Live research is mandatory.**

## 0. Activation Rules (Read First)

This skill is **manual-only**.

Activate when the request contains an explicit trend-language intent word applied to fiction:

- `teencode`, `tiếng lóng`, `slang`, `từ trend`, `bắt trend`, `hot trend`, `từ xu hướng`, `từ khóa hot`, `Gen Z`, `genz`, `Gen Alpha`, `meme`, `nói lái`, `viral`, `từ giới trẻ`, `nói kiểu trẻ`;
- combined with a fiction target: `truyện`, `truyện audio`, `kịch bản truyện`, `nhân vật`, `drama`, `ngôn tình`, `kinh dị`, `hài`, `trinh thám`, and similar.

Do **not** activate when:

- the user only asks to write, expand, rewrite, polish, or review a story;
- the story is historical, secondary-world, or period-set, unless the premise explicitly creates the contrast;
- the trend intent belongs to a product/commercial script — that routes to `product-review-youth-trend-language`.

If the target is ambiguous (for example `kịch bản ngắn` with no subject), ask one short routing question before doing research.

## 1. Coordination Contract

Follow the shared priority rules in [../audio-story-engagement/references/phoi-hop-skills.md](../audio-story-engagement/references/phoi-hop-skills.md).

Always run alongside:

- `audio-story-engagement` (base workflow, prose default, safety, output contract);
- one main `audio-story-genre-*` skill;
- any active `audio-story-premise-*` skill;
- `audio-story-literary-texture` when it runs;
- `audio-story-final-polish` last.

**Placement in the workflow:** this skill is a lexical sub-pass. Select trend candidates **after the story contract and character calibration are locked**, apply them **while drafting or during the texture pass**, and let `audio-story-final-polish` normalize every spoken token afterwards. Never let trend selection drive plot or character design.

This skill controls only:

- current youth slang and teencode;
- meme-derived phrasing;
- playful Vietnamese-English readings;
- `nói lái` and phonetic wordplay;
- contemporary labels for social behavior;
- trend-shaped hook lines and punch lines;
- trend freshness and expiry.

This skill must not be used to repair weak plot, missing motive, generic emotion, absent chemistry, unclear exposition, or poor pacing. Those belong to the base (including its character-life gate), genre, and final-polish skills.

Hard boundaries:

- do not make every young character use the same slang;
- do not let an omniscient narrator sound like a comment section unless that narrator voice is explicitly approved;
- do not mistake caption-ready banter for human dialogue; trend phrasing must not create a polished metaphor/setup solely for another character's instant comeback;
- do not use a trend merely because it appeared in a source;
- do not force a trend into trauma, death, abuse, confession, or grief unless the character deliberately uses humor as defense and the emotional consequence stays intact;
- do not insert hashtags, emoji, platform UI text, or raw production markup into spoken prose unless the story depicts them;
- do not override the base skill's naming, `xưng hô`, no-real-place-name, or anti-`sến` defaults.
- treat every example in this and other skills as contaminated teaching material; never reuse its objects, gestures, situations, sentence shapes, or dialogue choreography in a story.

## 2. Mandatory Live Research

Before using any time-sensitive slang, meme phrase, trend format, or playful pronunciation, research the current web with `WebSearch`/`WebFetch`, or with `agent-browser read <url>` when a specific page must be opened.

This applies even when the user supplies examples such as `trà xanh`, `tiểu tam`, `ngoan xinh yêu`, `sít rịt`, `gét gô`, `rồi em nhớ`, `nhíu em nhớ`, `flex`, `red flag`, `out meta`, or any newer phrase.

> User-provided examples are candidates, not automatic approvals.

Research is mandatory when:

- the term is described as hot, current, trending, viral, Gen Z, Gen Alpha, TikTok, Threads, Facebook, or meme language;
- the meaning may have shifted, or the phrase may be ironic rather than literal;
- origin affects correct use;
- the trend may already be stale;
- the phrase is niche to a fandom, product community, region, or platform;
- pronunciation matters for audio;
- the term may be insulting, sexual, discriminatory, political, or legally risky;
- the story is explicitly set in the present year.

If live browsing is unavailable:

- do not claim that a phrase is currently trending;
- use durable contemporary colloquial Vietnamese instead;
- mark freshness as unverified in planning notes and tell the user;
- prefer character-specific natural speech over trend insertion.

## 3. Research, Status, And Expiry

Read [references/research-and-expiry.md](references/research-and-expiry.md) completely whenever this skill is activated. It defines research windows, source hierarchy, counter-search, minimum verification, candidate cards, status labels, ledgers, and shelf-life rechecks. Do not insert a time-sensitive term until that reference is complete.

## 7. Meaning Precision

Many youth terms are not interchangeable.

```text
"Tiểu tam":
A broad colloquial label for a third person interfering in an existing romantic relationship.

"Trà xanh":
Often implies someone who performs innocence, gentleness, or harmlessness while acting strategically in a romantic or social rivalry.
```

Do not replace every reference to a third party with `trà xanh`. Do not present an accusation as narrator-confirmed fact unless the story has evidence.

Use social labels as character judgment, gossip, self-aware joke, social-media caption, biased POV, or a confirmed social role only once established. Track who uses the label and what that choice reveals about them.

## 8. Character Ownership

Every trend phrase must belong to someone. Ask:

```text
Would this person know the term?
Would they use it sincerely, ironically, incorrectly, or never?
Who are they speaking to?
Are they performing youthfulness?
Are they code-switching?
Are they trying to impress, flirt, mock, soften, or hide?
Would they use the same phrase with a parent, boss, lover, and stranger?
```

Ownership modes:

- **Native user** — the phrase is part of normal speech;
- **Selective user** — trends only with close friends or online;
- **Ironic user** — uses the phrase while mocking the trend or themselves;
- **Late adopter** — uses an older or slightly wrong version, creating character-based humor;
- **Observer** — understands but does not speak that way;
- **Outsider** — misunderstands the phrase; use sparingly, never make the character unrealistically foolish;
- **Performer** — uses youth language to sell, manipulate, gain status, or appear younger.

A character's slang profile should be as specific as their emotional and occupational voice. This connects directly to the base character-life and relationship-voice judgment in [../audio-story-engagement/references/van-xuoi-chuyen-nghiep.md](../audio-story-engagement/references/van-xuoi-chuyen-nghiep.md) (§6).

## 9. Narrator Policy

Pick one mode and hold it:

- **Neutral contemporary narrator** (safest default) — mostly standard conversational Vietnamese; trend terms appear mainly in dialogue or free indirect thought.
- **Youth first-person narrator** — may use more current language, but still needs rhythm variation and emotional sincerity; must not read like a continuous caption.
- **Comic commentator narrator** — may use trend structures as punch lines; must preserve causal clarity and not compete with every character.
- **Retrospective narrator** — use terms appropriate to the time of narration; distinguish language used at the event from language used later.
- **Historical or secondary-world narrator** — no modern internet slang unless the premise creates that contrast. A `xuyên không`/`hệ thống` protagonist may think in current slang, but other characters must not automatically understand it.

## 10. Density Budget

Trend language is a high-flavor ingredient. These are ceilings, not targets, and they sit below the base skill's clarity and anti-`sến` defaults.

### Serious drama, thriller, mystery, horror

```text
Opening:            0-1 trend-led phrase in the first 60-120 seconds.
Per 1,000 words:    usually 0-2 noticeable trend terms.
Same exact term:    usually at most 2 uses per episode unless it is a deliberate motif.
```

### Youth romance, campus, office comedy

```text
Opening:            0-2 trend touches when the hook is socially comic.
Per 1,000 words:    usually 1-4 noticeable trend terms.
Banter cluster:     at most 2 unfamiliar or highly current terms before returning to plain speech.
```

### High-comedy contemporary story

```text
Per 1,000 words:    usually 2-6 trend touches, counting structures and wordplay - not six unrelated slang words.
Require plain-language recovery between clusters.
```

A scene with no trend language may still be the best choice.

## 11. High-Value Insertion Zones

- **Opening hook** — one current phrase can establish youth setting, social stakes, narrator attitude, comic contradiction, or immediate tension. Use only when the label is already intelligible or is quickly dramatized.
- **Character banter** — best when both speakers share the reference, or one misuses it in a character-specific way, and the joke changes power, intimacy, or has a consequence.
- **Private chat or social-media scene** — group chat, comment section, livestream, campus thread, creator workplace, fan community. Density may rise naturally; speaker identity must survive.
- **Defensive humor** — a character uses a meme phrase to avoid sincerity; the story later reveals the emotional cost.
- **Punch line** — one trend phrase after clear setup. Never stack five current terms into the payoff.
- **Callback** — a trend phrase returns with changed emotional meaning:

```text
Early:  used as a joke between friends.
Later:  used by one person after the relationship breaks.
Final:  the same phrase is deliberately not answered.
```

## 12. Low-Value Or Dangerous Zones

Avoid or heavily justify trend language during: death notification; funeral; sexual violence; domestic abuse; child harm; medical emergency; sincere confession; legal evidence; major plot explanation; trauma disclosure; final emotional release.

Exception: the character uses humor defensively and the narrative clearly preserves the gravity. Never use slang to make pain "content-friendly."

## 13. Naturalization Test

A phrase is natural only when all pass:

```text
Speaker fit:    this person would plausibly know and use it.
Listener fit:   the in-story listener understands or can infer it.
Situation fit:  the phrase performs a social action here.
Meaning fit:    its current pragmatic meaning matches the scene.
Rhythm fit:     it lands without stopping the story.
Density fit:    nearby sentences are not already overloaded.
Expiry fit:     the story's intended shelf life supports the term.
TTS fit:        the written form renders correctly on VoxCPM (see section 17).
```

If two or more fail, remove or replace.

## 14. The One-Line Inference Rule

A listener should understand the emotional role of a term from context even without knowing its origin.

Weak:

> "Cô ta đúng là sít rịt."

Contextual:

> Bốc đại một người đi xem mắt mà trúng đúng con trai chủ nhà. Sít rịt đời thật đây rồi.

Do not pause the story for a dictionary definition.

## 15. Trend Transformation

Do not copy viral wording mechanically. Transform through character relationship, setting, present conflict, an object in the scene, a local detail, or a story motif. Profession may shape the social action or observation, but it must not be converted mechanically into a metaphor for love, family, or identity. Run the shared [human semantic-fit gate](../audio-story-engagement/references/ngon-ngu-con-nguoi.md) when a transformed phrase uses an occupational/object/system field.

Generic:

> "Gét gô!"

Character-specific:

> Hồ sơ đủ, camera đủ, người phản bội cũng đủ. Gét gô ra tòa thôi chị đẹp.

Use only if current research supports the phrase, or if intentional legacy humor is established.

## 16. `Nói Lái` And Phonetic Wordplay

Vietnamese youth language may use đảo âm, đổi vị trí từ, playful mispronunciation, Vietnamese phonetic English, sound resemblance, intentionally childlike pronunciation, and distorted spelling.

Examples supplied by the user (still require research):

- `rồi em nhớ` from `nhớ em rồi`;
- `nhíu em nhớ` from `nhớ em nhiều`;
- `gét gô` from `let's go`;
- `sít rịt` from `secret`.

Rules:

- preserve immediate comprehensibility;
- give a setup or a response that reveals the intended meaning;
- never place several `nói lái` phrases back to back;
- never use wordplay in critical evidence or plot-load-bearing information;
- never depend on visual spelling alone — audio listeners cannot see it;
- avoid accidental offensive or sexual readings;
- do not make every young person speak in distortions.

Anchor the joke by ear:

> "Rồi em nhớ."
>
> "Nhớ thì nói nhớ. Bày đặt nói lái."

## 17. Vietnamese-English Play And VoxCPM Spoken Form

Common modes: Vietnamese phonetic reading; code-switching; English noun with Vietnamese grammar; ironic business language; platform language; fandom language. Use only when it matches education, workplace, community, generation, personality, and relationship.

Weak:

> "Em feeling rất là happy vì vibe hôm nay healing."

Stronger:

> "Quán này đúng kiểu chữa lành bằng tiền của khách."

**VoxCPM constraint — this is a hard requirement in this repo.** The render pipeline has no Vietnamese pronunciation lexicon for bare Latin words, so English spellings, acronyms, stylized teencode, and digit-substitutions can be mispronounced, rushed, or swallowed. Every English-origin or stylized token that survives into the story file must already be written the way it should be heard.

Choose one repair per token:

1. **Vietnamese phonetic respelling** when Vietnamese speakers already say it that way and it stays recognizable by ear: `inbox` -> `in bốc`, `livestream` -> `lai sờ trim`, `comment` -> `còm men`, `Facebook` -> `phây búc`, `TikTok` -> `tích tóc`, `email` -> `i meo`, `OK` -> `ô kê`.
2. **A plain Vietnamese equivalent** when the respelling would look strange or unreadable: `inbox` -> `nhắn tin riêng`, `deal` -> `giá hời`, `review` -> `đánh giá`.
3. **Keep the English spelling only** when the term is already a settled loanword read as Vietnamese by the engine and the render has been verified, and record it as a render concern outside the story file.

Never leave the decision to the renderer. Record the chosen spoken form in the trend candidate card, and let `audio-story-final-polish` verify it in its VoxCPM/TTS pass. See [../audio-story-engagement/references/voxcpm-tts-ngat-nghi.md](../audio-story-engagement/references/voxcpm-tts-ngat-nghi.md), section "English, Teencode, And Trend Tokens".

Ask before shipping any wordplay:

```text
Will VoxCPM pronounce the written form as intended?
Will listeners hear the original phrase behind the distortion?
Does punctuation help or harm?
Would a plain Vietnamese anchor sentence improve recognition?
```

## 18. Durable Slang vs Fast Meme

**Durable contemporary vocabulary** may include `red flag`, `flex`, `toxic`, `chữa lành`, `hướng nội`, `crush`, `tiểu tam`. These often survive one viral cycle, but meaning, saturation, and spoken form still need checking.

**Fast meme language** includes viral audio fragments, creator catchphrases, current playful spellings, one-season challenge phrases, recent comment templates. Use only when the story is intentionally dated, publication is soon, evidence is strong, the character community fits, and the line still parses after the trend fades.

For evergreen audio, prefer durable language transformed through character voice.

## 19. Age, Region, And Community

"Young people" is not one language group. Calibrate for teenagers, university students, early-career office workers, gamers, beauty communities, K-pop/anime fandoms, queer communities, regional speech, urban vs provincial settings, creators and livestream sellers, tech workers, and young parents.

A term may be widely understood but rarely spoken; used only ironically; dominant in comments but awkward face to face; specific to one platform; more natural in the South, North, or Central region; or class- and education-coded. Use community evidence, not stereotypes.

## 20. Sensitivity And Harm Filter

Flag terms that may shame appearance; sexualize minors; stigmatize mental health; demean women or third parties; attack sexual orientation or gender identity; target ethnicity, region, disability, class, or occupation; encourage harassment; falsely accuse someone of cheating, abuse, crime, or disease; or trivialize trauma.

A term can be current and still unsuitable. For labels such as `trà xanh`, `tiểu tam`, `red flag`, `toxic`, or `pick me`: identify who is judging, distinguish suspicion from fact, avoid narrator endorsement without evidence, and preserve character bias intentionally. The base safety reference [../audio-story-engagement/references/an-toan-tu-vung.md](../audio-story-engagement/references/an-toan-tu-vung.md) wins any conflict.

## 23. Review And Repair

When reviewing a draft for trend language, report:

```text
Evidence:
Trend-language symptom:
Freshness status:
Character-fit problem:
Context problem:
Listener impact:
TTS/VoxCPM risk:
Smallest repair:
Evergreen alternative:
```

Symptoms: `trend spam`; `outdated phrase`; `wrong meaning`; `narrator contamination`; `all characters share one slang voice`; `visual-only wordplay`; `serious beat undercut accidentally`; `commercial-sounding youth imitation`; `unverified currentness`; `raw English token left for the renderer`.

Full manuscript diagnosis remains the job of `audio-story-reviewer`; this section covers only the trend layer.

## 24. Common Failure Modes

**Trend salad** — "Chị đẹp flex visual đỉnh chóp, ngoan xinh yêu, sít rịt, gét gô săn red flag nào." Repair: one social action, one phrase, grounded in character and situation.

**Dictionary dialogue** — a character stops to define the slang. Repair: let context reveal meaning unless the explanation is natural between those two people.

**Youth costume** — an older authorial narrator uses slang to sound young while characters stay generic. Repair: build character life and relationship voice first (base character-life gate, van-xuoi-chuyen-nghiep.md §6).

**Expired hook** — a once-viral phrase used as breaking news. Repair: recheck status or frame it as nostalgia.

**Emotional sabotage** — a meme phrase lands exactly where sincerity should. Repair: move the joke earlier, make it defensive, or delete it.

**TTS failure** — the written slang produces the wrong pronunciation on VoxCPM. Repair: apply section 17.

**Forced `nói lái`** — technically clever, but no character would say it. Repair: reserve wordplay for a speaker with that humor style or a relationship ritual.

**Copying the trend** — repeating a viral line without transformation. Repair: rebuild from profession, relationship, setting, or plot object.

**Aphorism tennis** — one trendy line exists mainly to cue an equally polished reply. Repair: return both speakers to separate immediate goals and ordinary language; a memorable caption is not a relationship beat.

## 25. Output Behavior

When planning:

- show only approved trend candidates with meaning, status, speaker, scene, risk, and VoxCPM spoken form;
- do not dump a giant slang glossary;
- record the research date internally.

When writing:

- use trend language only where it performs a narrative or social function;
- keep plain Vietnamese around the trend;
- do not explain the trend after it lands;
- no hashtags or emoji in spoken narration;
- preserve character-specific `xưng hô`;
- keep the saved file pure story, per the base output contract.

When the user asks for a current slang list: browse live, date the list, distinguish current/established/niche/legacy/uncertain, include usage context and misuse risk, and do not claim universal Gen Z usage.

## 26. Checklist

- [ ] Did the user explicitly ask for trend/teencode language in a story?
- [ ] Was live web research performed for every time-sensitive term?
- [ ] Are sources recent enough for the trend type?
- [ ] Was actual usage checked, not only explanation pages?
- [ ] Is each term labeled by current status with an evidence date?
- [ ] Does each phrase belong to a specific character or approved narrator mode?
- [ ] Does the speaker own the wording without borrowing another character's profession/image field or serving as setup for a perfect comeback?
- [ ] Is the pragmatic meaning correct for this scene?
- [ ] Is the phrase natural for this region, age group, and community?
- [ ] Can a listener infer its role without a dictionary interruption?
- [ ] Is trend density below the selected ceiling, and below base clarity?
- [ ] Are plain-language recovery lines present between dense clusters?
- [ ] Are serious emotional beats protected?
- [ ] Are accusations and social labels handled as perspective, not unsupported fact?
- [ ] Has harmful, discriminatory, or humiliating slang been filtered?
- [ ] Is `nói lái` understandable by ear, with an anchor when needed?
- [ ] Does every English-origin or stylized token have a decided VoxCPM spoken form?
- [ ] Are visual-only spellings, raw hashtags, and emoji removed from narration?
- [ ] Does a repeated trend phrase change function or meaning?
- [ ] Will the line still work after the trend cools?
- [ ] Does the story remain human, coherent, and emotionally sincere without the trend?
- [ ] Did `audio-story-final-polish` run after this pass?
