# Attack run — after

- Produced by: `run_attacks.py::main`
- Service: `app.py::submit`
- 56 attacks · 2026-11-08 11:30
- Auto-marked BROKE (5xx, crash, no response): **0**
- Left for you to judge: **56**

The Verdict column is blank where a script can't honestly decide. Whether
an evasion worked depends on where you put your thresholds — read the
`targets` column, look at what came back, and write HELD or BROKE yourself.

Each attack submits as creator_id `attacker_<id>`, and the content_id it
came back with is in the table — either one will match this run against your
audit log when you go looking for the ten entries to paste.

| ID | Family | Targeting | Status | Content ID | Guess | Score | Verdict |
|---|---|---|---|---|---|---|---|
| EV01 | evasion | signal two: typos raise word variety | 200 | `fb3bc97d-f57a-4c79-b949-8b2452c00c03` | human | 0.340 |  |
| EV02 | evasion | signal two: broken-up sentences raise length spread | 200 | `1396c599-34d3-4f18-8d9b-d2d73051fc13` | human | 0.410 |  |
| EV03 | evasion | signal two: a pasted quotation changes the shape | 200 | `33c521c5-7dc6-4e05-8f61-98aa315a9ab6` | unsure | 0.080 |  |
| EV04 | evasion | signal one: unusual words raise perplexity | 200 | `c552b9ca-fde0-46bf-8ca1-26c1e2f79307` | unsure | 0.110 |  |
| EV05 | evasion | both signals: heavy human editing pass | 200 | `a6838289-257b-4d0e-b482-8627761c29e3` | human | 0.650 |  |
| EV06 | evasion | signal two: one very long sentence and one very short | 200 | `717a5a57-3fa5-4d43-acdc-aa023da8a257` | human | 0.430 |  |
| EV07 | evasion | signal two: padding with punctuation | 200 | `513b59a5-ed71-4a17-bd22-b5cfa0cad1f8` | unsure | 0.160 |  |
| EV08 | evasion | signal one: text below the token window | 200 | `b0c6d169-c95d-49e7-84b6-250fca1f3946` | insufficient_evidence | — |  |
| EV09 | evasion | both: AI text with a human opening paragraph bolted on | 200 | `5f276310-3f05-42b7-b163-e8f021019bbd` | unsure | 0.060 |  |
| EV10 | evasion | signal two: repeated stanza structure | 200 | `c44bfaaf-e652-46eb-90e4-a55681f123e7` | ai | 0.790 |  |
| FP01 | false_positive | plain, clear human writing with no flourishes | 200 | `77053631-3e2b-417c-98a4-431289326a0c` | unsure | 0.140 |  |
| FP02 | false_positive | human writing in a formal register | 200 | `0e36dff8-2ee0-4185-9994-d364cd7a7078` | unsure | 0.270 |  |
| FP03 | false_positive | a non-native English speaker writing carefully | 200 | `c4500152-d3e8-498e-9d14-507e274f78a6` | unsure | 0.180 |  |
| FP04 | false_positive | a student essay written to a rubric | 200 | `6bdd0e04-c458-44ff-98d2-a01a4b5b4d48` | unsure | 0.170 |  |
| FP05 | false_positive | technical documentation written by a person | 200 | `23e3233f-7290-42b8-9bcb-6597d6cac847` | ai | 0.660 |  |
| FP06 | false_positive | a person imitating a formal template | 200 | `e41e5347-447c-4c1b-a8d9-675a0fdaedaf` | unsure | 0.170 |  |
| FP07 | false_positive | human writing that repeats a phrase deliberately | 200 | `1eda0c21-f191-4b02-a8f8-1864f0c989d4` | ai | 0.380 |  |
| FP08 | false_positive | very short genuine human submission | 200 | `00e1e2f7-7a71-4108-a1ec-0bd2ff4c78b9` | insufficient_evidence | — |  |
| PI01 | prompt_injection | instruction to ignore the check | 200 | `359c91c7-ccd1-4f89-a780-2aa05ae5ef52` | insufficient_evidence | — |  |
| PI02 | prompt_injection | instruction disguised as a system message | 200 | `8426ae1f-da20-4ee1-9ca4-f6edba79d2a0` | insufficient_evidence | — |  |
| PI03 | prompt_injection | instruction wrapped in the writer's voice | 200 | `ebe37296-a79b-4b17-9afd-62e4ecc61a8b` | unsure | 0.050 |  |
| PI04 | prompt_injection | attempt to make the label text hostile | 200 | `d571d351-8246-4030-8786-4170856244ec` | unsure | 0.200 |  |
| PI05 | prompt_injection | attempt to inject into the audit log | 200 | `47e2e1d4-f70f-4492-bc08-9b33b63807dd` | insufficient_evidence | — |  |
| PI06 | prompt_injection | instruction plus real human text | 200 | `37fb19ef-86c9-4003-a8d3-b6c1c78b67b4` | unsure | 0.190 |  |
| MF01 | malformed | text is only whitespace | 400 | `—` | — | — |  |
| MF02 | malformed | text is a single character | 200 | `65885732-f5de-4386-8b1e-fd0d3f2de316` | insufficient_evidence | — |  |
| MF03 | malformed | text is control characters | 200 | `d145c9f1-3433-4deb-86ec-1eb68d2d3f13` | insufficient_evidence | — |  |
| MF04 | malformed | text is only punctuation | 200 | `5cf64a4b-aece-4689-869a-975383829548` | insufficient_evidence | — |  |
| MF05 | malformed | text is a very long single word | 200 | `d52df01b-7bf7-4569-a1a2-45c1a224489d` | insufficient_evidence | — |  |
| MF06 | malformed | text is emoji only | 200 | `7d864263-0dfd-43cd-bd38-1b4a74abca31` | insufficient_evidence | — |  |
| MF07 | malformed | text is right-to-left script | 200 | `4ebf3541-e69a-46db-8c17-8ae5fe745d23` | insufficient_evidence | — |  |
| MF08 | malformed | text is 60,000 characters | 413 | `—` | — | — |  |
| RQ01 | malformed | no text field at all | 400 | `—` | — | — |  |
| RQ02 | malformed | no creator_id | 400 | `—` | — | — |  |
| RQ03 | malformed | text is a number | 400 | `—` | — | — |  |
| RQ04 | malformed | text is a list | 400 | `—` | — | — |  |
| RQ05 | malformed | text is null | 400 | `—` | — | — |  |
| RQ06 | malformed | creator_id is an object | 400 | `—` | — | — |  |
| RQ07 | malformed | body is a JSON array, not an object | 400 | `—` | — | — |  |
| RQ08 | malformed | body is unparseable JSON | 400 | `—` | — | — |  |
| RQ09 | malformed | body is empty | 400 | `—` | — | — |  |
| RQ10 | malformed | body is form-encoded, not JSON | 429 | `—` | — | — |  |
| RQ11 | malformed | body is JSON claiming to be plain text | 429 | `—` | — | — |  |
| RQ12 | malformed | deeply nested JSON | 400 | `—` | — | — |  |
| FL01_01 | flood_same_creator | 20 rapid submissions from one creator | 200 | `75cecf22-1abf-4c2b-8039-31800f603e90` | insufficient_evidence | — |  |
| FL01_02 | flood_same_creator | 20 rapid submissions from one creator | 200 | `4797abc1-4eea-4b4a-a5b0-ebbab43565ad` | insufficient_evidence | — |  |
| FL01_03 | flood_same_creator | 20 rapid submissions from one creator | 200 | `c2aa4bb8-8957-48df-b801-abe4c3e74f18` | insufficient_evidence | — |  |
| FL01_04 | flood_same_creator | 20 rapid submissions from one creator | 200 | `e7b4859c-c5eb-4c38-a5a1-48ea78ab95ad` | insufficient_evidence | — |  |
| FL01_05 | flood_same_creator | 20 rapid submissions from one creator | 200 | `2ade2306-f387-45e4-ac8e-0a7aa65d7ca2` | insufficient_evidence | — |  |
| FL01_06 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — |  |
| FL01_07 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — |  |
| FL01_08 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — |  |
| FL01_09 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — |  |
| FL01_10 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — |  |
| FL01_11 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — |  |
| FL01_12 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — |  |

