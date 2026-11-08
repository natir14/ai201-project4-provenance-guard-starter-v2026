# Provenance Guard

> ### 👋 Start here
>
> **New to this repo? Read [RUNNING.md](RUNNING.md) first.**
>
> Once `python test.py` passes, in one terminal:
>
> ```bash
> python app.py
> ```
>
> and in another:
>
> ```bash
> curl -X POST http://127.0.0.1:5000/ping \
>   -H "Content-Type: application/json" \
>   -d '{"message": "hello"}'
> ```
>
> That's a web service. Something sent it text and it sent something back.
> Everything this unit is filling in the middle.
>
> **The rest of this file is your submission.** Fill it in as you go.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     Unit 7 asks for the first five sections. Unit 8 adds the five below.

     Everything is pasted as TEXT. A pasted curl response gets full credit;
     a picture of your terminal gets none.
     ───────────────────────────────────────────────────────────────────────── -->

<!-- ═══════════════════════ UNIT 7 — THE BUILD ═══════════════════════ -->

## What This Does

<!-- The path a submission takes, from arriving to the label a reader sees.
     Six or seven steps — this is the trace you wrote in Milestone 1. -->

Provenance Guard takes a piece of writing and estimates whether it reads more
like a person or more like an AI model wrote it — and says so in plain
language, with a way to appeal. It is an estimate, not a verdict, and it is
**not calibrated**: no verified human writing has been run through it yet.

1. **The writer sends text.** `POST /submit` with `{"text", "creator_id"}`.
2. **The route checks the request before any model runs.** A body that isn't
   a JSON object, a missing/blank/non-string `text` or `creator_id` → `400
   invalid_input`; text over 20,000 characters → `413 too_long`. Each refusal
   is written to the audit log as a `rejected` entry. No score, no label, no
   `content_id` — a refusal is never a verdict on the writer.
3. **Too short to judge?** Under 50 words or under 3 sentences, nothing is
   scored: the answer is `200` with `guess: "insufficient_evidence"`, null
   scores and a neutral sentence. Short poems are legitimate, not suspicious.
4. **Signal one — predictability.** `detector.model_signal` runs GPT-2 on the
   writer's own machine and turns perplexity into `model_score` (0 = human-like,
   1 = AI-like). If the model can't load: `503 detector_unavailable` and **no
   label** — never a made-up score.
5. **Signal two — shape.** `stylometry.style_signal` measures how much sentence
   length and vocabulary vary, giving `style_score` on the same scale.
6. **Combine, then translate.** `scoring.combine_signals` averages the two
   scores into `combined_score`; `scoring.score_to_label` turns it into a
   `guess` and the sentence a reader sees; `scoring.confidence` says how far the
   score sits from a coin flip.
7. **Log, answer, and offer an appeal.** The decision is appended to
   `logs/audit.jsonl` with a new `content_id` (the submitted text itself is
   never logged, only its length), and the same values go back to the writer.
   If they disagree, `POST /appeal` with that `content_id` moves the item to
   `under_review` — appended after the decision, which is never overwritten.
   One appeal per item; a repeat gets `409 already_under_review`.

The full contracts are in [DESIGN.md](DESIGN.md). Where the build differs from
that Milestone 1 plan (confidence is also logged; punctuation is weighted 0;
the sentence splitter was fixed), the code and this README describe what was
built.

---

## Signals and Scoring

<!-- For each signal: what property it measures, why that might differ between
     human and AI writing, and WHAT IT CAN'T SEE.

     The blind spot is not optional. If you can't name it you don't understand
     the signal yet — and unit 8's attack set is built out of blind spots. -->

> **Calibration is incomplete.** Every number below — anchors, weights,
> thresholds — is provisional. The only texts scored so far were written by an
> AI (Claude, while building this), so nothing here measures accuracy.

### Signal one — the model signal

**What it measures:** How *predictable* the text is to GPT-2, running locally
(`detector.py`). It computes perplexity over the first 400 tokens and maps it
onto 0–1 with a logistic curve — midpoint 45 (scores 0.5), steepness 1.6, left
at the starter's values. Low perplexity → high `model_score` → more AI-like.

**Why that might differ between human and AI writing:** A language model writes
by repeatedly picking a likely next word, so its output tends to be text a
model finds easy to predict. People wander more — specific details, odd word
choices, abrupt turns.

**What it can't see:**
- **Predictability isn't authorship.** Plain writing — common words, short
  ordinary sentences — scores as machine-like. That describes second-language
  writers, younger writers, anyone writing simply on purpose: the writers this
  service is most likely to wrongly accuse. This is structural, not a bug.
- **The reverse fools it too.** Dense, unusual prose reads as human. A
  deliberately ornate paragraph *written by Claude* scored `model_score` 0.2553
  on the live server (see Label Variants).
- **Only the first 400 tokens** are read; anything after is invisible to it.
- Formulaic genres and famous quotations (which GPT-2 has effectively
  memorised) score as AI whoever wrote them. Short text gives noisy readings.
- GPT-2 is a 2019 model standing in for whatever model actually wrote a text.

### Signal two — the style signal

**What it measures:** The *shape* of the text, without reading it
(`stylometry.py`). Two measures count:
- **sentence-length spread** — standard deviation ÷ mean of words per sentence.
  Even sentences → AI-like (anchors: 0.20 scores 1.0, 0.70 scores 0.0).
- **vocabulary variety** — type-token ratio averaged over sliding 50-word
  windows, so length doesn't distort it. Repetitive → AI-like (0.60 → 1.0,
  0.80 → 0.0).

Each is scaled to 0–1 between its anchors and the two are averaged
(0.50 / 0.50). A measure the text is too short for counts as 0.5 — missing
evidence doesn't count against the writer. **Punctuation density is measured
but weighted 0**: in a calibration review it sat at or near "fully AI" on 7 of
8 samples (ordinary comma use read as AI), and its direction is unconfirmed.
The sentence splitter ignores abbreviations (Mr., Dr., e.g.) and splits
"Hello.World", so deleting spaces after full stops can no longer hide a text
from scoring.

**Why that might differ between human and AI writing:** "Most likely next
word" tends to produce even, mid-length sentences and a narrower band of
vocabulary on average. Human writing is lumpier — a three-word sentence next to
a forty-word one.

**What it can't see:**
- **It cannot read.** Typos, broken-up sentences or a pasted quotation move it
  without changing a word of substance — a cheap thing to do on purpose.
- **It shares signal one's worst blind spot.** Plain writing has even sentences
  and a small, sure vocabulary, so it leans AI on *both* measures. For plain
  writers the second signal tends to **agree** with the first, not correct it.
- **Vocabulary may point the wrong way for modern AI.** On every AI-written
  sample tried, including an obvious chatbot paragraph, vocabulary scored fully
  "human" (0.00): current models use broad, formal vocabulary.
