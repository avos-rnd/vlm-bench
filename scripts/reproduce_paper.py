"""Validate supplied eval files, reproduce paper statistics, and check published headlines.

This driver never performs model inference. It reads the original prediction files
from the directory supplied with ``--input-dir``; it does not reconstruct them from
aggregate Markdown reports.
"""
import argparse
import hashlib
import importlib.metadata
import json
import platform
import subprocess
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
MODELS = ['InternVL3-8B', 'Ristretto-3B', 'gpt-5-nano-2025-08-07']
SIZES = {'MMStar': 1500, 'HallusionBench': 951}


def validate_inputs(input_dir, benchmark):
    files = [input_dir / benchmark / f'{model}_{side}.xlsx'
             for side in ('full', 'blind') for model in MODELS]
    missing = [str(path) for path in files if not path.is_file()]
    if missing:
        raise ValueError('Missing original evaluation files:\n' + '\n'.join(missing)
                         + '\nSee docs/en/ReproducingPaper.md. Raw predictions are expected under paper-inputs/ '
                         '(or the directory supplied with --input-dir).')
    reference = None
    records = []
    for path in files:
        frame = pd.read_excel(path)
        required = {'index', 'prediction', 'answer', 'category'}
        if benchmark == 'MMStar':
            required.update('ABCD')
        absent = required - set(frame.columns)
        if absent or not ({'hit', 'score'} & set(frame.columns)):
            raise ValueError(f'{path}: missing required columns {sorted(absent)}; hit or score is also required')
        if len(frame) != SIZES[benchmark] or frame['index'].isna().any() or frame['index'].duplicated().any():
            raise ValueError(f'{path}: expected {SIZES[benchmark]} unique, non-null question IDs')
        frame = frame.sort_values('index').reset_index(drop=True)
        metadata = frame[['index', 'answer', 'category']].astype(str)
        if reference is None:
            reference = metadata
            hit_column = 'hit' if 'hit' in frame.columns else 'score'
        if not metadata.equals(reference) or hit_column not in frame.columns:
            raise ValueError(f'{path}: question IDs, gold labels, categories, or correctness columns differ across arms/models')
        records.append({'path': str(path.resolve()), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                        'rows': len(frame)})
    return files[:3], files[3:], records


def check_headlines(benchmark, stats):
    pool = stats['text_only_excess']['all']
    actual = {'questions': stats['n_questions'], 'observed_pct': round(pool['observed'], 1),
              'null_pct': round(pool['null_mean'], 1), 'excess_pp': round(pool['excess'], 1),
              'permutation_p': round(pool['p_value'], 4)}
    if benchmark == 'MMStar':
        actual['unanimous_candidates'] = stats['wilson']['unanimous_consensus']['count']
        expected = {'questions': 1500, 'observed_pct': 20.2, 'null_pct': 17.0,
                    'excess_pp': 3.2, 'permutation_p': 0.001, 'unanimous_candidates': 134}
    else:
        actual['design_label_auc'] = round(stats['design_label_auc']['auc'], 3)
        expected = {'questions': 951, 'observed_pct': 23.9, 'null_pct': 18.5,
                    'excess_pp': 5.4, 'permutation_p': 0.001, 'design_label_auc': 0.492}
    return {'actual': actual, 'expected': expected, 'matches': actual == expected}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input-dir', type=Path, required=True, help='Directory containing MMStar/ and HallusionBench/ eval files')
    parser.add_argument('--out', type=Path, default=Path('outputs/paper-reproduction'))
    parser.add_argument('--benchmarks', nargs='+', choices=list(SIZES), default=list(SIZES))
    parser.add_argument('--figures', action='store_true', help='Also regenerate statistical figures; pipeline diagram is authored separately')
    args = parser.parse_args()
    try:
        inputs = {benchmark: validate_inputs(args.input_dir, benchmark) for benchmark in args.benchmarks}
    except ValueError as error:
        parser.exit(2, f'{error}\n')
    args.out.mkdir(parents=True, exist_ok=True)
    commit = subprocess.run(['git', '-C', str(ROOT), 'rev-parse', 'HEAD'], capture_output=True, text=True)
    manifest = {'release': 'arxiv-v1.1', 'paper': 'https://arxiv.org/abs/2610.13548',
                'git_commit': commit.stdout.strip() if commit.returncode == 0 else None,
                'python': platform.python_version(), 'seed': 7, 'permutations': 999,
                'packages': {name: importlib.metadata.version(name) for name in ('numpy', 'pandas', 'openpyxl', 'matplotlib')},
                'inputs': [], 'commands': [], 'headline_checks': {}}
    for benchmark, (full, blind, records) in inputs.items():
        out = args.out / benchmark
        common = ['--full', *map(str, full), '--blind', *map(str, blind), '--models', *MODELS,
                  '--strata-column', 'category']
        if benchmark == 'HallusionBench':
            common += ['--design-prefix', 'VD']
        command = [sys.executable, str(ROOT / 'scripts/audit_significance.py'), *common,
                   '--perms', '999', '--seed', '7', '--exclude-from-flips', 'gpt-5-nano', '--out', str(out)]
        manifest['inputs'].extend(records)
        manifest['commands'].append(command)
        subprocess.run(command, check=True)
        stats = json.loads((out / 'significance_report.json').read_text())
        manifest['headline_checks'][benchmark] = check_headlines(benchmark, stats)
        if args.figures:
            command = [sys.executable, str(ROOT / 'scripts/audit_paper_figures.py'), *common,
                       '--stats-json', str(out / 'significance_report.json'), '--out', str(out / 'figures')]
            manifest['commands'].append(command)
            subprocess.run(command, check=True)
    (args.out / 'reproduction_manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print(json.dumps(manifest['headline_checks'], indent=2))
    if not all(result['matches'] for result in manifest['headline_checks'].values()):
        raise SystemExit('Headline mismatch: verify input provenance, model order, judging, and package versions.')


if __name__ == '__main__':
    main()
