#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path('packages/semg-core').resolve()))
sys.path.insert(0,str(Path('qa-validation/lib').resolve()))
import yaml
from day35_threshold_study import (
    load_yaml, load_fixtures, run_sweep, evaluate_robustness, write_csv,
    verify_day33_locked_isolation, validate_threshold_config,
)

ROOT=Path.cwd()
PROFILE=ROOT/'configs/qc/day35-threshold-study-profile.v0.1.yaml'
FX_MAN=ROOT/'qa-validation/evidence/day35-threshold-study-fixtures.v0.1.manifest.yaml'
FX_ROOT=ROOT/'qa-validation/test-data/research/day35'
DAY33=ROOT/'qa-validation/evidence/research-benchmark-corpus-v0.1.manifest.yaml'
OUT=ROOT/'qa-validation/evidence'
THRESH=ROOT/'configs/qc/thresholds.research-v0.1.yaml'


def main():
    profile=load_yaml(PROFILE)
    fxm=load_yaml(FX_MAN)
    day33=load_yaml(DAY33)
    locked_count=verify_day33_locked_isolation(day33)
    all_fx=load_fixtures(fxm,FX_ROOT)
    primary=[x for x in all_fx if x['stratum']=='PRIMARY']
    rows,selected=run_sweep(profile,primary,ROOT)
    robust=evaluate_robustness(profile,all_fx,selected,ROOT)
    write_csv(OUT/'day35-threshold-sensitivity-results-v0.1.csv',rows)
    write_csv(OUT/'day35-robustness-by-fs-window-v0.1.csv',robust)
    # Selected primary scores are reconstructed from the minimum rows.
    decisions={}
    for fam,params in selected.items():
        cand=[r for r in rows if r['family_id']==fam and all(float(r[k])==float(v) for k,v in params.items())]
        best=sorted(cand,key=lambda r:(r['weighted_error'],r['distance_from_upstream']))[0]
        decisions[fam]={'status':'SELECTED_RESEARCH_HEURISTIC','parameters':params,
                        'primary_synthetic_score':{k:best[k] for k in ('tp','fp','tn','fn','sensitivity','specificity','precision','f1','weighted_error')},
                        'evidence_class':'RESEARCH_HEURISTIC','clinical_threshold_claim':False}
    decisions['LF_POOR_CONTACT']={'status':'HOLD_NOT_SCORABLE','parameters':{},
       'reason':'NO_MULTI_CHANNEL_POSITIVE_KNOWN_TRUTH','evidence_class':'SITE_NOT_VERIFIED',
       'clinical_threshold_claim':False}
    decision_doc={'schema_version':'0.1','study_version':profile['study_version'],'claim_scope':'RESEARCH_ONLY',
      'selection_objective':profile['selection_objective'],'locked_partition_consumed':0,
      'locked_partition_items_seen_only_as_sealed_manifest_entries':locked_count,
      'day33_history_mutated':False,'decisions':decisions,
      'limitations':['synthetic engineering truth only','no public raw payload evaluation','no expert/site validation']}
    (OUT/'day35-threshold-selection-decision.v0.1.json').write_text(json.dumps(decision_doc,indent=2)+'\n')
    site_thresholds={
      'missing_warning_fraction':None,'zero_run_warning_fraction':None,'flatline_peak_to_peak_epsilon':None,
      'clipping_repeated_extrema_fraction':None,'baseline_rms_warning_threshold':None,
      'baseline_mad_warning_threshold':None,'powerline_warning_ratio':None,'motion_warning_low_ratio':None,
      'motion_drift_warning_normalized':None,'motion_transient_warning_z':None,
      'poor_contact_relative_rms_low_ratio':None,
    }
    research={fam:{'status':doc['status'],'evidence_class':doc['evidence_class'],
                   'parameters':doc['parameters'],'clinical_threshold_claim':False}
              for fam,doc in decisions.items()}
    cfg={'schema_version':'0.1','claim_scope':'RESEARCH_ONLY','site_threshold_status':'NOT_VERIFIED',
      'profiles':{
        'site-template':{'status':'SITE_NOT_VERIFIED','thresholds':site_thresholds,
                         'clinical_threshold_claim':False},
        'research-synthetic-v0.1':{'status':'RESEARCH_HEURISTIC','clinical_threshold_claim':False,
          'scope':'SYNTHETIC_ENGINEERING_AND_PUBLIC_RESEARCH_ONLY','detectors':research}},
      'provenance':{'study_version':profile['study_version'],
        'selection_evidence_ref':'qa-validation/evidence/day35-threshold-selection-decision.v0.1.json',
        'fixture_manifest_ref':'qa-validation/evidence/day35-threshold-study-fixtures.v0.1.manifest.yaml',
        'locked_partition_consumed':0,'day33_history_mutated':False}}
    validate_threshold_config(cfg)
    THRESH.write_text(yaml.safe_dump(cfg,sort_keys=False),encoding='utf-8')
    print(json.dumps({'status':'PASS','primary_fixtures':len(primary),'all_fixtures':len(all_fx),
                      'locked_consumed':0,'selected_families':len(selected),'poor_contact':'HOLD'},sort_keys=True))
if __name__=='__main__': main()
