from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from integrations.devices.noraxon.site_export_audit import SiteEvidenceError, audit_site_evidence

ROOT = Path(__file__).resolve().parents[2]
BUNDLE = ROOT / "integrations/devices/noraxon/site-export-evidence-bundle.template.json"


def load_bundle() -> dict:
    return json.loads(BUNDLE.read_text(encoding="utf-8"))


def test_template_truthfully_reports_site_not_verified() -> None:
    report = audit_site_evidence(load_bundle())
    assert report["status"] == "NOT_VERIFIED"
    assert "SITE_EXPORT_NOT_INSPECTED" in report["blockers"]
    assert "JSON_NOT_VERIFIED" in report["blockers"]
    assert "MFCV_NOT_VERIFIED" in report["blockers"]


def test_mfcv_cannot_be_true_without_all_evidence() -> None:
    bundle = load_bundle()
    bundle["mfcv"]["eligible"] = True
    with pytest.raises(SiteEvidenceError, match="MFCV_ELIGIBILITY_INCONSISTENT"):
        audit_site_evidence(bundle)


def test_native_json_stays_false_in_template() -> None:
    bundle = load_bundle()
    assert bundle["exports"]["nativeJsonExportVerified"] is False
