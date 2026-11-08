"""
Tests for POST /appeal — Milestones 5.4 and 5.5.

    python -m unittest test_appeal -v

Flask's test client, no server, no model. Every test writes to a temporary
audit log; the last check makes sure logs/audit.jsonl is never touched.

Covered: validation (400), unknown ids (404), creator mismatch (403),
recording an appeal (200), duplicate appeals (409), and duplicates that
arrive at the same moment.
"""

import shutil
import tempfile
import threading
import unittest
from datetime import datetime
from pathlib import Path
from unittest import mock

import audit
import config

import app as service

DECISION_ID = "3f2b8c1e-5d4a-4f7e-9a0b-6c1d2e3f4a5b"
SHORT_ID = "9a7d0c3b-1e2f-4a5b-8c6d-7e8f9a0b1c2d"
REASONING = "I wrote this myself. English is my second language, so I keep my sentences simple."
MESSAGE = ("Thanks — your appeal is recorded and a person will review this decision. "
           "The original label is paused while they do.")


class AppealTestCase(unittest.TestCase):
    """A temporary log holding one scored decision and one insufficient_evidence one."""

    @classmethod
    def setUpClass(cls):
        cls.real_log = config.AUDIT_LOG
        cls.real_log_bytes = cls.real_log.read_bytes() if cls.real_log.exists() else None

    def setUp(self):
        tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        patcher = mock.patch.multiple(config, LOG_DIR=tmp, AUDIT_LOG=tmp / "audit.jsonl")
        patcher.start()
        self.addCleanup(patcher.stop)

        audit.log_decision(content_id=DECISION_ID, creator_id="writer-042", guess="ai",
                           model_score=0.9, style_score=0.6, combined_score=0.75,
                           label="label text", confidence=0.5, text_length=500)
        audit.log_decision(content_id=SHORT_ID, creator_id="poet-7",
                           guess="insufficient_evidence", label="too short",
                           confidence=None, text_length=80, reason="too_short_to_assess")
        self.seeded = audit.read_entries()
        self.client = service.app.test_client()
        # Rate-limit counts live in memory for the whole run; start each test fresh.
        getattr(service.limiter, "reset", lambda: None)()

    def appeal(self, body):
        return self.client.post("/appeal", json=body)

    def new_entries(self):
        return audit.read_entries()[len(self.seeded):]

    def appeal_entries(self, content_id=None):
        return [e for e in audit.read_entries() if e.get("event") == "appeal"
                and (content_id is None or e["content_id"] == content_id)]

    def assert_rejected(self, response, status, error, field):
        self.assertEqual(response.status_code, status)
        self.assertEqual(response.get_json(),
                         {"error": error, "field": field, "message": response.get_json()["message"]})
        self.assertTrue(response.get_json()["message"])

    def assert_originals_unchanged(self):
        decisions = [e for e in audit.read_entries() if "event" not in e]
        self.assertEqual(decisions, self.seeded)


# ── 400: validation ──────────────────────────────────────────────────────────

class MalformedBody(AppealTestCase):
    def test_not_a_json_object(self):
        cases = {
            "not json": self.client.post("/appeal", data="not json",
                                         content_type="application/json"),
            "truncated json": self.client.post("/appeal", data='{"content_id": ',
                                               content_type="application/json"),
            "no JSON header": self.client.post("/appeal", data='{"content_id": "x"}'),
            "no body": self.client.post("/appeal"),
            "a list": self.appeal(["content_id", "reasoning"]),
            "a string": self.appeal("just a string"),
            "a number": self.appeal(42),
        }
        for name, r in cases.items():
            with self.subTest(body=name):
                self.assert_rejected(r, 400, "invalid_input", None)


class ContentIdValidation(AppealTestCase):
    def test_missing_blank_and_wrong_type(self):
        for bad in [None, "", "   ", "\n\t", 123, 1.5, True, [DECISION_ID], {"id": DECISION_ID}]:
            with self.subTest(content_id=bad):
                body = {"reasoning": REASONING}
                if bad is not None:
                    body["content_id"] = bad
                self.assert_rejected(self.appeal(body), 400, "invalid_input", "content_id")

    def test_explicit_null(self):
        r = self.appeal({"content_id": None, "reasoning": REASONING})
        self.assert_rejected(r, 400, "invalid_input", "content_id")


