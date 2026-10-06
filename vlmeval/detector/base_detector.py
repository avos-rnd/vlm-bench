"""Base classes and shared utilities for benchmark-quality detectors.

This module defines the common infrastructure of the benchmark-audit layer
(``run.py --mode bench_eval``):

- :class:`AnalysisContext` — an immutable bundle of everything a detector may
  need (dataset, aligned result frames, run configuration).
- :func:`align_results` — index-based alignment of prediction/eval frames
  across models and full/blind variants. All consensus-style detectors rely
  on this alignment instead of positional row order.
- :class:`BaseDetector` — the abstract detector interface plus shared answer
  normalization and MCQ option extraction helpers.

Design rules
------------
1. Detectors never traverse the filesystem; they consume
   ``context.loaded_results`` / ``context.result_paths`` prepared by
   ``vlmeval.bench_eval.run_pipeline``.
2. Model answers are always extracted from the raw ``prediction`` column.
   Ground-truth labels are never substituted for model answers, so detector
   outputs are independent of the correctness judge wherever possible.
3. Every per-question finding must carry the dataset-level ``index`` value
   as ``question_id`` (not the positional row number).
"""
from abc import ABC, abstractmethod
from collections import defaultdict
from pathlib import Path
import json
import re
import string


class DetectorInputError(Exception):
    """Raised when a detector cannot run on the provided inputs."""
    pass


class AnalysisContext:
    """Bundle of inputs shared by all detectors in one audit run.

    Parameters
    ----------
    dataset : ImageBaseDataset or compatible
        Dataset object built via ``vlmeval.dataset.build_dataset``; must
        expose a ``data`` DataFrame with an ``index`` column.
    dataset_name : str
        Registered dataset name (e.g. ``'MMStar'``).
    result_paths : dict of str to dict
        Mapping ``"<model>__<eval_id>"`` -> record with keys ``model``,
        ``eval_id``, ``variant``, ``pred``, ``eval``, ``blind`` (paths).
    config : dict, optional
        CLI arguments of the audit run (``vars(args)``).
    loaded_results : dict, optional
        Mapping from result key to an aligned pandas DataFrame (see
        :func:`align_results`). Contains both full-run keys and synthetic
        ``"<key>__blind"`` keys.
    full_results : dict, optional
        Subset of ``loaded_results`` holding only full-run frames, keyed by
        the base result key.
    blind_results : dict, optional
        Blind-run frames keyed by the *base* result key (not the synthetic
        ``__blind`` key), so that ``full_results[k]`` and
        ``blind_results[k]`` refer to the same model/eval pair.
    mode : {'full_only', 'full_vs_blind'}, optional
        Execution mode; inferred from ``blind_results`` when omitted.
    question_ids : list, optional
        Sorted dataset ``index`` values shared by all aligned frames. Row
        ``i`` of every aligned frame corresponds to ``question_ids[i]``.
    """

    def __init__(self, dataset, dataset_name, result_paths, config=None, loaded_results=None,
                 full_results=None, blind_results=None, mode=None, question_ids=None):
        self.dataset = dataset
        self.dataset_name = dataset_name
        self.result_paths = result_paths
        self.config = config or {}
        # legacy single mapping for detectors that expect loaded_results
        self.loaded_results = loaded_results or {}
        # new explicit mappings
        self.full_results = full_results or {}
        self.blind_results = blind_results or {}
        # execution mode: 'full_only' or 'full_vs_blind'
        self.mode = mode or ('full_vs_blind' if self.blind_results else 'full_only')
        self.question_ids = question_ids


def _as_dataframe(res):
    """Coerce a loaded result object into a pandas DataFrame.

    Parameters
    ----------
    res : DataFrame, list of dict, dict, or None
        Result object as returned by ``vlmeval.smp.load``.

    Returns
    -------
    pandas.DataFrame or None
        DataFrame view of the result, or None when coercion fails.
    """
    if res is None:
        return None
    import pandas as pd
    if isinstance(res, pd.DataFrame):
        return res
    if isinstance(res, list) and len(res) > 0 and isinstance(res[0], dict):
        return pd.DataFrame(res)
    if isinstance(res, dict):
        return pd.DataFrame([res])
    return None


