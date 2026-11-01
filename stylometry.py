"""
Signal two: the style signal. ← YOU BUILD THIS IN MILESTONE 4

Signal one reads the text for meaning. This one measures it *as text* — the
shape of it, without understanding a word.

Three measures are stubbed below because the brief names those three. They are
stubs, not implementations: what they compute is yours, and so is how you
combine them.

    sentence_length_spread   do sentences vary in length, or march in step?
    type_token_ratio         how much of the vocabulary repeats?
    punctuation_density      how much punctuation, and how varied?

Why these might differ between human and AI writing: generated prose tends
toward even, mid-length sentences and a narrower band of vocabulary, because
that's what "most likely next word" produces on average. Human writing is
lumpier — a three-word sentence next to a forty-word one.

⚠️ **The blind spot, which you have to name in Milestone 1.**

This signal cannot read. It has no idea what the text says. Anything that
changes the shape without changing the substance moves it — adding typos,
breaking up sentences, pasting in a quotation. That is a very cheap thing for
someone to do on purpose, and unit 8's attack set will do it to you.

Build each function on its own and call it from a terminal before you wire
anything together:

    python stylometry.py "some text to look at"
"""

import re
import statistics

import config


# Words whose full stop doesn't end a sentence. Kept short on purpose: "etc."
# and "St." end sentences often enough that guessing wrong costs more.
_ABBREVIATIONS = {"mr", "mrs", "ms", "dr", "prof", "sr", "jr", "vs", "e.g", "i.e", "cf"}

# A sentence ends at . ! or ? followed by whitespace, or followed straight by
# a capital letter ("Hello.World") — no space shouldn't hide a boundary.
_BOUNDARY = re.compile(r"(?<=[.!?])(?:\s+|(?=[A-Z]))")


def sentences(text: str) -> list[str]:
    """
    Split into sentences. Rough, but no longer fooled by two things the
    starter version was:

      - **Abbreviations.** "Mr. Okafor" or "e.g. this" isn't a boundary.
      - **A missing space.** "Hello.World" is two sentences, so deleting the
        spaces after full stops can't turn a whole text into one "sentence".

    A missing space is only a boundary before a capital letter, and not after
    a single letter, so "U.S.A." and "3.5" stay whole. Lowercase after a
    missing space ("example.com") is still not split.
    """
    text = text.strip()
    parts, start = [], 0
    for match in _BOUNDARY.finditer(text):
        chunk = text[start:match.start()]
        if _ends_with_abbreviation(chunk):
            continue
        if not match.group() and _ends_with_initial(chunk):
            continue
        parts.append(chunk)
        start = match.end()
    parts.append(text[start:])
    return [p for p in parts if p.strip()]


def _last_token(chunk: str) -> str:
    """The word before a chunk's final full stop, without that stop."""
    found = re.search(r"(\S+)\.$", chunk)
    return found.group(1).lstrip("(\"'“‘") if found else ""


def _ends_with_abbreviation(chunk: str) -> bool:
    return _last_token(chunk).lower() in _ABBREVIATIONS


def _ends_with_initial(chunk: str) -> bool:
    """Ends in a lone letter and a stop, like the "S." in "U.S.A."."""
    last = _last_token(chunk).rsplit(".", 1)[-1]
    return len(last) == 1 and last.isalpha()


def words(text: str) -> list[str]:
    """Split into lowercase words, punctuation stripped. Given to you."""
    return re.findall(r"[a-z0-9']+", text.lower())


# ── The three measures ───────────────────────────────────────────────────────
#
# Each returns the raw measurement, or None when the text doesn't give it
# enough to measure. None is "no evidence", and style_signal treats it as
# neutral rather than as a point against the writer.

# Punctuation inside a sentence, as opposed to the full stop that ends it.
# Each pattern is one "kind"; every match is one mark.
_INNER_PUNCTUATION = {
    "comma": r",",
    "semicolon": r";",
    "colon": r":",
    "dash": r"—|–|--| - ",
    "parenthesis": r"\(",
    "quotation": r"[\"“”]",
}


def sentence_length_spread(text: str) -> float | None:
    """
    How much sentence length varies: the coefficient of variation (standard
    deviation over mean) of words per sentence.

    Returns:
        0.0 upward. **Higher means more varied, which reads more human.**
        None for fewer than two sentences with words in them — one sentence
        has no spread, and `stdev` raises on fewer than two values.
    """
    lengths = [len(words(s)) for s in sentences(text)]
    lengths = [n for n in lengths if n > 0]    # "!!!" on its own isn't a sentence
    if len(lengths) < 2:
        return None
    return round(statistics.stdev(lengths) / statistics.mean(lengths), 4)


def type_token_ratio(text: str) -> float | None:
    """
    Unique words over total words, averaged over a sliding window
    (moving-average TTR) so a long text and a short one compare fairly.

    Returns:
        0–1. **Higher means more varied vocabulary, which reads more human.**
        None below `config.STYLE_TTR_WINDOW` words, where the window doesn't
        fit even once.

    Plain TTR falls as text gets longer, because common words repeat. A fixed
    window takes length out of it.
    """
    tokens = words(text)
    window = config.STYLE_TTR_WINDOW
    if len(tokens) < window:
        return None
    ratios = [
        len(set(tokens[i:i + window])) / window
        for i in range(len(tokens) - window + 1)
    ]
    return round(statistics.mean(ratios), 4)


