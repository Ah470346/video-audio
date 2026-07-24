---
name: audio-story-genre-hai-huoc
description: |
  Specialist skill for COMEDY (`hai huoc`): situation comedy, character comedy, romantic comedy, family comedy, dark comedy, satire, parody, and absurd comedy. Always use with `audio-story-engagement`; add premise modifiers when relevant. Trigger when the user's desired main reward is laughter, irony, comic release, or satirical perspective, not merely because the story contains a few jokes.
---

# Audio Story Genre: Comedy

Story comedy is not a chain of punchlines. It is a character pursuing a serious goal with increasingly wrong tactics inside a world that still reacts logically.

## 1. Coordination Contract

- Use `audio-story-engagement` as the base and follow [../audio-story-engagement/references/phoi-hop-skills.md](../audio-story-engagement/references/phoi-hop-skills.md).
- This skill defines the source of laughter and comic payoff. It does not replace approval gates, safety, Vietnamese address rules, or output format.
- Do not impose fixed counts for jokes per minute, punchline length, or callbacks.
- Run `audio-story-final-polish` last, while preserving intentional comic roughness and rhythm.

## 2. Genre Contract

Comedy needs:

1. **Recognizable expectation:** listeners understand what normal should be.
2. **Deviation:** character, situation, or system breaks the expectation.
3. **A frame safe enough to laugh:** harm level and joke target fit the tone.
4. **Consequence:** deviation forces response; it does not vanish after the punchline.
5. **Point of view:** narrator or character sees irony in a specific way.

Benign-violation research is useful as a diagnostic: a violation is more likely to feel funny when it is simultaneously a violation and safe enough. "Safe enough" varies by distance, culture, and power asymmetry. This is not the only theory of comedy.

**Genre test:** if removing the funny comparisons leaves no comic contradiction in character/situation, the story is relying on author voice rather than a comic engine.

## 3. Comedy Mechanisms

Choose one or combine deliberately:

| Mechanism | How it works | Avoid |
|---|---|---|
| Expectation mismatch | A is set up; B follows another logic | random result unrelated to setup |
| Disproportion | reaction too large/small for situation | one-size reaction repeated |
| Escalating commitment | character keeps defending an old error | making them stupid arbitrarily |
| Dramatic irony | listener knows what character does not | stretching what one question could solve |
| Status | powerful person loses footing or reverse | humiliating the powerless |
| Recognition | everyday truth named unexpectedly | generic meme observation |
| Language | double meaning, rhythm, literal reading | jokes that require seeing text |
| Callback | old detail returns with new function | repeating the same line unchanged |

A larger deviation is not automatically funnier. Play frame, harm level, character, and explanation all matter.

## 4. Central Question And Comic Engine

Template:

> *Can [character] achieve [serious goal] before [mistake/blind spot] pushes the situation beyond control?*

Vietnamese examples:

- *Tôi có giấu được việc đặt hai bàn tiệc cùng ngày trước khi hai gia đình tới cùng một nhà hàng?*
- *Một nhân viên tuân thủ đúng từng quy định vô lý sẽ buộc công ty thừa nhận quy trình sai ở đâu?*
- *Tôi có tỏ tình được khi em gái đã dùng nhầm bản nháp của tôi làm bài phát biểu đám cưới?*

Write the comic engine in one sentence:

```text
Whenever the character tries to [goal], [trait/situation rule] makes them [repeatable mistake type with variation].
```

Example:

> *Mỗi khi Minh cố chứng minh mình là người tổ chức chuyên nghiệp, thói quen không dám nói “không” khiến anh nhận thêm một yêu cầu mâu thuẫn.*

The engine must create multiple different scenes from the same logic. If it creates only one punchline, it is a gag, not an engine.

## 5. Comic Characters

Build from contradiction, not labels:

| Slot | Example |
|---|---|
| Image they want to keep | person who controls everything |
| Blind spot | cannot see they talk too much |
| Real competence | handles crises fast |
| Unbearable threshold | being seen as unprofessional |

Comedy happens when the blind spot damages the image, while real competence lets the character survive long enough for the situation to continue.

Characters need real goals and vulnerability. Do not turn body type, illness, regional accent, poverty, or trauma into the default punchline. The "straight" character also needs a blind spot; they are not just an explainer.

Comic pairs come from conflicting logics: improviser vs rule follower, face-saving person vs blunt truth-teller, accurately pessimistic person vs wrongly optimistic but useful person, metaphor-understander vs literal listener. Roles can switch by arena.

Conflicting logic does not mean both people trade polished quips. Literalization belongs when a character truly acts on a literal reading and the world produces consequence; it fails when one speaker offers a metaphor only so the other can reverse it like a caption. Let some replies be confused, practical, delayed, irritated, or plain. Run the base [human semantic-fit gate](../audio-story-engagement/references/ngon-ngu-con-nguoi.md) when profession/object language enters the exchange.

