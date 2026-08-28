"""Detector-oriented benchmark-quality evaluation pipeline.

This module implements the orchestration layer of the benchmark-audit line
(``run.py --mode bench_eval``):

1. validate that exactly one dataset is provided;
2. load the dataset once;
3. collect prediction/eval file paths across models and eval runs,
   pairing full runs with their blind counterparts (``*_blind.*`` files
   produced by ``run.py --blind``);
4. align all result frames on the dataset ``index`` column
   (:func:`vlmeval.detector.base_detector.align_results`);
5. run the registered detectors on a shared :class:`AnalysisContext`;
6. write per-detector reports, an aggregated audit report, and a
   reproducibility metadata record.

Outputs (under ``--work-dir``):

- ``reports/<detector>.json`` — per-detector reports;
- ``reports/aggregated_findings.json`` + ``reports/benchmark_audit_report.md``
  — aggregation across detectors;
- ``bench_quality_report.json`` — run manifest: inputs, detector status,
  audit paths, and reproducibility metadata (commit, CLI args, timestamps).
"""
from datetime import datetime
from pathlib import Path
import json
import sys

from vlmeval.dataset import build_dataset
from vlmeval.smp.file import get_pred_file_path, load, get_logger
from vlmeval.smp import githash
from vlmeval.config import detectors as DETECTORS_REGISTRY

from vlmeval.detector.base_detector import AnalysisContext, align_results
from vlmeval.reporting.benchmark_audit import BenchmarkAuditReportGenerator
logger = get_logger(__name__)


def collect_result_paths(args, dataset_name):
    """Scan the work dir for prediction/eval files of the requested models.

    For every ``<work_dir>/<model>/<eval_id>`` directory, the expected
    prediction file stem is derived via
    :func:`vlmeval.smp.file.get_pred_file_path`; files sharing that stem are
    classified as full or blind by the ``blind`` substring in their name.

    Parameters
    ----------
    args : argparse.Namespace
        CLI arguments; ``args.model`` (list of str) and ``args.work_dir``
        are used.
    dataset_name : str
        Registered dataset name.

    Returns
    -------
    dict of str to dict
        Mapping ``"<model>__<eval_id>"`` -> record with keys ``model``,
        ``eval_id``, ``variant``, ``pred``, ``eval``, ``blind``.
    """
    models = args.model if isinstance(args.model, list) else [args.model]
    result_paths = {}
    for model_name in models:
        work_dir = Path(args.work_dir) / model_name
        if not work_dir.exists():
            logger.warning(f'Work dir for model {model_name} does not exist: {work_dir}')
            continue

        eval_dirs = sorted([p for p in work_dir.iterdir() if p.is_dir()], key=lambda p: p.name)
        for eval_dir in eval_dirs:
            # prediction file is stored inside eval_dir named <model>_<dataset>.<ext>
            pred_path = get_pred_file_path(
                str(eval_dir), model_name, dataset_name, use_env_format=True, variant='full')
            if not Path(pred_path).exists():
                logger.info(
                    f'No prediction file for {model_name} at {eval_dir} — continuing to scan for eval/blind files')

            # try to locate corresponding eval file(s)
            eval_path = None
            blind_path = None
            pred_stem = Path(pred_path).stem if pred_path is not None else ''
            pred_suffix = Path(pred_path).suffix if pred_path is not None else ''
            for f in eval_dir.iterdir():
                if not f.is_file():
                    continue
                name = f.name
                # match same stem and suffix
                if pred_stem and name.startswith(pred_stem) and f.suffix == pred_suffix:
                    lname = name.lower()
                    if 'blind' in lname:
                        blind_path = str(f)
                    else:
                        # prefer first non-blind as eval
                        if eval_path is None:
                            eval_path = str(f)

            # determine variant (blind vs full) from filename or eval_dir
            is_blind = (pred_path and 'blind' in Path(pred_path).name.lower()) or ('blind' in eval_dir.name.lower())
            variant = 'blind' if is_blind else 'full'
            key = f"{model_name}__{eval_dir.name}"
            result_paths[key] = {
                'model': model_name,
                'eval_id': eval_dir.name,
                'variant': variant,
                'pred': str(pred_path) if pred_path is not None else None,
                'eval': str(eval_path) if eval_path is not None else None,
                'blind': str(blind_path) if blind_path is not None else None,
            }
    return result_paths


def load_and_align_results(result_paths):
    """Load result files and align them on the dataset ``index`` column.

    Evaluated files (with judge verdicts) are preferred over raw prediction
    files. Blind variants are loaded under a synthetic ``"<key>__blind"``
    key and additionally exposed via the ``blind_results`` mapping under the
    base key.

    Parameters
    ----------
    result_paths : dict of str to dict
        Output of :func:`collect_result_paths`.

    Returns
    -------
    loaded_results : dict of str to pandas.DataFrame or None
        Aligned frames for base and ``__blind`` keys.
    full_results : dict of str to pandas.DataFrame or None
        Aligned full-run frames keyed by base key.
    blind_results : dict of str to pandas.DataFrame
        Aligned blind-run frames keyed by base key.
    question_ids : list
        Sorted dataset ``index`` values common to all usable frames.
    """
    raw = {}
    for k, v in result_paths.items():
        try:
            if v.get('eval'):
                raw[k] = load(v['eval'])
            else:
                raw[k] = load(v['pred'])
        except Exception:
            logger.warning(f'Failed to load result for {k}')
            raw[k] = None
        if v.get('blind'):
            try:
                raw[f'{k}__blind'] = load(v['blind'])
            except Exception:
                logger.warning(f'Failed to load blind result for {k}')

    loaded_results, question_ids = align_results(raw, logger=logger)

    full_results = {}
    blind_results = {}
    for k in result_paths:
        full_results[k] = loaded_results.get(k)
        blind_key = f'{k}__blind'
        if loaded_results.get(blind_key) is not None:
            blind_results[k] = loaded_results[blind_key]
    return loaded_results, full_results, blind_results, question_ids


