from __future__ import annotations
import csv
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
LIB_DIR = ROOT / "qa-validation" / "lib"
if str(LIB_DIR) not in sys.path:
    sys.path.insert(0, str(LIB_DIR))

import day37_error_analysis as m


def strata():
    rows = m.build_day34_strata(ROOT / 'qa-validation/evidence/lf-performance-synthetic-v0.1.csv')
    rows += m.build_day36_strata(
        ROOT / 'qa-validation/evidence/day36-domain-challenge-results-v0.2.csv',
        ROOT / 'qa-validation/test-data/ood-challenge-set-manifest.v0.2-research.yaml',
    )
    return rows


def test_denominators_are_traceable_and_positive():
    rows = strata()
    m.validate_strata(rows)
    assert all(x.denominator > 0 for x in rows)


def test_no_mixed_evidence_tier_aggregate():
    assert {x.evidence_tier for x in strata()} == {'SYNTHETIC_KNOWN_TRUTH'}


def test_detector_surrogate_not_called_final_qc():
    assert all(
        x.metric_semantics == 'DETECTOR_FN_FP_NOT_FINAL_QC_ALLOW_BLOCK'
        for x in strata()
        if x.source == 'DAY34_SYNTHETIC_LF'
    )


def test_day36_final_qc_has_zero_false_allow_and_false_block():
    rows = [x for x in strata() if x.scope == 'WINDOW_QC_GATE']
    assert sum(x.false_allow_or_fn for x in rows) == 0
    assert sum(x.false_block_or_fp for x in rows) == 0


def test_unknown_domain_is_explicit_not_error_relabel():
    rows = [x for x in strata() if x.source == 'DAY36_DOMAIN_CHALLENGE']
    assert sum(x.unresolved for x in rows) == 2


def test_baseline_unresolved_is_preserved():
    row = next(x for x in strata() if x.detector_family == 'LF_BASELINE_NOISE')
    assert row.unresolved == 12
    assert row.false_allow_or_fn == 0


def test_poor_contact_unresolved_is_preserved():
    row = next(x for x in strata() if x.detector_family == 'LF_POOR_CONTACT')
    assert row.unresolved == 12


def test_top_risk_cases_are_replayable_and_at_most_twenty():
    risks = m.build_risk_cases(
        ROOT / 'qa-validation/evidence/research-review-candidate-list-v0.1.csv',
        ROOT / 'qa-validation/evidence/day36-domain-challenge-results-v0.2.csv',
        ROOT / 'qa-validation/test-data/ood-challenge-set-manifest.v0.2-research.yaml',
    )
    assert 1 <= len(risks) <= 20
    assert all(x['replay_command'].startswith('python3 scripts/dev/') for x in risks)
    assert all(x['clinical_claim'] is False for x in risks)


def test_truth_misalignment_cases_rank_as_corpus_gap():
    risks = m.build_risk_cases(
        ROOT / 'qa-validation/evidence/research-review-candidate-list-v0.1.csv',
        ROOT / 'qa-validation/evidence/day36-domain-challenge-results-v0.2.csv',
        ROOT / 'qa-validation/test-data/ood-challenge-set-manifest.v0.2-research.yaml',
    )
    assert any(x['category'] == 'CORPUS_TRUTH_GAP' for x in risks)


def test_acquisition_proxy_is_not_active_learning_performance():
    p = m.acquisition_proxy(ROOT / 'qa-validation/evidence/research-review-candidate-list-v0.1.csv')
    assert p['interpretation'] == 'PROXY_ONLY_NOT_ACTIVE_LEARNING_PERFORMANCE'
    assert 0 <= p['proxy_information_yield'] <= 1


def test_channel_and_session_reference_not_fabricated_after_runner():
    subprocess.run(
        [sys.executable, str(ROOT / 'scripts/dev/day37_error_analysis_runner.py')],
        check=True,
        capture_output=True,
        text=True,
    )
    s = json.loads((ROOT / 'qa-validation/evidence/day37-analysis-summary.json').read_text())
    assert s['channel_scope_status'] == 'NOT_EVALUATED_NO_REFERENCE_LABELS'
    assert s['session_scope_status'] == 'NOT_EVALUATED_NO_REFERENCE_LABELS'


def test_output_csv_retains_metric_semantics_column():
    subprocess.run(
        [sys.executable, str(ROOT / 'scripts/dev/day37_error_analysis_runner.py')],
        check=True,
        capture_output=True,
        text=True,
    )
    with (ROOT / 'qa-validation/evidence/qc-error-analysis-by-domain-v0.2.csv').open() as f:
        header = next(csv.reader(f))
    assert 'metric_semantics' in header
