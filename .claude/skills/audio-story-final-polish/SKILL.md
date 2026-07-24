---
name: audio-story-final-polish
description: Mandatory final editorial pass for every completed Vietnamese audio story or story script. Use after the agent has drafted, rewritten, expanded, completed, or revised a story, even if the user did not ask for "polish" or name the skill. Repair stiff prose, disconnected causality, thin plotting, weak motivation, flat emotional response, awkward dialogue, ambiguous pronouns, Vietnamese address forms (`xưng hô`) that do not fit the relationship, and VoxCPM/TTS-unfriendly punctuation, dialogue turns, or spoken-token forms. If any story content changes after this pass, run it again from the beginning. Do not use this skill as a substitute for the base writing skill or genre skills.
---

# Audio Story Final Polish

Turn a draft that already has a plot into a coherent Vietnamese audio story with believable human reactions, natural read-aloud flow, and clean VoxCPM/TTS pause structure. Run this after all other story-writing skills. Edit the manuscript itself; do not insert editorial comments into the story content.

Follow the shared coordination contract in [../audio-story-engagement/references/phoi-hop-skills.md](../audio-story-engagement/references/phoi-hop-skills.md): preserve the user's request, main genre, premise, approved ending, and approved intent. Final polish fixes execution problems; it must not add genre quotas, change the premise, or replace the chosen ending.

Use [../audio-story-engagement/references/van-xuoi-chuyen-nghiep.md](../audio-story-engagement/references/van-xuoi-chuyen-nghiep.md) as the professional-prose gate. A polished draft must not merely satisfy visible craft checklists; it must show earned knowledge, scene-specific selection, imperfect human contact, and freedom from skill-example residue.

## Required Pass Order

Run these passes in order. Do not polish sentences before the event chain and motivations stand, because smooth prose cannot rescue an illogical scene.

### 1. Lock Intent And Build The Story Ledger

Outside the story text, record the facts that must not drift: premise, point of view, narrative voice, approved ending, world rules, and user-specific requirements.

Create four short ledgers:

- **Time:** event, moment, elapsed time, ages/pregnancy/deadlines when relevant.
- **Knowledge:** in each scene, what each character knows, from where, and what they cannot yet know.
- **Relationships:** each pair's relative age/rank, status, intimacy, conflict, and current Vietnamese address pair.
- **Evidence/promises:** planted details, who holds them, when they pay off, and how.
- **Semantic clarity:** stable noun/role for each easily confused person, object, interface, message, mechanism, and rule; first-use method for premise-critical actions; prior premise required by consequential connectors; target, scene-specific criterion, and evidence for abstract evaluations or narrator meta-commentary.
- **Audio/TTS:** names, numbers, dates, times, acronyms, raw symbols, dense paragraphs, and dialogue-heavy scenes that need special pause or pronunciation attention.

Preserve intentional roughness and distinct voice. Do not turn every character into the same "beautiful prose" voice.

### 2. Repair Disconnection With Causality

Before smoothing scene links, run the one-listen semantic-clarity gate in [../audio-story-engagement/references/ro-rang-mot-luot-nghe.md](../audio-story-engagement/references/ro-rang-mot-luot-nghe.md):

1. Replace every `nó`, `họ`, `người đó`, `việc ấy`, `chuyện này`, and comparable pointer aloud with its intended noun. If there is no single established answer, repair the referent.
2. Expand `chỉ là`, `nhưng`, `vì vậy`, `vẫn`, `cũng`, `lại`, `nữa`, `mỗi lần`, and `lần này` into the prior statement/cause/state/occurrence they require. If that premise exists only in the outline, add the smallest necessary setup or remove the false connector.
3. For each premise-critical verb such as write, hear, see, activate, delete, alter, or control, verify that the first occurrence states a usable method and that later occurrences obey it.
4. Separate valid reader inference from missing information. Emotion and motive may be implied; basic identity, action, geography, mechanism, causality, and evidence scope may not be delegated to the listener.
5. For every narrator judgment such as `an toàn`, `có đời sống`, `chân thật`, `có trọng lượng`, `có chiều sâu`, `đủ thật`, or `có ý nghĩa`, state its **target, criterion in this scene, and audible evidence or consequence**. If two are missing, unpack the judgment into a concrete failure, contrast, behavior, or consequence, or cut it.

