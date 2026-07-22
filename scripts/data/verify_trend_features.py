#!/usr/bin/env python3
from __future__ import annotations
import argparse,json
from pathlib import Path
import sys
import numpy as np
ROOT=Path(__file__).resolve().parents[2]; sys.path.insert(0,str(ROOT/'packages/semg-core'))
from semg_core.trend import fit_linear_trend

def args():
 p=argparse.ArgumentParser(); p.add_argument('--json-output',type=Path,default=Path('qa-validation/evidence/day11-trend-verification.json')); p.add_argument('--evidence-md',type=Path,default=Path('qa-validation/evidence/day11-trend-verification.md')); return p.parse_args()
def chk(name,obs,exp,tol=1e-12): return {'name':name,'observed':obs,'expected':exp,'tolerance':tol,'passed':abs(obs-exp)<=tol}
def main():
 a=args(); checks=[]
 t=np.arange(0.,60.,1.); m=fit_linear_trend(t,10+0.25*t,minimum_point_count=20,minimum_duration_s=30)
 checks += [chk('slope_per_s',m.slope_per_s,0.25),chk('slope_per_min',m.slope_per_min,15.0),chk('r_squared',m.r_squared,1.0)]
 c=fit_linear_trend(t,np.ones_like(t)*100,minimum_point_count=20,minimum_duration_s=30)
 checks += [chk('constant_slope',c.slope_per_s,0.0),chk('constant_percent_change',c.percent_change or 0.0,0.0)]
 passed=all(x['passed'] for x in checks)
 payload={'schema_version':'trend-feature-verification.v0.1','status':'passed' if passed else 'failed','checks':checks,'limitations':['OLS là descriptive fit trên overlapping windows; không phải inferential statistics.']}
 a.json_output.parent.mkdir(parents=True,exist_ok=True); a.json_output.write_text(json.dumps(payload,indent=2,ensure_ascii=False)+'\n')
 a.evidence_md.write_text('# Bằng chứng kiểm chứng trend Day 11\n\n- Trạng thái: **'+payload['status']+'**\n\n> Synthetic known-answer only; không phải clinical validation.\n',encoding='utf-8')
 print('Trend verification:', 'PASS' if passed else 'FAIL'); return 0 if passed else 1
if __name__=='__main__': raise SystemExit(main())
