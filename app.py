#!/usr/bin/env python3
"""
Provenance Guard — the web service.

    python app.py

Then, in another terminal:

    curl -X POST http://127.0.0.1:5000/ping \
      -H "Content-Type: application/json" \
      -d '{"message": "hello"}'

That's the example route. It works right now, before you've written anything.
**Leave it alone** — it's your control. When something breaks later, check that
`/ping` still answers: if it does, the problem is in your handler; if it
doesn't, it's the service itself.

Routes:

    POST /ping        the worked example. Already works. Don't edit it
    POST /submit      score a piece of text, label it, log it (Milestones 3–5)
    POST /appeal      a writer contests a decision (Milestone 5)
    GET  /log         the audit log. Already works
    GET  /health      is the service up, and is the model loaded
"""

import threading
import uuid

from flask import Flask, jsonify, request

import audit
import config
import detector
import scoring
import stylometry

app = Flask(__name__)


# ── Rate limiting — UNIT 8 ────────────────────────────────────────────────────
# On (unit 8, Milestone 1): config.RATE_LIMITING_ENABLED defaults to True, the
# numbers are in config.py, and the @limiter.limit(...) line on /submit is
# live. AI201_RATE_LIMITS=0 switches it off, and then that decorator is a
# no-op that quietly does nothing.
#
# The storage backend is preconfigured, which stops Flask-Limiter printing a
# warning on every start. In-memory is right for one laptop and wrong for
# anything real — a restart forgets every count.

class _LimiterOff:
    """
    Stands in for the real limiter while rate limiting is off.

    It makes @limiter.limit(...) a decorator that returns the route
    untouched, so uncommenting the line before you flip the setting is
    harmless instead of a crash on startup.
    """

    def limit(self, *args, **kwargs):
        return lambda view: view


# The /submit limit, built once from config.py: "5/minute;100/day".
SUBMIT_RATE_LIMIT = f"{config.RATE_LIMIT_PER_MINUTE}/minute;{config.RATE_LIMIT_PER_DAY}/day"

limiter = _LimiterOff()
if config.RATE_LIMITING_ENABLED:
    from flask_limiter import Limiter
    from flask_limiter.util import get_remote_address

    def rate_limit_key():
        """
        Who a request counts against.

        Falling back to the caller's address is the easy version. Unit 8's
        stretch asks about per-creator limits instead — and the difference
        matters: one script can look like a thousand callers, and one household
        can look like one.
        """
        payload = request.get_json(silent=True)
        # A body that parses as JSON but isn't an object — a bare list or
        # string — has no .get. Without this guard the key function raises
        # BEFORE the route runs, and a malformed request becomes a 500 that
        # looks like your handler crashed when your handler never ran.
        if not isinstance(payload, dict):
            return get_remote_address()
        creator = payload.get("creator_id")
        return creator if isinstance(creator, str) and creator.strip() else get_remote_address()

    limiter = Limiter(
        key_func=rate_limit_key,
        app=app,
        storage_uri=config.RATE_LIMIT_STORAGE,
        default_limits=[],
    )

    @app.errorhandler(429)
    def rate_limited(exc):
        """
        A rejected request still leaves a trace.

        ⚠️ An attack that shows up only as an absence is one you'll never find.
        """
        payload = request.get_json(silent=True)
        if not isinstance(payload, dict):
            payload = {}
        creator = payload.get("creator_id")
        audit.log_rejection(
            creator_id=creator if isinstance(creator, str) and creator.strip() else "unknown",
            reason="rate_limited",
            limit=str(exc.description),
            http_status=429,
            endpoint=request.path,
        )
        return jsonify({
            "error": "rate_limited",
            "message": "Too many submissions. Try again shortly.",
            "limit": str(exc.description),
        }), 429


# ── The worked example. Already works. Don't edit. ────────────────────────────

@app.post("/ping")
def ping():
    """
    Everything a route needs, in six lines.

    JSON arrives as a dict. You pull things out of it. You return a dict and
    the framework turns it into a response. That's the whole idea.
    """
    payload = request.get_json(silent=True) or {}
    return jsonify({
        "ok": True,
        "you_sent": payload.get("message"),
        "service": "provenance-guard",
    })