Do not accept a sentence merely because its grammar is legal or because the intended meaning can be reconstructed after rereading. If a cold listener asks `nó là gì?`, `ai vừa làm việc đó?`, `chỉ là so với điều gì?`, `an toàn khỏi điều gì?`, or `có đời sống nghĩa là sao?`, the pass has failed.

Summarize each scene in one line:

```text
trigger -> character decision -> action -> consequence -> new state
```

For every two adjacent events, ask:

1. Does the later event happen **because of** the earlier event, or merely **after** it?
2. If the earlier event is removed, would the later event still happen unchanged?
3. Who made a choice that pushed the story to this step?

If two scenes merely sit next to each other, add the missing cause, reaction, or decision. Cut or merge scenes that create no change. Coincidence may create trouble; it must not solve trouble.

Check timeline errors, evidence that appears from nowhere, characters knowing information before receiving it, changing world rules, and forgotten consequences. For `xuyên sách`, `trùng sinh`, or `hệ thống`, audit what the character knows, cannot know, remembers accurately, and pays for knowing in advance.

For each decisive piece of evidence, verify its source, named person/sample/object, chain of custody, time-to-result, and exact scope of proof. "Suspicious" is not the same as "proves the mastermind."

### 3. Deepen Plot Through Choice And Cost

Every important scene must earn its place, but it need not display a complete `goal -> obstacle -> tactic -> turn` machine. A scene may earn its place through a consequential choice, changed relationship, gained or lost information, accumulating pressure, necessary absorption, comic escalation, atmosphere, or a precise change in what the listener understands. Do not manufacture resistance, tactics, or a miniature twist merely to fill a scene template.

Turn motivation explanation into evidence inside scenes: an action, an avoidance, a costly decision, or a contradiction between words and behavior. Important clues should be found, forced, traded for, or paid for by characters, not delivered by a helper, phone call, or document at the perfect moment.

At the climax, let the opponent react according to established competence. Victory must come from the protagonist's choices and preparation, and it should leave loss, responsibility, or a relationship that cannot simply reset.

Also diagnose amplitude. If the draft reads uniformly even — competent everywhere, peaked nowhere — the defect is structural, not stylistic: no scene passes the base skill's retell test, threads resolve separately instead of converging, or the peak scene cuts away right after its first impact. More sentence polish will only flatten such a draft further. Restage and expand the existing peak within the approved events (more room, consequences on-screen, threads converging in one scene); if the approved structure contains no peak at all, report it to the user instead of inventing new plot.

### 4. Repair Emotional Flatness With Rooted Reaction

For each major emotional turn, identify privately what the character fears losing, what they want to hide, and what the event means to them. Then choose among direct naming, thought, necessary behavior, silence, delayed reaction, later consequence, or no added sentence. If a concrete detail remains, require it to arise from the scene rather than serving as automatic bodily proof.

Do not equate "showing" with stuffing in shaking hands, breathlessness, heartbeat, and tears. Choose a reaction specific to the character, situation, and history. Direct emotional naming is allowed when it compresses time; avoid both performing and explaining the same emotion.

After major events, give enough absorption time for reactions and decisions to be credible. You may compress or skip the middle beat when character, genre, and circumstance justify it; do not jump from shock to perfect plan simply because the plot needs speed.

### 5. Naturalize Dialogue And Vietnamese Address Forms

Before an important conversation, note privately what each participant wants, avoids, misunderstands, or cannot yet say. Judge the exchange as a whole, not every line as a tactical move. Individual lines may be partial, clumsy, unanswered, merely practical, or attempts that fail; that friction is often where human speech lives. Cut routine material only when it adds neither relationship, rhythm, orientation, nor pressure.

