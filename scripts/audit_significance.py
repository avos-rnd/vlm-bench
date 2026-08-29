"""Statistical strengthening of audit numbers — no new inference runs.

Post-processes existing judged eval files (full + blind, per model) and
computes, for the visual-dependency and consensus lines of the audit:

1. **Wilson 95% intervals** for the headline proportions (text_only,
   consensus-flagged, unanimous) — a standard closed-form replacement for
   the bootstrap CI.
2. **Permutation-null excess** for ``text_only``: blind rows are block-
   shuffled across questions (marginals and inter-model structure kept,
   per-question full<->blind linkage destroyed). The reported statistic is
   ``observed - null_mean`` with a permutation p-value. Motivation: the raw
   text_only share is dominated by marginal-rate arithmetic and swings with
   the model pool; the excess is the per-question signal and is far more
   pool-stable (on the 3-model MMStar artifacts the pool spread shrinks
   from ~14pp to ~4.5pp).
3. **Leave-one-model-out** raw and excess values per 2-model pool.
4. **Stratified excess** over a dataset column (default ``category``):
   per-stratum observed/null/excess for text_only plus unanimous
   consensus-error counts — localizes the signal and provides internal
   replication across strata.
5. **Judge-free primary numbers**: the four visual-dependency categories
   recomputed with exact matching (extracted option letter == gold), plus
   the count of judge-vs-exact category flips overall and with the
   non-canonical-output model(s) excluded.
6. **VD threshold sweep**: the visual_dependent share under the strict
   (all/none) and majority (>=2/3, <=1/3) definitions — quantifies how
   threshold-fragile the VD share is.
7. **Split-half stability** of the text_only excess.
8. Optionally (``--design-prefix``): AUC of the continuous per-question
   visual gain against benchmark design labels derived from the question
   ``index`` prefix (e.g. HallusionBench ``VD_*`` vs ``VS_*``) — a
   calibration check of the detector against the benchmark's own intent.

Only pandas/openpyxl are required; the script does not import ``vlmeval``
(same policy as ``rejudge_exact.py``), so it runs on a machine without the
full environment. Answer extraction mirrors
``BaseDetector._extract_mcq_option``.

Examples
--------
$ python scripts/audit_significance.py \
    --full outputs/*/T*/InternVL3-8B_MMStar_gpt-4o-mini_result.xlsx ... \
    --blind outputs/*/T*/InternVL3-8B_MMStar_gpt-4o-mini_result_blind.xlsx ... \
    --out audit_preliminary/mmstar_3models_gpt-4o-mini

Files are paired by list position: the i-th ``--blind`` file must belong to
the same model as the i-th ``--full`` file.
"""
import argparse
import json
import math
import random
import re
import string
from itertools import combinations
from pathlib import Path

import pandas as pd


# --------------------------------------------------------------------------
# extraction (mirrors BaseDetector._extract_mcq_option / rejudge_exact.py)
# --------------------------------------------------------------------------

def extract_option(value, valid):
    """Judge-free MCQ option extraction; returns 'Z' for unparseable."""
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return 'Z'
    s = str(value).strip()
    if s == '':
        return 'Z'
    m = re.fullmatch(r'\W*([A-Za-z])\W*', s)
    if m and m.group(1).upper() in valid:
        return m.group(1).upper()
    m = re.match(r'^\W{0,2}([A-Za-z])\s*[\.\):\-,]', s)
    if m and m.group(1).upper() in valid:
        return m.group(1).upper()
    m = re.search(r'(?:answer|option)\s*(?:is|:)?\s*\(?([A-Za-z])\)?(?![A-Za-z])', s, re.IGNORECASE)
    if m and m.group(1).upper() in valid:
        return m.group(1).upper()
    return 'Z'


def wilson(k, n, z=1.96):
    """Wilson 95% score interval for a binomial proportion."""
    if n == 0:
        return (float('nan'), float('nan'))
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (c - h, c + h)


# --------------------------------------------------------------------------
# core statistics
# --------------------------------------------------------------------------

def category_of(favg, bavg, strict=(0.99, 0.01), gain=0.2):
    """Four-way visual-dependency category for one question."""
    if favg >= strict[0] and bavg <= strict[1]:
        return 'visual_dependent'
    if bavg > favg + gain:
        return 'conflicting_visual_signal'
    if abs(favg - bavg) <= 1e-6:
        return 'text_only'
    if favg - bavg >= gain:
        return 'visual_supplement'
    return 'text_only'


