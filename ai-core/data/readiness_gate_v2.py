from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Iterable, Mapping

from data.evidence_catalog import validate_catalog
from data.group_split_v2 import assert_no_group_leakage


def canonical_hash(payload: object) -> str:
    encoded = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def load_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def build_day25_gate(
    *,
    inventory_rows: Iterable[Mapping[str, str]],
    conflict_rows: Iterable[Mapping[str, str]],
    source_rows: Iterable[Mapping[str, str]],
    site_audit: Mapping[str, object],
    split: Mapping[str, object],
) -> dict[str, object]:
    inventory = [dict(row) for row in inventory_rows]
    conflicts = [dict(row) for row in conflict_rows]
    sources = [dict(row) for row in source_rows]
    summary = validate_catalog(inventory)

    groups = dict(split["groups"])
    assert_no_group_leakage(
        groups["train"], groups["validation"], groups["test"]
    )

    site_checks = dict(site_audit["checks"])
    checks = {
        "fourSourceReportsRegistered": len(sources) >= 4,
        "datasetLandscapeConsolidated": summary.total >= 15,
        "priorityFreeCoreAvailable": summary.priority_free_core >= 5,
        "restrictedLandscapeCovered": summary.restricted >= 2,
        "conflictsExplicitlyRegistered": len(conflicts) >= 8,
        "subjectSafeSplitDemonstrated": split.get("groupUnit") == "subject",
        "testSetSealed": split.get("testSetSealed") is True,
        "actualSiteExportInspected": bool(
            site_checks.get("actualDeidentifiedExportInspected")
        ),
        "exactSiteExportSchemaVerified": bool(
            site_checks.get("exactFieldSchemaVerified")
        ),
        "nativeJsonExportVerified": bool(
            site_checks.get("nativeJsonExportVerified")
        ),
        "mfcvEligibilityVerified": bool(
            site_checks.get("mfcvEligibilityVerified")
        ),
        "privacyScreeningPassedForSiteExport": bool(
            site_checks.get("privacyScreeningPassed")
        ),
    }

    evidence_engineering_ready = all(
        checks[key]
        for key in [
            "fourSourceReportsRegistered",
            "datasetLandscapeConsolidated",
            "priorityFreeCoreAvailable",
            "restrictedLandscapeCovered",
            "conflictsExplicitlyRegistered",
            "subjectSafeSplitDemonstrated",
            "testSetSealed",
        ]
    )
    site_training_ready = all(
        checks[key]
        for key in [
            "actualSiteExportInspected",
            "exactSiteExportSchemaVerified",
            "privacyScreeningPassedForSiteExport",
        ]
    )

    if not evidence_engineering_ready:
        status = "BLOCKED"
        implementation_allowed = False
    elif site_training_ready:
        # Day 25 policy intentionally keeps training disabled until a selected
        # dataset manifest and legal approval are explicitly supplied later.
        status = "CONDITIONAL_READY"
        implementation_allowed = True
    else:
        status = "CONDITIONAL_READY"
        implementation_allowed = True

    training_allowed = False
    blockers = [
        label
        for key, label in {
            "actualSiteExportInspected": "Chưa kiểm actual de-identified Motion Lab export.",
            "exactSiteExportSchemaVerified": "Chưa khóa field-level export schema tại site.",
            "privacyScreeningPassedForSiteExport": "Chưa có site export vượt privacy screening.",
            "nativeJsonExportVerified": "Native JSON export chưa được xác minh; không được claim.",
            "mfcvEligibilityVerified": "MFCV eligibility chưa được xác minh; module phải disabled.",
        }.items()
        if not checks[key]
    ]
    blockers.append(
        "Chưa có selected model-ready dataset manifest đã được legal/governance phê duyệt."
    )

    report: dict[str, object] = {
        "schemaVersion": "data-readiness-gate.v0.2",
        "status": status,
        "implementationAllowed": implementation_allowed,
        "trainingAllowed": training_allowed,
        "checks": checks,
        "blockers": blockers,
        "allowedActions": [
            "Dựng dataset registry và adapter scaffolding.",
            "Kiểm thử canonical contract và subject-safe split.",
            "Gửi site evidence request package.",
            "Chuẩn bị model research blueprint Day 26 với resultStatus=not_run.",
        ],
        "prohibitedActions": [
            "Train hoặc tune model.",
            "Freeze exact Noraxon parser schema.",
            "Gọi JSON là native MR3 output.",
            "Bật MFCV khi chưa đủ eligibility evidence.",
            "Dùng restricted data ngoài DUA/IRB.",
            "Claim clinical performance từ public healthy datasets.",
        ],
    }
    report["reportHashSha256"] = canonical_hash(report)
    return report
