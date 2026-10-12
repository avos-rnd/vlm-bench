# Reproducing the arXiv v1 results

Paper: [Auditing VLM Benchmarks from Existing Evaluation Runs](https://arxiv.org/abs/2610.13548).
The `arxiv-v1` release combines the camera-ready manuscript with the corrected audit
exports and CPU-only tests. Its manuscript source is based on camera-ready commit
`ce06863c4a721a13a9a21d31423f8dadb81e7aa0`.

## What is available

- Camera-ready LaTeX source, bibliography, pipeline diagram, and statistical figures.
- Statistics/figure scripts and audit code.
- Saved [MMStar significance report](../../audit_preliminary/mmstar_3models_gpt-4o-mini/significance_report.md),
  [HallusionBench significance report](../../audit_preliminary/hallusionbench_3models_auxmatch/significance_report.md),
  and an [archived item-finding digest](../../audit_preliminary/mmstar_3models_gpt-4o-mini/benchmark_audit_report.md).
- Original full/blind prediction files for MMStar and HallusionBench, stored under
  `paper-inputs/`; their SHA-256 hashes are recorded by the reproduction driver.
- Unfilled annotation templates; these are not evidence of completed human verification.

**The original full/blind prediction files are included in `paper-inputs/`.** The
included files contain the item-level predictions, annotations, and correctness values
required by the reproduction driver. Original run manifests are not included;
the driver records SHA-256 checksums for the files supplied to it.

The source runs are documented as eval ID `T20260611-093811`, with InternVL3-8B,
Ristretto-3B, and `gpt-5-nano-2025-08-07`. MMStar correctness uses `gpt-4o-mini`;
HallusionBench uses the saved `auxmatch` correctness results. Use those saved judged
outputs for the published arm. A new API/model run is a new experiment and may differ.

## 1. Install the CPU-only environment

Use Python 3.11. These pins describe the tested release environment; the original
inference environment is not reconstructed by them.

```bash
git clone https://github.com/avos-rnd/vlm-bench.git
cd vlm-bench
git checkout arxiv-v1
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements/audit.txt
python -m pytest tests/test_detectors.py tests/test_bench_eval_pipeline.py tests/test_audit_reporting.py tests/test_paper_reproduction.py -q
```

## 2. Check the included evaluation files

The repository includes six files for each benchmark in the layout below. Retain every
row, prediction, annotation, and correctness value if the files are replaced. The
driver records SHA-256 hashes of the files supplied to it.

```text
paper-inputs/
  MMStar/
    InternVL3-8B_full.xlsx
    InternVL3-8B_blind.xlsx
    Ristretto-3B_full.xlsx
    Ristretto-3B_blind.xlsx
    gpt-5-nano-2025-08-07_full.xlsx
    gpt-5-nano-2025-08-07_blind.xlsx
  HallusionBench/
    ... the same six filenames ...
```

Required columns are `index`, `prediction`, `answer`, `category`, and a consistent
`hit` or `score` correctness column. MMStar additionally needs option columns `A`–`D`.
Expect **1,500** MMStar rows and **951** HallusionBench rows per file, unique question
IDs, and matching IDs/gold labels/categories across every model and evaluation arm.
HallusionBench IDs must preserve the original `VD`/`VS` prefixes for the calibration check.
The driver refuses missing or misaligned inputs instead of silently comparing row positions.

## 3. Regenerate and check the headline statistics

```bash
python scripts/reproduce_paper.py \
  --input-dir paper-inputs \
  --out outputs/paper-reproduction
```

For MMStar alone, append `--benchmarks MMStar`. The driver calls
`scripts/audit_significance.py` with model order as above, **999 permutations**, **seed 7**,
`--strata-column category`, and `--exclude-from-flips gpt-5-nano`. HallusionBench
additionally uses `--design-prefix VD`.

It writes each benchmark's `significance_report.json` and Markdown digest, plus
`reproduction_manifest.json` with input hashes, commit, Python/package versions,
commands, and expected/actual headline checks. Mismatches produce a nonzero exit status.
Matching these headlines alone does not establish that two input archives are identical.

| Quantity | MMStar | HallusionBench diagnostic |
|---|---:|---:|
| Observed zero-gain share | 20.2% | 23.9% |
| Permutation null mean | 17.0% | 18.5% |
| Excess | +3.2 pp | +5.4 pp |
| Corrected permutation p | 0.001 | 0.001 |
| Unanimous non-gold candidates | 134 | MCQ-letter section inapplicable |
| Design-label AUC | — | 0.492 |

Shares and excess are checked to the displayed one-decimal precision. The AUC is checked
to three decimals. The canonical MMStar report also contains Wilson intervals,
leave-one-model-out pools, strata, judge-vs-exact differences, and threshold/split-half
checks; compare these sections with the saved Markdown report and manuscript.

## 4. Regenerate statistical figures

```bash
python scripts/reproduce_paper.py \
  --input-dir paper-inputs \
  --out outputs/paper-reproduction --figures
```

Figures go into the reproduction output, leaving the committed paper figures intact.
The figure script consumes the canonical statistics JSON for aggregate/stochastic
values; it does not rerun the permutation null. Ghostscript is optional for outlining
figure fonts. The pipeline diagram is authored separately and is not regenerated from
prediction files. Building the manuscript requires a TeX installation:

```bash
cd paper
pdflatex main && bibtex main && pdflatex main && pdflatex main
```

## Interpretation limits

Zero gain refers to pool-averaged full/blind correctness; it includes all-wrong items.
Of the 134 unanimous candidates, 117 have three parseable answers and 17 have two.
No verified annotation-error precision is reported. All 122 judge-vs-exact category
flips involve gpt-5-nano; removing it eliminates those flips. HallusionBench is a
format-calibration diagnostic, not support for extending the headline claims to yes/no
benchmarks. Historical detector scores and the counts in the archived digest are
heuristic outputs, not calibrated benchmark quality or verified defect rates.