- Still fooled by: lowercase after a missing space (`sat.the dog`), a quote
  after a full stop (`"Stop." She left.`), abbreviations not on its short list.
  English-only.

### The combining rule

<!-- Write the rule in words, then give the numbers. What happens when the two
     signals disagree? -->

**The rule:** A weighted average of the two signals, divided by the total
weight so it stays on 0–1. When they disagree, the result lands between them —
two methods splitting reads as uncertainty, not as either one winning. So a
confident label needs **both** signals to agree. Inputs outside 0–1, NaN, or
non-numbers are refused rather than clamped, and so are broken weights.

**The numbers:**
- `combined = (0.5 × model_score + 0.5 × style_score) ÷ (0.5 + 0.5)`, rounded
  to 4 places (`WEIGHT_MODEL_SIGNAL = WEIGHT_STYLE_SIGNAL = 0.5`).
- Labels: **human** below 0.35, **unsure** from 0.35 to 0.65 *inclusive*,
  **AI** above 0.65. So "human" needs model + style < 0.70, "AI" needs > 1.30.
- `confidence = round(|combined − 0.5| × 2, 2)` — 0 at 0.5, 1 at either end,
  at most 0.30 inside the unsure band. **Uncalibrated: it is not the
  probability that the guess is right**, and must never be shown as "80% sure".

**Where it lives:** `scoring.py::combine_signals`

<!-- ⚠️ The grader checks your code against that line. If your rule lives
     somewhere else, say where. -->

**A case where my two signals split, and what my rule does with it:**

A paragraph about a street that floods every October (written by Claude, so
AI-written), scored on the live server with **real GPT-2**:

| | score | reads as |
|---|---|---|
| `model_score` | **0.5046** | a coin flip |
| `style_score` | **0.2369** | fairly human — very uneven sentence lengths (8 to 29 words), varied vocabulary |
| `combined_score` | **0.3708** | **unsure** — confidence 0.26 |

The style signal pulls the score toward "human", but the model signal doesn't
agree, so the average stops in the unsure band. Two things this case shows:

- **The rule can still be wrong in the comfortable direction.** Before the
  splitter fix, "Mr. Okafor" was split into a fake 3-word sentence, the style
  score was 0.1431, and the combined score 0.3239 — *below* 0.35, so this
  AI-written text would have been labelled **human**.
- **When both signals agree, the rule follows them — even when both are
  wrong.** A deliberately ornate Claude-written paragraph got `model_score`
  0.2553 and `style_score` 0.0 → combined 0.1277 → **human**. That's a false
  negative, live.

(Offline/mocked, for contrast: in an end-to-end test with GPT-2 *mocked* at
0.95, the same flooding text still combined to 0.5935 → unsure.)

---

## Label Variants

<!-- The exact text of all three labels, as a reader would see them, and the
     score range each covers.

     Write them for someone who has never heard the word "threshold". -->

| Label | Score range | The exact text a reader sees |
|---|---|---|
| high-confidence human | below 0.35 | This text shows patterns more consistent with human writing. This is an automated estimate, not proof of authorship. |
| unsure | 0.35 to 0.65 (both ends included) | The available signals do not support a reliable classification. No conclusion about authorship should be drawn from this result. |
| high-confidence AI | above 0.65 | This text shows patterns associated with AI-generated writing. This result is not proof of AI use, and you can request a human review if you disagree. |

A score exactly on 0.35 or 0.65 is "unsure": a score sitting on the line
doesn't earn a confident label. Text too short to score gets a fourth,
separate response — "This piece is too short for us to assess, so we haven't
made any judgment about it." — outside these three bands.

**Why I worded the "unsure" one this way:**
<!-- It's the hardest of the three. It has to admit uncertainty without
     sounding like an accusation, because the person reading it may well have
     written every word themselves. -->

The person reading it may have written every word, so it says nothing about
*them* — only about the evidence: the signals "do not support a reliable
classification". It doesn't lean either way ("may be AI" would still be an
accusation), and it tells the reader what to do with the result: draw no
conclusion. It also avoids numbers and the word "confidence", because a
writer reading "52% AI" would hear an accusation the system can't back up.

**All three labels reached with real text.** Submitted to the local server with
real GPT-2 on 2026-11-01. ⚠️ **Every one of these texts was written by Claude**
— so they show the labels are reachable, *not* that they're right. The
"human" result is a false negative.

| Text (AI-written) | `content_id` | model | style | combined | label |
|---|---|---|---|---|---|
| ornate pantry memory | `2da075d2-fe8b-42b3-b166-967cf3664475` | 0.2553 | 0.0 | 0.1277 | **human** |
| flooding street | `a1f40d9d-34da-4691-a1d1-b0fbc814ec72` | 0.5046 | 0.2369 | 0.3708 | **unsure** |
| workplace communication (Sample Run) | `c12306dc-76ab-4325-991e-c9772a6c3ef6` | 0.6018 | 0.5 | 0.5509 | **unsure** |
| chatbot-style time management | `561e4ff0-7eef-400c-97e7-d2a00963c47d` | 0.8236 | 0.5 | 0.6618 | **AI** |
| repetitive "The system is good." | `27c9b50b-b10e-48a6-b621-20edfa7b1033` | 0.972 | 0.723 | 0.8475 | **AI** |

All five decisions are in `logs/audit.jsonl`. No verified human writing has
been scored yet, so the false-positive risk for plain human writers is
**untested** (criteria 1–3 need it).

---

## Sample Run

<!-- One submission and one appeal, pasted as text: the request, the response,
     and the log entries. -->

**A submission**

<!-- The response needs content_id, guess, confidence, label, AND both
     signal scores - model_score and style_score. Unit 8's tools read those
     two off the response, so leaving them out costs you next unit's
     diagnostics. -->

Run against the local server (`python app.py`) with real GPT-2 on
2026-11-01. The sample text was written by Claude for this run — it is
AI-written, and the service called it "unsure".

```bash
$ curl -X POST http://127.0.0.1:5000/submit \
  -H "Content-Type: application/json" \
  -d '{"text": "In the modern workplace, effective communication has become an essential skill for teams of every size. By setting clear expectations, sharing updates regularly, and listening actively, colleagues can significantly reduce misunderstandings. Furthermore, adopting shared tools such as project boards and team chat can help keep everyone aligned. Ultimately, strong communication not only improves results but also builds trust and supports a healthier working environment.", "creator_id": "sample-writer"}'
```

```json
{
  "appeal": {
    "content_id": "c12306dc-76ab-4325-991e-c9772a6c3ef6",
    "how": "POST /appeal with this content_id and your reasoning"
  },
  "combined_score": 0.5509,
  "confidence": 0.1,
  "content_id": "c12306dc-76ab-4325-991e-c9772a6c3ef6",
  "creator_id": "sample-writer",
  "guess": "unsure",
  "label": "The available signals do not support a reliable classification. No conclusion about authorship should be drawn from this result.",
  "model_score": 0.6018,
  "status": "decided",
  "style_score": 0.5
}
```

