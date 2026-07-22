#!/usr/bin/env python3
"""Chạy toàn pipeline đến descriptive trends RMS/MAV/MDF/MNF."""
from __future__ import annotations
import argparse,csv,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
for p in reversed((ROOT/'packages/semg-core',ROOT/'services/signal-ingestion-service/src',ROOT/'services/quality-gate-service/src',ROOT/'services/preprocessing-service/src',ROOT/'services/feature-extraction-service/src')):
    if str(p) not in sys.path: sys.path.insert(0,str(p))
from importers.csv_importer import CSVImporter
from config_loader import load_protocol,load_qc_config
from quality_gate import QualityGate,build_import_rejected_result
from preprocess_config import load_preprocess_config
from pipeline import PreprocessingPipeline
from preprocess_result_models import PreprocessingRunResult
from window_config import load_windowing_config
from windowing import WindowingPipeline
from feature_config import load_feature_config
from extractor import TimeDomainFeatureExtractor
from spectral_config import load_spectral_config
from spectral_extractor import SpectralEstimator
from frequency_feature_config import load_frequency_feature_config
from frequency_feature_extractor import FrequencyFeatureExtractor
from trend_feature_config import load_trend_feature_config
from trend_feature_extractor import TrendFeatureExtractor

def parse():
 p=argparse.ArgumentParser(); p.add_argument('--manifest',type=Path,required=True); p.add_argument('--protocol',type=Path,default=Path('clinical/protocols/quad-isometric-60s.v0.1.yaml')); p.add_argument('--qc-config',type=Path,default=Path('services/quality-gate-service/configs/qc_v0.1.yaml')); p.add_argument('--preprocess-config',type=Path,default=Path('services/preprocessing-service/configs/preprocess_v0.1.yaml')); p.add_argument('--windowing-config',type=Path,default=Path('services/feature-extraction-service/configs/windowing_v0.1.yaml')); p.add_argument('--time-feature-config',type=Path,default=Path('services/feature-extraction-service/configs/features_semg_v0.1.yaml')); p.add_argument('--spectral-config',type=Path,default=Path('services/feature-extraction-service/configs/spectral_estimation_v0.1.yaml')); p.add_argument('--frequency-feature-config',type=Path,default=Path('services/feature-extraction-service/configs/frequency_features_v0.1.yaml')); p.add_argument('--trend-config',type=Path,default=Path('services/feature-extraction-service/configs/trend_features_v0.1.yaml')); p.add_argument('--json-out',type=Path); p.add_argument('--csv-out',type=Path); p.add_argument('--quiet',action='store_true'); p.add_argument('--expect-status',choices=('completed','completed_with_exclusions','blocked')); p.add_argument('--expect-computed-channel-count',type=int); p.add_argument('--expect-reason',action='append',default=[]); return p.parse_args()
def sid(path):
 try: d=json.loads(path.read_text()); return str(d.get('session_id') or 'UNKNOWN_SESSION')
 except: return 'UNKNOWN_SESSION'
def blocked_pre(s,reasons): return PreprocessingRunResult(session_id=s,status='blocked',downstream_allowed=False,config_id='preprocess_v0.1',execution_mode='offline_zero_phase',inherited_qc_status='import_rejected',inherited_qc_reason_codes=reasons,reason_codes=('PREPROCESSING_BLOCKED_BY_QC',*reasons),steps=(),signal=None,limitations=('Import bị từ chối.',))
def write_csv(payload,path):
 path.parent.mkdir(parents=True,exist_ok=True); fields=['session_id','channel_id','feature_name','unit','slope_per_s','slope_per_min','r_squared','rmse','early_median','late_median','percent_change','normalized_slope_percent_per_min','status','reason_codes']
 with path.open('w',encoding='utf-8',newline='') as h:
  w=csv.DictWriter(h,fieldnames=fields); w.writeheader()
  for c in payload.get('channels',[]):
   for name,t in c.get('trends',{}).items():
    m=t.get('metrics') or {}; fit=m.get('linear_fit') or {}; early=m.get('early_late_summary') or {}; norm=m.get('normalized_slope_percent_per_min')
    w.writerow({'session_id':payload['session_id'],'channel_id':c['channel']['channel_id'],'feature_name':name,'unit':t['value_unit'],'slope_per_s':(fit.get('slope_per_s') or {}).get('value',''),'slope_per_min':(fit.get('slope_per_min') or {}).get('value',''),'r_squared':fit.get('r_squared',''),'rmse':(fit.get('rmse') or {}).get('value',''),'early_median':(early.get('early_median') or {}).get('value',''),'late_median':(early.get('late_median') or {}).get('value',''),'percent_change':(early.get('percent_change') or {}).get('value',''),'normalized_slope_percent_per_min':(norm or {}).get('value',''),'status':t['status'],'reason_codes':'|'.join(t.get('reason_codes',[]))})
def main():
 a=parse()
 try: protocol=load_protocol(a.protocol); qc=load_qc_config(a.qc_config); pre=load_preprocess_config(a.preprocess_config); win=load_windowing_config(a.windowing_config); tfc=load_feature_config(a.time_feature_config); spc=load_spectral_config(a.spectral_config); ffc=load_frequency_feature_config(a.frequency_feature_config); trc=load_trend_feature_config(a.trend_config)
 except Exception as e: print('CONFIG ERROR:',e,file=sys.stderr); return 2
 imported=CSVImporter().import_session(a.manifest)
 if not imported.ok or imported.signal is None:
  q=build_import_rejected_result(session_id=sid(a.manifest),blocking_codes=imported.blocking_codes,warning_codes=imported.warning_codes,issue_details=[x.to_dict() for x in imported.issues]); pr=blocked_pre(q.session_id,q.reason_codes)
 else:
  q=QualityGate(qc).run(imported.signal,protocol); pr=PreprocessingPipeline(pre).run(imported.signal,q)
 wr=WindowingPipeline(win).run(pr,protocol); tr=TimeDomainFeatureExtractor(tfc).run(wr); sr=SpectralEstimator(spc).run(wr); fr=FrequencyFeatureExtractor(ffc).run(sr); rr=TrendFeatureExtractor(trc).run(tr,fr); payload=rr.to_dict()
 if a.json_out: a.json_out.parent.mkdir(parents=True,exist_ok=True); a.json_out.write_text(json.dumps(payload,indent=2,ensure_ascii=False,allow_nan=False)+'\n')
 if a.csv_out: write_csv(payload,a.csv_out)
 if not a.quiet: print('TRENDS',payload['status'].upper(),'channels=',payload['summary']['computed_channel_count'],'hash=',payload.get('result_hash_sha256'))
 errors=[]
 if a.expect_status and payload['status']!=a.expect_status: errors.append('status mismatch')
 if a.expect_computed_channel_count is not None and payload['summary']['computed_channel_count']!=a.expect_computed_channel_count: errors.append('computed channel count mismatch')
 for r in a.expect_reason:
  if r not in payload.get('reason_codes',[]): errors.append('missing reason '+r)
 if errors:
  print('\n'.join(errors),file=sys.stderr); return 3
 return 0 if a.expect_status or rr.downstream_allowed else 1
if __name__=='__main__': raise SystemExit(main())