def punctuation_density(text: str) -> float | None:
    """
    Inner punctuation marks per sentence — commas, semicolons, colons, dashes,
    parentheses, quotation marks. Full stops, question and exclamation marks
    aren't counted: every sentence has one.

    Returns:
        0.0 upward. Higher means more inner punctuation, which this signal
        currently reads as more human — a direction DESIGN.md leaves to be
        settled in calibration. None if there are no sentences at all.
    """
    count = len(sentences(text))
    if count == 0:
        return None
    marks = sum(len(re.findall(p, text)) for p in _INNER_PUNCTUATION.values())
    return round(marks / count, 4)


def punctuation_kinds(text: str) -> int:
    """How many of the six kinds of inner punctuation appear at all, 0–6."""
    return sum(1 for p in _INNER_PUNCTUATION.values() if re.search(p, text))


# ── Combining them ───────────────────────────────────────────────────────────

def _scale(value: float | None, anchors: tuple[float, float]) -> float | None:
    """
    Map a raw measure onto 0–1 with 1.0 = most AI-like.

    `anchors` is (the value that scores 1.0, the value that scores 0.0), with a
    straight line between and clamping outside — so the flip for measures
    where *low* means AI happens here, by putting the low value first.
    """
    if value is None:
        return None
    ai_end, human_end = anchors
    scaled = (value - human_end) / (ai_end - human_end)
    return min(max(scaled, 0.0), 1.0)


def style_parts(text: str) -> dict[str, float | None]:
    """
    Each measure on the 0–1 AI-likeness scale, before averaging — None where
    the text gave nothing to measure. Useful for seeing which measure moved.
    """
    density = punctuation_density(text)
    if density is None:
        punctuation = None
    else:
        punctuation = statistics.mean([
            _scale(density, config.STYLE_PUNCT_DENSITY_ANCHORS),
            _scale(punctuation_kinds(text), config.STYLE_PUNCT_KINDS_ANCHORS),
        ])
    parts = {
        "spread": _scale(sentence_length_spread(text), config.STYLE_SPREAD_ANCHORS),
        "vocabulary": _scale(type_token_ratio(text), config.STYLE_TTR_ANCHORS),
        "punctuation": punctuation,
    }
    return {k: None if v is None else round(v, 4) for k, v in parts.items()}


def style_signal(text: str) -> float:
    """
    The style signal as a 0–1 score. **Higher means more likely AI.**

    A weighted average of the three parts from `style_parts`, each already
    flipped and scaled so 1.0 is the AI-like end. Weights live in config.py:

      - spread       low sentence-length variation → AI     STYLE_WEIGHT_SPREAD
      - vocabulary   low moving-average TTR → AI            STYLE_WEIGHT_VOCABULARY
      - punctuation  sparse, unvaried inner punctuation     STYLE_WEIGHT_PUNCTUATION

    **Punctuation is temporarily weighted 0.** It is still measured, and still
    shows in `style_parts`, but it doesn't move the score. In the Step 1B
    calibration review it sat at or near 1.0 on 7 of 8 samples — ordinary
    prose with a comma or two per sentence read as fully AI, and the "kinds"
    half mostly measured length — so it pushed nearly every text about a third
    of the way toward AI, plain human writing included. Its direction is also
    unconfirmed: current chat models often use *more* commas and dashes, not
    fewer. It comes back only if calibration on real samples shows it
    separates human from AI.

    A part the text is too short for counts as 0.5, neutral — missing evidence
    shouldn't count against the writer. So empty text scores 0.5.

    The anchors in config.py are proposals until the Milestone 4 calibration
    inputs have been run: clearly AI, clearly human, plain conventional human
    writing, lightly-edited AI. Plain writing is the one to watch — on spread
    and vocabulary it looks AI-like here for the same reason it does to
    signal one.
    """
    parts = style_parts(text)
    weights = {
        "spread": config.STYLE_WEIGHT_SPREAD,
        "vocabulary": config.STYLE_WEIGHT_VOCABULARY,
        "punctuation": config.STYLE_WEIGHT_PUNCTUATION,
    }
    total = sum(weights.values())
    if total <= 0:
        return 0.5
    score = sum(
        w * (0.5 if parts[name] is None else parts[name])
        for name, w in weights.items()
    ) / total
    return round(min(max(score, 0.0), 1.0), 4)


if __name__ == "__main__":
    import sys

    text = " ".join(sys.argv[1:]) or (
        "The system works well. It handles most cases correctly and provides "
        "good results. Users generally find it easy to use and understand."
    )

    print(f"{len(sentences(text))} sentences, {len(words(text))} words\n")
    print(f"sentence_length_spread   {sentence_length_spread(text)}")
    print(f"type_token_ratio         {type_token_ratio(text)}")
    print(f"punctuation_density      {punctuation_density(text)}")
    print(f"punctuation_kinds        {punctuation_kinds(text)}")
    print(f"parts (1.0 = AI-like)    {style_parts(text)}")
    print(f"style_signal             {style_signal(text)}   (higher = more likely AI)")
    print("\nNone means the text is too short for that measure; it counts as 0.5.")