**An appeal**

```bash
$ curl -X POST http://127.0.0.1:5000/appeal \
  -H "Content-Type: application/json" \
  -d '{"content_id": "c12306dc-76ab-4325-991e-c9772a6c3ef6", "reasoning": "I wrote this summary myself for a team workshop. The tone is formal because it was meant for a handout.", "creator_id": "sample-writer"}'
```

```json
{
  "appealed_at": "2026-11-01T23:31:03+00:00",
  "content_id": "c12306dc-76ab-4325-991e-c9772a6c3ef6",
  "message": "Thanks — your appeal is recorded and a person will review this decision. The original label is paused while they do.",
  "original_guess": "unsure",
  "previous_status": "decided",
  "status": "under_review"
}
```

The same appeal sent a second time (without `creator_id`) is refused — one
appeal per item:

```bash
$ curl -X POST http://127.0.0.1:5000/appeal \
  -H "Content-Type: application/json" \
  -d '{"content_id": "c12306dc-76ab-4325-991e-c9772a6c3ef6", "reasoning": "Sending my appeal again in case it did not go through."}'
```

```json
{
  "error": "already_under_review",
  "field": "content_id",
  "message": "Your appeal for this result is already recorded and waiting for a person to review it. You don't need to send it again."
}
```

(HTTP 409.)

**What the log shows afterwards**

```bash
$ curl "http://127.0.0.1:5000/log?limit=3"
```

```json
{
  "count": 3,
  "entries": [
    {
      "combined_score": 0.5509,
      "confidence": 0.1,
      "content_id": "c12306dc-76ab-4325-991e-c9772a6c3ef6",
      "creator_id": "sample-writer",
      "guess": "unsure",
      "label": "The available signals do not support a reliable classification. No conclusion about authorship should be drawn from this result.",
      "model_score": 0.6018,
      "status": "decided",
      "style_score": 0.5,
      "text_length": 471,
      "timestamp": "2026-11-01T23:30:55+00:00"
    },
    {
      "content_id": "c12306dc-76ab-4325-991e-c9772a6c3ef6",
      "creator_id": "sample-writer",
      "event": "appeal",
      "reasoning": "I wrote this summary myself for a team workshop. The tone is formal because it was meant for a handout.",
      "status": "under_review",
      "timestamp": "2026-11-01T23:31:03+00:00"
    },
    {
      "attempted_content_id": "c12306dc-76ab-4325-991e-c9772a6c3ef6",
      "creator_id": "unknown",
      "endpoint": "/appeal",
      "event": "rejected",
      "field": "content_id",
      "http_status": 409,
      "reason": "already_under_review",
      "status": "rejected",
      "timestamp": "2026-11-01T23:31:03+00:00"
    }
  ]
}
```

The decision is still there, unchanged, with `status: "decided"`; the appeal
sits after it with `status: "under_review"`; the refused duplicate left a
trace too. The submitted text is not in the log — only `text_length`.

---

## How I Used AI

I built this with Claude (Claude Code) working in small, reviewed steps: each
change came back with a diff and test results, and nothing was committed until
I approved it.

**Moment 1 — implementing the scoring**

- *What I asked for:* A combining rule in `scoring.py::combine_signals` using
  the existing config weights as a normalised weighted average, with invalid
  inputs and broken weight settings refused rather than accepted; then
  `score_to_label` and `confidence` built on the same validation.
- *What came back:* `combine_signals` with input and weight checks, 13 unit
  tests, and the wiring into `/submit`. With it, a calibration review on the
  available samples showing that the punctuation measure sat at "fully AI" on
  7 of 8 samples and that the provisional anchors were untested.
- *What I changed:* I set the decisions instead of accepting defaults. The
  starter's `score_to_label` stub put exactly 0.35 and 0.65 into the confident
  labels; I required **both boundaries to be "unsure"**. I wrote the three label
  texts myself. I had punctuation **weighted 0** rather than averaged in, kept
  the 0.5 / 0.5 weights and the thresholds explicitly provisional, and required
  confidence to be documented as **uncalibrated, not a probability**. I also
  had the sentence splitter fixed after the review showed that deleting spaces
  after full stops let any text skip scoring.

**Moment 2 — fixing concurrent duplicate appeals**

- *What I asked for:* A final verification of Milestone 5, including known
  limitations.
- *What came back:* The report flagged a real race: `/appeal` checks "already
  under review?" and then appends the appeal as two separate steps, and Flask's
  server is threaded — so two identical appeals arriving together could both
  see `decided` and both be recorded.
- *What I changed:* I asked for the fix to be narrow: one module-level
  `threading.Lock` around only the status check and the append, with
  validation and the creator check left alone, and a comment saying plainly it
  protects **one process only** (several gunicorn workers would need a file lock
  or a database). I asked for a deterministic test with separate test clients
  and no sleeps. Claude's test forces the race with an instrumented lock; I had
  it checked against an unlocked version, where it failed with `[200, 200]` —
  proof the race was real and the test catches it.

<!-- ✍️ Review these two moments and rewrite them in your own words before
     submitting — they're your account of the work. -->

Overall: every result in this README comes from a real run, and anything
offline, mocked, or written by Claude is labelled as such. The detector is not
calibrated, and the README doesn't claim it is accurate.

<!-- ═══════════════════════ UNIT 8 — THE TEST ═══════════════════════ -->

---

## Rate Limiting

**My limits:** 5 per minute, 100 per day — on `POST /submit` only
(`config.RATE_LIMIT_PER_MINUTE`, `config.RATE_LIMIT_PER_DAY`; `GET /health`
reports `"rate_limits": "5/minute;100/day"`).

**Why those numbers and not others:**
<!-- Think about two people: a real writer submitting their own work a few
     times an hour, and a script sending a thousand variations to map your
     thresholds. Your numbers have to be liveable for the first and hostile to
     the second. -->

- **5 a minute.** A real writer pastes a piece, reads the label, maybe edits
  and resubmits — one submission every 12 seconds is already brisk for that,
  so 5 a minute never gets in their way. A script probing for the thresholds
  gets 5 tries a minute instead of hundreds. Starter's 10 would also have
  worked; 5 halves what a prober gets for no cost to a writer.
- **100 a day.** A heavy day for one writer is a few dozen submissions; 100
  leaves room. Mapping where 0.35 and 0.65 sit takes thousands of
  variations — at 100 a day per creator, weeks.
- Rejected requests count too: a script sending junk to probe the validation
  uses up its allowance just the same (tested: 5 × `400`, then `429`).