---

## By family

| Family | Attacks | Auto-BROKE | Left to judge |
|---|---|---|---|
| `evasion` | 10 | 0 | 10 |
| `false_positive` | 8 | 0 | 8 |
| `flood_same_creator` | 12 | 0 | 12 |
| `malformed` | 20 | 0 | 20 |
| `prompt_injection` | 6 | 0 | 6 |

> The **false_positive** family is the one to look at hardest. Those are
> written to be genuine human writing that reads as machine-like. Every one
> your service calls AI is a real writer it would have accused.

---

## What came back

The detail behind the table. Paste the interesting failures into your
README — the ones that show something, not the ten easiest.

### EV01 — `evasion`

*Targeting:* signal two: typos raise word variety

```json
{
  "id": "EV01",
  "status": 200,
  "content_id": "fb3bc97d-f57a-4c79-b949-8b2452c00c03",
  "creator_id": "attacker_EV01",
  "guess": "human",
  "confidence": 0.34,
  "model_score": 0.1635,
  "style_score": 0.5,
  "label": "This text shows patterns more consistent with human writing. This is an automated estimate, not proof of authorship.",
  "error": null,
  "verdict": ""
}
```

### EV02 — `evasion`

*Targeting:* signal two: broken-up sentences raise length spread

```json
{
  "id": "EV02",
  "status": 200,
  "content_id": "1396c599-34d3-4f18-8d9b-d2d73051fc13",
  "creator_id": "attacker_EV02",
  "guess": "human",
  "confidence": 0.41,
  "model_score": 0.5943,
  "style_score": 0.0,
  "label": "This text shows patterns more consistent with human writing. This is an automated estimate, not proof of authorship.",
  "error": null,
  "verdict": ""
}
```

