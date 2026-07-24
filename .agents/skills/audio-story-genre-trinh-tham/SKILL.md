---
name: audio-story-genre-trinh-tham
description: |
  Specialist skill for MYSTERY/DETECTIVE fiction (`trinh tham`): whodunit, missing person, family mystery, cozy mystery, procedural, howdunit/whydunit, and mystery-thriller. Always use with `audio-story-engagement`; add premise modifiers when relevant. Trigger when the main reward is a solution inferred from clues, testimony, evidence, and causal chains, not merely because the story contains crime or secrets.
---

# Audio Story Genre: Mystery

Mystery satisfies when the answer is **surprising forward and reasonable backward**. Listeners do not have to guess correctly, but they must feel that facts, inference rules, and conclusion belong to the same story.

## 1. Coordination Contract

- Use `audio-story-engagement` as the base and follow [../audio-story-engagement/references/phoi-hop-skills.md](../audio-story-engagement/references/phoi-hop-skills.md).
- This skill defines the mystery question, evidence standard, and solution payoff. It does not replace approval gates, safety, Vietnamese address rules, or output format.
- Fair play is required when the story promises a whodunit listeners can solve. In procedural/thriller modes, specialized data may be withheld, but the final solution cannot be created from information that did not exist.
- Do not impose fixed numbers of suspects, red herrings, clues per episode, or percentage points for the culprit's first appearance.
- Run `audio-story-final-polish` last, especially checking timeline, knowledge, and scope of proof.

## 2. Branch And Genre Contract

### Whodunit / Fair-Play Mystery

Promise: listeners receive the necessary facts before reveal and could infer the answer if attentive.

### Whydunit / Howdunit

Identity or action may be clear early; the reward is motive, method, or proof.

### Missing Person / Family Mystery

Investigation changes how characters understand the missing person and family. Often hybridizes with drama.

### Procedural

Satisfaction comes from verification process, cooperation, and professional limits. Research current practice when using agencies, forensics, or law.

### Mystery-Thriller

Solution runs with deadline/danger. Do not let action swallow logic or halt investigation until the culprit attacks.

### Cozy

Lower graphic detail, stronger community and everyday observation. Cozy does not mean easy evidence or naive characters.

### Shared Contract

1. There is an investigable question.
2. Facts change probability or interpretation, not just decoration.
3. Characters build and revise hypotheses.
4. The solution fits timeline, motive, opportunity, and evidence.
5. Reveal changes judgment, relationship, or action, not only names the culprit.

## 3. Central Question

Not every mystery is `WHO + WHY`. Choose the right variable:

- **Who:** who did it / who is behind it?
- **What:** what really happened?
- **How:** by what means inside known limits?
- **Why:** what motive/meaning explains the choice?
- **Where/when:** where/when did the event actually happen?
- **Can it be proved:** truth is known, but can it be proven?

Template:

> *What really happened to [event], and what chain of facts can the character use to prove it before [consequence]?*

Vietnamese examples:

- *Nếu chị tôi tự bỏ đi, vì sao giọng cô vẫn xuất hiện trong các cuộc gọi được ghi sau ngày mất tích?*
- *Tôi biết ai đổi mẫu xét nghiệm; vấn đề là chứng minh thế nào khi tài khoản truy cập mang tên mình.*
- *Ai đã dựng tai nạn, và vì sao họ cố làm thời điểm xảy ra muộn hơn ba giờ?*

## 4. Design The Solution Backward

Before drafting the beginning, lock:

```text
Objective truth:
True action chain:
Motive and boundary-crossing choice:
Conditions/opportunity:
Mandatory traces:
Traces the culprit can create/delete:
Mistake or unexpected factor:
How the solution is proven:
Consequence after reveal:
```

Feasibility checks:

- Does the timeline allow movement/actions?
- Does the character have established knowledge, tools, or access?
- Would the action leave appropriate traces?
- If traces were deleted, did deletion create another trace?
- Is the motive strong enough for this person to choose this method over easier alternatives?

