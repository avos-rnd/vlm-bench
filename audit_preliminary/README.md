# Preliminary audit results (2026-08-28)

Produced with the **fixed** audit pipeline (current working tree: index-based
alignment, judge-free extraction, no ground-truth back-fill, 'Z' abstentions
excluded) applied to the existing prediction artifacts from the
`origin/results` branch (MMStar, 3 models: InternVL3-8B, Ristretto-3B,
gpt-5-nano-2025-08-07; eval id `T20260611-093811`; judge `gpt-4o-mini`).

## Headline numbers (3-model pool — preliminary, see caveats)

| Quantity | gpt-4o-mini judge | exact matching |
|---|---|---|
| visual_dependent | 22.5% | 20.5% |
| visual_supplement | 52.3% | 53.6% |
| text_only | 20.2% (boot95 [18.2, 22.2]) | 19.8% |
| conflicting_visual_signal | 5.0% | 6.1% |
| consensus-error rate (flagged) | 23.9% | see reports |
| unanimous consensus errors | 8.9% (134 questions) | see reports |
| Fleiss' kappa (raw answers) | 0.495 | see reports |
| per-question category flips between the two judges | 8.1% (122/1500) | — |
| text_only set Jaccard between judges | 0.79 | — |

Note vs the June (pre-fix) audit: consensus-error was then 18.4% with only
12 unanimous items — the old detector back-filled ground truth for
judged-correct answers, masking wrong-consensus. The corrected numbers
supersede the old ones everywhere.

## Caveats

- 3 models only: leave-one-model-out ranges are wide
  (`visual_dependency/stability_report.json`) — the paper pool is 6 models
  (see `docs/en/WorkPlan_TAI-Eval.md` Phase 1).
- The unanimous consensus-error set (134) is **before** human verification;
  precision comes from the annotation package below.
- Dataset frame was reconstructed from the eval files (no images); detector
  logic does not use images except `question_image_relevance` (not run).

## Contents

- `mmstar_3models_gpt-4o-mini/` — detector summary reports, stability
  report, `all_stat.json` (per-question, with per-model correctness), run
  manifest.
- `mmstar_3models_exact/` — the same predictions re-judged offline with
  exact matching (`scripts/rejudge_exact.py`), audited again.
- `annotation_mmstar/` — ready 150-item human-verification package
  (50 consensus_error + 50 visual_dependency + 50 distractor_similarity;
  seed 2026). Fill `annotator_A.csv` / `annotator_B.csv` independently, do
  NOT open `key.json` first; then score with
  `scripts/sample_for_annotation.py score` (protocol:
  `docs/en/AnnotationProtocol.md`).