### EV03 — `evasion`

*Targeting:* signal two: a pasted quotation changes the shape

```json
{
  "id": "EV03",
  "status": 200,
  "content_id": "33c521c5-7dc6-4e05-8f61-98aa315a9ab6",
  "creator_id": "attacker_EV03",
  "guess": "unsure",
  "confidence": 0.08,
  "model_score": 0.6662,
  "style_score": 0.2566,
  "label": "The available signals do not support a reliable classification. No conclusion about authorship should be drawn from this result.",
  "error": null,
  "verdict": ""
}
```

### EV04 — `evasion`

*Targeting:* signal one: unusual words raise perplexity

```json
{
  "id": "EV04",
  "status": 200,
  "content_id": "c552b9ca-fde0-46bf-8ca1-26c1e2f79307",
  "creator_id": "attacker_EV04",
  "guess": "unsure",
  "confidence": 0.11,
  "model_score": 0.6114,
  "style_score": 0.5,
  "label": "The available signals do not support a reliable classification. No conclusion about authorship should be drawn from this result.",
  "error": null,
  "verdict": ""
}
```

### EV05 — `evasion`

*Targeting:* both signals: heavy human editing pass

```json
{
  "id": "EV05",
  "status": 200,
  "content_id": "a6838289-257b-4d0e-b482-8627761c29e3",
  "creator_id": "attacker_EV05",
  "guess": "human",
  "confidence": 0.65,
  "model_score": 0.3212,
  "style_score": 0.0247,
  "label": "This text shows patterns more consistent with human writing. This is an automated estimate, not proof of authorship.",
  "error": null,
  "verdict": ""
}
```

### EV06 — `evasion`

*Targeting:* signal two: one very long sentence and one very short

```json
{
  "id": "EV06",
  "status": 200,
  "content_id": "717a5a57-3fa5-4d43-acdc-aa023da8a257",
  "creator_id": "attacker_EV06",
  "guess": "human",
  "confidence": 0.43,
  "model_score": 0.5727,
  "style_score": 0.0,
  "label": "This text shows patterns more consistent with human writing. This is an automated estimate, not proof of authorship.",
  "error": null,
  "verdict": ""
}
```