class ReasoningValidation(AppealTestCase):
    def test_missing_blank_and_wrong_type(self):
        for bad in ["missing", None, "", "   ", "\n\t ", 5, False, ["why"], {"why": "x"}]:
            with self.subTest(reasoning=bad):
                body = {"content_id": DECISION_ID}
                if bad != "missing":
                    body["reasoning"] = bad
                self.assert_rejected(self.appeal(body), 400, "invalid_input", "reasoning")

    def test_length_boundary(self):
        self.assertEqual(config.MAX_REASONING_CHARS, 2000)
        over_cap = "x" * (config.MAX_REASONING_CHARS + 1)
        self.assert_rejected(self.appeal({"content_id": DECISION_ID, "reasoning": over_cap}),
                             400, "invalid_input", "reasoning")
        at_cap = "x" * config.MAX_REASONING_CHARS
        self.assertEqual(self.appeal({"content_id": DECISION_ID, "reasoning": at_cap}).status_code, 200)
        self.assertEqual(self.appeal_entries(DECISION_ID)[0]["reasoning"], at_cap)


class CreatorIdValidation(AppealTestCase):
    def test_wrong_type_or_blank_is_refused(self):
        for bad in ["", "   ", 7, False, ["writer-042"], {"id": "writer-042"}]:
            with self.subTest(creator_id=bad):
                r = self.appeal({"content_id": DECISION_ID, "reasoning": REASONING,
                                 "creator_id": bad})
                self.assert_rejected(r, 400, "invalid_input", "creator_id")


# ── 404: unknown ids ─────────────────────────────────────────────────────────

class UnknownContentId(AppealTestCase):
    def test_unknown_id(self):
        r = self.appeal({"content_id": "no-such-id", "reasoning": REASONING})
        self.assert_rejected(r, 404, "unknown_content_id", "content_id")
        self.assertIn("check", r.get_json()["message"].lower())

    def test_mistyped_ids(self):
        for typo in [DECISION_ID[:-1] + "c",        # one character off
                     DECISION_ID[:-1],              # truncated
                     DECISION_ID.upper(),           # wrong case
                     f" {DECISION_ID} ",            # stray whitespace
                     DECISION_ID + "x"]:
            with self.subTest(content_id=typo):
                r = self.appeal({"content_id": typo, "reasoning": REASONING})
                self.assert_rejected(r, 404, "unknown_content_id", "content_id")

    def test_a_rejection_entry_is_not_a_decision(self):
        # Even a rejection carrying a content_id (hand-written here; the service
        # never writes one) must not count as something to appeal.
        audit.log_rejection(creator_id="x", reason="invalid_input", content_id="rejected-only")
        r = self.appeal({"content_id": "rejected-only", "reasoning": REASONING})
        self.assert_rejected(r, 404, "unknown_content_id", "content_id")

    def test_an_appeal_entry_alone_is_not_a_decision(self):
        audit.log_appeal(content_id="appeal-only", creator_id="x", reasoning="r")
        r = self.appeal({"content_id": "appeal-only", "reasoning": REASONING})
        self.assert_rejected(r, 404, "unknown_content_id", "content_id")

    def test_submit_rejections_cannot_be_appealed(self):
        # A rejected /submit leaves no content_id at all, so nothing to find.
        self.client.post("/submit", json={"text": "", "creator_id": "w1"})
        rejection = audit.read_entries()[-1]
        self.assertEqual(rejection["event"], "rejected")
        self.assertNotIn("content_id", rejection)


# ── 403: creator mismatch ────────────────────────────────────────────────────

