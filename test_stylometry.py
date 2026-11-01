"""
Focused tests for signal two, the style signal.

    python -m unittest test_stylometry -v

No model, no server — these run in a second. They check the arithmetic and
the edge cases, not whether the signal is any good at telling human from AI;
that's what the Milestone 4 calibration inputs are for.
"""

import math
import unittest
from unittest import mock

import config
import stylometry as s

# Three sentences of exactly six words, no inner punctuation, 18 words.
UNIFORM = "The cat sat on the mat. The dog sat on the rug. The cow sat on the hay."

VARIED = (
    "Rain. The gutters on our street, which nobody has cleaned since March, "
    "overflowed again last night; Mrs. Patel's cellar took the worst of it. "
    "She called the council (twice) and got the same answer: \"We're aware.\" "
    "Honestly? I laughed — what else is there to do when the water keeps coming "
    "and the people paid to stop it keep writing letters about leaves instead."
)


class SentenceLengthSpread(unittest.TestCase):
    def test_empty_and_one_sentence_are_undefined(self):
        self.assertIsNone(s.sentence_length_spread(""))
        self.assertIsNone(s.sentence_length_spread("   \n\t "))
        self.assertIsNone(s.sentence_length_spread("Just one sentence here."))

    def test_punctuation_only_sentences_are_ignored(self):
        # "!!!" splits off as a "sentence" with no words; it mustn't count.
        self.assertIsNone(s.sentence_length_spread("Only this one. !!!"))

    def test_equal_lengths_have_zero_spread(self):
        self.assertEqual(s.sentence_length_spread(UNIFORM), 0.0)

    def test_known_value(self):
        # 2 and 6 words: mean 4, sample stdev sqrt(8) -> CV 0.7071
        self.assertAlmostEqual(
            s.sentence_length_spread("Go now. I will see you after it."),
            round(math.sqrt(8) / 4, 4))


class TypeTokenRatio(unittest.TestCase):
    def test_below_window_is_undefined(self):
        self.assertIsNone(s.type_token_ratio(""))
        self.assertIsNone(s.type_token_ratio(" ".join(f"w{i}" for i in range(49))))

    def test_window_boundary(self):
        # Exactly one window of 50 distinct words -> 1.0
        self.assertEqual(s.type_token_ratio(" ".join(f"w{i}" for i in range(50))), 1.0)

    def test_repeated_word(self):
        # 60 copies of one word: every window holds 1 unique of 50 -> 0.02
        self.assertEqual(s.type_token_ratio("the " * 60), 0.02)


class Punctuation(unittest.TestCase):
    def test_no_sentences_is_undefined(self):
        self.assertIsNone(s.punctuation_density(""))
        self.assertEqual(s.punctuation_kinds(""), 0)

    def test_terminal_punctuation_is_not_counted(self):
        text = "Really?! Yes!!! Well... fine. Wow…"
        self.assertEqual(s.punctuation_density(text), 0.0)
        self.assertEqual(s.punctuation_kinds(text), 0)

    def test_all_six_kinds(self):
        # , ; : — ( and two " marks = 7 marks, one sentence
        text = 'Well, yes; no: maybe — (fine) "ok".'
        self.assertEqual(s.punctuation_kinds(text), 6)
        self.assertEqual(s.punctuation_density(text), 7.0)

    def test_dash_spellings(self):
        for dash in ("—", "–", "--", " - "):
            with self.subTest(dash=dash):
                self.assertEqual(s.punctuation_kinds(f"This{dash}that."), 1)

    def test_hyphen_inside_a_word_is_not_a_dash(self):
        self.assertEqual(s.punctuation_kinds("A well-known fact."), 0)


class Scale(unittest.TestCase):
    def test_anchors_and_clamping(self):
        anchors = (0.2, 0.7)                     # low value = AI end
        self.assertEqual(s._scale(0.2, anchors), 1.0)
        self.assertEqual(s._scale(0.7, anchors), 0.0)
        self.assertAlmostEqual(s._scale(0.45, anchors), 0.5)
        self.assertEqual(s._scale(-5, anchors), 1.0)
        self.assertEqual(s._scale(99, anchors), 0.0)
        self.assertIsNone(s._scale(None, anchors))


