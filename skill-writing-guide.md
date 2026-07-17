---
name: skill-creator
description: Guides the creation, formatting, and optimization of Anthropic Claude Agent Skills. Use this skill when the user wants to design a new skill, format a SKILL.md file, fix YAML frontmatter upload errors, or optimize an existing prompt using progressive disclosure tiers (metadata, body, scripts, references).
---

# Agent Skill Writing Guide (Token-Optimized)

This document is meant to be reused: read the theory once, then use the **Template** at the end to create any new skill. The illustrative example throughout is an "audio story narration" skill.

---

## 1. What Is a Skill and Why Does It Save Tokens

A **skill** is a folder containing a `SKILL.md` file (required) plus optional supporting files. It teaches an agent a specialized workflow once, so you never have to paste the same long prompt again.

What makes a skill different from "a big prompt": the **progressive disclosure** mechanism — information is only loaded into context when actually needed, split across three tiers:

| Tier | Content | When loaded into context | Token cost |
|------|---------|--------------------------|------------|
| 1. Metadata | `name` + `description` | Always (at startup) | ~30–100 tokens/skill |
| 2. Body | Full `SKILL.md` | Only when the skill is triggered | Entire file |
| 3. Resources | `references/`, `scripts/`, `assets/` | Only when the agent needs a specific file | Only the file read |

Practical implications for token optimization:
- You can have **dozens of skills** active at once at almost no token cost, since each idle skill costs only ~80 tokens for its metadata.
- Detailed knowledge, long examples, lookup tables → push down to `references/`, do not cram into `SKILL.md`.
- Repetitive work, computation, data processing → write as `scripts/`. The agent **runs the script without loading its code into context** (only the output enters context). This is the single biggest token saving — especially effective for data-heavy work like parsing HTML, normalizing tables, and so on, which belong in scripts rather than prose descriptions.

---

## 2. Folder Structure

```
my-skill/
├── SKILL.md          (required: YAML frontmatter + Markdown instructions)
├── scripts/          (optional: executable code for repetitive/computational tasks)
├── references/       (optional: detailed documentation, read on demand)
└── assets/           (optional: templates, fonts, icons… used in output)
```

Only `SKILL.md` is required. Add the other three folders only when genuinely needed. Do not create empty placeholder files.

---

## 3. YAML Frontmatter — The Most Important Part for Triggering

The top of `SKILL.md` is a YAML block between two `---` lines. Only **2 fields are required**: `name` and `description`.

```yaml
---
name: audio-story-narration
description: Converts or writes story text into a script optimized for AI/TTS voice reading. Use when the user mentions "audio story", "narration script", "convert story to audio", "make this listenable", or submits a story chapter and wants it to sound natural and well-paced when read aloud. Also triggers when they just say "make this sound good when read out" without mentioning "audio" explicitly.
---
```

### How to Write a Good `description`

`description` is the **only mechanism** that determines whether the agent invokes a skill. The agent reads only `name` + `description` to decide, so it must cover two things:

1. **What the skill does** (what).
2. **When to use it** (when) — list specific phrases and contexts the user actually types.

Practical rules:
- **Be a little pushy.** Claude tends to *under-trigger* (not calling a skill even when it should). Add a sentence like "Use this skill whenever the user mentions X, Y, or Z — even if they don't name the skill explicitly."
- **Use real keywords.** Include the exact phrases users type (including slang, abbreviations, file extensions like `.docx`, `.xlsx`…).
- **All "when to use" belongs here**, not in the body.
- **Write in third person**, describing the situation — not as a greeting or introduction.

Comparison example:

> ❌ Weak: `description: Process inventory data.`
>
> ✅ Strong: `description: Normalizes and extracts pharmaceutical/chemical inventory data from Google Sheets HTML exports into Markdown for agent consumption. Use when the user mentions product codes, batch tracking, label templates, multi-column HTML files, or wants to convert an inventory table to Markdown — even if they just say "make this readable for the agent".`

---

## 4. Writing the `SKILL.md` Body

After the frontmatter comes the Markdown instructions. This is the "manual" the agent reads when the skill activates.

### Core Principles

**Explain *why*, don't just issue commands.** Modern LLMs have strong reasoning and theory of mind. If you explain the reasoning behind a step, the agent handles edge cases you never anticipated. In contrast, instructions filled with rigid `ALWAYS` / `NEVER` in all caps produce mechanical behavior that breaks on unusual inputs. Use clear imperative sentences, but include the reason.

