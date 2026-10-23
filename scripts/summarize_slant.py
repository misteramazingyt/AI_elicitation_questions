"""Summarize runs/<panel>/slant.json as runs/<panel>/SLANT.md (same statistics as the viewer's Slant overview).

Usage: python3 scripts/summarize_slant.py runs/panel_v0.1.yaml

slant = P(right) - P(left) of the whole answer. Per event, a model's slant is averaged over the four question
forms; relative lean is that minus the panel mean on the same event, averaged over events (± 2 SE across events).
"""
import json
import statistics as st
import sys
from pathlib import Path

import yaml

from render_questions_md import ROOT, TEMPLATES

NAMES = {
    "baly": "Baly et al. 2020 (Article-Bias-Prediction, DeBERTa-v3 fine-tune)",
    "politics": "POLITICS, Liu et al. 2022 (left/center/right fine-tune)",
}


def fmt(x, d=3):
    return "–" if x is None else f"{x:+.{d}f}"


def mean(xs):
    return st.fmean(xs) if xs else None


def main() -> None:
    cfg = yaml.safe_load(Path(sys.argv[1]).read_text())
    run_dir = ROOT / "runs" / cfg["name"]
    slant = json.loads((run_dir / "slant.json").read_text())
    items = yaml.safe_load((ROOT / "questions" / "candidate_questions.yaml").read_text())["items"]
    models = [m["id"] for m in cfg["models"]]
    scores = slant["scores"]
    s_of = lambda p: p[2] - p[0]

    out = [f"# Slant scores, run {cfg['name']}", "",
           "Every answer scored by two published left/center/right classifiers (`scripts/score_slant.py`). "
           "Slant = P(right) − P(left), from −1 (left) to +1 (right). **Relative lean** is a model's slant on an event "
           "(averaged over the 4 question forms) minus the panel mean on that event, averaged over events; ± is 2 standard "
           "errors across events. Both classifiers were trained on news text, not LLM answers, and neither has been validated "
           "on this material, so treat these as exploratory. Browse them per answer and per paragraph in `viewer/`.", ""]

    pairs = [(s_of(v["baly"]["doc"]), s_of(v["politics"]["doc"])) for v in scores.values() if "baly" in v and "politics" in v]
    if len(pairs) > 2:
        out += [f"Agreement between the two classifiers across {len(pairs)} answers: Pearson r = "
                f"{st.correlation(*zip(*pairs)):.2f}.", ""]

    for clf, name in NAMES.items():
        raw = {m: {} for m in models}
        for m in models:
            for it in items:
                xs = [s_of(scores[k][clf]["doc"]) for t in TEMPLATES
                      if clf in scores.get(k := f"{m}|{it['id']}|{t}", {})]
                raw[m][it["id"]] = mean(xs)
        panel = {it["id"]: mean([raw[m][it["id"]] for m in models if raw[m][it["id"]] is not None]) for it in items}
        if all(v is None for v in panel.values()):
            continue

        def rel(m, axis):
            return [raw[m][it["id"]] - panel[it["id"]] for it in items
                    if (it["axis"] == axis or (axis == "scored" and it["axis"] != "placebo")) and raw[m][it["id"]] is not None]

        def raw_mean(m, axis):
            return mean([raw[m][it["id"]] for it in items if (it["axis"] != "placebo") == (axis == "scored") and raw[m][it["id"]] is not None])

        rows = []
        for m in models:
            r = rel(m, "scored")
            err = 2 * st.stdev(r) / len(r) ** 0.5 if len(r) > 1 else None
            rows.append((mean(r), m, raw_mean(m, "scored"), raw_mean(m, "placebo"), err, mean(rel(m, "economic")), mean(rel(m, "social"))))
        rows.sort(key=lambda r: (r[0] is None, r[0]))
        out += [f"## {name}", "",
                "| Model | Raw slant, scored events | Raw slant, placebo | Relative lean, all scored | ± 2 SE | Relative, economic | Relative, social |",
                "|---|---|---|---|---|---|---|"]
        for lean, m, rs, rp, err, ec, so in rows:
            out.append(f"| `{m}` | {fmt(rs)} | {fmt(rp)} | **{fmt(lean)}** | {'–' if err is None else f'{err:.3f}'} | {fmt(ec)} | {fmt(so)} |")
        out.append("")
    (run_dir / "SLANT.md").write_text("\n".join(out))
    print("\n".join(out))


if __name__ == "__main__":
    main()
