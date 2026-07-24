# Audio-Specific Clarity and TTS Readiness

Use this reference for cold-listening checks, audiobook clarity, VoxCPM/TTS readiness, pronunciation, names, numbers, symbols, scene orientation, dialogue-turn rendering, pause structure, and formatting-dependent reveals.

## Cold-Listening Mindset

Review as if the listener:

- cannot see paragraph breaks;
- cannot see quotation marks;
- cannot scan backward;
- may be multitasking;
- hears names and pronouns only once;
- relies on rhythm, repetition, and orientation.

A passage can be readable on page and confusing in audio.

Do not claim that listening is inherently inferior to reading. Treat this pass as a simulation of the actual delivery constraint: continuous input, no visual formatting, and limited opportunity to inspect a prior phrase. If the platform offers transcripts, rewind, chapters, or synchronized text, note that those affordances reduce some risks.

## Orientation at Scene Openings

At a scene change, listeners need quick anchors:

- who is present;
- where they are;
- when this is relative to the previous scene;
- what emotional or plot pressure continues.

Weak:

> Ba ngày sau, cô đứng đó, không nói gì.

Stronger:

> Ba ngày sau, Lan đứng trước cửa nhà xác. Người duy nhất đi cùng cô là Hùng, và anh vẫn chưa biết trong túi áo cô có tờ xét nghiệm.

## Names

Check:

- similar-sounding names: Lan/Linh, Minh/Vinh, Hạ/Hà, An/Anh;
- too many names introduced close together;
- foreign names with unclear pronunciation;
- titles used inconsistently with names;
- aliases not linked by audio-friendly reminders;
- character names that sound like common words in context.

Repair options:

- rename one character;
- add relationship anchors: `Minh, người anh cùng cha khác mẹ`;
- delay minor names;
- use titles until names matter;
- repeat a key relationship at scene entry.

## Pronoun Runs

Audio pronoun ambiguity often appears after two or more characters of the same gender enter a paragraph.

Flag:

> Anh nhìn hắn. Hắn không nói gì. Anh biết nếu anh bước thêm một bước, hắn sẽ không tha cho anh.

The listener may lose who each `anh` and `hắn` refers to.

Repair:

- restore names or relationship nouns;
- split sentence clusters;
- use an action beat;
- keep the emotional stance of pronouns consistent.

## Numbers, Dates, Units, and Symbols

TTS may handle these unpredictably:

- `3/4/2024`;
- `20%`;
- `1m65`;
- `CEO`, `ADN`, `CMND`, `CCCD`;
- `@`, `#`, `&`;
- URLs;
- legal codes;
- currency abbreviations;
- mixed Vietnamese-English terms.

Review whether the manuscript should write them for the ear:

- `ngày ba tháng tư năm hai nghìn không trăm hai mươi bốn`;
- `hai mươi phần trăm`;
- `một mét sáu mươi lăm`;
- `căn cước công dân` on first use;
- `ba trăm triệu đồng`.

Do not over-expand if the platform or narrator expects standard abbreviations. Flag where pronunciation choices must be made.

Build a normalization ledger for every consequential non-standard token:

| Written token | Intended spoken form | Context/meaning | First occurrence | Engine tested? | Consistent? |
|---|---|---|---|---|---|

The same written form can have different readings by context. Do not approve `3/4`, `1.000`, `AI`, a score, a room number, or a legal code until the intended spoken meaning is clear.

## VoxCPM/TTS Pause Readiness

For scripts headed to VoxCPM, judge the manuscript as plain Vietnamese input first. Do not assume SSML, `[pause]`, speaker labels, or visual formatting will save unclear prose unless the user has explicitly requested supported production markup.

Flag:

- raw dates/times such as `12/5`, `19:45`, `7h30`;
- raw symbols such as `/`, `%`, `@`, `#`, `&`;
- dense sentences with several comma breaths and multiple referents;
- dialogue turns from different speakers packed in one paragraph;
- line-leading dashes used as dialogue markers;
- repeated ellipses or dashes used as a substitute for emotional action;
- punctuation glued to the next word;
- quoted fragments that look like emphasis but may be mistaken for dialogue.

Repair direction:

- write consequential tokens in the form to be heard;
- use periods for deliberate stops and paragraph breaks for speaker/thought resets;
- use a sentence/paragraph boundary, withheld response, or scene-required action for a pause; do not add a decorative gesture;
- split a long quoted line by breathable meaning units such as stop, evidence, refusal, or consequence; do not manufacture a tactic for every unit;
- keep the story file pure unless production cues are requested.

Use the shared drafting reference `../../audio-story-engagement/references/voxcpm-tts-ngat-nghi.md` when you need the fuller pause hierarchy and examples.

## Foreign Words and Names

Check whether:

- a narrator can pronounce the term consistently;
- the term matters enough to keep;
- a Vietnamese gloss is needed;
- repeated English terms break voice;
- brand/product names are essential.

For fantasy names, avoid many similar invented terms in one paragraph. Audio memory is limited.

If the target engine is known, render a representative sample containing every recurring foreign name, abbreviation, number pattern, and invented term. A text-only review can mark likely risk but cannot certify pronunciation.

## Engine-Specific Output