**What a caller counts as:** <!-- per address, or per creator_id? They fail
differently — one script can look like a thousand callers, and one household
can look like one. -->
The starter's rule, unchanged (`app.py::rate_limit_key`): the request's
**`creator_id`** when it's a non-empty string, otherwise the **caller's IP
address** (missing, blank or non-string `creator_id`, non-JSON or non-object
bodies). How each fails:
- **Per `creator_id` can be dodged by rotating ids.** One script sending
  `sock_1`, `sock_2`, … looks like many writers and is never limited — a test
  in `test_rate_limit.py` documents exactly that.
- **Per address is shared.** A classroom or household behind one IP shares
  one allowance — but only requests *without* a usable `creator_id` fall back
  to it.
- Counts are kept in memory: a restart forgets them, and several server
  processes wouldn't share them.

**The run of status codes when I pushed past it:**

<!-- python run_attacks.py --flood 15 -->

Run against the local server on 2026-11-08 with
`python run_attacks.py --flood 15` — 15 submissions as `flood_tester`, saved
to `results/flood_2026-11-08_1042.md`:

```
200 200 200 200 200 429 429 429 429 429 429 429 429 429 429
```

10 of 15 rate limited: the first five got through (the flood text is short, so
each was answered `insufficient_evidence` without scoring), and every request
after that in the same minute got `429`. One of the ten logged rejections:

```json
{"timestamp": "2026-11-08T15:42:22+00:00", "creator_id": "flood_tester", "event": "rejected", "status": "rejected", "reason": "rate_limited", "limit": "5 per 1 minute", "http_status": 429, "endpoint": "/submit"}
```

Every `429` is logged as a `rejected` entry with `reason: "rate_limited"`,
`http_status: 429`, `endpoint: "/submit"`, the limit hit, and the
`creator_id` (or `"unknown"`) — an attack that only shows up as an absence is
one you'd never find.

---

## Attack Run — Before

<!-- Every attack with its outcome and a held-or-broke mark.
     `run_attacks.py --label before` produces the table. -->

`python run_attacks.py --set attack_set --label before`, against the local
server on 2026-11-08 (rate limiting on, 5/minute; nothing in the detector
changed). Raw output: `results/attack_run_2026-11-08_1100_before.md` — the
runner leaves the verdicts blank; the verdicts below are mine. Scores come
from the audit log entry for each attack's `content_id`.

**56 attacks: 49 held, 7 broke** — one of the seven, EV05, is ambiguous (see
below). **No crashes, no 5xx.** Nine `429`s — seven
from the flood family as intended, and two (RQ10, RQ11) that are a finding of
their own, below.

How I marked them:
- **evasion** — BROKE if AI text came out **human**, or a text long enough to
  judge escaped scoring. "Unsure" counts as held: it clears no one.
- **false_positive** — BROKE if human writing came out **AI**. "Unsure" is not
  an accusation (criterion 1).
- **prompt_injection** — BROKE if the instruction changed the score, the
  label or the log.
- **malformed / flood** — BROKE on a crash, 5xx, a false classification or a
  missing log entry.

| Family | Attacks | Held | Broke |
|---|---|---|---|
| evasion | 10 | 5 | **5** |
| false_positive | 8 | 6 | **2** |
| prompt_injection | 6 | 6 | 0 |
| malformed | 20 | 20 | 0 |
| flood_same_creator | 12 | 12 | 0 |
| **Total** | **56** | **49** | **7** |

