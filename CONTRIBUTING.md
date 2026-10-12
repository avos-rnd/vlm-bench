# Contributing

Keep changes focused and use descriptive English commit and pull-request titles:

- `fix(audit): export full and blind findings`
- `docs: explain the MMStar case study`
- `paper: update the camera-ready manuscript`
- `ci: test the audit without GPU runners`

Explain the concrete behavior changed in the commit body when needed. Squash temporary
fixup commits before merging a pull request; avoid generic titles such as `update`,
`fix`, or personal notes. Keep separate changes in separate pull requests.

The existing VLMEvalKit history is retained for provenance. Do not rewrite public
history or move a published release tag. Use a new tag for subsequent releases.

## Validation

With Python 3.11:

```bash
python -m pip install -r requirements/audit.txt
python -m pytest tests/test_detectors.py tests/test_bench_eval_pipeline.py tests/test_audit_reporting.py tests/test_paper_reproduction.py -q
```

These tests use synthetic fixtures and exercise the real audit logic without loading
models or downloading datasets. Changes to exports must preserve dataset question IDs,
full/blind provenance, and idempotent aggregation.

Changes to paper statistics must be checked against `docs/en/ReproducingPaper.md`.
Treat detector findings as review candidates; do not describe them as verified label
errors without human validation. Include baselines, model-pool scope, and format limits
when reporting numerical results.

The fork's GitHub Actions run CPU-only audit tests and syntax/name checks. Model
inference remains a separate manual experiment requiring the appropriate hardware.
