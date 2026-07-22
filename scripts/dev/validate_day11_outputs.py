#!/usr/bin/env python3
import json
from pathlib import Path
from jsonschema import Draft202012Validator
R=Path(__file__).resolve().parents[2]
def load(p): return json.loads(p.read_text())
def main():
 e=R/'qa-validation/evidence'; s=R/'packages/common-schemas/json'
 v=load(e/'day11-trend-verification.json'); a=load(e/'day11-trends.json'); b=load(e/'day11-trends-rerun.json'); blocked=load(e/'day11-trends-blocked.json')
 Draft202012Validator(load(s/'trend-feature-verification.schema.json')).validate(v); Draft202012Validator(load(s/'trend-feature-extraction-result.schema.json')).validate(a); Draft202012Validator(load(s/'trend-feature-extraction-result.schema.json')).validate(b); Draft202012Validator(load(s/'trend-feature-extraction-result.schema.json')).validate(blocked)
 if v['status']!='passed': raise SystemExit('verification fail')
 if a['result_hash_sha256']!=b['result_hash_sha256']: raise SystemExit('hash mismatch')
 if a['summary']['computed_channel_count']!=1: raise SystemExit('golden cần 1 channel')
 names=set(a['channels'][0]['trends']);
 if names!={'rms','mav','mdf','mnf'}: raise SystemExit('thiếu trends')
 for t in a['channels'][0]['trends'].values():
  if 'p_value' in json.dumps(t) or 'confidence_interval' in json.dumps(t): raise SystemExit('không được inferential stats')
 if blocked['status']!='blocked': raise SystemExit('blocked fixture không block')
 print('Day 11 outputs: PASS'); return 0
if __name__=='__main__': raise SystemExit(main())
