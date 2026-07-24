# Coordination Contract For Audio Story Skills

This is the shared priority source when multiple audio-story skills trigger. The goal is for each skill to do one job without stacking conflicting formulas.

**Supreme goal, binding on every layer:** the finished story must read as told by a human expert — natural, alive, worth retelling. Every rule below is an instrument for that outcome. When mechanical compliance with any rule would make the prose sound less human, choose the more human option within safety, logic, and one-listen clarity.

## 1. Four Layers And Scope

### Layer 1: Base — `audio-story-engagement`

Responsible for:

- idea and opening approval workflow;
- central question, causality, narrative reward;
- narrator-led default, criteria for direct dialogue, and one-listen semantic clarity: stable referents, explicit connector premises, action/mechanism legibility, and scene orientation;
- human semantic fit: natural Vietnamese collocation, category fit between words and their human targets, speaker ownership of marked metaphors, and dialogue that serves immediate intention rather than quote production;
- professional prose judgment: earned character knowledge, example immunity, scene-derived detail, imperfect human formulation, and technique that stays invisible;
- VoxCPM/TTS-ready punctuation, paragraphing, spoken-token forms, and dialogue turn shape;
- Vietnamese address forms (`xưng hô`) and base safety;
- output format and save location.

The base skill does **not** decide how a story must be scary, romantic, funny, or mysterious.

### Layer 2: Genre — `audio-story-genre-*`

Responsible for:

- emotional/genre promise;
- conflict type, scene engine, and genre-specific payoff;
- mistakes that break the audience expectation of that genre.

Genre provides choices; it must not impose hard quotas. A story has one **main genre**. Secondary genres only add material.

### Layer 3: Premise — `audio-story-premise-*`

Responsible for:

- rules of mechanisms such as reincarnation, system, book transmigration, or `truyện rác`;
- limits of knowledge/ability;
- consequences when the mechanism changes choices and the world.

Premise does not decide the final emotional payoff. Main genre and user intent do.

### Layer 4: Final Pass — `audio-story-final-polish`

Runs last to repair logic, motivation, emotion, dialogue, address forms, read-aloud rhythm, and VoxCPM/TTS pause readiness. It:

- must not change main genre, premise, approved ending, or approved intent;
- must not replace the narrator-led base default with dense dialogue unless the user requested audio drama / dialogue-heavy mode;
- must not insert SSML, `[pause]`, SFX/BGM, or production markup into pure story files unless the user requested that mode;
- must not add missing quotas or techniques for their own sake;
- must report to the user if fixing logic requires changing an approved creative decision.

### Cross-Genre Craft Skill — `audio-story-literary-texture`

Character and relationship life is **not** a separate skill. It is base judgment: the base skill applies the character-life gate in [van-xuoi-chuyen-nghiep.md](van-xuoi-chuyen-nghiep.md) (§2 earned insight, §3 dialogue, §6 character life, directional relationships, and opposing/minor characters) during contract lock, mapping, and drafting. Off-plot life, directional relationships, motivated error, and earned intimacy belong there, applied as judgment rather than filled-in worksheets, and never as an ordinary action inserted into every scene.

`audio-story-literary-texture` is the one cross-genre craft sub-pass. It applies to **every** genre but is not a new genre or premise, so it does not sit in the four-layer stack; it runs **inside** the base workflow, **after a causally clear draft exists and before final polish**. It never runs before the draft, because its own rule is to draft action and causality clearly first. It shapes POV imagery, metaphor, motif, sentence rhythm, and acoustic language.

The texture pass may conclude `no added material needed`. Its purpose is judgment, not visible technique coverage. Do not choose an image field by default or add a motif/callback because a skill offers one.