| ID | Family | Targeting | HTTP | Guess | model | style | combined | Verdict | What happened |
|---|---|---|---|---|---|---|---|---|---|
| EV01 | evasion | signal two: typos raise word variety | 200 | human | 0.1635 | 0.5 | 0.3317 | **BROKE** | AI text → **human**. Typos made GPT-2 surprised (model 0.16) |
| EV02 | evasion | signal two: broken-up sentences raise length spread | 200 | human | 0.5943 | 0 | 0.2972 | **BROKE** | AI text → **human**. Inserted 'Really.' sentences zeroed the spread measure |
| EV03 | evasion | signal two: a pasted quotation changes the shape | 200 | unsure | 0.6662 | 0.2566 | 0.4614 | **HELD** | unsure, not human |
| EV04 | evasion | signal one: unusual words raise perplexity | 200 | unsure | 0.6114 | 0.5 | 0.5557 | **HELD** | unsure, not human |
| EV05 | evasion | both signals: heavy human editing pass | 200 | human | 0.3212 | 0.0247 | 0.1729 | **BROKE** | edited AI text → **human** (arguable: a heavy human rewrite may now be human writing) |
| EV06 | evasion | signal two: one very long sentence and one very short | 200 | human | 0.5727 | 0 | 0.2863 | **BROKE** | AI text → **human**. One very long + one very short sentence zeroed spread |
| EV07 | evasion | signal two: padding with punctuation | 200 | insufficient_evidence | — | — | — | **BROKE** | 97-word AI text escaped scoring: semicolons for full stops → 1 sentence → too short |
| EV08 | evasion | signal one: text below the token window | 200 | insufficient_evidence | — | — | — | **HELD** | 10 words: too short to judge, by design |
| EV09 | evasion | both: AI text with a human opening paragraph bolted on | 200 | unsure | 0.7042 | 0.2325 | 0.4684 | **HELD** | unsure, not human |
| EV10 | evasion | signal two: repeated stanza structure | 200 | ai | 0.9792 | 0.8061 | 0.8926 | **HELD** | still AI |
| FP01 | false_positive | plain, clear human writing with no flourishes | 200 | unsure | 0.6175 | 0.2425 | 0.43 | **HELD** | unsure, no accusation |
| FP02 | false_positive | human writing in a formal register | 200 | unsure | 0.7387 | 0.5357 | 0.6372 | **HELD** | unsure — **0.637, 0.013 from AI** |
| FP03 | false_positive | a non-native English speaker writing carefully | 200 | unsure | 0.8051 | 0.3718 | 0.5885 | **HELD** | unsure — model alone 0.81; style kept it below 0.65 |
| FP04 | false_positive | a student essay written to a rubric | 200 | unsure | 0.8329 | 0.3333 | 0.5831 | **HELD** | unsure, no accusation |
| FP05 | false_positive | technical documentation written by a person | 200 | ai | 0.8005 | 0.8589 | 0.8297 | **BROKE** | human technical doc → **AI** (0.83): both signals agree |
| FP06 | false_positive | a person imitating a formal template | 200 | unsure | 0.8814 | 0.2908 | 0.5861 | **HELD** | unsure, no accusation |
| FP07 | false_positive | human writing that repeats a phrase deliberately | 200 | ai | 0.8816 | 0.5 | 0.6908 | **BROKE** | human text with deliberate repetition → **AI** (0.69) |
| FP08 | false_positive | very short genuine human submission | 200 | insufficient_evidence | — | — | — | **HELD** | too short, no judgment |
| PI01 | prompt_injection | instruction to ignore the check | 200 | insufficient_evidence | — | — | — | **HELD** | 45 words: not scored; instruction had no effect |
| PI02 | prompt_injection | instruction disguised as a system message | 200 | insufficient_evidence | — | — | — | **HELD** | 45 words: not scored; instruction had no effect |
| PI03 | prompt_injection | instruction wrapped in the writer's voice | 200 | unsure | 0.5943 | 0.3569 | 0.4756 | **HELD** | scored normally; not human |
| PI04 | prompt_injection | attempt to make the label text hostile | 200 | unsure | 0.4998 | 0.3033 | 0.4016 | **HELD** | label is fixed text; markup never echoed |
| PI05 | prompt_injection | attempt to inject into the audit log | 200 | insufficient_evidence | — | — | — | **HELD** | text isn't logged, so nothing to inject |
| PI06 | prompt_injection | instruction plus real human text | 200 | unsure | 0.5583 | 0.2546 | 0.4064 | **HELD** | scored normally; not human |
| MF01 | malformed | text is only whitespace | 400 | — | — | — | — | **HELD** | refused, logged |
| MF02 | malformed | text is a single character | 200 | insufficient_evidence | — | — | — | **HELD** | no crash, no judgment |
| MF03 | malformed | text is control characters | 200 | insufficient_evidence | — | — | — | **HELD** | no crash, no judgment |
| MF04 | malformed | text is only punctuation | 200 | insufficient_evidence | — | — | — | **HELD** | no crash, no judgment |
| MF05 | malformed | text is a very long single word | 200 | insufficient_evidence | — | — | — | **HELD** | no crash, no judgment |
| MF06 | malformed | text is emoji only | 200 | insufficient_evidence | — | — | — | **HELD** | no crash, no judgment |
| MF07 | malformed | text is right-to-left script | 200 | insufficient_evidence | — | — | — | **HELD** | no crash, no judgment |
| MF08 | malformed | text is 60,000 characters | 413 | — | — | — | — | **HELD** | refused as too long, logged |
| RQ01 | malformed | no text field at all | 400 | — | — | — | — | **HELD** | refused, logged |
| RQ02 | malformed | no creator_id | 400 | — | — | — | — | **HELD** | refused, logged |
| RQ03 | malformed | text is a number | 400 | — | — | — | — | **HELD** | refused, logged |
| RQ04 | malformed | text is a list | 400 | — | — | — | — | **HELD** | refused, logged |
| RQ05 | malformed | text is null | 400 | — | — | — | — | **HELD** | refused, logged |
| RQ06 | malformed | creator_id is an object | 400 | — | — | — | — | **HELD** | refused, logged |
| RQ07 | malformed | body is a JSON array, not an object | 400 | — | — | — | — | **HELD** | refused, logged |
| RQ08 | malformed | body is unparseable JSON | 400 | — | — | — | — | **HELD** | refused, logged |
| RQ09 | malformed | body is empty | 400 | — | — | — | — | **HELD** | refused, logged |
| RQ10 | malformed | body is form-encoded, not JSON | 429 | — | — | — | — | **HELD** | **429 not 400**: shared IP allowance already used by RQ02/06/07/08/09 |
| RQ11 | malformed | body is JSON claiming to be plain text | 429 | — | — | — | — | **HELD** | **429 not 400**: same shared IP allowance |
| RQ12 | malformed | deeply nested JSON | 400 | — | — | — | — | **HELD** | refused, logged |
| FL01_01 | flood_same_creator | 20 rapid submissions from one creator | 200 | insufficient_evidence | — | — | — | **HELD** | allowed, then limited |
| FL01_02 | flood_same_creator | 20 rapid submissions from one creator | 200 | insufficient_evidence | — | — | — | **HELD** | allowed, then limited |
| FL01_03 | flood_same_creator | 20 rapid submissions from one creator | 200 | insufficient_evidence | — | — | — | **HELD** | allowed, then limited |
| FL01_04 | flood_same_creator | 20 rapid submissions from one creator | 200 | insufficient_evidence | — | — | — | **HELD** | allowed, then limited |
| FL01_05 | flood_same_creator | 20 rapid submissions from one creator | 200 | insufficient_evidence | — | — | — | **HELD** | allowed, then limited |
| FL01_06 | flood_same_creator | 20 rapid submissions from one creator | 429 | — | — | — | — | **HELD** | rate limited, logged |
| FL01_07 | flood_same_creator | 20 rapid submissions from one creator | 429 | — | — | — | — | **HELD** | rate limited, logged |
| FL01_08 | flood_same_creator | 20 rapid submissions from one creator | 429 | — | — | — | — | **HELD** | rate limited, logged |
| FL01_09 | flood_same_creator | 20 rapid submissions from one creator | 429 | — | — | — | — | **HELD** | rate limited, logged |
| FL01_10 | flood_same_creator | 20 rapid submissions from one creator | 429 | — | — | — | — | **HELD** | rate limited, logged |
| FL01_11 | flood_same_creator | 20 rapid submissions from one creator | 429 | — | — | — | — | **HELD** | rate limited, logged |
| FL01_12 | flood_same_creator | 20 rapid submissions from one creator | 429 | — | — | — | — | **HELD** | rate limited, logged |

**What broke, in one line each:**
- **Evasion through signal two (EV02, EV06):** changing only sentence lengths
  — padding with "Really." or one huge sentence plus one tiny one — set
  `style_score` to 0.0, and averaged with a middling `model_score` that was
  enough for **human**.
- **Evasion through signal one (EV01):** the typos aimed at signal two
  actually hit signal one — misspellings made GPT-2 surprised (`model_score`
  0.16).
- **Ambiguous (EV05):** AI text after a *heavy human editing pass* came out
  **human** (0.17). Marked BROKE under the evasion rule, but a rewrite that
  heavy may genuinely be human writing now — it's the one verdict here I'd
  defend either way, and I don't count it as a clear detector failure.
- **Escaping the check (EV07):** joining every sentence with semicolons made a
  97-word AI paragraph count as *one* sentence, so the short-text rule (fewer
  than 3 sentences) answered "too short to assess" — no judgment at all.
- **False accusations (FP05, FP07):** human writing labelled AI — see below.
- **Two held only narrowly:** FP02 (formal report) at 0.637, 0.013 below the AI
  threshold; FP03 (careful non-native English) had `model_score` 0.81 on its
  own and was kept at "unsure" only by the style signal.
- **RQ10, RQ11 got `429` instead of `400`.** Requests without a usable
  `creator_id` share one allowance per IP address; five earlier malformed
  requests (RQ02, RQ06–RQ09) used it up, so these two were rate limited
  before they were ever validated. No crash and both logged, so held — but
  the rate limiter masked the validation it was meant to sit in front of.

**Ten audit log entries from the run**

<!-- Choose entries that show the interesting failures, not the ten easiest. -->

