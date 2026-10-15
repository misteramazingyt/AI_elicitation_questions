# Literature review: measuring political lean from text that isn't opinion

The question this review answers is narrow. **Which published methods can tell us the political lean of a text whose explicit content is meant to be factual?** Their designs then constrain how we write the questions in this repository.

We cannot ask a model for its opinions (Political Compass style). So we have to rely on methods that find lean in *how* facts are presented: word choice, which facts are selected and stressed, which causes are named, and which sources are cited.

**Verification status.** Entries marked ✅ were checked online when this review was drafted (2026-10). Entries marked 📚 are standard references in the field, cited from the canonical literature. Check their bibliographic details before any formal write-up.

---

## A. Why we avoid opinion surveys (motivation)

| Source | Finding relevant to us |
|---|---|
| ✅ Röttger et al. (2024), "Political Compass or Spinning Arrow? Towards More Meaningful Evaluations for Values and Opinions in LLMs," *ACL 2024* (arXiv 2402.16786) | Forced multiple-choice results from the Political Compass Test are unstable. They change when the forcing is removed, when the forcing method changes, and when items are paraphrased. Open-ended answers differ again. **Implication:** use open-ended, realistic prompts, test robustness to paraphrase, and don't force a format. |
| ✅ Rozado (2024), "The political preferences of LLMs," *PLOS ONE* | Political orientation tests given to 24 chat LLMs mostly come out left of center. Base models do not. Rozado also notes that the tests carry their own calibration biases. **Implication:** survey instruments are a weak foundation, which motivates indirect measures. |
| ✅ Rozado (2025), "Measuring Political Preferences in AI Systems: An Integrative Approach" (arXiv 2503.10649; Manhattan Institute) | Combines four methods into one score: (1) similarity of the AI's language to Republican vs. Democratic members of Congress, (2) lean of the policy recommendations it gives, (3) sentiment toward politically affiliated figures, (4) orientation tests. **Implication:** the closest precedent for a multi-channel, mostly indirect pipeline. Channel (1) is the lexical method we adapt below. |
| 📚 Santurkar et al. (2023), "Whose Opinions Do Language Models Reflect?" *ICML* (OpinionQA) | Compares LM answer distributions with US demographic groups' survey answers. Useful as a validity contrast, but it is still an opinion instrument. |
| 📚 Feng et al. (2023), "From Pretraining Data to Language Models to Downstream Tasks: Tracking the Trails of Political Biases," *ACL* | Shows that partisan pretraining corpora shift a model's measured lean. This supports using partisan-steered anchors to validate our measures (see §E). |

## B. Channel 1: articulation / lexical slant

| Source | Method | What we take from it |
|---|---|---|
| 📚 Gentzkow & Shapiro (2010), "What Drives Media Slant?" *Econometrica* 78(1) | Find two- and three-word phrases that predict a legislator's party in the *Congressional Record* (e.g. "death tax" vs. "estate tax"). Score a newspaper by how often it uses each side's phrases. | The core lexical method. Our questions must make the model talk about topics **where partisan vocabularies diverge**, or there is nothing for this channel to measure. |
| 📚 Gentzkow, Shapiro & Taddy (2019), "Measuring Group Differences in High-Dimensional Choices," *Econometrica* | A penalized, bias-corrected way to measure partisanship of speech, avoiding small-sample overstatement. | The estimator to use when we score phrase use. |
| 📚 Greenstein & Zhu (2012), "Is Wikipedia Biased?" *AEA Papers & Proceedings*; (2018) *MIS Quarterly* | Applies Gentzkow-Shapiro phrases to Wikipedia articles, which aim to be encyclopedic and factual. | **The most direct precedent.** It shows that lexical slant can be measured in text whose stated purpose is neutral factual exposition, which is exactly our setting. |
| 📚 Laver, Benoit & Garry (2003), "Extracting Policy Positions from Political Texts Using Words as Data," *APSR* (Wordscores) | Scales a new text against reference texts with known positions. | A supervised scaler. Our reference texts can be anchor answers with known lean (see §E). |
| 📚 Slapin & Proksch (2008), "A Scaling Model for Estimating Time-Series Party Positions from Texts," *AJPS* (Wordfish) | An unsupervised Poisson scaling model. | A robustness check that needs no anchors. |
| 📚 Recasens, Danescu-Niculescu-Mizil & Jurafsky (2013), "Linguistic Models for Analyzing and Detecting Biased Language," *ACL* | Learns from Wikipedia NPOV edits and separates **framing bias** (loaded words) from **epistemological bias** (factive verbs, hedges, assertives such as "claimed" vs. "stated" vs. "revealed"). | Gives us a second lexical sub-channel: *epistemic stance*, meaning which claims the model hedges and which it presents as fact. Questions need a balance of claims each side prefers to hedge. |
| ✅ Bang, Chen, Lee & Fung (2024), "Measuring Political Bias in LLMs: What Is Said and How It Is Said," *ACL 2024* (arXiv 2403.18932) | Two tiers: stance, measured by similarity to two opposed "extreme anchor" texts, plus framing bias in content and in style (lexical polarity). | Confirms that content and style are separate channels in LLM output. The anchor-comparison method carries over directly to our scoring. |
| 📚 Gentzkow-Shapiro-style moral lexicons, e.g. the Moral Foundations Dictionary (Graham, Haidt & Nosek 2009, *JPSP*) | Liberals and conservatives weight moral foundations differently. | An optional lexical feature: which moral vocabulary (harm/fairness vs. loyalty/authority/sanctity) the model uses to describe the same event. |