@app.get("/health")
def health():
    """Is the service up, and has the model been downloaded yet?"""
    import detector

    loaded = detector._model is not None
    return jsonify({
        "ok": True,
        "detector_model": config.DETECTOR_MODEL,
        "detector_loaded": loaded,
        "rate_limiting": config.RATE_LIMITING_ENABLED,
        "rate_limits": SUBMIT_RATE_LIMIT if config.RATE_LIMITING_ENABLED else None,
        "log_entries": len(audit.read_entries()),
    })


# ── Submissions and appeals (Milestones 3–5) ─────────────────────────────────

@app.post("/submit")
@limiter.limit(SUBMIT_RATE_LIMIT)
def submit():
    """
    Take a piece of text, decide about it, log the decision, answer.

    Expects JSON:
        {"text": "...", "creator_id": "..."}

    Should return JSON with, at minimum:
        {"content_id": "...", "guess": "...", "confidence": 0.0, "label": "...",
         "model_score": 0.0, "style_score": 0.0}

    ⚠️ **Both signal scores go in the response, not just the log.** Unit 8's
    `run_attacks.py` and `run_eval.py` read `model_score` and `style_score`
    straight off this response and put them in your reports. Leave them out and
    every row of next unit's evidence says `null` — which is exactly the
    diagnostic you need to name a stage and a mechanism. You do not want to
    find that out after running the attack set.

    ─────────────────────────────────────────────────────────────────────────
    Build it in three passes. Do not skip ahead — the ordering is how you tell
    a broken route from a broken signal.

    **Milestone 3 — the route answers.**
      1. Return a hardcoded response. Confirm `curl` gets it back before you
         add any logic at all.
      2. Then pull `text` and `creator_id` out of the payload.
      3. Then call ONE signal — `detector.model_signal(text)` — and put the
         real number in. Leave confidence and label as placeholders.
      4. Log every submission with `audit.log_decision(...)`. The content_id
         matters: `/appeal` needs it, and a student who skips it rebuilds this
         whole flow later.

    **Milestone 4 — the second signal and the score.**
      5. Add `stylometry.style_signal(text)`.
      6. Combine them with `scoring.combine_signals(...)`.
      7. Log BOTH signal scores alongside the combined one, and put them in the
         response too. Next unit you can't diagnose anything without them.

    **Milestone 5 — the label.**
      8. `scoring.score_to_label(...)` and put the real label in the response.

    ─────────────────────────────────────────────────────────────────────────
    Worth deciding early, because unit 8's attack set will decide it for you:
    what should this do when `text` is missing, empty, or enormous? A crash on
    a malformed input is one of the most common real failures there is.
    """
    payload = request.get_json(silent=True)

    # A bare list or string parses as JSON but has no .get — refuse it here
    # rather than let it become a 500 further down.
    if not isinstance(payload, dict):
        return _reject(400, "invalid_input", None,
                       "Send a JSON object with \"text\" and \"creator_id\".", payload)

    text = payload.get("text")
    creator_id = payload.get("creator_id")

    if not isinstance(text, str) or not text.strip():
        return _reject(400, "invalid_input", "text",
                       "\"text\" must be a non-empty string.", payload)
    if not isinstance(creator_id, str) or not creator_id.strip():
        return _reject(400, "invalid_input", "creator_id",
                       "\"creator_id\" must be a non-empty string.", payload)
    if len(text) > config.MAX_TEXT_CHARS:
        return _reject(413, "too_long", "text",
                       f"Text is longer than {config.MAX_TEXT_CHARS:,} characters. "
                       f"Please submit a shorter piece.", payload)

    # Too short to judge isn't suspicious and isn't an error: say so, run no
    # signal, and make no claim either way. Judged on word count alone — a
    # sentence count let a long text skip scoring by joining its sentences
    # with semicolons (attack EV07; Unit 8, Milestone 5).
    if len(stylometry.words(text)) < config.MIN_WORDS_TO_ASSESS:
        return _decide(creator_id, text, {
            "guess": "insufficient_evidence",
            "confidence": None,
            "label": "This piece is too short for us to assess, so we haven't "
                     "made any judgment about it.",
            "model_score": None,
            "style_score": None,
            "combined_score": None,
        }, reason="too_short_to_assess")

    # No model, no label — never fall back to a made-up score.
    try:
        model_score = detector.model_signal(text)
    except detector.DetectorUnavailable:
        return _reject(503, "detector_unavailable", None,
                       "The checker isn't available right now, so nothing was "
                       "decided about your text. Please try again later.", payload)

    style_score = stylometry.style_signal(text)
    combined_score = scoring.combine_signals(model_score, style_score)
    guess, label = scoring.score_to_label(combined_score)

    return _decide(creator_id, text, {
        "guess": guess,
        "confidence": scoring.confidence(combined_score),
        "label": label,
        "model_score": model_score,
        "style_score": style_score,
        "combined_score": combined_score,
    })


