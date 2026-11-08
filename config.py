"""
Settings for Provenance Guard.

Everything you're likely to change lives here, at the top, on purpose.

You'll edit the thresholds in Milestone 5 and the rate limits in unit 8.
"""

import os
from pathlib import Path

ROOT = Path(__file__).parent


# ─── The service ─────────────────────────────────────────────────────────────

# `127.0.0.1` is loopback — only your own machine can reach it, which is what
# you want all through units 7 and 8. A host somewhere else has to accept
# traffic from outside the box, and that means `0.0.0.0`. Setting the env var
# is how you get it; the default keeps your local `curl` commands unchanged.
HOST = os.getenv("HOST", "127.0.0.1")
PORT = int(os.getenv("PORT", "5000"))

# Flask's debug mode gives anyone who can reach the service an interactive
# Python prompt inside your process. Fine on loopback, a gift to strangers
# anywhere else — so it turns itself off the moment HOST isn't loopback.
DEBUG = os.getenv("AI201_DEBUG", "1") == "1" and HOST in ("127.0.0.1", "localhost")


# ─── The local model ─────────────────────────────────────────────────────────
# Your first signal runs a language model ON YOUR OWN MACHINE. No account, no
# key, no card. It downloads about 550 MB the first time — do that before
# class, not during it.
#
# What it measures: how *predictable* your text is to a language model. Text a
# model finds easy to predict tends to be text a model wrote.
#
# The first call is the slow one — ten to twenty seconds while the model loads,
# longer on an older laptop. After that it stays in memory and a submission
# takes a second or two. That cost is part of what you're learning: this is
# what running a model inline in a request actually looks like.

DETECTOR_MODEL = os.getenv("AI201_DETECTOR_MODEL", "gpt2")

# Longer text gives a steadier reading but takes longer. 400 tokens is roughly
# 300 words, which is enough for the signal to mean something.
DETECTOR_MAX_TOKENS = 400

# The longest `text` /submit accepts. Anything over it is refused with a 413,
# not truncated — see DESIGN.md. A proposal until tested, like every number here.
MAX_TEXT_CHARS = 20_000

# Below either of these, a submission is too short for the signals to mean
# anything, and gets "insufficient_evidence" instead of a score — not a 400,
# because a short poem is a legitimate submission. Proposals until Milestone 4.
MIN_WORDS_TO_ASSESS = 50
MIN_SENTENCES_TO_ASSESS = 3

# The longest `reasoning` /appeal accepts — see DESIGN.md.
MAX_REASONING_CHARS = 2_000


# ─── Scoring (Milestone 4) ───────────────────────────────────────────────────
# How much each signal counts toward the combined score.
#
# ⚠️ These are placeholders. Milestone 4 asks you to write your combining rule
# down BEFORE you code it, and to put the numbers in your README. Whatever you
# decide, it goes here.

WEIGHT_MODEL_SIGNAL = 0.5
WEIGHT_STYLE_SIGNAL = 0.5

# How stylometry.style_signal maps each raw measure onto 0–1. Each pair is
# (the value that scores 1.0, most AI-like; the value that scores 0.0, most
# human-like), with a straight line between and clamping outside. Proposals
# until the Milestone 4 calibration inputs have been run — see DESIGN.md.
#
# CALIBRATION STATUS (2026-11-01): INCOMPLETE. No verified human-written
# samples yet — only AI-written ones, two with real GPT-2 scores. These
# anchors, the part weights below, the signal weights above and the label
# thresholds are all provisional. Nothing here is a calibrated detector.
STYLE_SPREAD_ANCHORS = (0.20, 0.70)        # sentence-length CV: even → AI
STYLE_TTR_ANCHORS = (0.60, 0.80)           # moving-average TTR: repetitive → AI
STYLE_PUNCT_DENSITY_ANCHORS = (0.5, 2.0)   # inner punctuation per sentence: sparse → AI
STYLE_PUNCT_KINDS_ANCHORS = (1, 4)         # kinds of inner punctuation used: few → AI

