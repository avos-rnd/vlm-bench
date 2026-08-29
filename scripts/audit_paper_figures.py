#!/usr/bin/env python
"""Publication figures for the benchmark-audit paper.

Reads deterministic per-item quantities from the saved evaluation artifacts,
but takes every published aggregate/statistical value from the canonical JSON
emitted by ``audit_significance.py``.  In particular, this renderer never
reruns the permutation null, so figure labels cannot drift from the report.

Produces, into ``--out``:

``fig_visual_dependency.pdf``
    (a) per-question full vs blind accuracy, (b) canonical observed and
    permutation-null mean values with their excess,
    (c) composition of the text-only set (both-wrong vs both-right items).
``fig_strata.pdf``
    text-only excess and unanimous consensus-error rate per dataset
    category -- the two pathologies have opposite category profiles.
``fig_robustness.pdf``
    (a) category shares under the LLM judge vs exact matching,
    (b) per-model attribution of the judge-vs-exact category flips.
``fig_binary_format.pdf`` (only with ``--design-prefix``)
    ROC of the continuous visual gain against the benchmark's own design
    labels, plus the excess split by design label.

Fonts are embedded as TrueType (``pdf.fonttype=42``); NeurIPS accepts
Type 1 or embedded TrueType only, so matplotlib's default Type 3 output
would be a compliance failure.

Example
-------
$ python scripts/audit_paper_figures.py \
    --full  outputs/*/T*/InternVL3-8B_MMStar_gpt-4o-mini_result.xlsx ... \
    --blind outputs/*/T*/InternVL3-8B_MMStar_gpt-4o-mini_result_blind.xlsx ... \
    --models InternVL3-8B Ristretto-3B gpt-5-nano \
    --stats-json audit_preliminary/mmstar_3models_gpt-4o-mini/significance_report.json \
    --out paper/figures
"""
import argparse
import json
import random
import shutil
import string
import subprocess
import sys
from pathlib import Path

import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_significance import (  # noqa: E402
    category_of, extract_option,
)

# ---------------------------------------------------------------- style ----
INK = '#1A1A1A'
MUTED = '#8A8A8A'
BLUE = '#2F5C8F'      # primary / observed
SAND = '#C08A3E'      # null / secondary
RED = '#B4503C'       # pathology
GREEN = '#4E7A5A'     # benign
GRID = '#DCDCDC'

plt.rcParams.update({
    'pdf.fonttype': 42, 'ps.fonttype': 42,
    'font.family': 'serif',
    'font.serif': ['Times New Roman', 'Nimbus Roman', 'DejaVu Serif'],
    'font.size': 7.2, 'axes.titlesize': 7.6, 'axes.labelsize': 7.2,
    'xtick.labelsize': 6.6, 'ytick.labelsize': 6.6, 'legend.fontsize': 6.4,
    'axes.edgecolor': MUTED, 'axes.labelcolor': INK, 'text.color': INK,
    'xtick.color': MUTED, 'ytick.color': MUTED,
    'axes.linewidth': 0.6, 'xtick.major.width': 0.6, 'ytick.major.width': 0.6,
    'xtick.major.size': 2.5, 'ytick.major.size': 2.5,
    'legend.frameon': False, 'figure.dpi': 200,
    'savefig.bbox': 'tight', 'savefig.pad_inches': 0.01,
})


def outline_fonts(path):
    """Convert figure text to vector outlines via ghostscript.

    matplotlib embeds subsetted CID TrueType fonts; NeurIPS accepts only
    Type 1 or embedded TrueType, so outlining removes any ambiguity (and
    keeps figures identical on machines without the same fonts installed).
    Silently skipped when ghostscript is unavailable.
    """
    gs = shutil.which('gs')
    if not gs:
        print(f'  [warn] ghostscript not found; {path.name} keeps its fonts')
        return
    tmp = path.with_suffix('.outlined.pdf')
    subprocess.run([gs, '-q', '-dNOPAUSE', '-dBATCH', '-dNoOutputFonts',
                    '-sDEVICE=pdfwrite', '-dCompatibilityLevel=1.5',
                    f'-sOutputFile={tmp}', str(path)], check=True)
    tmp.replace(path)


def bare(ax, left=True, bottom=True):
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(left)
    ax.spines['bottom'].set_visible(bottom)


def panel_tag(ax, tag):
    ax.set_title(tag, loc='left', fontweight='bold', fontsize=7.6, pad=4)