class CreatorMismatch(AppealTestCase):
    def test_different_creator_is_refused(self):
        for other in ["someone-else", "WRITER-042", "writer-042 ", "poet-7"]:
            with self.subTest(creator_id=other):
                r = self.appeal({"content_id": DECISION_ID, "reasoning": REASONING,
                                 "creator_id": other})
                self.assert_rejected(r, 403, "creator_mismatch", "creator_id")

    def test_message_does_not_reveal_the_real_submitter(self):
        r = self.appeal({"content_id": DECISION_ID, "reasoning": REASONING,
                         "creator_id": "someone-else"})
        self.assertNotIn("writer-042", r.get_data(as_text=True))

    def test_mismatch_is_logged_and_records_no_appeal(self):
        self.appeal({"content_id": DECISION_ID, "reasoning": REASONING,
                     "creator_id": "someone-else"})
        [entry] = self.new_entries()
        self.assertEqual(entry["event"], "rejected")
        self.assertEqual(entry["reason"], "creator_mismatch")
        self.assertEqual(entry["http_status"], 403)
        self.assertEqual(entry["field"], "creator_id")
        self.assertEqual(entry["endpoint"], "/appeal")
        self.assertEqual(entry["creator_id"], "someone-else")
        self.assertEqual(entry["attempted_content_id"], DECISION_ID)
        self.assertNotIn("content_id", entry)
        self.assertNotIn("reasoning", entry)
        self.assertEqual(self.appeal_entries(), [])
        self.assert_originals_unchanged()

    def test_mismatch_leaves_the_item_appealable_by_its_owner(self):
        self.appeal({"content_id": DECISION_ID, "reasoning": REASONING,
                     "creator_id": "someone-else"})
        r = self.appeal({"content_id": DECISION_ID, "reasoning": REASONING,
                         "creator_id": "writer-042"})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.get_json()["previous_status"], "decided")


# ── 200: appeal recorded ─────────────────────────────────────────────────────

class SuccessfulAppeal(AppealTestCase):
    def assert_recorded(self, r, content_id, creator_id, original_guess):
        self.assertEqual(r.status_code, 200)
        body = r.get_json()
        self.assertEqual(set(body), {"content_id", "status", "previous_status",
                                     "original_guess", "message", "appealed_at"})
        self.assertEqual(body["content_id"], content_id)
        self.assertEqual(body["status"], "under_review")
        self.assertEqual(body["previous_status"], "decided")
        self.assertEqual(body["original_guess"], original_guess)
        self.assertEqual(body["message"], MESSAGE)

        [entry] = self.appeal_entries(content_id)
        self.assertEqual(entry, {
            "timestamp": body["appealed_at"],
            "content_id": content_id,
            "creator_id": creator_id,
            "event": "appeal",
            "status": "under_review",
            "reasoning": REASONING,
        })
        self.assertEqual(len(self.new_entries()), 1)              # exactly one entry appended
        self.assert_originals_unchanged()

    def test_with_matching_creator_id(self):
        r = self.appeal({"content_id": DECISION_ID, "reasoning": REASONING,
                         "creator_id": "writer-042"})
        self.assert_recorded(r, DECISION_ID, "writer-042", "ai")

    def test_with_creator_id_omitted(self):
        r = self.appeal({"content_id": DECISION_ID, "reasoning": REASONING})
        self.assert_recorded(r, DECISION_ID, "writer-042", "ai")

    def test_with_creator_id_null(self):
        r = self.appeal({"content_id": DECISION_ID, "reasoning": REASONING, "creator_id": None})
        self.assert_recorded(r, DECISION_ID, "writer-042", "ai")

    def test_insufficient_evidence_can_be_appealed(self):
        r = self.appeal({"content_id": SHORT_ID, "reasoning": REASONING})
        self.assert_recorded(r, SHORT_ID, "poet-7", "insufficient_evidence")

    def test_appealed_at_is_a_utc_timestamp(self):
        r = self.appeal({"content_id": DECISION_ID, "reasoning": REASONING})
        stamp = datetime.fromisoformat(r.get_json()["appealed_at"])
        self.assertIsNotNone(stamp.tzinfo)
        self.assertEqual(stamp.utcoffset().total_seconds(), 0)

    def test_appeal_goes_after_the_decision(self):
        self.appeal({"content_id": DECISION_ID, "reasoning": REASONING})
        trail = [e.get("event", "decision") for e in audit.entries_for(DECISION_ID)]
        self.assertEqual(trail, ["decision", "appeal"])

    def test_appealing_one_item_leaves_the_other_alone(self):
        self.appeal({"content_id": DECISION_ID, "reasoning": REASONING})
        self.assertEqual(self.appeal_entries(SHORT_ID), [])
        self.assertEqual(service._current_status(SHORT_ID), "decided")
        self.assertEqual(service._current_status(DECISION_ID), "under_review")

    def test_nothing_is_rescored(self):
        import detector
        import stylometry
        with mock.patch.object(detector, "model_signal") as model, \
             mock.patch.object(stylometry, "style_signal") as style:
            self.appeal({"content_id": DECISION_ID, "reasoning": REASONING})
        model.assert_not_called()
        style.assert_not_called()

    def test_decision_made_through_submit(self):
        import detector
        text = ("I started keeping a notebook last spring because my memory for small "
                "things was going. At first it was only lists, groceries and phone "
                "numbers. Then it turned into something else, a place where I argued "
                "with myself about books I had not finished. Some pages are just one "
                "sentence. Others run on for three pages about a bus driver who sang.")
        with mock.patch.object(detector, "model_signal", return_value=0.6):
            submitted = self.client.post("/submit", json={"text": text, "creator_id": "w5"}).get_json()
        r = self.appeal({"content_id": submitted["content_id"], "reasoning": REASONING})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.get_json()["original_guess"], submitted["guess"])
        [entry] = self.appeal_entries(submitted["content_id"])
        self.assertEqual(entry["creator_id"], "w5")


