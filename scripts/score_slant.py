"""Score every response in a panel run with off-the-shelf left/center/right slant classifiers.

Usage: python3 scripts/score_slant.py runs/panel_v0.1.yaml   (needs torch, transformers, sentencepiece)

Classifiers (both output P(left), P(center), P(right); label order 0/1/2 checked by probe):
  baly  - DeBERTa-v3-base fine-tuned on the Article-Bias-Prediction corpus of Baly et al. (EMNLP 2020),
          https://github.com/ramybaly/Article-Bias-Prediction, weights premsa/political-bias-prediction-allsides-DeBERTa.
  politics - POLITICS encoder of Liu et al. (Findings of NAACL 2022), https://github.com/launchnlp/POLITICS,
          fine-tuned for left/center/right leaning as matous-volf/political-leaning-politics.

Two granularities per response:
  doc   - the whole answer, split into consecutive 510-token windows; window probabilities are
          averaged, weighted by token count (both models were trained on article-length inputs).
  paras - each blank-line-separated block with >= MIN_WORDS words, truncated to 512 tokens. Blocks are
          split exactly as viewer/index.html splits them, so scores line up with rendered paragraphs.
Markdown markup is stripped before classification. slant = P(right) - P(left), in [-1, 1].

Output: runs/<panel>/slant.json. Re-running skips responses already scored.
"""
import json
import re
import sys
import time
from pathlib import Path

import torch
import yaml
from transformers import AutoModelForSequenceClassification, AutoTokenizer

from render_questions_md import ROOT

CLASSIFIERS = {
    "baly": {"model": "premsa/political-bias-prediction-allsides-DeBERTa", "tokenizer": None},
    "politics": {"model": "matous-volf/political-leaning-politics", "tokenizer": "launch/POLITICS"},
}
MIN_WORDS = 12
WINDOW = 510
BATCH = 16


def split_blocks(text):
    return re.split(r"\n\s*\n", text.strip())


def plain(md):
    md = re.sub(r"```.*?```", " ", md, flags=re.S)
    md = re.sub(r"!?\[([^\]]*)\]\([^)]*\)", r"\1", md)
    md = re.sub(r"^\s{0,3}(#{1,6}\s*|[-*+]\s+|\d+[.)]\s+|>\s?)", "", md, flags=re.M)
    md = re.sub(r"(\*\*|__|\*|_|`|\|)", " ", md)
    md = re.sub(r"^[\s:-]+$", "", md, flags=re.M)
    return re.sub(r"\s+", " ", md).strip()


class Scorer:
    def __init__(self, spec):
        self.tok = AutoTokenizer.from_pretrained(spec["tokenizer"] or spec["model"])
        self.model = AutoModelForSequenceClassification.from_pretrained(spec["model"]).eval()

    @torch.no_grad()
    def probs(self, id_lists):
        """Probabilities for pre-tokenized inputs (lists of token ids without special tokens)."""
        out = [None] * len(id_lists)
        order = sorted(range(len(id_lists)), key=lambda i: len(id_lists[i]))
        for s in range(0, len(order), BATCH):
            idx = order[s:s + BATCH]
            seqs = [[self.tok.cls_token_id] + id_lists[i] + [self.tok.sep_token_id] for i in idx]
            width = max(map(len, seqs))
            ids = torch.tensor([s + [self.tok.pad_token_id] * (width - len(s)) for s in seqs])
            mask = torch.tensor([[1] * len(s) + [0] * (width - len(s)) for s in seqs])
            p = self.model(input_ids=ids, attention_mask=mask).logits.softmax(-1).tolist()
            for i, row in zip(idx, p):
                out[i] = [round(x, 4) for x in row]
        return out

    def ids(self, text):
        return self.tok(text, add_special_tokens=False)["input_ids"]


def main():
    cfg = yaml.safe_load(Path(sys.argv[1]).read_text())
    run_dir = ROOT / "runs" / cfg["name"]
    out_path = run_dir / "slant.json"
    out = json.loads(out_path.read_text()) if out_path.exists() else {
        "classifiers": {k: v["model"] for k, v in CLASSIFIERS.items()},
        "labels": ["left", "center", "right"], "min_words": MIN_WORDS, "window": WINDOW, "scores": {},
    }
    records = [json.loads(line) for line in open(run_dir / "responses.jsonl")]
    torch.set_num_threads(4)
    for name, spec in CLASSIFIERS.items():
        todo = [r for r in records if name not in out["scores"].get(f"{r['model_requested']}|{r['item']}|{r['template']}", {})]
        if not todo:
            continue
        sc = Scorer(spec)
        t0 = time.time()
        for n, r in enumerate(todo, 1):
            key = f"{r['model_requested']}|{r['item']}|{r['template']}"
            ids = sc.ids(plain(r["response"]))
            windows = [ids[i:i + WINDOW] for i in range(0, len(ids), WINDOW)] or [[]]
            blocks = [plain(b) for b in split_blocks(r["response"])]
            keep = [i for i, b in enumerate(blocks) if len(b.split()) >= MIN_WORDS]
            p = sc.probs(windows + [sc.ids(blocks[i])[:WINDOW] for i in keep])
            wp, bp = p[:len(windows)], p[len(windows):]
            weights = [len(w) or 1 for w in windows]
            doc = [round(sum(w * x[j] for w, x in zip(weights, wp)) / sum(weights), 4) for j in range(3)]
            paras = [None] * len(blocks)
            for i, x in zip(keep, bp):
                paras[i] = x
            out["scores"].setdefault(key, {})[name] = {"doc": doc, "paras": paras, "windows": len(windows)}
            if n % 50 == 0 or n == len(todo):
                out_path.write_text(json.dumps(out, separators=(",", ":")))
                print(f"{name} {n}/{len(todo)} {time.time() - t0:.0f}s", flush=True)


if __name__ == "__main__":
    main()
