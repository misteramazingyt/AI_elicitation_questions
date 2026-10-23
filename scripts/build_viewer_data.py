"""Bundle a panel run and the question bank into viewer/data.json for viewer/index.html.

Usage: python3 scripts/build_viewer_data.py runs/panel_v0.1.yaml
"""
import json
import sys
from pathlib import Path

import yaml

from render_questions_md import ROOT, TEMPLATES

ITEM_FIELDS = ["id", "event_phrase", "axis", "valence", "mirror", "region", "period", "recent",
               "consensus_core", "emphasis", "terms", "historiography", "note", "caveat"]


def main() -> None:
    cfg = yaml.safe_load(Path(sys.argv[1]).read_text())
    items = yaml.safe_load((ROOT / "questions" / "candidate_questions.yaml").read_text())["items"]
    responses = {}
    for line in open(ROOT / "runs" / cfg["name"] / "responses.jsonl"):
        r = json.loads(line)
        u = r.get("usage") or {}
        responses[f"{r['model_requested']}|{r['item']}|{r['template']}"] = {
            "text": r["response"], "finish": r["finish_reason"], "cost": u.get("cost"),
            "tokens": u.get("completion_tokens"),
        }
    slant_path = ROOT / "runs" / cfg["name"] / "slant.json"
    slant = json.loads(slant_path.read_text()) if slant_path.exists() else None
    if slant:
        r3 = lambda p: p and [round(x, 3) for x in p]
        for key, by_clf in slant["scores"].items():
            responses[key]["slant"] = {c: {"doc": r3(s["doc"]), "paras": [r3(p) for p in s["paras"]]} for c, s in by_clf.items()}
    data = {
        "run": cfg["name"],
        "slant": slant and {k: slant[k] for k in ("classifiers", "labels", "min_words", "window")},
        "settings": {k: cfg[k] for k in ("temperature", "max_tokens", "reasoning", "system_prompt")},
        "templates": TEMPLATES,
        "models": cfg["models"],
        "items": [{k: it[k] for k in ITEM_FIELDS if k in it} for it in items],
        "responses": responses,
    }
    out = ROOT / "viewer" / "data.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")))
    print(f"wrote {out} ({out.stat().st_size / 1e6:.1f} MB, {len(responses)} responses)")


if __name__ == "__main__":
    main()
