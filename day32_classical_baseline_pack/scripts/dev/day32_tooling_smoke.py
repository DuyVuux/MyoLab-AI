#!/usr/bin/env python3
from pathlib import Path
import sys, json, numpy as np
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/"ai-core/modeling"))
from day32.model_factory import build_core_models, build_optional_models, CORE_MODEL_IDS
from day32.grouped_cv import make_grouped_folds
from day32.smoke_runner import run_synthetic_core_smoke
from day32.core_gate import decide_core_gate

data=np.load(ROOT/"qa-validation/fixtures/day32-synthetic-matrix.npz",allow_pickle=False)
folds=make_grouped_folds(data["y"],data["groups"],3)
f=folds[0]
results=run_synthetic_core_smoke(
    data["X"],data["y"],
    np.asarray(f["train_indices"]),
    np.asarray(f["validation_indices"]),
)
gate=decide_core_gate(results)
out_data={
    "schema_version":"day32-tooling-validation.v1",
    "core_model_ids":list(build_core_models()),
    "optional_model_ids":list(build_optional_models()),
    "fold_count":len(folds),
    "core_results":results,
    "core_gate":gate,
    "real_data_rows_read":0,
    "sealed_test_rows_read":0,
    "pooled_training_executed":False,
    "pass":gate["status"] != "CORE_GATE_BLOCKED",
}
out=ROOT/"qa-validation/evidence/day32-tooling-validation.json"
out.parent.mkdir(parents=True,exist_ok=True)
out.write_text(json.dumps(out_data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps(out_data,ensure_ascii=False,indent=2))
raise SystemExit(0 if out_data["pass"] else 2)
