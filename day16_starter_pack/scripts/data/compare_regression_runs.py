#!/usr/bin/env python3
"""So sánh candidate regression report với baseline đã đóng băng."""
from __future__ import annotations
import argparse, json
from pathlib import Path


def parse_args():
    p=argparse.ArgumentParser()
    p.add_argument('--baseline',type=Path,required=True)
    p.add_argument('--candidate',type=Path,required=True)
    return p.parse_args()


def main()->int:
    a=parse_args()
    baseline=json.loads(a.baseline.read_text(encoding='utf-8'))
    candidate=json.loads(a.candidate.read_text(encoding='utf-8'))
    checks=[]
    checks.append(('profile_id',baseline['profile_id'],candidate['profile']['profile_id']))
    checks.append(('profile_sha256',baseline['profile_sha256'],candidate['profile']['profile_sha256']))
    checks.append(('regression_fingerprint_sha256',baseline['regression_fingerprint_sha256'],candidate['regression_fingerprint_sha256']))
    candidate_signatures={x['scenario_id']:x['signature'] for x in candidate['scenarios']}
    checks.append(('scenario_signatures',baseline['scenario_signatures'],candidate_signatures))
    failed=[(name,expected,actual) for name,expected,actual in checks if expected!=actual]
    if failed:
        print('REGRESSION COMPARISON: FAIL')
        for name,expected,actual in failed:
            print(f'- {name}: expected={expected!r} actual={actual!r}')
        return 1
    print('REGRESSION COMPARISON: PASS')
    return 0

if __name__=='__main__': raise SystemExit(main())
