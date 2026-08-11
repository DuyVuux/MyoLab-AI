#!/usr/bin/env python3
from pathlib import Path
import csv,json,sys,yaml
sys.path.insert(0,str(Path('qa-validation/lib').resolve()))
from day35_threshold_study import validate_threshold_config, Day35StudyError
REQ=[
 'configs/qc/thresholds.research-v0.1.yaml',
 'qa-validation/validation-reports/qc-threshold-sensitivity-v0.1.md',
 'ai-core/notebooks/06_threshold_sensitivity.ipynb',
 'docs/03-architecture/decisions/ADR-day35-research-thresholds.md',
 'qa-validation/evidence/day35-scorable-truth-readiness-matrix.csv',
 'qa-validation/evidence/day35-threshold-sensitivity-results-v0.1.csv',
 'qa-validation/evidence/day35-robustness-by-fs-window-v0.1.csv',
 'qa-validation/evidence/day35-threshold-selection-decision.v0.1.json',
]

def main():
 r=Path.cwd()
 missing=[x for x in REQ if not (r/x).exists()]
 if missing: raise SystemExit('missing: '+','.join(missing))
 cfg=yaml.safe_load((r/REQ[0]).read_text())
 validate_threshold_config(cfg)
 dec=json.loads((r/'qa-validation/evidence/day35-threshold-selection-decision.v0.1.json').read_text())
 if dec['locked_partition_consumed']!=0: raise SystemExit('locked leakage')
 if dec['decisions']['LF_POOR_CONTACT']['status']!='HOLD_NOT_SCORABLE': raise SystemExit('poor contact must hold')
 with (r/'qa-validation/evidence/day35-scorable-truth-readiness-matrix.csv').open() as f: rows=list(csv.DictReader(f))
 if len(rows)!=6: raise SystemExit('readiness must have six families')
 if any(x['site_threshold_status']!='NOT_VERIFIED' for x in rows): raise SystemExit('site status changed')
 text=(r/'qa-validation/validation-reports/qc-threshold-sensitivity-v0.1.md').read_text().lower()
 for bad in ('clinically validated threshold','validated at vinmec','clinical optimum'):
  if bad in text: raise SystemExit('forbidden claim '+bad)
 print(json.dumps({'status':'PASS','families':6,'locked_consumed':0,'site_threshold_status':'NOT_VERIFIED'},sort_keys=True))
if __name__=='__main__': main()
