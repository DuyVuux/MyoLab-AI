#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; sys.path.insert(0,str(ROOT/'packages/semg-core'))
from semg_core.fatigue_evidence import DirectionalThreshold,evaluate_directional_evidence,aggregate_domain_status,overall_pattern_category

def parse():
 p=argparse.ArgumentParser(); p.add_argument('--json-output',type=Path,default=Path('qa-validation/evidence/day12-evidence-verification.json')); p.add_argument('--evidence-md',type=Path,default=Path('qa-validation/evidence/day12-evidence-verification.md')); return p.parse_args()
def feature(name,domain,direction,pc,slope,r2=.8): return evaluate_directional_evidence(feature_name=name,domain=domain,percent_change=pc,normalized_slope_percent_per_min=slope,r_squared=r2,threshold=DirectionalThreshold(direction,5,5,.2))
def scenario(name,vals):
 fs=aggregate_domain_status([x for x in vals if x.domain=='frequency']); amps=aggregate_domain_status([x for x in vals if x.domain=='amplitude']); return {'name':name,'frequency_status':fs,'amplitude_status':amps,'pattern':overall_pattern_category(frequency_status=fs,amplitude_status=amps)}
def main():
 a=parse(); scenarios=[]
 scenarios.append(scenario('multi_domain',[feature('mdf','frequency','decrease',-10,-10),feature('mnf','frequency','decrease',-12,-11),feature('rms','amplitude','increase',15,15),feature('mav','amplitude','increase',14,13)]))
 scenarios.append(scenario('spectral_only',[feature('mdf','frequency','decrease',-10,-10),feature('mnf','frequency','decrease',-12,-11),feature('rms','amplitude','increase',1,1),feature('mav','amplitude','increase',1,1)]))
 scenarios.append(scenario('mixed',[feature('mdf','frequency','decrease',-10,-10),feature('mnf','frequency','decrease',10,10),feature('rms','amplitude','increase',15,15),feature('mav','amplitude','increase',15,15)]))
 expected=['multi_domain_change_pattern_observed','frequency_decline_pattern_observed','evidence_mixed_or_opposite']; checks=[{'name':s['name'],'observed':s['pattern'],'expected':e,'passed':s['pattern']==e} for s,e in zip(scenarios,expected)]
 passed=all(x['passed'] for x in checks); payload={'schema_version':'fatigue-evidence-verification.v0.1','status':'passed' if passed else 'failed','checks':checks,'limitations':['Các scenario dùng metrics synthetic và threshold kỹ thuật tạm thời.']}
 a.json_output.parent.mkdir(parents=True,exist_ok=True); a.json_output.write_text(json.dumps(payload,indent=2,ensure_ascii=False)+'\n'); a.evidence_md.write_text('# Bằng chứng kiểm chứng Fatigue Evidence Engine Day 12\n\n- Trạng thái: **'+payload['status']+'**\n\n> Không phải fatigue classification hoặc clinical validation.\n',encoding='utf-8'); print('Evidence verification:', 'PASS' if passed else 'FAIL'); return 0 if passed else 1
if __name__=='__main__': raise SystemExit(main())