### EV07 — `evasion`

*Targeting:* signal two: padding with punctuation

```json
{
  "id": "EV07",
  "status": 200,
  "content_id": "513b59a5-ed71-4a17-bd22-b5cfa0cad1f8",
  "creator_id": "attacker_EV07",
  "guess": "unsure",
  "confidence": 0.16,
  "model_score": 0.5862,
  "style_score": 0.25,
  "label": "The available signals do not support a reliable classification. No conclusion about authorship should be drawn from this result.",
  "error": null,
  "verdict": ""
}
```

### EV08 — `evasion`

*Targeting:* signal one: text below the token window

```json
{
  "id": "EV08",
  "status": 200,
  "content_id": "b0c6d169-c95d-49e7-84b6-250fca1f3946",
  "creator_id": "attacker_EV08",
  "guess": "insufficient_evidence",
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": "This piece is too short for us to assess, so we haven't made any judgment about it.",
  "error": null,
  "verdict": ""
}
```

### EV09 — `evasion`

*Targeting:* both: AI text with a human opening paragraph bolted on

```json
{
  "id": "EV09",
  "status": 200,
  "content_id": "5f276310-3f05-42b7-b163-e8f021019bbd",
  "creator_id": "attacker_EV09",
  "guess": "unsure",
  "confidence": 0.06,
  "model_score": 0.7042,
  "style_score": 0.2325,
  "label": "The available signals do not support a reliable classification. No conclusion about authorship should be drawn from this result.",
  "error": null,
  "verdict": ""
}
```

### EV10 — `evasion`

*Targeting:* signal two: repeated stanza structure

```json
{
  "id": "EV10",
  "status": 200,
  "content_id": "c44bfaaf-e652-46eb-90e4-a55681f123e7",
  "creator_id": "attacker_EV10",
  "guess": "ai",
  "confidence": 0.79,
  "model_score": 0.9792,
  "style_score": 0.8061,
  "label": "This text shows patterns associated with AI-generated writing. This result is not proof of AI use, and you can request a human review if you disagree.",
  "error": null,
  "verdict": ""
}
```

### FP01 — `false_positive`

*Targeting:* plain, clear human writing with no flourishes

```json
{
  "id": "FP01",
  "status": 200,
  "content_id": "77053631-3e2b-417c-98a4-431289326a0c",
  "creator_id": "attacker_FP01",
  "guess": "unsure",
  "confidence": 0.14,
  "model_score": 0.6175,
  "style_score": 0.2425,
  "label": "The available signals do not support a reliable classification. No conclusion about authorship should be drawn from this result.",
  "error": null,
  "verdict": ""
}
```

### FP02 — `false_positive`

*Targeting:* human writing in a formal register

```json
{
  "id": "FP02",
  "status": 200,
  "content_id": "0e36dff8-2ee0-4185-9994-d364cd7a7078",
  "creator_id": "attacker_FP02",
  "guess": "unsure",
  "confidence": 0.27,
  "model_score": 0.7387,
  "style_score": 0.5357,
  "label": "The available signals do not support a reliable classification. No conclusion about authorship should be drawn from this result.",
  "error": null,
  "verdict": ""
}
```

### FP03 — `false_positive`

*Targeting:* a non-native English speaker writing carefully

```json
{
  "id": "FP03",
  "status": 200,
  "content_id": "c4500152-d3e8-498e-9d14-507e274f78a6",
  "creator_id": "attacker_FP03",
  "guess": "unsure",
  "confidence": 0.18,
  "model_score": 0.8051,
  "style_score": 0.3718,
  "label": "The available signals do not support a reliable classification. No conclusion about authorship should be drawn from this result.",
  "error": null,
  "verdict": ""
}
```

### FP04 — `false_positive`

*Targeting:* a student essay written to a rubric