class StyleSignal(unittest.TestCase):
    def test_empty_text_is_neutral(self):
        self.assertEqual(s.style_signal(""), 0.5)
        self.assertEqual(s.style_signal("   "), 0.5)

    def test_uniform_known_value(self):
        # spread 0 -> 1.0; 18 words -> vocabulary undefined -> 0.5;
        # punctuation 1.0 but weighted 0. So 0.5 * 1.0 + 0.5 * 0.5 = 0.75
        self.assertEqual(s.style_parts(UNIFORM),
                         {"spread": 1.0, "vocabulary": None, "punctuation": 1.0})
        self.assertEqual(s.style_signal(UNIFORM), 0.75)

    def test_direction(self):
        # Even, plain, repetitive text must score as more AI-like than lumpy,
        # punctuated, varied text — the direction DESIGN.md documents.
        self.assertGreater(s.style_signal(UNIFORM * 4), s.style_signal(VARIED))

    def test_always_bounded(self):
        cases = ["", "a", "the " * 500, "!!! ??? ...", "🙂 émoji, ünïcode; text.",
                 UNIFORM, VARIED, UNIFORM * 50, ",;:—()\"" * 100,
                 "word " * (config.MAX_TEXT_CHARS // 5)]
        for text in cases:
            with self.subTest(text=text[:30]):
                score = s.style_signal(text)
                self.assertIsInstance(score, float)
                self.assertGreaterEqual(score, 0.0)
                self.assertLessEqual(score, 1.0)

    def test_deterministic(self):
        self.assertEqual(s.style_signal(VARIED), s.style_signal(VARIED))
        self.assertEqual(s.style_parts(VARIED), s.style_parts(VARIED))
        self.assertEqual([s.style_signal(UNIFORM * 4) for _ in range(5)],
                         [s.style_signal(UNIFORM * 4)] * 5)


class Weighting(unittest.TestCase):
    """The provisional weights: spread 0.5, vocabulary 0.5, punctuation 0."""

    def test_configured_weights(self):
        self.assertEqual(config.STYLE_WEIGHT_SPREAD, 0.50)
        self.assertEqual(config.STYLE_WEIGHT_VOCABULARY, 0.50)
        self.assertEqual(config.STYLE_WEIGHT_PUNCTUATION, 0.00)

    def test_formula_on_text_with_every_part_defined(self):
        # VARIED is 63 words, 5 sentences: spread and vocabulary both defined
        parts = s.style_parts(VARIED)
        self.assertIsNotNone(parts["spread"])
        self.assertIsNotNone(parts["vocabulary"])
        self.assertEqual(s.style_signal(VARIED),
                         round(0.5 * parts["spread"] + 0.5 * parts["vocabulary"], 4))

    def test_punctuation_does_not_move_the_score(self):
        # Same words, same sentences, punctuation added inside them. The
        # punctuation part changes; the score must not.
        plain = UNIFORM * 4
        punctuated = plain.replace(" sat on ", ", sat; on ")
        self.assertEqual(s.words(plain), s.words(punctuated))
        self.assertEqual(len(s.sentences(plain)), len(s.sentences(punctuated)))
        self.assertNotEqual(s.style_parts(plain)["punctuation"],
                            s.style_parts(punctuated)["punctuation"])
        self.assertEqual(s.style_signal(plain), s.style_signal(punctuated))

    def test_weights_are_read_from_config(self):
        # Swap the weights and the formula must follow — proof the score
        # isn't hardcoded to 0.5 / 0.5.
        parts = s.style_parts(VARIED)
        with mock.patch.multiple(config, STYLE_WEIGHT_SPREAD=0.0,
                                 STYLE_WEIGHT_VOCABULARY=0.0,
                                 STYLE_WEIGHT_PUNCTUATION=1.0):
            self.assertEqual(s.style_signal(VARIED), parts["punctuation"])
        with mock.patch.multiple(config, STYLE_WEIGHT_SPREAD=0.0,
                                 STYLE_WEIGHT_VOCABULARY=0.0,
                                 STYLE_WEIGHT_PUNCTUATION=0.0):
            self.assertEqual(s.style_signal(VARIED), 0.5)    # no weight at all -> neutral


class NeutralHandling(unittest.TestCase):
    def test_both_parts_missing_is_neutral(self):
        # One sentence, under 50 words: no spread, no vocabulary
        self.assertEqual(s.style_parts("Just one sentence here.")["spread"], None)
        self.assertEqual(s.style_signal("Just one sentence here."), 0.5)

    def test_missing_vocabulary_counts_as_half(self):
        text = "Go now. I will see you after it."         # raw CV 0.7071, 8 words
        spread = s.style_parts(text)["spread"]
        self.assertEqual(spread, 0.0)                     # CV above 0.70 -> human end
        self.assertEqual(s.style_signal(text), 0.25)      # 0.5 * 0.0 + 0.5 * 0.5

    def test_missing_spread_counts_as_half(self):
        text = "the " * 60                                # one "sentence", TTR 0.02
        self.assertEqual(s.style_parts(text)["spread"], None)
        self.assertEqual(s.style_parts(text)["vocabulary"], 1.0)
        self.assertEqual(s.style_signal(text), 0.75)      # 0.5 * 0.5 + 0.5 * 1.0


class SentenceSplitterRegression(unittest.TestCase):
    """
    The two splitter problems found in Milestone 4 calibration, now fixed —
    and the ordinary behaviour that must not change with them.

    The starter's splitter turned "Mr." into a sentence end, and treated text
    with no space after its full stops as one long sentence. Both moved the
    style score, and the second let any text dodge scoring entirely.
    """

    def test_normal_sentences_unchanged(self):
        self.assertEqual(s.sentences("The cat sat. The dog ran."),
                         ["The cat sat.", "The dog ran."])
        self.assertEqual(s.sentences("Really?! Yes!!!  Fine.\nNext line."),
                         ["Really?!", "Yes!!!", "Fine.", "Next line."])
        self.assertEqual(s.sentences("Well... fine. Wow…"), ["Well...", "fine.", "Wow…"])
        self.assertEqual(s.sentences("  "), [])
        self.assertEqual(s.sentences("No full stop at all"), ["No full stop at all"])

    def test_abbreviations_do_not_end_sentences(self):
        self.assertEqual(s.sentences("Last year Mr. Okafor built a wall."),
                         ["Last year Mr. Okafor built a wall."])
        self.assertEqual(s.sentences("See e.g. this case. And Dr. Lee agreed."),
                         ["See e.g. this case.", "And Dr. Lee agreed."])
        for abbr in ("Mr.", "Mrs.", "Ms.", "Dr.", "Prof.", "e.g.", "i.e.", "vs.", "(e.g."):
            with self.subTest(abbr=abbr):
                self.assertEqual(len(s.sentences(f"Ask {abbr} Smith about it. Then go.")), 2)

    def test_abbreviation_at_the_very_end_is_kept(self):
        self.assertEqual(s.sentences("I asked Dr. Lee."), ["I asked Dr. Lee."])

    def test_missing_space_after_full_stop_is_a_boundary(self):
        self.assertEqual(s.sentences("Hello.World"), ["Hello.", "World"])
        self.assertEqual(s.sentences("The cat sat.The dog ran."),
                         ["The cat sat.", "The dog ran."])
        self.assertEqual(s.sentences("Really?Yes!Fine."), ["Really?", "Yes!", "Fine."])
        self.assertEqual(len(s.sentences(UNIFORM * 2)), 6)    # "hay.The" now splits

    def test_no_false_splits_without_a_capital(self):
        # Decimals, domains and initialisms stay whole.
        self.assertEqual(len(s.sentences("It costs 3.5 dollars. Fine.")), 2)
        self.assertEqual(len(s.sentences("Visit example.com today. Fine.")), 2)
        self.assertEqual(s.sentences("He lives in the U.S.A. Then he moved."),
                         ["He lives in the U.S.A.", "Then he moved."])

    def test_removing_spaces_no_longer_changes_the_score(self):
        # The cheap evasion is closed: same words, spaces after full stops removed.
        spaced = UNIFORM * 4
        squashed = spaced.replace(". ", ".")
        self.assertEqual(s.sentences(squashed), s.sentences(spaced))
        self.assertEqual(s.style_signal(squashed), s.style_signal(spaced))

    def test_abbreviation_no_longer_inflates_spread(self):
        # The calibration case: "Mr." used to create a fake 3-word sentence.
        with_abbr = "Last year Mr. Okafor built a wall. It fell. Then the rain came back."
        spelled = with_abbr.replace("Mr. ", "Mister ")
        self.assertEqual(len(s.sentences(with_abbr)), len(s.sentences(spelled)))
        self.assertEqual(s.sentence_length_spread(with_abbr),
                         s.sentence_length_spread(spelled))

    def test_known_remaining_limitations(self):
        # Documented, not endorsed: a quote after the stop, and lowercase after
        # a missing space, still don't split — same as the starter splitter.
        self.assertEqual(len(s.sentences('"Stop." She left.')), 1)
        self.assertEqual(len(s.sentences("The cat sat.the dog ran.")), 1)


if __name__ == "__main__":
    unittest.main()
