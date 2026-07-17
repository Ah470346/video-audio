---
name: audio-story-final-polish
description: Mandatory final editorial pass for every completed Vietnamese audio story or story script. Use after the agent has drafted, rewritten, expanded, completed, or revised a story, even if the user did not ask for "polish" or name the skill. Repair stiff prose, disconnected causality, thin plotting, weak motivation, flat emotional response, awkward dialogue, ambiguous pronouns, and Vietnamese address forms (`xưng hô`) that do not fit the relationship. If any story content changes after this pass, run it again from the beginning. Do not use this skill as a substitute for the base writing skill or genre skills.
---

# Audio Story Final Polish

Turn a draft that already has a plot into a coherent Vietnamese audio story with believable human reactions and natural read-aloud flow. Run this after all other story-writing skills. Edit the manuscript itself; do not insert editorial comments into the story content.

Follow the shared coordination contract in [../audio-story-engagement/references/phoi-hop-skills.md](../audio-story-engagement/references/phoi-hop-skills.md): preserve the user's request, main genre, premise, approved ending, and approved intent. Final polish fixes execution problems; it must not add genre quotas, change the premise, or replace the chosen ending.

## Required Pass Order

Run these passes in order. Do not polish sentences before the event chain and motivations stand, because smooth prose cannot rescue an illogical scene.

### 1. Lock Intent And Build The Story Ledger

Outside the story text, record the facts that must not drift: premise, point of view, narrative voice, approved ending, world rules, and user-specific requirements.

Create four short ledgers:

- **Time:** event, moment, elapsed time, ages/pregnancy/deadlines when relevant.
- **Knowledge:** in each scene, what each character knows, from where, and what they cannot yet know.
- **Relationships:** each pair's relative age/rank, status, intimacy, conflict, and current Vietnamese address pair.
- **Evidence/promises:** planted details, who holds them, when they pay off, and how.

Preserve intentional roughness and distinct voice. Do not turn every character into the same "beautiful prose" voice.

### 2. Repair Disconnection With Causality

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

Every important scene needs:

- The character wants a specific thing right now.
- Someone or something blocks that want.
- The character changes tactics or must choose.
- The result changes relationship, information, risk, or goal.

Turn motivation explanation into evidence inside scenes: an action, an avoidance, a costly decision, or a contradiction between words and behavior. Important clues should be found, forced, traded for, or paid for by characters, not delivered by a helper, phone call, or document at the perfect moment.

At the climax, let the opponent react according to established competence. Victory must come from the protagonist's choices and preparation, and it should leave loss, responsibility, or a relationship that cannot simply reset.

### 4. Repair Emotional Flatness With Rooted Reaction

For each turn, identify privately: what the character fears losing, what they want to hide, and where their body/action betrays them. Keep only the strongest concrete detail in the scene.

Do not equate "showing" with stuffing in shaking hands, breathlessness, heartbeat, and tears. Choose a reaction specific to the character, situation, and history. Direct emotional naming is allowed when it compresses time; avoid both performing and explaining the same emotion.

After major events, give enough absorption time for reactions and decisions to be credible. You may compress or skip the middle beat when character, genre, and circumstance justify it; do not jump from shock to perfect plan simply because the plot needs speed.

### 5. Naturalize Dialogue And Vietnamese Address Forms

Before each conversation, note privately for each participant: **what they want from the other person, what they hide, and what tactic they use**. Each line must be a move: probe, delay, pressure, soothe, blame, bargain, conceal, or withdraw. Cut greetings, logistics, and information both people already know unless those create pressure.

Let words and actions diverge when there is subtext. Add action beats only when they change the meaning of a line or clarify who is speaking; do not attach decorative gestures to every line. Read dialogue aloud and rewrite lines that the character could not plausibly say in one breath.

Use the relationship ledger to check every address pair:

- Self-reference and address must fit age, rank, status, intimacy, and public/private context.
- A shift from `anh/em` to `tôi/cô`, bare-name address, or `nó/hắn` must have visible emotional or power cause in the scene.
- Pronouns must have clear audible antecedents. If `nó`, `anh ấy`, `cô ta`, or `người đó` could refer to more than one target, repeat a relation, name, or title.
- Do not use `nó` for a person merely to avoid repetition unless the contempt/coldness fits the point of view.
- Follow the base skill's naming and address rules. For complex casts, read [../audio-story-engagement/references/xung-ho-dat-ten.md](../audio-story-engagement/references/xung-ho-dat-ten.md).

### 6. Remove Stiff Prose And Formula Marks

Edit by idea unit, not by swapping synonyms:

- Let each sentence carry one main action or image. Split chains of clauses that make listeners forget the subject.
- Put the subject near the verb. Replace ambiguous pronouns with the right noun/relation.
- Cut sentences that explain what listeners just understood, moral summaries, and empty foreshadowing like "everything had only just begun."
- Scan repeated templates such as `Tôi không... Không phải vì... Mà vì...`, `Tôi biết... nhưng tôi không biết...`, `Điều tôi không ngờ là...`, three-part balanced declarations, and scenes ending with a slogan. Do not ban them absolutely; keep only when voice and function justify them.
- Replace abstractions with actions or concrete consequences. Avoid lines that could be pasted into ten other stories.
- Keep rhythm varied: short sentences for impact, medium sentences for processing, longer sentences for layered observation. Do not chop everything into identical fragments.

If the draft is in a file, run the surface-audit helper after semantic edits:

```bash
python3 <skill-dir>/scripts/audit_story.py /path/to/story.md
```

`<skill-dir>` is the folder containing this `SKILL.md`; in this project it may be `.agents/skills/audio-story-final-polish` or the `.claude` mirror. Do not assume the current working directory is the skill directory.

The script only flags places to reread. It does not decide that a sentence is wrong and does not replace editorial judgment.

### 7. Read-Aloud Check And Pressure Tests

Read aloud or simulate TTS for the full opening, multi-person scenes, climax, and ending. Fix places where breath fails, speaker identity blurs, syllables clash, or pronouns lose antecedents.

Run eight final tests:

1. **Causality:** replace "then/after that" in the summary with "therefore/but"; weak links are where that fails.
2. **Knowledge:** every reveal has a valid source and acquisition time.
3. **Evidence:** documents/objects prove the exact conclusion, have source and timing, and can withstand one intelligent objection.
4. **Agency:** if removing the protagonist's decisions leaves the plot nearly unchanged, rewrite the action spine.
5. **Reaction:** reactions fit relationship, damage, and established character.
6. **Address forms:** every address shift reflects a real relationship or tactic shift.
7. **Blind dialogue:** hide speaker tags; most characters remain distinguishable by goal, vocabulary, and rhythm.
8. **Final sentence:** end on consequence, image, or decision, not an explanation of the theme.

## Completion Conditions

Final polish is complete only when no serious issue remains in these gates:

- **Logic gate:** time, knowledge, evidence, and causality do not contradict.
- **Character gate:** turns arise from goals, choices, and cost.
- **Emotion gate:** reactions have roots, not only labels or generic symptoms.
- **Speech gate:** dialogue has purpose; Vietnamese address forms fit relationships; pronouns are audible.
- **Prose gate:** sentences flow naturally, rhythm varies, and there is no extra explanation or repeated formula.

If fixing one gate changes neighboring scenes, return to Pass 1 and rerun the affected passes. Any story-content edit after this skill completes invalidates the "final-polished" state.

## How To Respond

- When the user asked to write or revise a story: update the story directly, keep the file pure story, and report briefly outside the file that final polish was completed.
- When the user only asked for analysis: do not edit the file; list problems by severity, quote/identify the relevant passage, and suggest repairs.
- When fixing logic would require changing the approved premise, ending, or intent: stop with a report and ask the user to decide, because that is no longer intent-preserving polish.

Read [references/diagnosis-and-repair.md](references/diagnosis-and-repair.md) when you need concrete examples for diagnosing and repairing specific problems. Read [references/research-basis.md](references/research-basis.md) when you need the reasoning basis or must adjust the rubric; ordinary use does not require re-reading it every time.
