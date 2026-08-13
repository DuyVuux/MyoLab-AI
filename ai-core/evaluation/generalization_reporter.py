#!/usr/bin/env python3
from __future__ import annotations
import argparse, csv, json
from pathlib import Path

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--public-acquisition-summary', '--day67', dest='public_acquisition_summary', required=True)
    ap.add_argument('--site-metric-summary', '--day68', dest='site_metric_summary', required=True)
    ap.add_argument('--domain-shift-matrix', '--day69-matrix', dest='domain_shift_matrix', required=True)
    ap.add_argument('--out', required=True)
    ns=ap.parse_args()
    d67=json.load(open(ns.public_acquisition_summary)); d68=json.load(open(ns.site_metric_summary))
    with open(ns.domain_shift_matrix,newline='',encoding='utf-8') as f: d69=list(csv.DictReader(f))
    public_comparable=sum(1 for r in d69 if r['comparison_class'] in ('COMPARABLE','CONDITIONALLY_COMPARABLE') and ('GRABMYO' in r['domain_b'] or 'HYSER' in r['domain_b']))
    out={
      'status':'GENERALIZATION_ANALYSIS_READY_WITH_LIMITATIONS',
      'denominators':{
        'public_acquisition_all_csv':d67['csv_detected'],
        'public_acquisition_parseable_csv':d67['csv_qc_parseable'],
        'public_acquisition_phi_metadata_excluded':d67['metadata_csv_phi_excluded'],
        'site_metric_rows':d68['rows'],
        'site_metric_available':d68['available'],
        'public_comparable_domain_pairs':public_comparable
      },
      'rates':{
        'technical_parse_coverage':d67['coverage'],
        'governance_abstention_rate':d67['abstention_rate'],
        'metric_availability_rate':(d68['available']/d68['rows']) if d68['rows'] else None
      },
      'supervised_qc_performance':'NOT_EVALUATED_NO_REFERENCE_LABELS',
      'false_block_proxy':'NOT_EVALUATED_NO_REFERENCE_LABELS',
      'cross_dataset_generalization':'NOT_ESTABLISHED_NO_PUBLIC_FEATURE_ROWS',
      'subject_generalization':'NOT_EVALUATED_SUBJECT_IDENTIFIERS_ABSENT',
      'session_generalization':'NOT_EVALUATED_SESSION_IDENTIFIERS_ABSENT',
      'site_technical_portability':'SUPPORTED_FOR_CURRENT_EXAMPLE_EXPORT_ONLY',
      'ml_question':{
        'decision_recommendation':'ML_NO_GO',
        'reason_codes':['NO_DEFENSIBLE_SUPERVISED_TARGET','NO_INDEPENDENT_SUBJECT_LEVEL_SAMPLES','NO_REFERENCE_QC_LABELS','PUBLIC_CROSS_DATASET_ROWS_ABSENT'],
        'deterministic_system_insufficient':False
      },
      'claim_scope':'RESEARCH_ONLY'
    }
    Path(ns.out).write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'status':out['status'],'public_comparable_pairs':public_comparable,'ml_recommendation':'ML_NO_GO'},sort_keys=True))
if __name__=='__main__': main()