# ----------------------------------------------------------------- data ----
def load(full, blind, models):
    """Mirror audit_significance.main()'s loading and derived vectors."""
    F = {m: pd.read_excel(f).sort_values('index').reset_index(drop=True)
         for m, f in zip(models, full)}
    B = {m: pd.read_excel(f).sort_values('index').reset_index(drop=True)
         for m, f in zip(models, blind)}
    ref = F[models[0]]
    n = len(ref)
    gt = [str(a).strip().upper() for a in ref['answer']]
    letters = {c.upper() for c in ref.columns
               if isinstance(c, str) and len(c) == 1 and c.isalpha()}
    if not letters:
        letters = set(string.ascii_uppercase[:8])
    hit_col = 'hit' if 'hit' in ref.columns else 'score'

    def as_hit(x):
        if isinstance(x, bool):
            return 1 if x else 0
        try:
            v = float(x)
            return 1 if (v == v and v != 0) else 0
        except (TypeError, ValueError):
            return 1 if str(x).strip().lower() in ('true', 'yes', 't', '1') else 0

    fh = {m: [as_hit(x) for x in F[m][hit_col]] for m in models}
    bh = {m: [as_hit(x) for x in B[m][hit_col]] for m in models}
    fans = {m: [extract_option(v, letters) for v in F[m]['prediction']] for m in models}
    bans = {m: [extract_option(v, letters) for v in B[m]['prediction']] for m in models}
    fhx = {m: [1 if (fans[m][i] != 'Z' and fans[m][i] == gt[i]) else 0
               for i in range(n)] for m in models}
    bhx = {m: [1 if (bans[m][i] != 'Z' and bans[m][i] == gt[i]) else 0
               for i in range(n)] for m in models}
    return dict(F=F, B=B, ref=ref, n=n, gt=gt, models=models,
                fh=fh, bh=bh, fans=fans, bans=bans, fhx=fhx, bhx=bhx)


def avg(h, ms, i):
    return sum(h[m][i] for m in ms) / len(ms)


def load_stats(path, d):
    """Load and validate the canonical report before drawing anything."""
    stats = json.loads(Path(path).read_text(encoding='utf-8'))
    if stats.get('n_questions') != d['n']:
        raise SystemExit(
            f"stats/data size mismatch: {stats.get('n_questions')} != {d['n']}")
    if stats.get('models') != d['models']:
        raise SystemExit(
            f"stats/data model mismatch: {stats.get('models')} != {d['models']}")
    required = ('text_only_excess', 'strata')
    missing = [key for key in required if key not in stats]
    if missing:
        raise SystemExit(f'canonical JSON is missing keys: {missing}')
    return stats


