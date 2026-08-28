# Runbook: TAI-Eval (NeurIPS 2026, Sydney) submission

**Paper:** "Auditing VLM Benchmarks for Free: Detecting Benchmark Pathologies
from Existing Evaluation Runs" — draft in [`paper/main.tex`](../../paper/main.tex),
verified bibliography in [`paper/references.bib`](../../paper/references.bib),
positioning analysis in [`RelatedWork_Gap_Analysis.md`](RelatedWork_Gap_Analysis.md).

**Frozen claim.** We ship a 6-detector benchmark-audit layer inside VLMEvalKit
that runs as post-processing over standard evaluation artifacts; case studies
on MMStar/HallusionBench with human-verified precision; audit conclusions are
judge-sensitive. We do NOT claim to discover the pathologies (DatBench,
Fantastic Bugs, BenchMarker are concurrent — see the gap analysis, §4-5).

**Everything below is executable by one person. Checkboxes = definition of
done. All numbers land in `paper/main.tex` replacing `\ph{...}` markers.**

---

## Phase 0 — Environment & sanity (0.5 day)

- [ ] Colab A100: clone the repo, `pip install -e .`, set `OPENAI_API_KEY`
      (and `LMUData` dir if customized).
- [ ] `python -m pytest tests/test_detectors.py -q` → 10 passed.
- [ ] Record the git commit hash you run with; **do not** edit detector code
      after Phase 1 starts (all runs must share one commit).
- [ ] **CFP verified 2026-08-28** (https://tai-eval.github.io/ — workshop is
      officially "TAE: Can We Trust AI Evaluation?"): submission deadline
      **August 29, 2026 AoE**; OpenReview:
      `https://openreview.net/group?id=NeurIPS.cc/2026/Workshop/TAE`;
      notification Sep 22; in-person poster session, Sydney Dec 11-12.
      Topics explicitly include *benchmark and leaderboard auditing* and
      *judge reliability* — direct fit. Page limit and anonymization were
      NOT stated on the site — check the OpenReview venue page before
      submitting. If the deadline cannot be met with the full 6-model
      matrix, follow the deadline scenario in `docs/ru/HANDOFF.md`
      (3-model preliminary submission path).
- [ ] Anonymization: the submission must NOT link this repo directly; prepare
      an anonymized artifact (e.g. anonymous.4open.science) at Phase 6.

## Phase 1 — Inference matrix (2-3 days, A100 + API)

**Model pool (n=6).** Registry names (verified in `vlmeval/config.py`):

| Model | Type | Note |
|---|---|---|
| `InternVL3-8B` | local | existing baseline, re-run on fixed commit |
| `Ristretto-3B` | local | existing baseline |
| `Qwen2.5-VL-7B-Instruct` | local | new, adds a model family |
| `LLaVA-OneVision-1.5-8B-Instruct` | local | new, adds a model family |
| `gpt-5-nano-2025-08-07` | API | re-run with recorded params |
| `gpt-4.1-mini-2025-04-14` | API | new API family |

