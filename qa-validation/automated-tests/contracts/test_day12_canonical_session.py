from __future__ import annotations

import importlib.util
import json
import re
import sys
from pathlib import Path

import jsonschema
import pytest
from pydantic import ValidationError
from referencing import Registry, Resource


ROOT = Path(__file__).resolve().parents[3]
SCHEMA_DIR = ROOT / "packages/common-schemas/json"
GOLDEN = ROOT / "qa-validation/test-data/golden/canonical/day12"
CORRUPTED = ROOT / "qa-validation/test-data/corrupted/canonical/day12"
MODULE_PATH = (
    ROOT
    / "services/signal-ingestion-service/src/canonical/session_contracts.py"
)
TRACE = ROOT / "qa-validation/traceability/day12-requirement-traceability.csv"
README = ROOT / "README.md"


def load_module():
    module_name = "day12_session_contracts_test_target"
    spec = importlib.util.spec_from_file_location(module_name, MODULE_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


M = load_module()


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def schema_registry() -> Registry:
    registry = Registry()
    for name in (
        "signal.schema.json",
        "protocol-context.schema.json",
        "domain-context.schema.json",
        "process-correlation.schema.json",
        "session.schema.json",
    ):
        content = read_json(SCHEMA_DIR / name)
        resource = Resource.from_contents(content)
        registry = registry.with_resource(content["$id"], resource)
        registry = registry.with_resource(
            f"https://motionlab.local/schemas/{name}", resource
        )
    return registry


def validate_json_schema(instance: dict) -> None:
    schema = read_json(SCHEMA_DIR / "session.schema.json")
    validator = jsonschema.Draft202012Validator(
        schema,
        registry=schema_registry(),
        format_checker=jsonschema.FormatChecker(),
    )
    validator.validate(instance)


def model_from(path: Path):
    return M.CanonicalSession.model_validate(read_json(path))


def test_01_required_schemas_exist_and_are_draft_2020_12() -> None:
    for name in (
        "session.schema.json",
        "signal.schema.json",
        "protocol-context.schema.json",
        "domain-context.schema.json",
        "process-correlation.schema.json",
    ):
        schema = read_json(SCHEMA_DIR / name)
        assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"
        jsonschema.Draft202012Validator.check_schema(schema)


def test_02_unknown_safe_fixture_is_valid_runtime_contract() -> None:
    session = model_from(GOLDEN / "session_unknown_safe.json")
    assert session.protocol_context.side.value is None
    assert session.protocol_context.side.evidence_status is M.EvidenceStatus.UNKNOWN


def test_03_verified_protocol_fixture_is_valid_runtime_contract() -> None:
    session = model_from(GOLDEN / "session_verified_protocol_synthetic.json")
    assert session.protocol_context.protocol_id.evidence_status is M.EvidenceStatus.VERIFIED
    assert session.domain_context.context_category is M.ContextCategory.SYNTHETIC


def test_04_golden_fixtures_validate_against_json_schema() -> None:
    for path in sorted(GOLDEN.glob("*.json")):
        validate_json_schema(read_json(path))


def test_05_unknown_cannot_carry_invented_value() -> None:
    with pytest.raises((ValidationError, M.ContractError)):
        M.EvidenceString(
            value="invented",
            evidence_status=M.EvidenceStatus.UNKNOWN,
            evidence_refs=(),
        )


def test_06_verified_value_requires_evidence_reference() -> None:
    with pytest.raises((ValidationError, M.ContractError)):
        M.EvidenceString(
            value="v0.1",
            evidence_status=M.EvidenceStatus.VERIFIED,
            evidence_refs=(),
        )


def test_07_source_reported_requires_source_value() -> None:
    with pytest.raises((ValidationError, M.ContractError)):
        M.EvidenceString(
            value=None,
            evidence_status=M.EvidenceStatus.SOURCE_REPORTED,
            evidence_refs=("source:x",),
        )


def test_08_identifier_generators_are_opaque_and_pattern_valid() -> None:
    values = {
        "session": M.new_session_id(),
        "subject": M.new_subject_analysis_id(),
        "signal": M.new_signal_id(),
        "case": M.new_case_id(),
        "correlation": M.new_correlation_id(),
    }
    assert re.fullmatch(r"ses_[0-9a-f]{32}", values["session"])
    assert re.fullmatch(r"subj_[0-9a-f]{32}", values["subject"])
    assert re.fullmatch(r"sig_[0-9a-f]{32}", values["signal"])
    assert re.fullmatch(r"case_[0-9a-f]{32}", values["case"])
    assert re.fullmatch(r"corr_[0-9a-f]{32}", values["correlation"])
    assert len(set(values.values())) == len(values)


def test_09_session_id_rejects_phi_like_free_text() -> None:
    bad = read_json(CORRUPTED / "invalid_phi_like_session_id.json")
    with pytest.raises(ValidationError):
        M.CanonicalSession.model_validate(bad)


def test_10_process_correlation_must_reference_same_session() -> None:
    bad = read_json(CORRUPTED / "invalid_correlation_session_mismatch.json")
    with pytest.raises((ValidationError, M.ContractError)):
        M.CanonicalSession.model_validate(bad)


def test_11_process_correlation_forbids_raw_payload() -> None:
    bad = read_json(CORRUPTED / "invalid_process_raw_payload.json")
    with pytest.raises(ValidationError):
        M.CanonicalSession.model_validate(bad)


def test_12_record_name_is_reference_not_copied_free_text() -> None:
    session = model_from(GOLDEN / "session_unknown_safe.json")
    assert session.record_name_ref is not None
    assert session.record_name_ref.field_path == "record_name"
    assert session.record_name_ref.exposure_policy == "RESTRICTED_SOURCE_METADATA"
    assert not hasattr(session, "record_name")


def test_13_every_signal_references_a_session_source_record() -> None:
    bad = read_json(CORRUPTED / "invalid_signal_orphan_source.json")
    with pytest.raises((ValidationError, M.ContractError)):
        M.CanonicalSession.model_validate(bad)


def test_14_source_record_ids_are_unique() -> None:
    bad = read_json(CORRUPTED / "invalid_duplicate_source_ids.json")
    with pytest.raises((ValidationError, M.ContractError)):
        M.CanonicalSession.model_validate(bad)


def test_15_signal_ids_are_unique_within_session() -> None:
    data = read_json(GOLDEN / "session_unknown_safe.json")
    duplicate = json.loads(json.dumps(data["signals"][0]))
    data["signals"].append(duplicate)
    with pytest.raises((ValidationError, M.ContractError)):
        M.CanonicalSession.model_validate(data)


def test_16_sampling_rate_must_be_positive_when_known() -> None:
    bad = read_json(CORRUPTED / "invalid_negative_sampling_rate.json")
    with pytest.raises(ValidationError):
        M.CanonicalSession.model_validate(bad)


def test_17_unknown_channel_mapping_cannot_contain_channel_id() -> None:
    with pytest.raises((ValidationError, M.ContractError)):
        M.CanonicalChannelRef(
            channel_id="left_biceps",
            mapping_version="v0.1",
            evidence_status=M.EvidenceStatus.UNKNOWN,
            evidence_refs=(),
        )


def test_18_mapped_channel_requires_mapping_version() -> None:
    with pytest.raises((ValidationError, M.ContractError)):
        M.CanonicalChannelRef(
            channel_id="left_biceps",
            mapping_version=None,
            evidence_status=M.EvidenceStatus.SOURCE_REPORTED,
            evidence_refs=("source:signal",),
        )


def test_19_source_vendor_text_is_not_silently_trimmed() -> None:
    evidence = M.EvidenceString(
        value="  Ultium_EMG-LT_BICEPS_FEM.  ",
        evidence_status=M.EvidenceStatus.SOURCE_REPORTED,
        evidence_refs=("source:name",),
    )
    assert evidence.value == "  Ultium_EMG-LT_BICEPS_FEM.  "


def test_20_vendor_name_does_not_auto_infer_side_or_channel() -> None:
    session = model_from(GOLDEN / "session_unknown_safe.json")
    signal = session.signals[0]
    assert "LT_" in (signal.source_signal_name.value or "")
    assert session.protocol_context.side.value is None
    assert signal.canonical_channel_ref is not None
    assert signal.canonical_channel_ref.channel_id is None


def test_21_domain_context_is_descriptive_not_ood_score() -> None:
    schema_text = (SCHEMA_DIR / "domain-context.schema.json").read_text(encoding="utf-8")
    assert '"ood_score"' not in schema_text
    assert '"prediction"' not in schema_text


def test_22_process_correlation_is_not_event_store_payload() -> None:
    schema = read_json(SCHEMA_DIR / "process-correlation.schema.json")
    props = schema["properties"]
    assert "event_type" not in props
    assert props["raw_payload_included"]["const"] is False


def test_23_unknown_domain_axes_are_explicit() -> None:
    session = model_from(GOLDEN / "session_unknown_safe.json")
    assert session.domain_context.electrode_layout_id.evidence_status is M.EvidenceStatus.UNKNOWN
    assert session.domain_context.channel_layout_id.value is None


def test_24_unknown_protocol_metadata_is_explicit() -> None:
    session = model_from(GOLDEN / "session_unknown_safe.json")
    assert session.protocol_context.protocol_id.value is None
    assert M.CanonicalizationReason.MISSING_PROTOCOL_METADATA in session.canonicalization_reasons


def test_25_session_schema_rejects_unknown_fields() -> None:
    data = read_json(GOLDEN / "session_unknown_safe.json")
    data["patient_name"] = "forbidden"
    with pytest.raises(ValidationError):
        M.CanonicalSession.model_validate(data)


def test_26_all_contracts_pin_schema_version() -> None:
    assert M.SCHEMA_VERSION == "1.0.0"
    for name in (
        "session.schema.json",
        "signal.schema.json",
        "protocol-context.schema.json",
        "domain-context.schema.json",
        "process-correlation.schema.json",
    ):
        text = (SCHEMA_DIR / name).read_text(encoding="utf-8")
        assert '"1.0.0"' in text


def test_27_day12_module_does_not_implement_vendor_parser() -> None:
    public = set(M.__all__)
    assert not any(name.lower().startswith("parse") for name in public)
    source = MODULE_PATH.read_text(encoding="utf-8")
    assert "pandas" not in source
    assert "csv.reader" not in source


def test_28_day12_has_no_training_or_model_inference_code() -> None:
    source = MODULE_PATH.read_text(encoding="utf-8").lower()
    for token in ("torch", "tensorflow", "sklearn", ".fit(", ".predict(", "ood_score"):
        assert token not in source


def test_29_pydantic_models_are_frozen() -> None:
    obj = M.EvidenceString(
        value="x",
        evidence_status=M.EvidenceStatus.SOURCE_REPORTED,
        evidence_refs=("source:x",),
    )
    with pytest.raises(ValidationError):
        obj.value = "y"


def test_30_invalid_unknown_side_with_value_is_rejected() -> None:
    bad = read_json(CORRUPTED / "invalid_unknown_side_with_value.json")
    with pytest.raises((ValidationError, M.ContractError)):
        M.CanonicalSession.model_validate(bad)


def test_31_invalid_verified_without_evidence_is_rejected() -> None:
    bad = read_json(CORRUPTED / "invalid_verified_without_evidence.json")
    with pytest.raises((ValidationError, M.ContractError)):
        M.CanonicalSession.model_validate(bad)


def test_32_all_corrupted_fixtures_fail_runtime_validation() -> None:
    paths = sorted(CORRUPTED.glob("*.json"))
    assert len(paths) >= 8
    for path in paths:
        with pytest.raises((ValidationError, M.ContractError)):
            M.CanonicalSession.model_validate(read_json(path))


def test_33_json_roundtrip_is_deterministic_for_same_canonical_object() -> None:
    session = model_from(GOLDEN / "session_unknown_safe.json")
    a = session.model_dump_json(indent=2)
    b = M.CanonicalSession.model_validate_json(a).model_dump_json(indent=2)
    assert a == b


def test_34_process_case_and_correlation_ids_are_distinct_concepts() -> None:
    session = model_from(GOLDEN / "session_unknown_safe.json")
    corr = session.process_correlation
    assert corr.case_id.startswith("case_")
    assert corr.correlation_id.startswith("corr_")
    assert corr.case_id != corr.correlation_id


def test_35_traceability_contains_all_roadmap_requirements() -> None:
    text = TRACE.read_text(encoding="utf-8")
    for req in ("FR-020", "FR-021", "FR-022", "FR-023", "FR-024", "NFR-002", "NFR-011"):
        assert req in text


def test_36_readme_preserves_safety_boundaries() -> None:
    text = README.read_text(encoding="utf-8")
    assert "không OOD score" in text
    assert "không production parser" in text
    assert "không suy đoán muscle/side/protocol" in text


def test_37_schema_and_runtime_both_reject_raw_payload_correlation() -> None:
    bad = read_json(CORRUPTED / "invalid_process_raw_payload.json")
    with pytest.raises(jsonschema.ValidationError):
        validate_json_schema(bad)
    with pytest.raises(ValidationError):
        M.CanonicalSession.model_validate(bad)


def test_38_signal_source_name_can_preserve_vendor_punctuation() -> None:
    session = model_from(GOLDEN / "session_unknown_safe.json")
    assert session.signals[0].source_signal_name.value == "Ultium_EMG-LT_BICEPS_FEM."
