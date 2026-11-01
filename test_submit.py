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

    def test_placeholders_untouched(self):
        body = self.submit({"text": LONG, "creator_id": "it_long"}).get_json()
        self.assertEqual(body["guess"], "unsure")
        self.assertEqual(body["confidence"], 0.0)
        self.assertTrue(body["label"].startswith("PLACEHOLDER"))

    def test_audit_record_matches_response(self):
        body = self.submit({"text": LONG, "creator_id": "it_long"}).get_json()
        records = [e for e in self.decisions() if e["content_id"] == body["content_id"]]
        self.assertEqual(len(records), 1)
        record = records[0]

        for field in NINE_FIELDS:
            self.assertIn(field, record)
        for field in ["content_id", "creator_id", "guess", "model_score",
                      "style_score", "combined_score", "label", "status"]:
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


class MinimumSentences(SubmitTestCase):
    """
    The short-text check counts sentences with stylometry.sentences, so the
    splitter fixes change which submissions get scored at all.
    """

    # 70 words, but only 2 real sentences — the starter splitter counted 6.
    TWO_SENTENCES_WITH_TITLES = (
        "Yesterday Mr. Okafor and Dr. Lee walked slowly along the river path near "
        "the old mill, talking about the flood that had ruined the bakery, the "
        "school, and most of the houses on the low side of town last spring. Later "
        "Mrs. Patel and Prof. Ruiz joined them for tea at the small cafe by the "
        "bridge and stayed there until the lights came on across the water."
    )

    def test_missing_spaces_cannot_dodge_scoring(self):
        # Deleting the spaces after full stops used to make LONG one "sentence",
        # so it got insufficient_evidence and was never scored.
        squashed = LONG.replace(". ", ".")
        self.assertGreaterEqual(len(stylometry.sentences(squashed)), config.MIN_SENTENCES_TO_ASSESS)

        body = self.submit({"text": squashed, "creator_id": "it_squashed"}).get_json()
        self.assertNotEqual(body["guess"], "insufficient_evidence")
        self.model.assert_called_once_with(squashed)
        self.assertIsNotNone(body["style_score"])

    def test_abbreviations_do_not_count_as_extra_sentences(self):
        text = self.TWO_SENTENCES_WITH_TITLES
        self.assertGreaterEqual(len(stylometry.words(text)), config.MIN_WORDS_TO_ASSESS)
        self.assertEqual(len(stylometry.sentences(text)), 2)

        body = self.submit({"text": text, "creator_id": "it_titles"}).get_json()
        self.assertEqual(body["guess"], "insufficient_evidence")
        self.model.assert_not_called()
        self.style.assert_not_called()
        self.combine.assert_not_called()

    def test_three_real_sentences_are_scored(self):
        text = self.TWO_SENTENCES_WITH_TITLES + " Nobody mentioned the flood again."
        self.assertEqual(len(stylometry.sentences(text)), 3)
        body = self.submit({"text": text, "creator_id": "it_three"}).get_json()
        self.assertNotEqual(body["guess"], "insufficient_evidence")
        self.model.assert_called_once()


class RealLogUntouched(SubmitTestCase):
    def test_real_audit_log_is_unchanged(self):
        self.submit({"text": LONG, "creator_id": "it_guard"})
        now = self.real_log.read_bytes() if self.real_log.exists() else None
        self.assertEqual(now, self.real_log_bytes)


if __name__ == "__main__":
    unittest.main()