Image fields and professional vocabulary are optional resources, not obligations. They may shape what one POV notices, but they may not turn people or relationships into objects by default, spread one character's vocabulary into every speaker, or create paired aphorisms for their own sake. Use the mandatory gate in [ngon-ngu-con-nguoi.md](ngon-ngu-con-nguoi.md) whenever a conspicuous metaphor or high-impact dialogue cluster uses an object, profession, system, or procedural source domain.

### Opt-In Lexical Sub-Pass — `audio-story-youth-trend-language`

Manual-only. It runs **only when the user explicitly asks for teencode, trend words, slang, meme phrasing, `nói lái`, or Gen Z speech in a story**. Finishing, polishing, or reviewing a story never activates it.

It is a lexical layer, not a layer in the four-layer stack:

- select trend candidates **after the contract and base character-life calibration are locked**, so the slang belongs to a character who already exists;
- apply them during drafting or during the `audio-story-literary-texture` pass;
- `audio-story-final-polish` still runs last and still owns the final spoken-token decision.

Authority: it sits **below base clarity, main genre payoff, safety, and TTS readiness**. It may not raise density past the base skill's one-listen clarity and anti-`sến` default, may not rename characters or move the setting to satisfy a trend, and may not put slang into a scene the genre needs to keep grave. Its density ceilings are ceilings, never targets. Every English-origin or stylized token it introduces must carry a decided VoxCPM spoken form (see `voxcpm-tts-ngat-nghi.md`, "English, Teencode, And Trend Tokens").

The product-side sibling, `product-review-youth-trend-language`, is **outside this contract entirely**: it writes commercial scripts, not fiction, and no audio-story skill (including final polish) should edit its output.

Authority: the literary-texture craft pass sits **below main genre payoff** in the priority order below. It adds material and surface; it must not steal the genre payoff, break one-listen clarity, obscure fair clues, hide missing motive, or change the approved premise/ending. It operates **inside** the base skill's firm-modern-prose / anti-`sến` default: when a texture suggestion conflicts with base clarity or restraint, base wins. Texture raises specificity and POV-distinctiveness, not ornamentation. Order: base character-life gate -> draft -> `audio-story-literary-texture` -> `audio-story-final-polish` (always last).

## 2. Priority Order When Instructions Conflict

Apply from top to bottom:

1. **Safety, truthfulness, non-contradictory logic, one-listen semantic clarity, human semantic fit, and earned character knowledge.** No creative request, genre, premise, literary omission, or stylistic compression can loosen harmful guidance, misrepresent real people, break established world rules, leave basic referents/actions/mechanisms unidentified, use connectors whose required premise is absent, make people sound like objects/systems merely to satisfy a motif, or let a character know another person's hidden truth without sufficient evidence/history. If logic requires changing an approved idea, report instead of silently changing it.
2. **The user's latest direct requirement inside those boundaries.** Example: third person, sad ending, no twist, or "choose and proceed" overrides defaults that it directly addresses.
3. **User-approved premise, ending, and promise.** Do not silently change these while polishing.
4. **Base workflow and output contract.** Genre/premise cannot skip approval gates or add metadata to pure story files.
5. **Active premise mechanism rules.** Only rules established in the story count.
6. **Main genre.** Controls emotional question and primary payoff.
7. **Secondary genres.** Add scenes, tone, or techniques without stealing payoff.
8. **Tips, numbers, title patterns, examples.** These are suggestions, not laws.

When two same-level instructions conflict, choose the one that best serves **approved promise + causal chain + one-listen clarity**. Record the choice in the story map; do not try to satisfy both.

**A pass that adds nothing is a valid and often correct result.** Every checklist in these skills tests for the *absence of defects*, not the *presence of technique*. Do not insert a hook, reversal, motif, ordinary action, worksheet field, or quotable line merely to satisfy a checklist item; when the draft already earns its value, conclude `no change needed` and move on. Technique added only to tick boxes — especially cumulatively across base, genre, premise, texture, and final polish — is itself the machinery these skills exist to prevent.

## 3. Unified Workflow

