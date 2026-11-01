"""
Focused tests for scoring.combine_signals.

    python -m unittest test_scoring -v

Pure arithmetic — no model, no server, no log.
"""

import math
import unittest
from unittest import mock

import config
from scoring import (LABEL_AI, LABEL_HUMAN, LABEL_UNSURE, combine_signals, confidence,
                     score_to_label)


def weights(model, style):
    return mock.patch.multiple(config, WEIGHT_MODEL_SIGNAL=model, WEIGHT_STYLE_SIGNAL=style)


class Arithmetic(unittest.TestCase):
    def test_configured_weights_are_unchanged(self):
        self.assertEqual((config.WEIGHT_MODEL_SIGNAL, config.WEIGHT_STYLE_SIGNAL), (0.5, 0.5))

    def test_step2_example(self):
        # 0.5 * 0.6123 + 0.5 * 0.3737 = 0.4930
        self.assertEqual(combine_signals(0.6123, 0.3737), 0.493)

    def test_unequal_weights(self):
        with weights(0.75, 0.25):
            # 0.75 * 0.8 + 0.25 * 0.4 = 0.7
            self.assertEqual(combine_signals(0.8, 0.4), 0.7)

    def test_weights_are_normalised(self):
        # Only the ratio matters: (2, 2) == (0.5, 0.5), (3, 1) == (0.75, 0.25)
        with weights(2, 2):
            self.assertEqual(combine_signals(0.6123, 0.3737), 0.493)
        with weights(3, 1):
            self.assertEqual(combine_signals(0.8, 0.4), 0.7)

    def test_one_zero_weight_uses_the_other_signal_alone(self):
        with weights(1, 0):
            self.assertEqual(combine_signals(0.8, 0.1), 0.8)
        with weights(0, 1):
            self.assertEqual(combine_signals(0.8, 0.1), 0.1)

    def test_disagreement_lands_between(self):
        self.assertEqual(combine_signals(0.9, 0.1), 0.5)


class Boundaries(unittest.TestCase):
    def test_corners(self):
        self.assertEqual(combine_signals(0.0, 0.0), 0.0)
        self.assertEqual(combine_signals(1.0, 1.0), 1.0)
        self.assertEqual(combine_signals(0.0, 1.0), 0.5)
        self.assertEqual(combine_signals(1.0, 0.0), 0.5)

    def test_integers_0_and_1_are_accepted(self):
        self.assertEqual(combine_signals(0, 1), 0.5)

    def test_result_stays_in_range_and_between_inputs(self):
        steps = [i / 10 for i in range(11)]
        for m in steps:
            for s in steps:
                with self.subTest(m=m, s=s):
                    c = combine_signals(m, s)
                    self.assertIsInstance(c, float)
                    self.assertGreaterEqual(c, 0.0)
                    self.assertLessEqual(c, 1.0)
                    self.assertGreaterEqual(c, round(min(m, s), 4))
                    self.assertLessEqual(c, round(max(m, s), 4))


class InvalidInputs(unittest.TestCase):
    def test_out_of_range_and_non_finite_are_refused(self):
        for bad in (-0.0001, 1.0001, -1, 2, math.nan, math.inf, -math.inf):
            for args in ((bad, 0.5), (0.5, bad)):
                with self.subTest(args=args):
                    with self.assertRaises(ValueError):
                        combine_signals(*args)

    def test_non_numbers_are_refused(self):
        for bad in (None, "0.5", True, False, [0.5]):
            for args in ((bad, 0.5), (0.5, bad)):
                with self.subTest(args=args):
                    with self.assertRaises(TypeError):
                        combine_signals(*args)


