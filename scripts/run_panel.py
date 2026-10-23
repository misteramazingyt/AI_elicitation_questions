"""Ask every candidate prompt to every model in a panel via OpenRouter.

Usage: OPENROUTER_API_KEY=... python3 scripts/run_panel.py runs/panel_v0.1.yaml [--models id ...] [--workers N]

Each response is saved to runs/<panel>/<model-slug>/<item>_<template>.json. Existing
complete responses are skipped, so the script can be re-run to resume or fill gaps;
responses cut off at max_tokens are asked again.
"""
import argparse
import concurrent.futures as cf
import json
import os
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

import yaml

from render_questions_md import ROOT, TEMPLATES

URL = "https://openrouter.ai/api/v1/chat/completions"


def prompts():
    items = yaml.safe_load((ROOT / "questions" / "candidate_questions.yaml").read_text())["items"]
    for it in items:
        for code, tpl in TEMPLATES.items():
            yield it["id"], code, tpl.format(e=it["event_phrase"])


def call(cfg, model, prompt, key):
    messages = ([{"role": "system", "content": cfg["system_prompt"]}] if cfg.get("system_prompt") else [])
    body = {
        "model": model,
        "messages": messages + [{"role": "user", "content": prompt}],
        "temperature": cfg["temperature"],
        "max_tokens": cfg["max_tokens"],
        "reasoning": cfg["reasoning"],
        "usage": {"include": True},
    }
    req = urllib.request.Request(URL, json.dumps(body).encode(), {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "X-Title": "AI elicitation questions",
    })
    for attempt in range(6):
        try:
            with urllib.request.urlopen(req, timeout=300) as r:
                data = json.loads(r.read())
            if "error" in data:
                raise RuntimeError(json.dumps(data["error"]))
            if not (data["choices"][0]["message"].get("content") or "").strip():
                raise RuntimeError("empty content (finish_reason=%s)" % data["choices"][0].get("finish_reason"))
            return data
        except urllib.error.HTTPError as e:
            err = f"HTTP {e.code}: {e.read()[:500].decode(errors='replace')}"
            if e.code in (400, 401, 402, 403, 404):
                raise RuntimeError(err)
        except Exception as e:  # network errors, timeouts, empty or errored completions
            err = str(e)
        time.sleep(2 ** attempt * 3)
    raise RuntimeError(err)


def run_one(cfg, out_dir, model, item, code, prompt, key):
    path = out_dir / f"{item}_{code}.json"
    if path.exists() and json.loads(path.read_text())["finish_reason"] != "length":
        return "skip", path
    started = datetime.now(timezone.utc).isoformat()
    data = call(cfg, model, prompt, key)
    choice = data["choices"][0]
    record = {
        "item": item, "template": code, "prompt": prompt,
        "model_requested": model, "model_served": data.get("model"), "provider": data.get("provider"),
        "response": choice["message"]["content"], "finish_reason": choice.get("finish_reason"),
        "usage": data.get("usage"), "started_at": started,
        "params": {k: cfg[k] for k in ("temperature", "max_tokens", "reasoning", "system_prompt")},
    }
    path.write_text(json.dumps(record, ensure_ascii=False, indent=1))
    return "ok", path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("panel")
    ap.add_argument("--models", nargs="*")
    ap.add_argument("--workers", type=int, default=8)
    args = ap.parse_args()
    key = os.environ["OPENROUTER_API_KEY"]
    cfg = yaml.safe_load(Path(args.panel).read_text())
    models = [m["id"] for m in cfg["models"] if not args.models or m["id"] in args.models]
    run_dir = ROOT / "runs" / cfg["name"]
    jobs = []
    for model in models:
        out_dir = run_dir / model.replace("/", "__").replace(":", "_")
        out_dir.mkdir(parents=True, exist_ok=True)
        jobs += [(out_dir, model, *p) for p in prompts()]

    counts = {"ok": 0, "skip": 0, "fail": 0}
    with cf.ThreadPoolExecutor(args.workers) as pool:
        futs = {pool.submit(run_one, cfg, j[0], *j[1:], key): j for j in jobs}
        for f in cf.as_completed(futs):
            _, model, item, code, _ = futs[f]
            try:
                status, _ = f.result()
                counts[status] += 1
            except Exception as e:
                counts["fail"] += 1
                print(f"FAIL {model} {item}_{code}: {e}", file=sys.stderr, flush=True)
            done = sum(counts.values())
            if done % 50 == 0:
                print(f"{done}/{len(jobs)} {counts}", flush=True)
    print(f"done {counts}")
    return 1 if counts["fail"] else 0


if __name__ == "__main__":
    sys.exit(main())
