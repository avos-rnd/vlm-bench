"""Generate the paper figures and LaTeX tables from audit outputs.

Consumes the ``reports/`` directory of one or more ``bench_eval`` runs and
produces publication assets under ``--out`` (default ``paper/figures``):

- ``fig_scatter_<name>.pdf`` — per-question full-vs-blind accuracy scatter,
  colored by visual-dependency category (Figure "scatter" in the paper);
- ``tab_main.tex`` — the main audit-results table (one row per benchmark);
- ``fig_precision.pdf`` — detector precision bars with Wilson intervals
  (requires ``validation_report.json`` from
  ``scripts/sample_for_annotation.py score``);
- ``tab_judge_sensitivity.tex`` — Jaccard overlap of flagged sets across
  judge protocols (requires several work dirs of the same predictions
  evaluated with different judges).

Examples
--------
$ python scripts/audit_paper_assets.py \
      --run MMStar=outputs_audit_mmstar --run HallusionBench=outputs_audit_hallusion \
      --validation annotation/mmstar/validation_report.json \
      --judge-run exact=outputs_audit_mmstar_exact --judge-run gpt4omini=outputs_audit_mmstar \
      --out paper/figures
"""
import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt  # noqa: E402

CATEGORY_COLORS = {
    'visual_dependent': '#1a7f37',
    'visual_supplement': '#57ab5a',
    'text_only': '#cf222e',
    'conflicting_visual_signal': '#8250df',
}


def _load(p):
    return json.loads(Path(p).read_text(encoding='utf-8'))


def fig_scatter(run_name, work_dir, out_dir):
    """Full-vs-blind per-question accuracy scatter for one benchmark."""
    stat_p = Path(work_dir) / 'reports' / 'visual_dependency' / 'all_stat.json'
    if not stat_p.exists():
        print(f'[skip] {stat_p} not found')
        return
    stats = _load(stat_p)
    fig, ax = plt.subplots(figsize=(4.2, 4.0))
    import random
    rng = random.Random(0)
    for cat, color in CATEGORY_COLORS.items():
        xs = [q['blind_accuracy'] + rng.uniform(-0.02, 0.02) for q in stats if q['category'] == cat]
        ys = [q['full_accuracy'] + rng.uniform(-0.02, 0.02) for q in stats if q['category'] == cat]
        ax.scatter(xs, ys, s=6, alpha=0.35, color=color,
                   label=f'{cat.replace("_", " ")} ({len(xs)})', linewidths=0)
    ax.plot([0, 1], [0, 1], ls='--', lw=0.8, color='gray')
    ax.set_xlabel('blind accuracy (per question, model-averaged)')
    ax.set_ylabel('full accuracy')
    ax.set_xlim(-0.05, 1.05)
    ax.set_ylim(-0.05, 1.05)
    ax.set_title(run_name)
    ax.legend(fontsize=6, loc='lower right', framealpha=0.9)
    fig.tight_layout()
    out = Path(out_dir) / f'fig_scatter_{run_name.lower()}.pdf'
    fig.savefig(out)
    plt.close(fig)
    print(f'[ok] {out}')


def _get(d, *keys, default=None):
    for k in keys:
        if isinstance(d, dict) and k in d:
            d = d[k]
        else:
            return default
    return d


def tab_main(runs, out_dir):
    """One-row-per-benchmark main results table (LaTeX body only)."""
    lines = []
    for name, wd in runs.items():
        vd = _load(Path(wd) / 'reports' / 'visual_dependency.json') \
            if (Path(wd) / 'reports' / 'visual_dependency.json').exists() else {}
        ce_path = Path(wd) / 'reports' / 'consensus_error.json'
        ce = _load(ce_path) if ce_path.exists() else {}
        ce_full = ce.get('full', ce)
        fk_path = Path(wd) / 'reports' / 'fleiss_kappa_agreement.json'
        fk = _load(fk_path) if fk_path.exists() else {}
        fk_full = fk.get('full', fk)
        cd = vd.get('category_distribution', {})
        row = (
            f"{name} & {cd.get('visual_dependent', float('nan')):.1f}"
            f" & {cd.get('visual_supplement', float('nan')):.1f}"
            f" & {cd.get('text_only', float('nan')):.1f}"
            f" & {cd.get('conflicting_visual_signal', float('nan')):.1f}"
            f" & {100 * ce_full.get('consensus_error_rate', float('nan')):.1f}"
            f" ({100 * ce_full.get('unanimous_consensus_error_rate', float('nan')):.1f})"
            f" & {fk_full.get('fleiss_kappa', float('nan')):.2f} \\\\"
        )
        lines.append(row)
    out = Path(out_dir) / 'tab_main.tex'
    out.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(f'[ok] {out}')


