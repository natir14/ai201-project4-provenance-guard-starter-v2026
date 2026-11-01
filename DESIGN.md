# Provenance Guard — Milestone 1 design

The paper trace for one submission, written before any endpoint is built.
Nothing here is implemented yet. `/submit` and `/appeal` still return `501`.

Scores run **0.0 (confidently human) → 1.0 (confidently AI)** everywhere: in
both signals, in the combined score, and in the log.

> **Status: design proposals, not measured results.** Every threshold,
> weight, length limit, cap and style-signal rule below is a proposal until
> it is implemented and tested in Milestones 3–5. The values already in
> `config.py` (weights 0.5 / 0.5, thresholds 0.35 / 0.65) and the detector's
> curve (midpoint 45, steepness 1.6) are starter placeholders. No score in
> this document comes from running the pipeline.

---

## 1. The submission flow

1. **The writer sends text.** `POST /submit` with `{"text", "creator_id"}`.
   Nothing about the writer is known beyond `creator_id`.

2. **The route checks the input before any model runs.** If the request is
   malformed (`text` or `creator_id` missing, not a string, or blank) or
   `text` is over the length cap, the route answers `400` / `413` and writes
   a `rejected` entry with `audit.log_rejection`. No score and no label are
   produced. A rejection is never a verdict on the writer.

3. **The submission gets an identity.** A `content_id` (`uuid4`) is
   created now, before scoring, so every later step and the eventual
   appeal refer to the same id.
   **Short-text branch:** if the text is valid but too short for the signals
   to mean anything (a short poem, a haiku), the route stops here. It
   answers `200` with `guess: "insufficient_evidence"`, null scores and a
   neutral sentence, and logs that outcome with `log_decision`. No signal
   runs, nothing is combined, and nothing about the writer is implied.

4. **Signal one: predictability.** `detector.model_signal(text)` runs gpt2
   locally, measures perplexity on the first 400 tokens, and squashes it
   to `model_score`. If the model can't load, the route answers `503` and
   **does not label**. A label built on one signal is not offered as if it
   used two.

5. **Signal two: shape.** `stylometry.style_signal(text)` measures
   sentence-length spread, vocabulary variety and punctuation, and gives
   `style_score`. It reads the whole text, not just the first 400 tokens.

6. **Combine, then translate for a person.**
   `scoring.combine_signals(model_score, style_score)` gives
   `combined_score`. `scoring.score_to_label(combined_score)` turns that into
   a `guess` (`human` / `unsure` / `ai`) and a plain-language `label`
   sentence. (The combining rule itself is a Milestone 4 decision.)

7. **Log, then answer, with the appeal route in the response.**
   `audit.log_decision(...)` writes all nine fields with
   `status: "decided"`, and the response returns the same values plus how to
   appeal. If the writer disagrees, they call `POST /appeal` with the
   `content_id`. That adds an `appeal` entry, and the item moves to
   `under_review`. The original decision is never overwritten.

```
writer ─POST /submit─▶ validate ──bad──▶ 400/413 + log_rejection
                          │ok
                          ▼
                    content_id ──too short──▶ 200 insufficient_evidence + log_decision
                          │enough text
                          ▼
                    model_signal ─▶ style_signal
                                         │503 if model missing (no label)
                                         ▼
                    combine_signals ─▶ score_to_label ─▶ log_decision ─▶ 200
                                                                   │
writer ─POST /appeal (content_id, reasoning)─▶ log_appeal ─▶ under_review
```

---

## 2. The two signals

They have to measure **different things**. If they only made the same
mistake twice, a second signal would add false confidence, not evidence.

### Signal one — `detector.py` (the model signal) · given

| | |
|---|---|
| **Measures** | Perplexity: how surprised gpt2 is by each next token, averaged over the first 400 tokens. A logistic curve on perplexity (midpoint 45, steepness 1.6) maps it to 0–1. Low perplexity → high score. |
| **Why it might differ** | A language model writes by picking likely next tokens, so its output is text a model finds easy to predict. Human writing wanders more: specific details, odd word choices, abrupt turns. |
| **Output** | `model_score` 0–1, higher = more likely AI. |

**What it can't see (limitations):**

- **Predictability is not authorship.** Plain writing, with common words in
  short ordinary sentences, scores as machine-like. That describes
  second-language writers, younger writers, and anyone writing simply on
  purpose. These are the writers it is most likely to accuse, and the
  ones least able to argue back. **This is the main false positive this
  design has to absorb.** It is structural, not a bug.
- **The reverse also happens.** Dense, ornate prose with rare words reads as
  *human*, and AI text that is paraphrased or sampled at high temperature
  gains perplexity and slips through.
