# Related Work & Research-Gap Analysis
**Paper under audit:** "Benchmark-audit layer for VLMEvalKit: 6 cheap post-processing detectors of benchmark pathologies" (target: NeurIPS 2026 TAI-Eval workshop, Sydney)
**Analysis date:** 2026-08-28

---

## 1) Verified citations table

All entries below were verified against arXiv abstract pages / ACL Anthology / OpenReview / official GitHub repos. None are fabricated.

| Key | Title | First author et al. | Venue / Year | arXiv |
|---|---|---|---|---|
| mmstar2024 | Are We on the Right Way for Evaluating Large Vision-Language Models? | Lin Chen et al. (11 authors) | NeurIPS 2024 (poster; OpenReview id evP9mxNNxJ) | 2403.20330 |
| hallusionbench2024 | HallusionBench: An Advanced Diagnostic Suite for Entangled Language Hallucination and Visual Illusion in Large Vision-Language Models | Tianrui Guan, Fuxiao Liu et al. | CVPR 2024 | 2310.14566 |
| northcutt2021pervasive | Pervasive Label Errors in Test Sets Destabilize Machine Learning Benchmarks | Curtis G. Northcutt, Anish Athalye, Jonas Mueller | NeurIPS 2021 Datasets & Benchmarks Track | 2103.14749 |
| mmluredux2024 | Are We Done with MMLU? | Aryo Pradipta Gema et al. (16 authors) | NAACL 2025 (aclanthology 2025.naacl-long.262) | 2406.04127 |
| naturalbench2024 | NaturalBench: Evaluating Vision-Language Models on Natural Adversarial Samples | Baiqi Li, Zhiqiu Lin et al. | NeurIPS 2024 (Datasets & Benchmarks) | 2410.14669 |
| vlmevalkit2024 | VLMEvalKit: An Open-Source Toolkit for Evaluating Large Multi-Modality Models | Haodong Duan et al. | ACM Multimedia 2024 (open-source track) | 2407.11691 |
| goyal2017vqa | Making the V in VQA Matter: Elevating the Role of Image Understanding in Visual Question Answering | Yash Goyal, Tejas Khot, Douglas Summers-Stay, Dhruv Batra, Devi Parikh | CVPR 2017 | 1612.00837 |
| vendrow2025platinum | Do Large Language Model Benchmarks Test Reliability? | Joshua Vendrow, Edward Vendrow, Sara Beery, Aleksander Madry | arXiv Feb 2025 (MadryLab "platinum benchmarks"; OpenReview under title "Large Language Model Benchmarks Do Not Test Reliability") | 2502.03461 |

Notes on the user's assumptions:
- **PlatinumBench actual title confirmed:** "Do Large Language Model Benchmarks Test Reliability?" — the project name is "platinum benchmarks" (github.com/MadryLab/platinum-benchmarks). An OpenReview page exists under the variant title "Large Language Model Benchmarks Do Not Test Reliability"; I could not confirm a specific conference acceptance, so the .bib cites arXiv.
- **MMStar venue:** NeurIPS 2024 confirmed via neurips.cc virtual poster page + official GitHub ("[NeurIPS 2024]").
- **MMLU-Redux venue:** NAACL 2025 Long Papers, confirmed via ACL Anthology.

Additional verified citations used for positioning (all confirmed via primary sources):

