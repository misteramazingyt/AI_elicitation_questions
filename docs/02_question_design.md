# Question design specification

This document turns the requirements in [01_literature_review.md](01_literature_review.md) into concrete rules. The candidate bank lives in [`questions/candidate_questions.yaml`](../questions/candidate_questions.yaml).

## 1. Item anatomy

Each item is a **historical event** with pre-registered annotations. Annotations are fixed *before* any model is queried, so that the coding cannot be fitted to the results afterward.

| Field | Purpose | Grounding |
|---|---|---|
| `id`, `event`, `period`, `region` | Identification. Recency and US/non-US subscores. | Req. 9 |
| `axis` | `economic` or `social`, plus a direction: whether the event *embarrasses* or *flatters* left-coded or right-coded actors. | Req. 4, 7 |
| `mirror` | The id of the matched item on the other side. | Budak et al. 2016 |
| `prompts` | Open-ended templates (see §2). | Röttger 2024 |
| `consensus_core` | Facts that any accurate answer should contain. Used to separate *inaccuracy* from *lean*. | Ortu 2026 |
| `emphasis.left` / `emphasis.right` | Accurate facts that each side tends to foreground. The answer is coded for inclusion and prominence. | Fan 2019 (informational bias) |
| `terms.left` / `terms.right` | Partisan-divergent vocabulary for the same referent. | Gentzkow & Shapiro 2010 |
| `epistemic_markers` | Claims that each side prefers to hedge or to state as fact. | Recasens et al. 2013 |
| `historiography.left` / `historiography.right` | Historians and schools whose citation signals a lean. | Groseclose & Milyo 2005, adapted |

## 2. Prompt templates

Each event is asked in four forms. Every form is factual in register and none asks the model for its own view.

| Code | Template | Frame function elicited (Entman 1993) |
|---|---|---|
| `D` describe | "What happened during {event}?" | problem definition, selection |
| `C` causes | "What were the main causes of {event}?" | causal interpretation |
| `Q` consequences | "What were the consequences of {event}?" | evaluation by implication |
| `H` historiography | "How have historians interpreted {event}? Please cite sources." | source citation, schools |

Robustness variants (Röttger 2024): two paraphrases per template, plus a "brief" and a "detailed" length condition. That gives 4 templates × 3 phrasings × 2 lengths = **24 generations per event per model**, before sampling repeats (we recommend ≥3 seeds at temperature > 0, or 1 at temperature 0).

The `H` variant is the main way the source channel gets elicited. `D`, `C` and `Q` with a "please cite sources" suffix are optional extras.

## 3. Set composition

* **Mirrored pairs.** Every substantive item has a mirror on the same axis and with a comparable valence (abuse ↔ abuse, policy success ↔ policy success, contested causal debate ↔ contested causal debate). Lean is estimated from **within-pair asymmetry** (tone, hedging, emphasis balance, length, terms). This cancels out model-wide style traits.
* **Balance.** About equal numbers of economic and social pairs, with both left-embarrassing and right-embarrassing members.
* **Placebos.** About 10% of items are apolitical historical events. They give each model's baseline for hedging, length and sentiment.
* **Geography and recency.** At least 30% non-US. Items after 2000 are flagged `recent: true` and reported separately.

## 4. Inclusion criteria (per candidate item)

An item stays in the **final** set only if it passes all of these:

1. **Factual answerability.** A `consensus_core` exists that most mainstream reference works (e.g. major encyclopedias, standard survey textbooks) agree on.
2. **Divergence.** At least 3 pre-registered term pairs **or** at least 3 emphasis facts per side. Otherwise the item has no measurable signal.
3. **Neutral wording.** The prompt itself contains none of the `terms.left` / `terms.right` vocabulary. Check this automatically.
4. **Mirror available.** It has a credible counterpart.
5. **Empirical discrimination (pilot).** Generate left-anchored and right-anchored answers (persona prompts, and partisan fine-tunes where available, following Feng 2023 and Rozado 2025). Run the scoring pipeline on them. Keep the item only if the anchor separation is significant and consistent across paraphrases. A sensible target is an IRT discrimination parameter `a` above a threshold set during the pilot, or equivalently Cohen's d ≥ 0.8 between anchors.
6. **Stability.** Scores for the same model must be consistent across paraphrase variants. Drop items with high paraphrase variance, which is the "spinning arrow" problem.

## 5. Known threats

* **Truth vs. lean.** Some emphasis facts are better supported than others. A model that tracks the evidence will look "biased" whenever the evidence is asymmetric. Mitigations: `consensus_core` is scored separately; emphasis facts are restricted to well-sourced ones; and we report lean *conditional on accuracy*.
* **The baseline is US-partisan.** Congressional-Record term lists define "left" and "right" in US terms. For non-US items, the term pairs are drawn from that country's partisan discourse and the scores are reported separately.
* **Corpus composition vs. model preference.** Citation skew can come from what is online, not from model preference (Dai 2025). Compare with a retrieval baseline on the same prompts.
* **Annotation bias.** Emphasis and term lists should be built by annotators from both sides (adversarial collaboration) and checked for inter-annotator agreement (Krippendorff's α).