- **Formulaic genres score as AI no matter who wrote them.** Examples are
  recipes, instructions, legal boilerplate, and well-known quotations gpt2
  has effectively memorised.
- **It only reads the first 400 tokens** (`DETECTOR_MAX_TOKENS`). Whatever
  comes after that is invisible to it, so a human opening followed by AI
  text (or the reverse) is judged on the opening alone.
- **Short text is unstable.** A few sentences give a noisy perplexity, and
  under 3 tokens it raises `ValueError`.
- **gpt2 is a 2019 model.** It is a stand-in for whatever model actually
  wrote the text, so its idea of "predictable" is not that model's.

### Signal two — `stylometry.py` (the style signal) · to build in Milestone 4

*Everything in this subsection is a proposal. The measures, window size,
clamping anchors, directions and neutral-0.5 rule all have to be checked
against the Milestone 4 calibration inputs before they count as decisions.*

| Measure | Proposed computation | Proposed: points toward AI when… |
|---|---|---|
| `sentence_length_spread` | stdev ÷ mean of words-per-sentence (coefficient of variation) | spread is **low**: sentences march in step |
| `type_token_ratio` | moving-average TTR over 50-word windows, so long and short texts compare fairly | variety is **low** |
| `punctuation_density` | non-terminal punctuation (`, ; : — – ( ) "`) per sentence, plus how many *kinds* appear | to be settled in calibration (see note) |

Each measure gets clamped onto 0–1 between calibration anchors and flipped
so that higher = more AI-like. `style_signal` then averages them.
**Undefined cases score neutral (0.5), never AI.** Examples are a
one-sentence submission with no spread, or a text too short for a 50-word
window. Missing evidence should not count against the writer.

> **Note on punctuation direction.** The starter's intuition is "less varied
> punctuation → more AI". Current chat models often over-use commas and em
> dashes, which would point the other way. I'll check the direction on the
> four Milestone 4 calibration inputs before committing to it. If it doesn't
> separate them, it gets a low weight.

**Why it might differ:** "most likely next word" produces even, mid-length
sentences and a narrower vocabulary on average. Human writing is lumpier,
with a three-word sentence next to a forty-word one.

**What it can't see (limitations):**

- **It cannot read.** It has no idea what the text says. Anything that
  changes the shape without changing the substance moves it, and that is
  cheap to do on purpose:
  - typos raise vocabulary variety → reads more human
  - breaking long sentences up, or merging short ones, changes spread
  - a pasted quotation or list changes all three measures
- **It shares signal one's worst blind spot.** A plain writer using short,
  even sentences and a small, sure vocabulary looks AI-like on spread *and*
  on variety. So for the false-positive case, the second signal tends to
  **agree with the first rather than correct it**. The two signals are not
  independent there, and the combining rule and thresholds have to allow
  for that.
- **Short text is noisy.** Three sentences don't have a meaningful
  "spread".
- **Genre and format.** Poems, bullet lists, dialogue and code all have
  shapes that have nothing to do with who wrote them.
- **English-only assumptions.** The sentence splitter and word regex expect
  English punctuation and ASCII words.

---

## 3. JSON contracts

### `POST /submit`

**Request**

```json
{
  "text": "The full piece of writing, at least a few sentences long...",
  "creator_id": "writer-042"
}
```

| Field | Rule |
|---|---|
| `text` | required, string, not blank after trimming, ≤ 20,000 characters (proposed cap) |
| `creator_id` | required, non-blank string (also the unit 8 rate-limit key) |

There is **no minimum length for a valid request.** A four-line poem is a
legitimate submission. Short text is not refused. It gets the
insufficient-evidence response below.

**200 — decided**

```json
{
  "content_id": "3f2b8c1e-5d4a-4f7e-9a0b-6c1d2e3f4a5b",
  "creator_id": "writer-042",
  "guess": "unsure",
  "confidence": 0.18,
  "label": "<the reader-facing sentence for this band — written in Milestone 5>",
  "model_score": 0.61,
  "style_score": 0.48,
  "combined_score": 0.55,
  "status": "decided",
  "appeal": {
    "how": "POST /appeal with this content_id and your reasoning",
    "content_id": "3f2b8c1e-5d4a-4f7e-9a0b-6c1d2e3f4a5b"
  }
}
```

- `model_score` and `style_score` are **always** in the response, not just
  the log. Unit 8's tools read them straight off it.