State each speaker's plain intention and formulation limit before preserving any marked comparison. Then run the mandatory [human semantic-fit and natural-dialogue gate](../audio-story-engagement/references/ngon-ngu-con-nguoi.md) on every high-impact exchange. Reject dialogue optimized for quoteability, a profession mechanically turned into emotional vocabulary, object/system verbs that flatten people or relationships, and one speaker's metaphor followed by the other's perfect metaphorical comeback.

Let words and actions diverge when there is subtext. Add action beats only when they change the meaning of a line or clarify who is speaking; do not attach decorative gestures to every line. Read dialogue aloud and rewrite lines that the character could not plausibly say in one breath.

Use the relationship ledger to check every address pair:

- Self-reference and address must fit age, rank, status, intimacy, and public/private context.
- A shift from `anh/em` to `tôi/cô`, bare-name address, or `nó/hắn` must have visible emotional or power cause in the scene.
- Pronouns must have clear audible antecedents. If `nó`, `anh ấy`, `cô ta`, or `người đó` could refer to more than one target, repeat a relation, name, or title.
- Do not use `nó` for a person merely to avoid repetition unless the contempt/coldness fits the point of view.
- Follow the base skill's naming and address rules. For complex casts, read [../audio-story-engagement/references/xung-ho-dat-ten.md](../audio-story-engagement/references/xung-ho-dat-ten.md).

### 6. Prepare VoxCPM/TTS Pauses And Spoken Tokens

Run this as an audio-production readiness pass, but keep the story file pure prose unless the user requested production cues. For detailed rules and examples, read [../audio-story-engagement/references/voxcpm-tts-ngat-nghi.md](../audio-story-engagement/references/voxcpm-tts-ngat-nghi.md).

- Check punctuation as pause structure: comma for short breath, period for full thought, question mark for true question intonation, exclamation mark only when the energy is earned, and ellipsis only for trailing/hesitation.
- Split overpacked sentences, especially those with multiple time layers, several pronouns, or many comma-separated clauses. Preserve voice; do not chop every sentence into identical fragments.
- Treat paragraph breaks as audible resets. Use them for speaker turns, thought turns, scene/time shifts, and emotional landings; do not bury a reveal in the middle of a dense paragraph.
- In dialogue, keep one speaker turn per paragraph when speakers alternate. Do not leave rapid-fire quotes from different speakers in one paragraph.
- Replace pause-by-decoration with meaning: instead of relying on dashes, repeated ellipses, or `[pause]`, use a sentence break, paragraph break, or action beat that carries subtext.
- Check consecutive sentences that open with the same words. On the page this is anaphora; in audio each sentence tends to land in its own chunk after a prosodic reset, so identical openings are heard as the synthesizer stuttering. Decide whether the repetition is doing work, then keep the anchor phrase and vary how each sentence reaches it, rather than deleting the device. See `references/diagnosis-and-repair.md`, "Consecutive Sentences Open With The Same Words".
- Rewrite important numbers, dates, times, percentages, money, account/phone/legal codes, acronyms, symbols, and foreign terms into the form that should be heard. If the exact written token must remain for production, note it outside the story as a render concern.
- Sweep the manuscript for English-origin words, brand/platform names, acronyms, and stylized teencode left as bare Latin strings (`inbox`, `deal`, `crush`, `flex`, `red flag`, `livestream`, `OK`, `email`). VoxCPM has no Vietnamese lexicon for these, so they get spelled out, guessed, or swallowed and the chunk timing drifts. Replace each one with either a Vietnamese phonetic respelling that is recognizable by ear (`inbox` -> `in bốc`, `livestream` -> `lai sờ trim`, `TikTok` -> `tích tóc`) or a plain Vietnamese equivalent (`inbox` -> `nhắn tin riêng`, `deal` -> `giá hời`). Keep one form per term across the whole story. Where a joke depends on the original sound (`gét gô`, `sít rịt`), the phonetic spelling is already correct — keep it and check that a nearby line anchors the meaning by ear. See the "English, Teencode, And Trend Tokens" section of the reference below.
- Check that no SSML, `[pause]`, SFX/BGM, heading, separator, or note slipped into a pure story file unless the user explicitly requested those cues.