# ── 409: one appeal per item ─────────────────────────────────────────────────

class DuplicateAppeals(AppealTestCase):
    FIRST = {"content_id": DECISION_ID, "reasoning": REASONING}

    def test_first_200_then_409_then_409(self):
        first = self.appeal(self.FIRST)
        self.assertEqual(first.status_code, 200)

        second = self.appeal({"content_id": DECISION_ID, "reasoning": "Sending it again."})
        self.assert_rejected(second, 409, "already_under_review", "content_id")
        third = self.appeal({"content_id": DECISION_ID, "reasoning": "And once more."})
        self.assert_rejected(third, 409, "already_under_review", "content_id")

        message = second.get_json()["message"]
        self.assertIn("already recorded", message)
        self.assertIn("don't need to send it again", message)

    def test_exactly_one_appeal_and_first_one_unchanged(self):
        first_body = self.appeal(self.FIRST).get_json()
        [first_entry] = self.appeal_entries(DECISION_ID)

        for reasoning in ("Second try.", "Third try.", "Fourth try."):
            self.appeal({"content_id": DECISION_ID, "reasoning": reasoning})

        self.assertEqual(self.appeal_entries(DECISION_ID), [first_entry])
        self.assertEqual(first_entry["timestamp"], first_body["appealed_at"])
        self.assertEqual(first_entry["reasoning"], REASONING)
        self.assert_originals_unchanged()
        self.assertEqual(service._current_status(DECISION_ID), "under_review")

    def test_each_duplicate_logs_one_rejection(self):
        self.appeal(self.FIRST)
        for n in range(3):
            with self.subTest(attempt=n + 2):
                before = len(audit.read_entries())
                r = self.appeal({"content_id": DECISION_ID, "reasoning": "Again."})
                self.assertEqual(r.status_code, 409)
                entries = audit.read_entries()
                self.assertEqual(len(entries), before + 1)
                entry = entries[-1]
                self.assertEqual(entry["event"], "rejected")
                self.assertEqual(entry["reason"], "already_under_review")
                self.assertEqual(entry["http_status"], 409)
                self.assertEqual(entry["field"], "content_id")
                self.assertEqual(entry["endpoint"], "/appeal")
                self.assertEqual(entry["attempted_content_id"], DECISION_ID)
                self.assertNotIn("content_id", entry)
                self.assertNotIn("reasoning", entry)

    def test_other_items_can_still_be_appealed(self):
        self.appeal(self.FIRST)
        r = self.appeal({"content_id": SHORT_ID, "reasoning": REASONING})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.get_json()["previous_status"], "decided")
        self.assertEqual(len(self.appeal_entries(SHORT_ID)), 1)
        self.assertEqual(len(self.appeal_entries(DECISION_ID)), 1)

    def test_creator_mismatch_still_403_when_under_review(self):
        # The creator check comes first: a stranger learns nothing about
        # whether the item has been appealed.
        self.appeal(self.FIRST)
        r = self.appeal({"content_id": DECISION_ID, "reasoning": REASONING,
                         "creator_id": "someone-else"})
        self.assert_rejected(r, 403, "creator_mismatch", "creator_id")
        self.assertEqual(len(self.appeal_entries(DECISION_ID)), 1)

    def test_omitted_null_or_matching_creator_cannot_bypass(self):
        self.appeal(self.FIRST)
        for extra in ({}, {"creator_id": None}, {"creator_id": "writer-042"}):
            with self.subTest(creator=extra):
                r = self.appeal({"content_id": DECISION_ID, "reasoning": REASONING, **extra})
                self.assert_rejected(r, 409, "already_under_review", "content_id")
        self.assertEqual(len(self.appeal_entries(DECISION_ID)), 1)

    def test_duplicate_of_insufficient_evidence_item(self):
        self.assertEqual(self.appeal({"content_id": SHORT_ID, "reasoning": REASONING}).status_code, 200)
        r = self.appeal({"content_id": SHORT_ID, "reasoning": REASONING})
        self.assert_rejected(r, 409, "already_under_review", "content_id")

    def test_no_rescoring_on_any_attempt(self):
        import detector
        import stylometry
        with mock.patch.object(detector, "model_signal") as model, \
             mock.patch.object(stylometry, "style_signal") as style:
            self.appeal(self.FIRST)
            self.appeal(self.FIRST)
            self.appeal(self.FIRST)
        model.assert_not_called()
        style.assert_not_called()