## C. Channel 2: selection and emphasis (informational bias and framing)

| Source | Method | What we take from it |
|---|---|---|
| ✅ Fan et al. (2019), "In Plain Sight: Media Bias Through the Lens of Factual Reporting," *EMNLP* (BASIL dataset) | Defines **informational bias**: factual but tangential, speculative or background material chosen to sway readers. It was **more frequent than lexical bias** in the news triplets they annotated. | **Central to our design.** A model can be fully accurate and still lean through what it includes. Questions should leave room for selection, e.g. "what were the causes and consequences" rather than "what year". For each question we pre-register the facts each side tends to stress so that inclusion can be coded. |
| 📚 Entman (1993), "Framing: Toward Clarification of a Fractured Paradigm," *Journal of Communication* | Frames do four things: define the problem, interpret causes, evaluate morally, and recommend treatment. | Our question templates (description / causes / consequences / historiography) are built to bring out these functions without asking for an opinion. |
| 📚 Card et al. (2015), "The Media Frames Corpus," *ACL* | 15 generic policy frames (economic, morality, fairness, legality, security, and so on). | A coding scheme for which frame dominates an answer. |
| 📚 Budak, Goel & Rao (2016), "Fair and Balanced? Quantifying Media Bias through Crowdsourced Content Analysis," *Public Opinion Quarterly* | Separates **issue-selection** bias from **presentation** bias. Bias shows up mostly in how stories critical of each party are treated. | Supports **mirrored question pairs**: matched events that embarrass or favor each side, so that asymmetric treatment shows. |
| 📚 Puglisi & Snyder (2011), "Newspaper Coverage of Political Scandals," *Journal of Politics* | Outlets give more coverage to scandals involving the opposing party. | Same logic: compare the depth and tone of answers about matched scandals and abuses on each side. |
| 📚 Hamborg, Donnay & Gipp (2019), "Automated identification of media bias in news articles: an interdisciplinary literature review," *Int. J. Digital Libraries* | A taxonomy: commission/omission, labeling and word choice, source selection, placement, size allocation, and more. | A checklist of features for the pipeline. |
| ✅ Yoo & Shin (2025), "Fair or Framed? Political Bias in News Articles Generated by LLMs," *EMNLP 2025* (authors per the conference listing) | Left-leaning bias persists in LLM-generated news even under balanced settings. 33–38% of quotations were "stance-flipped." | LLM framing bias shows up in generated factual-genre text. Supports measuring framing rather than stated opinion. |

## D. Channel 3: sources cited

