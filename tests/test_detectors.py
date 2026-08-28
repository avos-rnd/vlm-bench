"""Unit tests for the benchmark-audit detector layer.

These tests are self-contained: they load the detector modules via
``importlib`` with a stubbed ``vlmeval.smp.file`` so that the heavy
top-level ``vlmeval`` import chain (torch, decord, model registries, ...)
is never triggered. Only ``pandas``/``numpy`` are required.

Covered behavior
----------------
- index-based alignment of result frames (``align_results``);
- judge-free MCQ option extraction (no ground-truth substitution);
- consensus-error flagging with the 'Z' abstention sentinel excluded;
- visual-dependency categorization on synthetic full/blind runs;
- Fleiss' kappa computation on a known matrix.
"""
import importlib.util
import logging
import sys
import types
import unittest
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parent.parent
DET_DIR = REPO_ROOT / 'vlmeval' / 'detector'


def _install_stub_packages():
    """Register stub ``vlmeval`` packages so detector modules import cleanly."""
    if 'vlmeval' in sys.modules and not getattr(sys.modules['vlmeval'], '_is_test_stub', False):
        # A real vlmeval import already happened in this process; reuse it.
        return
    pkg = types.ModuleType('vlmeval')
    pkg.__path__ = [str(REPO_ROOT / 'vlmeval')]
    pkg._is_test_stub = True
    smp = types.ModuleType('vlmeval.smp')
    smp.__path__ = [str(REPO_ROOT / 'vlmeval' / 'smp')]
    smp_file = types.ModuleType('vlmeval.smp.file')
    smp_file.get_logger = lambda name=None: logging.getLogger(name or 'test')
    det_pkg = types.ModuleType('vlmeval.detector')
    det_pkg.__path__ = [str(DET_DIR)]
    sys.modules.setdefault('vlmeval', pkg)
    sys.modules.setdefault('vlmeval.smp', smp)
    sys.modules['vlmeval.smp.file'] = smp_file
    sys.modules.setdefault('vlmeval.detector', det_pkg)


def _load(mod_name):
    """Load ``vlmeval/detector/<mod_name>.py`` as a package submodule."""
    _install_stub_packages()
    full_name = f'vlmeval.detector.{mod_name}'
    if full_name in sys.modules:
        return sys.modules[full_name]
    spec = importlib.util.spec_from_file_location(full_name, DET_DIR / f'{mod_name}.py')
    mod = importlib.util.module_from_spec(spec)
    sys.modules[full_name] = mod
    spec.loader.exec_module(mod)
    return mod


base = _load('base_detector')


class DummyDataset:
    """Minimal dataset stand-in exposing a ``data`` DataFrame."""

    def __init__(self, df):
        self.data = df


def make_frame(ids, predictions, answers, hits=None):
    """Build a synthetic evaluated-result frame."""
    rec = {'index': ids, 'prediction': predictions, 'answer': answers}
    if hits is not None:
        rec['hit'] = hits
    return pd.DataFrame(rec)


class TestAlignResults(unittest.TestCase):

    def test_alignment_restricts_to_common_ids_and_sorts(self):
        f1 = make_frame([3, 1, 2], ['A', 'B', 'C'], ['A', 'B', 'C'])
        f2 = make_frame([2, 3, 99], ['C', 'A', 'D'], ['C', 'A', 'D'])
        aligned, qids = base.align_results({'m1': f1, 'm2': f2})
        self.assertEqual(qids, [2, 3])
        self.assertEqual(list(aligned['m1']['index']), [2, 3])
        self.assertEqual(list(aligned['m2']['index']), [2, 3])
        # row i refers to the same question in both frames
        self.assertEqual(list(aligned['m1']['prediction']), ['C', 'A'])
        self.assertEqual(list(aligned['m2']['prediction']), ['C', 'A'])

    def test_missing_index_column_gets_positional_ids(self):
        f = pd.DataFrame({'prediction': ['A', 'B'], 'answer': ['A', 'B']})
        aligned, qids = base.align_results({'m': f})
        self.assertEqual(qids, [0, 1])
        self.assertIn('index', aligned['m'].columns)


class TestMcqExtraction(unittest.TestCase):

    def setUp(self):
        class D(base.BaseDetector):
            NAME = 'dummy'

            def analyze(self, context, **kwargs):
                return {}
        self.det = D()
        self.valid = {'A', 'B', 'C', 'D'}

    def test_common_formats(self):
        cases = {
            'A': 'A', ' b ': 'B', '(C)': 'C', 'D.': 'D',
            'A. Paris': 'A', 'B) 42': 'B', 'C: because reasons': 'C',
            'The answer is (D)': 'D', 'Answer: B': 'B', 'option C': 'C',
        }
        for raw, expected in cases.items():
            self.assertEqual(self.det._extract_mcq_option(raw, self.valid), expected, raw)

    def test_unparseable_returns_sentinel(self):
        for raw in ['', None, 'I cannot tell from the image', 'E', float('nan')]:
            self.assertEqual(self.det._extract_mcq_option(raw, self.valid), 'Z', str(raw))

    def test_no_ground_truth_substitution(self):
        """A judged-correct row must still be read from `prediction`."""
        f = make_frame([0, 1], ['B', 'A'], ['A', 'A'], hits=[1, 1])
        ctx = base.AnalysisContext(
            dataset=DummyDataset(pd.DataFrame({'index': [0, 1], 'answer': ['A', 'A'],
                                               'A': ['x', 'x'], 'B': ['y', 'y']})),
            dataset_name='dummy',
            result_paths={'m1': {'model': 'm1'}},
            loaded_results={'m1': f}, question_ids=[0, 1])
        answers, _ = self.det._get_answers_by_model(ctx)
        # hit == 1 on row 0, yet the extracted answer must be the raw 'B'
        self.assertEqual(answers['m1'], ['B', 'A'])


