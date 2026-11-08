"""
Integration tests for POST /submit, with the GPT-2 detector mocked.

    python -m unittest test_submit -v

No model loads and no server runs: Flask's test client calls the route
directly. Every test writes to a temporary audit log, so nothing here ever
touches logs/audit.jsonl — and the last check makes sure of it.
"""

import shutil
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import audit
import config
import detector
import scoring
import stylometry

import app as service

MOCK_MODEL_SCORE = 0.6123

# 85 words, 6 sentences — long enough to be scored.
LONG = (
    "I started keeping a notebook last spring because my memory for small things "
    "was going. At first it was only lists, groceries and phone numbers and the "
    "names of my neighbour's dogs. Then it turned into something else, a place "
    "where I argued with myself about books I had not finished. Some pages are "
    "just one sentence. Others run on for three pages about a bus driver who "
    "sang. I do not reread it often, but when I do I barely recognise the person "
    "writing."
)
SHORT = "The fog comes on little cat feet. It sits looking over harbor and city. Then moves on."

NINE_FIELDS = ["timestamp", "content_id", "creator_id", "guess", "model_score",
               "style_score", "combined_score", "label", "status"]


class SubmitTestCase(unittest.TestCase):
    """Temporary audit log, a test client, and both signals spied on."""

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

        self.model = mock.patch.object(detector, "model_signal",
                                       return_value=MOCK_MODEL_SCORE).start()
        self.style = mock.patch.object(stylometry, "style_signal",
                                       wraps=stylometry.style_signal).start()
        self.combine = mock.patch.object(scoring, "combine_signals",
                                         wraps=scoring.combine_signals).start()
        self.addCleanup(mock.patch.stopall)

        self.client = service.app.test_client()
        # Rate-limit counts live in memory for the whole run; start each test fresh.
        getattr(service.limiter, "reset", lambda: None)()

    def submit(self, body=None, **kwargs):
        return self.client.post("/submit", json=body, **kwargs)

    def decisions(self):
        return [e for e in audit.read_entries() if "event" not in e]


class ScoredSubmission(SubmitTestCase):
    def test_response_carries_both_real_signals(self):
        r = self.submit({"text": LONG, "creator_id": "it_long"})
        self.assertEqual(r.status_code, 200)
        body = r.get_json()

        # Check the route's calls first — computing the expected value below
        # goes through the same spy.
        self.model.assert_called_once_with(LONG)
        self.style.assert_called_once_with(LONG)

        self.assertEqual(body["model_score"], MOCK_MODEL_SCORE)
        self.assertEqual(body["style_score"], stylometry.style_signal(LONG))
        self.assertNotEqual(body["style_score"], 0.5)        # no longer the placeholder

    def test_combined_score_comes_from_both_signals(self):
        body = self.submit({"text": LONG, "creator_id": "it_long"}).get_json()
        self.combine.assert_called_once_with(MOCK_MODEL_SCORE, body["style_score"])
        expected = round((config.WEIGHT_MODEL_SIGNAL * MOCK_MODEL_SCORE
                          + config.WEIGHT_STYLE_SIGNAL * body["style_score"])
                         / (config.WEIGHT_MODEL_SIGNAL + config.WEIGHT_STYLE_SIGNAL), 4)
        self.assertEqual(body["combined_score"], expected)
        self.assertNotEqual(body["combined_score"], 0.5)     # no longer the placeholder

    def test_label_and_confidence_come_from_combined_score(self):
        # Mocked model 0.6123 + real style 0.3737 -> combined 0.493 -> unsure, 0.01
        body = self.submit({"text": LONG, "creator_id": "it_long"}).get_json()
        self.assertEqual(body["combined_score"], 0.493)
        self.assertEqual((body["guess"], body["label"]),
                         scoring.score_to_label(body["combined_score"]))
        self.assertEqual(body["guess"], "unsure")
        self.assertEqual(body["label"], scoring.LABEL_UNSURE)
        self.assertEqual(body["confidence"], 0.01)
        self.assertNotIn("PLACEHOLDER", body["label"])

    def test_audit_record_matches_response(self):
        body = self.submit({"text": LONG, "creator_id": "it_long"}).get_json()
        records = [e for e in self.decisions() if e["content_id"] == body["content_id"]]
        self.assertEqual(len(records), 1)
        record = records[0]

        for field in NINE_FIELDS:
            self.assertIn(field, record)
        for field in ["content_id", "creator_id", "guess", "model_score",
                      "style_score", "combined_score", "label", "status", "confidence"]:
            self.assertEqual(record[field], body[field], field)
        self.assertEqual(record["text_length"], len(LONG))
        self.assertNotIn("text", record)

    def test_each_submission_gets_its_own_id(self):
        a = self.submit({"text": LONG, "creator_id": "it_a"}).get_json()["content_id"]
        b = self.submit({"text": LONG, "creator_id": "it_b"}).get_json()["content_id"]
        self.assertNotEqual(a, b)
        self.assertEqual(len(self.decisions()), 2)


