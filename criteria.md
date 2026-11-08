# Acceptance criteria — Provenance Guard

Five criteria that say what "working" means for this service, written in unit 7
**before** you built it.

**All five are yours.** None are given.

An acceptance criterion names a number or something plainly observable. *"The
detector is accurate"* is an opinion — and perfect AI detection isn't possible
anyway, so it's an opinion about something nobody can deliver. *"Of 10 pieces I
wrote myself, at most 1 is labelled high-confidence AI"* is a criterion.

Under each, write a sentence or two on **why that target**. *"I allow at most 1
false positive in 10 because on a writing site a wrong accusation costs more
than a missed detection"* is a real answer.

> Missing your own targets next unit costs you nothing. Setting a target so
> easy you can't miss it does.

---

## Pick numbers you can defend

**Cover at least three of these five areas.** They're prompts, not a form.

| Area | A question it could answer |
|---|---|
| False positives | How often may a human's writing get called AI? |
| Score spread | How far apart should clearly-AI and clearly-human text score? |
| Label coverage | Is every one of your three labels actually reachable? |
| The appeal path | Does an appeal always change status and always get recorded? |
| Bad input | What happens when `text` is missing, empty, or enormous? |

Two things worth knowing before you pick numbers:

- **The expensive mistake is one-sided.** Missing some AI text costs the site a
  little. Accusing a real writer costs that person a lot. A criterion that
  treats both errors as equally bad is describing a system nobody would ship.
- **Unit 8 tests across three trials, and the target has to hold across all
  three.** Your first signal runs a model, so identical input can score
  differently twice. A target of "at most 1 in 10" against trials of 2, 1, 2 is
  a **miss**.

---
## 1. False positives

Test 10 samples of my own human-written text. In each of three trials, no more
than 1 sample may receive a high-confidence AI label. An unsure label does not
count as a false accusation.

**Why this target:**

Wrongly accusing a genuine writer can cause serious harm. Allowing at most 1 in
10 gives the detector a challenging false-positive limit without requiring
perfection.

> **Revised in unit 8:** Test 10 human-written passages with verifiable
> provenance — public-domain books from Project Gutenberg, each selected by a
> fixed rule (the first paragraph at or after 40% of the way through the book
> with 100–250 words and at least 3 sentences; sources in `scenarios.py`). In
> each of three trials, no more than 1 may receive a high-confidence AI label.
> An unsure label does not count as a false accusation.
>
> **Why revised:** the original couldn't be *measured*. I don't have ten
> samples of my own writing, and no other text is "my own" — so as written it
> is **not evaluable**, not passed or failed. The target is unchanged (at most 1
> in 10); only the source of the human writing changed, to one whose human
> authorship can be checked. The cost: these are 19th-century literary prose,
> not modern writing — and not the plain, second-language writing this
> criterion most needs to protect. The original line stands above, untouched.

---

## 2. Score separation

Test 10 AI-generated samples and 10 genuinely human-written samples. In each of
three trials, the average `combined_score` for the AI-generated group must be
at least 0.20 higher than the average `combined_score` for the human-written
group. All samples must be long enough to receive a numeric score.

**Why this target:**

A 0.20 gap on a 0–1 scale would show meaningful separation while allowing
individual samples to overlap.

---

## 3. Label coverage

Prepare 3 candidate samples for each classification label: human, unsure, and
AI. In each of three trials, all three labels must appear at least once across
the 9 submissions. Samples must be long enough for classification;
`insufficient_evidence` does not count as one of the three labels.

**Why this target:**

The system should distinguish stronger evidence from uncertainty rather than
classify everything as human or AI. The unsure label is important for
borderline writing.

---

## 4. Appeal process

In each of three trials, test 5 valid appeals using fresh submissions and
unique `content_id` values. All 5 valid appeals must return HTTP 200, change
status to `under_review`, append an audit-log entry, and preserve the original
decision.

Additionally, in every trial, verify that an unknown `content_id` returns HTTP
404 with `unknown_content_id`, and a duplicate appeal returns HTTP 409 with
`already_under_review`.

**Why this target:**

Writers need a dependable way to challenge decisions. Preserving the original
record and logging the appeal supports accountability.

---

## 5. Invalid input

In each of three trials, test five invalid submissions: empty text, missing
`text` field, null text, numeric text, and text exceeding 20,000 characters.

All five must receive the documented response behavior and status codes in
DESIGN.md without producing a false classification or crashing the server.
Specifically, oversized text must return HTTP 413 with `too_long`, create the
documented rejection-log entry, and produce no score, label, or `content_id`.

**Why this target:**

Invalid requests should not create misleading accusations or destabilize the
service. A 100% target is appropriate for predictable input validation.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     UNIT 8 — read this before you change anything above.

     If a criterion turns out to be BROKEN rather than merely unmet, you can
     revise it, and that earns credit. But never delete or edit the original
     line. Add the revision underneath, like this:

         ## 2. Uncertain cases land in the unsure band

         The system handles uncertain cases well.

         **Why this target:** ...

         > **Revised in unit 8:** Text I judged borderline scores between
         > 0.4 and 0.6 in at least 4 of 5 cases.
         >
         > **Why revised:** "well" gave me nothing to check. I couldn't
         > reach a verdict from it at all.

     That's a revision because the criterion couldn't be MEASURED.

     Lowering a target because you missed it is not a revision, and it costs
     you the point:

         ✗ "At most 1 of 10 of my own pieces flagged as AI" → "at most 3
            of 10", because 1 of 10 turned out to be hard.

     A number you missed stays where it is, gets diagnosed, and gets a fix
     attempted. That's where the points are.
     ───────────────────────────────────────────────────────────────────────── -->
