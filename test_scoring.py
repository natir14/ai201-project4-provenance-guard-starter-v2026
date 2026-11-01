"""
Focused tests for scoring.combine_signals.

    python -m unittest test_scoring -v

Pure arithmetic — no model, no server, no log.
"""

import math
import unittest
from unittest import mock

import config
from scoring import combine_signals


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


if __name__ == "__main__":
    unittest.main()