Lines 58, 60, 50, 45, 44, 56, 55, 66, 85, 93 and 75 of `logs/audit.jsonl`,
copied as-is (eleven, to include both kinds of rejection):

```json
{"timestamp": "2026-11-08T16:00:29+00:00", "content_id": "d550a266-f088-4d04-a9ae-1b4107d0e791", "creator_id": "attacker_FP05", "guess": "ai", "model_score": 0.8005, "style_score": 0.8589, "combined_score": 0.8297, "label": "This text shows patterns associated with AI-generated writing. This result is not proof of AI use, and you can request a human review if you disagree.", "status": "decided", "confidence": 0.66, "text_length": 393}
{"timestamp": "2026-11-08T16:00:30+00:00", "content_id": "0abd96e8-1d08-4d64-9814-f2dedd86aba2", "creator_id": "attacker_FP07", "guess": "ai", "model_score": 0.8816, "style_score": 0.5, "combined_score": 0.6908, "label": "This text shows patterns associated with AI-generated writing. This result is not proof of AI use, and you can request a human review if you disagree.", "status": "decided", "confidence": 0.38, "text_length": 335}
{"timestamp": "2026-11-08T16:00:27+00:00", "content_id": "14496023-e02a-4ab4-bfd3-d2927df12c6f", "creator_id": "attacker_EV07", "guess": "insufficient_evidence", "model_score": null, "style_score": null, "combined_score": null, "label": "This piece is too short for us to assess, so we haven't made any judgment about it.", "status": "decided", "confidence": null, "text_length": 749, "reason": "too_short_to_assess"}
{"timestamp": "2026-11-08T16:00:26+00:00", "content_id": "65aada2d-ea5f-4802-9e82-32ce771a6a46", "creator_id": "attacker_EV02", "guess": "human", "model_score": 0.5943, "style_score": 0.0, "combined_score": 0.2972, "label": "This text shows patterns more consistent with human writing. This is an automated estimate, not proof of authorship.", "status": "decided", "confidence": 0.41, "text_length": 708}
{"timestamp": "2026-11-08T16:00:26+00:00", "content_id": "2f34c821-ea09-46c9-8876-7f282af14518", "creator_id": "attacker_EV01", "guess": "human", "model_score": 0.1635, "style_score": 0.5, "combined_score": 0.3317, "label": "This text shows patterns more consistent with human writing. This is an automated estimate, not proof of authorship.", "status": "decided", "confidence": 0.34, "text_length": 657}
{"timestamp": "2026-11-08T16:00:29+00:00", "content_id": "bff8d7de-7b8e-4ae1-938d-c5868fdcbeaa", "creator_id": "attacker_FP03", "guess": "unsure", "model_score": 0.8051, "style_score": 0.3718, "combined_score": 0.5885, "label": "The available signals do not support a reliable classification. No conclusion about authorship should be drawn from this result.", "status": "decided", "confidence": 0.18, "text_length": 418}
{"timestamp": "2026-11-08T16:00:29+00:00", "content_id": "4a0cb708-c9cd-4bc7-bef6-a25c799e3613", "creator_id": "attacker_FP02", "guess": "unsure", "model_score": 0.7387, "style_score": 0.5357, "combined_score": 0.6372, "label": "The available signals do not support a reliable classification. No conclusion about authorship should be drawn from this result.", "status": "decided", "confidence": 0.27, "text_length": 477}
{"timestamp": "2026-11-08T16:00:31+00:00", "content_id": "1ef4b6de-0cd6-44db-96db-6d7ae824bb5d", "creator_id": "attacker_PI05", "guess": "insufficient_evidence", "model_score": null, "style_score": null, "combined_score": null, "label": "This piece is too short for us to assess, so we haven't made any judgment about it.", "status": "decided", "confidence": null, "text_length": 213, "reason": "too_short_to_assess"}
{"timestamp": "2026-11-08T16:00:31+00:00", "creator_id": "unknown", "event": "rejected", "status": "rejected", "reason": "rate_limited", "limit": "5 per 1 minute", "http_status": 429, "endpoint": "/submit"}
{"timestamp": "2026-11-08T16:00:31+00:00", "creator_id": "attacker_flood", "event": "rejected", "status": "rejected", "reason": "rate_limited", "limit": "5 per 1 minute", "http_status": 429, "endpoint": "/submit"}
{"timestamp": "2026-11-08T16:00:31+00:00", "creator_id": "attacker_MF08", "event": "rejected", "status": "rejected", "reason": "too_long", "field": "text", "http_status": 413}
```

