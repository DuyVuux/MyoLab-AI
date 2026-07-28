from __future__ import annotations

import hashlib
import json
from typing import Any

from .contracts import is_sha256
from .group_split import assert_no_overlap


def _hash(value: object) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def build_engineering_gate(inputs: dict[str, Any]) -> dict[str, Any]:
    source = inputs.get("sourceVerification", {})
    receipt = inputs.get("retrievalReceipt", {})
    inventory = inputs.get("archiveInventory", {})
    profile = inputs.get("adapterProfile", {})
    label_report = inputs.get("labelMappingReport", {})
    smoke = inputs.get("canonicalSmokeReport", {})
    split = inputs.get("groupSplit", {})
    eligibility = inputs.get("experimentEligibility", {})

    groups = split.get("groups", {"train": [], "validation": [], "test": []})
    try:
        assert_no_overlap(groups)
        no_overlap = True
    except Exception:
        no_overlap = False

    checks = {
        "sourceVerified": source.get("status") == "VERIFIED",
        "archiveHashPresent": is_sha256(receipt.get("sha256")),
        "licenseAccepted": receipt.get("licenseAccepted") is True,
        "archiveSafe": inventory.get("safeToExtract") is True,
        "sourceFormatVerified": profile.get("verificationStatus") == "VERIFIED",
        "samplingRateKnown": isinstance(profile.get("signal", {}).get("samplingRateHz"), (int, float)),
        "unitKnown": profile.get("signal", {}).get("sourceUnit") in {"V", "mV", "uV", "µV"},
        "channelOrderKnown": bool(profile.get("signal", {}).get("channels")),
        "labelMapVerified": label_report.get("status") == "VERIFIED",
        "canonicalSmokePassed": smoke.get("status") == "PASS",
        "subjectSplitPresent": split.get("groupUnit") == "subject",
        "noGroupOverlap": no_overlap,
        "testSetSealed": split.get("testSetSealed") is True and split.get("testOpened") is False,
        "experimentEligibilityMapped": eligibility.get("status") == "MAPPED",
        "trainingStillLocked": inputs.get("trainingExecutionAllowed") is False,
        "motionLabTransferNotClaimed": inputs.get("motionLabTransferVerified") is False,
        "clinicalUseNotClaimed": inputs.get("clinicalUseAllowed") is False,
    }
    all_required = all(checks.values())
    status = "GO_FOR_DAY28_EDA" if all_required else "BLOCKED_SOURCE_OR_SCHEMA"
    blockers = [key for key, value in checks.items() if not value]
    report: dict[str, Any] = {
        "schemaVersion": "engineering-data-gate.v1",
        "status": status,
        "checks": checks,
        "blockers": blockers,
        "publicDatasetEngineeringReady": all_required,
        "publicBaselineTrainingEligible": all_required,
        "trainingExecutionAllowed": False,
        "testSetSealed": checks["testSetSealed"],
        "motionLabTransferVerified": False,
        "clinicalUseAllowed": False,
        "allowedNextActions": ["Day28 EDA on train/validation only"] if all_required else ["Resolve blockers and rerun gate"],
        "prohibitedActions": ["Training", "Opening sealed test", "Motion Lab or clinical claims"],
    }
    report["reportSha256"] = _hash(report)
    return report
