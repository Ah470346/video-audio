---
name: audio-story-engagement
description: |
  Base skill for writing high-retention Vietnamese audio-story scripts through clear promises, causality, character motivation, narrative rewards, pacing, immersion, narrator-led prose, and selective dialogue.
  ALWAYS use this skill whenever the user asks to create/write a story, write an audio-story script, write drama/adultery/mystery/horror/romance/comedy fiction, or any narrative fiction request, even if the user does not name the skill.
  This skill does NOT define the genre. It defines the thinking model and structure for keeping listeners engaged. When the request has a concrete genre, use the matching `audio-story-genre-*` skill as well; use `audio-story-premise-*` when the premise includes reincarnation, a system, transmigration into a book, rage-bait/truyen-rac, or related mechanics.
---

# Audio Story Engagement

Turn every story request into a Vietnamese audio script that is understandable in one listen, driven by motivation, causality, and emotional progression. Do not merely list events; design expectation and payoff so the listener wants the next minute. Do not claim that wording can reliably "trigger" dopamine, oxytocin, cortisol, mirror neurons, or similar biological effects. Treat those labels only as old mnemonics; the practical writing operations live in [references/ky-thuat-chi-tiet.md](references/ky-thuat-chi-tiet.md).

When this skill runs with genre, premise, or final-polish skills, follow the shared priority contract in [references/phoi-hop-skills.md](references/phoi-hop-skills.md). Specialist skills must not skip approval gates, loosen safety rules, impose hard quotas, or change a user-approved creative intent.

**Core test:** every audio minute must answer, "Why should the listener not stop right now?" If a section cannot answer that, rewrite it.

## Project Defaults

Apply these defaults unless the user asks otherwise. Direct user requirements for point of view, setting, naming system, ending, or style override defaults within the boundaries of safety, logic, and one-listen clarity.

### 1. Pronouns, Address, And Setting

Write in **first person** by default. Do not use real place names; use generic locations such as *nhà tôi, làng tôi, công ty tôi, thành phố tôi đang sống*. Do not use "Hà Nội" or "Sài Gòn" unless the user explicitly requests a real Vietnamese setting.

- Build Vietnamese address forms (`xưng hô`) pair by pair. Consider relative age, kinship/rank, power, intimacy, public/private context, and current emotion. Kinship labels often anchor family relations in narration; names are natural in dialogue when needed for clarity, contrast, or a relationship temperature shift.
- Default names: Chinese-style Sino-Vietnamese names (`tên phong cách Trung Quốc/Hán-Việt`) with common Chinese surnames and preferably two-syllable given names, e.g. the structure of *Lâm Vân Khê, Cố Thừa Ngôn*. Keep Vietnamese address forms; do not import `ta-ngươi` into modern stories. Use natural Vietnamese names only when the user asks for a Vietnamese setting. The naming system must match the story world. Never copy sample names from the skill into the actual story.
- Ear clarity beats anti-repetition. Use name, relation, title, pronoun, or omitted subject according to point of view. In scenes with multiple people, repeat names/roles when a pronoun could be ambiguous.
- A change in address form is a relationship beat: *anh-em -> tôi-anh*, given name -> title, intimate -> distant only after an action/emotion makes the shift meaningful.
- For pair maps, default naming, ambiguous pronouns, and audio-first examples, read [references/xung-ho-dat-ten.md](references/xung-ho-dat-ten.md).

### 2. Firm Modern Prose, Not Sentimental Prose

Default style: fewer words, clean sentences, concrete details, emotion revealed through action. Sentimentality (`sến`) kills appeal faster than a weak plot.

- Cut rather than decorate. Every description must push plot, curiosity, tension, character, or consequence. If it exists only to sound beautiful or sad, delete it.
- Avoid stale emotional metaphors: no *tim tan vỡ, lệ rơi như mưa, đau như dao cứa, thế giới sụp đổ*. Prefer dry concrete behavior: *"Tôi đặt bát cơm xuống. Không ăn nữa."*
- Do not whine or over-explain grief. Modern characters often swallow feeling; one small action should let listeners feel it themselves.
- One precise detail is better than three pretty details. Reduce adjectives/adverbs; keep strong nouns and verbs.
- Test every sentence that sounds like `bolero` melodrama. If it could be pasted into ten other stories unchanged, make it specific.

Vietnamese calibration examples must stay Vietnamese:

> *"Nước mắt tuôn như mưa, tim tan nát"* -> *"Tôi không khóc. Tôi chỉ thấy tay mình lạnh."*
>
> *"Ánh mắt trìu mến vô bờ"* -> *"Anh nhìn tôi lâu hơn bình thường đúng một giây."*

### 3. Narrator-Led By Default, Dialogue As Impact

For single-voice audio/TTS stories, use the narrator as the spine: summarize routine exchanges, connect choice to consequence, guide psychology, and push plot. Direct dialogue is scarce. A scene does not need dialogue unless the exact wording matters. If the user asks for audio drama, scripted dialogue, or multiple actors, treat that as a different mode, but still require every line to function.