| Source | Method | What we take from it |
|---|---|---|
| 📚 Groseclose & Milyo (2005), "A Measure of Media Bias," *QJE* 120(4) | Scores outlets by which think tanks they cite, compared with the think tanks members of Congress cite. | **The canonical citation-based slant method.** Questions must invite citation, for example with a variant that asks for sources or further reading. Each cited source is then mapped to a lean using an external rating (AllSides, Ad Fontes, or a Groseclose-Milyo-style congressional citation baseline). |
| ✅ Dai et al. (2025), "Media Source Matters More Than Content: Unveiling Political Bias in LLM-Generated Citations," *EMNLP 2025* | LLMs cite left-leaning outlets more than BM25 or dense retrievers do. They can identify an outlet's lean almost perfectly from its name, but not from its content. | Direct evidence that the cited-source channel carries signal in LLMs, separately from content. We need a **retrieval baseline** for comparison so that we don't mistake the composition of the corpus for model bias. |
| History-specific note | Historiographical citation | For historical questions, the "sources" are often historians and schools (for example Conquest vs. revisionist scholarship on Soviet history, or Dunning School vs. Foner on Reconstruction). **We need a hand-built map from historian/school to political valence, per question.** No general-purpose rating exists for this. It is the main original contribution this project has to make. |

## E. LLM-specific designs for contested history

| Source | Relevance |
|---|---|
| ✅ Ortu et al. (2026), "Preserving Historical Truth: Detecting Historical Revisionism in LLMs," *ICLR 2026* (arXiv 2602.17433), HistoricalMisinfo | 500 contested events from 45 countries, each with a factual narrative and a documented revisionist narrative. Each event is posed in 11 prompt scenarios. LLM-as-judge scores relative alignment to the two references. The authors note that revisionism shows up mainly as omission and selective emphasis. **Implication:** this validates the reference-pair design. We adapt it from "factual vs. revisionist" to "left-coded vs. right-coded emphasis, both factual." We can also mine the dataset for events. |
| ✅ arXiv 2506.06751 (2025): geopolitical bias across 55 conflicts / 109 events (USA, UK, China, USSR/Russia) | Neutral description plus two national viewpoints per event. It shows that historical events can be posed so that a model's alignment with competing narratives is measurable. |
| ✅ Faulborn et al. (2025), "Only a Little to the Left: A Theory-grounded Measure of Political Bias in LLMs" | A theory-grounded alternative to the PCT. Use it to check convergent validity. |
| 📚 Grimmer & Stewart (2013), "Text as Data: The Promise and Pitfalls of Automatic Content Analysis Methods for Political Texts," *Political Analysis* | "Validate, validate, validate." Any automated measure has to be checked against texts of known position. |

---

## Synthesis: requirements for our question set

1. **Open-ended and realistic** (Röttger 2024). Use natural questions a user might ask, with no forced choice, and with paraphrase variants.
2. **Lexically divergent topics** (Gentzkow & Shapiro 2010; Greenstein & Zhu 2012). Each question must touch an event where the left and right use different vocabularies. We pre-register those term pairs.
3. **Room for selection** (Fan 2019; Entman 1993). Questions ask for causes, consequences and historiography, not only dates. For each question we pre-register the facts each side tends to stress.
4. **Mirrored pairs** (Budak et al. 2016; Puglisi & Snyder 2011). Every left-embarrassing event has a matched right-embarrassing one, and the same for left-flattering and right-flattering events. Lean is then the *asymmetry within a pair*, which cancels out model-wide traits such as general hedging or verbosity.
5. **Citation-eliciting variants** (Groseclose & Milyo 2005; Dai 2025). Each question has a "with sources" variant, scored against outlet ratings and a historian/school map, compared with a retrieval baseline.
6. **Placebo controls** (Grimmer & Stewart 2013). Apolitical historical questions give a per-model baseline for style, hedging and length.
7. **Two axes.** The compass needs an economic (left–right) axis and a social (libertarian–authoritarian) axis. Each item is tagged with the axis it mainly loads on.
8. **Empirical item validation** (Bang 2024 anchors; Feng 2023; Laver et al. 2003). Before the final set is fixed, each candidate is run with **left-anchored and right-anchored generations** (e.g. "answer as a progressive historian" / "as a conservative historian," or models fine-tuned on partisan data). Only items whose pipeline scores separate the anchors reliably are kept, using item discrimination as in IRT. A question that does not separate known-lean answers cannot measure an unknown one.
9. **Mind recency and geography.** The lexical baselines (the Congressional Record) are US-centric. Recent events mix lean with differences in training cutoff. Tag both, and report US/non-US and pre-/post-2000 subscores.
