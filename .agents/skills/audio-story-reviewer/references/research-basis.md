# Research Basis and Evidence Guardrails

Use this reference when calibrating the review method, resolving disagreement about a rule, or extending the skill. It summarizes research that materially changes the editorial workflow. It is not a literature review and should not be loaded for every manuscript.

## Contents

1. Evidence policy
2. Narrative comprehension
3. Goals, causality, and memory
4. Event boundaries and audio orientation
5. Tension and suspense
6. Vietnamese person reference
7. Listening and modality
8. TTS normalization and prosody
9. Unsupported shortcuts to avoid
10. Sources

## Evidence Policy

Keep three levels separate:

- **Research finding:** an observed result or a model supported by cited research.
- **Editorial inference:** a practical test derived from that finding.
- **Local heuristic:** a useful convention that has not been validated as a universal threshold.

Never present an editorial inference as a law of cognition. Genre, audience, performance, narrator skill, platform, and manuscript purpose can change the result.

Treat counts from `statistics.py`, tension scores, dialogue ratios, sentence-length flags, and the 100-point rubric as local heuristics. They organize attention; they do not prove quality.

## Narrative Comprehension

Research on situation models and event indexing shows that comprehenders track changes in protagonist, time, space, causality, and goals or intentions. Larger changes are associated with event boundaries and model updating.

Editorial inference:

- At every scene or major event boundary, check all five dimensions.
- When several dimensions change together, require stronger orientation than when only one changes.
- Do not demand explicit restatement of every dimension; require enough cues for a listener to update without guessing.

This supports the `boundary stack` test used in `narrator.md` and `audio.md`.

## Goals, Causality, and Memory

Narrative research consistently links comprehension and recall to causal connections and character goals. Active goals help organize attempts and outcomes; obsolete goals can be suppressed when a new goal takes over. Causally important moments are more likely to support a feeling of comprehension than merely adjacent moments.

Editorial inference:

- Track each major goal as active, blocked, achieved, abandoned, replaced, or forgotten.
- Require a visible trigger when the protagonist changes goals.
- Distinguish a deliberate abandoned goal from an author-forgotten promise.
- Test distant causes at later emotional or plot payoffs; listeners may need a compact reminder when the antecedent is remote or separated by several boundaries.

Do not equate chronological adjacency with causality. `A happened, then B happened` is weaker than evidence that A changed a decision, opportunity, belief, or constraint that produced B.

## Event Boundaries and Audio Orientation

Event-segmentation research indicates that people divide continuous activity into meaningful events, often around changes in characters, location, objects, goals, time, or causality. Boundaries help structure memory but also require the current event model to be updated.

Editorial inference:

- Treat scene changes, time jumps, location changes, goal changes, and POV changes as memory-update points.
- Re-anchor the minimum needed information immediately after a high-load boundary.
- Flag `boundary stacking`: several changes occur in one or two sentences with no stable anchor.
- Preserve deliberate disorientation in horror, mystery, or surreal fiction only when the listener can later reconstruct what changed.

## Tension and Suspense

The psychological model of Lehne and Koelsch describes tension as arising from conflict, instability, dissonance, or uncertainty about emotionally significant future outcomes. Tension is future-directed and depends on prediction, hope, fear, and the urge for resolution.

Editorial inference:

- Map the live question, plausible outcomes, their emotional difference, and what delays resolution.
- Do not score tension from event loudness alone. A quiet wait can carry high tension when outcomes matter.
- Distinguish suspense from surprise: suspense operates before an outcome; surprise occurs when an expectation is violated.
- A reveal that closes one question should create consequence, reaction, or a newly meaningful question if the story continues.

The model does not justify a universal rising curve, an ideal delay length, or a fixed number of hooks.

## Vietnamese Person Reference

Vietnamese person reference uses personal pronouns, kinship terms, names, titles, and status terms. These choices encode more than grammatical person: they can signal age, generation, kin relation, status, formality, solidarity, distance, evaluation, and emotional stance. Kinship terms also function outside literal families.

Editorial inference:

- Track both sides of a pair: how A names self to B and how A addresses B.
- Separately track how A refers to B when speaking to a third person and how the narrator refers to B.
- Treat public/private setting, audience, strategic politeness, concealment, region, and family convention as variables.
- Read a shift as a possible action: attack, distancing, submission, reconciliation, performance, or status claim.
- Do not "correct" marked forms to a neutral pair until the scene's social intention is understood.

## Listening and Modality

