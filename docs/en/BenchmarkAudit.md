# Benchmark Audit Layer (`run.py --mode bench_eval`)

This document is the reference for the benchmark-audit line of this repository:
how to produce the required artifacts (full + blind runs), how to run the
detectors, what they compute, and how to reproduce a published audit.

## 1. Concept

Standard VLM evaluation answers *"how good is the model?"*. The audit layer
reuses the very same artifacts — the per-question prediction/eval files that
VLMEvalKit already saves — to answer *"how good is the benchmark?"*:

| Detector | Question it answers | Needs |
|---|---|---|
| `visual_dependency` | Does this question require the image at all? | full + blind runs, ≥2 models, judged `hit` labels |
| `consensus_error` | Do models unanimously contradict the annotation (label-error candidate)? | ≥2 models, MCQ |
| `fleiss_kappa_agreement` | How much do models agree on raw answers (Fleiss' κ)? | ≥2 models, MCQ |
| `correctness_agreement` | Agreement/difficulty profile on judged correctness | ≥2 models, judged `hit` labels |
| `answer_options_distribution` | Is the correct option position biased (e.g. "C" too often)? | dataset only, MCQ |
| `distractor_similarity` | Are options near-duplicates (degenerate MCQ)? | dataset only, MCQ |
| `question_image_relevance` | Is the image even related to the question (CLIP similarity)? | dataset + CLIP backend |

## 2. Blind-run protocol

A **blind run** is a normal evaluation run with *all visual content removed
from every prompt*, textual content unchanged. It is implemented centrally in
`vlmeval/inference.py::strip_visual_content` and activated with the CLI flag:

```bash
python run.py --data MMStar --model InternVL3-8B --mode all --reuse --blind
```

Rules:

- **Never** modify model wrappers to drop images; the `--blind` flag is the
  single supported mechanism (it covers both local and API models).
- Blind prediction/eval files receive a `_blind` suffix
  (`<model>_<dataset>_blind.xlsx`, `..._blind_<judge>_result.xlsx`) via
  `vlmeval/smp/file.py::get_pred_file_path`, so full and blind artifacts
  coexist in the *same* eval directory (`outputs/<model>/<eval_id>/`).
  `bench_eval` pairs them by this suffix.
- Run full and blind with **identical** generation settings and the
  **identical** judge. The run manifest (`run_status.json`, updated by
  `upsert_run_status`) records `blind`, `generation_kwargs`, git commit and
  argv for every run.

## 3. Running the audit

```bash
python run.py --mode bench_eval --data MMStar \
    --model InternVL3-8B Ristretto-3B gpt-5-nano-2025-08-07 \
    --detectors all --work-dir ./outputs
```

- Exactly **one** dataset per audit run.
- `--detectors` accepts a subset (e.g. `visual_dependency consensus_error`).
- The pipeline aligns all result frames on the dataset `index` column
  (`vlmeval/detector/base_detector.py::align_results`). Files that disagree on
  question ids are restricted to the shared subset with a logged warning —
  detectors never rely on row order.

### Outputs (under `--work-dir`)

```
bench_quality_report.json      # run manifest: commit, argv, inputs, detector status
reports/<detector>.json        # per-detector report (summary + findings)
reports/<detector>/*.json      # per-question exports (flagged lists, all_stat)
reports/aggregated_findings.json
reports/benchmark_audit_report.md
```

Every per-question finding carries the **dataset-level `index`** as
`question_id`, a `severity` (`critical`/`warning`/`info`) and a `reason`.

## 4. Methodological notes (read before interpreting numbers)

1. **Judge-free vs judge-mediated detectors.** `consensus_error` and
   `fleiss_kappa_agreement` operate on option letters extracted from *raw
   predictions* (`BaseDetector._extract_mcq_option`); unparseable predictions
   become the sentinel `'Z'` and are excluded from votes. `visual_dependency`
   and `correctness_agreement` consume judged `hit` labels and therefore
   inherit the judge protocol — always report which judge produced them and
   run the judge-sensitivity comparison (`exact_matching` vs LLM judge).
2. **Thresholds.** Category thresholds (e.g. `visual_dependent_full_thresh`)
   are heuristics; the defaults live in each detector's `DEFAULT_CONFIG` and
   can be overridden. Report threshold sensitivity when publishing.
3. **Model-pool dependence.** With `n` models, per-question accuracies live on
   a grid of `n+1` values; categories stabilize with more/diverse models.
   Use ≥5 models for publishable claims and report leave-one-model-out
   stability.
4. **Contamination confound.** High blind accuracy mixes language priors and
   training-data leakage; the audit does not separate them.

## 5. Reproducing a published audit

1. `git checkout <commit recorded in bench_quality_report.json>`.
2. Place (or re-generate) the prediction/eval files listed under
   `result_paths` in the manifest.
3. Re-run the `bench_eval` command from the manifest's `argv`.
4. Detector reports are deterministic given the same inputs; only
   `question_image_relevance`/`distractor_similarity` depend on optional
   embedding backends (CLIP / sentence-transformers versions are recorded in
   `requirements.txt`).

## 6. Testing

```bash
python -m pytest tests/test_detectors.py -q
```

The tests cover frame alignment, judge-free option extraction (including the
no-ground-truth-substitution guarantee), consensus flagging with abstentions,
visual-dependency categorization, and Fleiss' κ.
