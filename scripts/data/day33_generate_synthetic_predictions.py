#!/usr/bin/env python3
from pathlib import Path
import csv,json
ROOT=Path(__file__).resolve().parents[2];out=ROOT/"qa-validation/fixtures/day33-synthetic-window-predictions.csv";out.parent.mkdir(parents=True,exist_ok=True)
classes=["rest","hand_close","wrist_flexion","wrist_extension"]
fields=["dataset_id","dataset_view_id","run_id","model_id","feature_arm","outer_fold","subject_id","day_id","session_id","repetition_id","record_id","window_id","y_true","y_pred","split_name","score_type","class_order_json","class_scores_json","qc_flags_json","source_matrix_sha256","fold_manifest_sha256","model_config_sha256"]
rows=[]
for s in range(1,9):
  sid=f"S{s:02d}"
  for true in classes:
    for rep in range(2):
      rid=f"{sid}-{true}-R{rep}"
      for w in range(4):
        pred="hand_close" if (s in {3,7} and true=="wrist_flexion" and rep==1 and w>=2) else true
        scores={c:(0.8 if c==pred else 0.2/3) for c in classes}
        rows.append({"dataset_id":"synthetic-day33-mendeley-like","dataset_view_id":"synthetic_core4","run_id":"synthetic-logistic-F-ALL14","model_id":"logistic_regression","feature_arm":"F-ALL14","outer_fold":s%3,"subject_id":sid,"day_id":"D1","session_id":"SE1","repetition_id":rid,"record_id":"REC-"+rid,"window_id":rid+f"-W{w}","y_true":true,"y_pred":pred,"split_name":"development_outer_validation","score_type":"probability","class_order_json":json.dumps(classes),"class_scores_json":json.dumps(scores),"qc_flags_json":json.dumps(["motion_warning"] if s==7 and w==3 else []),"source_matrix_sha256":"a"*64,"fold_manifest_sha256":"b"*64,"model_config_sha256":"c"*64})
with out.open("w",newline="",encoding="utf-8") as f:
  wr=csv.DictWriter(f,fieldnames=fields);wr.writeheader();wr.writerows(rows)
print(out)
