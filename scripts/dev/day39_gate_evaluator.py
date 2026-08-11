from __future__ import annotations
import hashlib, json
from pathlib import Path
import yaml
ROOT=Path(__file__).resolve().parents[2]
REQUIRED=[
 'qa-validation/evidence/day32-validation-report.json',
 'qa-validation/evidence/day33-validation-report.json',
 'qa-validation/evidence/day34-validation-report.json',
 'qa-validation/evidence/day35-validation-report.json',
 'qa-validation/evidence/day36-validation-report.json',
 'qa-validation/evidence/day37-validation-report.json',
 'qa-validation/evidence/day38-validation-report.json',
 'configs/qc/thresholds.research-v0.1.yaml',
 'qa-validation/evidence/day38-qc-freeze-manifest.v0.2.json',
 'qa-validation/evidence/qc-error-analysis-by-domain-v0.2.csv',
]
missing=[p for p in REQUIRED if not (ROOT/p).exists()]
freeze=json.loads((ROOT/'qa-validation/evidence/day38-qc-freeze-manifest.v0.2.json').read_text())
hash_errors=[]
for item in freeze['items']:
 p=ROOT/item['path']; actual=hashlib.sha256(p.read_bytes()).hexdigest()
 if actual!=item['sha256']: hash_errors.append(item['path'])
th=yaml.safe_load((ROOT/'configs/qc/thresholds.research-v0.1.yaml').read_text())
site=th['profiles']['site-template']['thresholds']
d37=json.loads((ROOT/'qa-validation/evidence/day37-analysis-summary.json').read_text())
d38=json.loads((ROOT/'qa-validation/evidence/day38-validation-report.json').read_text())
checks={
 'required_evidence_complete': not missing,
 'freeze_hashes_match': not hash_errors,
 'site_threshold_status_not_verified': th['site_threshold_status']=='NOT_VERIFIED' and all(v is None for v in site.values()),
 'hard_integrity_false_allow_unresolved': bool(d38['hard_integrity_false_allow_unresolved']),
 'final_qc_false_allow_zero': d37['final_qc_false_allow']==0,
 'reproducibility_pass': d38['status']=='PASS' and d38['full_qc_property_regression']['failed']==0,
 'locked_evaluation_consumed_zero': freeze['locked_evaluation_consumed']==0,
}
blocking = bool(missing or hash_errors or checks['hard_integrity_false_allow_unresolved'] or not checks['final_qc_false_allow_zero'] or not checks['reproducibility_pass'] or not checks['site_threshold_status_not_verified'] or not checks['locked_evaluation_consumed_zero'])
status='BLOCKED_WITH_EVIDENCE' if blocking else 'QC_RESEARCH_CORE_READY'
result={
 'schema_version':'0.1','gate':'GATE-C-R','status':status,'claim_scope':'RESEARCH_ONLY',
 'checks':checks,'missing':missing,'hash_errors':hash_errors,
 'weak_supervision_maturity':'RESEARCH_ONLY',
 'weak_supervision_annotation_aid_validation':'NOT_PERFORMED',
 'distribution_support_maturity':'INFORMATIONAL_RESEARCH_ONLY',
 'distribution_support_blocking_gate_enabled':False,
 'ood_model':'NOT_IMPLEMENTED','ood_score':None,
 'clinical_validation':'NOT_PERFORMED','site_validation':'NOT_PERFORMED',
 'release_tag_candidate':'qc-core-research-v0.1' if not blocking else None,
}
(ROOT/'qa-validation/evidence/day39-gate-decision.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,sort_keys=True))
raise SystemExit(1 if blocking else 0)