Use plain spoken Vietnamese as the portable baseline. If the production system supports SSML or an equivalent markup, it may help specify sentence structure, pauses, pronunciation, prosody, substitutions, and interpretation of dates or numbers.

Do not insert SSML into the manuscript unless the user requests production markup and the target engine supports the chosen elements. Engine behavior varies, and unsupported markup can be ignored or spoken incorrectly.

## Formatting-Dependent Reveals

Audio cannot preserve:

- footnotes;
- hidden acrostics;
- visual separators;
- typography-based emphasis;
- tables;
- chat screenshots unless narrated;
- color or layout clues;
- quote indentation;
- parenthetical jokes that rely on seeing parentheses.

Repair direction: verbalize the clue or turn it into an object, line, sound, or narrator observation.

## Dialogue in Audio

Check:

- speakers re-anchored after long turns;
- interruptions readable aloud;
- silence meaningful;
- action beats not too frequent;
- names or kinship terms used naturally;
- no two voices share identical rhythm in the same exchange.
- each speaker turn is separated enough for a single-voice TTS engine to reset;
- a dialogue-heavy sample can be rendered without rushed turn-taking or swallowed words.

When there are three or more speakers, use more anchors than page fiction would need.

Risky:

> "Ra ngoài." "Không." "Tôi bảo cô ra ngoài."

Better for audio/TTS:

> "Ra ngoài."
>
> "Không."
>
> Anh hạ giọng. "Tôi bảo cô ra ngoài."

Do not mark every same-paragraph quote as an error. A short quote followed by narration and a second line from the same speaker may be fine. Flag it when turn ownership, breath, or render reset becomes unclear.

## Dense Lists

Audio listeners struggle with long lists:

- names;
- evidence items;
- family relations;
- company positions;
- fantasy ranks;
- injuries;
- dates.

Repair:

- group into two or three meaningful clusters;
- keep only plot-relevant items;
- repeat the key item after the list;
- turn the list into a choice or conflict.

## Strategic Repetition

Repetition is not always bad in audio. It can help listeners track:

- a central object;
- a threat;
- a relationship noun;
- a rule;
- a deadline;
- a promise.

Good repetition changes pressure or meaning. Bad repetition repeats wording without new function.

Example:

First:

> Chiếc nhẫn nằm trong ngăn kéo cuối cùng.

Later:

> Đến khi mở ngăn kéo cuối cùng, cô mới hiểu vì sao chiếc nhẫn không được cất trong hộp trang sức.

The repetition helps memory and changes meaning.

### Consecutive Openings That Sound Like A Synthesis Fault

Separate from motif repetition, check runs of consecutive sentences that begin with the same words. A renderer cuts prose into short chunks and each chunk starts after a prosodic reset, so two chunks opening alike are heard as the engine repeating itself rather than as a device.

This has produced a false bug report in production: a listener flagged a chunk as stuttering, and measuring the waveform showed the synthesis matched the script exactly. Report it as a script issue, never as a render defect — re-rendering cannot change it.

Judge intent before flagging. An anaphora building toward a payoff is worth keeping; the repair is to change each sentence's first word while keeping the anchor phrase, not to delete the repetition. Do not accept a one-word insert after the same first word (`Tôi muốn` / `Tôi rất muốn` / `Tôi còn muốn`) as a completed repair — production listening showed the unstressed insert is swallowed and the run is still heard as a stutter. Sentences that merely happen to start alike carry no such credit.

## Recording Readiness

Judge readiness:

- **Ready after light polish:** grammar clean, speakers clear, no major logic gaps, emotional beats land.
- **Needs targeted revision:** one or two major issues but story foundation works.
- **Needs substantial revision:** repeated causality, POV, pacing, or emotion issues.
- **Not ready to record:** listeners cannot understand core identity, chronology, climax, or ending.

Be direct. Recording a structurally broken script wastes narration time.

Keep two verdicts separate when relevant:

- **Text readiness:** the manuscript is editorially coherent and pronounceable in principle.
- **Render readiness:** the target human narrator or TTS engine has been sampled and essential names, numbers, pauses, and speaker turns are verified.
- **VoxCPM readiness:** plain-text punctuation, paragraphing, dialogue turns, and spoken-token forms are clean enough to render a representative sample before running the full job.

Never infer render readiness from the 100-point editorial score alone.

Block or downgrade render readiness when:

- a central reveal depends on a token likely to be misread;
- the climax or a multi-person scene has unclear speaker turns by ear;
- important pauses depend on unsupported markup or decorative punctuation;
- raw numbers/acronyms recur without a pronunciation decision;
- no dialogue-heavy or token-heavy sample has been listened to for a long render.

## Cold-Listening Checklist

- Can the first minute be understood without reading?
- Are scene changes verbally oriented?
- Are similar names separated?
- Are pronouns anchored?
- Are speakers clear in multi-person scenes?
- Are numbers and abbreviations pronounceable?
- Are punctuation, paragraph breaks, and dialogue turns strong enough for VoxCPM/TTS?
- Are raw dates/times/symbols/acronyms either rewritten for the ear or listed in a normalization ledger?
- Does the climax have enough reaction space?
- Does the ending leave an audible aftertaste?
- Are decorative separators or layout cues converted to spoken cues?
- Is the narrator voice consistent enough for a performer or TTS model?
