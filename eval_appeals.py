#!/usr/bin/env python3
"""
Criterion 4 — the appeal path, three trials.  <- UNIT 8, MILESTONE 3

    python app.py                                  # in one terminal
    python eval_appeals.py --label before          # in another

run_eval.py only sends /submit, and criterion 4 needs a submission first and
then an appeal against the content_id that came back — so it runs here.

Each trial, against the live service:
  1. Five fresh submissions (fresh creator_ids, so nothing is rate limited),
     each appealed by its own creator. Every appeal must return 200 with
     status `under_review`, append exactly one appeal entry to the audit log,
     and leave the original decision entry exactly as it was.
  2. One appeal for a content_id that doesn't exist: must be 404
     `unknown_content_id`.
  3. A second appeal for the first item: must be 409 `already_under_review`.

The audit log is read through GET /log before and after each appeal. This
does the sending, the checking and the recording; the verdict against the
criterion is in the README.
"""

import argparse
import datetime as dt
import json
import sys

import config
import scenarios

DEFAULT_URL = f"http://{config.HOST}:{config.PORT}"
APPEALS_PER_TRIAL = 5
REASONING = "I wrote this myself and I think the result is wrong. Please review it."


def entries_for(requests, url, content_id):
    log = requests.get(f"{url}/log", timeout=30).json()["entries"]
    return [e for e in log if e.get("content_id") == content_id]


def run_trial(requests, url, trial, texts):
    checks, evidence = [], {"appeals": []}

    for i in range(APPEALS_PER_TRIAL):
        creator = f"eval_c4_t{trial}_{i + 1}"
        submitted = requests.post(f"{url}/submit", timeout=90,
                                  json={"text": texts[i], "creator_id": creator})
        body = submitted.json()
        cid = body.get("content_id")
        before = entries_for(requests, url, cid)
        decision_before = [e for e in before if "event" not in e]

        appealed = requests.post(f"{url}/appeal", timeout=30,
                                 json={"content_id": cid, "reasoning": REASONING,
                                       "creator_id": creator})
        after = entries_for(requests, url, cid)
        decision_after = [e for e in after if "event" not in e]
        appeals = [e for e in after if e.get("event") == "appeal"]

        result = {
            "submit_status": submitted.status_code,
            "content_id": cid,
            "guess": body.get("guess"),
            "appeal_status": appealed.status_code,
            "appeal_response": appealed.json(),
            "appeal_entries_after": len(appeals),
            "decision_unchanged": decision_before == decision_after and len(decision_after) == 1,
            "log_entries_added": len(after) - len(before),
        }
        result["passed"] = (submitted.status_code == 200
                            and appealed.status_code == 200
                            and result["appeal_response"].get("status") == "under_review"
                            and result["appeal_entries_after"] == 1
                            and result["log_entries_added"] == 1
                            and result["decision_unchanged"])
        evidence["appeals"].append(result)
        checks.append(result["passed"])

    unknown = requests.post(f"{url}/appeal", timeout=30,
                            json={"content_id": f"no-such-id-trial-{trial}",
                                  "reasoning": REASONING})
    evidence["unknown"] = {"status": unknown.status_code, "response": unknown.json()}
    checks.append(unknown.status_code == 404
                  and unknown.json().get("error") == "unknown_content_id")

    first = evidence["appeals"][0]["content_id"]
    duplicate = requests.post(f"{url}/appeal", timeout=30,
                              json={"content_id": first, "reasoning": REASONING,
                                    "creator_id": f"eval_c4_t{trial}_1"})
    evidence["duplicate"] = {"status": duplicate.status_code, "response": duplicate.json(),
                             "appeal_entries_after": len([e for e in entries_for(requests, url, first)
                                                          if e.get("event") == "appeal"])}
    checks.append(duplicate.status_code == 409
                  and duplicate.json().get("error") == "already_under_review"
                  and evidence["duplicate"]["appeal_entries_after"] == 1)

    evidence["valid_appeals_passed"] = sum(r["passed"] for r in evidence["appeals"])
    evidence["trial_passed"] = all(checks)
    return evidence


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--trials", type=int, default=3)
    parser.add_argument("--label", default="")
    parser.add_argument("--url", default=DEFAULT_URL)
    args = parser.parse_args()

    import requests
    try:
        requests.get(f"{args.url}/health", timeout=5)
    except Exception:  # noqa: BLE001
        print(f"Nothing answering at {args.url}. Start it:  python app.py", file=sys.stderr)
        sys.exit(1)

    # Claude-written texts, long enough to be scored (see scenarios.py).
    texts = next(s for s in scenarios.SCENARIOS if s["name"] == "c2-ai")["texts"]

    trials = []
    for trial in range(1, args.trials + 1):
        evidence = run_trial(requests, args.url, trial, texts)
        trials.append(evidence)
        print(f"trial {trial}: valid appeals passed {evidence['valid_appeals_passed']}/"
              f"{APPEALS_PER_TRIAL} · unknown -> {evidence['unknown']['status']} · "
              f"duplicate -> {evidence['duplicate']['status']} · "
              f"{'PASS' if evidence['trial_passed'] else 'FAIL'}")

    config.RESULTS_DIR.mkdir(exist_ok=True)
    stamp = dt.datetime.now().strftime("%Y-%m-%d_%H%M")
    label = f"_{args.label}" if args.label else ""
    path = config.RESULTS_DIR / f"appeals_{stamp}{label}.md"
    lines = [f"# Criterion 4 — appeals{f' — {args.label}' if args.label else ''}", "",
             "- Produced by: `eval_appeals.py::main`",
             "- Service: `app.py::submit`, `app.py::appeal`; log read through `GET /log`",
             f"- {args.trials} trials · {dt.datetime.now().strftime('%Y-%m-%d %H:%M')}", "",
             "| Trial | Valid appeals passed | Unknown id | Duplicate | Trial |",
             "|---|---|---|---|---|"]
    for n, e in enumerate(trials, 1):
        lines.append(f"| {n} | {e['valid_appeals_passed']}/{APPEALS_PER_TRIAL} | "
                     f"{e['unknown']['status']} | {e['duplicate']['status']} | "
                     f"{'PASS' if e['trial_passed'] else 'FAIL'} |")
    lines += ["", "## What actually came back", ""]
    for n, e in enumerate(trials, 1):
        lines += [f"**Trial {n}**", "", "```json", json.dumps(e, indent=2, ensure_ascii=False),
                  "```", ""]
    path.write_text("\n".join(lines), encoding="utf-8")
    print(f"\nWrote {path.relative_to(config.ROOT)}")


if __name__ == "__main__":
    main()