def build_run_metadata(args, dataset_name, question_ids, result_paths):
    """Assemble the reproducibility metadata record of an audit run.

    Parameters
    ----------
    args : argparse.Namespace
        CLI arguments of the audit run.
    dataset_name : str
        Audited dataset name.
    question_ids : list
        Aligned question ids used by the detectors.
    result_paths : dict
        Output of :func:`collect_result_paths`.

    Returns
    -------
    dict
        JSON-serializable metadata: timestamp, git commit, argv, CLI args,
        number of aligned questions, and the input file manifest.
    """
    try:
        commit = githash(digits=8)
    except Exception:
        commit = None
    return {
        'date_time': f'{datetime.now()}',
        'commit': commit,
        'argv': list(sys.argv),
        'cli_args': {k: v for k, v in vars(args).items() if isinstance(v, (str, int, float, bool, list, type(None)))},
        'dataset': dataset_name,
        'num_aligned_questions': len(question_ids),
        'result_paths': result_paths,
    }


def run_pipeline(args):
    """Run the full benchmark-audit pipeline.

    Parameters
    ----------
    args : argparse.Namespace
        CLI arguments; requires ``args.data`` (exactly one dataset),
        ``args.model`` (one or more models with existing outputs under
        ``args.work_dir``), and optionally ``args.detectors``.

    Returns
    -------
    dict
        Per-detector execution status (``{'executed': bool, ...}``).

    Raises
    ------
    ValueError
        If ``args.data`` does not contain exactly one dataset.
    """
    # Validate dataset list: exactly one dataset supported for now
    if not args.data or len(args.data) != 1:
        raise ValueError('Benchmark quality analysis supports exactly one dataset per run.')

    dataset_name = args.data[0]
    dataset = build_dataset(dataset_name)

    result_paths = collect_result_paths(args, dataset_name)
    if not result_paths:
        logger.error('No result files found for the requested models/dataset. Aborting bench-eval.')
        return {}

    loaded_results, full_results, blind_results, question_ids = load_and_align_results(result_paths)
    if not question_ids:
        logger.error('No usable result frames after alignment. Aborting bench-eval.')
        return {}

    # infer execution mode
    mode = 'full_vs_blind' if len(blind_results) > 0 else 'full_only'
    logger.info(
        f'Audit context: {len(result_paths)} result sets, {len(question_ids)} aligned questions, mode={mode}')

    context = AnalysisContext(
        dataset=dataset, dataset_name=dataset_name, result_paths=result_paths,
        config=vars(args), loaded_results=loaded_results, full_results=full_results,
        blind_results=blind_results, mode=mode, question_ids=question_ids)

    # Execute detectors
    selected = [d.lower() for d in (args.detectors or ['all'])]
    detector_outputs = {}
    for det_name, det_factory in DETECTORS_REGISTRY.items():
        if 'all' in selected or det_name in selected:
            det = det_factory()
            try:
                can, reason = det.can_run(context)
            except Exception as e:
                logger.exception(f'Failed to validate detector {det_name}: {e}')
                detector_outputs[det_name] = {'executed': False, 'reason': f'Validation error: {e}'}
                continue

            if not can:
                detector_outputs[det_name] = {'executed': False, 'reason': reason}
                logger.info(f'Skipping detector {det_name}: {reason}')
                continue

            try:
                logger.info(f'Running detector {det_name}...')
                det.run(context, out_dir=str(Path(args.work_dir)))
                detector_outputs[det_name] = {'executed': True}
                logger.info(f'Finished detector {det_name}...')
            except Exception as e:
                logger.exception(f'Detector {det_name} failed: {e}')
                detector_outputs[det_name] = {'executed': False, 'error': str(e)}

    # write aggregated detector outputs + reproducibility metadata
    agg = build_run_metadata(args, dataset_name, question_ids, result_paths)
    agg['detector_status'] = detector_outputs
    agg_path = Path(args.work_dir) / 'bench_quality_report.json'
    try:
        agg_path.parent.mkdir(parents=True, exist_ok=True)
        with open(agg_path, 'w', encoding='utf-8') as f:
            json.dump(agg, f, ensure_ascii=False, indent=2)
        logger.info(f'Wrote aggregated bench quality report: {agg_path}')
    except Exception:
        logger.exception('Failed to write aggregated bench quality report')

    # attempt to generate benchmark audit (aggregated detector findings)
    try:
        gen = BenchmarkAuditReportGenerator()
        gen_res = gen.generate(str(Path(args.work_dir)))
        logger.info(f'Generated benchmark audit reports: {gen_res}')
        try:
            agg['audit'] = gen_res
            with open(agg_path, 'w', encoding='utf-8') as f:
                json.dump(agg, f, ensure_ascii=False, indent=2)
        except Exception:
            logger.exception('Failed to update bench_quality_report.json with audit info')
    except Exception:
        logger.exception('Benchmark audit generation failed')

    return detector_outputs
