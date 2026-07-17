# Coordination Contract For Audio Story Skills

This is the shared priority source when multiple audio-story skills trigger. The goal is for each skill to do one job without stacking conflicting formulas.

## 1. Four Layers And Scope

### Layer 1: Base — `audio-story-engagement`

Responsible for:

- idea and opening approval workflow;
- central question, causality, narrative reward;
- narrator-led default, criteria for direct dialogue, and one-listen clarity;
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

Runs last to repair logic, motivation, emotion, dialogue, address forms, and read-aloud rhythm. It:

- must not change main genre, premise, approved ending, or approved intent;
- must not replace the narrator-led base default with dense dialogue unless the user requested audio drama / dialogue-heavy mode;
- must not add missing quotas or techniques for their own sake;
- must report to the user if fixing logic requires changing an approved creative decision.

## 2. Priority Order When Instructions Conflict

Apply from top to bottom:

1. **Safety, truthfulness, and non-contradictory logic.** No creative request, genre, or premise can loosen harmful guidance, misrepresent real people, or break established world rules. If logic requires changing an approved idea, report instead of silently changing it.
2. **The user's latest direct requirement inside those boundaries.** Example: third person, sad ending, no twist, or "choose and proceed" overrides defaults that it directly addresses.
3. **User-approved premise, ending, and promise.** Do not silently change these while polishing.
4. **Base workflow and output contract.** Genre/premise cannot skip approval gates or add metadata to pure story files.
5. **Active premise mechanism rules.** Only rules established in the story count.
6. **Main genre.** Controls emotional question and primary payoff.
7. **Secondary genres.** Add scenes, tone, or techniques without stealing payoff.
8. **Tips, numbers, title patterns, examples.** These are suggestions, not laws.

When two same-level instructions conflict, choose the one that best serves **approved promise + causal chain + one-listen clarity**. Record the choice in the story map; do not try to satisfy both.

## 3. Unified Workflow

1. **Identify layers:** base always applies; choose main genre; add secondary genre or premise only when triggered.
2. **Step 0:** research/propose ideas through the base workflow. Each idea states main genre, premise, and payoff type. If the user already gave a concrete premise or gave authority to proceed, record the choice and do not stop.
3. **Lock the contract:** central question, target emotion, listener reward, world rules, and things the user does not want.
4. **Step 2:** propose different openings through the base workflow. Genre/premise helps generate options but cannot skip the gate or force one type. If the user gave an opening or authority to choose, choose with a reason and continue.
5. **Map:** base choice-consequence chain + genre scene engine + premise law/knowledge ledger.
6. **Write:** prioritize story, not visible technique labels.
7. **Self-check:** run base, main genre, and premise checks. For secondary genres, check only promises actually used.
8. **Final polish:** after a complete story draft exists, run full `audio-story-final-polish`. If story content changes afterward, rerun it. For premise contracts, outlines, or opening options, use relevant checks only; do not claim the whole story is final-polished.
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
- [ ] No genre/premise skipped approval gates unless the brief or user authority explicitly allowed it?
- [ ] No numeric/minute/percentage quota is treated as law without user/channel data?
- [ ] Genre, premise, and final polish preserve narrator-led default and selective dialogue?
- [ ] When instructions conflicted, the priority table decided instead of combining incompatible demands?
- [ ] Safety and causality were not loosened by genre/premise?
- [ ] Final polish ran last and preserved approved intent?