# ── Simultaneous duplicates ──────────────────────────────────────────────────

class _SpyLock:
    """A real lock that also reports when two requests have reached it."""

    def __init__(self):
        self._lock = threading.Lock()
        self._count = threading.Lock()
        self.arrivals = 0
        self.both_arrived = threading.Event()

    def __enter__(self):
        with self._count:
            self.arrivals += 1
            if self.arrivals >= 2:
                self.both_arrived.set()
        self._lock.acquire()
        return self

    def __exit__(self, *exc):
        self._lock.release()
        return False


class ConcurrentAppeals(AppealTestCase):
    """
    Two appeals for one item at the same moment: exactly one is recorded.

    No sleeps. The first request to read the status is held INSIDE the
    critical section until the other request has reached the lock, which
    forces the interleaving the race needs. If the check weren't under the
    lock, the second request would never reach it and the test fails on
    `both_arrived` rather than passing by luck.
    """

    WAIT = 5    # seconds — a safety net for a broken run, never hit when it passes

    def run_in_threads(self, bodies):
        results, errors = [None] * len(bodies), []

        def send(i, body):
            try:
                r = service.app.test_client().post("/appeal", json=body)  # one client each
                results[i] = (r.status_code, r.get_json())
            except Exception as exc:  # noqa: BLE001
                errors.append(exc)

        threads = [threading.Thread(target=send, args=(i, b)) for i, b in enumerate(bodies)]
        for t in threads:
            t.start()
        return threads, results, errors

    def join(self, threads, errors):
        for t in threads:
            t.join(self.WAIT * 2)
            self.assertFalse(t.is_alive(), "a request thread never finished")
        self.assertEqual(errors, [])

    def test_two_simultaneous_appeals(self):
        spy = _SpyLock()
        first_checked, go = threading.Event(), threading.Event()
        real_status = service._current_status

        def held_status(content_id):
            status = real_status(content_id)
            first_checked.set()
            go.wait(self.WAIT)          # returns at once for the second request
            return status

        body = {"content_id": DECISION_ID, "reasoning": REASONING, "creator_id": "writer-042"}
        with mock.patch.object(service, "_APPEAL_LOCK", spy), \
             mock.patch.object(service, "_current_status", side_effect=held_status):
            threads, results, errors = self.run_in_threads([body, dict(body)])

            # One request has read "decided" and is paused inside the lock...
            self.assertTrue(first_checked.wait(self.WAIT), "no request reached the status check")
            # ...and the other is at the lock, wanting to check too.
            self.assertTrue(spy.both_arrived.wait(self.WAIT),
                            "the second request never reached the lock — is the check unlocked?")
            go.set()
            self.join(threads, errors)

        self.assertEqual(sorted(code for code, _ in results), [200, 409])
        [conflict] = [body for code, body in results if code == 409]
        self.assertEqual(conflict["error"], "already_under_review")

        self.assertEqual(len(self.appeal_entries(DECISION_ID)), 1)
        self.assert_originals_unchanged()
        [rejection] = [e for e in audit.read_entries() if e.get("event") == "rejected"]
        self.assertEqual((rejection["reason"], rejection["http_status"]),
                         ("already_under_review", 409))
        self.assertEqual(spy.arrivals, 2)

    def test_burst_of_simultaneous_appeals(self):
        # Eight at once, released together by a barrier: one recorded, seven 409.
        n = 8
        barrier = threading.Barrier(n, timeout=self.WAIT)
        real_appeal = service.app.view_functions["appeal"]
        body = {"content_id": DECISION_ID, "reasoning": REASONING}

        def gated(*args, **kwargs):
            barrier.wait()
            return real_appeal(*args, **kwargs)

        with mock.patch.dict(service.app.view_functions, {"appeal": gated}):
            threads, results, errors = self.run_in_threads([dict(body) for _ in range(n)])
            self.join(threads, errors)

        codes = sorted(code for code, _ in results)
        self.assertEqual(codes, [200] + [409] * (n - 1))
        self.assertEqual(len(self.appeal_entries(DECISION_ID)), 1)
        self.assert_originals_unchanged()
        rejections = [e for e in audit.read_entries() if e.get("event") == "rejected"]
        self.assertEqual(len(rejections), n - 1)