In order: FP05 and FP07 (the false accusations), EV07 (escaped scoring), EV02
and EV01 (AI → human), FP03 and FP02 (held narrowly), PI05 (log injection —
nothing to inject, the text isn't logged), RQ10's `429` with
`creator_id: "unknown"`, a flood `429`, and MF08's `413`.

**The single worst outcome** — the one I'd least want to explain to a writer
whose work got caught by it:

**FP05 — technical documentation written by a person, labelled AI at 0.83**
(model 0.80, style 0.86, confidence 0.66). It's the highest AI score any human
text got, and it's not borderline: both signals agreed, so the combining rule
had nothing to balance. The writer did nothing unusual — documentation is
*meant* to be plain, consistent and repetitive.

*Preliminary hypothesis, not yet a diagnosis:* the failure is shared by both
signals and passed straight through the combining rule. **Signal one** — the
formulaic-genre blind spot: instructions like "Set the port value… Save the
file and restart the service" are highly predictable to GPT-2. **Signal two**
— even, imperative sentences push `spread` to 0.85 and repeated terms ("the
service", "the file") push `vocabulary` to 0.87, both towards AI. **The
combining rule** averages two agreeing errors, so neither can correct the
other. FP07 (deliberate repetition) looks like the same mechanism through the
vocabulary measure. To be tested in the Run Log and Verdicts stage.

---

## Run Log and Verdicts

<!-- Your five criteria across three trials. `run_eval.py --label before`. -->

Run against the local server on 2026-11-08 (rate limiting on; detector
unchanged). Criteria 1–3 and 5: `python run_eval.py --label before` →
`results/run_2026-11-08_1120_before.md`. Criterion 4: `python eval_appeals.py
--label before` → `results/appeals_2026-11-08_1120_before.md` (`run_eval.py`
only sends `/submit`, so the appeal path needed its own script).

**What was tested — and where it came from** (full sources in `scenarios.py`):
- **Human writing:** 10 passages from public-domain books on Project Gutenberg
  (Austen, Twain, Conan Doyle, Stoker, Thoreau, Douglass, Washington, Dickens,
  Shelley, Brontë), each picked by a fixed rule *before* anything was scored —
  the first paragraph at or after 40% of the way in, 100–250 words, at least 3
  sentences. URL, paragraph number and file hash are recorded for each.
- **AI writing:** 10 paragraphs written by Claude for this test.
- **Not my own writing.** I don't have ten samples of my own, so criterion 1
  as written can't be measured; it has a documented revision in `criteria.md`,
  with the original left in place.

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. False positives — *as written* | ≤ 1 of 10 of **my own** texts labelled AI | not run | not run | not run | **NOT EVALUABLE** — no samples of my own writing exist |
| 1. False positives — *revised* | ≤ 1 of 10 Gutenberg human passages labelled AI | 0 of 10 (7 unsure, 3 human) | 0 of 10 | 0 of 10 | **MET** (revised criterion only) |
| 2. Score separation | AI mean `combined_score` ≥ human mean + 0.20, all scored | AI 0.6243 − human 0.3872 = **+0.2371** | +0.2371 | +0.2371 | **MET** — by 0.037 |
| 3. Label coverage | all three labels at least once in 9 submissions | human 1, unsure 5, AI 3 | same | same | **MET** |
| 4. Appeal process | 5/5 valid appeals → 200, `under_review`, entry appended, decision kept; unknown → 404; duplicate → 409 | 5/5 · 404 · 409 | 5/5 · 404 · 409 | 5/5 · 404 · 409 | **MET** |
| 5. Invalid input | empty, missing, null, numeric → 400; > 20,000 chars → 413 with a rejection entry and no score, label or `content_id` | 400 400 400 400 413 | same | same | **MET** |

**Verdicts, honestly qualified.** A verdict is MET only if all three trials
hit the target as written.
- **Criterion 1 is NOT EVALUABLE as written** — it names *my own* writing and
  there is none. The revised version (same target, human writing with
  checkable provenance) is MET, but it says nothing about modern or plain
  writing: every passage is 19th-century literary prose.
- **Criterion 2 is MET, but narrowly** (+0.237 against +0.20), and the gap
  hides a weak AI side: only 3 of the 10 AI texts were labelled AI; the other 7
  came back unsure. See diagnosis D1.
- **Criterion 3 is MET, but the one "human" result came from AI text** — the
  Claude-written pantry paragraph. Both genuinely human candidates (Thoreau,
  Shelley) came back unsure. "Human" is reachable; the run doesn't show it's
  reachable *for human writing*.
- **Criteria 4 and 5 are MET** with nothing to qualify.

No criterion was missed. Criteria 2 and 3 pass in ways that point at the same
weakness the attack run found — diagnosed below.

All three trials came out identical, to four decimal places. Signal one is
GPT-2 in evaluation mode and signal two is plain arithmetic, so the same text
gets the same score — the trials test repeatability, not luck.

Criterion 2's `combined_score` isn't in `run_eval.py`'s report, so it was
recomputed with `scoring.combine_signals` from the recorded `model_score` and
`style_score` — and checked against the audit log, where all 60 entries carry
exactly those values. Criterion 5's rejections were checked in the log: 15
entries (3 per body), each `invalid_input`/400 or `too_long`/413, none with a
`content_id`.

**Real output from one trial**, pasted as text, naming the file and function
that produced it:

Criterion 5, trial 1 — `results/run_2026-11-08_1120_before.md`, produced by
`run_eval.py::main` (service: `app.py::submit`):

```json
[
  {
    "status": 400,
    "guess": null,
    "confidence": null,
    "model_score": null,
    "style_score": null,
    "label": null,
    "sent": "(empty text)"
  },
  {
    "status": 400,
    "guess": null,
    "confidence": null,
    "model_score": null,
    "style_score": null,
    "label": null,
    "sent": "{\"creator_id\": \"eval_c5_missing\"}"
  },
  {
    "status": 400,
    "guess": null,
    "confidence": null,
    "model_score": null,
    "style_score": null,
    "label": null,
    "sent": "{\"text\": null, \"creator_id\": \"eval_c5_null\"}"
  },
  {
    "status": 400,
    "guess": null,
    "confidence": null,
    "model_score": null,
    "style_score": null,
    "label": null,
    "sent": "{\"text\": 12345, \"creator_id\": \"eval_c5_numeric\"}"
  },
  {
    "status": 413,
    "guess": null,
    "confidence": null,
    "model_score": null,
    "style_score": null,
    "label": null,
    "sent": "word word word word word word word word word word word word word word "
  }
]
```

Criterion 4, trial 1 (first of five appeals, plus the 404 and 409) —
`results/appeals_2026-11-08_1120_before.md`, produced by
`eval_appeals.py::main` (service: `app.py::submit`, `app.py::appeal`):

```json
{
  "appeals[0]": {
    "submit_status": 200,
    "content_id": "dad7b905-fab0-46fa-8303-93bf966e356e",
    "guess": "unsure",
    "appeal_status": 200,
    "appeal_response": {
      "appealed_at": "2026-11-08T16:20:17+00:00",
      "content_id": "dad7b905-fab0-46fa-8303-93bf966e356e",
      "message": "Thanks — your appeal is recorded and a person will review this decision. The original label is paused while they do.",
      "original_guess": "unsure",
      "previous_status": "decided",
      "status": "under_review"
    },
    "appeal_entries_after": 1,
    "decision_unchanged": true,
    "log_entries_added": 1,
    "passed": true
  },
  "unknown": {
    "status": 404,
    "response": {
      "error": "unknown_content_id",
      "field": "content_id",
      "message": "We couldn't find a result with that content_id. Please check it matches the one in your result exactly."
    }
  },
  "duplicate": {
    "status": 409,
    "response": {
      "error": "already_under_review",
      "field": "content_id",
      "message": "Your appeal for this result is already recorded and waiting for a person to review it. You don't need to send it again."
    },
    "appeal_entries_after": 1
  },
  "valid_appeals_passed": 5,
  "trial_passed": true
}
```

**Diagnoses**

<!-- For each miss AND each broken attack: the stage and the mechanism.

     Your service has five stages: the route, signal one, signal two, the
     combining rule, and the label mapping.

     Not a diagnosis:  "The evasion attacks got through."
     A diagnosis:      "Four evasion inputs got through. All four had typos
                        added to AI-generated text. My second signal measures
                        word variety, and typos raise word variety — so it read
                        them as more human. My combining rule weights that
                        signal at 0.6, so it dragged the whole score down."

     Look for a pattern. Five failures on one signal is one problem, not five. -->

Each diagnosis separates **Observed** (numbers from the audit log or the run
reports), **Mechanism** (traced through the code and checked by recomputing
the scores exactly) and **Hypothesis** (plausible, not yet tested). Raw style
values were recomputed offline with the unchanged `stylometry.py`; they match
the logged `style_score` for every case below.

Seven broken attacks and two weak passes come down to **four problems**, not
nine.

**D1 — Signal two's vocabulary measure works backwards on these samples.**
*Stage: signal two (`stylometry.type_token_ratio`), passed on by the
combining rule.* Explains criterion 2's weak AI side, FP05, FP07, and why
EV02/EV06 worked (D2).
- *Observed:* vocabulary scored **0.00 on all 10 AI texts** in the criteria
  run — their type-token ratios were 0.88–0.95, above the 0.80 "human" anchor.
  The human Gutenberg passages scored *lower* variety (0.74–0.87). Vocabulary
  pushed hard toward AI only on deliberately degenerate AI text (EV10's
  repeated stanza, the "The system is good." test paragraphs) — and on two
  pieces of **human** writing: FP05 (0.87, repeated technical terms) and FP07
  (1.00, deliberate repetition). On natural AI prose it never fired.
- *Mechanism:* with vocabulary stuck at 0, an AI paragraph's style score is
  at most 0.5 × spread ≤ 0.5. A combined score above 0.65 then needs
  `model_score` above 0.80 — which only 3 of the 10 AI texts reached. So 7
  came back unsure, and the criterion 2 gap rests almost entirely on signal
  one and on sentence spread.
- *Hypothesis:* the starter's assumption ("AI repeats vocabulary") fits older
  or degenerate generation; modern assistant prose uses broad, formal
  vocabulary, while some human genres (documentation, rhetorical repetition)
  repeat on purpose.

**D2 — Sentence spread is the only working style measure, and it costs
nothing to fake.** *Stage: signal two (`stylometry.sentence_length_spread`),
then the combining rule.* Broke EV02 and EV06.
- *Observed:* EV02 added one-word sentences ("Really.") — lengths
  11, 1, 15, 1, 10, 1… — and EV06 put a 51-word sentence next to a 1-word one.
  Spread variation rose to 0.85 and 1.19, past the 0.70 "human" anchor, so
  spread scored **0.0**; with vocabulary already 0 (D1), `style_score` = **0.0**.
- *Mechanism:* combined = 0.5 × model + 0.5 × 0 = half the model score. EV02's
  model 0.594 became 0.297 and EV06's 0.573 became 0.286 — both **human**. A
  style score of 0 halves whatever signal one says, so any AI text with
  `model_score` below 0.70 can be pushed into "human" by adding short
  sentences, without changing a word of content.

**D3 — The short-text gate counts sentences by full stops.** *Stage: the
route (`app.py::submit`, the `MIN_SENTENCES_TO_ASSESS` check), using
`stylometry.sentences`.* Broke EV07.
- *Observed:* EV07 is 97 words — over the 50-word minimum — but contains one
  full stop and six semicolons, so `sentences()` finds **1** sentence, and the
  route answered `insufficient_evidence` without scoring.
- *Mechanism:* the gate is "fewer than 50 words **or** fewer than 3
  sentences". The sentence half was meant to stop short texts being judged,
  but it also lets a long text skip judgment entirely by joining sentences
  with semicolons. This is a gap I introduced in Milestone 3, not a signal
  failure.

**D4 — Signal one rates plain, formulaic or repetitive human writing as
predictable.** *Stage: signal one (`detector.model_signal`); D1 then adds to
it.* Broke FP05 and FP07; FP02 and FP03 held only narrowly.
- *Observed:* human texts scored high on signal one: FP05 documentation
  **0.80**, FP07 repetition **0.88**, FP02 formal report 0.74, FP03 careful
  non-native English **0.81**. FP05 was then pushed to 0.83 by a style score of
  0.86 (spread 0.85, vocabulary 0.87); FP07 to 0.69 with style 0.5.
- *Mechanism:* when both signals lean AI, the average can't correct either —
  FP05 had nothing pulling it back. FP03 stayed unsure only because its
  spread scored 0.74, not higher.
- *Hypothesis:* predictable instructions ("set the port…, save the file…")
  and phrases repeated within a text are exactly what GPT-2 predicts well —
  the documented blind spot. Not yet tested by, for example, scoring the same
  text with its repetition removed.

**Single attacks:**
- **EV01 (typos → human):** *Observed:* `model_score` **0.16** with style 0.5
  (spread 1.0, vocabulary 0.0), combined 0.33. *Hypothesis:* the misspellings
  are low-probability tokens that raised GPT-2's perplexity — the attack aimed
  at signal two but hit signal one. Not confirmed: the unaltered text wasn't
  scored on its own.
- **EV05 (heavy human edit → human):** *Observed:* model 0.32, style 0.02,
  combined 0.17. Both signals agree it reads as human; whether that's a failure
  depends on whether a heavy rewrite *is* human writing. Ambiguous, not
  diagnosed as a defect.
- **RQ10, RQ11 (429 instead of 400):** not broken, but a design finding.
  *Mechanism:* the rate-limit key falls back to the IP address when there's
  no usable `creator_id`, and the limiter runs before validation, so five
  earlier malformed requests used up the shared allowance. *Stage:* rate
  limiting (`app.py::rate_limit_key`).

---

## The Improvement

**What I changed:**

**Which diagnosis pointed at it:**

### Attack Run — After

<!-- Same format. `run_attacks.py --label after` -->



**Did it help, and how do I know:**

<!-- Widening the unsure band usually fixes one problem and creates another.
     Reporting that trade honestly is worth full credit. -->



---

## What's Still Broken

<!-- For each attack still getting through and each criterion still missed:
     what you'd do, and why you stopped. -->



**The trade I'd make if this ran for real:**

<!-- Two sentences. Fewer wrong accusations means more AI text getting through.
     Say which way you'd go and WHO PAYS FOR IT. -->



<!-- ═════════════════════════════════════════════════════════════════════

     SUBMISSION CHECKLIST — unit 7

       [ ] criteria.md has five numbered criteria, each naming a target
       [ ] Each has a reason underneath
       [ ] POST /submit returns content_id, guess, confidence, label,
           model_score and style_score
       [ ] Two signals that measure DIFFERENT things, each with a named blind spot
       [ ] Three label variants, all reachable, written out in full
       [ ] POST /appeal changes status and writes to the log
       [ ] Signals and Scoring names scoring.py::combine_signals
       [ ] Sample Run: a submission AND an appeal, as pasted text
       [ ] At least four new commits
       [ ] Repository URL submitted — WRITE IT DOWN

     SUBMISSION CHECKLIST — unit 8

       [ ] Rate limiting on /submit, with your numbers justified
       [ ] The pasted run of status codes showing 429
       [ ] Audit log with all nine fields, recording rejections too
       [ ] The attack set run IN FULL, every input with an outcome
       [ ] Ten audit log entries pasted as text
       [ ] Five criteria across three trials
       [ ] A diagnosis for every miss and every broken attack — stage AND mechanism
       [ ] One improvement, with Attack Run — After
       [ ] What's Still Broken, including the production trade
       [ ] At least four new commits
       [ ] The SAME repository URL as last unit

     Do not delete and recreate this repository.
     ═════════════════════════════════════════════════════════════════════ -->

---

📖 **How to run this project: [RUNNING.md](RUNNING.md)**