def to_share(fh, bh, ms, items):
    """Share (%) of ``items`` classified text_only (same rule as the detector).

    Uses :func:`category_of`, so small non-zero gaps below the supplement
    threshold also count as text_only — identical to
    ``vlmeval/detector/visual_dependency.py`` for any pool size (for pools
    of <=4 models this coincides with exact equality).
    """
    c = 0
    for i in items:
        favg = sum(fh[m][i] for m in ms) / len(ms)
        bavg = sum(bh[m][i] for m in ms) / len(ms)
        if category_of(favg, bavg) == 'text_only':
            c += 1
    return 100.0 * c / len(items)


def null_excess(fh, bh, ms, items, perms, rng):
    """Observed text_only share, permutation-null mean/sd and p-value.

    The p-value uses the standard permutation correction ``(ge+1)/(N+1)``
    (the observed statistic counts as one member of the null set), so it is
    valid and never reported below ``1/(N+1)``.
    """
    obs = to_share(fh, bh, ms, items)
    vals = []
    for _ in range(perms):
        p = list(items)
        rng.shuffle(p)
        bp = {m: {i: bh[m][p[j]] for j, i in enumerate(items)} for m in ms}
        c = 0
        for i in items:
            favg = sum(fh[m][i] for m in ms) / len(ms)
            bavg = sum(bp[m][i] for m in ms) / len(ms)
            if category_of(favg, bavg) == 'text_only':
                c += 1
        vals.append(100.0 * c / len(items))
    mu = sum(vals) / len(vals)
    sd = (sum((x - mu) ** 2 for x in vals) / len(vals)) ** 0.5
    ge = sum(1 for x in vals if x >= obs)
    return {'observed': obs, 'null_mean': mu, 'null_sd': sd,
            'excess': obs - mu, 'p_value': (ge + 1) / float(len(vals) + 1)}


def unanimous_flags(ans, gt, ms, items):
    """Question ids where every parseable answer is the same non-gold option."""
    out = []
    for i in items:
        vals = [ans[m][i] for m in ms if ans[m][i] != 'Z']
        if len(vals) >= 2 and len(set(vals)) == 1 and vals[0] != gt[i]:
            out.append(i)
    return out


def auc(scores, labels):
    """Rank AUC of ``scores`` for separating labels 1 (positive) vs 0."""
    pos = [s for s, l in zip(scores, labels) if l == 1]
    neg = [s for s, l in zip(scores, labels) if l == 0]
    if not pos or not neg:
        return float('nan')
    wins = 0.0
    for a in pos:
        for b in neg:
            wins += 1.0 if a > b else (0.5 if a == b else 0.0)
    return wins / (len(pos) * len(neg))


