#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, os, platform, sys
from importlib.metadata import version, PackageNotFoundError
from pathlib import Path

p=argparse.ArgumentParser(); p.add_argument('--output',required=True); a=p.parse_args()
def v(name):
    try: return version(name)
    except PackageNotFoundError: return None
payload={'python':sys.version,'executable':sys.executable,'platform':platform.platform(),'machine':platform.machine(),'processor':platform.processor(),'packages':{n:v(n) for n in ['numpy','scipy','scikit-learn','mlflow','pyyaml','jsonschema']},'thread_env':{k:os.getenv(k) for k in ['OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS','BLIS_NUM_THREADS','VECLIB_MAXIMUM_THREADS','NUMEXPR_NUM_THREADS']}}
out=Path(a.output); out.parent.mkdir(parents=True,exist_ok=True); out.write_text(json.dumps(payload,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print(out)
