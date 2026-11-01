"""
Turning two numbers into one, and one number into something a person can read.
Built in Milestones 4 and 5.

Two functions do the deciding — `combine_signals` and `score_to_label` — with
`confidence` beside them. Thresholds and weights come from config.py and are
provisional: calibration is incomplete.

`combine_signals` is where your false-positive decision from Milestone 1
actually gets made. Everything above it — the labels, the appeal path — is
downstream of a number this function produced.

`score_to_label` is where you stop writing for a machine and start writing for
a person. A score of 0.62 means nothing to a writer.

⚠️ Your README's **Signals and Scoring** section has to name the file and
function holding your combining rule. The grader checks your code against what
you claim, so that line should read `scoring.py::combine_signals`.
"""

import math
from numbers import Real

import config


def _check_score(name: str, value) -> float:
    """A signal score must be a real, finite number in 0–1 — refuse anything else."""
    if isinstance(value, bool) or not isinstance(value, Real):
        raise TypeError(f"{name} must be a number, got {type(value).__name__}")
    if not math.isfinite(value) or not 0.0 <= value <= 1.0:
        raise ValueError(f"{name} must be between 0 and 1, got {value!r}")
    return float(value)


def _check_weights() -> tuple[float, float]:
    """
    The two weights from config.py, refused if they can't make an average:
    non-numeric, negative, NaN/infinite, or both zero. A broken setting fails
    loudly here rather than quietly producing a score nobody chose.
    """
    weights = {
        "WEIGHT_MODEL_SIGNAL": config.WEIGHT_MODEL_SIGNAL,
        "WEIGHT_STYLE_SIGNAL": config.WEIGHT_STYLE_SIGNAL,
    }
    for name, w in weights.items():
        if isinstance(w, bool) or not isinstance(w, Real) or not math.isfinite(w) or w < 0:
            raise ValueError(f"config.{name} must be a finite number ≥ 0, got {w!r}")
    model_w, style_w = (float(w) for w in weights.values())
    if model_w + style_w <= 0:
        raise ValueError("config.WEIGHT_MODEL_SIGNAL and WEIGHT_STYLE_SIGNAL can't both be 0")
    return model_w, style_w


def combine_signals(model_score: float, style_score: float) -> float:
    """
    Combine two 0–1 signals into one 0–1 score.

    **The rule:** a normalised weighted average,

        (WEIGHT_MODEL_SIGNAL × model_score + WEIGHT_STYLE_SIGNAL × style_score)
        ÷ (WEIGHT_MODEL_SIGNAL + WEIGHT_STYLE_SIGNAL)

    with both weights currently 0.5, so it's the plain mean. Dividing by the
    total keeps the result on 0–1 whatever the weights add up to. When the
    signals disagree, the result lands between them — two methods splitting
    reads as uncertainty, not as either one winning. Rounded to 4 places, like
    both signals.

    Invalid inputs are refused, not clamped: a score outside 0–1, NaN or
    infinite raises ValueError; a non-number (including True/False) raises
    TypeError. So do broken weights — see `_check_weights`.

    Both inputs point the same way: higher means more likely AI. Your output
    should too.

    Args:
        model_score: from `detector.model_signal` — how predictable the text is.
        style_score: from `stylometry.style_signal` — the shape of the text.

    Returns:
        A float from 0.0 (confidently human) to 1.0 (confidently AI).

    ⚠️ **Write the rule down before you code it, and put the numbers in your
    README.** A weighted average is the obvious choice and it is not the only
    one. Things worth thinking about:

      - **What happens when they disagree?** One signal at 0.9 and the other at
        0.1 averages to 0.5 — "unsure". Is that what you want? It might be
        exactly right: two methods disagreeing IS uncertainty. Or you might
        decide one signal is more trustworthy when they split.

      - **Which way do you want to be wrong?** Weighting toward the signal that
        reads more human means fewer false accusations and more AI text
        getting through. There's no weighting that avoids the trade.

      - Milestone 4 asks you to find a case where your two signals split and
        write it down. That case is what this rule exists to handle.

    The weights in config.py are placeholders. Change them, or ignore them and
    write a different rule.
    """
    model_score = _check_score("model_score", model_score)
    style_score = _check_score("style_score", style_score)
    model_w, style_w = _check_weights()
    combined = (model_w * model_score + style_w * style_score) / (model_w + style_w)
    return round(min(max(combined, 0.0), 1.0), 4)


