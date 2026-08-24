#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT / "ai-core") not in sys.path:
    sys.path.insert(0, str(ROOT / "ai-core"))

from governance.phase6r_leakage import audit_leakage
from governance.phase6r_claims import audit_claim_boundaries
from governance.phase6r_branch import resolve_ml_no_go_branch

SAFE_BOUNDARY = 'RESEARCH_ONLY | NOT_CLINICALLY_VALIDATED | NOT_FOR_CLINICAL_USE | CORE_ML_DEFAULT_OFF'

def read_preflight(repo: Path) -> dict:
    p = repo / 'qa-validation/evidence/phase6r-entry-preflight.json'
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text(encoding='utf-8'))
    except Exception:
        return {}

def write_file(repo: Path, rel: str, text: str) -> None:
    p = repo / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text.rstrip() + '\n', encoding='utf-8')

def distinct_question(repo: Path) -> bool:
    cfg = repo / 'ai-core/configs/representation-research-v0.1.yaml'
    if not cfg.exists():
        return False
    txt = cfg.read_text(encoding='utf-8', errors='replace').lower()
    return bool(re.search(r'distinct_representation_question\s*:\s*true', txt))

def finalize_not_justified(repo: Path, leakage: dict, claims: dict, preflight: dict) -> None:
    write_file(repo, 'ai-core/research/phase6r/research-question/representation-learning-protocol-v0.1.md', f'''# Phase 6R Representation-Learning Applicability Decision

## Decision

`representation_learning_applicability = NOT_JUSTIFIED`

`starting_ml_decision = ML_NO_GO`

The active research-ML feasibility decision is `ML_NO_GO`. No separate, defensible representation-learning target has been established in the current governed configuration. Under the no-forced-ML rule, Phase 6R therefore does not train an SSL encoder merely to create an AI artifact.

## Evidence basis

- M5-R / Gate E-R: supplied preflight reports ready/pass.
- PublicFeatureWindowRecord v1.2: supplied preflight reports PASS.
- Reproducibility: supplied preflight reports PASS.
- Leakage audit: `{leakage['status']}` after evidence-based re-audit.
- Claim-boundary audit: `{claims['status']}` after context-aware re-audit.
- Starting ML feasibility decision: `ML_NO_GO`.

## Scientific rationale

A representation-learning experiment must answer a technical question distinct from the failed/not-justified classical ML path. No such approved question is present in the active configuration. Training an encoder now would invert the required order from evidence → question → applicability → experiment.

## Consequences

- Handcrafted baseline: no new Phase 6R baseline is fabricated; Phase 5R feasibility evidence remains authoritative.
- SSL encoder: `SKIPPED_BY_GOVERNANCE`.
- Representation evaluation: `NOT_RUN`.
- Embedding supportability: `NOT_RUN`; existing metadata/rule-based supportability remains the baseline.
- Calibration/selective prediction: `NOT_APPLICABLE` because no valid probabilistic research head is promoted.
- Ablation: `NOT_APPLICABLE` because no Phase 6R model was trained.
- Core system remains ML default OFF.

## Claim boundary

{SAFE_BOUNDARY}
''')

    write_file(repo, 'qa-validation/evidence/representation-learning-not-justified-v0.1.md', f'''# Representation Learning — Governance Outcome

Status: `SKIPPED_BY_GOVERNANCE`

Reason: active ML feasibility is `ML_NO_GO`, leakage and claim audits pass, and no scientifically distinct representation-learning question is configured. No checkpoint, embedding table, calibration number or ablation score was fabricated.

Claim boundary: {SAFE_BOUNDARY}
''')

    write_file(repo, 'qa-validation/evidence/calibration-not-applicable-v0.1.md', f'''# Calibration Applicability

Status: `NOT_APPLICABLE`

No Phase 6R probabilistic supervised head is promoted under the active `ML_NO_GO` branch. Therefore probability calibration, selective prediction and conformal coverage are not computed.

Claim boundary: {SAFE_BOUNDARY}
''')

    write_file(repo, 'qa-validation/evidence/embedding-supportability-not-run-v0.1.md', f'''# Embedding Supportability

Status: `NOT_RUN`

No SSL/representation encoder was trained. Embedding distance is therefore not computed and no OOD probability or production OOD score is created. Existing non-probabilistic metadata/rule supportability remains unchanged.

Claim boundary: {SAFE_BOUNDARY}
''')

    write_file(repo, 'qa-validation/evidence/ablation-not-applicable-v0.1.md', f'''# ML Ablation / Robustness Applicability

Status: `NOT_APPLICABLE`

No Phase 6R model was trained under the evidence-backed `ML_NO_GO` branch. Model ablation and seed robustness scores would therefore be fabricated if reported.

Claim boundary: {SAFE_BOUNDARY}
''')

    write_file(repo, 'docs/00-executive/gates/gate-f-r-research-ml-decision.md', f'''# Gate F-R — Research ML Decision

## Final decision

`RESEARCH_ML_NOT_JUSTIFIED`

## Decision matrix

| Question | Decision |
|---|---|
| Research question valid? | NO distinct representation-learning question established |
| Data sufficient for the frozen public benchmark? | YES per active M5-R preflight |
| Handcrafted/classical ML feasibility | `ML_NO_GO` |
| Representation learning trained? | SKIPPED |
| Representation adds measurable value? | NOT_RUN |
| Embedding supportability useful? | NOT_RUN |
| Probabilistic calibration applicable? | NO |
| Model reproducible? | NOT_APPLICABLE |
| Model included as optional research module? | NO |
| Core deterministic system requires ML? | NO |
| Leakage audit | {leakage['status']} |
| Claim-boundary audit | {claims['status']} |

## Rationale

The roadmap explicitly permits a negative result. With an active `ML_NO_GO` and no separately justified representation-learning question, additional model complexity has no evidence-backed research purpose. The deterministic DSP/QC/metric system remains the core.

## Claim boundary

{SAFE_BOUNDARY}
''')

    write_file(repo, 'docs/00-executive/milestones/m6-r-research-ml.md', f'''# M6-R — Research ML Milestone

Status: `RESEARCH_ML_NOT_JUSTIFIED`

Phase 6R closes without a research model. This is an evidence-based negative decision, not an execution failure. No SSL checkpoint, embedding OOD score, calibrated probability or clinical claim is produced.

Core ML default: `OFF`

Claim boundary: {SAFE_BOUNDARY}
''')

    write_file(repo, 'docs/00-executive/technology-maturity-register-v0.2.md', '''# Technology Maturity Register v0.2

| Capability | Maturity | Decision |
|---|---|---|
| Deterministic QC | REPRODUCIBLE_RESEARCH | Core research capability |
| Handcrafted ML | EXCLUDED | Active feasibility decision `ML_NO_GO` |
| Synthetic perturbation ML | NOT_APPLICABLE | No active ML_GO scope |
| SSL representation | EXCLUDED | Not justified under current evidence |
| Embedding supportability | NOT_STARTED | No embeddings created |
| Calibration | NOT_APPLICABLE | No probabilistic head |
| Selective prediction | NOT_APPLICABLE | No calibrated probabilistic head |
| Conformal | NOT_APPLICABLE | Preconditions absent |
| OOD | NOT_STARTED | No production OOD semantics |
| Domain adaptation / TTA | RESEARCH_ONLY | Future watch item; default OFF |

Claim boundary: RESEARCH_ONLY / NOT_CLINICALLY_VALIDATED / NOT_FOR_CLINICAL_USE.
''')

    write_file(repo, 'ai-core/research/phase6r/governance/phase6r-to-locked-validation-handoff.yaml', '''phase: Phase 6R
m6_r_decision: RESEARCH_ML_NOT_JUSTIFIED
model_inclusion_status: EXCLUDED
model_hashes: []
ml_go_scope: NOT_APPLICABLE
calibration_applicable: false
representation_learning_status: SKIPPED_BY_GOVERNANCE
embedding_supportability_status: NOT_RUN
core_ml_default: OFF
next_phase: Locked Validation / Portfolio Release
next_phase_readiness: YES
claim_boundary:
  - RESEARCH_ONLY
  - NOT_CLINICALLY_VALIDATED
  - NOT_FOR_CLINICAL_USE
''')

    write_file(repo, 'ai-core/research/phase6r/governance/phase6r-to-locked-validation-handoff.md', f'''# Phase 6R → Locked Validation Handoff

M6-R: `RESEARCH_ML_NOT_JUSTIFIED`

No Phase 6R research model is included. The deterministic core remains authoritative and ML remains default OFF. Phase 7R may proceed with locked validation of the deterministic/public-benchmark system, subject to its own freeze and no-retune rules.

Claim boundary: {SAFE_BOUNDARY}
''')

