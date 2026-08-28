# vlm-bench: Benchmark Audit Layer for VLM Evaluation

**Audit the benchmark, not just the model.** This repository is a research
fork of [VLMEvalKit](https://github.com/open-compass/VLMEvalKit) that adds a
**benchmark-audit layer**: a set of detectors that reuse the standard
artifacts of VLM evaluation — the per-question prediction/eval files the
toolkit already saves — to diagnose the quality of the *benchmark itself*:

- questions solvable **without the image** (full-vs-blind runs);
- likely **annotation errors** (cross-model consensus vs. the gold label);
- unstable/ambiguous items (inter-model **Fleiss' κ**);
- **answer-position bias** and **near-duplicate distractors** in MCQ options.

The audit runs as a single command over existing outputs and emits a
per-question report with severity levels, plus a reproducibility manifest
(git commit, CLI args, generation parameters). Only the blind run adds any
inference cost — and it is text-only.

> Preliminary case study (MMStar, 3 models, fixed pipeline): **20.2%** of
> questions are answered identically by all models with and without the
> image; on **23.9%** of questions a model consensus contradicts the gold
> label (134 unanimously); switching the answer-extraction judge flips the
> category of **8.1%** of questions. Details and caveats:
> [audit_preliminary/README.md](audit_preliminary/README.md). A paper based
> on this line is in preparation.

## 🏗️ Quickstart

```bash
git clone <this-repo> && cd vlm-bench
pip install -e .
export OPENAI_API_KEY=...   # for API models / LLM judges
```

Produce the artifacts and run the audit (example: MMStar, two models):

```bash
# 1) full runs (with images)
python run.py --data MMStar --model InternVL3-8B Ristretto-3B --mode all --reuse --judge gpt-4o-mini
# 2) blind runs (images stripped centrally; files get a `_blind` suffix)
python run.py --data MMStar --model InternVL3-8B Ristretto-3B --mode all --reuse --blind --judge gpt-4o-mini
# 3) audit over the collected artifacts
python run.py --mode bench_eval --data MMStar --model InternVL3-8B Ristretto-3B --detectors all
```

Outputs land under `--work-dir` (default `./outputs`): per-detector reports
in `reports/<detector>/`, an aggregated `reports/aggregated_findings.json`,
a human-readable `reports/benchmark_audit_report.md`, and the run manifest
`bench_quality_report.json`.

Model inference, dataset loading, and judging are inherited from
VLMEvalKit — any of its ~200 models and ~150 benchmarks can feed the audit
(MCQ/yes-no benchmarks are the supported target today). See the upstream
docs for the underlying toolkit: [Quickstart](/docs/en/Quickstart.md),
[ConfigSystem](/docs/en/ConfigSystem.md), [Development](/docs/en/Development.md).

## 🔍 Detectors

| Detector | Question it answers | Judge-dependent |
|---|---|---|
| `visual_dependency` | Does this question require the image at all? | yes |
| `consensus_error` | Do models unanimously contradict the annotation? | no |
| `fleiss_kappa_agreement` | How much do models agree on raw answers? | no |
| `correctness_agreement` | Difficulty/discrimination profile of items | yes |
| `answer_options_distribution` | Is the correct-option position biased? | no |
| `distractor_similarity` | Are options near-duplicates? | no |

Design rules: answers are extracted from **raw predictions** (never
back-filled from gold labels), frames are aligned on the dataset `index`
(never on row order), and unparseable predictions are excluded from votes.
Full protocol and methodological notes:
[docs/en/BenchmarkAudit.md](docs/en/BenchmarkAudit.md).

## 🧰 Analysis toolkit

- `scripts/audit_stability.py` — bootstrap CIs, leave-one-model-out ranges,
  threshold sweeps for the visual-dependency categories.
- `scripts/rejudge_exact.py` — re-judge existing eval files offline with
  exact matching (the cheap arm of a judge-sensitivity study).
- `scripts/sample_for_annotation.py` — stratified samples for human
  verification of flagged items + precision/Cohen's κ scoring
  (protocol: [docs/en/AnnotationProtocol.md](docs/en/AnnotationProtocol.md)).
- `scripts/audit_paper_assets.py` — publication figures and LaTeX tables
  straight from audit reports.

Tests (no GPU or full install needed):

```bash
python -m pytest tests/test_detectors.py tests/test_bench_eval_pipeline.py -q
```

## 📂 Repository map

| Path | What it is |
|---|---|
| `vlmeval/detector/` | the audit detectors + shared base/alignment logic |
| `vlmeval/bench_eval.py` | audit orchestration (`run.py --mode bench_eval`) |
| `vlmeval/reporting/` | findings aggregation and markdown report |
| `audit_preliminary/` | preliminary MMStar audit results + annotation package |
| `paper/` | manuscript draft (LaTeX) and verified bibliography |
| `docs/en/BenchmarkAudit.md` | audit protocol reference |
| `docs/en/WorkPlan_TAI-Eval.md`, `docs/ru/HANDOFF.md` | internal experiment runbooks |
| everything else | inherited VLMEvalKit evaluation infrastructure |

## 🔗 Relation to VLMEvalKit

This fork tracks [open-compass/VLMEvalKit](https://github.com/open-compass/VLMEvalKit)
(Apache-2.0) and keeps its evaluation behavior intact; the audit layer is
additive. One deliberate deviation: SSL certificate verification is **on by
default** here (set `VLMEVAL_INSECURE_SSL=1` to restore the upstream
unverified-download behavior for broken mirrors).

If you use the underlying evaluation toolkit, please cite:

```bib
@inproceedings{duan2024vlmevalkit,
  title={Vlmevalkit: An open-source toolkit for evaluating large multi-modality models},
  author={Duan, Haodong and Yang, Junming and Qiao, Yuxuan and Fang, Xinyu and Chen, Lin and Liu, Yuan and Dong, Xiaoyi and Zang, Yuhang and Zhang, Pan and Wang, Jiaqi and others},
  booktitle={Proceedings of the 32nd ACM International Conference on Multimedia},
  pages={11198--11201},
  year={2024}
}
```

A citation for the benchmark-audit paper will be added once available.

## 📄 License

[Apache-2.0](LICENSE), same as upstream VLMEvalKit.