```json
{
  "id": "FP04",
  "status": 200,
  "content_id": "6bdd0e04-c458-44ff-98d2-a01a4b5b4d48",
  "creator_id": "attacker_FP04",
  "guess": "unsure",
  "confidence": 0.17,
  "model_score": 0.8329,
  "style_score": 0.3333,
  "label": "The available signals do not support a reliable classification. No conclusion about authorship should be drawn from this result.",
  "error": null,
  "verdict": ""
}
```

### FP05 — `false_positive`

*Targeting:* technical documentation written by a person

```json
{
  "id": "FP05",
  "status": 200,
  "content_id": "23e3233f-7290-42b8-9bcb-6597d6cac847",
  "creator_id": "attacker_FP05",
  "guess": "ai",
  "confidence": 0.66,
  "model_score": 0.8005,
  "style_score": 0.8589,
  "label": "This text shows patterns associated with AI-generated writing. This result is not proof of AI use, and you can request a human review if you disagree.",
  "error": null,
  "verdict": ""
}
```

### FP06 — `false_positive`

*Targeting:* a person imitating a formal template

```json
{
  "id": "FP06",
  "status": 200,
  "content_id": "e41e5347-447c-4c1b-a8d9-675a0fdaedaf",
  "creator_id": "attacker_FP06",
  "guess": "unsure",
  "confidence": 0.17,
  "model_score": 0.8814,
  "style_score": 0.2908,
  "label": "The available signals do not support a reliable classification. No conclusion about authorship should be drawn from this result.",
  "error": null,
  "verdict": ""
}
```

### FP07 — `false_positive`

*Targeting:* human writing that repeats a phrase deliberately

```json
{
  "id": "FP07",
  "status": 200,
  "content_id": "1eda0c21-f191-4b02-a8f8-1864f0c989d4",
  "creator_id": "attacker_FP07",
  "guess": "ai",
  "confidence": 0.38,
  "model_score": 0.8816,
  "style_score": 0.5,
  "label": "This text shows patterns associated with AI-generated writing. This result is not proof of AI use, and you can request a human review if you disagree.",
  "error": null,
  "verdict": ""
}
```

### FP08 — `false_positive`

*Targeting:* very short genuine human submission

```json
{
  "id": "FP08",
  "status": 200,
  "content_id": "00e1e2f7-7a71-4108-a1ec-0bd2ff4c78b9",
  "creator_id": "attacker_FP08",
  "guess": "insufficient_evidence",
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": "This piece is too short for us to assess, so we haven't made any judgment about it.",
  "error": null,
  "verdict": ""
}
```

### PI01 — `prompt_injection`

*Targeting:* instruction to ignore the check

```json
{
  "id": "PI01",
  "status": 200,
  "content_id": "359c91c7-ccd1-4f89-a780-2aa05ae5ef52",
  "creator_id": "attacker_PI01",
  "guess": "insufficient_evidence",
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": "This piece is too short for us to assess, so we haven't made any judgment about it.",
  "error": null,
  "verdict": ""
}
```

### PI02 — `prompt_injection`

*Targeting:* instruction disguised as a system message

```json
{
  "id": "PI02",
  "status": 200,
  "content_id": "8426ae1f-da20-4ee1-9ca4-f6edba79d2a0",
  "creator_id": "attacker_PI02",
  "guess": "insufficient_evidence",
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": "This piece is too short for us to assess, so we haven't made any judgment about it.",
  "error": null,
  "verdict": ""
}
```

### PI03 — `prompt_injection`

*Targeting:* instruction wrapped in the writer's voice

```json
{
  "id": "PI03",
  "status": 200,
  "content_id": "ebe37296-a79b-4b17-9afd-62e4ecc61a8b",
  "creator_id": "attacker_PI03",
  "guess": "unsure",
  "confidence": 0.05,
  "model_score": 0.5943,
  "style_score": 0.3569,
  "label": "The available signals do not support a reliable classification. No conclusion about authorship should be drawn from this result.",
  "error": null,
  "verdict": ""
}
```

### PI04 — `prompt_injection`

*Targeting:* attempt to make the label text hostile

