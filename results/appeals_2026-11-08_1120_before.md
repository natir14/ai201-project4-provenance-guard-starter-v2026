# Criterion 4 — appeals — before

- Produced by: `eval_appeals.py::main`
- Service: `app.py::submit`, `app.py::appeal`; log read through `GET /log`
- 3 trials · 2026-11-08 11:20

| Trial | Valid appeals passed | Unknown id | Duplicate | Trial |
|---|---|---|---|---|
| 1 | 5/5 | 404 | 409 | PASS |
| 2 | 5/5 | 404 | 409 | PASS |
| 3 | 5/5 | 404 | 409 | PASS |

## What actually came back

**Trial 1**

```json
{
  "appeals": [
    {
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
    {
      "submit_status": 200,
      "content_id": "951afe23-762a-4eae-bfcd-95c904d64805",
      "guess": "unsure",
      "appeal_status": 200,
      "appeal_response": {
        "appealed_at": "2026-11-08T16:20:18+00:00",
        "content_id": "951afe23-762a-4eae-bfcd-95c904d64805",
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
    {
      "submit_status": 200,
      "content_id": "42bdcb39-7a2a-4b32-83b3-4aedaff5a8bc",
      "guess": "ai",
      "appeal_status": 200,
      "appeal_response": {
        "appealed_at": "2026-11-08T16:20:18+00:00",
        "content_id": "42bdcb39-7a2a-4b32-83b3-4aedaff5a8bc",
        "message": "Thanks — your appeal is recorded and a person will review this decision. The original label is paused while they do.",
        "original_guess": "ai",
        "previous_status": "decided",
        "status": "under_review"
      },
      "appeal_entries_after": 1,
      "decision_unchanged": true,
      "log_entries_added": 1,
      "passed": true
    },
    {
      "submit_status": 200,
      "content_id": "9399cdd5-b744-4e2a-a861-ad5af7687d84",
      "guess": "unsure",
      "appeal_status": 200,
      "appeal_response": {
        "appealed_at": "2026-11-08T16:20:18+00:00",
        "content_id": "9399cdd5-b744-4e2a-a861-ad5af7687d84",
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
    {
      "submit_status": 200,
      "content_id": "df51dc2d-f229-431a-ba08-56c2383a8374",
      "guess": "unsure",
      "appeal_status": 200,
      "appeal_response": {
        "appealed_at": "2026-11-08T16:20:19+00:00",
        "content_id": "df51dc2d-f229-431a-ba08-56c2383a8374",
        "message": "Thanks — your appeal is recorded and a person will review this decision. The original label is paused while they do.",
        "original_guess": "unsure",
        "previous_status": "decided",
        "status": "under_review"
      },
      "appeal_entries_after": 1,
      "decision_unchanged": true,
      "log_entries_added": 1,
      "passed": true
    }
  ],
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

**Trial 2**

```json
{
  "appeals": [
    {
      "submit_status": 200,
      "content_id": "aa2201dd-2870-4223-aaf2-02fc24fb8236",
      "guess": "unsure",
      "appeal_status": 200,
      "appeal_response": {
        "appealed_at": "2026-11-08T16:20:19+00:00",
        "content_id": "aa2201dd-2870-4223-aaf2-02fc24fb8236",
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
    {
      "submit_status": 200,
      "content_id": "5e1dd8a6-aa59-490b-8d57-f224b8bdb46b",
      "guess": "unsure",
      "appeal_status": 200,
      "appeal_response": {
        "appealed_at": "2026-11-08T16:20:20+00:00",
        "content_id": "5e1dd8a6-aa59-490b-8d57-f224b8bdb46b",
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
    {
      "submit_status": 200,
      "content_id": "df19a1e9-7fa3-47fd-8c3b-86c6654155e3",
      "guess": "ai",
      "appeal_status": 200,
      "appeal_response": {
        "appealed_at": "2026-11-08T16:20:20+00:00",
        "content_id": "df19a1e9-7fa3-47fd-8c3b-86c6654155e3",
        "message": "Thanks — your appeal is recorded and a person will review this decision. The original label is paused while they do.",
        "original_guess": "ai",
        "previous_status": "decided",
        "status": "under_review"
      },
      "appeal_entries_after": 1,
      "decision_unchanged": true,
      "log_entries_added": 1,
      "passed": true
    },
    {
      "submit_status": 200,
      "content_id": "7b9230f3-bd44-40f9-911b-70bd753ac7d5",
      "guess": "unsure",
      "appeal_status": 200,
      "appeal_response": {
        "appealed_at": "2026-11-08T16:20:21+00:00",
        "content_id": "7b9230f3-bd44-40f9-911b-70bd753ac7d5",
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
    {
      "submit_status": 200,
      "content_id": "950c8ecd-ea82-4a70-a6c7-d83ef804fb23",
      "guess": "unsure",
      "appeal_status": 200,
      "appeal_response": {
        "appealed_at": "2026-11-08T16:20:21+00:00",
        "content_id": "950c8ecd-ea82-4a70-a6c7-d83ef804fb23",
        "message": "Thanks — your appeal is recorded and a person will review this decision. The original label is paused while they do.",
        "original_guess": "unsure",
        "previous_status": "decided",
        "status": "under_review"
      },
      "appeal_entries_after": 1,
      "decision_unchanged": true,
      "log_entries_added": 1,
      "passed": true
    }
  ],
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

**Trial 3**

```json
{
  "appeals": [
    {
      "submit_status": 200,
      "content_id": "d513a35c-6c41-45a6-84aa-270cb6436301",
      "guess": "unsure",
      "appeal_status": 200,
      "appeal_response": {
        "appealed_at": "2026-11-08T16:20:21+00:00",
        "content_id": "d513a35c-6c41-45a6-84aa-270cb6436301",
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
    {
      "submit_status": 200,
      "content_id": "abc1b3bb-b7f3-4269-a2c9-6b72f56c6758",
      "guess": "unsure",
      "appeal_status": 200,
      "appeal_response": {
        "appealed_at": "2026-11-08T16:20:22+00:00",
        "content_id": "abc1b3bb-b7f3-4269-a2c9-6b72f56c6758",
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
    {
      "submit_status": 200,
      "content_id": "001030e7-6876-4707-898a-4612441f9a69",
      "guess": "ai",
      "appeal_status": 200,
      "appeal_response": {
        "appealed_at": "2026-11-08T16:20:22+00:00",
        "content_id": "001030e7-6876-4707-898a-4612441f9a69",
        "message": "Thanks — your appeal is recorded and a person will review this decision. The original label is paused while they do.",
        "original_guess": "ai",
        "previous_status": "decided",
        "status": "under_review"
      },
      "appeal_entries_after": 1,
      "decision_unchanged": true,
      "log_entries_added": 1,
      "passed": true
    },
    {
      "submit_status": 200,
      "content_id": "ef26637f-8d50-45df-a249-978ec16aaa9d",
      "guess": "unsure",
      "appeal_status": 200,
      "appeal_response": {
        "appealed_at": "2026-11-08T16:20:23+00:00",
        "content_id": "ef26637f-8d50-45df-a249-978ec16aaa9d",
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
    {
      "submit_status": 200,
      "content_id": "cc7271b2-924a-4551-abce-91b8dc8de853",
      "guess": "unsure",
      "appeal_status": 200,
      "appeal_response": {
        "appealed_at": "2026-11-08T16:20:23+00:00",
        "content_id": "cc7271b2-924a-4551-abce-91b8dc8de853",
        "message": "Thanks — your appeal is recorded and a person will review this decision. The original label is paused while they do.",
        "original_guess": "unsure",
        "previous_status": "decided",
        "status": "under_review"
      },
      "appeal_entries_after": 1,
      "decision_unchanged": true,
      "log_entries_added": 1,
      "passed": true
    }
  ],
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