- `confidence` = `abs(combined_score − 0.5) × 2`, rounded to 2 places: 0 at
  the midpoint, 1 at either extreme. **It is an uncalibrated, score-based
  indicator. It is not a probability that the prediction is correct.** It
  only says how far the combined score sits from 0.5. Nothing has measured
  how often a `0.8` turns out right, and nothing should be read as if it
  had. It is never shown to the writer as a percentage or as "80% sure". An
  `unsure` result will always carry a low value.
- `label` is the only field written for a person. Every other field is for
  machines and for the log.

**200 — insufficient evidence** (text valid but too short to score reliably)

```json
{
  "content_id": "9a7d0c3b-1e2f-4a5b-8c6d-7e8f9a0b1c2d",
  "creator_id": "writer-042",
  "guess": "insufficient_evidence",
  "confidence": null,
  "label": "This piece is too short for us to assess, so we haven't made any judgment about it.",
  "model_score": null,
  "style_score": null,
  "combined_score": null,
  "status": "decided",
  "reason": "too_short_to_assess",
  "appeal": {
    "how": "POST /appeal with this content_id and your reasoning",
    "content_id": "9a7d0c3b-1e2f-4a5b-8c6d-7e8f9a0b1c2d"
  }
}
```

- **Not suspicious, and not an error.** It is a `200`, not a `4xx`, and it
  is logged with `log_decision`, not `log_rejection`. The label makes no
  claim in either direction. It says the system didn't look, not that the
  writing looked odd.
- **The cut-off is a proposal:** under about 50 words, *or* under 3
  sentences, pending Milestone 4. The test will be to score short texts of
  known origin and see below what length the signals stop telling them
  apart. The detector's own hard floor (fewer than 3 tokens raises
  `ValueError`) sits far below this, so the branch also stops that error
  from ever reaching the writer.
- Scores are `null`, not computed-and-hidden, because a number from a few
  words is noise that invites being read as evidence.
- This adds a fourth `guess` value. It is **outside** the three score-band
  labels. Those three still cover the whole 0–1 range of `combined_score`
  for text long enough to score.
- An appeal is still accepted on it. It just should rarely be needed.

**Field names, checked against the starter.**

| Field | Required by | Present |
|---|---|---|
| `content_id`, `guess`, `confidence`, `label`, `model_score`, `style_score` | `app.py::submit` docstring; read off the response by `run_attacks.py` and `run_eval.py` | ✓ in every 200 |
| `timestamp`, `content_id`, `creator_id`, `guess`, `model_score`, `style_score`, `combined_score`, `label`, `status` | the nine audit fields in `audit.log_decision` | ✓ in every decision log entry |
| `creator_id`, `combined_score`, `status`, `appeal`, `reason` | not required | extras: harmless, since the tools read fields by name with `.get()` |

On error responses those six fields are simply absent, and the unit 8 tools
record them as `null` without crashing.

**Errors.** Every error has the same shape and is written to the log with
`log_rejection`:

```json
{ "error": "invalid_input", "field": "text", "message": "Text is too short to assess — please submit at least a few sentences." }
```

| Status | `error` | When |
|---|---|---|
| 400 | `invalid_input` | body isn't a JSON object; `text` / `creator_id` missing, wrong type, or blank |
| 413 | `too_long` | text over the cap |
| 503 | `detector_unavailable` | model can't load: **no label is issued** |
| 429 | `rate_limited` | unit 8; handler already exists in `app.py` |

Note: `run_attacks.py::auto_verdict` marks **every 5xx as BROKE**, so a `503`
during an attack run counts against the service. That's the right call. A
service that can't load its model *is* down. It still beats a 500 or a label
built on one signal.

**Log entry written** (`audit.log_decision`, all nine fields + `text_length`):

```json
{"timestamp": "2026-11-01T18:04:12+00:00", "content_id": "3f2b8c1e-...", "creator_id": "writer-042",
 "guess": "unsure", "model_score": 0.61, "style_score": 0.48, "combined_score": 0.55,
 "label": "<label text>", "status": "decided", "text_length": 1184}
```

The submitted text itself is **not** logged, only its length. The log is
evidence about decisions, not a copy of people's writing.

### `POST /appeal`

**Request**

```json
{
  "content_id": "3f2b8c1e-5d4a-4f7e-9a0b-6c1d2e3f4a5b",
  "reasoning": "I wrote this myself. English is my second language, so I keep my sentences simple. I have my handwritten draft."
}
```

| Field | Rule |
|---|---|
| `content_id` | required; must match a submission logged with `log_decision`, found with `audit.entries_for` (rejections have no `content_id`) |
| `reasoning` | required, non-blank string, ≤ 2,000 characters |
| `creator_id` | optional. If sent, it must match the original submission's. If omitted, it's taken from the original entry |

**200 — appeal recorded**

