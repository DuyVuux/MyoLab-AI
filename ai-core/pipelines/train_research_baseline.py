#!/usr/bin/env python3
"""ML feasibility gate.

This file intentionally refuses to train under the current evidence state.
Its existence satisfies the roadmap's executable ML gate without fabricating a
model for portfolio decoration.
"""
from __future__ import annotations
import argparse, json
from pathlib import Path

REASONS=[
 'NO_DEFENSIBLE_SUPERVISED_TARGET',
 'NO_INDEPENDENT_SUBJECT_LEVEL_SAMPLES',
 'NO_REFERENCE_QC_LABELS',
 'PUBLIC_CROSS_DATASET_ROWS_ABSENT',
]

def decide(generalization:dict)->dict:
    rec=generalization.get('ml_question',{}).get('decision_recommendation')
    if rec!='ML_NO_GO':
        raise RuntimeError('Current frozen generalization evidence does not authorize training')
    return {
      'decision':'ML_NO_GO',
      'training_executed':False,
      'model_artifact':None,
      'calibration':'NOT_APPLICABLE',
      'conformal':'NOT_APPLICABLE',
      'locked_evaluation_consumed':False,
      'reason_codes':REASONS,
      'claim_scope':'RESEARCH_ONLY'
    }

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--generalization',required=True); ap.add_argument('--out'); ns=ap.parse_args()
    d=json.load(open(ns.generalization)); out=decide(d)
    text=json.dumps(out,indent=2,sort_keys=True)+'\n'
    if ns.out: Path(ns.out).write_text(text)
    print(json.dumps(out,sort_keys=True))
if __name__=='__main__': main()