> ❌ `ALWAYS split long sentences into short ones.`
>
> ✅ `Split sentences longer than 25 words into shorter ones, because TTS voices run out of breath and sound confused on heavily nested clauses.`

**Keep the body concise — ideally under 500 lines (~5,000 tokens).** If you exceed this, move content into `references/` and link to it. The body should contain only: the main workflow, branching logic, and pointers to supporting files.

**Write generically, not for a single example.** A skill may run thousands of times on very different inputs. If it only works correctly for the one example you tested, it is useless.

### Useful Body Patterns

**Fixed output format** — give the agent a clear template:

```markdown
## Audio Script Structure
Always use this exact frame:
[OPENING] — 1–2 lead sentences, slow pace.
[BODY]    — divided by scene, each scene separated by a blank line.
[CLOSING] — final hook that teases the next chapter.
```

**Input → Output examples** — highly effective; agents learn quickly from concrete samples:

```markdown
**Example 1:**
Input:  "He drew his sword, steel flashing in the dark, and before the enemy could react his head had left his shoulders."
Output: "He drew his sword. Steel flashed in the dark. The enemy never had a chance to react — his head left his shoulders."
(Why: splitting the rhythm lets the voice actor create dramatic pauses.)
```

**Checklist for complex workflows** — the agent can copy this and tick items off:

```markdown
## Pre-export Checklist
- [ ] Numbers/symbols converted to readable words (e.g. "3" → "three", "%" → "percent")
- [ ] Pronunciation hints added for difficult proper nouns (first appearance only)
- [ ] Long sentences split, pauses added
- [ ] Non-speakable characters removed (emoji, ***, ---)
```

---

## 5. When to Use scripts / references / assets

This is where you decide whether a skill is truly token-optimized.

### `scripts/` — for deterministic, repetitive, or computational work
If a task is faster, more accurate, and more repeatable as **code** than as LLM-generated text — write a script. The agent runs it and **only the output enters context; the code itself does not**.

Signs a task belongs in a script: sorting/filtering large lists, parsing HTML/XML, normalizing formats, validating data, applying rule-based bulk replacements. (For data-heavy workflows: a `normalize_numbers.py` script that converts digits and units to spoken words will be reused every time, rather than re-describing those rules in prose on every run.)

Important: the API environment **has no network access and does not auto-install packages**. List required packages explicitly in `SKILL.md` and only use what is already available. Don't write "use the pdf library" without specifying where it comes from.

### `references/` — for detailed documentation read on demand
Long lookup tables, genre-specific rules, extended examples → put them here. In `SKILL.md`, one line is enough: "For cultivation-fantasy genre, read `references/xianxia.md` for terminology pronunciation rules."

For reference files longer than 300 lines, add a table of contents at the top so the agent can jump to the right section.

When a skill serves **multiple variants or genres**, organize by variant so the agent reads only one file:

```
audio-story-narration/
├── SKILL.md              (general workflow + branching logic)
└── references/
    ├── xianxia.md
    ├── urban.md
    └── romance.md
```

### `assets/` — files embedded in the output
Templates, fonts, icons, fixed opening/closing segments… Things that are *inserted into the output*, as distinct from references (things to *read and understand*).

---

## 6. Seven Token-Optimization Principles (Quick Reference)

1. **Keep metadata concise but keyword-rich.** It is always in context, so don't pad it — but it must be complete enough to trigger correctly.
2. **Keep the body under 500 lines.** If it exceeds that, split content into `references/`.
3. **Push detail to Tier 3.** Lookup tables, long examples, branch-specific rules → `references/`; only link from the body.
4. **Repetition and computation → `scripts/`.** Running code is cheaper than generating text, and code doesn't consume context tokens.
5. **Organize by variant** so the agent loads only the one reference file it needs.
6. **Don't re-describe what the agent can already do.** If Claude handles a step well on its own, don't rewrite it — write only what is specialized or error-prone.
7. **Cut the filler.** After writing a draft, read it with fresh eyes and delete every sentence that contributes nothing to the outcome.

---

## 7. Skill Creation Workflow (Follow in Order)

1. **Define intent:** what does the skill do? When does it trigger? What is the output format?
2. **Write a draft** `SKILL.md` (frontmatter + body).
3. **Test with 2–3 real prompts** — the kind of sentence a real user would actually type, not a clean ideal-case sentence.
4. **Evaluate the results** and revise the skill. If across multiple test runs the agent independently writes the same helper code every time → that is a signal to bundle it into `scripts/`.
5. **Repeat** until satisfied.
6. **Refine the `description`** last, to tune triggering (try a few should-trigger and should-not-trigger sentences and check whether the skill activates correctly).