| Key | Title | First author | Venue / Year | arXiv |
|---|---|---|---|---|
| zheng2024selectors | Large Language Models Are Not Robust Multiple Choice Selectors | Chujie Zheng et al. | ICLR 2024 (Spotlight) | 2309.03882 |
| mmbench2024 | MMBench: Is Your Multi-modal Model an All-around Player? | Yuan Liu et al. | ECCV 2024 (arXiv 2307.06281) | 2307.06281 |
| lmmseval2024 | LMMs-Eval: Reality Check on the Evaluation of Large Multimodal Models | (EvolvingLMMs-Lab) | arXiv Jul 2024 | 2407.12772 |
| mmevalpro2024 | MMEvalPro: Calibrating Multimodal Benchmarks Towards Trustworthy and Efficient Evaluation | Jinsheng Huang, Liang Chen et al. | arXiv 2024 | 2407.00468 |
| mmdetect2024 | Both Text and Images Leaked! A Systematic Analysis of Data Contamination in Multimodal LLM | Dingjie Song et al. | arXiv Nov 2024 | 2411.03823 |
| redundancy2025 | Redundancy Principles for MLLMs Benchmarks | Zicheng Zhang et al. | ACL 2025 (aclanthology 2025.acl-long.612) | 2501.13953 |
| datbench2026 | DatBench: Discriminative, Faithful, and Efficient VLM Evaluations | Siddharth Joshi, Haoli Yin et al. (DatologyAI, 31 authors) | arXiv Jan 2026 | 2601.02316 |
| fantasticbugs2025 | Fantastic Bugs and Where to Find Them in AI Benchmarks | Sang Truong, Yuheng Tu et al. (Stanford) | arXiv Nov 2025 | 2511.16842 |
| benchmarker2026 | BenchMarker: An Education-Inspired Toolkit for Highlighting Flaws in Multiple-Choice Benchmarks | Nishant Balepur et al. | arXiv Feb 2026 | 2602.06221 |
| rosenthal2025unexplored | Unexplored Flaws in Multiple-Choice VQA Evaluations | Fabio Rosenthal et al. | arXiv Nov 2025 | 2511.22341 |
| visualignorance2026 | Diagnosing Visual Ignorance in Vision-Language Models | Runyu Zhou et al. | arXiv Jun 2026 | 2606.06890 |
| seeorguess2026 | Do Vision-Language Models See or Guess? Measuring and Reducing Textual-Prior Reliance with a Phrasing-Controlled Benchmark | Pratham Singla et al. | arXiv Jun 2026 | 2606.10400 |

---

## 2) Closest neighbors (ranked by proximity)

**#1 — DatBench (arXiv 2601.02316, Jan 2026). CLOSEST / RED FLAG.**
What it does: audits 33 VLM datasets across 9 capabilities; finds blindly-solvable questions up to 70% of some evaluations and mislabeled/ambiguous samples up to 42%; shows MCQ-to-generative conversion drops scores up to 35%; releases a cleaned suite (DatBench-Full) plus a discriminative fast subset (13x average speedup).
Difference: DatBench's deliverable is *curated replacement datasets*; the audited project's deliverable is a *reusable audit layer inside VLMEvalKit* that any user can re-run on their own prediction artifacts for any benchmark/model set. Honest caveat: the headline empirical findings (blind-solvability + label-error rates in popular VLM benchmarks) substantially overlap; DatBench's scale (33 datasets) exceeds the 2-benchmark case study. The findings are NOT novel; the mechanism/packaging arguably is.