class InvalidWeights(unittest.TestCase):
    def test_broken_weights_are_refused(self):
        for model_w, style_w in [(-0.5, 0.5), (0.5, -0.1), (math.nan, 0.5), (0.5, math.inf),
                                 (0, 0), (0.0, 0.0), ("0.5", 0.5), (None, 0.5), (True, 0.5)]:
            with self.subTest(weights=(model_w, style_w)):
                with weights(model_w, style_w):
                    with self.assertRaises(ValueError):
                        combine_signals(0.5, 0.5)


class Deterministic(unittest.TestCase):
    def test_same_inputs_same_result(self):
        results = {combine_signals(0.6123, 0.3737) for _ in range(100)}
        self.assertEqual(results, {0.493})


class Labels(unittest.TestCase):
    """score_to_label: three bands, both thresholds belong to "unsure"."""

    def test_thresholds_are_unchanged(self):
        self.assertEqual((config.HUMAN_THRESHOLD, config.AI_THRESHOLD), (0.35, 0.65))

    def test_exact_label_texts(self):
        self.assertEqual(LABEL_HUMAN,
                         "This text shows patterns more consistent with human writing. "
                         "This is an automated estimate, not proof of authorship.")
        self.assertEqual(LABEL_UNSURE,
                         "The available signals do not support a reliable classification. "
                         "No conclusion about authorship should be drawn from this result.")
        self.assertEqual(LABEL_AI,
                         "This text shows patterns associated with AI-generated writing. "
                         "This result is not proof of AI use, and you can request a human "
                         "review if you disagree.")

    def test_each_band(self):
        self.assertEqual(score_to_label(0.10), ("human", LABEL_HUMAN))
        self.assertEqual(score_to_label(0.50), ("unsure", LABEL_UNSURE))
        self.assertEqual(score_to_label(0.90), ("ai", LABEL_AI))

    def test_both_thresholds_are_unsure(self):
        self.assertEqual(score_to_label(0.35), ("unsure", LABEL_UNSURE))
        self.assertEqual(score_to_label(0.65), ("unsure", LABEL_UNSURE))
        self.assertEqual(score_to_label(config.HUMAN_THRESHOLD)[0], "unsure")
        self.assertEqual(score_to_label(config.AI_THRESHOLD)[0], "unsure")

    def test_just_either_side_of_each_threshold(self):
        self.assertEqual(score_to_label(0.3499)[0], "human")
        self.assertEqual(score_to_label(0.3501)[0], "unsure")
        self.assertEqual(score_to_label(0.6499)[0], "unsure")
        self.assertEqual(score_to_label(0.6501)[0], "ai")

    def test_ends_of_the_scale(self):
        self.assertEqual(score_to_label(0.0)[0], "human")
        self.assertEqual(score_to_label(1.0)[0], "ai")
        self.assertEqual(score_to_label(0)[0], "human")       # int accepted, like combine_signals
        self.assertEqual(score_to_label(1)[0], "ai")

    def test_all_three_reachable_and_no_gaps(self):
        # Every 0.0001 step from 0 to 1 gets a label, and all three appear.
        guesses = {score_to_label(i / 10000)[0] for i in range(10001)}
        self.assertEqual(guesses, {"human", "unsure", "ai"})

    def test_thresholds_read_from_config(self):
        with mock.patch.multiple(config, HUMAN_THRESHOLD=0.2, AI_THRESHOLD=0.8):
            self.assertEqual(score_to_label(0.3)[0], "unsure")
            self.assertEqual(score_to_label(0.7)[0], "unsure")
            self.assertEqual(score_to_label(0.2)[0], "unsure")
            self.assertEqual(score_to_label(0.19)[0], "human")
            self.assertEqual(score_to_label(0.81)[0], "ai")

    def test_combined_examples(self):
        # The real-GPT-2 calibration examples from Milestone 4 (AI-written),
        # labelled — mechanics only, not evidence of accuracy.
        self.assertEqual(score_to_label(combine_signals(0.5046, 0.2369))[0], "unsure")  # 0.3708
        self.assertEqual(score_to_label(combine_signals(0.4798, 0.3737))[0], "unsure")  # 0.4267

    def test_invalid_scores_refused_like_combine_signals(self):
        for bad in (-0.0001, 1.0001, -1, 2, math.nan, math.inf, -math.inf):
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError):
                    score_to_label(bad)
                with self.assertRaises(ValueError):
                    combine_signals(bad, 0.5)
        for bad in (None, "0.5", True, False, [0.5]):
            with self.subTest(bad=bad):
                with self.assertRaises(TypeError):
                    score_to_label(bad)
                with self.assertRaises(TypeError):
                    combine_signals(bad, 0.5)

    def test_deterministic(self):
        for score in (0.0, 0.35, 0.5, 0.65, 1.0):
            with self.subTest(score=score):
                self.assertEqual({score_to_label(score) for _ in range(50)},
                                 {score_to_label(score)})

    def test_label_text_is_never_a_placeholder(self):
        for score in (0.1, 0.5, 0.9):
            self.assertNotIn("PLACEHOLDER", score_to_label(score)[1])