# ── Rejections leave a trace, and never an appeal ────────────────────────────

class RejectionLogging(AppealTestCase):
    CASES = [
        ("not json", 400, "invalid_input", None, None, "unknown"),
        ({"reasoning": REASONING}, 400, "invalid_input", "content_id", None, "unknown"),
        ({"content_id": DECISION_ID}, 400, "invalid_input", "reasoning", DECISION_ID, "unknown"),
        ({"content_id": DECISION_ID, "reasoning": "x" * 2001}, 400, "invalid_input",
         "reasoning", DECISION_ID, "unknown"),
        ({"content_id": DECISION_ID, "reasoning": REASONING, "creator_id": 7}, 400,
         "invalid_input", "creator_id", DECISION_ID, "unknown"),
        ({"content_id": "no-such-id", "reasoning": REASONING, "creator_id": "w9"}, 404,
         "unknown_content_id", "content_id", "no-such-id", "w9"),
        ({"content_id": DECISION_ID, "reasoning": REASONING, "creator_id": "w9"}, 403,
         "creator_mismatch", "creator_id", DECISION_ID, "w9"),
    ]

    def send(self, body):
        if body == "not json":
            return self.client.post("/appeal", data=body, content_type="application/json")
        return self.appeal(body)

    def test_every_rejection_is_logged(self):
        for body, status, error, field, attempted, creator in self.CASES:
            with self.subTest(error=error, field=field):
                before = len(audit.read_entries())
                self.assertEqual(self.send(body).status_code, status)

                entries = audit.read_entries()
                self.assertEqual(len(entries), before + 1)       # exactly one new entry
                entry = entries[-1]
                self.assertEqual(entry["event"], "rejected")
                self.assertEqual(entry["status"], "rejected")
                self.assertEqual(entry["reason"], error)
                self.assertEqual(entry["field"], field)
                self.assertEqual(entry["http_status"], status)
                self.assertEqual(entry["endpoint"], "/appeal")
                self.assertEqual(entry.get("attempted_content_id"), attempted)
                self.assertEqual(entry["creator_id"], creator)
                self.assertNotIn("content_id", entry)            # never mistaken for a decision
                self.assertNotIn("reasoning", entry)             # the writer's words aren't logged

    def test_rejected_appeals_create_no_appeal_entries(self):
        for body, *_ in self.CASES:
            self.send(body)
        self.assertEqual(self.appeal_entries(), [])
        self.assert_originals_unchanged()
        self.assertEqual(service._current_status(DECISION_ID), "decided")

    def test_attempted_id_is_capped(self):
        self.appeal({"content_id": "z" * 5000, "reasoning": REASONING})
        self.assertEqual(len(audit.read_entries()[-1]["attempted_content_id"]), 100)


class RealLogUntouched(AppealTestCase):
    def test_real_audit_log_is_unchanged(self):
        self.appeal({"content_id": "no-such-id", "reasoning": REASONING})
        self.appeal({"content_id": DECISION_ID, "reasoning": REASONING})
        now = self.real_log.read_bytes() if self.real_log.exists() else None
        self.assertEqual(now, self.real_log_bytes)


if __name__ == "__main__":
    unittest.main()