# -------------------------------------------------------------- figures ----
def fig_visual_dependency(d, stats, out):
    ms, n = d['models'], d['n']
    items = list(range(n))
    fav = [avg(d['fh'], ms, i) for i in items]
    bav = [avg(d['bh'], ms, i) for i in items]
    cats = [category_of(fav[i], bav[i]) for i in items]

    fig, axes = plt.subplots(1, 3, figsize=(5.45, 1.86),
                             gridspec_kw={'width_ratios': [1.0, 1.12, 0.94],
                                          'wspace': 0.46})

    # (a) scatter -------------------------------------------------------
    ax = axes[0]
    rng = random.Random(0)
    style = {'text_only': (RED, 'no gain from image'),
             'visual_dependent': (BLUE, 'visual-dependent'),
             'visual_supplement': (GREEN, 'visual supplement'),
             'conflicting_visual_signal': (SAND, 'image hurts')}
    for key in ['visual_supplement', 'visual_dependent',
                'conflicting_visual_signal', 'text_only']:
        xs = [bav[i] + rng.uniform(-.035, .035) for i in items if cats[i] == key]
        ys = [fav[i] + rng.uniform(-.035, .035) for i in items if cats[i] == key]
        ax.scatter(xs, ys, s=1.6, alpha=.45, linewidths=0,
                   color=style[key][0], label=f'{style[key][1]} ({len(xs)})')
    ax.plot([-.05, 1.05], [-.05, 1.05], ls=(0, (3, 3)), lw=.7, color=INK, zorder=0)
    ax.set_xlim(-.09, 1.09); ax.set_ylim(-.09, 1.09)
    ax.set_xticks([0, .5, 1]); ax.set_yticks([0, .5, 1])
    ax.set_xlabel('blind accuracy'); ax.set_ylabel('full accuracy')
    ax.legend(loc='upper center', bbox_to_anchor=(.5, -.30), ncol=2,
              handlelength=.6, labelspacing=.3, borderpad=.05,
              handletextpad=.3, columnspacing=.8, markerscale=3.4)
    bare(ax); panel_tag(ax, 'a')

    # (b) canonical permutation result ----------------------------------
    ax = axes[1]
    canonical = stats['text_only_excess']['all']
    obs = float(canonical['observed'])
    mu = float(canonical['null_mean'])
    excess = float(canonical['excess'])
    raw_obs = 100.0 * cats.count('text_only') / n
    if abs(raw_obs - obs) > 0.051:
        raise SystemExit(f'canonical observed share mismatch: {obs} != {raw_obs}')
    ax.bar([0, 1], [mu, obs], width=.56, color=[SAND, RED], alpha=.85)
    for x, value in enumerate((mu, obs)):
        ax.text(x, value + .35, f'{value:.1f}%', ha='center', fontsize=6.6,
                fontweight='bold')
    ax.annotate('', xy=(1, obs - .6), xytext=(0, mu + .6),
                arrowprops=dict(arrowstyle='->', color=INK, lw=.7))
    ax.text(.5, max(mu, obs) + 2.1, f'{excess:+.1f} pp', ha='center',
            fontsize=6.6, fontweight='bold')
    ax.set_xticks([0, 1]); ax.set_xticklabels(['permutation\nnull mean', 'observed'])
    ax.tick_params(axis='x', length=0)
    ax.set_ylabel('zero-gain share (%)')
    ax.set_ylim(0, max(mu, obs) * 1.28)
    bare(ax); panel_tag(ax, 'b')

    # (c) composition of the text-only set --------------------------------
    ax = axes[2]
    to_items = [i for i in items if cats[i] == 'text_only']
    both_wrong = sum(1 for i in to_items if fav[i] == 0 and bav[i] == 0)
    both_right = sum(1 for i in to_items if fav[i] == 1 and bav[i] == 1)
    partial = len(to_items) - both_wrong - both_right
    parts = [('every model wrong,\nimage or not', both_wrong, '#9C4A3A'),
             ('mixed', partial, '#D3A98F'),
             ('every model right\nwithout the image', both_right, '#C98A6A')]
    ys = [2.0, 1.0, 0.0]
    for y0, (label, v, color) in zip(ys, parts):
        ax.barh(y0, v, height=.34, color=color)
        ax.text(v + 4, y0, str(v), va='center', ha='left', fontsize=6.6,
                fontweight='bold')
        ax.text(0, y0 + .30, label.replace('\n', ' '), va='bottom', ha='left',
                fontsize=5.9, color=INK)
    ax.set_yticks([]); ax.set_ylim(-.45, 2.72)
    ax.set_xlim(0, len(to_items) * .78)
    ax.set_xlabel(f'questions (of {len(to_items)})')
    bare(ax, left=False); panel_tag(ax, 'c')

    fig.savefig(out / 'fig_visual_dependency.pdf')
    plt.close(fig)
    outline_fonts(out / 'fig_visual_dependency.pdf')
    return {'observed': obs, 'null_mean': mu, 'excess': excess,
            'text_only_n': len(to_items), 'both_wrong': both_wrong,
            'both_right': both_right, 'mixed': partial,
            'counts': {k: cats.count(k) for k in set(cats)}}


def fig_strata(d, stats, column, out):
    rows = []
    for st, value in stats['strata'].items():
        n = int(value['n'])
        unan_n = int(value.get('unanimous', 0))
        rows.append({'stratum': st, 'n': n, 'excess': float(value['excess']),
                     'unan': 100.0 * unan_n / n, 'unan_n': unan_n})
    rows.sort(key=lambda r: r['excess'])
    labels = [r['stratum'].replace('&', '\\&') if False else r['stratum'] for r in rows]
    y = range(len(rows))

    fig, axes = plt.subplots(1, 2, figsize=(5.45, 1.82),
                             gridspec_kw={'wspace': 0.08})

    ax = axes[0]
    for i, r in zip(y, rows):
        ax.barh(i, r['excess'], height=.62,
                color=RED if r['excess'] > 0 else GREEN, alpha=.88)
        off = 3 if r['excess'] > 0 else -3
        ax.text(r['excess'] + (0.25 if r['excess'] > 0 else -0.25), i,
                f"{r['excess']:+.1f}", va='center',
                ha='left' if r['excess'] > 0 else 'right', fontsize=6.2)
    ax.axvline(0, color=INK, lw=.7)
    ax.set_yticks(list(y)); ax.set_yticklabels(labels, fontsize=6.6)
    ax.tick_params(axis='y', length=0)
    ax.set_xlabel('zero-gain excess over null (pp)')
    ax.set_xlim(-3.2, 9.4)
    bare(ax, left=False); panel_tag(ax, 'a  zero-gain excess')

    ax = axes[1]
    for i, r in zip(y, rows):
        ax.barh(i, r['unan'], height=.62, color=BLUE, alpha=.85)
        ax.text(r['unan'] + .25, i, f"{r['unan']:.1f}%", va='center',
                ha='left', fontsize=6.2)
    ax.set_yticks(list(y)); ax.set_yticklabels([])
    ax.tick_params(axis='y', length=0)
    ax.set_xlabel('unanimous label-conflict candidates (\\%)'.replace('\\', ''))
    ax.set_xlim(0, 18)
    bare(ax, left=False); panel_tag(ax, 'b  label-conflict candidates')

    fig.savefig(out / 'fig_strata.pdf')
    plt.close(fig)
    outline_fonts(out / 'fig_strata.pdf')
    return rows


