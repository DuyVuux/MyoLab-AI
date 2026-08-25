#!/usr/bin/env python3
import json,sys
from pathlib import Path
B=["signal_read_model","processed_signal_store","processing_manifest_store","metric_read_model","review_state_machine","audit_event_store"]
S=["executed","raw_window_observed","raw_source_identity_present","processed_window_observed","processed_manifest_present","metric_evidence_observed","ineligible_metric_null_with_reason_observed","review_action_observed","review_revision_advanced","audit_event_read_back"]
def main():
 root=Path(sys.argv[1] if len(sys.argv)>1 else ".").resolve();p=root/"qa-validation/evidence/ui-i3-live-backend-binding.json"
 if not p.exists():print("BLOCKED_EVIDENCE_BINDING: missing",p);return 5
 d=json.loads(p.read_text());e=[]
 if d.get("status")!="PASS":e.append("status != PASS")
 b=d.get("canonical_bindings") or {}; s=d.get("real_mode_smoke") or {}
 for k in B:
  if not b.get(k):e.append("missing binding: "+k)
 if s.get("mock_or_demo_backend_used") is not False:e.append("real-mode smoke must prove mock/demo backend was not used")
 for k in S:
  if s.get(k) is not True:e.append("smoke missing/false: "+k)
 for k in ["session_id","channel_id","review_case_id","audit_event_id"]:
  if not s.get(k):e.append("smoke identity missing: "+k)
 if e:
  print("BLOCKED_EVIDENCE_BINDING");[print("-",x) for x in e];return 5
 print("PASS: UI-I3 live evidence backend binding");return 0
if __name__=="__main__":raise SystemExit(main())