## 6. Beats And Punchlines

Basic beat:

> **clear setup -> listener forms expectation -> pivot -> consequence/reaction**

Use pauses only when voice and production support them. Do not insert `[pause]` tags into pure story unless requested.

Put the meaning-changing information near the end of a sentence unit when possible, but do not sacrifice natural syntax or clarity. "Punchline must be the final word" is too rigid.

Vietnamese calibration:

**Forced:**

> *Từ trong vali, một con gà bất ngờ chạy ra khiến tất cả chúng tôi hoảng hốt.*

**Cleaner:**

> *Tôi mở vali. Quần áo không có. Có một con gà.*

The laugh comes from pacing and dry confirmation, not from inverted syntax.

Reaction may confirm absurdity, misunderstand further, preserve face, shift power, or create the next problem. Do not explain why the punchline is funny, but clarify facts if listeners may miss what happened.

Useful tools: rule of three, understatement/overstatement, bathos, misdirection, literalization. Use them when they serve character logic.

## 7. Situation Escalation

Good snowball is causal:

> **small mistake -> cover/fix attempt because of character -> solution creates new obligation -> threads collide -> final choice**

Escalation axes:

- number of people who know;
- contradictory promises;
- public exposure;
- cost of confessing.

Misunderstandings work only when characters have a reason not to ask plainly, answering now carries real cost, each delay creates new action/evidence, and the reveal leaves consequence.

The world must react. Bills still matter, guests still respond, bosses still have goals, and harmed people do not forget because the scene needs a laugh.

### The Comic Set-Piece And Toppers

Follow the base skill's Peak Design. Every comedy needs one **set-piece**: the scene where the comic engine runs hottest, the planted threads collide in one place with witnesses, and the character cannot retreat. Let it run visibly longer than feels safe — ending the scene right after the first laugh wastes the whole setup.

- **Toppers:** after the first detonation, do not cut away. While the situation is still hot, stack two to four escalating toppers, each growing from a different already-planted thread arriving in the same room, never from a fresh coincidence. The listener should think the scene is over — then it gets worse in a way the setup already paid for.
- **Doubling down:** at the peak the character digs deeper live — covering, improvising, defending the lie in front of everyone — instead of reflecting afterward. Commitment under witnesses converts smiles into laughs.
- **Smile vs laugh:** narrator wit produces smiles; situation, witnesses, and irreversibility produce hard laughs. A comedy cannot live on narration wit alone; at the set-piece the situation itself must do the work.
- "Leave room after big beats" applies once the set-piece has fully detonated, not between its toppers.

## 8. Running Gags And Callbacks

A running gag must change function, not merely repeat three times.

| Pass | Possible function |
|---|---|
| setup | introduces object/line/trait |
| variation | appears where its meaning changes |
| payoff | solves or detonates the main conflict |

Example: a distorted speaker first ruins a speech, later leaks a phone call, and finally becomes the only way to transmit a real apology.

Not every comedy needs a running gag. Observational comedy or satire may use an idea motif instead.

## 9. Comedy Branches

- **Situation comedy:** goal and obligations collide. Prioritize causality, timing, and status.
- **Character/family comedy:** familiar life logics collide. Know whether the story laughs with, laughs at, or critiques someone.
- **Romantic comedy:** deviation lets two people see each other more clearly. Accidents cannot replace chemistry or consent.
- **Dark comedy:** define target, distance, and harm level. Laugh at power, ritual, denial, or absurdity; do not sacrifice the powerless as punchline. Follow base safety.
- **Satire:** establish system rules, let characters follow them to absurd consequence, and keep critique target consistent.
- **Absurd/surreal:** the world can be unreal but must have internal logic. Listeners need to know what is normal there.

## 10. Audio Rhythm And Dialogue

- Laugh frequency depends on the promise: sketch is denser than dramedy. Use listening tests/retention, not a rigid 60-90 second law.
- A joke sentence does not have to be under 15 words. Length serves setup, voice, and breath.
- Distinguish voices by goal, logic, and status; do not make everyone quip.
- Do not confuse rapid aphorism tennis with chemistry. Two separate speakers do not need to share one image field or deliver the exact setup and comeback the author wants.
- Leave room after big beats when listeners need to catch the pivot; the gap can be an action, not a silence tag.
- A serious passage does not forget the genre if it raises cost or deepens later payoff.
- Modern comparisons such as wifi/apps work only when age, job, and voice fit. Do not turn narration into a meme pile.

Test on someone who does not know the setup. Note where they miss facts, predict too early, understand but do not laugh because harm is too large, or laugh at the reaction instead of the planned punchline.

## 11. Flexible Structures

- **Snowball:** one mistake protected by later mistakes; payoff when threads collide.
- **Goal comedy:** simple goal, varied arenas.
- **Status reversal:** the seemingly powerful person reveals dependence.
- **Satirical demonstration:** one rule/system tested across cases, exposing contradictions.
- **Comic reconciliation:** opposing logics cooperate without becoming identical.

