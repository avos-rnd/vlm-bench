"""Original eval files must align across models and arms before statistics run."""
import importlib.util
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import pandas as pd

path = Path(__file__).resolve().parents[1] / 'scripts/reproduce_paper.py'
spec = importlib.util.spec_from_file_location('paper_reproduction', path)
reproduction = importlib.util.module_from_spec(spec)
spec.loader.exec_module(reproduction)


class TestPaperInputs(unittest.TestCase):

    def make_inputs(self, root):
        folder = root / 'MMStar'
        folder.mkdir()
        frame = pd.DataFrame({'index': [20, 10], 'prediction': ['B', 'A'], 'answer': ['B', 'A'],
                              'category': ['math', 'science'], 'hit': [1, 1],
                              **{letter: [letter, letter] for letter in 'ABCD'}})
        for side in ('full', 'blind'):
            for model in reproduction.MODELS:
                frame.to_excel(folder / f'{model}_{side}.xlsx', index=False)
        return folder, frame

    def test_row_order_is_aligned_but_mismatched_gold_labels_are_rejected(self):
        with tempfile.TemporaryDirectory() as td, patch.dict(reproduction.SIZES, {'MMStar': 2}):
            root = Path(td)
            folder, frame = self.make_inputs(root)
            path = folder / f'{reproduction.MODELS[0]}_blind.xlsx'
            frame.iloc[::-1].to_excel(path, index=False)
            full, blind, records = reproduction.validate_inputs(root, 'MMStar')
            self.assertEqual((len(full), len(blind), len(records)), (3, 3, 6))
            frame.loc[0, 'answer'] = 'D'
            frame.to_excel(path, index=False)
            with self.assertRaisesRegex(ValueError, 'differ across arms/models'):
                reproduction.validate_inputs(root, 'MMStar')

    def test_duplicate_question_ids_are_rejected(self):
        with tempfile.TemporaryDirectory() as td, patch.dict(reproduction.SIZES, {'MMStar': 2}):
            root = Path(td)
            folder, frame = self.make_inputs(root)
            frame['index'] = [10, 10]
            frame.to_excel(folder / f'{reproduction.MODELS[0]}_full.xlsx', index=False)
            with self.assertRaisesRegex(ValueError, 'unique, non-null question IDs'):
                reproduction.validate_inputs(root, 'MMStar')