Triggering tip: overly simple single-step requests (e.g. "read this file") often do **not** trigger a skill even when the description matches, because the agent can handle them directly. Good test prompts must be substantive enough that the agent sees value in consulting the skill.

---

## 8. Full Example: "Audio Story Narration" Skill

A complete `SKILL.md` to use as a reference model.

````markdown
---
name: audio-story-narration
description: Converts story text into a script optimized for AI/TTS voice reading, or writes original audio story content. Use when the user mentions "audio story", "narration script", "convert story to audio", "make this listenable", or submits a story chapter wanting it to sound natural, well-paced, and correctly pronouncing character names. Also triggers when they say "make this sound good when read aloud" without using the word "audio".
---

# Audio Story Narration

Transforms story text (typically translated or converted web novels) into a script that an AI voice reads naturally, at the right pace, without stumbling.

## Workflow

1. **Identify the genre** to select the right terminology handling. For cultivation fantasy (xianxia), read `references/xianxia.md`; for urban fiction read `references/urban.md`. Genre determines how to pronounce domain-specific terms.

2. **Normalize unreadable symbols** using the script, because doing it manually causes inconsistencies and omissions:
   ```bash
   python scripts/normalize.py input.txt > step1.txt
   ```
   The script converts digits to words ("3 years" → "three years"), symbols to words ("%" → "percent"), and strips emoji/`***`/`---` (which TTS voices would read as "asterisk asterisk asterisk").

3. **Split sentence rhythm.** Sentences longer than 25 words, or with multiple nested clauses, cause TTS voices to run out of breath and sound confused. Break them into shorter sentences; use em dashes to create dramatic pauses.

   Example:
   Input:  "He drew his sword, steel flashing in the dark, and before the enemy could react his head had left his shoulders."
   Output: "He drew his sword. Steel flashed in the dark. The enemy never had a chance to react — his head left his shoulders."

4. **Add pronunciation hints for difficult proper nouns.** For names that are likely to be mispronounced, add a phonetic hint in parentheses on first appearance. Listeners can't see the text, so a mispronounced character name breaks immersion.

5. **Export using this structure:**
   ```
   [OPENING] — 1–2 lead sentences, slow pace.
   [BODY]    — divided by scene, each scene separated by a blank line.
   [CLOSING] — final hook that teases the next chapter.
   ```

## Pre-export Checklist
- [ ] Ran `scripts/normalize.py` (numbers, symbols, junk characters)
- [ ] Split long sentences and added pauses
- [ ] Added pronunciation hints for difficult proper nouns (first appearance)
- [ ] Verified no characters remain that the voice engine cannot speak

## Environment Requirements
Standard Python library only — no additional packages required.
````

This skill folder would also include `scripts/normalize.py` and the `references/*.md` files referenced above.

Key observations from the example, mapped back to the 7 principles:
- Symbol normalization → **script** (Tier 3, zero context tokens, consistent results).
- Genre-specific rules → **separate `references/` files**; agent reads only the one it needs.
- Body is short; every step **includes a reason** ("because TTS voices run out of breath…").
- `description` lists real keywords and adds the "even when they don't say audio explicitly" clause.

---

## 9. Blank Template — Copy to Create Any New Skill

Copy the block below, fill it in, and rename the folder and files. Delete optional sections you don't need.

````markdown
---
name: skill-name-lowercase-hyphenated
description: [ONE SENTENCE: what the skill does]. Use when the user [list real phrases/contexts they actually type], or when [implicit situation]. Also triggers when they don't name the skill explicitly but [describe the underlying need].
---

# [Readable Skill Title]

[1–2 sentences: what this skill enables the agent to do.]

## Workflow

1. [Step 1 — include *why* if this step is easy to get wrong.]
2. [Step 2. If there is repetitive/computational work → point to scripts/process.py and explain what the script does.]
3. [Step 3. If there are branches by input type → point to references/<type>.md.]

## Output Format
[Fixed frame the agent must follow, if applicable.]

## Example
Input:  [a real case]
Output: [desired result]
(Why: [reason for this choice].)

## Pre-export Checklist
- [ ] ...
- [ ] ...

## Environment Requirements (if using scripts)
[List required packages; note if the standard library is sufficient.]
````

**Final reminder:** write the draft → read it with fresh eyes → cut the filler → test with a few real prompts → revise. A good skill is concise, explains the *why* behind its instructions, and offloads heavy work to `scripts/` and `references/`.
