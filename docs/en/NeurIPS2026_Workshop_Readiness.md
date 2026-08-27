# NeurIPS 2026 Workshop Readiness Plan

## 1. Scope of the paper line

This document is for the **benchmark-audit** line in this repository, not for the full VLMEvalKit surface area.

Working paper question:

> Can existing VLM evaluation runs be repurposed to automatically audit benchmark quality, instead of only ranking models by score?

Current code paths that define this line:

- `/home/runner/work/vlm-bench/vlm-bench/run.py` (`--mode bench_eval`)
- `/home/runner/work/vlm-bench/vlm-bench/vlmeval/bench_eval.py`
- `/home/runner/work/vlm-bench/vlm-bench/vlmeval/detector/`
- `/home/runner/work/vlm-bench/vlm-bench/vlmeval/reporting/benchmark_audit.py`

## 2. Target NeurIPS 2026 workshops

### Primary targets

1. **TAI-Eval** (Sydney)
2. **Can We Trust the Judge?** (Atlanta)

### Backup targets

1. **AI for Meta-Science** (Paris)
2. **AI for Science: Verification in the Age of AI Scientists** (Sydney)
3. **Attributing Model Behavior at Scale** (Sydney)

### Workshop trap to avoid

- **Evaluation of Interactive Agents** (Atlanta)  
  The current paper line is about static benchmark auditing for VLM evaluation artifacts, not interactive agents.

### Submission reminder

- Recommended global target: **29.08.2026 23:59 AoE**
- Each workshop may use its own deadline and page rules
- Always re-check **CFP / OpenReview / archival / anonymity** before submission

## 3. Repository organization for the workshop paper

### Keep as the core contribution

- `run.py --mode bench_eval` as the user-facing entrypoint
- `vlmeval/bench_eval.py` as the orchestration layer
- `vlmeval/detector/*.py` as the benchmark pathology detectors
- `vlmeval/reporting/benchmark_audit.py` as the report aggregation layer

### Treat as supporting infrastructure, not the main paper contribution

- the large model registry in `/home/runner/work/vlm-bench/vlm-bench/vlmeval/config.py`
- the broad dataset registry in `/home/runner/work/vlm-bench/vlm-bench/vlmeval/dataset/`
- generic inference / API integration paths in `/home/runner/work/vlm-bench/vlm-bench/vlmeval/api/` and `/home/runner/work/vlm-bench/vlm-bench/vlmeval/vlm/`

### Suggested documentation / artifact split

- `README.md`: short public statement of target workshops and paper line
- this file: internal publication to-do and open questions
- future paper artifact directory: final configs, commands, tables, and figures for the chosen workshop

## 4. Work plan to reach workshop quality

### A. Claim freeze

- Freeze one narrow claim around **automatic benchmark auditing from existing evaluation runs**
- Do not position the work as “a general new VLM evaluation toolkit”
- Do not position the work as “state of the art benchmark science” without validation

### B. Minimal experimental package

- Choose **1 benchmark family** first, preferably MCQ-heavy
- Choose **3 reference models** already used in CI where possible
- Produce **1 end-to-end audit report**
- Produce **1 manual validation pass** over top flagged samples
- Produce **1 judge sensitivity comparison**

### C. Writing package

- one figure for the pipeline
- one table for detector taxonomy
- one case-study table with benchmark findings
- one limitations section focused on judge dependence, heuristics, and reproducibility

## 5. Methodological rigor to-do

### Must-have before submission

1. **Document the blind-run protocol**
   - `visual_dependency` assumes matching full/blind runs
   - today this protocol is not documented in the main docs

2. **Validate detector outputs with manual review**
   - at least for the highest-severity findings
   - show which alerts were true positives vs noise

3. **Measure judge sensitivity**
   - compare `exact_matching`
   - compare `gpt-4o-mini`
   - compare one local or alternative judge if available

4. **Define benchmark inclusion criteria**
   - which datasets are suitable for the paper
   - which detectors are applicable to which dataset types

5. **Add an explicit limitations section**
   - heuristic thresholds
   - dependence on existing predictions
   - possible prompt confounders
   - incomplete support outside MCQ-like settings

### Strongly recommended

6. **Add one public example command sequence for bench audit**
7. **Add one small reproducible result bundle**
8. **Record exact configs, judge model, and eval IDs used in the paper**
9. **Explain why this line is distinct from the ACM Multimedia 2024 VLMEvalKit paper**

## 6. Hypotheses about scientific novelty

These are working hypotheses, not established claims yet.

1. **Artifact novelty hypothesis**  
   The main novelty is a reusable audit layer that operates on existing VLM evaluation artifacts.

2. **Evaluation hypothesis**  
   Detector-based audit signals can reveal benchmark pathologies that are invisible in leaderboard scores alone.

3. **Judge hypothesis**  
   Conclusions about benchmark quality are sensitive to the answer extraction / judge protocol, and this sensitivity should be measured rather than hidden.

4. **Practical science hypothesis**  
   For workshop-level contribution, a well-validated benchmark-audit artifact plus case studies may be more compelling than another generic leaderboard update.

## 7. Research gap hypotheses

1. Existing VLM evaluation toolkits mostly optimize for **scoring models**, not **auditing benchmarks**.
2. Existing leaderboard pipelines rarely expose benchmark pathology analysis as a first-class output artifact.
3. Benchmark quality checks are often done manually and late, instead of through a reproducible post-processing layer.
4. Judge-mediated VLM evaluation introduces hidden variability that is rarely surfaced in benchmark audit workflows.

## 8. Unanswered questions we should try to answer

1. Which benchmark family is the strongest first case study for this paper?
2. How should blind runs be created and named for reproducible `visual_dependency` analysis?
3. Which detectors have the highest precision on real benchmark artifacts?
4. How much do conclusions change under different judge choices?
5. Which findings are actionable for benchmark maintainers?
6. What is the smallest result package that can still convince a workshop reviewer?
7. How do we clearly separate this paper from the previously published VLMEvalKit line?

## 9. What not to do for this submission

- Do not broaden the paper to the full repository
- Do not start many new benchmark integrations just for the submission
- Do not claim benchmark science beyond the evidence currently available
- Do not optimize for SOTA leaderboard coverage; optimize for a sharp, validated benchmark-audit story

## 10. Candidate additional required changes to discuss

These changes are likely important, but should be discussed before implementation:

1. Add a dedicated `bench_eval` section to `README.md` or `/home/runner/work/vlm-bench/vlm-bench/docs/en/Quickstart.md`
2. Add a documented blind/full benchmark audit workflow
3. Add at least one test covering `bench_eval` or the detector/reporting path
4. Revisit the global SSL verification bypass in `/home/runner/work/vlm-bench/vlm-bench/vlmeval/__init__.py`
5. Decide whether to ship a small example audit artifact in the repository or only in the paper supplement