def fig_robustness(d, out):
    ms, n = d['models'], d['n']
    items = list(range(n))
    order = ['visual_dependent', 'visual_supplement', 'text_only',
             'conflicting_visual_signal']
    nice = ['visual-\ndependent', 'visual\nsupplement', 'no gain\nfrom image',
            'image\nhurts']
    judged = [category_of(avg(d['fh'], ms, i), avg(d['bh'], ms, i)) for i in items]
    exact = [category_of(avg(d['fhx'], ms, i), avg(d['bhx'], ms, i)) for i in items]
    jshare = [100.0 * judged.count(k) / n for k in order]
    eshare = [100.0 * exact.count(k) / n for k in order]

    fig, axes = plt.subplots(1, 2, figsize=(5.45, 1.62),
                             gridspec_kw={'width_ratios': [1.42, 1], 'wspace': .3})

    ax = axes[0]
    xs = range(len(order))
    w = .36
    ax.bar([x - w / 2 for x in xs], jshare, w, color=BLUE, alpha=.9,
           label='LLM judge (gpt-4o-mini)')
    ax.bar([x + w / 2 for x in xs], eshare, w, color=SAND, alpha=.9,
           label='exact matching')
    for x, (a, b) in enumerate(zip(jshare, eshare)):
        ax.text(x - w / 2, a + 1.1, f'{a:.1f}', ha='center', fontsize=6.0)
        ax.text(x + w / 2, b + 1.1, f'{b:.1f}', ha='center', fontsize=6.0)
        ax.text(x, max(a, b) + 5.0, f'$\\Delta${abs(a - b):.1f}', ha='center',
                fontsize=6.0, color=MUTED)
    ax.set_xticks(list(xs)); ax.set_xticklabels(nice, fontsize=6.4)
    ax.tick_params(axis='x', length=0)
    ax.set_ylabel('share of questions (\\%)'.replace('\\', ''))
    ax.set_ylim(0, 74)
    ax.legend(loc='upper right', handlelength=.9, borderpad=.05,
              labelspacing=.3, handletextpad=.4)
    bare(ax); panel_tag(ax, 'a  same conclusions without a judge')

    # per-model source of the disagreement: judge vs letter parser
    ax = axes[1]
    flips_total = sum(1 for i in items if judged[i] != exact[i])
    attrib = []
    for m in ms:
        dis = (sum(1 for i in items if d['fh'][m][i] != d['fhx'][m][i])
               + sum(1 for i in items if d['bh'][m][i] != d['bhx'][m][i]))
        unparsed = 100.0 * d['fans'][m].count('Z') / n
        attrib.append((m, dis, unparsed))
    vals = [v for _, v, _ in attrib]
    ax.bar(range(len(vals)), vals, width=.55,
           color=[GREEN if v == 0 else RED for v in vals], alpha=.9)
    top = max(vals) if max(vals) else 1
    for x, (m, v, u) in enumerate(attrib):
        ax.text(x, v + top * .04, str(v), ha='center', fontsize=6.8,
                fontweight='bold')
    ax.set_xticks(range(len(vals)))
    ax.set_xticklabels([f'{m}\n{u:.0f}% unparsed' for m, _, u in attrib],
                       fontsize=6.0, linespacing=1.25)
    ax.tick_params(axis='x', length=0)
    ax.set_ylabel('items scored differently')
    ax.set_ylim(0, top * 1.18)
    bare(ax); panel_tag(ax, 'b  one model causes every flip')

    fig.savefig(out / 'fig_robustness.pdf')
    plt.close(fig)
    outline_fonts(out / 'fig_robustness.pdf')
    return {'judged': dict(zip(order, jshare)), 'exact': dict(zip(order, eshare)),
            'flips_total': flips_total,
            'attribution': {m: (v, u) for m, v, u in attrib}}