**Datasets:** `MMStar`, `HallusionBench`. (Do NOT add more — see "What not
to do".)

**Decoding:** greedy everywhere it is controllable (`do_sample=False`,
temperature 0 — for API models pass via model kwargs / `--judge-args`-style
overrides where the wrapper supports it). The run manifest
(`outputs/<model>/<eval_id>/run_status.json`) now records
`generation_kwargs`, `blind`, commit and argv automatically — spot-check one
manifest after the first run.

Commands per model M and dataset D (full, then blind — same eval directory):

```bash
python run.py --data D --model M --mode all --reuse --judge gpt-4o-mini
python run.py --data D --model M --mode all --reuse --blind --judge gpt-4o-mini
```

- [ ] 6 models x 2 datasets x {full, blind} = 24 prediction files + judged
      eval files, all under one `eval_id` per model.
- [ ] **Variance study:** for `InternVL3-8B` on `MMStar`, 3 extra full+blind
      repeats with default sampling (`do_sample=True`); keep in separate
      eval dirs. Feeds Appendix "Run-to-run variance".
- [ ] Verify pairing: each eval dir contains `M_D.xlsx` and `M_D_blind.xlsx`
      (plus `_gpt-4o-mini_result` eval files for both).

## Phase 2 — Judge sensitivity (0.5-1 day, cheap: eval-stage only)

Re-judge the SAME predictions under 2 more protocols (no new inference):

```bash
# exact matching (deterministic, no API)
python run.py --data D --model M --mode eval --reuse --judge exact_matching
# second LLM judge
python run.py --data D --model M --mode eval --reuse --judge gpt-4.1-mini-2025-04-14
```

- [ ] 3 judge variants x 2 datasets, full + blind, all 6 models.
- [ ] Keep the three judged result sets in separate audit work dirs (copy
      eval files into `outputs_audit_<ds>_<judge>/<model>/<eval_id>/`), so
      each judge gets its own `bench_eval` run.

## Phase 3 — Audits (0.5 day)

For each dataset D and judge J:

```bash
python run.py --mode bench_eval --data D \
  --model InternVL3-8B Ristretto-3B Qwen2.5-VL-7B-Instruct \
          LLaVA-OneVision-1.5-8B-Instruct gpt-5-nano-2025-08-07 gpt-4.1-mini-2025-04-14 \
  --detectors all --work-dir outputs_audit_<D>_<J>
```

- [ ] 6 audit dirs (2 datasets x 3 judges), each with
      `bench_quality_report.json` + `reports/`.
- [ ] Sanity: `visual_dependency` executed (needs full+blind pairs across
      all models); `consensus_error` flagged counts are nonzero; question_ids
      in findings are dataset ids (not 0..N row numbers).
- [ ] **Stability analyses** (notebook or small script, from
      `reports/visual_dependency/all_stat.json`):
      leave-one-model-out category shares (drop each model, recompute) and a
      bootstrap 95% CI over questions for the text_only/VD shares. These two
      numbers go straight into Section 5 of the paper.
- [ ] **MMStar overlap check:** compare our text_only question set with the
      MMStar authors' leakage analysis (their paper/repo); report overlap %.
      This is the reviewer-B killer — do not skip.

## Phase 4 — Human verification (1 day, 2 annotators x 3-4 h)

Protocol: [`AnnotationProtocol.md`](AnnotationProtocol.md).

```bash
python scripts/sample_for_annotation.py sample \
  --work-dir outputs_audit_MMStar_gpt-4o-mini \
  --dataset-tsv ~/LMUData/MMStar.tsv --per-stratum 50 --seed 2026 \
  --out annotation/mmstar
# ... two people fill annotator_A.csv / annotator_B.csv independently ...
python scripts/sample_for_annotation.py score \
  --a annotation/mmstar/annotator_A_filled.csv \
  --b annotation/mmstar/annotator_B_filled.csv \
  --key annotation/mmstar/key.json --out annotation/mmstar
```

- [ ] `validation_report.json` with per-stratum precision + Cohen's kappa.
- [ ] Adjudicated disagreements recorded in `adjudication_worklist.csv`.
- [ ] Pick 6-10 worked examples (ids + verdicts) for the appendix.

## Phase 5 — Figures, tables, numbers into the paper (1 day)

```bash
python scripts/audit_paper_assets.py \
  --run MMStar=outputs_audit_MMStar_gpt-4o-mini \
  --run HallusionBench=outputs_audit_HallusionBench_gpt-4o-mini \
  --validation annotation/mmstar/validation_report.json \
  --judge-run exact=outputs_audit_MMStar_exact_matching \
  --judge-run gpt4omini=outputs_audit_MMStar_gpt-4o-mini \
  --judge-run gpt41mini=outputs_audit_MMStar_gpt-4.1-mini-2025-04-14 \
  --out paper/figures
```

- [ ] `fig_scatter_*.pdf`, `tab_main.tex`, `fig_precision.pdf`,
      `tab_judge_sensitivity.tex` generated; wire them into `main.tex`
      (replace the `\fbox` placeholders with `\includegraphics`).
- [ ] Replace every `\ph{...}` in `paper/main.tex`; then
      `grep -c 'ph{' paper/main.tex` must return 0 (except the macro
      definition).
- [ ] Threshold-sensitivity appendix: rerun `bench_eval` with 2-3 threshold
      configs (detector kwargs) OR compute offline from `all_stat.json`
      (preferred: it contains raw full/blind accuracies per question).
- [ ] Compute honesty: total A100-hours + API spend into Section "setup".

## Phase 6 — Text, review, submission (2-3 days)

- [ ] Write results paragraphs (marked `\ph{One paragraph: ...}`) from the
      actual numbers; keep the "we do not claim discovery" framing from the
      intro (see gap analysis §5 for the positioning paragraph and the
      one-line differentiators vs DatBench / Fantastic Bugs / BenchMarker).
- [ ] Limitations: keep all six items; update with observed false-positive
      modes from Phase 4.
- [ ] NeurIPS checklist appendix filled.
- [ ] Anonymized artifact: export the repo without
      `docs/en/NeurIPS2026_Workshop_Readiness.md`, `docs/en/WorkPlan_TAI-Eval.md`
      and anything naming authors/affiliations; include audit reports +
      annotation CSVs (no raw images — link datasets instead).
- [ ] Internal review pass: one person reads as "hostile MMStar author"
      (is the overlap analysis there?), one as "reproducibility skeptic"
      (can they rerun bench_eval from the manifest?).
- [ ] Submit on OpenReview; verify page limit and non-archival settings.

## Budget estimate

- Local inference: 4 models x 2 datasets x 2 variants x (~1-2 h) ≈ 16-32
  A100-hours (+3 variance repeats ≈ +6 h). Blind runs are faster (no
  vision tokens).
- API inference: 2 models x 2 datasets x 2 variants (≈ 2,451 questions x 2)
  + judge calls (gpt-4o-mini + gpt-4.1-mini over ~29k rows) — small; log
  actual spend for the paper.

## What NOT to do (scope freeze)

- No new benchmarks beyond MMStar/HallusionBench (MMVet/MMBench artifacts in
  `origin/results` stay out of the paper).
- No `question_image_relevance` results in the main text (CLIP-threshold
  validity is unvalidated; mention as future work at most).
- No composite "Benchmark Score" averaging detector scores (incomparable
  scales; reviewers will attack it).
- No model-ranking claims — this paper is about benchmarks, not models.
- Do not restart detector development; the commit is frozen after Phase 0.
