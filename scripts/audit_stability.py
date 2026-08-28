"""Stability analyses for the visual-dependency audit.

Reads the enriched per-question export of the ``visual_dependency`` detector
(``reports/visual_dependency/all_stat.json``, which carries per-model
correctness) and computes the three robustness numbers the paper needs:

1. **Bootstrap CI** — 95% percentile intervals for each category share,
   resampling questions with replacement;
2. **Leave-one-model-out (LOMO)** — category shares recomputed with each
   model dropped, reported as min/max ranges;
3. **Threshold sweep** — category shares over a grid of detector thresholds.

Writes ``stability_report.json`` (and prints a compact summary) to ``--out``.

Examples
--------
$ python scripts/audit_stability.py \
      --all-stat outputs_audit_mmstar/reports/visual_dependency/all_stat.json \
      --out outputs_audit_mmstar/reports/visual_dependency
"""
import argparse
import json
import random
from collections import Counter
from pathlib import Path

CATEGORIES = ['visual_dependent', 'visual_supplement', 'text_only', 'conflicting_visual_signal']

DEFAULT_THRESH = dict(full=0.99, blind=0.01, supplement=0.2, conflict=0.2)


def classify(full_acc, blind_acc, th):
    """Reproduce the VisualDependencyDetector category rule."""
    if full_acc >= th['full'] and blind_acc <= th['blind']:
        return 'visual_dependent'
    if blind_acc > full_acc + th['conflict']:
        return 'conflicting_visual_signal'
    if abs(full_acc - blind_acc) <= 1e-6:
        return 'text_only'
    if (full_acc - blind_acc) >= th['supplement']:
        return 'visual_supplement'
    return 'text_only'


def shares(cats):
    """Percentage share per category."""
    n = len(cats)
    c = Counter(cats)
    return {k: 100.0 * c.get(k, 0) / n if n else float('nan') for k in CATEGORIES}


def accuracies(q, drop_model=None):
    """Model-averaged full/blind accuracy of one question, optionally dropping a model."""
    pm = q['per_model']
    models = [m for m in pm if m != drop_model]
    full = sum(pm[m]['full'] for m in models) / len(models)
    blind = sum(pm[m]['blind'] for m in models) / len(models)
    return full, blind


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--all-stat', required=True, help='visual_dependency/all_stat.json (with per_model)')
    ap.add_argument('--bootstrap', type=int, default=10000)
    ap.add_argument('--seed', type=int, default=2026)
    ap.add_argument('--out', required=True)
    args = ap.parse_args()

    stats = json.loads(Path(args.all_stat).read_text(encoding='utf-8'))
    if not stats or 'per_model' not in stats[0]:
        raise SystemExit('all_stat.json has no per_model field — regenerate the audit with current code.')
    models = list(stats[0]['per_model'].keys())
    th = dict(DEFAULT_THRESH)

    base_cats = [classify(*accuracies(q), th) for q in stats]
    report = {'n_questions': len(stats), 'models': models,
              'thresholds': th, 'base_shares': shares(base_cats)}

    # 1) bootstrap over questions
    rng = random.Random(args.seed)
    boot = {k: [] for k in CATEGORIES}
    n = len(base_cats)
    for _ in range(args.bootstrap):
        sample = [base_cats[rng.randrange(n)] for _ in range(n)]
        s = shares(sample)
        for k in CATEGORIES:
            boot[k].append(s[k])
    report['bootstrap_ci95'] = {}
    for k in CATEGORIES:
        v = sorted(boot[k])
        report['bootstrap_ci95'][k] = [v[int(0.025 * len(v))], v[int(0.975 * len(v)) - 1]]

    # 2) leave-one-model-out
    lomo = {}
    for m in models:
        cats = [classify(*accuracies(q, drop_model=m), th) for q in stats]
        lomo[m] = shares(cats)
    report['leave_one_model_out'] = lomo
    report['lomo_range'] = {k: [min(v[k] for v in lomo.values()), max(v[k] for v in lomo.values())]
                            for k in CATEGORIES}

    # 3) threshold sweep
    sweep = []
    for supp in (0.1, 0.2, 0.3):
        for conf in (0.1, 0.2, 0.3):
            for fullt, blindt in ((0.99, 0.01), (0.75, 0.25)):
                t = dict(full=fullt, blind=blindt, supplement=supp, conflict=conf)
                cats = [classify(*accuracies(q), t) for q in stats]
                sweep.append({'thresholds': t, 'shares': shares(cats)})
    report['threshold_sweep'] = sweep

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / 'stability_report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')

    print(f"n={report['n_questions']}, models={models}")
    for k in CATEGORIES:
        lo, hi = report['bootstrap_ci95'][k]
        rlo, rhi = report['lomo_range'][k]
        print(f"{k:26s} {report['base_shares'][k]:5.1f}%  boot95=[{lo:.1f},{hi:.1f}]  lomo=[{rlo:.1f},{rhi:.1f}]")
    print(f"-> {out / 'stability_report.json'}")


if __name__ == '__main__':
    main()