### 7. Remove Stiff Prose And Formula Marks

Edit by idea unit, not by swapping synonyms:

- Let each sentence carry one main action or image. Split chains of clauses that make listeners forget the subject.
- Put the subject near the verb. Replace ambiguous, missing-antecedent, or role-switching pronouns with the right noun/relation. Do not rotate several nearby entities into one vague `nó`.
- Remove connectors that counterfeit missing context. `Chỉ là`, `vì vậy`, `lại`, `vẫn`, `cũng`, `lần này`, and `sau mỗi lần` must point to a statement, cause, state, or occurrence the listener has actually heard.
- Cut sentences that explain what listeners just understood, moral summaries, and empty foreshadowing like "everything had only just begun." This includes **reveal re-derivation**: restating a fresh reveal in two or three escalating paraphrases before a button line. Keep one processing beat, cut the rest.
- Cut false-profundity reflection. Treat it as a **class of sentence, not a list of phrases**, and apply the check to every reflective or closing sentence, not only scene endings: any line that reaches for depth through abstraction, paradox, or negation instead of a concrete person, object, or action, so it lands as `khó hiểu và rời rạc` on one listen. One-listen test — (a) is the referent concrete, not `một người` / `một điều gì đó` / `cách duy nhất` / `con số của chính mình` / `một ngăn không tên`; (b) does it parse on first hearing, with no unresolved paradox like `giữ một người đã không còn ở lại`; (c) does it add something rather than restate what the scene already showed. Fail two and it is the defect. Repair by naming the concrete referent, keeping the action or image, and deleting the gloss — never by rephrasing one abstraction into a prettier one; if nothing concrete remains, end the paragraph one sentence earlier. See `references/diagnosis-and-repair.md`, "False-Profundity Abstract Closer", for the one-listen test and the full shape family (vague referent, paradox, negation-as-depth, singularity gloss, mind-ledger, `nạn nhân của...`).
- Cut or unpack unexplained abstract evaluation and narrator meta-commentary, including mid-scene lines. For `an toàn`, `có đời sống`, `chân thật`, `có trọng lượng`, `có chiều sâu`, `đủ thật`, or similar language, demand three answers: **what exact target is judged, what the label means here, and what audible detail or consequence proves it**. Fail two and rewrite the judgment as the concrete defect, behavior, contrast, or result. Example: `Câu ấy đúng ngữ pháp, an toàn và không có chút đời sống nào` is not rescued by smoother adjectives; say what it hides: `Câu đó không sai, nhưng nghe như một bản thông cáo. Nó không cho khán giả biết hai người đã sống với nhau ra sao hay vì sao phải ly hôn.` See `references/diagnosis-and-repair.md`, "Abstract Evaluation Without Concrete Meaning".
- Scan repeated templates such as `Tôi không... Không phải vì... Mà vì...`, `Tôi biết... nhưng tôi không biết...`, `Điều tôi không ngờ là...`, hindsight interjections (`Tôi đâu biết...`, `Mãi về sau tôi mới hiểu...`, `Đó là sai lầm đầu tiên...`), three-part balanced declarations, and scenes ending with a slogan. Do not ban them absolutely; keep only when voice and function justify them, with a hindsight interjection surviving at most once per story. The defect to hunt is **allusive posturing** — any foreshadow, hindsight or not, that gestures at future irony through an abstract riddle instead of naming the concrete stake in the narrator's own texture: `Tôi đâu biết mình vừa đặt cược bằng đúng cái thứ mình sắp thua` forces the listener to decode `cái thứ`. Repair by rewriting toward the concrete stake, not by default deletion: `Tôi tự tin tới mức đã bắt đầu nghĩ xem nên gọi vị trà sữa nào trước` (the state shown as a concrete comic action, no hindsight needed) or `Tôi không hề biết một tháng trà sữa của mình đã bắt đầu đếm ngược từ đó` (hindsight kept, stake named). Cut the line only when no concrete version earns its place.
- Map the last sentence of every scene and major paragraph. If more than roughly one in three closes on an aphorism, thesis, balanced antithesis, or punchy fragment triple, rewrite most of them to end on action, speech, plain fact, or an unfinished thought. Uniformly clever closure is an audible machine signature even when each individual closer is good.
- Replace abstractions with actions or concrete consequences. Avoid lines that could be pasted into ten other stories.
- Do not assume concrete is automatically natural. Check Vietnamese collocation and category fit: if a line treats a person, marriage, memory, or moral choice as a broken object, machine, account, case file, or interface, demand an exact character-owned mapping and scene purpose. Otherwise name the human behavior or consequence directly.
- Track metaphor ownership across adjacent turns. A comparison plausible in private thought or retrospective narration may be implausibly polished in live speech; another character must not inherit the same field merely to deliver a rebuttal.
- Audit earned insight. Separate what a character observed, what they may reasonably infer, what repeated contact could establish as a pattern, and what only later proof or intimacy could justify as truth. Rewrite instant diagnoses of a stranger's deepest habit as limited observations, guesses, questions, or later-earned conclusions.
- Treat every example in every skill as contaminated source material. Remove copied or lightly disguised objects, gestures, occupations, image fields, sentence shells, and emotional choreography. Repair with consequences generated by this scene's place, task, history, and pressure—not a synonym or a replacement stock prop.
- Run the object-presence test on conspicuous domestic actions and handheld props: if removing the object leaves meaning, causality, and blocking unchanged, the action is probably decorative choreography. Delete it or replace it with behavior the situation itself requires. Do not use bowls, chopsticks, cups, phones, sleeves, keys, doors, papers, or tidying motions as automatic proof of interior life.
- Look for visible checklist prose: every scene announcing a realization, every exchange ending in a polished counter-line, every paragraph closing with a thesis, or every emotional turn receiving a symbolic object beat. Vary or remove the machinery; some scenes should simply act, miss, wait, misunderstand, or carry residue forward.
- Remove guardrail leakage: sentences that explain the narrator is not mind-reading, that a profession does not grant universal insight, that a detail is only an inference, or that the prose is avoiding a cliché. Enforce the limit through what is and is not claimed; do not narrate compliance with a skill.
- Scrutinize `lần đầu tiên`, `lần này`, and `chỉ khác là` when they announce a changed routine or delayed reply near a scene/episode ending. Delete the label and see whether the actual behavior already carries the change. Keep it only when temporal firstness itself matters, not as an arc certificate.
- Trim trailing evaluative tails. When most action sentences drag a commentary clause (`, khiến tôi...`, `, như thể...`, `, để lại trong tôi...`), keep the few that genuinely change meaning and let the other actions stand bare; the accumulation, not any single tail, is the defect.
- Keep rhythm varied: short sentences for impact, medium sentences for processing, longer sentences for layered observation. Do not chop everything into identical fragments. Vary paragraph length too — a run of same-length paragraphs reads as machine cadence even when each is individually clean.