def confidence(combined_score: float) -> float:
    """
    How far the combined score sits from a coin flip, on 0–1:

        round(abs(combined_score − 0.5) × 2, 2)

    0.0 at 0.5, 1.0 at either end, and at most 0.30 anywhere in the unsure
    band (0.35–0.65).

    ⚠️ **An uncalibrated, score-based indicator — not a probability that the
    guess is correct.** Nothing has measured how often a 0.8 turns out right,
    so it must never be shown to a writer as "80% sure".

    Invalid scores are refused exactly as in `combine_signals` and
    `score_to_label`.
    """
    combined_score = _check_score("combined_score", combined_score)
    return round(abs(combined_score - 0.5) * 2, 2)


LABEL_HUMAN = (
    "This text shows patterns more consistent with human writing. "
    "This is an automated estimate, not proof of authorship."
)
LABEL_UNSURE = (
    "The available signals do not support a reliable classification. "
    "No conclusion about authorship should be drawn from this result."
)
LABEL_AI = (
    "This text shows patterns associated with AI-generated writing. "
    "This result is not proof of AI use, and you can request a human review "
    "if you disagree."
)


def score_to_label(score: float) -> tuple[str, str]:
    """
    Turn a score into a guess and the text a reader actually sees.

    **The bands** (thresholds from config.py, provisional — calibration is
    incomplete):

        score <  HUMAN_THRESHOLD (0.35)   -> "human"
        0.35 <= score <= 0.65             -> "unsure"
        score >  AI_THRESHOLD (0.65)      -> "ai"

    A score exactly on either threshold is "unsure": a score sitting on the
    line between two labels doesn't earn a confident one.

    Invalid scores are refused the same way `combine_signals` refuses its
    inputs: outside 0–1, NaN or infinite raises ValueError; a non-number
    (including True/False) raises TypeError.

    Returns:
        (guess, label_text) — where `guess` is a short machine-readable string
        like "ai" / "human" / "unsure", and `label_text` is the full sentence
        shown to a person.

    ⚠️ Write the label text for someone who has never heard the word
    "threshold".

        ✗ "human, 0.81 confidence"
        ✓ "We think this was probably written by a person."

    All three labels have to be **reachable**. If no score can produce one of
    them, your ranges have a gap — and Milestone 5 asks you to submit text that
    produces each one, which is how you'd find out.

    The hardest one to write is "unsure". It has to admit uncertainty without
    sounding like an accusation, because the person reading it may well have
    written every word themselves. Your breakout asks your group what they'd
    think if they got it on their own work. That question is the whole
    milestone.
    """
    score = _check_score("score", score)
    if score < config.HUMAN_THRESHOLD:
        return "human", LABEL_HUMAN
    if score > config.AI_THRESHOLD:
        return "ai", LABEL_AI
    return "unsure", LABEL_UNSURE


def label_ranges() -> list[tuple[str, str]]:
    """
    The score range each label covers. Your README needs these beside the
    label text — given to you so the numbers can't drift apart from config.py.
    """
    return [
        ("high-confidence human", f"0.00 – {config.HUMAN_THRESHOLD:.2f}"),
        ("unsure", f"{config.HUMAN_THRESHOLD:.2f} – {config.AI_THRESHOLD:.2f}"),
        ("high-confidence AI", f"{config.AI_THRESHOLD:.2f} – 1.00"),
    ]