def _decide(creator_id, text, decision, **extra):
    """
    Give a submission its id, log the decision, and answer with it.

    The response and the log entry are built from the same values, so the
    content_id a writer is handed is always one /appeal can find. The text
    itself isn't logged, only its length. `confidence` isn't one of the nine
    audit fields, so it's logged as an extra beside them.
    """
    content_id = str(uuid.uuid4())
    audit.log_decision(
        content_id=content_id,
        creator_id=creator_id,
        guess=decision["guess"],
        model_score=decision["model_score"],
        style_score=decision["style_score"],
        combined_score=decision["combined_score"],
        label=decision["label"],
        status="decided",
        confidence=decision["confidence"],
        text_length=len(text),
        **extra,
    )
    return jsonify({
        "content_id": content_id,
        "creator_id": creator_id,
        **decision,
        "status": "decided",
        **extra,
        "appeal": {
            "how": "POST /appeal with this content_id and your reasoning",
            "content_id": content_id,
        },
    })


def _reject(status, error, field, message, payload, **extra):
    """
    Refuse a request, and leave a trace of it.

    A rejection is never a verdict on the writer: no score, no label, no
    content_id. The text itself isn't logged, only which rule it broke.
    """
    creator = payload.get("creator_id") if isinstance(payload, dict) else None
    audit.log_rejection(
        creator_id=creator if isinstance(creator, str) and creator.strip() else "unknown",
        reason=error,
        field=field,
        http_status=status,
        **extra,
    )
    return jsonify({"error": error, "field": field, "message": message}), status


# Held across "is it already under review?" and "record the appeal", so two
# appeals for the same item arriving together can't both see `decided` and
# both get recorded. Flask's server is threaded, so that race is real.
#
# ⚠️ One process only. A threading.Lock is invisible to other processes — run
# several gunicorn workers and each has its own lock, and the race is back.
# That would need a file lock or a database transaction instead.
_APPEAL_LOCK = threading.Lock()


