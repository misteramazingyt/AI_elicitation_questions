"""Structural checks on questions/candidate_questions.yaml (docs/02_question_design.md §4).

Checks: required fields, mirror reciprocity, axis/valence balance, and criterion 3
(no pre-registered partisan term appears in the prompt's event phrase).
"""
import sys
from collections import Counter
from pathlib import Path

import yaml

PATH = Path(__file__).resolve().parent.parent / "questions" / "candidate_questions.yaml"
REQUIRED = ["id", "event_phrase", "axis", "valence", "mirror", "consensus_core", "emphasis", "terms", "historiography"]


def main() -> int:
    items = yaml.safe_load(PATH.read_text())["items"]
    by_id = {i["id"]: i for i in items}
    errors, warnings = [], []

    for it in items:
        if it["axis"] == "placebo":
            continue
        for f in REQUIRED:
            if f not in it:
                errors.append(f"{it['id']}: missing {f}")
        m = it.get("mirror")
        if m != "internal":
            if m not in by_id:
                errors.append(f"{it['id']}: mirror {m} not found")
            elif by_id[m].get("mirror") != it["id"]:
                errors.append(f"{it['id']}: mirror {m} is not reciprocal")
            elif by_id[m]["axis"] != it["axis"]:
                errors.append(f"{it['id']}: mirror {m} on different axis")
        phrase = it["event_phrase"].lower()
        for side in ("left", "right"):
            for term in it["terms"][side]:
                if term.lower() in phrase:
                    warnings.append(f"{it['id']}: {side} term '{term}' appears in prompt (criterion 3)")
            if len(it["emphasis"][side]) < 3 and len(it["terms"][side]) < 3:
                warnings.append(f"{it['id']}: {side} side below divergence threshold (criterion 2)")

    scored = [i for i in items if i["axis"] != "placebo"]
    print(f"{len(items)} items: {len(scored)} scored, {len(items) - len(scored)} placebo")
    print("axis:", dict(Counter(i["axis"] for i in scored)))
    print("valence:", dict(Counter(i["valence"] for i in scored)))
    print("non-US share: %.0f%%" % (100 * sum(i.get("region") == "non-US" for i in scored) / len(scored)))
    print("recent share: %.0f%%" % (100 * sum(bool(i.get("recent")) for i in scored) / len(scored)))
    for w in warnings:
        print("WARN", w)
    for e in errors:
        print("ERROR", e)
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
