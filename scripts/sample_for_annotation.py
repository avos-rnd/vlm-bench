"""Build and score the human-verification sample for the benchmark audit.

Two subcommands:

``sample``
    Draw a stratified random sample of flagged questions from an audit run
    (``reports/aggregated_findings.json``) and write annotator CSVs
    (identical content, independently shuffled per annotator) plus a hidden
    answer-key JSON with detector metadata.

``score``
    Given the two filled annotator CSVs, compute per-detector precision
    (with Wilson 95% intervals), Cohen's kappa between annotators, and an
    adjudication worklist of disagreements.

Examples
--------
$ python scripts/sample_for_annotation.py sample \
      --work-dir outputs_audit_mmstar --dataset-tsv ~/LMUData/MMStar.tsv \
      --per-stratum 50 --seed 2026 --out annotation/mmstar
$ python scripts/sample_for_annotation.py score \
      --a annotation/mmstar/annotator_A_filled.csv \
      --b annotation/mmstar/annotator_B_filled.csv \
      --key annotation/mmstar/key.json --out annotation/mmstar
"""
import argparse
import json
import math
import random
from pathlib import Path

import pandas as pd

# Strata: (name, detector, severities) — edit to match the paper design.
STRATA = [
    ('consensus_error', 'consensus_error', ('critical', 'warning')),
    ('visual_dependency', 'visual_dependency', ('critical',)),
    ('distractor_similarity', 'distractor_similarity', ('critical', 'warning')),
]

ANNOTATION_COLUMNS = [
    # verdict: for consensus_error -> is the gold label wrong? (yes/no/ambiguous)
    #          for visual_dependency -> is the question answerable without the image? (yes/no/ambiguous)
    #          for distractor_similarity -> are the flagged options effectively duplicates? (yes/no/ambiguous)
    'verdict',
    'comment',
]


def load_findings(work_dir):
    """Load aggregated findings from an audit work dir.

    Parameters
    ----------
    work_dir : str or Path
        Audit output directory (parent of ``reports/``).

    Returns
    -------
    list of dict
        Flat list of findings.
    """
    p = Path(work_dir) / 'reports' / 'aggregated_findings.json'
    data = json.loads(p.read_text(encoding='utf-8'))
    out = []
    # 'by_detector' holds only example heads; 'questions' carries every finding
    for qid, rec in data.get('questions', {}).items():
        for f in rec.get('findings', []):
            f = dict(f)
            f['question_id'] = f.get('question_id', qid)
            out.append(f)
    return out


