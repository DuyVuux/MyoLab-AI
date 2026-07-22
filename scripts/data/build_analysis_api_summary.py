#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
SCHEMAS=ROOT/'services/api-server/src/schemas'
if str(SCHEMAS) not in sys.path: sys.path.insert(0,str(SCHEMAS))
from analysis_contract import build_session_analysis_summary


def main()->int:
    p=argparse.ArgumentParser()
    p.add_argument('--analysis-dir',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--base-url',default='/v1')
    a=p.parse_args()
    summary=build_session_analysis_summary(a.analysis_dir,base_url=a.base_url)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(summary.model_dump(mode='json'),indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print('SUMMARY:',summary.status,summary.technical_conclusion,summary.summary_hash_sha256)
    return 0

if __name__=='__main__': raise SystemExit(main())
