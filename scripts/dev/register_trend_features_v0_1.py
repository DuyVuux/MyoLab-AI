#!/usr/bin/env python3
import hashlib,json
from pathlib import Path
import yaml
R=Path(__file__).resolve().parents[2]; REG=R/'mlops/registry/feature_extractors.yaml'
def sha(p): return hashlib.sha256((R/p).read_bytes()).hexdigest()
def main():
 d=yaml.safe_load(REG.read_text()) or {}; entries=list(d.setdefault('feature_extractors',[])); result=json.loads((R/'qa-validation/evidence/day11-trends.json').read_text())
 entry={'config_id':'trend_features_v0.1','schema_version':'feature-extractor-registry-entry.v0.1','lifecycle_status':'implemented_for_mvp0','analytical_verification_status':'passed','clinical_validation_status':'not_validated','implemented_features':['rms_slope','mav_slope','mdf_slope','mnf_slope','early_late_change'],'fit_method':'ordinary_least_squares_descriptive','inferential_statistics_emitted':False,'fatigue_inference_in_scope':False,'ml_training_in_scope':False,'artifacts':{'config':{'path':'services/feature-extraction-service/configs/trend_features_v0.1.yaml','sha256':sha('services/feature-extraction-service/configs/trend_features_v0.1.yaml')},'core':{'path':'packages/semg-core/semg_core/trend.py','sha256':sha('packages/semg-core/semg_core/trend.py')},'extractor':{'path':'services/feature-extraction-service/src/trend_feature_extractor.py','sha256':sha('services/feature-extraction-service/src/trend_feature_extractor.py')}},'evidence':{'analytical_verification':'qa-validation/evidence/day11-trend-verification.json','golden_e2e':'qa-validation/evidence/day11-trends.json','golden_result_hash_sha256':result['result_hash_sha256']},'limitations':['Overlapping windows không độc lập; trend chỉ mang tính mô tả.','Chưa tạo fatigue evidence hoặc clinical output.']}
 entries=[x for x in entries if x.get('config_id')!='trend_features_v0.1']; entries.append(entry); d['feature_extractors']=entries; REG.write_text(yaml.safe_dump(d,sort_keys=False,allow_unicode=True)); print('Registered trend_features_v0.1'); return 0
if __name__=='__main__': raise SystemExit(main())
