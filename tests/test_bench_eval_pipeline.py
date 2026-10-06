"""End-to-end test of the ``bench_eval`` pipeline on synthetic artifacts.

Loads ``vlmeval/bench_eval.py`` via ``importlib`` with stubbed ``vlmeval``
sub-packages (dataset/config/smp), so the heavy top-level import chain is
bypassed while the *real* orchestration, alignment, detectors, and reporting
code runs. The same harness (:func:`load_pipeline`) is reused by analysis
drivers to audit real prediction artifacts without a full install.
"""
import importlib.util
import json
import logging
import sys
import types
import unittest
from functools import partial
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parent.parent

# reuse the detector-loading stubs from the unit tests
sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_detectors import DummyDataset, _load as load_detector  # noqa: E402

DETECTOR_MODULES = {
    'answer_options_distribution': ('answer_options_distribution', 'AnswerOptionsDistributionDetector'),
    'fleiss_kappa_agreement': ('fleiss_kappa_agreement', 'FleissKappaAgreementDetector'),
    'consensus_error': ('consensus_error', 'ConsensusErrorDetector'),
    'correctness_agreement': ('correctness_agreement', 'CorrectnessAgreementDetector'),
    'visual_dependency': ('visual_dependency', 'VisualDependencyDetector'),
    'distractor_similarity': ('distractor_similarity', 'DistractorSimilarityDetector'),
}


def _stub_get_pred_file_path(work_dir, model_name, dataset_name, use_env_format=True, variant=None):
    tag = '_blind' if variant == 'blind' else ''
    return str(Path(work_dir) / f'{model_name}_{dataset_name}{tag}.xlsx')


def _stub_load(path):
    p = Path(path)
    if p.suffix == '.xlsx':
        return pd.read_excel(p)
    if p.suffix in ('.tsv', '.csv'):
        return pd.read_csv(p, sep='\t' if p.suffix == '.tsv' else ',')
    raise ValueError(f'unsupported: {p}')


def load_pipeline(dataset_df, detector_names=None):
    """Load the real ``bench_eval`` module with stubbed dependencies.

    Parameters
    ----------
    dataset_df : pandas.DataFrame
        Frame served by the stubbed ``build_dataset`` (must have ``index``,
        ``answer`` and option columns for MCQ detectors).
    detector_names : list of str, optional
        Subset of :data:`DETECTOR_MODULES` to register (default: all).

    Returns
    -------
    module
        The loaded ``vlmeval.bench_eval`` module (fresh instance).
    """
    names = detector_names or list(DETECTOR_MODULES)
    registry = {}
    for name in names:
        mod_name, cls_name = DETECTOR_MODULES[name]
        mod = load_detector(mod_name)
        registry[name] = partial(getattr(mod, cls_name))

    ds_pkg = types.ModuleType('vlmeval.dataset')
    ds_pkg.build_dataset = lambda name, **kw: DummyDataset(dataset_df)
    smp_pkg = sys.modules.get('vlmeval.smp') or types.ModuleType('vlmeval.smp')
    smp_pkg.githash = lambda digits=8: 'testhash0'
    smp_file = sys.modules['vlmeval.smp.file']
    smp_file.get_pred_file_path = _stub_get_pred_file_path
    smp_file.load = _stub_load
    smp_file.get_logger = lambda name=None: logging.getLogger(name or 'test')
    cfg_pkg = types.ModuleType('vlmeval.config')
    cfg_pkg.detectors = registry
    rep_pkg = types.ModuleType('vlmeval.reporting')
    sys.modules['vlmeval.dataset'] = ds_pkg
    sys.modules['vlmeval.smp'] = smp_pkg
    sys.modules['vlmeval.config'] = cfg_pkg
    sys.modules.setdefault('vlmeval.reporting', rep_pkg)

    # real reporting module (stdlib-only)
    if 'vlmeval.reporting.benchmark_audit' not in sys.modules:
        spec = importlib.util.spec_from_file_location(
            'vlmeval.reporting.benchmark_audit',
            REPO_ROOT / 'vlmeval' / 'reporting' / 'benchmark_audit.py')
        m = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = m
        spec.loader.exec_module(m)

    # fresh bench_eval instance
    spec = importlib.util.spec_from_file_location('vlmeval.bench_eval', REPO_ROOT / 'vlmeval' / 'bench_eval.py')
    be = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = be
    spec.loader.exec_module(be)
    return be


def make_eval_frame(ids, preds, answers, hits, options):
    rec = {'index': ids, 'question': [f'q{i}' for i in ids]}
    for letter, vals in options.items():
        rec[letter] = vals
    rec.update({'answer': answers, 'prediction': preds, 'hit': hits})
    return pd.DataFrame(rec)


class TestBenchEvalPipeline(unittest.TestCase):

    def test_full_vs_blind_pipeline_on_synthetic_artifacts(self):
        import tempfile
        ids = list(range(12))
        answers = ['A', 'B', 'C', 'D'] * 3
        options = {L: [f'{L}-opt-{i}' for i in ids] for L in 'ABCD'}
        ds_df = pd.DataFrame({'index': ids, 'question': [f'q{i}' for i in ids],
                              **options, 'answer': answers})

        with tempfile.TemporaryDirectory() as td:
            work = Path(td)
            for m in ['modelA', 'modelB']:
                d = work / m / 'T001'
                d.mkdir(parents=True)
                # full: everything correct except q0 (both predict 'B' vs gold 'A')
                full_preds = ['B'] + answers[1:]
                make_eval_frame(ids, full_preds, answers, [0] + [1] * 11, options) \
                    .to_excel(d / f'{m}_DummyDS_judge_result.xlsx', index=False)
                # blind: only q1 answered correctly
                blind_preds = ['Z-nonsense'] * 12
                blind_preds[1] = 'B'
                make_eval_frame(ids, blind_preds, answers, [0, 1] + [0] * 10, options) \
                    .to_excel(d / f'{m}_DummyDS_judge_result_blind.xlsx', index=False)

            be = load_pipeline(ds_df)
            args = types.SimpleNamespace(
                data=['DummyDS'], model=['modelA', 'modelB'],
                work_dir=str(work), detectors=['all'])
            status = be.run_pipeline(args)

            self.assertTrue(status['visual_dependency']['executed'], status)
            self.assertTrue(status['consensus_error']['executed'], status)
            self.assertTrue(status['fleiss_kappa_agreement']['executed'], status)

            manifest = json.loads((work / 'bench_quality_report.json').read_text())
            self.assertEqual(manifest['num_aligned_questions'], 12)
            self.assertEqual(manifest['commit'], 'testhash0')

            vd = json.loads((work / 'reports' / 'visual_dependency.json').read_text())
            self.assertEqual(vd['num_questions'], 12)
            # q0: full wrong for all, blind wrong -> text_only; q1: correct in both -> text_only
            # remaining 10: full correct, blind wrong -> visual_dependent
            dist = vd['category_distribution']
            self.assertAlmostEqual(dist['visual_dependent'], 10 / 12 * 100, places=3)

            ce = json.loads((work / 'reports' / 'consensus_error.json').read_text())
            flagged = ce['full']['_flagged'] if 'full' in ce else ce['_flagged']
            self.assertEqual(len(flagged), 1)
            self.assertEqual(flagged[0]['question_id'], 0)
            self.assertEqual(flagged[0]['confidence'], 'very_high')

            agg = json.loads((work / 'reports' / 'aggregated_findings.json').read_text())
            self.assertGreater(agg['total_findings'], 0)


if __name__ == '__main__':
    unittest.main()