If the draft is in a file, run the surface-audit helper after semantic edits:

```bash
python3 <skill-dir>/scripts/audit_story.py /path/to/story.md
```

`<skill-dir>` is the folder containing this `SKILL.md`; in this project it may be `.agents/skills/audio-story-final-polish` or the `.claude` mirror. Do not assume the current working directory is the skill directory.

The script only flags places to reread. It does not decide that a sentence is wrong and does not replace editorial judgment.

### 8. Read-Aloud Check And Pressure Tests

Read aloud or simulate TTS for the full opening, multi-person scenes, climax, ending, and at least one dialogue-heavy sample if the story has dialogue. Fix places where breath fails, speaker identity blurs, syllables clash, raw tokens misread, or pronouns lose antecedents.

Run twelve final tests:

1. **Referents:** every pronoun/pointer has one audible antecedent of the correct role; names and roles do not silently switch.
2. **Presuppositions:** every contrast, cause, continuation, recurrence, or exception marker has the explicit prior premise it claims.
3. **Causality:** replace "then/after that" in the summary with "therefore/but"; weak links are where that fails.
4. **Knowledge:** every reveal has a valid source and acquisition time.
5. **Evidence:** documents/objects prove the exact conclusion, have source and timing, and can withstand one intelligent objection.
6. **Agency:** if removing the protagonist's decisions leaves the plot nearly unchanged, rewrite the action spine.
7. **Reaction:** reactions fit relationship, damage, and established character.
8. **Address forms:** every address shift reflects a real relationship or tactic shift.
9. **Blind dialogue:** hide speaker tags; most characters remain distinguishable by goal, vocabulary, and rhythm. No pair sounds as though they are co-authoring one polished aphorism, and each marked image belongs to the speaker who uses it.
10. **VoxCPM/TTS:** punctuation, paragraphing, dialogue turns, and spoken-token forms are ready for rendering without avoidable rushed or misread passages. No bare English word, acronym, or stylized teencode token is left for the renderer to guess.
11. **Final sentence:** end on consequence, image, or decision, not an explanation of the theme. If the ending reuses an earlier phrase, object, or habit, its changed meaning is enacted by the situation, never glossed with `có nghĩa là`, `hóa ra`, or `không còn là... mà là...`.
12. **Professional prose:** no instant psychological omniscience, copied skill-example material, stock object choreography, visible beat machinery, guardrail leakage, prefab arc announcement, or compulsory metaphor remains; plain direct language is retained where it is the most exact choice.

