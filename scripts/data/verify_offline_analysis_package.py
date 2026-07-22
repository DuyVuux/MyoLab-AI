#!/usr/bin/env python3
"""Kiểm tra tính toàn vẹn của một output directory Day 15."""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PIPELINES = ROOT / "ai-core/pipelines"
if str(PIPELINES) not in sys.path:
    sys.path.insert(0, str(PIPELINES))
from analysis_manifest import canonical_json_sha256


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--analysis-dir", type=Path, required=True)
    p.add_argument("--json-out", type=Path)
    return p.parse_args()


def scan(payload, path="root"):
    hits = []
    forbidden_keys = {"samples", "samples_uV", "raw_samples", "signal_values", "patient_name", "mrn", "email", "phone"}
    if isinstance(payload, dict):
        for key, value in payload.items():
            if key in forbidden_keys:
                hits.append(f"{path}.{key}")
            hits.extend(scan(value, f"{path}.{key}"))
    elif isinstance(payload, list):
        for idx, value in enumerate(payload):
            hits.extend(scan(value, f"{path}[{idx}]"))
    return hits


def main() -> int:
    a = parse_args()
    manifest_path = a.analysis_dir / "11-analysis-manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    checks = []
    all_payloads = []
    for record in manifest["pipeline"]["stage_records"]:
        path = a.analysis_dir / record["output_file"]
        exists = path.is_file()
        checks.append({"check_id": f"stage_file_{record['stage_id']}", "passed": exists})
        if exists:
            payload = json.loads(path.read_text(encoding="utf-8"))
            all_payloads.append(payload)
            actual = canonical_json_sha256(payload)
            checks.append({
                "check_id": f"stage_hash_{record['stage_id']}",
                "passed": actual == record["output_payload_sha256"],
                "expected": record["output_payload_sha256"],
                "actual": actual,
            })
    hits = []
    for payload in all_payloads + [manifest]:
        hits.extend(scan(payload))
    checks.append({"check_id": "no_raw_or_direct_identifier_keys", "passed": not hits, "hits": hits})
    checks.append({"check_id": "clinical_use_disabled", "passed": manifest["final"]["clinical_use_allowed"] is False})
    checks.append({"check_id": "human_review_required", "passed": manifest["final"]["human_review_required"] is True})
    payload = {
        "schema_version": "offline-analysis-verification.v0.1",
        "passed": all(item["passed"] for item in checks),
        "analysis_fingerprint_sha256": manifest["analysis_fingerprint_sha256"],
        "checks": checks,
    }
    if a.json_out:
        a.json_out.parent.mkdir(parents=True, exist_ok=True)
        a.json_out.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("OFFLINE ANALYSIS PACKAGE VERIFICATION:", "PASS" if payload["passed"] else "FAIL")
    return 0 if payload["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
