# Auditing VLM Benchmarks from Existing Evaluation Runs

Denis Degtiarev, Anna Gromova, Sergey Katkov, Artem Mikhailin,
Safina Mukhamedshina, Albert Nasybullin, Karina Shaikhutdinova, Artem Tuzov — Innopolis University.

[arXiv v1](https://arxiv.org/abs/2610.13548v1) ·
[OpenReview](https://openreview.net/forum?id=0RTvEQrBET) ·
[NeurIPS poster](https://neurips.cc/virtual/2026/loc/sydney/178389)

Accepted as a poster at TAE (Trust-AI-Eval): Can We Trust AI Evaluation?,
NeurIPS 2026 Workshop (non-archival). This directory contains the camera-ready
manuscript with named authors and final workshop formatting, based on
`ce06863c4a721a13a9a21d31423f8dadb81e7aa0`.

## Build

With a TeX installation, from this directory:

```bash
pdflatex main && bibtex main && pdflatex main && pdflatex main
```

`neurips_2026.sty` is the official workshop style. `main.pdf` is the committed
camera-ready rendering. For statistics and figure generation, follow
[ReproducingPaper.md](../docs/en/ReproducingPaper.md); original prediction files
are included under `../paper-inputs/`.

## Figures

| File | Content |
|---|---|
| `figures/fig_pipeline.pdf` | Saved evaluation artifacts, six detectors, and per-question reports. |
| `figures/fig_visual_dependency.pdf` | Visual gain, permutation null, and composition of zero-gain items. |
| `figures/fig_strata.pdf` | Category profiles of zero-gain excess and label-conflict candidates. |
| `figures/fig_robustness.pdf` | LLM judge vs exact matching and the source of scoring discrepancies. |
| `figures/fig_binary_format.pdf` | HallusionBench calibration diagnostic. |

`scripts/audit_significance.py` generates the canonical statistical report;
`scripts/audit_paper_figures.py` uses that report for stochastic/aggregate values.
The pipeline diagram is authored separately. The README's visual abstract is
`assets/visual-abstract.svg` at the repository root.

## Human verification

The 134 unanimous conflicts are **candidates**. The annotation templates are unfilled,
and detector precision has not been measured. Preserve that distinction in derivative
reports, descriptions, and figures.
