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



**Ten audit log entries from the run**

<!-- Choose entries that show the interesting failures, not the ten easiest. -->

```json

```

**The single worst outcome** — the one I'd least want to explain to a writer
whose work got caught by it:



---

## Run Log and Verdicts

<!-- Your five criteria across three trials. `run_eval.py --label before`. -->

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1.  |  |  |  |  |  |
| 2.  |  |  |  |  |  |
| 3.  |  |  |  |  |  |
| 4.  |  |  |  |  |  |
| 5.  |  |  |  |  |  |

**Real output from one trial**, pasted as text, naming the file and function
that produced it:

```json

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