```json
{
  "id": "PI04",
  "status": 200,
  "content_id": "d571d351-8246-4030-8786-4170856244ec",
  "creator_id": "attacker_PI04",
  "guess": "unsure",
  "confidence": 0.2,
  "model_score": 0.4998,
  "style_score": 0.3033,
  "label": "The available signals do not support a reliable classification. No conclusion about authorship should be drawn from this result.",
  "error": null,
  "verdict": ""
}
```

### PI05 — `prompt_injection`

*Targeting:* attempt to inject into the audit log

```json
{
  "id": "PI05",
  "status": 200,
  "content_id": "47e2e1d4-f70f-4492-bc08-9b33b63807dd",
  "creator_id": "attacker_PI05",
  "guess": "insufficient_evidence",
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": "This piece is too short for us to assess, so we haven't made any judgment about it.",
  "error": null,
  "verdict": ""
}
```

### PI06 — `prompt_injection`

*Targeting:* instruction plus real human text

```json
{
  "id": "PI06",
  "status": 200,
  "content_id": "37fb19ef-86c9-4003-a8d3-b6c1c78b67b4",
  "creator_id": "attacker_PI06",
  "guess": "unsure",
  "confidence": 0.19,
  "model_score": 0.5583,
  "style_score": 0.2546,
  "label": "The available signals do not support a reliable classification. No conclusion about authorship should be drawn from this result.",
  "error": null,
  "verdict": ""
}
```

### MF01 — `malformed`

*Targeting:* text is only whitespace

