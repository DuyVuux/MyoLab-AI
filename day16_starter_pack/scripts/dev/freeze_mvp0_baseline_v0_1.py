#!/usr/bin/env python3
"""Đóng băng regression baseline MVP-0 v0.1 từ report đã PASS."""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path


def file_sha256(path:Path)->str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse_args():
    p=argparse.ArgumentParser()
    p.add_argument('--report',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--overwrite',action='store_true')
    return p.parse_args()


def main()->int:
    a=parse_args()
    if a.output.exists() and not a.overwrite:
        raise SystemExit(f'Baseline đã tồn tại: {a.output}. Dùng --overwrite có chủ đích.')
    report=json.loads(a.report.read_text(encoding='utf-8'))
    if report.get('schema_version')!='mvp0-regression-report.v0.1' or report.get('passed') is not True:
        raise SystemExit('Chỉ được freeze report v0.1 đã PASS')
    golden=next(x for x in report['scenarios'] if x['scenario_id']=='golden')
    payload={
      'schema_version':'mvp0-regression-baseline.v0.1',
      'baseline_id':'mvp0_baseline_v0.1',
      'baseline_scope':'same_environment_exact_hash_plus_profile_numeric_ranges',
      'evidence_scope':report['evidence_scope'],
      'clinical_validation_status':'not_validated',
      'profile_id':report['profile']['profile_id'],
      'profile_sha256':report['profile']['profile_sha256'],
      'pipeline_config_sha256':report['profile']['pipeline_config_sha256'],
      'regression_fingerprint_sha256':report['regression_fingerprint_sha256'],
      'local_golden_analysis_fingerprint_sha256':golden['analysis_fingerprint_sha256'],
      'scenario_signatures':{x['scenario_id']:x['signature'] for x in report['scenarios']},
      'source_report_sha256':file_sha256(a.report),
      'limitations':[
        'Baseline khóa software behavior trên synthetic fixtures, không khóa clinical truth.',
        'Exact payload hash được kỳ vọng trong cùng environment; cross-environment cần numerical review.',
        'Mọi thay đổi profile/config/code có chủ đích phải tạo baseline version mới.'
      ]
    }
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(payload,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print('FROZEN:',a.output)
    return 0

if __name__=='__main__': raise SystemExit(main())