class ShortText(SubmitTestCase):
    def test_short_text_calls_neither_signal(self):
        r = self.submit({"text": SHORT, "creator_id": "it_short"})
        self.assertEqual(r.status_code, 200)
        body = r.get_json()

        self.model.assert_not_called()
        self.style.assert_not_called()
        self.combine.assert_not_called()
        self.assertEqual(body["guess"], "insufficient_evidence")
        for field in ["model_score", "style_score", "combined_score", "confidence"]:
            self.assertIsNone(body[field], field)

        [record] = self.decisions()
        self.assertEqual(record["content_id"], body["content_id"])
        self.assertEqual(record["guess"], "insufficient_evidence")
        self.assertIsNone(record["style_score"])
        self.assertIsNone(record["confidence"])
        self.assertEqual(record["label"], body["label"])
        self.assertNotIn(body["label"], (scoring.LABEL_HUMAN, scoring.LABEL_UNSURE,
                                         scoring.LABEL_AI))


class InvalidInput(SubmitTestCase):
    CASES = [
        ({"creator_id": "it_bad"}, 400),
        ({"text": None, "creator_id": "it_bad"}, 400),
        ({"text": 42, "creator_id": "it_bad"}, 400),
        ({"text": "   ", "creator_id": "it_bad"}, 400),
        ({"text": LONG}, 400),
        ({"text": LONG, "creator_id": ""}, 400),
        (["not", "an", "object"], 400),
        ({"text": "x" * (config.MAX_TEXT_CHARS + 1), "creator_id": "it_bad"}, 413),
    ]

    def test_invalid_input_calls_neither_signal(self):
        for body, status in self.CASES:
            with self.subTest(body=str(body)[:40]):
                self.assertEqual(self.submit(body).status_code, status)
        r = self.client.post("/submit", data="not json", content_type="application/json")
        self.assertEqual(r.status_code, 400)

        self.model.assert_not_called()
        self.style.assert_not_called()
        self.combine.assert_not_called()
        self.assertEqual(self.decisions(), [])
        self.assertEqual(len(audit.read_entries()), len(self.CASES) + 1)   # one rejection each


class DetectorFailure(SubmitTestCase):
    def test_failure_is_a_503_with_no_decision_and_no_score(self):
        self.model.side_effect = detector.DetectorUnavailable("simulated")
        r = self.submit({"text": LONG, "creator_id": "it_fail"})

        self.assertEqual(r.status_code, 503)
        body = r.get_json()
        self.assertEqual(body["error"], "detector_unavailable")
        for field in ["content_id", "guess", "label", "model_score", "style_score",
                      "combined_score", "confidence"]:
            self.assertNotIn(field, body)

        self.style.assert_not_called()
        self.combine.assert_not_called()
        self.assertEqual(self.decisions(), [])
        [rejection] = audit.read_entries()
        self.assertEqual(rejection["reason"], "detector_unavailable")


class ShortTextGate(SubmitTestCase):
    """
    "Too short to assess" is decided by word count alone (Unit 8, Milestone 5).

    It used to be "fewer than 50 words OR fewer than 3 sentences". Attack EV07
    showed the sentence half let a long text skip scoring by joining its
    sentences with semicolons, so it was removed.
    """

    # 70 words, 2 sentences (the abbreviations don't count as extra ones).
    TWO_SENTENCES_WITH_TITLES = (
        "Yesterday Mr. Okafor and Dr. Lee walked slowly along the river path near "
        "the old mill, talking about the flood that had ruined the bakery, the "
        "school, and most of the houses on the low side of town last spring. Later "
        "Mrs. Patel and Prof. Ruiz joined them for tea at the small cafe by the "
        "bridge and stayed there until the lights came on across the water."
    )

    def assert_scored(self, text, creator_id):
        body = self.submit({"text": text, "creator_id": creator_id}).get_json()
        self.assertNotEqual(body["guess"], "insufficient_evidence")
        self.model.assert_called_once_with(text)
        self.assertIsNotNone(body["combined_score"])
        return body

    def assert_not_scored(self, text, creator_id):
        body = self.submit({"text": text, "creator_id": creator_id}).get_json()
        self.assertEqual(body["guess"], "insufficient_evidence")
        self.model.assert_not_called()
        self.style.assert_not_called()
        return body

    def test_semicolon_joined_long_text_is_scored(self):
        # The EV07 pattern: every full stop but the last swapped for a semicolon.
        joined = LONG.replace(". ", "; ")
        self.assertEqual(len(stylometry.sentences(joined)), 1)
        self.assertGreaterEqual(len(stylometry.words(joined)), config.MIN_WORDS_TO_ASSESS)
        body = self.assert_scored(joined, "it_semicolons")
        self.assertIsNotNone(body["style_score"])

    def test_long_text_with_two_sentences_is_scored(self):
        text = self.TWO_SENTENCES_WITH_TITLES
        self.assertEqual(len(stylometry.sentences(text)), 2)   # abbreviations don't split
        self.assert_scored(text, "it_titles")

    def test_missing_spaces_still_cannot_dodge_scoring(self):
        squashed = LONG.replace(". ", ".")
        self.assertGreaterEqual(len(stylometry.sentences(squashed)), 3)
        self.assert_scored(squashed, "it_squashed")

    def test_word_count_boundary(self):
        self.assertEqual(config.MIN_WORDS_TO_ASSESS, 50)
        self.assertFalse(hasattr(config, "MIN_SENTENCES_TO_ASSESS"))
        words49 = " ".join(["Word"] * 48) + " end."
        words50 = " ".join(["Word"] * 49) + " end."
        self.assertEqual(len(stylometry.words(words49)), 49)
        self.assertEqual(len(stylometry.words(words50)), 50)
        self.assert_not_scored(words49, "it_49")
        self.model.reset_mock()
        self.style.reset_mock()
        self.assert_scored(words50, "it_50")

    def test_short_text_with_many_sentences_still_not_scored(self):
        # Under 50 words stays "too short", however many sentences it has.
        short = "Went for a run. Legs hurt. Worth it. Will go again. Maybe."
        self.assertGreater(len(stylometry.sentences(short)), 3)
        self.assert_not_scored(short, "it_short_many")


