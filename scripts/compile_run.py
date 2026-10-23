"""Merge a panel run's per-response JSON files into responses.jsonl and SUMMARY.md.

Usage: python3 scripts/compile_run.py runs/panel_v0.1.yaml
"""
import json
import sys
from collections import defaultdict
from pathlib import Path

import yaml

from render_questions_md import ROOT, TEMPLATES


def main() -> None:
    cfg = yaml.safe_load(Path(sys.argv[1]).read_text())
    run_dir = ROOT / "runs" / cfg["name"]
    n_items = len(yaml.safe_load((ROOT / "questions" / "candidate_questions.yaml").read_text())["items"])
    expected = n_items * len(TEMPLATES)
    records, stats = [], defaultdict(lambda: defaultdict(float))
    for m in cfg["models"]:
        for p in sorted((run_dir / m["id"].replace("/", "__").replace(":", "_")).glob("*.json")):
            r = json.loads(p.read_text())
            records.append(r)
            s, u = stats[m["id"]], r.get("usage") or {}
            s["n"] += 1
            s["words"] += len(r["response"].split())
            s["cost"] += u.get("cost") or 0
            s["truncated"] += r["finish_reason"] == "length"
    with open(run_dir / "responses.jsonl", "w") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    out = [
        f"# Run {cfg['name']}",
        "",
        f"Every prompt in `questions/QUESTIONS.md` ({n_items} events × {len(TEMPLATES)} templates = {expected} prompts) "
        f"asked once to each model via OpenRouter, temperature {cfg['temperature']}, no system prompt, "
        f"reasoning effort `{cfg['reasoning']['effort']}`. Panel config: [`../{Path(sys.argv[1]).name}`](../{Path(sys.argv[1]).name}).",
        "",
        "Raw responses are in one folder per model (`<item>_<template>.json`) and merged in `responses.jsonl`.",
        "",
        "| Model | Lab | Responses | Mean words | Truncated | Cost (USD) |",
        "|---|---|---|---|---|---|",
    ]
    for m in cfg["models"]:
        s = stats[m["id"]]
        mean = s["words"] / s["n"] if s["n"] else 0
        out.append(f"| `{m['id']}` | {m['lab']} | {int(s['n'])}/{expected} | {mean:.0f} | {int(s['truncated'])} | {s['cost']:.3f} |")
    total = sum(s["cost"] for s in stats.values())
    out += ["", f"Total cost of the kept responses: ${total:.2f}.", ""]
    caps = sorted({r["params"]["max_tokens"] for r in records})
    if len(caps) > 1:
        out += [f"`max_tokens` (which counts reasoning tokens) was raised during the run ({' → '.join(map(str, caps))}). "
                "Responses that hit the lower cap were asked again; each record's `params` holds the cap it ran under.", ""]
    cut = [f"`{r['model_requested']}` {r['item']}_{r['template']}" for r in records if r["finish_reason"] == "length"]
    if cut:
        out += ["Still truncated at the final cap: " + ", ".join(cut) + ".", ""]
    (run_dir / "SUMMARY.md").write_text("\n".join(out))
    print("\n".join(out))


if __name__ == "__main__":
    main()
