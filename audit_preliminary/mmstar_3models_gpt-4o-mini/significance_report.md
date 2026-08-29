# Significance report (no new runs)

- text_only: **20.2%** (Wilson95 [18.2, 22.3])
- unanimous consensus-error: **8.9%** (134 q; Wilson95 [7.6, 10.5])

## text_only: observed vs permutation null (excess is the metric to report)

| pool | observed | null mean | excess (pp) | p |
|---|---|---|---|---|
| all | 20.2% | 17.0% | **+3.2** | 0.0010 |
| without_InternVL3-8B | 27.9% | 24.1% | **+3.7** | 0.0010 |
| without_Ristretto-3B | 25.5% | 21.9% | **+3.6** | 0.0010 |
| without_gpt-5-nano-2025-08-07 | 34.4% | 26.7% | **+7.7** | 0.0010 |

Pool spread: raw 14.2 pp -> excess 4.6 pp.

## Stratified by `category`

| stratum | n | observed | excess (pp) | unanimous CE |
|---|---|---|---|---|
| coarse perception | 250 | 12.4% | -1.7 | 29 (11.6%) |
| fine-grained perception | 250 | 23.6% | +2.1 | 36 (14.4%) |
| instance reasoning | 250 | 13.6% | +0.4 | 15 (6.0%) |
| logical reasoning | 250 | 18.0% | +1.9 | 17 (6.8%) |
| math | 250 | 22.8% | +6.6 | 11 (4.4%) |
| science & technology | 250 | 30.8% | +7.5 | 26 (10.4%) |

## Judge-free (exact matching) primary numbers

- categories: conflicting_visual_signal 6.1%, text_only 19.8%, visual_dependent 20.5%, visual_supplement 53.6%
- judge-vs-exact category flips: all_models = 122, excluding_gpt-5-nano = 0

## VD threshold sweep / split-half

- VD (strict_all_none): 338 (22.5%)
- VD (majority_2of3): 822 (54.8%)
- split-half |excess diff| median: 1.5 pp
