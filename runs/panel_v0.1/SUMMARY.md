# Run panel_v0.1

Every prompt in `questions/QUESTIONS.md` (42 events × 4 templates = 168 prompts) asked once to each model via OpenRouter, temperature 0, no system prompt, reasoning effort `low`. Panel config: [`../panel_v0.1.yaml`](../panel_v0.1.yaml).

Raw responses are in one folder per model (`<item>_<template>.json`) and merged in `responses.jsonl`.

| Model | Lab | Responses | Mean words | Truncated | Cost (USD) |
|---|---|---|---|---|---|
| `openai/gpt-6-luna` | OpenAI | 168/168 | 344 | 0 | 0.059 |
| `anthropic/claude-haiku-5.5` | Anthropic | 168/168 | 545 | 0 | 0.141 |
| `google/gemini-3.1-flash-lite` | Google | 168/168 | 727 | 0 | 0.289 |
| `x-ai/grok-4.3` | xAI | 168/168 | 432 | 0 | 0.475 |
| `meta-llama/llama-4-maverick` | Meta | 168/168 | 488 | 0 | 0.076 |
| `deepseek/deepseek-v4.1-flash` | DeepSeek | 168/168 | 498 | 1 | 0.363 |
| `qwen/qwen3.7-plus` | Alibaba | 168/168 | 831 | 0 | 0.562 |
| `mistralai/mistral-large-2512` | Mistral | 168/168 | 971 | 0 | 0.442 |
| `z-ai/glm-5.3-flash` | Zhipu | 168/168 | 400 | 0 | 0.020 |
| `nvidia/nemotron-3-ultra-550b-a55b:free` | NVIDIA | 168/168 | 1170 | 0 | 0.000 |

Total cost of the kept responses: $2.43.

`max_tokens` (which counts reasoning tokens) was raised during the run (4000 → 16000). Responses that hit the lower cap were asked again; each record's `params` holds the cap it ran under.

Still truncated at the final cap: `deepseek/deepseek-v4.1-flash` S04_H.
