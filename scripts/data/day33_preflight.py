#!/usr/bin/env python3
from pathlib import Path
import argparse,json
p=argparse.ArgumentParser()
p.add_argument("--day32-preflight",required=True);p.add_argument("--day32-core-smoke",required=True);p.add_argument("--day32-optional",required=True);p.add_argument("--output",required=True)
a=p.parse_args()
pre=json.loads(Path(a.day32_preflight).read_text());core=json.loads(Path(a.day32_core_smoke).read_text());opt=json.loads(Path(a.day32_optional).read_text())
errors=[]
if pre.get("pass") is not True:errors.append("day32_preflight_failed")
if core.get("core_gate",{}).get("status")!="CORE_GATE_PASS":errors.append("core_gate_not_pass")
if core.get("sealed_test_rows_read")!=0:errors.append("sealed_test_nonzero")
if core.get("pooled_training_executed") is not False:errors.append("pooled_training")
r={"schema_version":"day33-preflight.v1","pass":not errors,"errors":errors,"day32_scope":core.get("scope"),
"day32_real_data_rows_read":core.get("real_data_rows_read"),"day32_real_fitting_executed":opt.get("real_fitting_executed"),
"real_prediction_inventory_present":False,"current_mode":"TOOLING_VALIDATION",
"current_status":"TOOLING_READY_REAL_EVALUATION_BLOCKED","sealed_test_opened":False,"pooled_evaluation_allowed":False}
o=Path(a.output);o.parent.mkdir(parents=True,exist_ok=True);o.write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
raise SystemExit(0 if r["pass"] else 2)