def align_results(loaded_results, logger=None):
    """Align result frames on the dataset ``index`` column.

    All frames are restricted to the intersection of their ``index`` values
    and sorted by ``index``, so that row ``i`` refers to the same benchmark
    question in every frame. This replaces the fragile assumption that all
    result files store rows in identical order.

    Parameters
    ----------
    loaded_results : dict of str to object
        Mapping from result key to a loaded result (DataFrame/list/dict).
        Entries that cannot be coerced to a DataFrame are kept as None.
    logger : logging.Logger, optional
        If given, mismatches between frames are reported as warnings.

    Returns
    -------
    aligned : dict of str to pandas.DataFrame or None
        Aligned frames (sorted by ``index``, reset positional index).
    question_ids : list
        Sorted ``index`` values common to every non-None frame. Empty when
        no frame is usable.

    Notes
    -----
    A frame without an ``index`` column is assigned a synthetic
    ``0..n-1`` index; this preserves backward compatibility but such files
    should be regenerated with a current toolkit version.
    """
    frames = {}
    for k, res in loaded_results.items():
        df = _as_dataframe(res)
        if df is None:
            frames[k] = None
            continue
        df = df.copy()
        if 'index' not in df.columns:
            if logger is not None:
                logger.warning(f'Result {k} has no `index` column; assigning positional ids.')
            df['index'] = range(len(df))
        frames[k] = df

    id_sets = [set(df['index']) for df in frames.values() if df is not None]
    if not id_sets:
        return frames, []
    common = set.intersection(*id_sets)
    union = set.union(*id_sets)
    if logger is not None and common != union:
        logger.warning(
            f'Result files disagree on question ids: {len(common)} shared of {len(union)} total. '
            'Restricting all detectors to the shared subset.')

    aligned = {}
    for k, df in frames.items():
        if df is None:
            aligned[k] = None
            continue
        sub = df[df['index'].isin(common)].sort_values('index').reset_index(drop=True)
        aligned[k] = sub
    question_ids = sorted(common)
    return aligned, question_ids