def cmd_sample(args):
    findings = load_findings(args.work_dir)
    ds = pd.read_csv(args.dataset_tsv, sep='\t') if args.dataset_tsv else None
    rng = random.Random(args.seed)

    rows, key = [], {}
    for name, detector, severities in STRATA:
        cand = [f for f in findings
                if f.get('detector') == detector and f.get('severity') in severities]
        # unique by question id, deterministic order before shuffle
        seen, uniq = set(), []
        for f in sorted(cand, key=lambda x: str(x.get('question_id'))):
            q = str(f.get('question_id'))
            if q not in seen:
                seen.add(q)
                uniq.append(f)
        rng.shuffle(uniq)
        take = uniq[:args.per_stratum]
        print(f'stratum {name}: {len(uniq)} candidates -> sampled {len(take)}')
        for f in take:
            qid = f.get('question_id')
            item = {
                'item_id': f'{name}:{qid}',
                'stratum': name,
                'question_id': qid,
                'question': None, 'A': None, 'B': None, 'C': None, 'D': None,
                'gold_answer': None,
            }
            if ds is not None and 'index' in ds.columns:
                row = ds[ds['index'].astype(str) == str(qid)]
                if len(row):
                    r = row.iloc[0]
                    item['question'] = r.get('question')
                    for c in ['A', 'B', 'C', 'D']:
                        item[c] = r.get(c)
                    item['gold_answer'] = r.get('answer')
            rows.append(item)
            key[item['item_id']] = {k: v for k, v in f.items()}

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    base = pd.DataFrame(rows)
    for c in ANNOTATION_COLUMNS:
        base[c] = ''
    for annot in ['A', 'B']:
        shuffled = base.sample(frac=1.0, random_state=args.seed + ord(annot)).reset_index(drop=True)
        shuffled.to_csv(out / f'annotator_{annot}.csv', index=False)
    (out / 'key.json').write_text(json.dumps(key, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'Wrote {len(base)} items to {out}/annotator_A.csv, annotator_B.csv (+ key.json).')
    print('Annotators must NOT open key.json before finishing.')


def wilson(p_hat, n, z=1.96):
    """Wilson 95% score interval for a binomial proportion."""
    if n == 0:
        return (float('nan'), float('nan'))
    denom = 1 + z ** 2 / n
    center = (p_hat + z ** 2 / (2 * n)) / denom
    half = z * math.sqrt(p_hat * (1 - p_hat) / n + z ** 2 / (4 * n ** 2)) / denom
    return (center - half, center + half)


def cohen_kappa(a, b):
    """Cohen's kappa for two equal-length label lists."""
    assert len(a) == len(b) and len(a) > 0
    cats = sorted(set(a) | set(b))
    n = len(a)
    po = sum(1 for x, y in zip(a, b) if x == y) / n
    pe = sum((a.count(c) / n) * (b.count(c) / n) for c in cats)
    return (po - pe) / (1 - pe) if pe < 1 else float('nan')


def cmd_score(args):
    da = pd.read_csv(args.a).set_index('item_id')
    db = pd.read_csv(args.b).set_index('item_id')
    common = da.index.intersection(db.index)
    da, db = da.loc[common], db.loc[common]
    va = [str(x).strip().lower() for x in da['verdict']]
    vb = [str(x).strip().lower() for x in db['verdict']]
    kappa = cohen_kappa(va, vb)

    report = {'n_items': int(len(common)), 'cohen_kappa': kappa, 'per_stratum': {}}
    disagreements = []
    for stratum in da['stratum'].unique():
        mask = da['stratum'] == stratum
        ids = da.index[mask]
        # true positive = both annotators say 'yes' (flag confirmed);
        # disagreement -> adjudicate, excluded from the headline precision here
        both_yes = sum(1 for i in ids if str(da.loc[i, 'verdict']).strip().lower() == 'yes'
                       and str(db.loc[i, 'verdict']).strip().lower() == 'yes')
        both_done = sum(1 for i in ids
                        if str(da.loc[i, 'verdict']).strip().lower() in ('yes', 'no', 'ambiguous')
                        and str(db.loc[i, 'verdict']).strip().lower() in ('yes', 'no', 'ambiguous'))
        p = both_yes / both_done if both_done else float('nan')
        lo, hi = wilson(p, both_done) if both_done else (float('nan'), float('nan'))
        report['per_stratum'][stratum] = {
            'n_scored': int(both_done), 'precision_both_yes': p,
            'wilson95': [lo, hi],
        }
        for i in ids:
            if str(da.loc[i, 'verdict']).strip().lower() != str(db.loc[i, 'verdict']).strip().lower():
                disagreements.append({'item_id': i,
                                      'A': str(da.loc[i, 'verdict']),
                                      'B': str(db.loc[i, 'verdict'])})
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / 'validation_report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    pd.DataFrame(disagreements).to_csv(out / 'adjudication_worklist.csv', index=False)
    print(json.dumps(report, indent=2))
    print(f'{len(disagreements)} disagreements -> {out}/adjudication_worklist.csv')


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest='cmd', required=True)
    s = sub.add_parser('sample')
    s.add_argument('--work-dir', required=True)
    s.add_argument('--dataset-tsv', default=None, help='LMUData TSV of the benchmark (adds question text/options)')
    s.add_argument('--per-stratum', type=int, default=50)
    s.add_argument('--seed', type=int, default=2026)
    s.add_argument('--out', required=True)
    s.set_defaults(func=cmd_sample)
    c = sub.add_parser('score')
    c.add_argument('--a', required=True)
    c.add_argument('--b', required=True)
    c.add_argument('--key', default=None)
    c.add_argument('--out', required=True)
    c.set_defaults(func=cmd_score)
    args = ap.parse_args()
    args.func(args)


if __name__ == '__main__':
    main()
