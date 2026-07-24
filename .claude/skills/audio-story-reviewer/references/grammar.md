# Grammar, Wording, Punctuation, and Sentence Flow

Use this reference when the review needs detailed line-level diagnosis: grammar, punctuation, wording, repeated cadence, sentence length, oral rhythm, and Vietnamese prose that becomes hard to understand when heard once.

## Review Goal

Line editing for audio is not cosmetic. The goal is to make each sentence clear enough to survive one hearing while preserving voice, region, register, and genre tone.

Do not flatten all prose into neutral textbook Vietnamese. A narrator can be lyrical, comic, blunt, rural, melodramatic, or intimate. Treat a line as defective only when it causes confusion, unwanted stiffness, broken grammar, wrong social meaning, or avoidable listening strain.

## Grammar Pass

Check:

- spelling and typo-like substitutions;
- missing, duplicated, or swapped words;
- malformed idioms and unnatural collocations;
- semantic-domain/category mismatch: object, machine, accounting, medical, legal, or interface verbs applied to people and relationships as though the mapping were literal, with no intentional character effect;
- translated metaphor/collocation: a source-language mapping remains understandable (`broken/fix a marriage`) but sounds unnatural when carried directly into Vietnamese;
- subject-predicate mismatch;
- dangling modifiers;
- unclear clause attachment;
- inconsistent tense and temporal markers;
- cause/effect connectors that reverse logic;
- wrong word class, for example noun used where verb is needed;
- excessive Sino-Vietnamese wording in a colloquial scene;
- regional or slang wording that conflicts with the established voice.

Common Vietnamese problems:

- `cứu cánh` used as if it means "cứu giúp" in everyday speech;
- `bàng quang` confused with `bàng quan`;
- `chín mùi` overused for every secret or timing;
- `trực chờ` used when `chực chờ` is meant;
- `yếu điểm` used when the intended meaning is `điểm yếu`;
- repeated `không khỏi`, `bỗng nhiên`, `lúc này`, `sau đó`, `ngay lập tức`.

Flag only what appears in evidence. Do not turn the review into a generic grammar lesson.

## Punctuation for Vietnamese Audio Prose

Check:

- missing terminal punctuation;
- question sentences without `?`;
- exclamations overused until all intensity becomes equal;
- comma splices that make two actions sound simultaneous when they are sequential;
- misplaced colon before dialogue;
- inconsistent ellipses: `...`, `…`, `....`;
- overuse of dashes as a substitute for scene logic;
- decorative dashes or line-leading dialogue dashes in VoxCPM-bound pure prose;
- punctuation glued to the next word, causing TTS token/rhythm risk;
- quotation marks not closed;
- speaker attribution separated from the utterance incorrectly;
- multiple speaker turns in one paragraph when turn ownership or TTS reset becomes unclear;
- numbers, abbreviations, and symbols that TTS may read awkwardly.

Dialogue punctuation examples:

Problem:

> Mẹ anh nhìn cô rồi nói. "Con về rồi à"

Diagnosis: the reporting clause is separated incorrectly, the utterance is a question, and `hỏi` is more precise than `nói`.

Revision:

> Mẹ anh nhìn cô, khẽ hỏi: "Con về rồi à?"

Problem:

> "Anh đi đâu", cô hỏi?

Revision:

> "Anh đi đâu?" cô hỏi.

Problem:

> "Tôi không cần." Anh nói rồi quay đi.

Revision:

> "Tôi không cần." Anh quay đi.

Why: the action beat already identifies the reaction; `nói rồi` adds little unless the beat must show sequence.

VoxCPM/TTS-oriented examples:

Problem:

> "Ra ngoài." "Không." "Tôi bảo cô ra ngoài."

Diagnosis: three turns are visually separated but may be delivered as one fast stream by single-voice TTS.

Revision:

> "Ra ngoài."
>
> "Không."
>
> Anh hạ giọng. "Tôi bảo cô ra ngoài."

Problem:

> Tin nhắn gửi lúc 19:45, kèm mã hồ sơ ADN số 03/2024.

Revision:

> Tin nhắn gửi lúc bảy giờ bốn mươi lăm tối, kèm mã hồ sơ xét nghiệm ADN đầu tháng tư năm đó.

Why: raw times, slashes, and codes may be misread or create false pauses; write the intended spoken form unless the exact code matters.

## Sentence Listenability

Ask:

- Can a listener understand the sentence in one hearing?
- Is the subject close to the main verb?
- Does the sentence contain one primary action, image, or thought?
- Are cause, perception, reaction, and consequence ordered clearly?
- Is the sentence overloaded with names, dates, clauses, or abstract nouns?
- Does punctuation create a natural breath pattern?
- Does the sentence end at the emotional beat, or explain after the beat lands?

Do not enforce a universal word limit. Risk depends on clause nesting, referent count, unfamiliar terms, delivery speed, punctuation/prosody, and whether the sentence asks the listener to retain an unresolved opening phrase. A long sentence with a clear spine may be easier than a shorter sentence with three ambiguous pronouns.

High-risk sentence patterns:

- long front-loaded clauses before the subject appears;
- a chain of subordinate clauses ending in a generic emotion;
- multiple characters and pronouns in one sentence;
- action, backstory, thought, and explanation packed together;
- several abstract nouns with no concrete behavior;
- a polished three-part cadence repeated across paragraphs;
- every sentence beginning with the character name plus verb;
- every sentence cut short until the rhythm becomes mechanical.

Example:

Problem:

> Sau khi nghe những lời ấy của người đàn ông mà ba năm trước cô từng tin tưởng tuyệt đối nhưng cũng chính là người đã bỏ đi trong đêm mưa định mệnh, Lan cảm thấy trong lòng mình dâng lên một cảm giác rất khó tả.

Revision:

> Lan nhận ra giọng nói ấy ngay lập tức. Ba năm trước, chính người đàn ông này đã bỏ cô lại trong đêm mưa. Cổ họng cô nghẹn cứng.

Why it works: the long dependency is split, the memory is anchored, and a generic emotion becomes a bodily response.

## Paragraph-Level Flow

A paragraph in audio prose should usually carry one listening unit:

- one beat of action;
- one reveal;
- one emotional turn;
- one small causal link;
- one compact reflection.

Flag paragraphs that:

- shift time or place without orientation;
- contain too many pronouns after multiple characters are introduced;
- explain the same feeling in three ways;
- repeat the previous paragraph's function;
- bury the important turn in the middle;
- end with a generic thesis statement after a stronger image.

Useful repair directions:

- move the subject and scene anchor earlier;
- split a mixed paragraph into action, reaction, and consequence;
- replace abstract explanation with one behavior;
- delete the sentence that tells the listener what they already inferred;
- repeat a name or relationship noun when pronouns become ambiguous by ear.

## AI-Like Cadence and Formulaic Prose

Do not accuse the author of using AI. Diagnose textual symptoms.

Surface symptoms:

- repeated `Không phải vì... mà vì...`;
- repeated `Tôi biết... nhưng tôi không biết...`;
- repeated `Điều tôi không ngờ là...`;
- neat moral summaries at scene endings;
- symmetrical sentence triples in unrelated emotional states;
- repeated hindsight interjections (`tôi đâu biết`, `mãi về sau tôi mới hiểu`, `đó là sai lầm đầu tiên`);
- allusive-posturing foreshadows: hints at future irony through an abstract riddle (`đúng cái thứ mình sắp thua`) instead of a concretely named stake in the character's voice;
- most scene/paragraph endings sharing one closure shape: aphorism, thesis, balanced antithesis, or punchy fragment triple;
- a fresh reveal restated in several escalating paraphrases before a button line;
- a returning callback or symbol whose changed meaning the narration explains (`câu đó có nghĩa là...`);
- most action sentences dragging a trailing evaluative clause (`, khiến tôi...`, `, như thể...`, `, để lại...`);
- dense soft-cliché vocabulary: clusters of `khoảnh khắc`, `hành trình`, `chữa lành`, `bình yên`, `vụn vỡ`, `chông chênh`, `lặng lẽ`/`khẽ`, `như một` + abstraction;
- paragraphs of nearly uniform length and internal shape across the manuscript;
- all characters using the same smooth, correct, abstract voice;
- many sentences that could be moved to another story without change.