```json
{
  "content_id": "3f2b8c1e-5d4a-4f7e-9a0b-6c1d2e3f4a5b",
  "status": "under_review",
  "previous_status": "decided",
  "original_guess": "ai",
  "message": "Thanks — your appeal is recorded and a person will review this decision. The original label is paused while they do.",
  "appealed_at": "2026-11-01T18:09:40+00:00"
}
```

**Errors.** These are also written with `log_rejection`, so a mistyped id
leaves a trace instead of failing silently:

| Status | `error` | When |
|---|---|---|
| 400 | `invalid_input` | missing / blank `content_id` or `reasoning`, or reasoning over the cap |
| 404 | `unknown_content_id` | no decision with that id: the message tells the writer to check it |
| 403 | `creator_mismatch` | `creator_id` given and it isn't the original submitter |
| 409 | `already_under_review` | an appeal for this id already exists; the response says so, and it isn't an error on the writer's part |

**Log entry written** (`audit.log_appeal`). It is appended after the
original decision, which stays untouched:

```json
{"timestamp": "2026-11-01T18:09:40+00:00", "content_id": "3f2b8c1e-...", "creator_id": "writer-042",
 "event": "appeal", "status": "under_review", "reasoning": "I wrote this myself. ..."}
```

There is **no automatic re-scoring** on appeal. The same text through the
same signals gives the same answer, so re-running them would only look like
a review. The appeal goes to a person.

---

## 4. A false-positive scenario, and the appeal

> **This scenario is hypothetical.** It has not been run through the model or
> the scoring pipeline, which doesn't exist yet. It shows how the documented
> blind spots *could* combine into a wrong accusation. It does not report a
> classification the system made. Whether this text actually reaches
> high-confidence AI depends on signal two and the combining rule, both
> still to be built and tested.

**The writer (fictional).** Amina is a nurse who moved to Canada two years ago. English
is her second language. She submits a short personal essay to a community
writing site. She writes carefully, sticking to words she's sure of:

> *I came to Canada two years ago for work. I am a nurse in a small
> hospital. My job is hard but I like it. Every day I help many people. Some
> patients are old and they are alone. I talk with them and I try to make
> them happy. After work I am very tired. I go home and I cook dinner for my
> family. On the weekend we go to the park. My children play and I rest. I
> miss my country but I am happy here. I want to learn more English so I can
> do a better job.*

**What the service could do to her.** This is a reasoned trace from the
documented blind spots, with no numbers attached. The first real check is
`python detector.py "<the text above>"` once Milestone 3 is reached.

| Step | What could happen | Why |
|---|---|---|
| Validate | passes; long enough to score (≈ 95 words, 12 sentences) | — |
| Signal one | `model_score` could be on the high side | common words in short ordinary sentences → low perplexity. This is the blind spot `detector.py` itself names. |
| Signal two | under the proposed measures, `style_score` could also lean high | 12 sentences of 5–12 words → low spread; "I", "and", "my", "am" repeat → low variety; almost no commas → low punctuation |
| Combine | if both lean high, nothing pulls the score back | in this case the second signal would *confirm* the first one's mistake instead of catching it |
| Label | possibly **high-confidence AI** | not confirmed; depends on the untested rule and thresholds |

If it did land there, every word would still be hers. She would be wronged
for a structural reason, not a random one, and so would every writer like
her. That possibility is what the appeal path and the threshold choices have
to be designed around.

**How she would appeal.** The response she got contains her `content_id` and the
appeal instructions, so she sends:

```json
{
  "content_id": "<her content_id>",
  "reasoning": "I wrote this myself about my own life. English is my second language, so I use simple words and short sentences on purpose. I can share my draft."
}
```

**What changes:**

1. `/appeal` finds her `content_id` in the log and checks there isn't
   already an open appeal.
2. `log_appeal` appends an `appeal` entry. Her item is now `under_review`.
3. She gets a `200` telling her a person will look at it and the label is
   paused. It does not say "the system stands by its decision".
4. The log now shows, in order: the decision with both signal scores, then
   her appeal with her reasoning. A reviewer can see *why* it was flagged
   (two high scores driven by plain style), not just *that* it was.

**What this scenario asks of later milestones** (design notes, not
criteria):

- The thresholds and combining rule (M4/M5) should make it **hard** for plain
  writing to reach high-confidence AI. If the two signals turn out to agree
  on plain writing, a simple average won't stop it. Milestone 4 should test
  that directly.
- The high-confidence AI label (M5) must not read like a final verdict. It
  should point to the appeal in the same sentence.
- The `unsure` label must not read as an accusation either, because Amina is
  exactly the kind of person who will see it.
