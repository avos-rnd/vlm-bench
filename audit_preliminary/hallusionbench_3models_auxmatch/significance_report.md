# Significance report (no new runs)

- text_only: **23.9%** (Wilson95 [21.3, 26.7])
- MCQ-letter sections (unanimous CE, exact-matching arm) skipped: predictions do not parse as option letters (Z-rate 100%).

## text_only: observed vs permutation null (excess is the metric to report)

| pool | observed | null mean | excess (pp) | p |
|---|---|---|---|---|
| all | 23.9% | 18.5% | **+5.4** | 0.0010 |
| without_InternVL3-8B | 33.9% | 27.1% | **+6.8** | 0.0010 |
| without_Ristretto-3B | 29.3% | 22.9% | **+6.4** | 0.0010 |
| without_gpt-5-nano-2025-08-07 | 36.6% | 27.7% | **+8.9** | 0.0010 |

Pool spread: raw 12.7 pp -> excess 3.5 pp.

## Stratified by `category`

| stratum | n | observed | excess (pp) | unanimous CE |
|---|---|---|---|---|
| VD | 591 | 22.5% | +3.4 | n/a |
| VS | 360 | 26.1% | +7.6 | n/a |

## VD threshold sweep / split-half

- VD (strict_all_none): 140 (14.7%)
- VD (majority_2of3): 478 (50.3%)
- split-half |excess diff| median: 2.1 pp

## Design-label calibration: AUC = 0.492 (prefix `VD`, 591 positives; 0.5 = chance)
