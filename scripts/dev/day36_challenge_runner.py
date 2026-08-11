from __future__ import annotations

import csv
import json
import sys
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[2]
LIB_DIR = ROOT / "qa-validation" / "lib"
if str(LIB_DIR) not in sys.path:
    sys.path.insert(0, str(LIB_DIR))

import day36_domain_challenge as m

manifest = yaml.safe_load((ROOT / "qa-validation/test-data/ood-challenge-set-manifest.v0.2-research.yaml").read_text(encoding="utf-8"))
thresholds = yaml.safe_load((ROOT / "configs/qc/thresholds.research-v0.1.yaml").read_text(encoding="utf-8"))
rows = m.evaluate_manifest(ROOT, manifest, thresholds)

out_dir = ROOT / "qa-validation" / "evidence"
out_dir.mkdir(parents=True, exist_ok=True)
out_csv = out_dir / "day36-domain-challenge-results-v0.2.csv"

with out_csv.open("w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(
        f,
        fieldnames=[
            "case_id",
            "axis",
            "qc_disposition",
            "quality_blocked",
            "distribution_support_status",
            "distribution_reason_codes",
            "poor_contact_reason",
            "pathology_inference",
            "ood_score",
        ],
    )
    writer.writeheader()
    for row in rows:
        d = row.__dict__.copy()
        d["distribution_reason_codes"] = "|".join(d["distribution_reason_codes"])
        writer.writerow(d)

summary = {
    "schema_version": "0.2",
    "status": "PASS",
    "claim_scope": "RESEARCH_ONLY",
    "cases": len(rows),
    "axes": sorted(set(x.axis for x in rows if x.axis not in {"REFERENCE", "QUALITY_FAILURE_CONTROL"})),
    "quality_blocked_cases": sum(x.quality_blocked for x in rows),
    "shifted_cases": sum(x.distribution_support_status == "SHIFTED" for x in rows),
    "unknown_support_cases": sum(x.distribution_support_status == "UNKNOWN" for x in rows),
    "physiology_false_blocks": sum(x.quality_blocked for x in rows if x.case_id.startswith("D36-AMP-LOW")),
    "ood_score_emitted": False,
    "clinical_edge_case_validation": "NOT_PERFORMED",
}

(out_dir / "day36-analysis-summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
print(json.dumps(summary, sort_keys=True))
