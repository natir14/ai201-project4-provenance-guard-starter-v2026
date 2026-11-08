# Attack run — before

- Produced by: `run_attacks.py::main`
- Service: `app.py::submit`
- 56 attacks · 2026-11-08 11:00
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
| EV01 | evasion | signal two: typos raise word variety | 200 | `2f34c821-ea09-46c9-8876-7f282af14518` | human | 0.340 |  |
| EV02 | evasion | signal two: broken-up sentences raise length spread | 200 | `65aada2d-ea5f-4802-9e82-32ce771a6a46` | human | 0.410 |  |
| EV03 | evasion | signal two: a pasted quotation changes the shape | 200 | `a3ea0b61-c005-48aa-8ba5-abc0158bbf46` | unsure | 0.080 |  |
| EV04 | evasion | signal one: unusual words raise perplexity | 200 | `ccae2225-db2e-4665-9cbc-3ef813bd4ccc` | unsure | 0.110 |  |
| EV05 | evasion | both signals: heavy human editing pass | 200 | `477e7af2-45a5-4e81-964e-cb425c92faf9` | human | 0.650 |  |
| EV06 | evasion | signal two: one very long sentence and one very short | 200 | `43c2a1f6-ec62-4986-8969-3cf8551203a2` | human | 0.430 |  |
| EV07 | evasion | signal two: padding with punctuation | 200 | `14496023-e02a-4ab4-bfd3-d2927df12c6f` | insufficient_evidence | — |  |
| EV08 | evasion | signal one: text below the token window | 200 | `a63424fe-24fc-4ab7-96f3-27c8a01f8dd0` | insufficient_evidence | — |  |
| EV09 | evasion | both: AI text with a human opening paragraph bolted on | 200 | `a4e158df-5782-43d1-a164-cab5e2ce0729` | unsure | 0.060 |  |
| EV10 | evasion | signal two: repeated stanza structure | 200 | `6b13f747-d056-41c6-92d4-98e9de8c63b1` | ai | 0.790 |  |
| FP01 | false_positive | plain, clear human writing with no flourishes | 200 | `09abfc82-81ba-41a7-98df-2f0d841acd5d` | unsure | 0.140 |  |
| FP02 | false_positive | human writing in a formal register | 200 | `4a0cb708-c9cd-4bc7-bef6-a25c799e3613` | unsure | 0.270 |  |
| FP03 | false_positive | a non-native English speaker writing carefully | 200 | `bff8d7de-7b8e-4ae1-938d-c5868fdcbeaa` | unsure | 0.180 |  |
| FP04 | false_positive | a student essay written to a rubric | 200 | `b98eb68b-9ccf-444e-83ec-e1063d52f886` | unsure | 0.170 |  |
| FP05 | false_positive | technical documentation written by a person | 200 | `d550a266-f088-4d04-a9ae-1b4107d0e791` | ai | 0.660 |  |
| FP06 | false_positive | a person imitating a formal template | 200 | `4e1e56de-d166-439b-bdb4-002a80aaa11a` | unsure | 0.170 |  |
| FP07 | false_positive | human writing that repeats a phrase deliberately | 200 | `0abd96e8-1d08-4d64-9814-f2dedd86aba2` | ai | 0.380 |  |
| FP08 | false_positive | very short genuine human submission | 200 | `fd8c9b2b-1910-4f28-b110-20cff265539a` | insufficient_evidence | — |  |
| PI01 | prompt_injection | instruction to ignore the check | 200 | `932e0e13-41ec-423f-8cdc-77689bf6e35d` | insufficient_evidence | — |  |
| PI02 | prompt_injection | instruction disguised as a system message | 200 | `60e3b2de-abb7-4f29-a1df-4ec959a9b37a` | insufficient_evidence | — |  |
| PI03 | prompt_injection | instruction wrapped in the writer's voice | 200 | `f3f86ee7-dd29-43df-8704-5e28ebd37c17` | unsure | 0.050 |  |
| PI04 | prompt_injection | attempt to make the label text hostile | 200 | `561a8476-4275-4ce4-a379-75936980fce5` | unsure | 0.200 |  |
| PI05 | prompt_injection | attempt to inject into the audit log | 200 | `1ef4b6de-0cd6-44db-96db-6d7ae824bb5d` | insufficient_evidence | — |  |
| PI06 | prompt_injection | instruction plus real human text | 200 | `1a8157ee-70fc-4ef9-a375-179f0a0ca791` | unsure | 0.190 |  |
| MF01 | malformed | text is only whitespace | 400 | `—` | — | — |  |
| MF02 | malformed | text is a single character | 200 | `3d9de495-b7e2-464f-b7f8-e0bed88b96b8` | insufficient_evidence | — |  |
| MF03 | malformed | text is control characters | 200 | `c6409c7b-8866-4a68-a55e-134fc30703bb` | insufficient_evidence | — |  |
| MF04 | malformed | text is only punctuation | 200 | `d914b2b2-4dfe-49e8-81c6-eff90b84dec3` | insufficient_evidence | — |  |
| MF05 | malformed | text is a very long single word | 200 | `c1cd99b3-3eec-46fb-b350-2d332aae31d0` | insufficient_evidence | — |  |
| MF06 | malformed | text is emoji only | 200 | `bdec1101-9a2a-4a98-a0e9-90b9d7df836d` | insufficient_evidence | — |  |
| MF07 | malformed | text is right-to-left script | 200 | `c2e1fa36-82ef-4cbe-bfd5-822b457a2f22` | insufficient_evidence | — |  |
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
| FL01_01 | flood_same_creator | 20 rapid submissions from one creator | 200 | `ddc6420c-e66c-48fd-b7bd-1cb62e5c0f59` | insufficient_evidence | — |  |
| FL01_02 | flood_same_creator | 20 rapid submissions from one creator | 200 | `72f2498f-eaa4-4e4a-a5a3-1cb8ba2c55e2` | insufficient_evidence | — |  |
| FL01_03 | flood_same_creator | 20 rapid submissions from one creator | 200 | `2676594e-a188-4017-9b85-1ba591e33278` | insufficient_evidence | — |  |
| FL01_04 | flood_same_creator | 20 rapid submissions from one creator | 200 | `d82c56bc-494e-4384-8879-a8f5073cb554` | insufficient_evidence | — |  |
| FL01_05 | flood_same_creator | 20 rapid submissions from one creator | 200 | `eab01bee-e0c5-493d-b7b5-2a48c1017eed` | insufficient_evidence | — |  |
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
  "content_id": "2f34c821-ea09-46c9-8876-7f282af14518",
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
  "content_id": "65aada2d-ea5f-4802-9e82-32ce771a6a46",
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
  "content_id": "a3ea0b61-c005-48aa-8ba5-abc0158bbf46",
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
  "content_id": "ccae2225-db2e-4665-9cbc-3ef813bd4ccc",
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
  "content_id": "477e7af2-45a5-4e81-964e-cb425c92faf9",
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
  "content_id": "43c2a1f6-ec62-4986-8969-3cf8551203a2",
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
  "content_id": "14496023-e02a-4ab4-bfd3-d2927df12c6f",
  "creator_id": "attacker_EV07",
  "guess": "insufficient_evidence",
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": "This piece is too short for us to assess, so we haven't made any judgment about it.",
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
  "content_id": "a63424fe-24fc-4ab7-96f3-27c8a01f8dd0",
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
  "content_id": "a4e158df-5782-43d1-a164-cab5e2ce0729",
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
  "content_id": "6b13f747-d056-41c6-92d4-98e9de8c63b1",
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
  "content_id": "09abfc82-81ba-41a7-98df-2f0d841acd5d",
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
  "content_id": "4a0cb708-c9cd-4bc7-bef6-a25c799e3613",
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
  "content_id": "bff8d7de-7b8e-4ae1-938d-c5868fdcbeaa",
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
  "content_id": "b98eb68b-9ccf-444e-83ec-e1063d52f886",
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
  "content_id": "d550a266-f088-4d04-a9ae-1b4107d0e791",
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
  "content_id": "4e1e56de-d166-439b-bdb4-002a80aaa11a",
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
  "content_id": "0abd96e8-1d08-4d64-9814-f2dedd86aba2",
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
  "content_id": "fd8c9b2b-1910-4f28-b110-20cff265539a",
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
  "content_id": "932e0e13-41ec-423f-8cdc-77689bf6e35d",
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
  "content_id": "60e3b2de-abb7-4f29-a1df-4ec959a9b37a",
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
  "content_id": "f3f86ee7-dd29-43df-8704-5e28ebd37c17",
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
  "content_id": "561a8476-4275-4ce4-a379-75936980fce5",
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
  "content_id": "1ef4b6de-0cd6-44db-96db-6d7ae824bb5d",
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
  "content_id": "1a8157ee-70fc-4ef9-a375-179f0a0ca791",
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
  "content_id": "3d9de495-b7e2-464f-b7f8-e0bed88b96b8",
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
  "content_id": "c6409c7b-8866-4a68-a55e-134fc30703bb",
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
  "content_id": "d914b2b2-4dfe-49e8-81c6-eff90b84dec3",
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
  "content_id": "c1cd99b3-3eec-46fb-b350-2d332aae31d0",
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
  "content_id": "bdec1101-9a2a-4a98-a0e9-90b9d7df836d",
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
  "content_id": "c2e1fa36-82ef-4cbe-bfd5-822b457a2f22",
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
  "content_id": "ddc6420c-e66c-48fd-b7bd-1cb62e5c0f59",
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
  "content_id": "72f2498f-eaa4-4e4a-a5a3-1cb8ba2c55e2",
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
  "content_id": "2676594e-a188-4017-9b85-1ba591e33278",
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
  "content_id": "d82c56bc-494e-4384-8879-a8f5073cb554",
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
  "content_id": "eab01bee-e0c5-493d-b7b5-2a48c1017eed",
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