Endings may be warm, sour, open, or sharp. Pay off the promised comic experience.

## 12. Hybrids And Premises

- **Comedy + drama:** if drama is main, jokes must not erase damage; if comedy is main, reduce harm and keep recoverability.
- **Comedy + romance:** laughter creates chemistry or exposes vulnerability; it does not replace romantic choice.
- **Comedy + mystery:** solution stays fair; deviation may live in hypotheses or the investigator.
- **Comedy + horror:** decide where listeners should fear or laugh; stray quips can break dread.
- **Comedy + system/xuyên sách:** humor comes from mismatch between rules/expectations and behavior, not from long UI explanations.
- **Comedy + truyen-rac:** keep consequences recoverable; if foolishness causes severe harm to innocents, tone shifts toward drama/rage bait.

## 13. Repair Examples

**Author trying to joke:**

> *Sếp tôi tức như một con hổ bị mất wifi, nhìn buồn cười không chịu được.*

**Comic engine:**

> *Sếp cấm cả phòng dùng điện thoại trong cuộc họp về chuyển đổi số. Ba phút sau, ông hỏi vì sao không ai quét mã để xem tài liệu.*

Absurdity comes from the character's goal and rule.

**Absurdity without consequence:**

> *Tôi mời nhầm một trăm người và ai cũng vui vẻ tới dự.*

**Causal chain:**

> *Tôi gửi nhầm thiệp cho cả danh sách khách hàng. Xóa tin không kịp, tôi bèn bảo đó là “sự kiện tri ân”. Đến lúc giám đốc hỏi ngân sách, tôi đã có tám mươi sáu người xác nhận tham dự và một ban nhạc tự nguyện.*

**Punching down weak:** laughing because a poor employee does not know luxury rituals.

**Better:** laugh because the company forces employees to learn luxury rituals to hide unpaid wages. The target becomes the power system.

## 14. Common Traps

| Trap | Repair |
|---|---|
| Quips in every sentence | Let characters speak by goal; keep punchlines where setup exists |
| Metaphor plus perfect counter-metaphor | Put the comic deviation into behavior/consequence, or let the reply use the second character's own plain language |
| Occupation becomes every joke and emotion | Use professional knowledge in action/attention; do not turn all relationships into tools, accounts, diagnoses, or procedures |
| Character is stupid so plot can move | Use consistent blind spot, status, or commitment |
| Punchline forced to final word | Prioritize natural syntax and clear idea units |
| Every scene worsens in the same way | Change axis: knowledge, status, publicity, obligation |
| Misunderstanding prolonged by fake silence | Create reason and cost for not speaking |
| Running gag repeats unchanged | Change function or meaning each time |
| Dark comedy becomes cruelty | Check target, power, harm, and distance |
| Satire has no target | Define the system/belief being criticized |
| Warm ending mandatory | Pay the promised tone; warmth is optional |
| Rhythm controlled by `[pause]` tags | Write rhythm through sentence/action; add cues only if requested |
| Narrator caps every comic beat with a wise epigram or hindsight aside | Let reaction and consequence be the button; keep narrator commentary occasional so wit stays a voice, not a tic |

## 15. Checklist

- [ ] Does the genre contract include expectation, deviation, safe-enough frame, consequence, and point of view?
- [ ] Can the comic engine generate multiple scenes?
- [ ] Does the character have a real goal, desired image, blind spot, and competence?
- [ ] Does each beat provide enough setup for the pivot?
- [ ] Is the punchline clear by ear and natural in Vietnamese syntax?
- [ ] Does the humor arise from character/situation and consequence rather than two characters co-authoring quotable lines?
- [ ] Does escalation come from choices to fix/cover, not random events?
- [ ] Is there one comic set-piece where planted threads collide in front of witnesses, held long enough for toppers that grow from setup?
- [ ] Does misunderstanding have reason and real cost?
- [ ] Are joke target and power asymmetry appropriate?
- [ ] Does any running gag change function?
- [ ] Do serious passages still serve goal/cost?
- [ ] Does the ending pay comic consequence, not mandatory lesson or warmth?
- [ ] No quotas for joke count, sentence length, or callback count?

## 16. Basis

- [PubMed: Benign violations](https://pubmed.ncbi.nlm.nih.gov/20587696/)
- [PubMed: Benign violation, power asymmetry and culture](https://pubmed.ncbi.nlm.nih.gov/31275204/)
- [PubMed: Final-note expectancy and humor](https://pubmed.ncbi.nlm.nih.gov/36180930/)
- [Purdue OWL: Writing Compelling Characters](https://owl.purdue.edu/owl/subject_specific_writing/creative_writing/writers/fiction-basics/writing_compelling_characters.html)