**#2 — Fantastic Bugs and Where to Find Them in AI Benchmarks (arXiv 2511.16842, Nov 2025). RED FLAG.**
What it does: statistical analysis of model response patterns (measurement-theoretic signals; secondary sources indicate Fleiss' kappa and ensemble anomaly scores were among methods compared, e.g. on GSM8K) to flag potentially invalid questions in nine widely used benchmarks, at up to 84% precision, with an LLM-judge first pass.
Difference: same "cheap post-processing over model responses to flag bad items" philosophy, but on text LLM benchmarks, not multimodal — no blind/full visual-dependency contrast, no image-specific pathologies, and not integrated into an eval toolkit. The consensus/agreement-based label-error detector in the audited project must be positioned as a multimodal instantiation, not an invention.

**#3 — BenchMarker (arXiv 2602.06221, Feb 2026). RED FLAG.**
What it does: an education-inspired *toolkit* using LLM judges to flag three MCQ flaws — contamination, shortcut cues in choices, writing errors (19-rule rubric) — audits 12 benchmarks (e.g., predicts 47% of TruthfulQA appears online; 100% of HellaSwag violates writing rules) and shows flaws shift rankings.
Difference: text-only MCQ benchmarks and LLM-judge-based rubric detection, vs. the audited project's behavioral detectors (blind runs, consensus, kappa, position stats) on multimodal benchmarks. Overlap in "toolkit that flags benchmark flaws" framing — the paper cannot claim to be the first such toolkit.

**#4 — MMStar itself (Chen et al., NeurIPS 2024).**
What it does: the audited paper's own case-study benchmark was *built* by running LLMs without images and detecting leakage — i.e., the visual-dependency detector is MMStar's own construction method, applied post-hoc. The blind-run methodology is 2024 prior art (also Goyal et al. 2017 for VQA language priors; MMEvalPro 2024 showed blind LLMs score non-trivially on MCQ multimodal benchmarks).
Difference: the audited project turns this one-off curation analysis into a standing toolkit feature and — importantly — shows MMStar itself still contains ~20% blind-solvable items despite being curated for vision-indispensability. That reflexive result is genuinely new and is the paper's best headline.

**#5 — MMLU-Redux (NAACL 2025) + Platinum Benchmarks (2025) + Northcutt et al. (NeurIPS 2021).**
What they do: establish that label errors are pervasive and destabilize rankings (Northcutt: cross-model confident learning; MMLU-Redux: manual re-annotation; Platinum: careful curation to minimize label error/ambiguity).
Difference: all are text/unimodal or general-ML, and none run inside a multimodal eval harness; the audited project's model-consensus-vs-ground-truth detector is a direct, cheaper, automated analogue for VLM benchmarks. Cite as intellectual ancestors, not competitors.

Also relevant (briefer):
- **Zheng et al., ICLR 2024 (2309.03882):** selection/position bias in MCQ LLMs + PriDe debiasing — prior art for the answer-position detector (text-only).
- **MMBench (ECCV 2024, 2307.06281):** CircularEval rotates answer positions in VLM MCQ — position bias is already operationalized in a major VLM benchmark's own protocol.
- **Rosenthal et al. 2025 (2511.22341):** MCQ VQA highly sensitive to semantically neutral prompt-format changes (7 MLLMs, 5 datasets, 48 format variants) — direct prior art for the "conclusions are sensitive to answer-extraction/judge protocol" claim.
- **MM-Detect (2411.03823):** multimodal contamination detection incl. an Option Order Sensitivity Test — overlaps with position-bias detection, framed as contamination.
- **Redundancy Principles (ACL 2025, 2501.13953):** cross-benchmark redundancy computed from existing score matrices of hundreds of MLLMs — same "mine artifacts you already have" spirit, different pathology (redundancy, not validity).
- **Diagnosing Visual Ignorance (2606.06890, Jun 2026):** progressive Gaussian-blur decay metric over 12 VQA benchmarks, 3 VLMs; separately-reported text-only inspector results show e.g. AI2D 66.7% text-only accuracy — concurrent audit of visual dependency of *existing* benchmarks.
- **Do VLMs See or Guess? (2606.10400, Jun 2026):** phrasing-controlled new benchmark + no-image ablations; measures and trains away textual-prior reliance — concurrent, but builds a new benchmark rather than auditing existing ones.
- **LMMs-Eval (2407.12772):** the other major toolkit; its "reality check" concerns coverage/cost/contamination (LiveBench), not a per-item audit layer — supports the claim that toolkits lack audit layers.

---

## 3) Concurrent-work threats 2024-2026 (summary judgment)

| Detector in the audited paper | Prior/concurrent art | Threat level |
|---|---|---|
| Visual dependency via full-vs-blind runs | Goyal 2017; MMStar 2024 (construction method); MMEvalPro 2024; DatBench 2026 (70% blind-solvable); Visual Ignorance 2026; See-or-Guess 2026 | HIGH — finding is well established; only the MMStar-specific ~20% reflexive number and toolkit packaging are new |
| Model-consensus vs ground truth (label errors) | Northcutt 2021; MMLU-Redux 2024/25; Platinum 2025; DatBench 2026 (42% mislabeled/ambiguous in some sets); Fantastic Bugs 2025 | HIGH for the idea; MEDIUM for the multimodal, in-toolkit instantiation; the ~18% MMStar consensus-contradicts-GT number appears not previously reported |
| Inter-model Fleiss' kappa agreement | Fantastic Bugs 2025 (agreement-style signals on LLM benchmarks); general IRR literature | MEDIUM — not previously applied as a VLM-benchmark item-quality signal, as far as found |
| Answer-position distribution bias | Zheng 2024 (ICLR); MMBench CircularEval; MM-Detect option-order test | HIGH for the phenomenon; LOW for "as a cheap audit statistic over saved artifacts" |
| Near-duplicate distractors | No direct multimodal prior found (BenchMarker's "shortcut cues in choices" is nearest, text-only, LLM-judge-based) | LOW — most novel detector |
| Judge/answer-extraction protocol sensitivity | Rosenthal 2025 (prompt-format sensitivity in MCQ VQA); extraction-strategy discussions in VLMEvalKit/lmms-eval | MEDIUM-HIGH — treat as confirmation on new benchmarks, not discovery |

**No paper found that does the exact combination:** a unified, multi-detector audit layer integrated into a mainstream VLM evaluation toolkit (VLMEvalKit or lmms-eval), running purely as post-processing over prediction artifacts the toolkit already saves, with per-benchmark audit reports. Searched explicitly for "VLMEvalKit audit", "lmms-eval audit layer", "benchmark audit" + VLM — nothing matching.

---

## 4) Gap verdict

**The gap is real but narrower than the current claim implies.**

- **Threatened:** any claim that the *pathologies themselves* are newly discovered. Blind-solvability of VLM benchmarks (incl. at large scale — DatBench, Jan 2026), label errors detectable via models, position bias, and protocol sensitivity are all published, some in 2024. DatBench in particular preempts the two headline phenomena (blind-solvable %, mislabeled %) at 33-dataset scale. If a reviewer knows DatBench, a framing of "we discover that VLM benchmarks are text-solvable and mislabeled" dies on contact.
- **Safe:** (a) the *systems contribution* — a reusable audit layer shipped inside VLMEvalKit, costing ~zero extra inference because it re-reads artifacts the toolkit already saves (only the blind run adds inference, and it's text-only); (b) the *reflexive case-study numbers* — ~20% of MMStar (a benchmark explicitly curated to be vision-indispensable) still blind-solvable, ~18% consensus-vs-GT conflicts on MMStar, and HallusionBench results — none of these specific numbers were found elsewhere; (c) the near-duplicate-distractor detector; (d) Fleiss' kappa as a per-item multimodal audit signal; (e) the demonstration that audit conclusions themselves flip with the extraction/judge protocol — a meta-point Rosenthal et al. make for accuracy, not for audit outcomes.
- **Workshop fit:** for TAI-Eval this is fine — workshops reward practical infrastructure + honest replication/extension. But the related-work section must cite DatBench, Fantastic Bugs, and BenchMarker as concurrent and state differences precisely, or reviewers will do it for you.

## 5) Recommended positioning paragraph (adapt into the paper)

> A growing body of work documents pathologies of multimodal benchmarks: many items are solvable without the image [MMStar; MMEvalPro; DatBench], ground-truth labels are frequently wrong [Northcutt; MMLU-Redux; Platinum; DatBench], multiple-choice formats carry position and selection biases [Zheng; MMBench; MM-Detect], and reported accuracies are sensitive to prompt and extraction protocols [Rosenthal]. Prior responses to these findings have been to build cleaner replacement benchmarks [MMStar; NaturalBench; Platinum; DatBench] or standalone flaw-flagging pipelines for text-only MCQ benchmarks [Fantastic Bugs; BenchMarker]. We take a complementary, infrastructure-first view: rather than releasing another cleaned dataset, we integrate a suite of six pathology detectors directly into a widely used evaluation toolkit (VLMEvalKit), operating as cheap post-processing over the prediction artifacts such toolkits already persist, so that every evaluation run can double as a benchmark audit. Applied to MMStar and HallusionBench, this layer shows that even a benchmark explicitly curated for vision-indispensability retains ~20% blind-solvable items and ~18% items where cross-model consensus contradicts the gold label — and that these audit conclusions themselves shift under different answer-extraction and judge protocols, arguing for audit reports to accompany leaderboard numbers as a matter of course.

Against the 3 closest works, the one-line differentiators:
- vs **DatBench**: they sell cleaned datasets; we sell the audit machinery, embedded where evaluations already happen, reusable on any benchmark and model set (and we corroborate their findings independently on MMStar/HallusionBench).
- vs **Fantastic Bugs**: same response-pattern-mining philosophy, but multimodal (blind-vs-full contrast is impossible in their text-only setting) and toolkit-integrated rather than standalone.
- vs **BenchMarker**: they use LLM judges + an education rubric on text MCQs; our detectors are behavioral (model responses), multimodal, and free of an additional judge model except where we explicitly study judge sensitivity.

## 6) Queries run and where

**paper-search MCP (search_arxiv):** "Are We on the Right Way for Evaluating Large Vision-Language Models"; "HallusionBench image-context reasoning hallucination benchmark"; "Pervasive Label Errors in Test Sets Destabilize Machine Learning Benchmarks"; "Are We Done with MMLU"; "NaturalBench vision-language models natural adversarial samples"; "VLMEvalKit toolkit evaluating large multi-modality models"; "Making the V in VQA Matter elevating image understanding"; "Do Large Language Model Benchmarks Test Reliability platinum"; "blind evaluation vision language models answer without images benchmark"; "benchmark audit multimodal evaluation label errors detection"; "MMEvalPro calibrating multimodal benchmarks trustworthy evaluation"; "selection bias multiple choice large language models robust selectors position"; "answer extraction LLM judge choice extraction multimodal evaluation sensitivity"; "large language models are not robust multiple choice selectors selection bias". (Several MCP queries returned noisy results; findings were cross-checked via WebFetch of arXiv abstract pages.)

**WebSearch:** '"benchmark audit" vision-language evaluation VLM 2025 arxiv'; 'VLM benchmark "without the image" text-only solvable questions 2025 audit'; 'lmms-eval OR VLMEvalKit "reality check" evaluation large multimodal models arxiv'; 'multimodal benchmark label errors "model consensus" ground truth wrong annotations 2025 VLM arxiv'; 'openreview NeurIPS 2025 datasets benchmarks track multimodal benchmark quality audit blind text-only'; '"answer extraction" OR "choice extraction" protocol sensitivity multiple-choice VLM MLLM evaluation LLM judge rankings change arxiv'; '"Redundancy Principles" MLLM benchmarks arxiv 2501'; '"MM-Detect" multimodal data contamination benchmark leaked arxiv'; '"visual dependency" multimodal benchmark blind LLM text-only MMStar follow-up 2025 2026'; 'benchmark quality control toolkit LLM evaluation "post-hoc" detect flawed questions position bias duplicates 2025'; 'Fleiss kappa inter-model agreement LLM ensemble detect mislabeled benchmark questions'; 'MMStar "Are We on the Right Way..." NeurIPS 2024 accepted'; '"Are We Done with MMLU" NAACL 2025 MMLU-Redux venue'; '"Do Large Language Model Benchmarks Test Reliability" Vendrow platinum benchmarks ICML 2025'; '"BenchMarker" "Education-Inspired Toolkit" multiple-choice benchmarks arxiv authors'.

**WebFetch (primary-source verification):** arXiv abs pages for 2403.20330, 1612.00837, 2601.02316, 2309.03882, 2606.10400, 2511.16842, 2606.06890, 2511.22341.

**Not found despite searching:** any existing "audit layer" for VLMEvalKit or lmms-eval; any multimodal near-duplicate-distractor detector; any prior report of the specific MMStar ~20%/~18% figures.

**UNVERIFIED / excluded from .bib:** exact conference venues for MMEvalPro, MM-Detect, LMMs-Eval, DatBench, Fantastic Bugs, BenchMarker, and the two June-2026 preprints (cited as arXiv preprints); a conference acceptance for Vendrow et al. (cited as arXiv).
