# Human Verification Protocol (detector precision)

Goal: measure the **precision** of the audit detectors on real flagged items,
with two independent annotators. This produces the key table of the paper
(Fig. "precision") and the Cohen's kappa number.

## 1. Sample

Created by `scripts/sample_for_annotation.py sample` (default: 50 items per
stratum, seed 2026):

| Stratum | Detector | What is flagged |
|---|---|---|
| `consensus_error` | consensus_error (critical/warning) | model majority contradicts the gold label |
| `visual_dependency` | visual_dependency (critical) | question labeled visual-dependent / text-only boundary cases |
| `distractor_similarity` | distractor_similarity (critical/warning) | near-duplicate options |

Each annotator receives their own independently shuffled CSV
(`annotator_A.csv`, `annotator_B.csv`). **Do not open `key.json`** (detector
metadata) until both CSVs are filled.

## 2. Instructions per stratum

Open the benchmark TSV (or the data browser) to see the image for the
question id. Fill `verdict` with exactly one of `yes` / `no` / `ambiguous`,
and use `comment` for anything noteworthy.

- **consensus_error** — Question: *is the gold label actually wrong or
  defensible?* `yes` = the gold label is wrong or the majority answer is at
  least as correct; `no` = the gold label is clearly right; `ambiguous` =
  the question itself is ill-posed (multiple defensible answers, missing
  context).
- **visual_dependency** — Question: *can a competent human answer this
  question correctly without seeing the image* (using only text, options,
  and general knowledge)? `yes` = answerable without the image (text-only
  confirmed); `no` = the image is required; `ambiguous` = answerable by
  elimination/guessing bias but not reliably.
- **distractor_similarity** — Question: *are the flagged options effectively
  the same answer* (paraphrases, identical after normalization)? `yes` /
  `no` / `ambiguous`.

Rules: no discussing items before both files are complete; ~60-90 seconds
per item; if an image fails to load, write `image_missing` in the comment
and `ambiguous` in the verdict.

## 3. Scoring

```bash
python scripts/sample_for_annotation.py score \
  --a annotation/<ds>/annotator_A_filled.csv \
  --b annotation/<ds>/annotator_B_filled.csv \
  --key annotation/<ds>/key.json --out annotation/<ds>
```

Outputs `validation_report.json` (per-stratum precision = share of items
where **both** annotators said `yes`, with Wilson 95% intervals; Cohen's
kappa) and `adjudication_worklist.csv` (disagreements). Adjudicate
disagreements together, record the final verdicts in the worklist CSV, and
report both the strict (both-yes) and adjudicated precision in the paper.

## 4. Reporting in the paper

- Precision per stratum + Wilson interval (bar chart via
  `scripts/audit_paper_assets.py --validation ...`).
- Cohen's kappa between annotators.
- 2-3 worked examples per stratum (confirmed and false-positive) in the
  appendix, with question ids.
- Annotator description: two authors, not blinded to the project, blinded to
  detector metadata (`key.json`).