1. **Identify layers:** base always applies; choose main genre; add secondary genre or premise only when triggered.
2. **Step 0:** research/propose ideas through the base workflow. Each idea states main genre, premise, and payoff type. Stop for the user's choice. Skip only on an explicit no-approval instruction (*"không cần hỏi"*, *"cứ viết luôn"*); a detailed brief or *"bạn tự tìm ý tưởng"* is NOT authority to proceed. When skipping, record the chosen direction.
3. **Lock the contract:** central question, target emotion, listener reward, world rules, and things the user does not want.
   - **Human life (all genres):** after locking the contract and before mapping, apply the base character-life gate in [van-xuoi-chuyen-nghiep.md](van-xuoi-chuyen-nghiep.md) (§6) so major characters carry off-plot pressure, directional relationships, competence limits, and contradictions relevant to action. This is judgment, not a worksheet; do not equalize depth across the cast, fill every field, or insert an ordinary action into every scene.
4. **Step 2:** propose different openings through the base workflow. Genre/premise helps generate options but cannot skip the gate or force one type. Skip only when the user gave a concrete opening to use, or an explicit no-approval instruction; then choose with a reason and continue. Approving an idea in Step 0 does not approve the opening.
5. **Map:** base choice-consequence chain + genre scene engine + premise law/knowledge ledger + semantic-clarity ledger for stable entity/mechanism names, first-use interaction methods, and the explicit premise behind consequential connectors.
6. **Write:** prioritize story, not visible technique labels. Treat all skill examples as contaminated teaching material; generate names, occupations, objects, gestures, sensory anchors, and sentence shapes from the current story rather than the example bank. Run [van-xuoi-chuyen-nghiep.md](van-xuoi-chuyen-nghiep.md).
   - **Literary texture (all genres):** once the draft reads clearly for action and causality, run `audio-story-literary-texture` to add POV imagery, motif, and rhythm only where they change meaning, staying inside the firm-modern-prose default. Run it before final polish, never before a causally clear draft exists.
7. **Self-check:** run base, main genre, and premise checks. For secondary genres, check only promises actually used.
8. **Final polish:** after a complete story draft exists, run full `audio-story-final-polish`, including the VoxCPM/TTS pause and spoken-token pass. If story content changes afterward, rerun it. For premise contracts, outlines, or opening options, use relevant checks only; do not claim the whole story is final-polished.
9. **Save/respond:** follow base output contract and user request. Hybrid stories save under the main genre folder; premises do not create folders.

`final-polish` is the **last content editing pass** of the story draft, not a label to attach to intermediate artifacts. Saving a file after polish is not content editing; any sentence/scene change is.

## 4. Choose The Main Genre For Hybrids

Ask:

1. What reward keeps the listener listening?
2. What type is the central question?
3. If one genre is removed, which loss breaks the identity or ending?

| Main reward | Usual main genre |
|---|---|
| relationship truth + choice after betrayal | drama |
| laughter from deviation and consequence | comedy |
| unease/fear + confronting threat | horror |
| romantic relationship transformation | romance |
| evidence-based solution to mystery | mystery |

Example: a missing-person story with a ghost, but the final payoff is proving who staged the scene, is mainly `trinh-tham` with `kinh-di` secondary. If the solution is less important than a force invading the family, reverse it.

Do not trigger a secondary genre merely because there is a love scene, a joke, or a secret. Trigger it only when the story promises a meaningful experience from that genre.

## 5. How Genre And Premise Cooperate

Genre answers:

- What emotion/reward does the listener expect?
- What type of choice creates the climax?
- What ending fulfills the promise?

Premise answers:

- What special ability/knowledge/constraint exists?
- What limits and world-state changes follow?
- How does the mechanism make the genre choice harder or different?

Do not let premise replace story with interface. Example: a system in romance must complicate/clarify romantic choice; it must not become unrelated point collection.

If multiple premises apply:

- make a law ledger for each;
- keep only mechanisms that change choice;
- decide whether one law contains the other;
- do not use a second premise only to rescue the first.

## 6. What Is Not A Conflict

- **Tone variation inside one story:** a light joke in horror is contrast, not automatically comedy genre.
- **One technique, many uses:** dramatic irony in drama and mystery serves different information structures.
- **Genre-specific pacing:** mystery may delay information; comedy may pay off more frequently. This is fine if causality and progress remain.
- **Non-default endings:** romance may be SE/BE if approved; horror may explain everything; mystery may intentionally fail if that is the promise.

A conflict exists only when two rules require incompatible behavior or one skill breaks the main skill's promise.

## 7. Common Conflict Matrix

| Conflict | Unified handling |
|---|---|
| Genre wants a special hook; base asks user to choose | Genre creates suitable options; base keeps the gate unless user gave authority |
| Premise wants a law info-dump; base wants action opening | Introduce only the law affecting current choice |
| Comedy wants harmlessness; drama wants heavy consequence | Main genre decides. Drama main: jokes do not erase harm. Comedy main: limit harm |
| Horror wants ambiguity; mystery wants fair play | Hide form/meaning, not data needed for promised solution |
| Romance wants closeness; mystery/thriller wants suspicion | Each intimate scene also changes trust or evidence |
| Truyen-rac wants "stupid" characters; base requires motive | Write consistent bias/need that causes wrong choices |
| Foreknowledge removes surprise | Shift suspense to prevention, cost, proof, ethics; do not force every forecast to fail |
| Final polish finds premise illogical | Repair inside approved law; if law/ending must change, report to user |
| Any skill sets number/minute/percentage quotas | Treat as pacing examples, not law |
| Safety weakens a "heavy" scene | Keep event clear; move weight to choice/consequence |
| Literary texture wants imagery; base wants firm, anti-`sến` prose | Base clarity/restraint wins ties; keep only texture that passes the device-function test and the "pushes plot/character" test |
| Character profession supplies an image field; dialogue wants natural speech | Profession may shape perception, action, or one owned comparison. It does not require occupational metaphors, does not transfer that vocabulary to other speakers, and never outranks the plain line that better performs the human intention. |
| Genre wants a memorable/punchy line; human speech would be plainer | Use the plainer line. Quoteability, symmetry, and instant comeback are not genre payoffs. Resonance must emerge from pressure and consequence, not aphorism tennis. |
| Character-life gate offers ordinary action; scene works without choreography | Add nothing. Food, cleaning, clothing adjustment, object alignment, and household ritual are optional; stillness or direct narration may be more truthful. |
| Skill example offers a fitting object/gesture/occupation | Do not reuse it. Re-derive detail from physical presence, schedule, money, body, setting, and current task in the approved story. |
| Retention rule wants a hook/turn every minute; scene needs consequence or absorption | Let the consequence/absorption carry value. Retention is not constant surprise, reversal, or slogan density. |
| Sharp observer appears to understand a stranger immediately | Separate observation from inference and truth. Keep certainty provisional until repeated evidence, history, or disclosure earns it. |
| Mystery, horror, or literary omission wants ambiguity; base requires orientation | Withhold motive, answer, or meaning; name the current actor/object/mechanism, establish scene geography, and state the rule needed to understand present danger. Missing referents and causal steps are not suspense. |
| Character-life gate wants messy detail; final polish is the last pass | Character-life judgment (base gate) runs during drafting before final polish; final polish preserves that roughness and remains the last content edit |
| Craft-skill detail competes with genre payoff | Main genre keeps the central reward; the base character-life gate and texture add material without stealing payoff or obscuring fair clues |
| User asks for teencode/trend words; base wants firm, clear, anti-`sến` prose | Trend language is an accent on specific characters and scenes, not a narration style. Base one-listen clarity wins ties; keep plain Vietnamese around every trend cluster |
| Trend skill wants an English word; VoxCPM cannot pronounce it | Write the spoken form in the file (`inbox` -> `in bốc`) or use a Vietnamese equivalent. Final polish verifies it; never ship a bare Latin token to the renderer |
| Trend slang uses accusation labels (`trà xanh`, `tiểu tam`, `red flag`) | Base safety wording rules win. The label is a character's judgment, not narrator-confirmed fact, unless the story proved it |
| Trend skill implies a modern influencer setting; base defaults to Chinese-style names and a modern Chinese setting | Base naming/setting defaults hold unless the user changes them. Trend language adapts to the world; the world does not adapt to the slang |
| Trend phrase lands on a death, confession, or final emotional beat | Genre payoff wins. Move the joke earlier or cut it, unless the character is visibly using humor as defense and the weight survives |