Research does not support a blanket claim that listening is inherently inferior to reading. One controlled study found no significant comprehension or retention difference among audiobook, e-text, and combined presentation for its adult sample and nonfiction material. Other spoken-narrative studies show that matching context improves comprehension and recall, while degraded acoustics can reduce memory for story details.

Editorial inference:

- Review the actual delivery condition instead of treating all audio as one medium.
- Prioritize context, clean referents, event orientation, and recoverable causal links.
- Mark the cold-listening pass as a production-risk simulation, not a universal cognitive test.
- If a voice, speed, music bed, or TTS engine is known, test that output; text-only judgment cannot certify final audio.

## TTS Normalization and Prosody

W3C SSML separates structure analysis, text normalization, pronunciation, and prosody. It also warns that automatic normalization is ambiguous and may differ across processors. Vietnamese TTS research identifies numbers, dates, ranges, abbreviations, URLs, email addresses, hashtags, contact names, foreign words, long sentences, and prosodic phrasing as practical problems.

Editorial inference:

- Build a pronunciation/normalization ledger for non-standard tokens.
- Specify intended spoken forms when a token has multiple readings.
- Test the target engine because punctuation and markup support vary.
- Use plain spoken Vietnamese as the portable baseline; use SSML only when the production pipeline supports it.
- Treat punctuation as one prosodic cue, not a guarantee of a natural pause.

## Unsupported Shortcuts to Avoid

Do not use or imply:

- a universal maximum sentence length;
- an ideal narration-to-dialogue ratio;
- a rule that tension must rise in every scene;
- a claim that more sensory detail always increases immersion;
- dopamine, oxytocin, mirror-neuron, or Zeigarnik explanations as story-engine laws;
- textual symptoms as proof that AI wrote the manuscript;
- a single total score as proof of recording readiness.

## Sources

- Zacks, Speer, and Reynolds, "Segmentation in Reading and Film Comprehension," *Journal of Experimental Psychology: General* 138(2), 2009. https://pmc.ncbi.nlm.nih.gov/articles/PMC8710938/
- Linderholm et al., "Suppression of Story Character Goals During Reading," *Discourse Processes* 37(1), 2004. https://pmc.ncbi.nlm.nih.gov/articles/PMC4266429/
- Chang et al., "Cognitive and Neural State Dynamics of Narrative Comprehension," *Journal of Neuroscience* 41(43), 2021. https://pmc.ncbi.nlm.nih.gov/articles/PMC8549535/
- Lehne and Koelsch, "Toward a General Psychological Model of Tension and Suspense," *Frontiers in Psychology* 6, 2015. https://doi.org/10.3389/fpsyg.2015.00079
- Smirnov et al., "Fronto-parietal Network Supports Context-dependent Speech Comprehension," *Neuropsychologia* 63, 2014. https://pmc.ncbi.nlm.nih.gov/articles/PMC4410787/
- Ward et al., "Effects of Age, Acoustic Challenge, and Verbal Working Memory on Recall of Narrative Speech," *Journal of Speech, Language, and Hearing Research* 59, 2016. https://pmc.ncbi.nlm.nih.gov/articles/PMC5096888/
- Rogowsky, Calhoun, and Tallal, "Does Modality Matter?" *SAGE Open* 6(3), 2016. https://doi.org/10.1177/2158244016669550
- Luong, *Discursive Practices and Linguistic Meanings: The Vietnamese System of Person Reference*. John Benjamins. https://benjamins.com/catalog/pbns.11
- Ton, "Markedness in Vietnamese Kinship Terms," University of New England seminar summary, 2016. https://www.une.edu.au/about-une/faculty-of-humanities-arts-social-sciences-and-education/hass/news-and-events/linguistics-seminars/markedness-in-vietnamese-kinship-terms
- Nguyễn Văn Khang, "Addressing in Vietnamese with Kinship Term and Their Use in Public Services Communication," *Ngôn ngữ và Đời sống*, 2014. https://vjol.info.vn/index.php/NNDS/article/view/20274
- Dang, Vuong, and Phan, "Non-Standard Vietnamese Word Detection and Normalization for Text-to-Speech," 2022. https://arxiv.org/abs/2209.02971
- Pham et al., "Improving Prosodic Phrasing of Vietnamese Text-to-Speech Systems," VLSP 2020. https://aclanthology.org/2020.vlsp-1.4/
- W3C, *Speech Synthesis Markup Language (SSML) Version 1.1*. https://www.w3.org/TR/speech-synthesis11/