def main() -> int:
    parser = argparse.ArgumentParser(description='Continue Phase 6R safely for active ML_NO_GO branch.')
    parser.add_argument('repo_root', type=Path)
    args = parser.parse_args()
    repo = args.repo_root.resolve()

    leakage_result = audit_leakage(repo)
    claims_result = audit_claim_boundaries(repo)
    preflight = read_preflight(repo)

    entry_core = (
        preflight.get('m5r_public_benchmark_ready') == 'PASS'
        and preflight.get('gate_e_r_evidence') == 'PASS'
        and preflight.get('public_feature_contract_v1_2') == 'PASS'
        and preflight.get('reproducibility') == 'PASS'
    )
    start = preflight.get('starting_ml_decision', 'UNKNOWN')

    branch_result = resolve_ml_no_go_branch(
        entry_pass=entry_core,
        leakage_status=leakage_result['status'],
        claim_status=claims_result['status'],
        starting_ml_decision=start,
        distinct_representation_question=distinct_question(repo)
    )

    out_dir = repo / 'qa-validation/evidence'
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / 'phase6r-leakage-audit.json').write_text(json.dumps(leakage_result, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    (out_dir / 'phase6r-claim-audit-contextual.json').write_text(json.dumps(claims_result, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    (out_dir / 'phase6r-branch-decision.json').write_text(json.dumps(branch_result, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')

    print(json.dumps({
        'entry_core': entry_core,
        'starting_ml_decision': start,
        'leakage': leakage_result['status'],
        'claims': claims_result['status'],
        'branch': branch_result
    }, indent=2, ensure_ascii=False))

    if branch_result.get('m6_r') == 'RESEARCH_ML_NOT_JUSTIFIED':
        finalize_not_justified(repo, leakage_result, claims_result, preflight)
        return 0

    return 2 if branch_result['execution_status'] == 'BLOCKED_WITH_EVIDENCE' else 3

if __name__ == '__main__':
    raise SystemExit(main())
