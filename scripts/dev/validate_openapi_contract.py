#!/usr/bin/env python3
"""Lightweight OpenAPI 3.1 structural validator cho Day 17."""
from __future__ import annotations
import argparse,json,re
from pathlib import Path
from typing import Any
import yaml

HTTP_METHODS={'get','post','put','patch','delete','options','head','trace'}
FORBIDDEN_TOKENS={'patient_name','mrn','raw_samples','samples_uv','probability_of_fatigue','fatigue_detected','return_to_play_ready','stop_exercise'}


def resolve_pointer(root:Any,pointer:str)->Any:
    if not pointer.startswith('#/'):
        raise ValueError(f'Chỉ hỗ trợ local ref: {pointer}')
    cur=root
    for part in pointer[2:].split('/'):
        part=part.replace('~1','/').replace('~0','~')
        cur=cur[part]
    return cur


def walk_refs(node:Any,root:Any,hits:list[str],path='root'):
    if isinstance(node,dict):
        if '$ref' in node:
            try: resolve_pointer(root,node['$ref'])
            except Exception as exc: hits.append(f'{path}: {exc}')
        for k,v in node.items(): walk_refs(v,root,hits,f'{path}.{k}')
    elif isinstance(node,list):
        for i,v in enumerate(node): walk_refs(v,root,hits,f'{path}[{i}]')


def main()->int:
    p=argparse.ArgumentParser(); p.add_argument('--openapi',type=Path,required=True); a=p.parse_args()
    doc=yaml.safe_load(a.openapi.read_text(encoding='utf-8'))
    errors=[]
    if not str(doc.get('openapi','')).startswith('3.1.'):
        errors.append('openapi phải 3.1.x')
    if not isinstance(doc.get('paths'),dict) or not doc['paths']:
        errors.append('paths thiếu')
    operation_ids=[]
    for path,operations in doc.get('paths',{}).items():
        if not str(path).startswith('/'):
            errors.append(f'Path không bắt đầu /: {path}')
        for method,operation in operations.items():
            if method not in HTTP_METHODS: continue
            opid=operation.get('operationId')
            if not opid: errors.append(f'{method.upper()} {path} thiếu operationId')
            else: operation_ids.append(opid)
            if not operation.get('responses'): errors.append(f'{method.upper()} {path} thiếu responses')
    if len(operation_ids)!=len(set(operation_ids)): errors.append('operationId không unique')
    refs=[]; walk_refs(doc,doc,refs); errors.extend(refs)
    if 'bearerAuth' not in doc.get('components',{}).get('securitySchemes',{}): errors.append('Thiếu bearerAuth contract')
    serialized=json.dumps(doc,ensure_ascii=False).lower()
    for token in FORBIDDEN_TOKENS:
        if token in serialized: errors.append(f'Forbidden token trong OpenAPI: {token}')
    if errors:
        print('OPENAPI CONTRACT: FAIL')
        for e in errors: print('-',e)
        return 1
    print('OPENAPI CONTRACT: PASS')
    return 0

if __name__=='__main__': raise SystemExit(main())
