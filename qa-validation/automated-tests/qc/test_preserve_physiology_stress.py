from __future__ import annotations

import sys
from pathlib import Path

import pytest
import yaml

REPO = Path(__file__).resolve().parents[3]
LIB_DIR = REPO / "qa-validation" / "lib"
if str(LIB_DIR) not in sys.path:
    sys.path.insert(0, str(LIB_DIR))

import day36_domain_challenge as m

MANIFEST = REPO / "qa-validation" / "test-data" / "ood-challenge-set-manifest.v0.2-research.yaml"
THRESH = REPO / "configs" / "qc" / "thresholds.research-v0.1.yaml"


def load():
    return yaml.safe_load(MANIFEST.read_text(encoding="utf-8")), yaml.safe_load(THRESH.read_text(encoding="utf-8"))


def results():
    manifest, thresholds = load()
    return m.evaluate_manifest(REPO, manifest, thresholds)


def test_manifest_has_at_least_five_axes():
    manifest, _ = load()
    m.validate_manifest(manifest)
    assert len(set(manifest["axes"])) >= 5


def test_no_ood_model_or_score_allowed():
    manifest, _ = load()
    assert manifest["ood_method_status"] == "NOT_IMPLEMENTED"
    assert manifest["ood_score_allowed"] is False
    assert all(row.ood_score is None for row in results())


@pytest.mark.parametrize("case_id", ["D36-AMP-LOW-010", "D36-AMP-LOW-025"])
def test_low_amplitude_never_quality_blocks(case_id):
    row = next(item for item in results() if item.case_id == case_id)
    assert row.quality_blocked is False
    assert row.poor_contact_reason != "POOR_CONTACT_SUSPECTED"
    assert row.pathology_inference is False


def test_amplitude_metmorphic_relation_is_deterministic():
    manifest, _ = load()
    low = next(x for x in manifest["cases"] if x["case_id"] == "D36-AMP-LOW-010")
    ref = next(x for x in manifest["cases"] if x["case_id"] == "D36-REF-CLEAN")
    low2 = dict(low)
    low2["seed"] = ref["seed"]
    low2["amplitude_scale"] = 0.1
    x = m.generate_signal(ref)
    y = m.generate_signal(low2)
    assert pytest.approx(abs(y).mean(), rel=1e-12) == abs(x).mean() * 0.1


@pytest.mark.parametrize("case_id", ["D36-FS-1000", "D36-FS-4000", "D36-LAYOUT-B", "D36-PROTOCOL-V2", "D36-SESSION-DAY7", "D36-MORPH-HARMONIC"])
def test_domain_shift_not_equal_quality_failure(case_id):
    row = next(item for item in results() if item.case_id == case_id)
    assert row.distribution_support_status == "SHIFTED"
    assert row.quality_blocked is False


def test_optional_missing_modality_is_unknown_not_quality_fail():
    row = next(item for item in results() if item.case_id == "D36-OPTIONAL-MODALITY-UNKNOWN")
    assert row.distribution_support_status == "UNKNOWN"
    assert row.quality_blocked is False


def test_required_missing_modality_blocks_and_support_unknown():
    row = next(item for item in results() if item.case_id == "D36-REQUIRED-MODALITY-MISSING")
    assert row.quality_blocked is True
    assert row.distribution_support_status == "UNKNOWN"


def test_dropout_quality_failure_is_not_distribution_shift():
    row = next(item for item in results() if item.case_id == "D36-DROPOUT-HARD-CONTROL")
    assert row.quality_blocked is True
    assert row.distribution_support_status == "SUPPORTED"


def test_no_pathology_tokens_in_manifest():
    text = MANIFEST.read_text(encoding="utf-8").lower()
    for token in m.PATHOLOGY_TOKENS:
        assert token not in text


def test_domain_status_deterministic():
    a = [(x.case_id, x.distribution_support_status, x.distribution_reason_codes) for x in results()]
    b = [(x.case_id, x.distribution_support_status, x.distribution_reason_codes) for x in results()]
    assert a == b


def test_site_thresholds_remain_null():
    _, thresholds = load()
    site = thresholds["profiles"]["site-template"]["thresholds"]
    assert thresholds["site_threshold_status"] == "NOT_VERIFIED"
    assert all(value is None for value in site.values())


def test_poor_contact_still_not_selected_in_threshold_profile():
    _, thresholds = load()
    poor = thresholds["profiles"]["research-synthetic-v0.1"]["detectors"]["LF_POOR_CONTACT"]
    assert poor["status"] == "HOLD_NOT_SCORABLE"
    assert poor["parameters"] == {}