These are not automatically errors. They become errors when they flatten character, slow pacing, or explain instead of dramatizing.

Also inspect **over-finished dialogue sequences**, not only repeated sentence shells:

- one speaker introduces a polished metaphor and the next instantly completes or overturns it;
- a character's profession supplies every comparison even outside that register;
- several speakers share one image field without shared history;
- every challenge receives an exact, quotable comeback;
- characters understand and state the theme more neatly than their current knowledge or pressure allows.
- a new acquaintance states another person's hidden psychological pattern as fact after one small cue;
- unrelated scenes reuse conspicuous household props, tidying motions, delayed answers, or realization phrasing as ready-made emotion;
- every scene exposes the same sequence of setup, symbolic gesture, insight, and quotable closer.

These symptoms are often semantic and character failures rather than grammar errors. Cross-check [dialogue.md](dialogue.md) and the shared [human semantic-fit gate](../../audio-story-engagement/references/ngon-ngu-con-nguoi.md).

Do not repair generic emotion by automatically inserting a household object or small hand movement. That merely replaces one formula with another. Ask what this exact place, task, relationship history, and immediate consequence make the character notice or fail to do. Direct emotional naming may be the most precise repair.

Treat all examples in story skills as contaminated source material. Reuse of their objects, gestures, occupations, image fields, or sentence architecture requires independent scene necessity; a synonym or a different domestic prop is not sufficient distance.

## Diagnosing Diction

When a word feels wrong, name the exact mismatch:

- register mismatch: too formal, too modern, too literary, too crude, too childish;
- relationship mismatch: the word sounds too intimate or too distant;
- narrator mismatch: vocabulary does not fit education, region, age, or POV;
- genre mismatch: comedy word in a grief scene, melodrama word in a procedural scene;
- category mismatch: the word is ordinary for an object/system but makes the human target sound literally repairable, measurable, filed, debugged, or processed without an earned metaphor;
- ownership mismatch: the word belongs to another character's profession/image field or to retrospective narration, not this speaker's live vocabulary;
- audio mismatch: hard-to-hear abbreviation, foreign name, or symbol.

Avoid vague comments like `dùng từ chưa hay`. A synonym-only note is especially inadequate when the defect is category fit or speaker ownership. Use:

> `định mệnh` appears three times in two paragraphs, so the word loses force and makes the narration sound prepackaged. Keep it only at the strongest turning point or replace the other two with concrete event language.

Or:

> `hỏng/sửa/đồ vật` forms one repair field across both speakers. The issue is not that `hỏng` is always forbidden; it is that the marriage has been reduced to an object and the reply exists to complete the metaphor. Rewrite from each speaker's immediate human intention instead of swapping in `nứt/vỡ`.

## Repair Hierarchy

Fix in this order:

1. meaning and grammar;
2. pronoun clarity and speaker clarity;
3. sentence length and breath;
4. unnecessary explanation;
5. earned knowledge, example distance, and scene-specific selection;
6. diction and rhythm polish.

Do not polish a sentence that belongs to a scene likely to be cut or moved.

For TTS-bound text, treat punctuation as a cue to be tested, not a guaranteed pause. Different engines infer structure and prosody differently; move to `audio.md` when a problem depends on the target voice or engine.

For VoxCPM-bound manuscripts, also check the shared pause guide at `../../audio-story-engagement/references/voxcpm-tts-ngat-nghi.md` when deciding whether a mark should become a comma, period, paragraph break, action beat, or spoken-token rewrite.

## Evidence Frame

Use this compact frame for line-level issues:

- **Evidence:** exact short quote.
- **Defect:** grammar / punctuation / wording / cadence / pronoun ambiguity.
- **Listener impact:** what becomes hard to hear or emotionally flat.
- **Repair direction:** split, reorder, name the subject, replace abstract label, delete explanation, or fix punctuation.
- **Illustrative revision:** only if it clarifies the fix.