class Confidence(unittest.TestCase):
    """confidence = round(abs(combined - 0.5) * 2, 2) — uncalibrated, not a probability."""

    def test_midpoint_is_zero(self):
        self.assertEqual(confidence(0.5), 0.0)

    def test_ends_are_one(self):
        self.assertEqual(confidence(0.0), 1.0)
        self.assertEqual(confidence(1.0), 1.0)
        self.assertEqual(confidence(0), 1.0)
        self.assertEqual(confidence(1), 1.0)

    def test_quarter_points(self):
        self.assertEqual(confidence(0.25), 0.5)
        self.assertEqual(confidence(0.75), 0.5)

    def test_thresholds(self):
        # abs(0.35 - 0.5) * 2 is 0.30000000000000004 in floats; rounding gives 0.3
        self.assertAlmostEqual(confidence(0.35), 0.3)
        self.assertAlmostEqual(confidence(0.65), 0.3)
        self.assertEqual(confidence(config.HUMAN_THRESHOLD), 0.3)
        self.assertEqual(confidence(config.AI_THRESHOLD), 0.3)

    def test_rounded_to_two_places(self):
        self.assertEqual(confidence(0.493), 0.01)       # the Milestone 4 mocked example
        self.assertEqual(confidence(0.3708), 0.26)      # real-GPT-2 flooding example
        self.assertEqual(confidence(0.9123), 0.82)

    def test_symmetric_around_half(self):
        for i in range(101):
            x = i / 100
            with self.subTest(x=x):
                self.assertEqual(confidence(x), confidence(round(1 - x, 2)))

    def test_always_between_zero_and_one(self):
        for i in range(10001):
            c = confidence(i / 10000)
            self.assertIsInstance(c, float)
            self.assertGreaterEqual(c, 0.0)
            self.assertLessEqual(c, 1.0)

    def test_never_above_point_three_inside_unsure_band(self):
        for i in range(3500, 6501):
            self.assertLessEqual(confidence(i / 10000), 0.3)

    def test_invalid_inputs_refused_like_the_others(self):
        for bad in (-0.0001, 1.0001, -1, 2, math.nan, math.inf, -math.inf):
            with self.subTest(bad=bad):
                for fn in (confidence, score_to_label, lambda v: combine_signals(v, 0.5)):
                    with self.assertRaises(ValueError):
                        fn(bad)
        for bad in (None, "0.5", True, False, [0.5]):
            with self.subTest(bad=bad):
                for fn in (confidence, score_to_label, lambda v: combine_signals(v, 0.5)):
                    with self.assertRaises(TypeError):
                        fn(bad)

    def test_deterministic(self):
        for score in (0.0, 0.35, 0.493, 0.65, 1.0):
            with self.subTest(score=score):
                self.assertEqual({confidence(score) for _ in range(50)}, {confidence(score)})


if __name__ == "__main__":
    unittest.main()
