#!/usr/bin/env python3
from __future__ import annotations
import argparse, csv, hashlib, json, math, statistics
from collections import defaultdict
from pathlib import Path

METRICS=('rms','mav','mdf_hz','mnf_hz')
PUBLIC_TARGETS=('GRABMYO_V1_1_0','HYSER_V2_0_0')

def canon_hash(obj):
    return hashlib.sha256(json.dumps(obj,sort_keys=True,separators=(',',':')).encode()).hexdigest()

def read_rows(path):
    with open(path,newline='',encoding='utf-8') as f:
        rows=list(csv.DictReader(f))
    for r in rows:
        for k in ('fs_hz','rms','mav','mdf_hz','mnf_hz'): r[k]=float(r[k])
        r['sample_count']=int(r['sample_count'])
        sig=r['signal_name']
        if 'Ultium_EMG-LT_' in sig: r['side']='LT'; r['muscle']=sig.split('Ultium_EMG-LT_',1)[1]
        elif 'Ultium_EMG-RT_' in sig: r['side']='RT'; r['muscle']=sig.split('Ultium_EMG-RT_',1)[1]
        else: r['side']='UNKNOWN'; r['muscle']=sig
    return rows

def summary(vals):
    return {'n':len(vals),'mean':statistics.fmean(vals),'median':statistics.median(vals),'std':statistics.stdev(vals) if len(vals)>1 else 0.0,'min':min(vals),'max':max(vals)}

def analyze(rows,dataset_id):
    if len(rows)!=12: raise ValueError('expected 12 DAY68 feature rows')
    if any(r['status']!='AVAILABLE' for r in rows): raise ValueError('all DAY68 rows expected AVAILABLE')
    shared={'dataset_id':dataset_id,'fs_hz':sorted(set(r['fs_hz'] for r in rows)),'units':sorted(set(r['unit'] for r in rows)),'sample_counts':sorted(set(r['sample_count'] for r in rows)),'benchmark_versions':sorted(set(r['benchmark_version'] for r in rows)),'rows':len(rows),'origin':'VINMEC_SITE_RAW_TECHNICAL','claim_scope':'RESEARCH_ONLY'}
    fingerprint={'domain_fingerprint_id':'dfp_sha256_'+canon_hash(shared),'metadata':shared,'feature_summary':{m:summary([r[m] for r in rows]) for m in METRICS},'support_state':'SUPPORTED_FOR_SITE_TECHNICAL_DESCRIPTIVE_ANALYSIS','ood_score':None,'pathology_inference':False}
    by_side={}
    for side in ('LT','RT'):
        s=[r for r in rows if r['side']==side]
        by_side[side]={'n':len(s),'feature_summary':{m:summary([r[m] for r in s]) for m in METRICS}}
    pairs=[]
    lookup={(r['side'],r['muscle']):r for r in rows}
    muscles=sorted(set(r['muscle'] for r in rows))
    for muscle in muscles:
        l=lookup.get(('LT',muscle)); rr=lookup.get(('RT',muscle))
        if not l or not rr: continue
        rec={'muscle':muscle}
        for m in METRICS:
            meanabs=(abs(l[m])+abs(rr[m]))/2
            rec[m+'_abs_diff']=abs(rr[m]-l[m]); rec[m+'_relative_pair_difference']=abs(rr[m]-l[m])/meanabs if meanabs else None
        pairs.append(rec)
    comparisons=[]
    comparisons.append({'domain_a':dataset_id+':LT','domain_b':dataset_id+':RT','comparison_class':'CONDITIONALLY_COMPARABLE','support_state':'SHIFTED','basis':'same acquisition family/Fs/unit/sample count; paired muscles; descriptive only','n_a':6,'n_b':6,'ood_score':None,'pathology_inference':False,'reason_code':'WITHIN_SITE_LATERALITY_DESCRIPTIVE_ONLY'})
    for public in PUBLIC_TARGETS:
        comparisons.append({'domain_a':dataset_id,'domain_b':public,'comparison_class':'INCOMPARABLE','support_state':'UNKNOWN','basis':'DAY68 feature table contains no rows from requested public dataset','n_a':12,'n_b':0,'ood_score':None,'pathology_inference':False,'reason_code':'NO_PUBLIC_FEATURE_ROWS_IN_DAY68_SUMMARY'})
    return fingerprint,by_side,pairs,comparisons

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('csv'); ap.add_argument('--out-dir',required=True); ap.add_argument('--dataset-id',default='VINMEC_MOTION_LAB_EXAMPLE_OUTPUT'); ns=ap.parse_args()
    out=Path(ns.out_dir); out.mkdir(parents=True,exist_ok=True); rows=read_rows(ns.csv); fp,side,pairs,comparisons=analyze(rows,ns.dataset_id)
    (out/'domain-fingerprint.json').write_text(json.dumps({'fingerprint':fp,'side_domains':side,'matched_pair_differences':pairs},indent=2,sort_keys=True)+'\n')
    with (out/'cross-dataset-domain-shift-v1.0.csv').open('w',newline='',encoding='utf-8') as f:
        fields=['domain_a','domain_b','comparison_class','support_state','basis','n_a','n_b','ood_score','pathology_inference','reason_code']; w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(comparisons)
    print(json.dumps({'status':'DISTRIBUTION_SUPPORT_RESEARCH_EVIDENCE_READY','rows':len(rows),'comparisons':len(comparisons),'public_comparable_pairs':sum((x['comparison_class']!='INCOMPARABLE') and (('GRABMYO' in x['domain_b']) or ('HYSER' in x['domain_b'])) for x in comparisons),'ood_score':None},sort_keys=True))
if __name__=='__main__': main()
