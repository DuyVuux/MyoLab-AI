import json
from pathlib import Path
import sys

import jsonschema


HERE = Path(__file__).resolve()
ROOT = HERE.parents[3]
APPLICATION = ROOT / "services/quality-gate-service/src/application"
sys.path.insert(0, str(APPLICATION))

from normalization_eligibility import (  # noqa: E402
    NormalizationMethod,
    NormalizationReference,
    NormalizationRequest,
    NormalizationStatus,
    ReferenceType,
    evaluate_normalization_eligibility,
)


REFERENCE_HASH = "a" * 64


def request(**overrides):
    values = {
        "source_window_id": "w",
        "method": NormalizationMethod.MVC_PERCENT,
        "protocol_id": "p1",
        "domain_id": "d1",
        "partition": "benchmark-development",
        "units": "uV",
        "distribution_support_status": "SUPPORTED",
        "explicit_reference_id": None,
    }
    values.update(overrides)
    return NormalizationRequest(**values)


def reference(**overrides):
    values = {
        "reference_id": "r1",
        "reference_type": ReferenceType.MVC,
        "sha256": REFERENCE_HASH,
        "version": "1.0.0",
        "protocol_id": "p1",
        "domain_id": "d1",
        "partition": "reference-development",
        "units": "uV",
    }
    values.update(overrides)
    return NormalizationReference(**values)


def test_missing_reference_null_reason():
    result = evaluate_normalization_eligibility(request(), [])
    assert result.status == NormalizationStatus.UNAVAILABLE
    assert result.metric_value is None
    assert result.reference is None


def test_protocol_mismatch():
    result = evaluate_normalization_eligibility(
        request(),
        [reference(protocol_id="p2")],
    )
    assert result.status == NormalizationStatus.UNAVAILABLE
    assert "NORMALIZATION_PROTOCOL_MISMATCH" in result.reason_codes


def test_domain_mismatch():
    result = evaluate_normalization_eligibility(
        request(),
        [reference(domain_id="d2")],
    )
    assert result.status == NormalizationStatus.UNAVAILABLE
    assert "NORMALIZATION_DOMAIN_MISMATCH" in result.reason_codes


def test_locked_partition_guard():
    result = evaluate_normalization_eligibility(
        request(partition="benchmark-locked"),
        [reference()],
    )
    assert result.status == NormalizationStatus.BLOCKED
    assert result.reference is None


def test_unknown_distribution_support_abstains():
    result = evaluate_normalization_eligibility(
        request(distribution_support_status="UNKNOWN"),
        [reference()],
    )
    assert result.status == NormalizationStatus.UNAVAILABLE


def test_shifted_distribution_support_requires_revalidation():
    result = evaluate_normalization_eligibility(
        request(distribution_support_status="SHIFTED"),
        [reference()],
    )
    assert result.status == NormalizationStatus.UNAVAILABLE


def test_unique_compatible_reference_selected_deterministically():
    result = evaluate_normalization_eligibility(
        request(),
        [
            reference(reference_id="z", protocol_id="other"),
            reference(reference_id="a"),
        ],
    )
    assert result.status == NormalizationStatus.ELIGIBLE
    assert result.reference.reference_id == "a"


def test_ambiguous_reference_requires_explicit_id():
    result = evaluate_normalization_eligibility(
        request(),
        [reference(reference_id="a"), reference(reference_id="b")],
    )
    assert result.status == NormalizationStatus.UNAVAILABLE
    assert (
        "AMBIGUOUS_NORMALIZATION_REFERENCE_REQUIRE_EXPLICIT_ID"
        in result.reason_codes
    )


def test_explicit_reference_resolves_ambiguity():
    result = evaluate_normalization_eligibility(
        request(explicit_reference_id="b"),
        [reference(reference_id="a"), reference(reference_id="b")],
    )
    assert result.status == NormalizationStatus.ELIGIBLE
    assert result.reference.reference_id == "b"


def test_schema_accepts_result():
    result = evaluate_normalization_eligibility(
        request(),
        [reference()],
    ).to_dict()
    schema_path = (
        ROOT / "packages/common-schemas/json/normalization-eligibility.schema.json"
    )
    schema = json.loads(schema_path.read_text())
    jsonschema.Draft202012Validator(schema).validate(result)
