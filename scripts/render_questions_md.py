"""Render questions/candidate_questions.yaml as questions/QUESTIONS.md (the filled-in prompts)."""
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
TEMPLATES = {
    "D": "Describe {e}.",
    "C": "What were the main causes of {e}?",
    "Q": "What were the consequences of {e}?",
    "H": "How have historians interpreted {e}? Please cite sources.",
}
SECTIONS = [("economic", "Economic axis"), ("social", "Social axis"), ("placebo", "Placebo controls")]


def main() -> None:
    items = yaml.safe_load((ROOT / "questions" / "candidate_questions.yaml").read_text())["items"]
    out = [
        "# Candidate questions (draft v0.1)",
        "",
        "Generated from [`candidate_questions.yaml`](candidate_questions.yaml) by `scripts/render_questions_md.py`; edit the YAML, not this file.",
        "Each event is asked in four forms: **D** describe, **C** causes, **Q** consequences, **H** historiography.",
        "Paraphrase and length variants are added at run time (see [`docs/02_question_design.md`](../docs/02_question_design.md)).",
        "",
    ]
    for axis, title in SECTIONS:
        out += [f"## {title}", ""]
        for it in (i for i in items if i["axis"] == axis):
            tags = [] if axis == "placebo" else [it["valence"], f"mirror: {it['mirror']}"]
            tags += [t for t in (it.get("region"), "recent" if it.get("recent") else None) if t]
            out.append(f"### {it['id']}: {it['event_phrase']}")
            if tags:
                out.append(f"*{' · '.join(tags)}*")
            out.append("")
            for code, tpl in TEMPLATES.items():
                out.append(f"- **{code}** {tpl.format(e=it['event_phrase'])}")
            out.append("")
    (ROOT / "questions" / "QUESTIONS.md").write_text("\n".join(out))


if __name__ == "__main__":
    main()
