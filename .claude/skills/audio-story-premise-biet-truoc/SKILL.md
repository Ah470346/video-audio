---
name: audio-story-premise-biet-truoc
description: |
  Premise modifier for reincarnation/regression (`trung sinh/trong sinh`), foreknowledge, time loops, SYSTEM stories (`he thong`), transmigration into a book (`xuyen sach`), pure transmigration (`xuyen khong`), quick transmigration (`xuyen nhanh`), and any special knowledge/rule mechanism. Always use with `audio-story-engagement` and the main genre skill. Do not treat all variants as the same: pure transmigration does not imply future knowledge; a system is not necessarily omniscient; transmigration into a book only gives knowledge from the version/POV read.
---

# Premise: Foreknowledge, Reincarnation, System, Book Transmigration

This premise is compelling when special knowledge or ability makes the character **choose differently**, without erasing other characters' agency or turning the world into a script copy.

## 1. Coordination Contract

- Always use `audio-story-engagement`, one main genre, and [../audio-story-engagement/references/phoi-hop-skills.md](../audio-story-engagement/references/phoi-hop-skills.md).
- This premise defines the source of knowledge/ability, limits, change model, and consequences. The main genre defines the emotional question and payoff.
- Do not skip approval gates or force one opening type. Create premise-appropriate options; let the base workflow preserve user choice.
- Do not explain the origin of reincarnation/system/book-transmigration unless the story promises that question or needs it for payoff.
- This can stack with `audio-story-premise-truyen-rac`.
- Run `audio-story-final-polish` last, especially checking knowledge ledger, timeline, and world rules.

## 2. Identify The Variant Correctly

| Variant | What the character actually has | Do not assume |
|---|---|---|
| **Trùng sinh/trọng sinh** | memory of one lived life/branch | perfect memory, forced repeat |
| **Foreknowledge** | prediction, dream, prophecy, data | 100% accuracy, full context |
| **Time loop** | accumulated experience across loops | every object/person resets identically |
| **System** | goals/rules/rewards/UI | omniscience, truthfulness, future knowledge |
| **Xuyên sách** | memory of a text/version read | off-page scenes, everyone's inner life |
| **Pure xuyên không** | knowledge/skills from old world | future plot/history of new world |
| **Xuyên nhanh** | world-hopping mechanism | each arc fully isolated, no throughline |

Activate only the needed module. If the prompt says only *xuyên không* without foreknowledge/system, use pure transmigration; do not force "original plot" or "script correction."

## 3. Premise Contract

Before plotting, lock seven lines:

```text
Source of knowledge/ability:
Scope of what can be known/done:
Accuracy and detail level:
What cannot be known/done:
World-change model:
Risk if others discover it:
Where this knowledge/ability forces a different choice:
```

If the last line has no answer, the premise is decorative.

### Central Question

> *With [knowledge/ability], what choice will the character use to change [genre outcome], when [limit/opposition] makes the advantage insufficient by itself?*

Tension may come from execution, ethics, proof, other people adapting, or cost even when the forecast remains true.

## 4. Choose A Time/Change Model

Pick **one** primary model before writing:

- **Fixed timeline:** attempts to change the result are part of why it happened. Requires causal-loop setup; avoid making all choices meaningless.
- **Editable timeline:** new actions change the future in the same world. Track memory, evidence, and who notices change.
- **New branch:** old life still happened in another branch/life; character creates another future. Old memory is no longer certain after divergence.
- **Loop reset:** define what resets, what persists, start/end point, and exit condition. Track small deltas per loop.
- **Plot as text, not law:** in `xuyên sách`, the original is a source about one version. "Plot correction" exists only if the story establishes it as a rule.

Do not mix models mid-story to rescue a climax. If a twist shows the model was misunderstood, plant contradictions earlier.

## 5. Knowledge Ledger

For important scenes, track:

| Scene | What character knows/remembers | Source | Certainty | What has diverged | Action based on knowledge | New result |
|---|---|---|---|---|---|---|
| wedding | test result was swapped in book | chapter 3, wife's POV | high result, low culprit | bride called lawyer early | keep original sample | culprit changes frame-up |

Distinguish:

- **Memory:** personal experience, possibly flawed or incomplete.
- **Read/heard:** depends on narrator and version.
- **Inference:** conclusion from old knowledge.
- **Forecast:** not yet happened in this branch.

The narration must mark certainty. Do not let *"tôi biết"* hide that the character is guessing.

If memory is wrong, tie it to POV, time, trauma, or hidden information; plant signs. Do not erase only the one detail the author needs to hide at the end.

## 6. Reincarnation / Regression

The emotional core is counterfactual: *what if I did differently?* Use regret vs disappointment to choose arc:

- **Repairing fault:** character faces their own choices.
- **Saving someone:** knowing outcome still must respect the saved person's agency.
- **Revenge:** not just swapping winners; character decides who they become.
- **Escaping the loop:** old goal may no longer be what they need.

Lock old-life state:

```text
Death/bottom moment:
What the character personally witnessed:
What others only told them:
What they misunderstood:
Three choices they regret most:
One thing they want to preserve, not only change:
```

Choose a return point that creates a decision. It need not be right before tragedy; returning too early, too late, or after an irreversible act can create a different story.

Other people are not old chess pieces. Even if the new branch resembles the old life, they respond to new actions.

## 7. Foreknowledge And Loops

For forecasts, define whether the character sees image, wording, probability, or result; cause or only consequence; clear time or vague time; whether forecast updates after action; and who else can explain the source.

A forecast can be completely true and still create suspense: listeners worry how the character reaches it, whom they save, what they pay, or what meaning they misread.

For loops, each loop needs a **delta**:

| Loop | Experiment | New information | Cost/erosion | Next hypothesis |
|---|---|---|---|---|

Vary tactics: avoid, confront, persuade, gather proof, sacrifice a goal, cooperate. Do not use repeated-death montage instead of progress.

Exit conditions do not need metaphysical origin if that is not the central question, but they must match the theme/choice already built.

## 8. System

A system is **an agent/rule**, not automatically foreknowledge.

Specification:

```text
Who receives it and who can perceive it?
Stable narrative name for the system/agent:
Visible interface components and each component's role:
How the character inputs/responds the first time:
Does it assign goals or only measure states?
What can it observe?
What can it affect?
Where do reward/punishment come from?
Can it explain rules?
Can it lie/be wrong, and what signs show that?
Are loopholes features or bugs?
Does final purpose need payoff?
```

Rules:

- Introduce a rule when it affects the current choice.
- Give the hidden agent, visible frame, message, input field, submitted command/comment, and resulting effect stable, distinct labels. They are not interchangeable. Use `nó` only after one unique audible antecedent exists.
- The first time the character writes, selects, hears, submits, deletes, or activates something, state how that interaction happens. Later repetitions may compress after the listener knows the method.
- A system message may be mysterious about purpose, but not about surface action: listeners must know what appeared, who can perceive it, what the character did, and what changed immediately afterward.
- Every reward has scope; do not turn it into any ability needed by the scene.
- Punishment must fit tone and safety; do not threaten death for every small task.
- Points matter only if they change tactic/access. Number increases without story change are dead weight.
- If the system lies, show contradiction, observation limit, or self-interest early.

Before drafting or polishing a system scene, run [../audio-story-engagement/references/ro-rang-mot-luot-nghe.md](../audio-story-engagement/references/ro-rang-mot-luot-nghe.md). In particular, reject sentences where `nó`, `thứ đó`, `khung chữ`, or `hệ thống` silently changes role, and reject connectors such as `chỉ là`, `lại`, or `sau mỗi lần` when the required promise or prior occurrence has not appeared in the prose.

The character needs room to interpret, resist, bargain, exploit loopholes, or accept consequences. A system that dictates every decision makes the character a task executor.

In pure story files, write system messages briefly through narration/dialogue. Use `[system sound]` or production UI cues only when requested.

Genre integrity:

- Romance: affection points do not prove consent.
- Mystery: hints are not free answers.
- Drama: tasks must change relationship/power.
- Horror: system cannot cleanly explain away the threat instead of experience.
- Comedy: loopholes may be funny but rules still hold.

## 9. Book Transmigration (`xuyên sách`)

Treat the book as a limited source:

```text
Which version/how far did the character read?
Book POV and narrator?
Which scenes were shown directly, which only summarized?
What happens off-page?
Does character remember plot or exact wording, and what proves that?
How similar is the new world to the book?
```

Do not let the transmigrated character know inner thoughts or schemes from scenes they never read.

Text is not world. Book characters have lives beyond plot function. When the transmigrated person acts differently, others respond to current goals. This naturally diverges the "original" without needing fate.

If plot correction exists, define how it detects deviation, scope, cost/mechanism, and evidence before it saves/threatens at climax. Do not use "original plot must happen" as the reason everyone acts against motive.

Clarify identity ethics when relevant: whether the original body's consciousness remains, what memories are shared, and what responsibility the transmigrator has toward the life they took over.

## 10. Pure Transmigration And Quick Transmigration

Pure transmigration resources may be job knowledge, language/culture, carried objects, or a different view of a social system. Modern characters do not automatically remember exact technology/history; knowledge must fit profession and available resources.

Conflict may come from communication, law/status, skills not transferring directly, relationship with a new identity, wanting to return or stay, or old values applied in a new context.

For `xuyên nhanh`, each world needs a local arc, but the throughline must change at least one of: goal, relationship with system, memory, identity, or price.

| World | Genre task | Local rule | What character learns/loses | Throughline trace |
|---|---|---|---|---|

## 11. Suspense When Outcome Is Known

Shift the question:

| Known | New suspense question |
|---|---|
| who betrays | can it be proven, how to respond? |
| accident will happen | whom to save first, how to prevent? |
| couple will separate | why still choose each other now? |
| culprit identity | what evidence survives rebuttal? |
| character will die | what meaning/cost changes for others? |

