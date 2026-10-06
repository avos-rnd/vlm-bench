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

## Strengthened statistics (2026-08-28, post-processing only)

`scripts/audit_significance.py` re-derives the headline numbers with
publication-grade statistics from the same artifacts (no new inference);
full output: `mmstar_3models_gpt-4o-mini/significance_report.{md,json}`,
`hallusionbench_3models_auxmatch/significance_report.{md,json}`.

**Report the permutation-null excess, not the raw text_only share.** The
raw share is dominated by marginal-rate arithmetic and by the model pool
(raw spread across 2–3-model pools: 14.2 pp). The excess over a
block-shuffle null is the per-question signal: MMStar **+3.2 pp**
(p=0.001, null 17.0%), stable across every pool (+3.2…+7.7, all p=0.001;
pool spread shrinks to 4.6 pp; split-half reproducibility ±1.5 pp).

**The signal is localized, not uniform.** Stratifying by the six official
MMStar categories: the text-only excess concentrates in *math* (+6.6 pp)
and *science & technology* (+7.5 pp) — knowledge-solvable strata — while
*coarse perception* shows none (−1.7). Unanimous consensus-error
candidates peak in the perception strata (fine-grained 14.4%, coarse
11.6%) and are lowest in math/reasoning (4.4–6.8%), with science &
technology intermediate (10.4%) — so the two pathologies separate but not
perfectly. Six strata with a coherent pattern double as internal
replication.

**Primary numbers are judge-free.** consensus/κ never used an LLM judge;
the visual-dependency categories re-computed with exact matching are
20.5 / 53.6 / 19.8 / 6.1% (vs 22.5 / 52.3 / 20.2 / 5.0 judged) — same
conclusions. All 122 judge-vs-exact category flips originate from
gpt-5-nano's non-canonical outputs; with it excluded, flips = **0**. The
LLM judge is therefore a robustness arm, not a dependency.

**Do not headline the visual_dependent share.** It is threshold-fragile:
22.5% under the strict all/none definition vs 54.8% under a ≥2/3-majority
definition (sweep in the report). text_only has no threshold (exact
equality) and the unanimous CE count has none either.

**HallusionBench is excluded from headline claims.** On the yes/no format
blind guessing sits at 50%, unanimity is trivial with two options, and the
continuous visual gain does not recover the benchmark's own VD/VS design
split (AUC 0.49 ≈ chance). One directionally consistent signal survives:
the text-only *excess* is 2.2× larger on design-VS questions (+7.6 pp)
than on design-VD (+3.4 pp). Treat the format as out of scope for the
current detector calibration.

Wilson 95% intervals (closed-form, replaces the bootstrap): text_only
[18.2, 22.3], unanimous CE [7.6, 10.5].

## Caveats

- 3 models only: leave-one-model-out ranges are wide (per-pool table in
  `significance_report.md`) — the paper pool is 6 models
  (see `docs/en/WorkPlan_TAI-Eval.md` Phase 1).
- The unanimous consensus-error set (134) is **before** human verification;
  precision comes from the annotation package below.
- Dataset frame was reconstructed from the eval files (no images); detector
  logic does not use images except `question_image_relevance` (not run).

## Contents

- `mmstar_3models_gpt-4o-mini/` — `benchmark_audit_report.md` (aggregated
  detector digest) and `significance_report.{md,json}` (permutation-null
  excess, strata, judge-free exact arm, threshold sweep — see above). The
  exact-matching arm lives inside the significance report; per-question
  `all_stat.json`/stability exports are regenerated on demand
  (`run.py --mode bench_eval` + `scripts/audit_stability.py`), they are
  not committed (`*json` is git-ignored repo-wide).
- `hallusionbench_3models_auxmatch/` — `significance_report.{md,json}`
  for HallusionBench (excess + design-label calibration; MCQ-letter
  sections not applicable to the yes/no format).
- `annotation_mmstar/` — ready 150-item human-verification package
  (50 consensus_error + 50 visual_dependency + 50 distractor_similarity;
  seed 2026). Fill `annotator_A.csv` / `annotator_B.csv` independently, do
  NOT open `key.json` first; then score with
  `scripts/sample_for_annotation.py score` (protocol:
  `docs/en/AnnotationProtocol.md`).
