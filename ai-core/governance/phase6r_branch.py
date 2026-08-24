from __future__ import annotations

ALLOWED_M6R = {'RESEARCH_ML_READY', 'RESEARCH_ML_NOT_JUSTIFIED', 'INSUFFICIENT_DATA'}

def resolve_ml_no_go_branch(*, entry_pass: bool, leakage_status: str, claim_status: str,
                             starting_ml_decision: str, distinct_representation_question: bool) -> dict:
    if not entry_pass or leakage_status != 'PASS' or claim_status != 'PASS':
        return {
            'phase_branch': 'ML_NO_GO' if starting_ml_decision == 'ML_NO_GO' else 'UNRESOLVED',
            'execution_status': 'BLOCKED_WITH_EVIDENCE',
            'representation_learning_applicability': 'BLOCKED',
            'm6_r': None,
            'reason': 'Phase-entry, leakage, or claim-boundary requirements are not satisfied.',
        }
    if starting_ml_decision != 'ML_NO_GO':
        return {
            'phase_branch': starting_ml_decision,
            'execution_status': 'PASS_WITH_LIMITATIONS',
            'representation_learning_applicability': 'REQUIRES_SEPARATE_RESEARCH_QUESTION_REVIEW',
            'm6_r': None,
            'reason': 'This continuation package is intentionally scoped to the active ML_NO_GO branch.',
        }
    if distinct_representation_question:
        return {
            'phase_branch': 'ML_NO_GO',
            'execution_status': 'PASS_WITH_LIMITATIONS',
            'representation_learning_applicability': 'JUSTIFIED_DISTINCT_QUESTION_REQUIRES_PROTOCOL',
            'm6_r': None,
            'reason': 'ML_NO_GO does not forbid a scientifically distinct representation-learning question.',
        }
    return {
        'phase_branch': 'ML_NO_GO',
        'execution_status': 'SKIPPED_BY_GOVERNANCE',
        'representation_learning_applicability': 'NOT_JUSTIFIED',
        'm6_r': 'RESEARCH_ML_NOT_JUSTIFIED',
        'reason': 'No defensible scientifically distinct representation-learning question is established; no forced ML.',
    }
