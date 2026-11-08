"""
Tests for rate limiting on POST /submit — Unit 8, Milestone 1.

    python -m unittest test_rate_limit -v

Flask's test client, GPT-2 mocked, a temporary audit log. Short texts are used
so most requests take the insufficient_evidence path — the limiter is what's
under test, not the signals.

Skipped when rate limiting is switched off (AI201_RATE_LIMITS=0).
"""

import shutil
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import audit
import config
import detector

import app as service

SHORT = "Just a short note. Not enough to score."           # insufficient_evidence
LIMIT = config.RATE_LIMIT_PER_MINUTE


@unittest.skipUnless(config.RATE_LIMITING_ENABLED, "rate limiting is off (AI201_RATE_LIMITS=0)")
class RateLimitTestCase(unittest.TestCase):

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
        self.model = mock.patch.object(detector, "model_signal", return_value=0.6).start()
        self.addCleanup(mock.patch.stopall)

        service.limiter.reset()
        self.addCleanup(service.limiter.reset)
        self.client = service.app.test_client()

    def submit(self, body, **kwargs):
        return self.client.post("/submit", json=body, **kwargs)

    def codes(self, bodies):
        return [self.submit(b).status_code for b in bodies]

    def rejections(self, reason=None):
        return [e for e in audit.read_entries() if e.get("event") == "rejected"
                and (reason is None or e["reason"] == reason)]

    def decisions(self):
        return [e for e in audit.read_entries() if "event" not in e]


class Configuration(RateLimitTestCase):
    def test_limits_are_the_documented_ones(self):
        self.assertTrue(config.RATE_LIMITING_ENABLED)
        self.assertEqual((config.RATE_LIMIT_PER_MINUTE, config.RATE_LIMIT_PER_DAY), (5, 100))
        self.assertEqual(service.SUBMIT_RATE_LIMIT, "5/minute;100/day")
        self.assertLess(config.RATE_LIMIT_PER_MINUTE, 15)    # so --flood 15 shows 429s

    def test_health_reports_rate_limiting(self):
        body = self.client.get("/health").get_json()
        self.assertIs(body["rate_limiting"], True)
        self.assertEqual(body["rate_limits"], "5/minute;100/day")


class PerMinuteLimit(RateLimitTestCase):
    def test_flood_of_15_from_one_creator(self):
        # What run_attacks.py --flood 15 does, in miniature: one creator_id.
        codes = self.codes([{"text": SHORT, "creator_id": "flood_tester"}] * 15)
        self.assertEqual(codes, [200] * LIMIT + [429] * (15 - LIMIT))

    def test_429_response_shape(self):
        for _ in range(LIMIT):
            self.submit({"text": SHORT, "creator_id": "w1"})
        r = self.submit({"text": SHORT, "creator_id": "w1"})
        self.assertEqual(r.status_code, 429)
        body = r.get_json()
        self.assertEqual(body["error"], "rate_limited")
        self.assertIn("5 per 1 minute", body["limit"])
        for field in ("content_id", "guess", "label", "model_score", "style_score"):
            self.assertNotIn(field, body)

    def test_limited_request_never_reaches_the_route(self):
        long_text = ("I started keeping a notebook last spring because my memory for small "
                     "things was going. At first it was only lists, groceries and phone "
                     "numbers. Then it turned into something else, a place where I argued "
                     "with myself about books I had not finished. Some pages are just one "
                     "sentence. Others run on for three pages about a bus driver who sang.")
        codes = self.codes([{"text": long_text, "creator_id": "w2"}] * (LIMIT + 2))
        self.assertEqual(codes, [200] * LIMIT + [429, 429])
        self.assertEqual(self.model.call_count, LIMIT)        # no scoring for a 429
        self.assertEqual(len(self.decisions()), LIMIT)        # no decision for a 429

    def test_invalid_requests_count_too(self):
        # Junk still uses up the allowance — a script can't probe for free.
        bodies = [{"text": "", "creator_id": "w3"}] * LIMIT + [{"text": SHORT, "creator_id": "w3"}]
        self.assertEqual(self.codes(bodies), [400] * LIMIT + [429])