- Keep direct speech only when the wording itself performs an action (confession, refusal, command, threat, promise), shifts power/relationship, reveals voice or subtext, lands a joke/twist/emotional beat, or cannot be paraphrased without losing force.
- Compress procedural communication: greetings, logistics, repeated arguments, known information, and plot explanation should become narration or be cut. Do not narrate an idea and then make a character repeat it.
- Narrate psychology as a process: what the character notices -> how they interpret/misinterpret it -> what they want -> what they choose. Avoid repeating labels like *tôi buồn, tôi sốc, tôi tức*.
- Vary narrative distance: summary, one concrete detail, a line of inner logic, a staged moment, then a strong line of dialogue with immediate consequence. Do not turn the whole story into a flat event report, and do not stage long exchanges when power, information, or decision does not change.
- For dialogue selection, narrative distance, and editing examples, read [references/ky-thuat-chi-tiet.md](references/ky-thuat-chi-tiet.md#10-narrative-voice-dialogue-and-subtext).

## Mandatory Workflow For Story Creation

Do not start drafting the story immediately. Run these steps in order.

### Step 0: Research And Propose Ideas

Before writing any story prose, first: (1) research current motifs/topics for the requested genre, (2) distill them into **3-5 clearly different ideas**; each idea must include a hook/title, a 1-2 sentence logline, and a twist/angle, (3) present the numbered list and **stop for the user to choose**.

Exception: the user already gave a sufficiently specific premise/plot, or explicitly authorized the agent to choose and proceed. In that case, briefly state the chosen direction and continue. Genre/premise skills may not use themselves as an excuse to skip this gate when the brief is still open.

Read [references/tim-y-tuong.md](references/tim-y-tuong.md) for the research method, output format, and fallback when web access is unavailable.

### Step 1: Central Question

Lock one central question that listeners want answered from the first minute and that is fully paid off at the end. It must include personal stakes: who loses what, not just what information is missing.

### Step 2: Opening Selection Gate

Before writing the real story, choose the opening type with the user. Use [references/mo-dau.md](references/mo-dau.md) to select the 3-4 best opening techniques from the 10-type menu, then draft **3-4 short opening options**, each using a different technique and each providing transformation, minimal anchor, specific gap, and movement. Label each technique, present the options, and **stop for the user to choose**.

Exception: the user already gave a concrete opening line/paragraph, or explicitly authorized the agent to choose and continue. When choosing under authorization, briefly note the technique/reason outside the story file, then proceed.

### Step 3: Expectation And Causality Map

Before drafting, outline the central question/goal, required subloops, where loops open/progress/close, the choice -> consequence chain, information/emotional/power rewards, and setup for twists. Do not impose fixed numbers of loops or reversals.

### Step 4: Draft

Draft using the 10 core techniques summarized below. Expand the user-approved Step 2 opening into the actual opening of the story.

### Step 5: Self-Check

Run the checklist below and self-repair before returning or saving.

### Step 6: Mandatory Final Polish

After completing the draft and the base/genre/premise checklists, use `audio-story-final-polish` to repair causality, motivation, plot depth, emotional reaction, dialogue, Vietnamese address forms, pronouns, and read-aloud rhythm. Keep the narrator as the spine; do not add extra back-and-forth just to make scenes "lively." This must be the final content pass. If any story content changes afterward, run `audio-story-final-polish` again from the beginning.

### Step 7: Save The Script

Save complete scripts under `/Users/truongdv/Documents/projects/video-audio/kich-ban/` in the folder for the main genre: `drama/`, `trinh-tham/`, `kinh-di/`, `tinh-cam/`, or `hai-huoc/`. Hybrid stories go under the main genre. Premises such as `xuyên sách`, `hệ thống`, `trùng sinh`, or `truyện rác` do not get their own folders.

- File name: `ten-viet-thuong-khong-dau.md`, words separated by hyphens, e.g. `chong-toi-ngoai-tinh.md`.
- The saved file must contain **pure story only**: start with the first hook sentence and end with the final story sentence. Do not include title headings, metadata, genre/POV/word-count notes, read-aloud instructions, `---`/`***` act separators, `[SFX]`/`[BGM]`, or chapter labels unless the user explicitly requests production cues. Put production notes, if any, in a separate response or file.

## 10 Core Techniques

This is the quick operating version. For examples, edge cases, and deeper tables, read [references/ky-thuat-chi-tiet.md](references/ky-thuat-chi-tiet.md).

1. **Hook and promise.** Open with a concrete change, enough anchor for listeners to know what they are missing, and a push into action. Match the title; do not use false hooks or shock stacking. For opening menus and transmigration/reincarnation openings, read [references/mo-dau.md](references/mo-dau.md).
2. **Open loops.** Each loop needs a specific question/goal, a reason to care, progress path, and intended closure. Use loop count according to length. Provide real progress instead of endless interruption.
3. **Variable rewards.** Vary reward type: information, capability, emotion, power reversal, confirmation, or fair surprise. Rewards must be earned through choice, investigation, or tradeoff.
4. **Immersive detail.** Choose senses and reactions according to what the character wants/notices. Prefer action that shows emotion. Do not replace every feeling with a stock body symptom.
5. **Audio pacing.** Each scene needs goal -> obstacle -> turn. Control pace through events, narrative distance, sentence rhythm, dialogue turns, and information load. Read aloud.
6. **Setup-payoff and "Aha!".** Design backward from payoff to required clues. Surprise must be hard to predict but explainable in retrospect, and it must change decision/relationship, not merely provide trivia.
7. **Emotional investment.** Give characters specific wants, inner conflict, agency, and individual detail. Understand antagonist motives without excusing responsibility.
8. **Escalation and release.** Increase cost, proximity, deadline, irreversibility, or relationship pressure. Quiet scenes must still create consequence, alliance shifts, clues, or decisions.
9. **Sound as information** when production layers are requested. Use sound to locate, signal change, or create motif. In pure narrated stories, write sound into action; do not add SFX/BGM tags unless requested.
10. **Narrative voice and dialogue.** Let the narrator summarize, guide psychology, connect causality, and shift distance. Keep direct dialogue only when the exact words must be heard.

## Segments And Length

- Every segment must create a meaningful change: an obstructed goal, a character choice, changed information/power/relationship, and a consequence that pushes the next section.
- Every episode must have its own emotional arc in addition to any cliffhanger.
- If the user does not specify length, ask briefly whether it is one episode or multiple episodes and approximate duration. Compact serial episodes often run around 1,200-2,500 Vietnamese words, roughly 5-15 minutes at 130-160 Vietnamese words/minute. Judge by the ear, not by the page.

## Ending Design

Fully answer the Central Question at minimum. A final twist must pay off prior foreshadowing, not introduce a brand-new cheat. Justice/causality may be morally uneven, but the price must match what characters did and lost. End with a callback that now means something different. The final sentence should leave resonance, not a moral lesson. A sequel seed is allowed only if it opens a new loop; do not leave the old debt unpaid.

## Fatal Engagement Problems

Do not use: character-profile openings; info-dumps; ambiguous pronouns; passive protagonists; events with no causality; unsetup twists; hiding information the narrator would obviously know; one-note cliffhangers; flat rhythm; unreadable sentences; unpaid endings; repetitive inner conclusions; dialogue explaining what both people know; long exchanges where power/information/decision does not change; narration followed by dialogue repeating the same idea; flat event-report narration; one-note emotional tone; sentimental/flowery cliche (`sến`); description only for beauty; feeling pain on behalf of the listener; wrong Vietnamese address forms; naming systems that mismatch setting; mechanical label rotation.

## Safety And Sensitive Content

There is no reliable "unsafe word -> safe synonym" table. Judge the whole scene by context, focus, tone, realism, graphic detail, and imitability. Keep events clear but move weight toward choice and consequence. Remove methods, instructions, romanticization, and shock-only details. Review title, thumbnail, captions, and audio as well. Use extra caution for self-harm, sexual violence, and minors. Read [references/an-toan-tu-vung.md](references/an-toan-tu-vung.md) for risk levels, the 7-step editing process, before/after examples, and current policy sources.

## Self-Check Before Returning

- [ ] **Style:** no sentimental/cliche/bolero lines; no stale metaphors; firm concise prose; every description works?
- [ ] **Address forms:** every pair fits age/rank/power/emotion? Naming system matches the story world? Pronouns are clear in one listen? Address shifts are motivated?
- [ ] **Opening:** Step 2 gate completed or explicitly waived? It matches the title and has transformation + anchor + specific gap + movement?
- [ ] Open loops progress and close appropriately for the length?
- [ ] Major twists have enough setup without spotlighting?
- [ ] Emotion appears through detail/action/choice, not stock symptom lists?
- [ ] Conflict escalates on at least one meaningful axis? Quiet scenes still work?
- [ ] Characters have specific wants, inner conflict, and active decisions? Consequences come from choices?
- [ ] **Narration/dialogue:** narrator is the spine and shifts distance; every remaining direct line needs to be heard verbatim and creates action/relationship/subtext/payoff?
- [ ] Emotional tone varies when the story needs it? Callback, if used, changes meaning?
- [ ] Read aloud: natural flow and no breathless lines? Central Question fully answered at the end?
- [ ] **Safety:** sensitive scenes have function and avoid instruction/graphic detail/romanticization? Context, focus, title, captions, visuals, and sound have been reviewed?

When a concrete genre is present, keep this base framework and also use the matching `audio-story-genre-*` skill. Do not ask the user about technical craft details; apply them yourself. Ask only when essential creative information is missing, such as length or one-episode vs multi-episode.