Tension sources: execution under deadline, evidence and credibility, others adapting, incompatible goals, moral cost of manipulation, correct knowledge with wrong interpretation, divergence reducing memory value, identity secret exposed.

Do not automatically add another reincarnated/system character as difficulty. That is a major choice and can dilute the premise if used as default escalation.

## 12. Cost, Limits, And Resistance

Advantage does not need to cost life span or points every use. Choose organic limits:

- information limits: old POV, vague memory, only results, no proof;
- execution limits: no power, money, time, skill, trust;
- social resistance: knowing too much creates suspicion; others change tactics;
- moral cost: using people as pieces, sacrificing one to save another, removing agency through "I know the future";
- identity cost: living with two-life memories, taking over a body, not knowing whether love belongs to self or original role;
- rule limits: ability has conditions, but no random punishment merely to keep tension.

Choose 1-3 genre-relevant axes, not all of them.

## 13. Open Without Info-Dump

The opening needs only four functions:

1. present situation;
2. concrete sign proving the premise;
3. one thing the character knows/can do differently;
4. nearest action.

Vietnamese examples:

**Trùng sinh**

> *Trên bàn là bản hợp đồng tôi từng ký ngày 12 tháng Tám. Kiếp trước, chữ ký ấy khiến tôi mất công ty ba tháng sau. Tôi gấp bút lại và gọi người kiểm toán đã qua đời trước khi kịp gặp mình lần trước.*

**Hệ thống**

> *Dòng chữ chỉ mình tôi thấy hiện trên tờ đơn ly hôn: “Giữ cuộc hôn nhân thêm bảy ngày.” Tôi xé tờ đơn. Không phải để làm theo, mà để xem hệ thống sẽ phạt tôi bằng cách nào.*

**Xuyên sách**

> *Vệ Minh đặt kết quả xét nghiệm lên bàn và nói đứa bé không phải con anh. Tôi biết tờ giấy là giả vì trong cuốn tiểu thuyết mình đọc tối qua, nó xuất hiện đúng trước khi người vợ bị đuổi khỏi lễ cưới. Lần này, tôi đã giữ lại mẫu xét nghiệm gốc.*

Do not write *"I read this scene word for word"* unless the exact remembered detail changes action.

## 14. Causality And Continuity

Track world state:

- changed events;
- who knows the change;
- evidence kept/lost;
- relationship changes;
- forecasts still conditional;
- activated system rules;
- memories confirmed/disproven.

Butterfly effect should be selective. Not every small change must make the future random. Identify which person, information, or decision was altered; only dependent events shift.

Foreknowledge does not make others believe the character. They may prove a low-risk prediction, create evidence before the event, be in the right place, share part of the source, or accept disbelief and change tactic.

Do not let knowledge solve every genre problem: knowing betrayal does not heal relationship; knowing culprit does not create proof; knowing a lover will leave does not grant control over them.

## 15. Fair Twists

Possible twists if planted:

- source knowledge came from a different POV;
- another person remembers, for a real thematic/plot reason;
- system has its own goal;
- original text is edited/incomplete;
- memory is right about event, wrong about motive;
- time model differs from what character believes;
- the attempted fix caused the old result.

Test:

- Was there at least one contradiction/sign before reveal?
- Does the twist change choice, not only weaken the protagonist?
- Does it deny any objective fact already told?
- If removed, does the premise still have an arc?
- Does it make all previous effort meaningless?

Do not default to "system lies," "old life was fake," or "someone else also reincarnated." Overuse makes every rule untrustworthy.

## 16. Checklist

- [ ] Correct module selected: reincarnation/forecast/loop/system/book/pure transmigration/quick transmigration?
- [ ] Premise contract locks source, scope, accuracy, limits, and change model?
- [ ] Central question belongs to main genre and knowledge makes choice harder/different?
- [ ] Time model is consistent or model-twist is set up?
- [ ] Knowledge ledger separates memory, reading, inference, forecast?
- [ ] Character does not know scenes outside POV/version?
- [ ] Each future change follows causality?
- [ ] Foreknowledge does not automatically create proof, repair relationships, or control others?
- [ ] System has observation/effect/reliability spec and preserves agency?
- [ ] System/agent, interface, message, input, and effect have stable distinct names; every pointer has one antecedent; first-use interaction method is audible?
- [ ] Loops have deltas in information, tactic, cost, or character?
- [ ] Limits/costs are genre-linked, not random penalties?
- [ ] Opening shows one concrete premise sign and action?
- [ ] Twist does not deny facts or make all effort meaningless?
- [ ] Origins are answered only if promised?
- [ ] After writing, final polish has checked timeline/knowledge/rules?

## 17. Need-Based Reference

Read [references/phoi-hop-va-vi-du.md](references/phoi-hop-va-vi-du.md) when:

- combining this premise with a genre or `audio-story-premise-truyen-rac`;
- needing before/after examples for stiff meta narration, arbitrary butterfly effects, or omnipotent systems;
- needing a quick trap table or research basis.