def fig_precision(validation_report, out_dir):
    """Detector precision bars with Wilson 95% intervals."""
    rep = _load(validation_report)
    strata = list(rep.get('per_stratum', {}).keys())
    if not strata:
        print('[skip] validation report has no strata')
        return
    ps = [rep['per_stratum'][s]['precision_both_yes'] for s in strata]
    los = [rep['per_stratum'][s]['wilson95'][0] for s in strata]
    his = [rep['per_stratum'][s]['wilson95'][1] for s in strata]
    fig, ax = plt.subplots(figsize=(4.6, 2.8))
    xs = range(len(strata))
    ax.bar(xs, ps, color='#4c78a8', width=0.6)
    ax.errorbar(xs, ps, yerr=[[p - lo for p, lo in zip(ps, los)],
                              [hi - p for p, hi in zip(ps, his)]],
                fmt='none', ecolor='black', capsize=3, lw=1)
    ax.set_xticks(list(xs))
    ax.set_xticklabels([s.replace('_', '\n') for s in strata], fontsize=7)
    ax.set_ylabel('precision (both annotators confirm)')
    ax.set_ylim(0, 1)
    ax.axhline(rep.get('cohen_kappa', float('nan')), ls=':', lw=0.8, color='gray')
    fig.tight_layout()
    out = Path(out_dir) / 'fig_precision.pdf'
    fig.savefig(out)
    plt.close(fig)
    print(f'[ok] {out}')


def _flagged_sets(work_dir):
    """Per-detector sets of flagged question ids from one audit run."""
    agg_p = Path(work_dir) / 'reports' / 'aggregated_findings.json'
    if not agg_p.exists():
        return {}
    agg = _load(agg_p)
    sets = {}
    for qid, rec in agg.get('questions', {}).items():
        for f in rec.get('findings', []):
            det = f.get('detector', 'unknown')
            sets.setdefault(det, set()).add(str(f.get('question_id', qid)))
    return sets


def tab_judge_sensitivity(judge_runs, out_dir):
    """Pairwise Jaccard overlap of flagged sets across judge protocols."""
    per_judge = {j: _flagged_sets(wd) for j, wd in judge_runs.items()}
    judges = list(per_judge.keys())
    detectors = sorted({d for s in per_judge.values() for d in s})
    lines = []
    for det in detectors:
        cells = [det.replace('_', r'\_')]
        for i in range(len(judges)):
            for j in range(i + 1, len(judges)):
                a, b = per_judge[judges[i]].get(det, set()), per_judge[judges[j]].get(det, set())
                jac = len(a & b) / len(a | b) if (a | b) else float('nan')
                cells.append(f'{jac:.2f}')
        lines.append(' & '.join(cells) + r' \\')
    header = 'pairs: ' + ', '.join(f'{judges[i]}-{judges[j]}'
                                   for i in range(len(judges)) for j in range(i + 1, len(judges)))
    out = Path(out_dir) / 'tab_judge_sensitivity.tex'
    out.write_text(f'% {header}\n' + '\n'.join(lines) + '\n', encoding='utf-8')
    print(f'[ok] {out}')


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--run', action='append', default=[],
                    help='NAME=WORK_DIR of an audit run (repeatable)')
    ap.add_argument('--validation', default=None, help='validation_report.json path')
    ap.add_argument('--judge-run', action='append', default=[],
                    help='JUDGE=WORK_DIR of the same predictions audited under a different judge (repeatable)')
    ap.add_argument('--out', default='paper/figures')
    args = ap.parse_args()

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    runs = dict(kv.split('=', 1) for kv in args.run)
    for name, wd in runs.items():
        fig_scatter(name, wd, out_dir)
    if runs:
        tab_main(runs, out_dir)
    if args.validation:
        fig_precision(args.validation, out_dir)
    judge_runs = dict(kv.split('=', 1) for kv in args.judge_run)
    if len(judge_runs) >= 2:
        tab_judge_sensitivity(judge_runs, out_dir)


if __name__ == '__main__':
    main()
