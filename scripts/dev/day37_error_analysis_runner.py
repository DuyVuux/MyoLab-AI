from __future__ import annotations
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LIB_DIR = ROOT / "qa-validation" / "lib"
if str(LIB_DIR) not in sys.path:
    sys.path.insert(0, str(LIB_DIR))

import day37_error_analysis as m


def run_day37_analysis(root_dir: Path = ROOT) -> dict:
    rows = m.build_day34_strata(root_dir / 'qa-validation/evidence/lf-performance-synthetic-v0.1.csv')
    rows += m.build_day36_strata(
        root_dir / 'qa-validation/evidence/day36-domain-challenge-results-v0.2.csv',
        root_dir / 'qa-validation/test-data/ood-challenge-set-manifest.v0.2-research.yaml',
    )
    m.validate_strata(rows)
    m.write_strata_csv(root_dir / 'qa-validation/evidence/qc-error-analysis-by-domain-v0.2.csv', rows)
    
    risks = m.build_risk_cases(
        root_dir / 'qa-validation/evidence/research-review-candidate-list-v0.1.csv',
        root_dir / 'qa-validation/evidence/day36-domain-challenge-results-v0.2.csv',
        root_dir / 'qa-validation/test-data/ood-challenge-set-manifest.v0.2-research.yaml',
    )
    (root_dir / 'qa-validation/evidence/day37-top-risk-cases.json').write_text(json.dumps(risks, indent=2) + '\n')
    
    proxy = m.acquisition_proxy(root_dir / 'qa-validation/evidence/research-review-candidate-list-v0.1.csv')
    
    summary = {
        'schema_version': '0.2',
        'status': 'PASS',
        'claim_scope': 'RESEARCH_ONLY',
        'strata': len(rows),
        'final_qc_false_allow': sum(r.false_allow_or_fn for r in rows if r.scope == 'WINDOW_QC_GATE'),
        'final_qc_false_block': sum(r.false_block_or_fp for r in rows if r.scope == 'WINDOW_QC_GATE'),
        'unresolved': sum(r.unresolved for r in rows),
        'top_risk_cases': len(risks),
        'acquisition_proxy': proxy,
        'channel_scope_status': 'NOT_EVALUATED_NO_REFERENCE_LABELS',
        'session_scope_status': 'NOT_EVALUATED_NO_REFERENCE_LABELS',
        'clinical_sensitivity_claim': False,
    }
    (root_dir / 'qa-validation/evidence/day37-analysis-summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    return summary


if __name__ == '__main__':
    res = run_day37_analysis()
    print(json.dumps(res, sort_keys=True))
