"""Semantic similarity between MCQ answer options (distractor quality).

This detector inspects the dataset itself (no model results needed): for
every multiple-choice question it computes pairwise semantic similarities
between the answer options, using sentence-transformer embeddings when
available and a difflib string-ratio fallback otherwise. Questions whose
most similar option pair exceeds the warning/critical thresholds — or that
contain literal duplicate options — are reported as findings keyed by the
dataset-level ``index`` value.
"""
from typing import Dict, Any, List, Tuple, Optional

from tqdm import tqdm
from .base_detector import BaseDetector, AnalysisContext, DetectorInputError
from datetime import datetime
from pathlib import Path
import json
import re
from vlmeval.smp.file import get_logger

logger = get_logger(__name__)


class DistractorSimilarityDetector(BaseDetector):
    """Detect near-duplicate or overly similar MCQ answer options.

    For each question the maximum and mean pairwise similarity between
    non-missing options is computed. Severity per question:

    - ``critical`` — ``max_similarity >= threshold_critical`` (default
      0.90): options are near-duplicates and the question may have no
      single defensible answer;
    - ``warning`` — ``max_similarity >= threshold_warning`` (default
      0.75): distractors are suspiciously close to each other or to the
      correct option;
    - ``healthy`` — otherwise.

    Notes
    -----
    The ``backend`` config selects the similarity engine: ``'auto'`` tries
    ``sentence_transformers`` (all-MiniLM-L6-v2 cosine similarity) and
    falls back to ``difflib.SequenceMatcher`` string ratios, whose scale
    is not directly comparable to embedding cosine — thresholds may need
    retuning for the fallback. Placeholder tokens (``nan``/``none``/
    ``n/a``/empty) are treated as missing options and excluded.
    """

    NAME = 'distractor_similarity'
    DESCRIPTION = 'Detect semantically-similar MCQ distractors within dataset.'
    DEFAULT_CONFIG = {
        "backend": "auto",  # auto -> try sentence_transformers, fallback to difflib
        "threshold_warning": 0.75,
        "threshold_critical": 0.90,
    }

    REQUIRES_FULL_RESULTS = False
    REQUIRES_BLIND_RESULTS = False
    REQUIRES_MULTIPLE_MODELS = False
    SUPPORTS_COMPARISON = False

    def _find_options_columns(self, df) -> List[List[str]]:
        """Collect the per-question option lists from a dataset frame.

        Parameters
        ----------
        df : pandas.DataFrame
            Dataset ``data`` frame. Options are read from an ``options``
            or ``choices`` list column, or from single-letter ``A``/``B``/
            ... columns.

        Returns
        -------
        list of list of str
            One option list per row; empty list when no option columns
            are found.
        """
        # Attempt common column names
        if "options" in df.columns:
            return [list(r) if r is not None else [] for r in df["options"]]
        if "choices" in df.columns:
            return [list(r) if r is not None else [] for r in df["choices"]]

        # Look for A/B/C/D style columns
        letter_cols = [
            c for c in df.columns if re.fullmatch(r"^[A-Z]$", c, re.IGNORECASE)
        ]
        if letter_cols:
            return [[row[c] for c in letter_cols] for _, row in df.iterrows()]

        return []

    def _get_correct_index(self, ans_val, options: List[str]) -> Optional[int]:
        """Resolve the ground-truth answer to a positional option index.

        Parameters
        ----------
        ans_val : object
            Raw answer annotation; interpreted as an option letter
            (``'A'``...), a numeric index, or the exact option text.
        options : list of str
            Normalized option texts of the question.

        Returns
        -------
        int or None
            Zero-based index of the correct option, or None when the
            answer cannot be resolved.
        """
        if ans_val is None:
            return None
        # direct match
        try:
            normalized_options = [
                s.strip().lower() if s is not None else "" for s in options
            ]
            if isinstance(ans_val, str):
                a = ans_val.strip()
                # letter map A/B/C -> index
                if re.fullmatch(r"^[A-Za-z]$", a):
                    idx = ord(a.upper()) - ord("A")
                    if 0 <= idx < len(options):
                        return idx
                # numeric index string
                if re.fullmatch(r"^\d+$", a):
                    ni = int(a)
                    if 0 <= ni < len(options):
                        return ni
                # exact text match
                low = a.lower()
                if low in normalized_options:
                    return normalized_options.index(low)
            else:
                # numeric
                if isinstance(ans_val, (int, float)) and 0 <= int(ans_val) < len(
                    options
                ):
                    return int(ans_val)
        except Exception:
            return None
        return None

    def _embed_backend(self):
        """Select and initialize the similarity backend.

        Returns
        -------
        tuple of (str, object or None)
            ``('st', model)`` with a loaded ``SentenceTransformer`` when
            the configured backend is available, otherwise
            ``('difflib', None)`` for the string-ratio fallback.
        """
        cfg = self.config.get('backend', 'auto')
        if cfg in ('st', 'sentence_transformers', 'auto'):
            try:
                from sentence_transformers import SentenceTransformer

                model = SentenceTransformer("all-MiniLM-L6-v2")
                return ("st", model)
            except Exception:
                pass
        # fallback: use difflib
        return ("difflib", None)

    def _pairwise_similarities(self, texts: List[str], backend_info) -> List[Tuple[int, int, float]]:
        """Compute all pairwise similarities between option texts.

        Parameters
        ----------
        texts : list of str
            Option texts of one question.
        backend_info : tuple
            Backend descriptor from :meth:`_embed_backend`.

        Returns
        -------
        list of tuple of (int, int, float)
            Triples ``(i, j, similarity)`` for every pair ``i < j``:
            cosine similarity of normalized embeddings for the
            sentence-transformer backend, ``SequenceMatcher`` ratio for
            the difflib fallback.
        """
        kind, model = backend_info
        sims = []
        n = len(texts)
        if kind == "st" and model is not None:
            import numpy as np

            embs = model.encode(texts, convert_to_numpy=True)
            # normalize
            norms = np.linalg.norm(embs, axis=1, keepdims=True)
            norms[norms == 0] = 1.0
            embs = embs / norms
            for i in range(n):
                for j in range(i + 1, n):
                    sim = float(np.dot(embs[i], embs[j]))
                    sims.append((i, j, sim))
            return sims
        else:
            # difflib fallback
            from difflib import SequenceMatcher

            for i in tqdm(range(n), desc="Computing pairwise similarities"):
                for j in range(i + 1, n):
                    a = texts[i] or ""
                    b = texts[j] or ""
                    sim = SequenceMatcher(None, a, b).ratio()
                    sims.append((i, j, float(sim)))
            return sims

    def analyze(self, context: AnalysisContext, **kwargs) -> Dict[str, Any]:
        """Compute the distractor-similarity report for the dataset.

        Parameters
        ----------
        context : AnalysisContext
            Prepared inputs; only ``context.dataset.data`` is used (model
            results are not required).
        **kwargs
            Unused; accepted for interface compatibility.

        Returns
        -------
        dict
            Dataset-level report with ``avg_max_pair_similarity``,
            ``duplicate_rate_percent``, ``high_similarity_rate_percent``,
            ``critical_rate_percent``, ``summary`` and per-question
            ``findings`` (dataset-level ``question_id``).

        Raises
        ------
        DetectorInputError
            When the dataset is unavailable or exposes no option columns.
        """
        dataset = getattr(context, 'dataset', None)
        if dataset is None or not hasattr(dataset, 'data'):
            raise DetectorInputError('Dataset not available in context')

        if dataset.TYPE != "MCQ":
            raise DetectorInputError(
                "DistractorSimilarityDetector only supports MCQ datasets."
            )

        df = dataset.data
        options_rows = self._find_options_columns(df)
        if not options_rows:
            raise DetectorInputError("No options columns found in dataset")

        backend = self._embed_backend()
        thresh_warn = float(self.config.get("threshold_warning", 0.75))
        thresh_crit = float(self.config.get("threshold_critical", 0.90))

        per_q_reports = []
        max_pairs = []
        duplicate_count = 0

        MISSING_TOKENS = set(["nan", "none", "n/a", "na", ""])

        # dataset-level question ids: row idx of options_rows maps to df_ids[idx]
        df_ids = list(df['index']) if 'index' in df.columns else list(range(len(df)))

        for idx, opts in enumerate(options_rows):
            # normalize options as strings
            opts = [o if o is not None else "" for o in opts]
            norm_opts = [re.sub(r"\s+", " ", str(o).strip()) for o in opts]
            # identify non-missing options (ignore placeholder tokens like 'nan')
            lowered = [o.lower() for o in norm_opts]
            idx_map = [i for i, v in enumerate(lowered) if v not in MISSING_TOKENS]
            consider_only = [lowered[i] for i in idx_map]
            has_dup = (
                len(set(consider_only)) < len(consider_only) if consider_only else False
            )
            if has_dup:
                duplicate_count += 1

            # compute similarities over non-missing options only
            if len(idx_map) < 2:
                sims = []
            else:
                texts = [norm_opts[i] for i in idx_map]
                sims_local = self._pairwise_similarities(texts, backend)
                # map local pair indices back to original option indices
                sims = [(idx_map[a], idx_map[b], s) for (a, b, s) in sims_local]
            if not sims:
                max_sim = 0.0
                mean_sim = 0.0
            else:
                vals = [s for (_, _, s) in sims]
                max_sim = max(vals)
                mean_sim = float(sum(vals) / len(vals))

            # correct option similarity
            correct_val = None
            if "answer" in df.columns:
                correct_val = df["answer"].iloc[idx]
            correct_idx = (
                self._get_correct_index(correct_val, norm_opts)
                if correct_val is not None
                else None
            )
            max_correct_sim = None
            most_similar_pair = None
            if sims:
                # find most similar pair indices
                imax = max(sims, key=lambda x: x[2])
                most_similar_pair = (imax[0], imax[1])
            if correct_idx is not None and sims:
                # compute similarities between correct and others
                cs = [s for (i, j, s) in sims if i == correct_idx or j == correct_idx]
                if cs:
                    max_correct_sim = max(cs)

            # severity
            if max_sim >= thresh_crit:
                severity = "critical"
            elif max_sim >= thresh_warn:
                severity = "warning"
            else:
                severity = "healthy"

            per_q_reports.append(
                {
                    "question_id": idx,
                    "question": (
                        df.get("question", df.get("question_text", "")).iloc[idx]
                        if "question" in df.columns or "question_text" in df.columns
                        else None
                    ),
                    "options": {
                        chr(ord("A") + i): norm_opts[i] if i < len(norm_opts) else ""
                        for i in range(len(norm_opts))
                    },
                    "max_similarity": float(max_sim),
                    "mean_similarity": float(mean_sim),
                    "max_correct_similarity": (
                        float(max_correct_sim) if max_correct_sim is not None else None
                    ),
                    "severity": severity,
                    "duplicate_options": bool(has_dup),
                    "most_similar_pair": (
                        [
                            chr(ord("A") + most_similar_pair[0]),
                            chr(ord("A") + most_similar_pair[1]),
                        ]
                        if most_similar_pair is not None
                        else None
                    ),
                }
            )
            max_pairs.append(max_sim)

        total_q = len(per_q_reports)
        avg_max = float(sum(max_pairs) / total_q) if total_q > 0 else 0.0
        duplicate_rate = 100.0 * duplicate_count / total_q if total_q > 0 else 0.0
        warning_count = sum(1 for r in per_q_reports if r["severity"] == "warning")
        critical_count = sum(1 for r in per_q_reports if r["severity"] == "critical")
        high_sim_rate = (
            100.0 * (warning_count + critical_count) / total_q if total_q > 0 else 0.0
        )
        critical_rate = 100.0 * critical_count / total_q if total_q > 0 else 0.0

        dataset_report = {
            "date_time": f"{datetime.now()}",
            "detector": self.NAME,
            "dataset": getattr(context, "dataset_name", None),
            "num_questions": total_q,
            "avg_max_pair_similarity": avg_max,
            "duplicate_rate_percent": duplicate_rate,
            "high_similarity_rate_percent": high_sim_rate,
            "critical_rate_percent": critical_rate,
            "thresholds": {"warning": thresh_warn, "critical": thresh_crit},
        }
        # normalized severity score: average maximal pair similarity (0..1, higher == worse)
        dataset_report["score"] = 1.0 - float(avg_max)

        # build summary and findings for audit
        findings = []
        for q in per_q_reports:
            ms = q.get("max_similarity", 0.0)
            if ms >= float(1.0):
                findings.append(
                    {
                        "question_id": q.get("question_id"),
                        "detector": self.NAME,
                        "severity": "duplicate",
                        "reason": "duplicate_options",
                        "score": ms,
                        "metadata": {"duplicate_options": q.get("most_similar_pair")},
                    }
                )
            elif ms >= float(thresh_crit):
                findings.append(
                    {
                        "question_id": q.get("question_id"),
                        "detector": self.NAME,
                        "severity": "critical",
                        "reason": "near_duplicate_options",
                        "score": ms,
                        "metadata": {"most_similar_pair": q.get("most_similar_pair")},
                    }
                )
            elif ms >= float(thresh_warn):
                findings.append(
                    {
                        "question_id": q.get("question_id"),
                        "detector": self.NAME,
                        "severity": "warning",
                        "reason": "similar_options",
                        "score": ms,
                        "metadata": {"most_similar_pair": q.get("most_similar_pair")},
                    }
                )

        self._findings = findings
        self._all_stat = per_q_reports

        return dataset_report

    def run(self, context: AnalysisContext, out_dir: str = None, **kwargs):
        """Run the detector and export per-question similarity files.

        In addition to the base JSON report, writes
        ``reports/<NAME>/high_similarity_questions.json`` (warning and
        critical questions) and ``reports/<NAME>/all_stat.json`` (every
        question), both keyed by dataset-level ``question_id``.

        Parameters
        ----------
        context : AnalysisContext
            Prepared inputs (see :meth:`analyze`).
        out_dir : str, optional
            Audit output directory; exports are skipped when omitted.
        **kwargs
            Forwarded to :meth:`analyze`.

        Returns
        -------
        dict
            The detector report returned by :meth:`analyze`.
        """
        res = super().run(context, out_dir=out_dir, **kwargs)
        if out_dir:
            try:
                rpt_dir = Path(out_dir) / "reports" / self.NAME
                rpt_dir.mkdir(parents=True, exist_ok=True)
                (rpt_dir / f"{self.NAME}_findings.json").write_text(
                    json.dumps(
                        {"findings": self._findings, "detector": self.NAME},
                        ensure_ascii=False,
                        indent=2,
                    ),
                    encoding="utf-8",
                )

                (rpt_dir / "all_stat.json").write_text(
                    json.dumps(self._all_stat, ensure_ascii=False, indent=2),
                    encoding="utf-8",
                )
            except Exception:
                logger.exception("Failed to write distractor similarity reports")
        return res