# Moving-average TTR window. Below this many words the measure is undefined.
STYLE_TTR_WINDOW = 50

# How much each part counts inside stylometry.style_signal. Provisional.
# Punctuation is measured but weighted 0 for now: in the Step 1B calibration
# review it sat at or near 1.0 (most AI-like) on 7 of 8 samples, adding about
# +0.33 to almost everything, and its direction is still unconfirmed.
STYLE_WEIGHT_SPREAD = 0.50
STYLE_WEIGHT_VOCABULARY = 0.50
STYLE_WEIGHT_PUNCTUATION = 0.00


# ─── Thresholds (Milestone 5) ────────────────────────────────────────────────
# Where one label becomes another. Scores run 0.0 (confidently human) to 1.0
# (confidently AI).
#
#   score < HUMAN_THRESHOLD          -> high-confidence human
#   between the two                  -> unsure
#   score > AI_THRESHOLD             -> high-confidence AI
#
# ⚠️ This is where your false-positive decision from Milestone 1 actually gets
# made. Widening the unsure band means fewer wrong accusations and more AI text
# getting through. There is no setting that avoids the trade — only settings
# that decide who pays for it.

HUMAN_THRESHOLD = 0.35
AI_THRESHOLD = 0.65

# Exactly 0.35 or exactly 0.65 is "unsure" — see scoring.score_to_label.
#
# ⚠️ Reachability. The combined score is a weighted average, and an average
# can only land between its two inputs. The style signal now varies (it is no
# longer the 0.5 stub), so all three labels are reachable in principle — but
# with weights 0.5 / 0.5:
#
#   - "human" needs model_score + style_score < 0.70: BOTH signals fairly low.
#   - "ai" needs model_score + style_score > 1.30: BOTH signals fairly high.
#
# One signal alone can't produce a confident label; if they disagree the
# result is "unsure". Whether real text actually lands in each band is NOT yet
# shown — calibration is incomplete (see STYLE_* above). Criterion 3 tests it.
# `scoring.label_ranges()` prints the bands; the reachable range is a
# different question.


# ─── Rate limiting (UNIT 8) ──────────────────────────────────────────────────
# On from unit 8, Milestone 1. Set AI201_RATE_LIMITS=0 to switch it off.
#
# Think about two people: a real writer submitting their own work a few times
# an hour, and a script sending a thousand variations to map your thresholds.
# Your README has to say why your numbers and not others.
#
# Counted per creator_id (falling back to the caller's address) — see
# app.py::rate_limit_key. Applies to POST /submit only.
#
#   5 a minute — a writer pastes, reads the label, edits, resubmits: one every
#     12 seconds is already brisk for that. A script probing thresholds gets
#     5, not hundreds. And it's under 15, so the flood test shows 429s.
#   100 a day — a heavy day for a real writer is a few dozen submissions; 100
#     leaves room. Mapping the thresholds takes thousands of variations, so at
#     100 a day one creator_id would need weeks.
#
# ⚠️ A script can rotate creator_ids to look like many writers, and in-memory
# storage forgets every count on restart. These numbers slow a careless
# attacker; they don't stop a determined one.

RATE_LIMITING_ENABLED = os.getenv("AI201_RATE_LIMITS", "1") == "1"

RATE_LIMIT_PER_MINUTE = 5
RATE_LIMIT_PER_DAY = 100

# Flask-Limiter warns loudly without this. In-memory is right for one laptop
# and wrong for anything real — a restart forgets every count, and two copies
# of the service wouldn't share limits.
RATE_LIMIT_STORAGE = "memory://"


# ─── Paths ───────────────────────────────────────────────────────────────────

LOG_DIR = ROOT / "logs"
AUDIT_LOG = LOG_DIR / "audit.jsonl"
RESULTS_DIR = ROOT / "results"
