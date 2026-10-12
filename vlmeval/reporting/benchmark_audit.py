"""Aggregation layer of the benchmark-audit pipeline.

Collects per-question findings emitted by the detectors (JSON reports under
``<work_dir>/reports/``) into a single machine-readable summary
(``aggregated_findings.json``) and a human-readable markdown digest
(``benchmark_audit_report.md``). Findings are grouped by detector, severity
and question id, so that a benchmark maintainer can triage the most
suspicious questions first.
"""
from pathlib import Path
import json
from collections import defaultdict, Counter
from typing import Any, Dict, List, Tuple


class BenchmarkAuditReportGenerator:
    """Aggregate detector findings into audit artifacts.

    Examples
    --------
    >>> gen = BenchmarkAuditReportGenerator()
    >>> gen.generate('outputs')  # doctest: +SKIP
    {'aggregated_path': 'outputs/reports/aggregated_findings.json',
     'markdown_path': 'outputs/reports/benchmark_audit_report.md'}
    """

    def generate(self, out_dir: str, detector_names=None) -> Dict[str, Any]:
        """Aggregate all detector findings found under ``out_dir/reports``.

        Each canonical detector report containing a top-level ``findings`` list (or
        ``full``/``blind`` sub-reports with such lists) contributes its
        findings. Legacy side exports are used only if the canonical report has no
        findings. Repeated aggregation never consumes its own output.

        Parameters
        ----------
        out_dir : str
            Audit work directory (the parent of ``reports/``).

        detector_names : iterable of str, optional
            Restrict aggregation to detectors executed in the current run; older
            reports from skipped or failed detectors are ignored.

        Returns
        -------
        dict
            Paths of the generated artifacts:
            ``{'aggregated_path': ..., 'markdown_path': ...}``.

        Raises
        ------
        FileNotFoundError
            If ``<out_dir>/reports`` does not exist.
        """
        out = Path(out_dir)
        rpt_dir = out / 'reports'
        if not rpt_dir.exists():
            raise FileNotFoundError(f"Reports directory not found: {rpt_dir}")

        # Prefer canonical detector reports. Side exports remain a legacy fallback;
        # reading both would count the same finding twice. Ignore our own outputs.
        selected = set(detector_names) if detector_names is not None else None
        reports = {}
        for path in sorted(rpt_dir.glob('*.json')):
            if path.name == 'aggregated_findings.json' or (selected is not None and path.stem not in selected):
                continue
            try:
                data = json.loads(path.read_text(encoding='utf-8'))
            except (OSError, ValueError):
                continue
            if isinstance(data, dict):
                reports[path] = data

        scores: List[Tuple[str, float]] = []
        findings_list = []
        covered_detectors = set()

        def collect_findings(data):
            if isinstance(data.get('findings'), list):
                return [dict(f) for f in data['findings']]
            findings = []
            for side in ('full', 'blind'):
                section = data.get(side)
                if isinstance(section, dict) and isinstance(section.get('findings'), list):
                    findings.extend(dict(f, comparison_side=side) for f in section['findings'])
            return findings

        for path, data in reports.items():
            score = data.get('score')
            if isinstance(score, (int, float)) and 0.0 <= score <= 1.0:
                scores.append((path.name, float(score)))
            has_findings = isinstance(data.get('findings'), list) or any(
                isinstance(data.get(side), dict) and isinstance(data[side].get('findings'), list)
                for side in ('full', 'blind'))
            if has_findings:
                covered_detectors.add(data.get('detector', path.stem))
                findings_list.extend(collect_findings(data))

        for path in sorted(rpt_dir.rglob('*_findings.json')):
            if path.parent == rpt_dir:
                continue
            try:
                data = json.loads(path.read_text(encoding='utf-8'))
            except (OSError, ValueError):
                continue
            if (isinstance(data, dict)
                    and data.get('detector', path.parent.name) not in covered_detectors
                    and (selected is None or data.get('detector', path.parent.name) in selected)):
                findings_list.extend(collect_findings(data))

        bench_score = sum(score for _, score in scores) / len(scores) if scores else None
        aggregated = {'total_findings': 0, 'by_detector': {}, 'by_severity': {}, 'questions': {}}

        # Build aggregates
        by_detector = defaultdict(list)
        by_severity = defaultdict(list)
        questions = defaultdict(list)

        for f in findings_list:
            det = f.get('detector', 'unknown')
            sev = f.get('severity', 'info')
            qid = f.get('question_id', None)
            by_detector[det].append(f)
            by_severity[sev].append(f)
            if qid is not None:
                questions.setdefault(str(qid), []).append(f)

        aggregated['total_findings'] = len(findings_list)
        aggregated['by_detector'] = {k: {'count': len(v), 'examples': v[:10]} for k, v in by_detector.items()}
        aggregated['by_severity'] = {k: {'count': len(v), 'examples': v[:10]} for k, v in by_severity.items()}
        aggregated['questions'] = {k: {'count': len(v), 'findings': v} for k, v in questions.items()}

        # Write aggregated JSON
        agg_path = rpt_dir / 'aggregated_findings.json'
        agg_path.write_text(json.dumps(aggregated, ensure_ascii=False, indent=2), encoding='utf-8')

        # --- Create markdown report ---
        md_lines = []
        md_lines.append('# Benchmark Audit Report')
        md_lines.append('')

        # --- Scores section (first block) ---
        md_lines.append('## Scores')
        md_lines.append('')
        
        if scores:
            md_lines.append(f'*Benchmark Score (average):* **{bench_score:.4f}**' if bench_score is not None else '*Benchmark Score:* N/A')
            md_lines.append('')
            md_lines.append('### Individual Scores')
            md_lines.append('')
            md_lines.append('| File | Score |')
            md_lines.append('|------|-------|')
            for filename, score in sorted(scores, key=lambda x: x[1], reverse=True):
                md_lines.append(f'| {filename} | {score:.4f} |')
            md_lines.append('')
            md_lines.append(f'*Total files with scores:* {len(scores)}')
        else:
            md_lines.append('*No score files found.*')
        md_lines.append('')

        # --- Findings sections ---
        md_lines.append(f'*Total findings:* {aggregated["total_findings"]}')
        md_lines.append('')

        md_lines.append('## Findings by Detector')
        for det, info in aggregated['by_detector'].items():
            md_lines.append(f'- **{det}**: {info["count"]} findings')
        md_lines.append('')

        md_lines.append('## Findings by Severity')
        for sev, info in aggregated['by_severity'].items():
            md_lines.append(f'- **{sev}**: {info["count"]} findings')
        md_lines.append('')

        # Most common problems
        md_lines.append('## Most Common Problems')
        problem_counts = Counter([f.get('reason', 'unknown') for f in findings_list])
        for reason, cnt in problem_counts.most_common(20):
            md_lines.append(f'- {reason}: {cnt}')
        md_lines.append('')

        # Top critical questions
        md_lines.append('## Top 20 Critical Questions')
        criticals = [f for f in findings_list if f.get('severity') == 'critical']
        crit_by_q = defaultdict(list)
        for f in criticals:
            qid = f.get('question_id')
            crit_by_q[qid].append(f)
        top_q = sorted(crit_by_q.items(), key=lambda x: len(x[1]) if x[0] is not None else 0, reverse=True)[:20]
        for qid, flist in top_q:
            md_lines.append(f'- Question `{qid}`: {len(flist)} critical findings')
        md_lines.append('')

        md_lines.append('## Notes')
        md_lines.append('- Findings are screening signals for review, not verified benchmark defects.')
        md_lines.append('- Full and blind findings are counted separately and retain their comparison side.')
        md_lines.append('- Detector scores and their average are heuristic diagnostics, not calibrated quality estimates.')
        md_lines.append('- Review per-question details in `reports/aggregated_findings.json`.')

        md_path = rpt_dir / 'benchmark_audit_report.md'
        md_path.write_text('\n'.join(md_lines), encoding='utf-8')

        return {
            'aggregated_path': str(agg_path),
            'markdown_path': str(md_path),
            'scores': scores,
            'bench_score': bench_score
        }