@app.post("/appeal")
def appeal():
    """
    A writer says you got it wrong.

    Expects JSON:
        {"content_id": "...", "reasoning": "...", "creator_id": "..." (optional)}

    What it does (the contract is in DESIGN.md):
      1. Validates the body — a JSON object, a non-empty `content_id`, a
         non-empty `reasoning` of at most MAX_REASONING_CHARS, and, if sent,
         a non-empty `creator_id`. Otherwise 400 `invalid_input`.
      2. Finds the original decision with `audit.entries_for(id)` — only a
         decision entry counts. None: 404 `unknown_content_id`, so a typo
         fails loudly instead of silently.
      3. If `creator_id` was sent and isn't the original submitter's: 403
         `creator_mismatch`. If it was left out, the original one is used.
      4. If the item is already `under_review` — an appeal is on record — 409
         `already_under_review`. One appeal per item: nothing new is appended,
         and the first appeal stands. The message reassures rather than
         blames; sending twice isn't the writer's mistake. The check and the
         append share `_APPEAL_LOCK`, so this holds even for simultaneous
         requests — within one process.
      5. Otherwise records the appeal with `audit.log_appeal(...)` — appended
         after the decision, which is never touched — moving the item to
         `under_review`.
      6. Answers 200 with the new status, the previous one, the original
         guess, and when the appeal was recorded.

    Every refusal is logged with `log_rejection`. Nothing is re-scored: the
    appeal goes to a person.

    This is the smallest endpoint in the project and the one that matters most
    to the person on the other end. It's the only thing standing between a
    wrong accusation and nothing at all.
    """
    payload = request.get_json(silent=True)

    def refuse(status, error, field, message):
        # The id the writer tried goes under its own key: a rejection never
        # carries `content_id`, so entries_for() can't mistake it for a decision.
        attempted = payload.get("content_id") if isinstance(payload, dict) else None
        extra = {"endpoint": "/appeal"}
        if isinstance(attempted, str):
            extra["attempted_content_id"] = attempted[:100]
        return _reject(status, error, field, message, payload, **extra)

    if not isinstance(payload, dict):
        return refuse(400, "invalid_input", None,
                      "Send a JSON object with \"content_id\" and \"reasoning\".")

    content_id = payload.get("content_id")
    reasoning = payload.get("reasoning")
    creator_id = payload.get("creator_id")

    if not isinstance(content_id, str) or not content_id.strip():
        return refuse(400, "invalid_input", "content_id",
                      "\"content_id\" must be the non-empty id from your result.")
    if not isinstance(reasoning, str) or not reasoning.strip():
        return refuse(400, "invalid_input", "reasoning",
                      "Please tell us why you think the result is wrong.")
    if len(reasoning) > config.MAX_REASONING_CHARS:
        return refuse(400, "invalid_input", "reasoning",
                      f"Please keep your reasoning under {config.MAX_REASONING_CHARS:,} "
                      f"characters.")
    # Optional — but if it's sent, it has to be a real id.
    if creator_id is not None and (not isinstance(creator_id, str) or not creator_id.strip()):
        return refuse(400, "invalid_input", "creator_id",
                      "\"creator_id\" is optional, but if you send it, it must be a "
                      "non-empty string.")

    decision = _find_decision(content_id)
    if decision is None:
        return refuse(404, "unknown_content_id", "content_id",
                      "We couldn't find a result with that content_id. Please check it "
                      "matches the one in your result exactly.")

    original_creator = decision["creator_id"]
    if creator_id is not None and creator_id != original_creator:
        return refuse(403, "creator_mismatch", "creator_id",
                      "That creator_id doesn't match the one this text was submitted "
                      "under. Only the original submitter can appeal it.")

    # The check and the append happen under one lock — see _APPEAL_LOCK.
    with _APPEAL_LOCK:
        previous_status = _current_status(content_id)
        entry = None
        if previous_status != "under_review":
            entry = audit.log_appeal(content_id, original_creator, reasoning)

    if entry is None:
        return refuse(409, "already_under_review", "content_id",
                      "Your appeal for this result is already recorded and waiting for "
                      "a person to review it. You don't need to send it again.")

    return jsonify({
        "content_id": content_id,
        "status": entry["status"],
        "previous_status": previous_status,
        "original_guess": decision["guess"],
        "message": "Thanks — your appeal is recorded and a person will review this "
                   "decision. The original label is paused while they do.",
        "appealed_at": entry["timestamp"],
    })


def _find_decision(content_id):
    """
    The original decision for a content_id, or None.

    Only a decision counts — an entry from log_decision, which has no "event".
    Appeal and rejection entries are ignored even if they carry the same id.
    """
    for entry in audit.entries_for(content_id):
        if "event" not in entry:
            return entry
    return None


def _current_status(content_id):
    """
    Where an item stands now: the status on its latest decision or appeal
    entry. The log is append-only, so the newest entry wins.
    """
    status = None
    for entry in audit.entries_for(content_id):
        if "event" not in entry or entry.get("event") == "appeal":
            status = entry["status"]
    return status


# ── Already works ─────────────────────────────────────────────────────────────

@app.get("/log")
def get_log():
    """
    The audit log, most recent last.

        curl "http://127.0.0.1:5000/log?limit=10"

    You need this in unit 8 to paste entries into your README, and you need it
    now to see whether your logging is actually working.
    """
    limit = request.args.get("limit", type=int)
    entries = audit.read_entries(limit=limit)
    return jsonify({"count": len(entries), "entries": entries})


def main():
    print(f"Provenance Guard on http://{config.HOST}:{config.PORT}")
    print(f"  detector model:  {config.DETECTOR_MODEL}")
    print(f"  rate limiting:   {'ON' if config.RATE_LIMITING_ENABLED else 'off (unit 8)'}")
    print(f"  audit log:       {config.AUDIT_LOG}")
    print()
    print("Check it's alive:")
    print(f'  curl -X POST http://{config.HOST}:{config.PORT}/ping \\')
    print('    -H "Content-Type: application/json" \\')
    print("    -d '{\"message\": \"hello\"}'")
    print()
    # debug=True hands out an interactive debugger, so it's local-only — see config.py
    app.run(host=config.HOST, port=config.PORT, debug=config.DEBUG)


if __name__ == "__main__":
    main()