Do not describe harmful methods in actionable detail. Build internal logic, then narrate only at the safe detail level needed for inference.

## 5. Clue Roles

Do not force every story into "three layers." Assign functional roles:

| Clue role | Function | Example |
|---|---|---|
| Directional | opens an investigation path | access card with odd time |
| Constraint | rules out possibility | call proves someone elsewhere |
| Contradiction | two facts cannot both be true | rain began before alleged photo time |
| Reinterpretation | old detail changes meaning | bell was phone, not church |
| Link | connects person/object/place | fabric from same uniform batch |
| Motive | explains decision | secret contract |
| Proof | survives rebuttal | independent log + witness + physical evidence |

A clue can hold multiple roles but must have source and limits.

Fair-play requires listeners to hear essential facts, necessary specialist rule, POV scope, and at least one plausible inference path. Do not make the reveal depend on "I suddenly remembered an untold detail."

## 6. Evidence Ledger And Chain Of Custody

| Evidence | Created by | Collected/held by | Time | Proves | Does not prove | Tamperable? |
|---|---|---|---|---|---|---|
| lobby camera | building system | guard -> investigator | 21:10 | X entered lobby | which room they entered | missing segment |

Scope of proof:

- Fingerprints show contact, not automatically time or intent.
- DNA shows biological source within sample scope, not the whole act.
- Photos/videos have framing, timestamp, and edit chain.
- Messages have device/account, not automatically the person holding it.
- Testimony is data to verify, not truth because the speaker is emotional.

When using real forensics, law, cameras, DNA, digital data, or procedure timing, verify current sources if accuracy affects plot.

## 7. Hypotheses And Investigation Progress

Scene engine:

> **local question -> verification action -> fact -> interpretation -> next-route decision**

Each investigation scene must change at least one of:

- probability of a possibility;
- timeline;
- opportunity list;
- motive;
- source reliability;
- risk/cost of investigating.

A convincing investigation shows characters propose hypotheses from existing facts, test what could disprove them, update instead of protecting ego, and distinguish known / inferred / guessed.

Investigation mistakes are strongest when they arise from blind spot, pressure, or missing data, not ignoring the obvious for convenience.

Give listeners room to think. Do not insert "something was wrong" after every clue. Put the fact clearly, let a bit of action pass before interpretation, or let two characters argue competing hypotheses.

## 8. Suspects And Side Secrets

Each significant suspect should have at least two of:

- plausible motive;
- opportunity/access;
- concealment behavior;
- relationship that distorts testimony.

Do not make everyone evenly have `motive + opportunity + secret`; that feels like a board game.

Side secrets must work: explain a lie while clearing main crime, create motive, shift alliance, explain misread evidence, or create drama after innocence. If a secret only keeps a suspect in play and vanishes, cut or connect it to theme.

In fair-play, culprit or mechanism must exist in the data system early enough for inference. No universal 30% rule.

## 9. Fair Red Herrings

A red herring is a **true fact misinterpreted**, or a created trace within the opponent's established ability.

Types:

1. **Coincidence with cause:** suspicious object belongs to another secret.
2. **Investigator bias:** wrong weight because of relationship/prejudice.
3. **Active misdirection:** opponent creates/deletes traces and risks doing so.

Do not set a quota for red herrings. One strong herring with consequence beats three formula suspects.

When disproving it, show what hypothesis failed, which facts remain true, why the old reading was reasonable then, and what new route grows from the remaining facts.

## 10. Interviews And Testimony

Do not use `avoids eye contact, shaking, too much detail, answering with a question` as lie detectors. Research shows people detect lies near chance; anxiety, culture, and trauma can look similar.

Interviews are valuable when they lock timeline with specific questions, allow free narrative before comparison, test independently verifiable details, hold back strategic evidence, and compare content contradictions rather than diagnosing gestures.

Interview scene engine:

```text
What does the questioner need to verify?
What does the respondent need to protect?
What evidence does each side know?
Which line forces a tactic change?
What new information leads to action?
```

Slips work only when the detail is truly not public and the story tracks who knows what. Do not end with a careless self-confession just because the plot needs speed.

## 11. Investigator And Agency

The investigator needs:

- reason to participate and authority limits;
- method/strength;
- correctable blind spot;
- cost of continuing;
- active actions that create progress.

Personal connection to the victim is not mandatory if duty/profession is enough. Personal stake may be responsibility, professional honor, community safety, or a belief under test.

Competence should have limits. Let allies provide data/methods for the investigator to integrate, not carry the answer in.

## 12. Reveal And Payoff

A strong reveal pays four layers:

1. **Truth:** what happened.
2. **Inference:** which facts force the conclusion.
3. **Motive/choice:** why this person chose it.
4. **Consequence:** what knowing it changes.

Climax does not have to be dangerous confrontation. It may be a verification trap, timeline reconstruction, formal challenge, public evidence choice, rescue before full explanation, or realizing the truth cannot be proven and choosing another cost.

Avoid solution monologues. Spread inference through action, questions, objects, and rebuttals. A final synthesis is allowed for audio clarity, but each step must rest on heard facts and withstand one intelligent objection.

Postdictability test:

- Does the new meaning fit the old surface meaning?
- Did culprit/method behave irrationally only to hide twist?
- Did any objective fact get denied?
- Does the solution matter to choice/consequence?

