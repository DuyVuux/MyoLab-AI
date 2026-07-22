#!/usr/bin/env python3
import json
from pathlib import Path
from jsonschema import Draft202012Validator
R=Path(__file__).resolve().parents[2]
def l(p):return json.loads(p.read_text())
def main():
 e=R/'qa-validation/evidence'; s=R/'packages/common-schemas/json'; v=l(e/'day12-evidence-verification.json'); a=l(e/'day12-fatigue-evidence.json'); b=l(e/'day12-fatigue-evidence-rerun.json'); x=l(e/'day12-fatigue-evidence-abstained.json')
 Draft202012Validator(l(s/'fatigue-evidence-verification.schema.json')).validate(v); [Draft202012Validator(l(s/'fatigue-evidence-result.schema.json')).validate(z) for z in (a,b,x)]
 if v['status']!='passed' or a['result_hash_sha256']!=b['result_hash_sha256']: raise SystemExit('verification/hash fail')
 if a['channels'][0]['pattern_category']!='multi_domain_change_pattern_observed': raise SystemExit('golden pattern unexpected')
 text=json.dumps(a).lower()
 for prohibited in ('fatigue_detected','no_fatigue','recommendation_vi','fatigue_resistance_score','probability_score'):
  if prohibited in text: raise SystemExit('prohibited output '+prohibited)
 if x['status']!='abstained' or x['channels']: raise SystemExit('abstention invalid')
 print('Day 12 outputs: PASS'); return 0
if __name__=='__main__': raise SystemExit(main())