## 8. Combination Examples

### Drama + Book Transmigration

- **Genre:** betrayal truth and choice after knowing.
- **Premise:** narrator remembers the book version but not off-page scenes.
- **Correct climax:** choose between publishing evidence or saving someone who once betrayed them.
- **Wrong:** every scene says "in the book" and events happen exactly as written.

### Mystery + Horror

- **Main mystery:** listeners get enough data to solve; supernatural rules are testable facts.
- **Secondary horror:** clue presentation creates dread and unsafe space.
- **Wrong:** hiding evidence and calling it supernatural mystery.

### Romance + Comedy

- **Main romance:** relationship changes through sincere choice.
- **Secondary comedy:** mismatched logics create friction and intimacy.
- **Wrong:** prolonging a misunderstanding because they do not say one obvious sentence.

### Truyen-Rac + Reincarnation + Drama

- **Drama:** payoff is the narrator regaining choice after betrayal.
- **Reincarnation:** memory enables preparation, but changes cause future divergence.
- **Truyen-rac:** other characters keep choosing wrongly through built bias.
- **Wrong:** narrator knows everything and wins everything while everyone else is foolish only for revenge scenes.

## 9. Coordination Checklist

- [ ] Main genre, secondary genres, and premises are recorded?
- [ ] Central question and payoff belong to the main genre?
- [ ] Each premise has tracked rules, limits, and state?
- [ ] Secondary genres add experience without stealing payoff?
- [ ] No genre/premise skipped approval gates unless the user gave an explicit no-approval instruction?
- [ ] No numeric/minute/percentage quota is treated as law without user/channel data?
- [ ] Genre, premise, and final polish preserve narrator-led default and selective dialogue?
- [ ] VoxCPM/TTS readiness is preserved: natural punctuation, clean paragraph resets, clear speaker turns, and pronounceable numbers/acronyms/symbols?
- [ ] One-listen semantic clarity is preserved: every pointer has one antecedent, every connector has its prerequisite, first-use mechanism actions are audible, and no basic identity/action/geography/causality must be guessed?
- [ ] Human semantic fit is preserved: concrete wording uses natural Vietnamese collocation; marked metaphors have exact mappings and character ownership; no profession/object field has spread across speakers; no exchange exists mainly as quotable aphorism and comeback?
- [ ] Professional prose judgment is preserved: insight is earned; no skill-example object/action/sentence shape leaked into the draft; technique does not show as a checklist; quiet scenes are valued by function rather than forced into visible turns?
- [ ] When instructions conflicted, the priority table decided instead of combining incompatible demands?
- [ ] Safety and causality were not loosened by genre/premise?
- [ ] The base character-life gate was applied during contract lock and drafting, and `audio-story-literary-texture` (if used) ran after a causally clear draft and before final polish?
- [ ] `audio-story-youth-trend-language` ran **only** because the user explicitly asked for trend/teencode language, with live research and a decided spoken form for every English-origin token?
- [ ] Craft-skill life detail and literary texture added material without stealing genre payoff, breaking one-listen clarity, or obscuring fair clues?
- [ ] Final polish ran last and preserved approved intent?