The mystery peak (base skill's Peak Design) is the reveal itself: stage it as one converging scene where evidence, suspects, and cost arrive together, with disproportionate room — not as a chain of small confirmations that leaks the payoff piecemeal.

## 13. Audio Clarity

- Do not stack many names, times, and objects in one sentence.
- Anchor each clue to a concrete object/sound/action.
- For complex timelines, reference relational markers: *trước cuộc gọi*, *sau khi điện mất*, not only numbers.
- Summarize only when hypothesis state changes; do not reread entire clue lists by percentage point.
- Sound motifs are clues only if listeners can distinguish them in the actual pipeline; otherwise describe in words.
- Read multi-suspect scenes without tags to test names and `xưng hô`.

Mark fact vs inference:

> *Camera ghi cô ấy vào sảnh lúc chín giờ* is a fact.
>
> *Vậy cô ấy là người vào phòng* is an inference.

Let the narrator signal certainty: *tôi biết, dữ liệu cho thấy, có thể, tôi đoán, tôi đã nhầm*.

## 14. Flexible Structures

- **Whodunit:** lock solution -> introduce question -> open possibilities -> narrow by constraints -> fair reveal.
- **Howcatchem / inverted mystery:** listener knows culprit early; tension is proof and tactics.
- **Missing person:** each trace both locates and revises the missing person's portrait.
- **Procedural:** methods, error margins, collaboration, institutional limits. Jargon is not conflict.
- **Closed circle:** limited people/place/time; requires audible opportunity map.
- **Mystery of interpretation:** objective facts may be clear; answer lies in meaning/motive.

Do not force act ratios. Divide by hypothesis changes and proof strength.

## 15. Hybrids And Premises

- **Mystery + drama:** clue changes relationship; emotion cannot make evidence true.
- **Mystery + horror:** if mystery is main, keep fair-play; supernatural rule is data, not a license to change rules.
- **Mystery + romance:** romance creates bias/cost but must not remove reasoning ability.
- **Mystery + comedy:** comedy may live in method/character; solution remains coherent.
- **Mystery + reincarnation:** knowing outcome is not knowing cause/proof; early changes cause new timeline changes.
- **Mystery + system:** task/points cannot deliver free answer; each hint has scope and price.
- **Mystery + xuyên sách:** the "original text" is a POV source, not an omniscient dossier.

## 16. Repair Examples

**Reveal from new information:**

> *Tôi chợt nhớ hung thủ bị dị ứng hoa lan, điều chưa từng được kể. Vậy chính anh ta đã vào nhà kính.*

**Fairer:**

> Ở cảnh đầu, anh từ chối đứng cạnh bó hoa vì “mùi quá nồng”. Giữa truyện, hồ sơ y tế xác nhận dị ứng nhưng không chứng minh anh vào nhà kính. Reveal chỉ xảy ra khi phấn hoa đặc thù được tìm trên mặt trong găng tay anh tự nói chưa từng dùng.

**Body language = lying:**

> *Cô ta né mắt. Tôi biết cô ta nói dối.*

**Better:**

> *Cô nói chưa từng vào phòng kho, nhưng mô tả chiếc khóa đã được thay. Thông tin đó chưa từng công bố.*

**Clue proves too much:** fingerprint on knife proves contact, not murder. Timeline, knife source, testimony, and independent traces create the conclusion.

**Confession ending weak:** one question makes culprit tell everything. Better: investigator creates a test forcing the opponent to choose between losing evidence or acting in a way only the truth-knower would.

## 17. Safety And Realism

- Follow [../audio-story-engagement/references/an-toan-tu-vung.md](../audio-story-engagement/references/an-toan-tu-vung.md).
- Do not provide actionable procedures for crime, evading investigation, making dangerous substances/weapons, or destroying traces.
- Verify official/current sources when forensics, law, cameras, DNA, digital data, or procedure timing affects the plot.
- Do not assume a victim must have a "dark secret" to deserve harm.
- Do not replace mystery with corpse/gore description.
- Do not use mental illness or social groups as default culprit markers.

## 18. Common Traps

| Trap | Repair |
|---|---|
| Every mystery must be WHO + WHY | Choose correct who/what/how/why/when/proof variable |
| Every clue must have three layers | Assign function, source, and limits |
| Culprit must appear before 30% | Ensure fairness by promise, not percentage |
| Everyone has motive + opportunity + secret | Create natural uneven suspect field |
| At least two red herrings | Use only needed herrings with plausible misreading |
| Eye aversion/shaking = lie | Test content, timeline, independent evidence |
| Summarize clues at 60-70% | Summarize when hypothesis changes and audio needs it |
| Listener must solve before character | Place information according to suspense/surprise |
| Reveal by confession | Prove first; confession can add motive/emotion |
| Forensics as magic | State limits, timing, error, and proof scope |
| Second-half action replaces reasoning | Each danger must force investigative decisions |

## 19. Checklist

- [ ] Correct branch and fair-play/procedural/thriller promise chosen?
- [ ] Central question selects correct who/what/how/why/when/proof?
- [ ] Solution locked backward with timeline, motive, opportunity, mandatory traces?
- [ ] Each clue has source, role, proof scope, and limit?
- [ ] Decisive evidence has custody and can withstand rebuttal?
- [ ] Each investigation scene updates hypothesis or risk?
- [ ] Investigator mistakes come from plausible data/blind spot?
- [ ] Suspects and side secrets have function, not board-game symmetry?
- [ ] Red herrings are true/validly created facts, not erased by random info?
- [ ] Interviews use content verification, not body-language myths?
- [ ] Reveal pays truth + inference + motive + consequence?
- [ ] Audio distinguishes facts from inference, people, and timeline?
- [ ] Crime detail is enough for inference, not harmful instruction?
- [ ] No hard quotas for clues, suspects, herrings, or percentages?

## 20. Basis

- [ACL: A framework for narrative surprise](https://aclanthology.org/2025.wnu-1.7/)
- [PubMed: Causal integration in narrative comprehension](https://pubmed.ncbi.nlm.nih.gov/34531284/)
- [APA: Deception detection](https://www.apa.org/monitor/2016/03/deception)
- [Purdue OWL: Writing Compelling Characters](https://owl.purdue.edu/owl/subject_specific_writing/creative_writing/writers/fiction-basics/writing_compelling_characters.html)
