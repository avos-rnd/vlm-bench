# Paper: Auditing VLM Benchmarks for Free (TAE @ NeurIPS 2026)

## Build

The official (unmodified) `neurips_2026.sty` sits in this directory. TAE
rules (verified 28.08): 8 pages excl. references/appendices, single PDF,
`\usepackage[dblblindworkshop]{neurips_2026}` + `\workshoptitle{TAE
(Trust-AI-Eval): Can We Trust AI Evaluation?}` — already set in
`main.tex`. Full submission contract, style rules, per-section advice
and pre-submit checklist: [WRITING_GUIDE.md](WRITING_GUIDE.md).

```bash
export PATH="/opt/homebrew/opt/texlive/bin:$PATH"   # brew install texlive
pdflatex main && bibtex main && pdflatex main && pdflatex main
```

Current state (29.08): complete draft, no placeholders. Sections are
Abstract / Introduction (+ Contributions) / Related work / Methodology
(incl. the evaluation protocol) / Results / Limitations / Conclusion, then
References and three appendices. Compiles with 0 errors, 0 undefined
references, 0 overfull boxes; content ends on page 7 of 8, References start
on page 8, appendices follow (both are outside the limit). `pdffonts` shows
Type 1 only; US Letter. The first-page footer intentionally reads
"Submitted to ... Do not distribute" — the workshop name appears only under
`[final]`, at camera-ready.

## Numbers and figures

Nothing in `main.tex` is typed by hand. Every number comes from
`scripts/audit_significance.py` and every figure from
`scripts/audit_paper_figures.py`, which imports its detector logic from the
former so the two cannot drift apart. Regenerate both with the commands in
Appendix A of the paper. Figures are post-processed by ghostscript
(`-dNoOutputFonts`, invoked inside the figure script) to convert text to
outlines — matplotlib otherwise embeds CID TrueType subsets, and NeurIPS
allows only Type 1 or embedded TrueType.

Figures in the paper:

| File | Where | Shows |
|---|---|---|
| `fig_visual_dependency.pdf` | §4.1 | scatter, permutation null, composition of the no-gain set |
| `fig_strata.pdf` | §4.2 | text-only excess vs label-error candidates per category |
| `fig_robustness.pdf` | §4.4 | judge vs exact matching, and the single model behind every flip |
| `fig_binary_format.pdf` | App. C | HallusionBench ROC at chance + the surviving signal |

## Human verification

The paper deliberately makes **no** claim about detector precision: the
annotation package in `audit_preliminary/annotation_mmstar/` contains only
empty templates, so §4.3 reports the 134 unanimous conflicts as *candidates*
and Limitation (ii) states that their precision is unmeasured. If the
annotation is completed later, add the precision numbers to §4.3 and adjust
that limitation — do not weaken the candidate framing anywhere else.

## Anonymization

Do not include repository URLs, author names, or the internal planning docs
(`NeurIPS2026_Workshop_Readiness.md`, `WorkPlan_TAI-Eval.md`,
`docs/ru/HANDOFF.md`, `paper/WRITING_GUIDE.md`) in the submitted artifact.
