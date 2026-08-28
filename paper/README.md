# Paper: Auditing VLM Benchmarks for Free (TAI-Eval @ NeurIPS 2026)

## Build

1. Download the official `neurips_2026.sty` from the TAI-Eval CFP page (or
   neurips.cc) into this directory. Check whether the workshop mandates its
   own style/page limit before submitting.
2. `pdflatex main && bibtex main && pdflatex main && pdflatex main`.

The draft compiles cleanly (0 errors, 0 BibTeX warnings) against a minimal
style stub; all citations in `references.bib` are verified against primary
sources (see `docs/en/RelatedWork_Gap_Analysis.md`).

## Placeholders

Every to-be-measured number is typeset as `\ph{...}` (red). The experiment
runbook that produces them is `docs/en/WorkPlan_TAI-Eval.md`. Before
submission: `grep -n 'ph{' main.tex` must only match the macro definition.

## Figures

Generated into `figures/` by `scripts/audit_paper_assets.py` (scatter,
precision bars, judge-sensitivity table, main results table body). Replace
the `\fbox` placeholders in `main.tex` with `\includegraphics` once
generated.

## Anonymization

Do not include repository URLs, author names, or the internal planning docs
(`NeurIPS2026_Workshop_Readiness.md`, `WorkPlan_TAI-Eval.md`) in the
submitted artifact.