class BaseDetector(ABC):
    """Abstract base class for benchmark-pathology detectors.

    Subclasses implement :meth:`analyze` and declare capability flags so
    that the pipeline can decide whether a detector is applicable to the
    provided context (see :meth:`can_run`).

    Attributes
    ----------
    NAME : str
        Registry name of the detector (also used for report directories).
    DESCRIPTION : str
        One-line human-readable description.
    DEFAULT_CONFIG : dict
        Default configuration; merged with constructor kwargs.
    REQUIRES_FULL_RESULTS : bool
        Whether full-run prediction frames are required.
    REQUIRES_BLIND_RESULTS : bool
        Whether blind-run frames are required (e.g. visual dependency).
    REQUIRES_MULTIPLE_MODELS : bool
        Whether at least two models are required (consensus detectors).
    REQUIRES_CORRECTNESS_LABELS : bool
        Whether judged correctness labels (``hit`` column) are required.
    SUPPORTS_COMPARISON : bool
        Whether the detector produces a full-vs-blind comparison report.
    """

    NAME = None

    DESCRIPTION = None

    DEFAULT_CONFIG = {}

    # Capability flags (detectors may override)
    REQUIRES_FULL_RESULTS = True
    REQUIRES_BLIND_RESULTS = False
    REQUIRES_MULTIPLE_MODELS = False
    REQUIRES_CORRECTNESS_LABELS = False
    SUPPORTS_COMPARISON = False

    def __init__(self, context=None, **kwargs):
        self.config = {**self.DEFAULT_CONFIG, **kwargs}

    @abstractmethod
    def analyze(self, context, **kwargs):
        """Perform detector analysis on an :class:`AnalysisContext`.

        Parameters
        ----------
        context : AnalysisContext
            Prepared inputs; frames in ``context.loaded_results`` are
            already aligned by :func:`align_results`.
        **kwargs
            Detector-specific overrides.

        Returns
        -------
        dict
            JSON-serializable report. Must include ``findings`` (list of
            per-question finding dicts with ``question_id``, ``detector``,
            ``severity``, ``reason``) and ``summary`` keys for the audit
            aggregation layer.
        """
        raise NotImplementedError()

    def run(self, context, out_dir: str = None, **kwargs):
        """Run the detector and optionally persist its JSON report.

        Parameters
        ----------
        context : AnalysisContext
            Prepared inputs (see :meth:`analyze`).
        out_dir : str, optional
            Audit output directory; the report is written to
            ``<out_dir>/reports/<NAME>.json`` when provided.
        **kwargs
            Forwarded to :meth:`analyze`.

        Returns
        -------
        dict
            The detector report returned by :meth:`analyze`.
        """
        result = self.analyze(context=context, **kwargs)
        if out_dir and result is not None:
            try:
                p = Path(out_dir) / "reports" / f"{self.NAME}.json"
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text(
                    json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8"
                )
            except Exception:
                # best-effort: do not raise from file-writing issues
                pass
        return result

    def can_run(self, context: AnalysisContext):
        """Check whether the detector is applicable to the given context.

        Parameters
        ----------
        context : AnalysisContext
            Prepared inputs.

        Returns
        -------
        tuple of (bool, str or None)
            ``(True, None)`` when the detector can run, otherwise
            ``(False, reason)`` with a human-readable explanation.
        """
        # check full results
        if self.REQUIRES_FULL_RESULTS:
            if not getattr(context, "full_results", None):
                return False, "Full results are required but not provided."
        # check blind results
        if self.REQUIRES_BLIND_RESULTS:
            if not getattr(context, "blind_results", None):
                return False, "Blind results are required but not provided."
        # check multiple models
        if self.REQUIRES_MULTIPLE_MODELS:
            rp = getattr(context, "result_paths", {})
            if not rp or len(rp) < 2:
                return False, "Detector requires results from multiple models."
        return True, None

    def _normalize_answer(self, a):
        """Normalize a raw answer value to a stripped string.

        Parameters
        ----------
        a : object
            Raw answer cell value (may be None/NaN/str/number).

        Returns
        -------
        str or None
            Stripped string form, or None for empty/missing values.
        """
        if a is None:
            return None
        try:
            import pandas as pd

            if pd.isna(a):
                return None
        except Exception:
            pass
        s = str(a).strip()
        if s == "":
            return None
        return s

    def _extract_mcq_option(self, value, valid_options=None) -> str:
        """Extract an MCQ option letter from a raw model prediction.

        The extraction is judge-free: it never consults ground-truth labels
        or judged correctness. It handles the common answer formats produced
        by instruction-tuned VLMs:

        1. a bare letter, possibly wrapped in punctuation (``"A"``, ``"(b)"``,
           ``"C."``);
        2. a leading letter followed by a separator (``"A. Paris"``,
           ``"B) 42"``, ``"C: because ..."``);
        3. an explicit statement (``"The answer is (D)"``,
           ``"Answer: A"``, ``"Option B is correct"``).

        Parameters
        ----------
        value : object
            Raw ``prediction`` cell value.
        valid_options : iterable of str, optional
            Allowed option letters (e.g. ``{'A', 'B', 'C', 'D'}``). When
            omitted, letters A-H are accepted.

        Returns
        -------
        str
            The extracted upper-case option letter, or ``'Z'`` when no
            valid option can be identified (abstention/unparseable). ``'Z'``
            is a sentinel and must be excluded from agreement statistics or
            reported separately.
        """
        valid_options = [opt.upper() for opt in valid_options]
        if value is None:
            return "Z"

        try:
            import pandas as pd

            if pd.isna(value):
                return "Z"
        except Exception:
            pass

        s = str(value).strip()
        if s == '':
            return 'Z'

        if valid_options:
            valid = {str(o).strip().upper() for o in valid_options if o is not None and str(o).strip()}
        else:
            valid = set(string.ascii_uppercase[:8])

        # 1) bare letter, possibly wrapped in punctuation/whitespace
        m = re.fullmatch(r'\W*([A-Za-z])\W*', s)
        if m and m.group(1).upper() in valid:
            return m.group(1).upper()

        # 2) leading letter with a separator: "A.", "(B)", "C:", "D)"
        m = re.match(r'^\W{0,2}([A-Za-z])\s*[\.\):\-,]', s)
        if m and m.group(1).upper() in valid:
            return m.group(1).upper()

        # 3) explicit statement: "answer is (C)", "Answer: B", "option D"
        m = re.search(r'(?:answer|option)\s*(?:is|:)?\s*\(?([A-Za-z])\)?(?![A-Za-z])', s, re.IGNORECASE)
        if m and m.group(1).upper() in valid:
            return m.group(1).upper()

        # No valid option found
        return "Z"

    def _get_option_letters(self, context: AnalysisContext, frame=None):
        """Determine the set of valid option letters for the dataset.

        Preference order: single-letter option columns of the dataset
        (``A``/``B``/...), then unique ground-truth letters observed in the
        given result frame, then the A-H fallback.

        Parameters
        ----------
        context : AnalysisContext
            Prepared inputs.
        frame : pandas.DataFrame, optional
            A result frame whose ``answer`` column is used as fallback.

        Returns
        -------
        set of str
            Upper-case option letters.
        """
        dataset = getattr(context, 'dataset', None)
        try:
            df = dataset.data if dataset is not None and hasattr(dataset, 'data') else None
            if df is not None:
                letters = {c.upper() for c in df.columns
                           if isinstance(c, str) and len(c) == 1 and c.isalpha()}
                if letters:
                    return letters
        except Exception:
            pass
        if frame is not None and 'answer' in getattr(frame, 'columns', []):
            letters = set()
            for a in frame['answer'].dropna().unique():
                s = str(a).strip().upper()
                if len(s) == 1 and s.isalpha():
                    letters.add(s)
            if letters:
                return letters
        return set(string.ascii_uppercase[:8])

    def _get_question_ids(self, context: AnalysisContext, loaded=None):
        """Return the aligned question-id list for the current context.

        Parameters
        ----------
        context : AnalysisContext
            Prepared inputs.
        loaded : dict, optional
            Frame mapping to fall back on (e.g. a sub-context's
            ``loaded_results``) when ``context.question_ids`` is unset.

        Returns
        -------
        list
            Dataset ``index`` values such that row ``i`` of every aligned
            frame corresponds to element ``i``. Empty list when unknown.
        """
        if getattr(context, 'question_ids', None):
            return list(context.question_ids)
        loaded = loaded if loaded is not None else getattr(context, 'loaded_results', {})
        for res in loaded.values():
            df = _as_dataframe(res)
            if df is not None and 'index' in df.columns:
                return list(df['index'])
        return []

    def _get_answers_by_model(self, context: AnalysisContext):
        """Extract per-model MCQ answers from raw predictions.

        Answers are extracted with :meth:`_extract_mcq_option` from the
        ``prediction`` column only. Judged correctness (``hit``) and
        ground-truth labels are deliberately ignored so that consensus
        statistics are not contaminated by the judge (see module notes).

        Parameters
        ----------
        context : AnalysisContext
            Prepared inputs; frames must be aligned (see
            :func:`align_results`).

        Returns
        -------
        answers_by_model : dict of str to (list of str or None)
            For each result key, the per-question option letters (``'Z'``
            marks unparseable predictions), or None when the frame is
            unusable.
        model_keys : list of str
            Ordered result keys, matching ``context.result_paths``.
        """
        dataset = getattr(context, "dataset", {})
        
        rp = getattr(context, "result_paths", {})
        loaded = getattr(context, "loaded_results", {})
        
        # ordered list of model keys
        model_keys = list(rp.keys())
        answers_by_model = {}

        for k in model_keys:
            df = _as_dataframe(loaded.get(k, None))
            if df is None or 'prediction' not in df.columns:
                answers_by_model[k] = None
                continue
            try:
                valid_options = self._get_option_letters(context, frame=df)
                answers = [self._extract_mcq_option(v, valid_options) for v in df['prediction']]
                answers_by_model[k] = answers
            except Exception:
                answers_by_model[k] = None

        return answers_by_model, model_keys

    def _get_ground_truth_answers(self, context: AnalysisContext):
        """Extract aligned ground-truth labels.

        Ground truth is read from the ``answer`` column of the first usable
        result frame (result files embed the dataset labels), which is
        guaranteed to be aligned with all other frames. Falls back to the
        dataset ``data`` frame restricted to the aligned question ids.

        Parameters
        ----------
        context : AnalysisContext
            Prepared inputs.

        Returns
        -------
        list of (str or None)
            Normalized ground-truth answers, one per aligned question;
            empty list when no source is available.
        """
        loaded = getattr(context, 'loaded_results', {})
        for res in loaded.values():
            df = _as_dataframe(res)
            if df is not None and 'answer' in df.columns:
                return [self._normalize_answer(a) for a in df['answer']]

        dataset = getattr(context, 'dataset', None)
        try:
            data = dataset.data
            qids = self._get_question_ids(context)
            if qids and 'index' in data.columns and 'answer' in data.columns:
                sub = data[data['index'].isin(set(qids))].sort_values('index')
                return [self._normalize_answer(a) for a in sub['answer']]
        except Exception:
            pass
        return []