# --------------------------------------------------------------------------
# main
# --------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--full', nargs='+', required=True, help='judged eval files, full runs (one per model)')
    ap.add_argument('--blind', nargs='+', required=True, help='judged eval files, blind runs (same model order)')
    ap.add_argument('--out', required=True, help='output directory for significance_report.{json,md}')
    ap.add_argument('--models', nargs='+', default=None,
                    help='model names, one per --full file (default: the full-file stems; '
                         'names must be unique — do NOT rely on filename splitting, model ids may contain underscores)')
    ap.add_argument('--strata-column', default='category', help='dataset column for stratification (default: category)')
    ap.add_argument('--design-prefix', default=None,
                    help="index prefix marking design-positive questions (e.g. 'VD' for HallusionBench); enables the AUC calibration check")
    ap.add_argument('--exclude-from-flips', default=None,
                    help='model-file substring whose model is excluded in the second judge-vs-exact flip count')
    ap.add_argument('--perms', type=int, default=999)
    ap.add_argument('--seed', type=int, default=7)
    args = ap.parse_args()
    if len(args.full) != len(args.blind):
        raise SystemExit('--full and --blind must list the same number of files')

    rng = random.Random(args.seed)
    # File stems are unique by construction; naive splitting on '_' is NOT
    # safe (model ids like GPT4o_MINI contain underscores) — use --models
    # for readable names.
    models = args.models if args.models else [Path(f).stem for f in args.full]
    if len(models) != len(args.full):
        raise SystemExit('--models must list one name per --full file')
    if len(set(models)) != len(models):
        raise SystemExit(f'model names are not unique: {models}')
    F, Bl = {}, {}
    for m, ff, bf in zip(models, args.full, args.blind):
        F[m] = pd.read_excel(ff).sort_values('index').reset_index(drop=True)
        Bl[m] = pd.read_excel(bf).sort_values('index').reset_index(drop=True)
    n = len(F[models[0]])
    ref = F[models[0]]
    gt = [str(a).strip().upper() for a in ref['answer']]
    letters = {c.upper() for c in ref.columns if isinstance(c, str) and len(c) == 1 and c.isalpha()}
    if not letters:
        letters = set(string.ascii_uppercase[:8])
    hit_col = 'hit' if 'hit' in ref.columns else 'score'

    def as_hit(x):
        if isinstance(x, bool):
            return 1 if x else 0
        try:
            v = float(x)
            return 1 if (v == v and v != 0) else 0  # NaN counts as a miss
        except (TypeError, ValueError):
            return 1 if str(x).strip().lower() in ('true', 'yes', 't', '1') else 0

    fh = {m: [as_hit(x) for x in F[m][hit_col]] for m in models}
    bh = {m: [as_hit(x) for x in Bl[m][hit_col]] for m in models}
    fans = {m: [extract_option(v, letters) for v in F[m]['prediction']] for m in models}
    bans = {m: [extract_option(v, letters) for v in Bl[m]['prediction']] for m in models}
    fhx = {m: [1 if (fans[m][i] != 'Z' and fans[m][i] == gt[i]) else 0 for i in range(n)] for m in models}
    bhx = {m: [1 if (bans[m][i] != 'Z' and bans[m][i] == gt[i]) else 0 for i in range(n)] for m in models}

    # MCQ-letter sections only make sense when predictions parse as letters
    # (on yes/no benchmarks extraction yields 'Z' everywhere and the exact
    # arm degenerates); guard on the overall full-run parse rate.
    z_rate = sum(fans[m].count('Z') for m in models) / float(n * len(models))
    mcq_ok = z_rate < 0.5

    all_items = list(range(n))
    rep = {'n_questions': n, 'models': models, 'hit_column': hit_col,
           'perms': args.perms, 'seed': args.seed}

    # 1) headline proportions + Wilson
    to_n = round(to_share(fh, bh, models, all_items) * n / 100)
    unan = unanimous_flags(fans, gt, models, all_items) if mcq_ok else []
    rep['mcq_sections_applicable'] = mcq_ok
    rep['wilson'] = {
        'text_only': {'count': to_n, 'share': 100.0 * to_n / n,
                      'ci95': [100 * x for x in wilson(to_n, n)]},
    }
    if mcq_ok:
        rep['wilson']['unanimous_consensus'] = {
            'count': len(unan), 'share': 100.0 * len(unan) / n,
            'ci95': [100 * x for x in wilson(len(unan), n)]}

    # 2-3) excess: full pool + LOMO
    pools = {'all': models}
    for m in models:
        pools[f'without_{m}'] = [x for x in models if x != m]
    rep['text_only_excess'] = {}
    for pname, ms in pools.items():
        if len(ms) < 2:
            continue
        rep['text_only_excess'][pname] = null_excess(fh, bh, ms, all_items, args.perms, rng)
    ex_vals = [v['excess'] for v in rep['text_only_excess'].values()]
    raw_vals = [v['observed'] for v in rep['text_only_excess'].values()]
    rep['pool_spread'] = {'raw_pp': max(raw_vals) - min(raw_vals),
                          'excess_pp': max(ex_vals) - min(ex_vals)}

    # 4) stratification
    rep['strata'] = {}
    if args.strata_column in ref.columns:
        cats = list(ref[args.strata_column])
        for st in sorted(set(map(str, cats))):
            items = [i for i in range(n) if str(cats[i]) == st]
            if len(items) < 30:
                continue
            r = null_excess(fh, bh, models, items, max(150, args.perms // 2), rng)
            r['n'] = len(items)
            if mcq_ok:
                r['unanimous'] = len(unanimous_flags(fans, gt, models, items))
            rep['strata'][st] = r

    # 5) judge-free primary + flips (MCQ only)
    def cat_list(fhits, bhits, ms):
        return [category_of(sum(fhits[m][i] for m in ms) / len(ms),
                            sum(bhits[m][i] for m in ms) / len(ms)) for i in range(n)]
    if mcq_ok:
        cx = cat_list(fhx, bhx, models)
        from collections import Counter as _C
        dist = _C(cx)
        rep['exact_only_categories'] = {k: 100.0 * v / n for k, v in dist.items()}
        cj = cat_list(fh, bh, models)
        rep['judge_vs_exact_flips'] = {'all_models': sum(1 for a, b in zip(cj, cx) if a != b)}
        if args.exclude_from_flips:
            kept = [m for m in models if args.exclude_from_flips not in m]
            if len(kept) >= 2:
                cj2 = cat_list(fh, bh, kept)
                cx2 = cat_list(fhx, bhx, kept)
                rep['judge_vs_exact_flips'][f'excluding_{args.exclude_from_flips}'] = \
                    sum(1 for a, b in zip(cj2, cx2) if a != b)

    # 6) VD threshold sweep
    sweep = {}
    for tag, (ft, bt) in {'strict_all_none': (0.99, 0.01), 'majority_2of3': (0.66, 0.34)}.items():
        c = sum(1 for i in range(n)
                if sum(fh[m][i] for m in models) / len(models) >= ft
                and sum(bh[m][i] for m in models) / len(models) <= bt)
        sweep[tag] = {'count': c, 'share': 100.0 * c / n}
    rep['vd_threshold_sweep'] = sweep

    # 7) split-half stability of the excess
    diffs = []
    for _ in range(20):
        ii = all_items[:]
        rng.shuffle(ii)
        halves = (ii[:n // 2], ii[n // 2:])
        e = [null_excess(fh, bh, models, h, 60, rng)['excess'] for h in halves]
        diffs.append(abs(e[0] - e[1]))
    diffs.sort()
    rep['split_half_abs_diff_median_pp'] = diffs[len(diffs) // 2]

    # 8) optional design-label AUC
    if args.design_prefix:
        labels = [1 if str(i).startswith(args.design_prefix) else 0 for i in ref['index']]
        gains = [sum(fh[m][i] for m in models) / len(models)
                 - sum(bh[m][i] for m in models) / len(models) for i in range(n)]
        rep['design_label_auc'] = {'prefix': args.design_prefix,
                                   'positives': sum(labels), 'auc': auc(gains, labels)}

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / 'significance_report.json').write_text(
        json.dumps(rep, ensure_ascii=False, indent=2), encoding='utf-8')

    # markdown digest
    md = ['# Significance report (no new runs)', '']
    w = rep['wilson']
    md.append(f"- text_only: **{w['text_only']['share']:.1f}%** "
              f"(Wilson95 [{w['text_only']['ci95'][0]:.1f}, {w['text_only']['ci95'][1]:.1f}])")
    if mcq_ok:
        md.append(f"- unanimous consensus-error: **{w['unanimous_consensus']['share']:.1f}%** "
                  f"({w['unanimous_consensus']['count']} q; Wilson95 "
                  f"[{w['unanimous_consensus']['ci95'][0]:.1f}, {w['unanimous_consensus']['ci95'][1]:.1f}])")
    else:
        md.append('- MCQ-letter sections (unanimous CE, exact-matching arm) skipped: '
                  f'predictions do not parse as option letters (Z-rate {100 * z_rate:.0f}%).')
    md.append('')
    md.append('## text_only: observed vs permutation null (excess is the metric to report)')
    md.append('')
    md.append('| pool | observed | null mean | excess (pp) | p |')
    md.append('|---|---|---|---|---|')
    for pname, v in rep['text_only_excess'].items():
        p = f"{v['p_value']:.4f}"
        md.append(f"| {pname} | {v['observed']:.1f}% | {v['null_mean']:.1f}% | "
                  f"**{v['excess']:+.1f}** | {p} |")
    md.append('')
    md.append(f"Pool spread: raw {rep['pool_spread']['raw_pp']:.1f} pp -> "
              f"excess {rep['pool_spread']['excess_pp']:.1f} pp.")
    if rep['strata']:
        md.append('')
        md.append(f"## Stratified by `{args.strata_column}`")
        md.append('')
        md.append('| stratum | n | observed | excess (pp) | unanimous CE |')
        md.append('|---|---|---|---|---|')
        for st, v in rep['strata'].items():
            un = (f"{v['unanimous']} ({100.0 * v['unanimous'] / v['n']:.1f}%)"
                  if 'unanimous' in v else 'n/a')
            md.append(f"| {st} | {v['n']} | {v['observed']:.1f}% | {v['excess']:+.1f} | {un} |")
    if mcq_ok:
        md.append('')
        md.append('## Judge-free (exact matching) primary numbers')
        md.append('')
        md.append('- categories: ' + ', '.join(f"{k} {v:.1f}%" for k, v in
                                               sorted(rep['exact_only_categories'].items())))
        md.append('- judge-vs-exact category flips: ' + ', '.join(
            f"{k} = {v}" for k, v in rep['judge_vs_exact_flips'].items()))
    md.append('')
    md.append('## VD threshold sweep / split-half')
    md.append('')
    for tag, v in rep['vd_threshold_sweep'].items():
        md.append(f"- VD ({tag}): {v['count']} ({v['share']:.1f}%)")
    md.append(f"- split-half |excess diff| median: {rep['split_half_abs_diff_median_pp']:.1f} pp")
    if 'design_label_auc' in rep:
        d = rep['design_label_auc']
        md.append('')
        md.append(f"## Design-label calibration: AUC = {d['auc']:.3f} "
                  f"(prefix `{d['prefix']}`, {d['positives']} positives; 0.5 = chance)")
    (out / 'significance_report.md').write_text('\n'.join(md) + '\n', encoding='utf-8')
    print(f"wrote {out / 'significance_report.json'}")
    print(f"wrote {out / 'significance_report.md'}")


if __name__ == '__main__':
    main()