class TestConsensusError(unittest.TestCase):

    def _make_context(self, frames, ids):
        rp = {k: {'model': k, 'eval_id': 'T1', 'variant': 'full'} for k in frames}
        ds = DummyDataset(pd.DataFrame({'index': ids, 'answer': ['A'] * len(ids),
                                        'A': ['x'] * len(ids), 'B': ['y'] * len(ids),
                                        'C': ['z'] * len(ids), 'D': ['w'] * len(ids)}))
        return base.AnalysisContext(
            dataset=ds, dataset_name='dummy', result_paths=rp,
            loaded_results=frames, full_results=frames, question_ids=ids)

    def test_unanimous_wrong_consensus_is_flagged_with_dataset_ids(self):
        ce = _load('consensus_error')
        ids = [10, 20, 30]
        frames = {
            'm1': make_frame(ids, ['B', 'A', 'A'], ['A', 'A', 'A']),
            'm2': make_frame(ids, ['B', 'A', 'A'], ['A', 'A', 'A']),
            'm3': make_frame(ids, ['B', 'A', 'A'], ['A', 'A', 'A']),
        }
        det = ce.ConsensusErrorDetector()
        report = det.analyze(self._make_context(frames, ids))
        flagged = report['_flagged']
        self.assertEqual(len(flagged), 1)
        self.assertEqual(flagged[0]['question_id'], 10)
        self.assertEqual(flagged[0]['confidence'], 'very_high')
        self.assertEqual(flagged[0]['majority_answer'], 'B')

    def test_abstentions_do_not_vote(self):
        ce = _load('consensus_error')
        ids = [0, 1]
        # question 0: two unparseable predictions + one wrong -> skipped (only 1 valid vote)
        frames = {
            'm1': make_frame(ids, ['I do not know', 'A'], ['A', 'A']),
            'm2': make_frame(ids, ['unclear', 'A'], ['A', 'A']),
            'm3': make_frame(ids, ['B', 'A'], ['A', 'A']),
        }
        det = ce.ConsensusErrorDetector()
        report = det.analyze(self._make_context(frames, ids))
        self.assertEqual(len(report['_flagged']), 0)
        skipped = [q for q in report['_all_q'] if q.get('skipped')]
        self.assertEqual(len(skipped), 1)
        self.assertEqual(skipped[0]['question_id'], 0)


class TestVisualDependency(unittest.TestCase):

    def _make_context(self, full_hits, blind_hits, ids):
        """Build a full-vs-blind context for two models."""
        rp, loaded, full_res, blind_res = {}, {}, {}, {}
        for m in full_hits:
            key = f'{m}__T1'
            rp[key] = {'model': m, 'eval_id': 'T1', 'variant': 'full', 'blind': f'/tmp/{m}_blind.xlsx',
                       'pred': f'/tmp/{m}.xlsx', 'eval': f'/tmp/{m}_result.xlsx'}
            loaded[key] = make_frame(ids, ['A'] * len(ids), ['A'] * len(ids), hits=full_hits[m])
            loaded[f'{key}__blind'] = make_frame(ids, ['A'] * len(ids), ['A'] * len(ids), hits=blind_hits[m])
            full_res[key] = loaded[key]
            blind_res[key] = loaded[f'{key}__blind']
        ds = DummyDataset(pd.DataFrame({'index': ids, 'answer': ['A'] * len(ids)}))
        return base.AnalysisContext(
            dataset=ds, dataset_name='dummy', result_paths=rp, loaded_results=loaded,
            full_results=full_res, blind_results=blind_res, mode='full_vs_blind',
            question_ids=ids)

    def test_categories(self):
        vd = _load('visual_dependency')
        ids = [100, 200, 300]
        # q100: both correct full / both wrong blind  -> visual_dependent
        # q200: identical accuracy                    -> text_only
        # q300: blind strictly better                 -> conflicting_visual_signal
        full_hits = {'m1': [1, 1, 0], 'm2': [1, 1, 0]}
        blind_hits = {'m1': [0, 1, 1], 'm2': [0, 1, 1]}
        det = vd.VisualDependencyDetector()
        report = det.analyze(self._make_context(full_hits, blind_hits, ids))
        cats = {q['question_id']: q['category'] for q in det._per_question}
        self.assertEqual(cats[100], 'visual_dependent')
        self.assertEqual(cats[200], 'text_only')
        self.assertEqual(cats[300], 'conflicting_visual_signal')
        self.assertEqual(report['num_questions'], 3)


class TestFleissKappa(unittest.TestCase):

    def test_perfect_agreement_gives_kappa_one(self):
        fk = _load('fleiss_kappa_agreement')
        det = fk.FleissKappaAgreementDetector()
        # 4 subjects, 3 raters, everyone picks the same category per subject
        matrix = [[3, 0], [0, 3], [3, 0], [0, 3]]
        self.assertAlmostEqual(det._fleiss_kappa(matrix), 1.0, places=6)

    def test_chance_level_agreement(self):
        fk = _load('fleiss_kappa_agreement')
        det = fk.FleissKappaAgreementDetector()
        # maximal disagreement between 2 raters over 2 categories
        matrix = [[1, 1], [1, 1]]
        self.assertLess(det._fleiss_kappa(matrix), 0.01)


if __name__ == '__main__':
    unittest.main()
