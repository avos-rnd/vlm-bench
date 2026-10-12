"""Regression tests for canonical reports, legacy exports, and repeat aggregation."""
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

path = Path(__file__).resolve().parents[1] / 'vlmeval/reporting/benchmark_audit.py'
spec = importlib.util.spec_from_file_location('audit_reporting', path)
reporting = importlib.util.module_from_spec(spec)
spec.loader.exec_module(reporting)


class TestAuditReporting(unittest.TestCase):

    def test_canonical_findings_are_counted_once_and_root_only_reports_are_included(self):
        with tempfile.TemporaryDirectory() as td:
            reports = Path(td) / 'reports'
            side_dir = reports / 'consensus_error'
            side_dir.mkdir(parents=True)
            finding = {'question_id': 42, 'detector': 'consensus_error',
                       'severity': 'critical', 'reason': 'review_candidate'}
            canonical = {'full': {'findings': [finding]}, 'blind': {'findings': [finding]}, 'score': 0.8}
            (reports / 'consensus_error.json').write_text(json.dumps(canonical))
            (side_dir / 'consensus_error_findings.json').write_text(json.dumps(
                {'detector': 'consensus_error', 'findings': [finding, finding]}))
            (reports / 'answer_options_distribution.json').write_text(json.dumps(
                {'findings': [{'question_id': None, 'detector': 'answer_options_distribution',
                               'severity': 'warning', 'reason': 'option_imbalance'}], 'score': 0.5}))
            gen = reporting.BenchmarkAuditReportGenerator()
            first = gen.generate(td)
            expected = json.loads((reports / 'aggregated_findings.json').read_text())
            self.assertEqual(expected['total_findings'], 3)
            self.assertEqual(expected['by_detector']['answer_options_distribution']['count'], 1)
            self.assertEqual([f['comparison_side'] for f in expected['questions']['42']['findings']],
                             ['full', 'blind'])
            self.assertEqual(first['bench_score'], 0.65)
            gen.generate(td)
            self.assertEqual(expected, json.loads((reports / 'aggregated_findings.json').read_text()))

    def test_legacy_side_exports_remain_readable(self):
        with tempfile.TemporaryDirectory() as td:
            reports = Path(td) / 'reports' / 'legacy'
            reports.mkdir(parents=True)
            (reports / 'legacy_findings.json').write_text(json.dumps(
                {'detector': 'legacy', 'findings': [{'question_id': 7, 'detector': 'legacy',
                                                   'severity': 'info', 'reason': 'legacy'}]}))
            reporting.BenchmarkAuditReportGenerator().generate(td)
            aggregate = json.loads((reports.parent / 'aggregated_findings.json').read_text())
            self.assertEqual(aggregate['total_findings'], 1)
