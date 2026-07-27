from __future__ import annotations

import hashlib
import json
from typing import Mapping


class SiteEvidenceError(ValueError):
    pass


def canonical_hash(payload: object) -> str:
    encoded = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def audit_site_evidence(bundle: Mapping[str, object]) -> dict[str, object]:
    exports = dict(bundle.get("exports") or {})
    hardware = dict(bundle.get("hardware") or {})
    software = dict(bundle.get("software") or {})
    mfcv = dict(bundle.get("mfcv") or {})
    privacy = dict(bundle.get("privacy") or {})

    required_mfcv = [
        "linearArrayConfirmed",
        "interElectrodeDistanceKnown",
        "electrodeOrderKnown",
        "fibreAlignmentConfirmed",
        "compatibleRawSignalAvailable",
        "propagationEvidenceAvailable",
    ]
    computed_mfcv_eligible = all(bool(mfcv.get(key)) for key in required_mfcv)
    if bool(mfcv.get("eligible")) != computed_mfcv_eligible:
        raise SiteEvidenceError("MFCV_ELIGIBILITY_INCONSISTENT_WITH_EVIDENCE")

    checks = {
        "hardwareVersionVerified": bool(hardware.get("verified")),
        "softwareVersionVerified": bool(software.get("verified")),
        "actualDeidentifiedExportInspected": bool(
            exports.get("actualDeidentifiedExportInspected")
        ),
        "exactFieldSchemaVerified": bool(exports.get("exactFieldSchemaVerified")),
        "nativeJsonExportVerified": bool(exports.get("nativeJsonExportVerified")),
        "mfcvEligibilityVerified": computed_mfcv_eligible,
        "privacyScreeningPassed": (
            bool(privacy.get("deidentified"))
            and privacy.get("phiScreening") == "pass"
        ),
    }

    blockers = []
    messages = {
        "hardwareVersionVerified": "HARDWARE_VERSION_NOT_VERIFIED",
        "softwareVersionVerified": "SOFTWARE_VERSION_NOT_VERIFIED",
        "actualDeidentifiedExportInspected": "SITE_EXPORT_NOT_INSPECTED",
        "exactFieldSchemaVerified": "EXACT_SCHEMA_NOT_VERIFIED",
        "nativeJsonExportVerified": "JSON_NOT_VERIFIED",
        "mfcvEligibilityVerified": "MFCV_NOT_VERIFIED",
        "privacyScreeningPassed": "PHI_SCREENING_NOT_PASSED",
    }
    for key, passed in checks.items():
        if not passed:
            blockers.append(messages[key])

    report: dict[str, object] = {
        "schemaVersion": "noraxon-site-audit.v0.1",
        "status": "SITE_VERIFIED" if all(checks.values()) else "NOT_VERIFIED",
        "checks": checks,
        "blockers": blockers,
        "safeConclusions": [
            "Project JSON remains a downstream representation unless native JSON is proven.",
            "MFCV must remain disabled unless every eligibility item is evidenced.",
            "Public vendor capabilities do not prove installed-site capability.",
        ],
    }
    report["reportHashSha256"] = canonical_hash(report)
    return report