def fig_binary_format(d, stats, prefix, out):
    """HallusionBench: the detector does not recover the design labels."""
    ms, n = d['models'], d['n']
    items = list(range(n))
    idx = [str(v) for v in d['ref']['index']]
    lab = [1 if idx[i].startswith(prefix) else 0 for i in items]
    gain = [avg(d['fh'], ms, i) - avg(d['bh'], ms, i) for i in items]
    calibration = stats.get('design_label_auc')
    if not calibration or calibration.get('prefix') != prefix:
        raise SystemExit(f'canonical JSON lacks design-label AUC for {prefix!r}')
    a = float(calibration['auc'])

    # ROC points
    pairs = sorted(zip(gain, lab), key=lambda t: -t[0])
    P, N = sum(lab), len(lab) - sum(lab)
    tp = fp = 0
    xs, ys = [0.0], [0.0]
    for _, l in pairs:
        tp += (l == 1); fp += (l == 0)
        xs.append(fp / N); ys.append(tp / P)

    fig, axes = plt.subplots(1, 2, figsize=(5.45, 1.75),
                             gridspec_kw={'width_ratios': [1, 1.05], 'wspace': .32})
    ax = axes[0]
    ax.plot(xs, ys, color=BLUE, lw=1.2)
    ax.plot([0, 1], [0, 1], ls=(0, (3, 3)), lw=.7, color=INK)
    ax.text(.55, .28, f'AUC = {a:.2f}\n(chance = 0.50)', fontsize=6.8, color=BLUE,
            linespacing=1.2)
    ax.set_xlabel('false-positive rate'); ax.set_ylabel('true-positive rate')
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    ax.set_xticks([0, .5, 1]); ax.set_yticks([0, .5, 1])
    bare(ax); panel_tag(ax, 'a  visual gain vs design label')

    ax = axes[1]
    res = []
    for name, key in ((f'design {prefix}', prefix), ('design VS', 'VS')):
        value = stats['strata'].get(key)
        if value is None:
            raise SystemExit(f'canonical JSON lacks stratum {key!r}')
        res.append((name, int(value['n']), float(value['excess'])))
    ax.bar(range(len(res)), [r[2] for r in res], width=.5,
           color=[SAND, RED], alpha=.9)
    for x, r in enumerate(res):
        ax.text(x, r[2] + .18, f'+{r[2]:.1f} pp', ha='center', fontsize=6.6,
                fontweight='bold')
    ax.set_xticks(range(len(res)))
    ax.set_xticklabels([f'{r[0]}\n(n={r[1]})' for r in res], fontsize=6.4,
                       linespacing=1.25)
    ax.tick_params(axis='x', length=0)
    ax.tick_params(axis='x', length=0)
    ax.set_ylabel('zero-gain excess (pp)')
    ax.set_ylim(0, max(r[2] for r in res) * 1.3)
    bare(ax); panel_tag(ax, 'b  the one surviving signal')

    fig.savefig(out / 'fig_binary_format.pdf')
    plt.close(fig)
    outline_fonts(out / 'fig_binary_format.pdf')
    return {'auc': a, 'by_design': {r[0]: r[2] for r in res}}


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--full', nargs='+', required=True)
    ap.add_argument('--blind', nargs='+', required=True)
    ap.add_argument('--models', nargs='+', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--stats-json', required=True,
                    help='canonical significance_report.json; figures never rerun permutations')
    ap.add_argument('--strata-column', default='category')
    ap.add_argument('--design-prefix', default=None)
    args = ap.parse_args()

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    d = load(args.full, args.blind, args.models)
    stats = load_stats(args.stats_json, d)

    if args.design_prefix:
        print('binary-format figure:',
              fig_binary_format(d, stats, args.design_prefix, out))
        return
    print('visual dependency:', fig_visual_dependency(d, stats, out))
    print('robustness:', fig_robustness(d, out))
    for r in fig_strata(d, stats, args.strata_column, out):
        print('  stratum', r)


if __name__ == '__main__':
    main()
