#!/usr/bin/env python3
import hashlib,json
from pathlib import Path
import yaml
R=Path(__file__).resolve().parents[2]; P=R/'mlops/registry/evidence_engines.yaml'
def sha(p):return hashlib.sha256((R/p).read_bytes()).hexdigest()
def main():
 d=yaml.safe_load(P.read_text()) if P.exists() else {'schema_version':'evidence-engine-registry.v0.1','evidence_engines':[]}; es=list(d.get('evidence_engines',[])); r=json.loads((R/'qa-validation/evidence/day12-fatigue-evidence.json').read_text())
 entry={'config_id':'fatigue_evidence_v0.1','lifecycle_status':'implemented_for_mvp0','analytical_verification_status':'passed','clinical_validation_status':'not_validated','output_type':'structured_evidence_not_inference','outputs_probability':False,'outputs_fatigue_status':False,'outputs_frs':False,'human_review_required':True,'artifacts':{'config':{'path':'services/inference-service/evidence/fatigue_evidence_v0.1.yaml','sha256':sha('services/inference-service/evidence/fatigue_evidence_v0.1.yaml')},'core':{'path':'packages/semg-core/semg_core/fatigue_evidence.py','sha256':sha('packages/semg-core/semg_core/fatigue_evidence.py')},'engine':{'path':'services/inference-service/src/evidence_engine.py','sha256':sha('services/inference-service/src/evidence_engine.py')}},'evidence':{'verification':'qa-validation/evidence/day12-evidence-verification.json','golden_e2e':'qa-validation/evidence/day12-fatigue-evidence.json','golden_result_hash_sha256':r['result_hash_sha256']},'limitations':['Thresholds provisional, chưa local/clinical validation.','Không phải diagnosis, probability, score hoặc recommendation.']}
 es=[x for x in es if x.get('config_id')!='fatigue_evidence_v0.1'];es.append(entry);d['evidence_engines']=es;P.parent.mkdir(parents=True,exist_ok=True);P.write_text(yaml.safe_dump(d,sort_keys=False,allow_unicode=True));print('Registered fatigue_evidence_v0.1');return 0
if __name__=='__main__':raise SystemExit(main())