## Completion Conditions

Final polish is complete only when no serious issue remains in these gates:

- **Logic gate:** time, knowledge, evidence, and causality do not contradict.
- **Semantic-clarity gate:** every referent is identifiable, every connector has its prerequisite, premise-critical actions have an established method, every abstract evaluation has a named target plus concrete criterion/evidence, and no basic identity/action/geography/mechanism step is outsourced to listener guesswork.
- **Character gate:** turns arise from goals, choices, and cost.
- **Emotion gate:** reactions have roots, not only labels or generic symptoms.
- **Speech gate:** dialogue has purpose; Vietnamese address forms fit relationships; pronouns are audible.
- **Human-language gate:** concrete wording fits its human target; professional/image fields remain optional and speaker-owned; high-impact dialogue passes the plain-paraphrase, mouth, reply, and residue tests; no aphorism tennis remains.
- **Earned-knowledge gate:** observation, inference, pattern, and truth are not collapsed; intimacy and psychological certainty are supported by time, evidence, or prior relationship.
- **Originality gate:** no skill example, stock domestic choreography, prestige sentence shell, or conspicuous device substitutes for scene-specific human behavior.
- **Audio/TTS gate:** sentence breaks, punctuation, paragraph resets, dialogue turns, and spoken-token forms are natural for VoxCPM/TTS.
- **Prose gate:** sentences flow naturally, rhythm varies, and there is no extra explanation or repeated formula.
- **Amplitude gate:** the story has one identifiable peak where planted threads converge with disproportionate room; the draft is not uniformly even from start to finish.

If fixing one gate changes neighboring scenes, return to Pass 1 and rerun the affected passes. Any story-content edit after this skill completes invalidates the "final-polished" state.

## How To Respond

- When the user asked to write or revise a story: update the story directly, keep the file pure story, and report briefly outside the file that final polish was completed.
- When the user only asked for analysis: do not edit the file; list problems by severity, quote/identify the relevant passage, and suggest repairs.
- When fixing logic would require changing the approved premise, ending, or intent: stop with a report and ask the user to decide, because that is no longer intent-preserving polish.

Read [references/diagnosis-and-repair.md](references/diagnosis-and-repair.md) when you need concrete examples for diagnosing and repairing specific problems. Read [references/research-basis.md](references/research-basis.md) when you need the reasoning basis or must adjust the rubric; ordinary use does not require re-reading it every time.