```json
{
  "id": "MF01",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_MF01",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### MF02 — `malformed`

*Targeting:* text is a single character

```json
{
  "id": "MF02",
  "status": 200,
  "content_id": "65885732-f5de-4386-8b1e-fd0d3f2de316",
  "creator_id": "attacker_MF02",
  "guess": "insufficient_evidence",
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": "This piece is too short for us to assess, so we haven't made any judgment about it.",
  "error": null,
  "verdict": ""
}
```

### MF03 — `malformed`

*Targeting:* text is control characters

```json
{
  "id": "MF03",
  "status": 200,
  "content_id": "d145c9f1-3433-4deb-86ec-1eb68d2d3f13",
  "creator_id": "attacker_MF03",
  "guess": "insufficient_evidence",
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": "This piece is too short for us to assess, so we haven't made any judgment about it.",
  "error": null,
  "verdict": ""
}
```

### MF04 — `malformed`

*Targeting:* text is only punctuation

```json
{
  "id": "MF04",
  "status": 200,
  "content_id": "5cf64a4b-aece-4689-869a-975383829548",
  "creator_id": "attacker_MF04",
  "guess": "insufficient_evidence",
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": "This piece is too short for us to assess, so we haven't made any judgment about it.",
  "error": null,
  "verdict": ""
}
```

### MF05 — `malformed`

*Targeting:* text is a very long single word

```json
{
  "id": "MF05",
  "status": 200,
  "content_id": "d52df01b-7bf7-4569-a1a2-45c1a224489d",
  "creator_id": "attacker_MF05",
  "guess": "insufficient_evidence",
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": "This piece is too short for us to assess, so we haven't made any judgment about it.",
  "error": null,
  "verdict": ""
}
```

### MF06 — `malformed`

*Targeting:* text is emoji only

```json
{
  "id": "MF06",
  "status": 200,
  "content_id": "7d864263-0dfd-43cd-bd38-1b4a74abca31",
  "creator_id": "attacker_MF06",
  "guess": "insufficient_evidence",
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": "This piece is too short for us to assess, so we haven't made any judgment about it.",
  "error": null,
  "verdict": ""
}
```

### MF07 — `malformed`

*Targeting:* text is right-to-left script

```json
{
  "id": "MF07",
  "status": 200,
  "content_id": "4ebf3541-e69a-46db-8c17-8ae5fe745d23",
  "creator_id": "attacker_MF07",
  "guess": "insufficient_evidence",
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": "This piece is too short for us to assess, so we haven't made any judgment about it.",
  "error": null,
  "verdict": ""
}
```

### MF08 — `malformed`

*Targeting:* text is 60,000 characters

```json
{
  "id": "MF08",
  "status": 413,
  "content_id": null,
  "creator_id": "attacker_MF08",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ01 — `malformed`

*Targeting:* no text field at all

```json
{
  "id": "RQ01",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_RQ01",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ02 — `malformed`

*Targeting:* no creator_id

```json
{
  "id": "RQ02",
  "status": 400,
  "content_id": null,
  "creator_id": null,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ03 — `malformed`

*Targeting:* text is a number

```json
{
  "id": "RQ03",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_RQ03",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ04 — `malformed`

*Targeting:* text is a list

```json
{
  "id": "RQ04",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_RQ04",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ05 — `malformed`

*Targeting:* text is null

```json
{
  "id": "RQ05",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_RQ05",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ06 — `malformed`

*Targeting:* creator_id is an object

```json
{
  "id": "RQ06",
  "status": 400,
  "content_id": null,
  "creator_id": {
    "id": "x"
  },
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ07 — `malformed`

*Targeting:* body is a JSON array, not an object

```json
{
  "id": "RQ07",
  "status": 400,
  "content_id": null,
  "creator_id": null,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ08 — `malformed`

*Targeting:* body is unparseable JSON

```json
{
  "id": "RQ08",
  "status": 400,
  "content_id": null,
  "creator_id": null,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ09 — `malformed`

*Targeting:* body is empty

```json
{
  "id": "RQ09",
  "status": 400,
  "content_id": null,
  "creator_id": null,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ10 — `malformed`

*Targeting:* body is form-encoded, not JSON

```json
{
  "id": "RQ10",
  "status": 429,
  "content_id": null,
  "creator_id": null,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ11 — `malformed`

*Targeting:* body is JSON claiming to be plain text

```json
{
  "id": "RQ11",
  "status": 429,
  "content_id": null,
  "creator_id": null,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ12 — `malformed`

*Targeting:* deeply nested JSON

```json
{
  "id": "RQ12",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_RQ12",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### FL01_01 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_01",
  "status": 200,
  "content_id": "75cecf22-1abf-4c2b-8039-31800f603e90",
  "creator_id": "attacker_flood",
  "guess": "insufficient_evidence",
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": "This piece is too short for us to assess, so we haven't made any judgment about it.",
  "error": null,
  "verdict": ""
}
```

### FL01_02 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_02",
  "status": 200,
  "content_id": "4797abc1-4eea-4b4a-a5b0-ebbab43565ad",
  "creator_id": "attacker_flood",
  "guess": "insufficient_evidence",
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": "This piece is too short for us to assess, so we haven't made any judgment about it.",
  "error": null,
  "verdict": ""
}
```

### FL01_03 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_03",
  "status": 200,
  "content_id": "c2aa4bb8-8957-48df-b801-abe4c3e74f18",
  "creator_id": "attacker_flood",
  "guess": "insufficient_evidence",
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": "This piece is too short for us to assess, so we haven't made any judgment about it.",
  "error": null,
  "verdict": ""
}
```

### FL01_04 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_04",
  "status": 200,
  "content_id": "e7b4859c-c5eb-4c38-a5a1-48ea78ab95ad",
  "creator_id": "attacker_flood",
  "guess": "insufficient_evidence",
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": "This piece is too short for us to assess, so we haven't made any judgment about it.",
  "error": null,
  "verdict": ""
}
```

### FL01_05 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_05",
  "status": 200,
  "content_id": "2ade2306-f387-45e4-ac8e-0a7aa65d7ca2",
  "creator_id": "attacker_flood",
  "guess": "insufficient_evidence",
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": "This piece is too short for us to assess, so we haven't made any judgment about it.",
  "error": null,
  "verdict": ""
}
```

### FL01_06 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_06",
  "status": 429,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### FL01_07 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_07",
  "status": 429,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### FL01_08 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_08",
  "status": 429,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### FL01_09 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_09",
  "status": 429,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### FL01_10 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_10",
  "status": 429,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### FL01_11 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_11",
  "status": 429,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### FL01_12 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_12",
  "status": 429,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```
