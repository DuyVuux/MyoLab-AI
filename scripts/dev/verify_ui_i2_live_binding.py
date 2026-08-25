#!/usr/bin/env python3
from __future__ import annotations
import json, sys
from pathlib import Path

def main():
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
    path = root / "qa-validation/evidence/ui-i2-live-backend-binding.json"
    if not path.exists():
        print("BLOCKED_BACKEND_BINDING: missing", path)
        return 5

    data = json.loads(path.read_text(encoding="utf-8"))
    errors = []
    if data.get("status") != "PASS":
        errors.append("binding status is not PASS")

    bindings = data.get("canonical_bindings") or {}
    for key in ["sessions", "ingestion", "preflight", "mapping", "quality", "pipeline_job"]:
        if not bindings.get(key):
            errors.append(f"missing canonical binding: {key}")

    smoke = data.get("real_mode_smoke") or {}
    if smoke.get("executed") is not True:
        errors.append("real-mode smoke not executed")
    if smoke.get("mock_or_demo_backend_used") is not False:
        errors.append("real-mode smoke must explicitly prove mock/demo backend was NOT used")
    if smoke.get("source_hash_present") is not True:
        errors.append("real-mode smoke did not prove source hash")
    for key in ["preflight_observed", "mapping_observed", "quality_observed"]:
        if smoke.get(key) is not True:
            errors.append(f"real-mode smoke missing: {key}")

    if not data.get("route_registration"):
        errors.append("route registration evidence missing")

    if errors:
        print("BLOCKED_BACKEND_BINDING")
        for item in errors:
            print("-", item)
        return 5

    print("PASS: UI-I2 live backend binding evidence")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