class WhoCounts(RateLimitTestCase):
    def test_each_creator_id_has_its_own_allowance(self):
        for _ in range(LIMIT):
            self.submit({"text": SHORT, "creator_id": "busy"})
        self.assertEqual(self.submit({"text": SHORT, "creator_id": "busy"}).status_code, 429)
        self.assertEqual(self.submit({"text": SHORT, "creator_id": "quiet"}).status_code, 200)

    def test_rotating_creator_ids_is_not_limited(self):
        # The known weakness: one caller, many creator_ids, never limited.
        codes = self.codes([{"text": SHORT, "creator_id": f"sock_{i}"} for i in range(LIMIT * 3)])
        self.assertEqual(set(codes), {200})

    def test_no_creator_id_falls_back_to_the_address(self):
        # Missing, blank or non-string creator_id, non-object and non-JSON
        # bodies all count against the caller's address (127.0.0.1 here).
        bodies = [{"text": SHORT}, {"text": SHORT, "creator_id": ""},
                  {"text": SHORT, "creator_id": 7}, ["not", "an", "object"], None]
        codes = []
        for body in bodies:
            if body is None:
                codes.append(self.client.post("/submit", data="not json",
                                              content_type="application/json").status_code)
            else:
                codes.append(self.submit(body).status_code)
        self.assertEqual(codes, [400] * LIMIT)                # all refused, none crashed
        self.assertEqual(self.submit({"text": SHORT}).status_code, 429)
        self.assertEqual(self.submit({"text": SHORT, "creator_id": "named"}).status_code, 200)

    def test_different_addresses_have_separate_allowances(self):
        for _ in range(LIMIT):
            self.submit({"text": SHORT}, environ_base={"REMOTE_ADDR": "10.0.0.1"})
        self.assertEqual(self.submit({"text": SHORT}, environ_base={"REMOTE_ADDR": "10.0.0.1"})
                         .status_code, 429)
        self.assertEqual(self.submit({"text": SHORT}, environ_base={"REMOTE_ADDR": "10.0.0.2"})
                         .status_code, 400)               # reached the route: no creator_id

    def test_appeal_is_not_rate_limited(self):
        for _ in range(LIMIT + 3):
            r = self.client.post("/appeal", json={"content_id": "no-such-id", "reasoning": "x",
                                                  "creator_id": "w4"})
            self.assertEqual(r.status_code, 404)


class RejectionLogging(RateLimitTestCase):
    def test_every_429_is_logged(self):
        self.codes([{"text": SHORT, "creator_id": "flood_tester"}] * 15)
        limited = self.rejections("rate_limited")
        self.assertEqual(len(limited), 15 - LIMIT)
        for entry in limited:
            self.assertEqual(entry["event"], "rejected")
            self.assertEqual(entry["status"], "rejected")
            self.assertEqual(entry["creator_id"], "flood_tester")
            self.assertEqual(entry["http_status"], 429)
            self.assertEqual(entry["endpoint"], "/submit")
            self.assertIn("5 per 1 minute", entry["limit"])
            self.assertNotIn("content_id", entry)
            self.assertNotIn("text", entry)

    def test_unusable_creator_id_logged_as_unknown(self):
        for _ in range(LIMIT + 1):
            self.submit({"text": SHORT, "creator_id": 7})
        [entry] = self.rejections("rate_limited")
        self.assertEqual(entry["creator_id"], "unknown")

    def test_invalid_submissions_still_logged_alongside_429s(self):
        self.codes([{"text": "", "creator_id": "w5"}] * LIMIT + [{"text": "", "creator_id": "w5"}])
        self.assertEqual(len(self.rejections("invalid_input")), LIMIT)
        self.assertEqual(len(self.rejections("rate_limited")), 1)

    def test_allowed_decisions_keep_all_nine_fields(self):
        self.codes([{"text": SHORT, "creator_id": "w6"}] * (LIMIT + 1))
        nine = ["timestamp", "content_id", "creator_id", "guess", "model_score",
                "style_score", "combined_score", "label", "status"]
        decisions = self.decisions()
        self.assertEqual(len(decisions), LIMIT)
        for d in decisions:
            for field in nine:
                self.assertIn(field, d)

    def test_real_audit_log_is_unchanged(self):
        self.codes([{"text": SHORT, "creator_id": "flood_tester"}] * 8)
        now = self.real_log.read_bytes() if self.real_log.exists() else None
        self.assertEqual(now, self.real_log_bytes)


if __name__ == "__main__":
    unittest.main()
