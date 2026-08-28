"""Re-judge existing eval files offline with exact option matching.

Takes an ``outputs/`` tree of judged eval files (``*_<judge>_result.xlsx``
or plain prediction files) and writes a parallel tree in which the ``hit``
column is recomputed as ``extracted_option(prediction) == answer`` using the
same judge-free extraction as the audit detectors
(:meth:`BaseDetector._extract_mcq_option`). No API calls are made.

This provides the ``exact_matching`` arm of the judge-sensitivity study
without re-running any inference or LLM judging: run ``bench_eval`` once on
the original tree (LLM judge) and once on the re-judged tree, then compare
flagged sets with ``scripts/audit_paper_assets.py --judge-run ...``.

Examples
--------
$ python scripts/rejudge_exact.py --src outputs --dst outputs_exact
"""
import argparse
import re
import shutil
import string
from pathlib import Path

import pandas as pd


def extract_option(value, valid):
    """Judge-free MCQ option extraction (mirrors BaseDetector._extract_mcq_option)."""
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


def rejudge_file(src, dst):
    """Recompute the ``hit`` column of one eval file with exact matching."""
    df = pd.read_excel(src) if src.suffix == '.xlsx' else pd.read_csv(src, sep='\t' if src.suffix == '.tsv' else ',')
    if 'prediction' not in df.columns or 'answer' not in df.columns:
        return False
    letters = {c.upper() for c in df.columns if isinstance(c, str) and len(c) == 1 and c.isalpha()}
    if not letters:
        letters = set(string.ascii_uppercase[:8])
    extracted = [extract_option(v, letters) for v in df['prediction']]
    answers = [str(a).strip().upper() if pd.notna(a) else '' for a in df['answer']]
    df['hit'] = [1 if e != 'Z' and e == a else 0 for e, a in zip(extracted, answers)]
    df['exact_extracted'] = extracted
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.suffix == '.xlsx':
        df.to_excel(dst, index=False)
    else:
        df.to_csv(dst, index=False)
    return True


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--src', required=True, help='source outputs tree (LLM-judged)')
    ap.add_argument('--dst', required=True, help='destination tree (exact-matching hits)')
    args = ap.parse_args()

    src_root, dst_root = Path(args.src), Path(args.dst)
    n_done = n_copied = 0
    for p in src_root.rglob('*'):
        if not p.is_file():
            continue
        rel = p.relative_to(src_root)
        q = dst_root / rel
        if p.suffix in ('.xlsx', '.tsv', '.csv'):
            try:
                if rejudge_file(p, q):
                    n_done += 1
                    continue
            except Exception as e:
                print(f'[warn] {rel}: {e}')
        q.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(p, q)
        n_copied += 1
    print(f're-judged {n_done} files, copied {n_copied} as-is -> {dst_root}')


if __name__ == '__main__':
    main()