class Classification(SubmitTestCase):
    """
    guess, label and confidence through the real route, with BOTH signals
    pinned (model mocked, style forced to 0.4) so each combined score is
    exact: combined = (model + 0.4) / 2.
    """

    STYLE = 0.4

    def setUp(self):
        super().setUp()
        self.style.return_value = self.STYLE     # an explicit return_value overrides wraps

    def submit_with_model(self, model_score, creator_id="it_band"):
        self.model.return_value = model_score
        return self.submit({"text": LONG, "creator_id": creator_id}).get_json()

    def assert_decision(self, body, guess, label, combined, confidence):
        self.assertEqual(body["combined_score"], combined)
        self.assertEqual(body["guess"], guess)
        self.assertEqual(body["label"], label)
        self.assertEqual(body["confidence"], confidence)
        self.assertEqual(body["style_score"], self.STYLE)

    def test_human(self):
        body = self.submit_with_model(0.10)            # (0.10 + 0.4) / 2 = 0.25
        self.assert_decision(body, "human", scoring.LABEL_HUMAN, 0.25, 0.5)

    def test_unsure(self):
        body = self.submit_with_model(0.60)            # 0.50
        self.assert_decision(body, "unsure", scoring.LABEL_UNSURE, 0.5, 0.0)

    def test_ai(self):
        body = self.submit_with_model(1.00)            # 0.70
        self.assert_decision(body, "ai", scoring.LABEL_AI, 0.7, 0.4)

    def test_exact_boundaries_are_unsure(self):
        low = self.submit_with_model(0.30, "it_low")   # exactly 0.35
        high = self.submit_with_model(0.90, "it_high") # exactly 0.65
        self.assert_decision(low, "unsure", scoring.LABEL_UNSURE, 0.35, 0.3)
        self.assert_decision(high, "unsure", scoring.LABEL_UNSURE, 0.65, 0.3)

    def test_just_past_each_boundary(self):
        human = self.submit_with_model(0.2998, "it_h")  # 0.3499
        ai = self.submit_with_model(0.9002, "it_a")     # 0.6501
        self.assert_decision(human, "human", scoring.LABEL_HUMAN, 0.3499, 0.3)
        self.assert_decision(ai, "ai", scoring.LABEL_AI, 0.6501, 0.3)

    def test_confidence_is_rounded_to_two_places(self):
        body = self.submit_with_model(0.9246)           # 0.6623 -> |0.1623| * 2 = 0.3246
        self.assertEqual(body["combined_score"], 0.6623)
        self.assertEqual(body["confidence"], 0.32)

    def test_every_band_logged_exactly_as_returned(self):
        bodies = [self.submit_with_model(m, f"it_{m}") for m in (0.10, 0.30, 0.60, 0.90, 1.00)]
        records = {e["content_id"]: e for e in self.decisions()}
        self.assertEqual(len(records), 5)
        for body in bodies:
            record = records[body["content_id"]]
            for field in ("guess", "label", "confidence", "combined_score",
                          "model_score", "style_score", "creator_id", "status"):
                self.assertEqual(record[field], body[field], field)


class RealLogUntouched(SubmitTestCase):
    def test_real_audit_log_is_unchanged(self):
        self.submit({"text": LONG, "creator_id": "it_guard"})
        now = self.real_log.read_bytes() if self.real_log.exists() else None
        self.assertEqual(now, self.real_log_bytes)


if __name__ == "__main__":
    unittest.main()
