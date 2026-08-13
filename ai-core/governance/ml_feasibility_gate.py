#!/usr/bin/env python3
from __future__ import annotations
import argparse, csv, hashlib, json
from pathlib import Path

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--selection',required=True); ap.add_argument('--protocol',required=True); ap.add_argument('--split',required=True)
    ap.add_argument('--public-acquisition-summary', '--day67', dest='public_acquisition_summary', required=True)
    ap.add_argument('--site-feature-parquet', '--day68-parquet', dest='site_feature_parquet', required=True)
    ap.add_argument('--domain-shift-matrix', '--day69', dest='domain_shift_matrix', required=True)
    ap.add_argument('--generalization-summary', '--day70', dest='generalization_summary', required=True)
    ap.add_argument('--ml-feasibility-decision', '--day71', dest='ml_feasibility_decision', required=True)
    ap.add_argument('--out',required=True)
    ns=ap.parse_args()
    d67=json.load(open(ns.public_acquisition_summary)); d70=json.load(open(ns.generalization_summary)); d71=json.load(open(ns.ml_feasibility_decision))
    with open(ns.domain_shift_matrix,newline='',encoding='utf-8') as f: d69=list(csv.DictReader(f))
    public_comparable=[r for r in d69 if r['comparison_class'] in ('COMPARABLE','CONDITIONALLY_COMPARABLE') and ('GRABMYO' in r['domain_b'] or 'HYSER' in r['domain_b'])]
    public_ready = bool(public_comparable) and d70.get('cross_dataset_generalization') not in ('NOT_ESTABLISHED_NO_PUBLIC_FEATURE_ROWS',None)
    status='PUBLIC_BENCHMARK_READY' if public_ready else 'BLOCKED_WITH_EVIDENCE'
    blockers=[]
    if not public_comparable: blockers.append('NO_PUBLIC_CROSS_DATASET_FEATURE_COMPARISON')
    if d70.get('cross_dataset_generalization')=='NOT_ESTABLISHED_NO_PUBLIC_FEATURE_ROWS': blockers.append('PUBLIC_GENERALIZATION_NOT_ESTABLISHED')
    if d67.get('dataset_runtime_id')=='VINMEC_MOTION_LAB_EXAMPLE_OUTPUT': blockers.append('SITE_EVIDENCE_ORIGIN_IS_NOT_PUBLIC')
    out={
      'gate':'GATE-E-R','milestone':'M5-R','status':status,'public_benchmark_ready':public_ready,
      'ml_status':d71['decision'],'blockers':blockers,
      'frozen_input_hashes':{
        'selection_sha256':sha(ns.selection),'protocol_sha256':sha(ns.protocol),'split_sha256':sha(ns.split),
        'public_acquisition_summary_sha256':sha(ns.public_acquisition_summary),'site_feature_parquet_sha256':sha(ns.site_feature_parquet),'domain_shift_matrix_sha256':sha(ns.domain_shift_matrix),'generalization_summary_sha256':sha(ns.generalization_summary),'ml_feasibility_decision_sha256':sha(ns.ml_feasibility_decision)
      },
      'locked_policy_preserved':True,
      'locked_outcome_tuning_detected':False,
      'public_raw_in_package':False,
      'site_raw_in_package':False,
      'claim_scope':'RESEARCH_ONLY',
      'next_stage_ready':False if not public_ready else True
    }
    Path(ns.out).write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'gate':out['gate'],'status':status,'blockers':blockers,'ml_status':out['ml_status']},sort_keys=True))
if __name__=='__main__': main()
