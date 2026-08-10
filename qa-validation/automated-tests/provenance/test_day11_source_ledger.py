from __future__ import annotations

import importlib.util
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import jsonschema
import pytest


ROOT = Path(__file__).resolve().parents[3]
MODULE_PATH = (
    ROOT
    / "services/signal-ingestion-service/src/provenance/source_ledger.py"
)
SCHEMA_PATH = ROOT / "packages/common-schemas/json/source-record.schema.json"
POLICY_PATH = ROOT / "data-platform/storage/raw-immutability-policy.md"
RETENTION_PATH = (
    ROOT / "data-platform/storage/unlabeled-corpus-retention-policy.v0.1.md"
)
TRACE_PATH = ROOT / "qa-validation/traceability/day11-requirement-traceability.csv"
GOLDEN = (
    ROOT
    / "qa-validation/test-data/golden/provenance/day11/synthetic-mr4-source.csv"
)
DUPLICATE_COPY = (
    ROOT
    / "qa-validation/test-data/golden/provenance/day11/"
    "synthetic-mr4-source-duplicate-name-copy.csv"
)
MUTATED = (
    ROOT
    / "qa-validation/test-data/corrupted/provenance/day11/mutated-same-name.csv"
)


def _load_module():
    spec = importlib.util.spec_from_file_location("day11_source_ledger", MODULE_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ledger_mod = _load_module()


def _metadata(original_filename: str = "synthetic-mr4-source.csv"):
    return ledger_mod.SourceMetadata(
        original_filename=original_filename,
        device_vendor="Noraxon",
        device_family="Ultium EMG",
        device_model=None,
        software_name="Noraxon MR",
        software_version="4.0.22",
        export_family="MR4_SINGLE_CSV",
    )


def _governance(research_reuse_eligible=None):
    return ledger_mod.GovernanceMetadata(
        deidentification_status="NOT_APPLICABLE_SYNTHETIC",
        governance_status="APPROVED_FOR_DEFINED_PURPOSE",
        research_reuse_eligible=research_reuse_eligible,
        retention_class="SYNTHETIC_QA",
    )


def _register(tmp_path: Path, source: Path = GOLDEN):
    ledger = ledger_mod.JsonlSourceLedger(tmp_path / "source-ledger.jsonl")
    result = ledger.register_source(
        source,
        storage_reference="qa://day11/synthetic",
        metadata=_metadata(source.name),
        governance=_governance(False),
        evidence_status="VERIFIED",
        ingestion_timestamp=datetime(2026, 8, 10, 4, 0, tzinfo=timezone.utc),
    )
    return ledger, result


def test_01_required_artifacts_exist() -> None:
    required = [MODULE_PATH, SCHEMA_PATH, POLICY_PATH, RETENTION_PATH, TRACE_PATH]
    assert all(path.is_file() for path in required)


def test_02_schema_is_valid_draft_2020_12() -> None:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator.check_schema(schema)


def test_03_sha256_matches_known_fixture() -> None:
    digest = ledger_mod.sha256_file(GOLDEN)
    assert digest == "19b5800653c648307701cb134eb661900b66caea25530d70dea7ee5894c3f3f4"


def test_04_source_id_is_content_addressed() -> None:
    digest = ledger_mod.sha256_file(GOLDEN)
    assert ledger_mod.source_id_from_digest(digest) == f"src_sha256_{digest}"


def test_05_invalid_digest_is_rejected() -> None:
    with pytest.raises(ValueError):
        ledger_mod.source_id_from_digest("abc")


def test_06_registration_does_not_modify_raw_bytes(tmp_path: Path) -> None:
    source = tmp_path / "raw.csv"
    source.write_bytes(GOLDEN.read_bytes())
    before = source.read_bytes()
    _register(tmp_path, source)
    assert source.read_bytes() == before


def test_07_first_registration_appends_one_record(tmp_path: Path) -> None:
    ledger, result = _register(tmp_path)
    assert result.status == ledger_mod.RegistrationStatus.REGISTERED
    assert result.appended is True
    assert len(ledger.ledger_path.read_text(encoding="utf-8").splitlines()) == 1


def test_08_registered_record_matches_json_schema(tmp_path: Path) -> None:
    _, result = _register(tmp_path)
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator(schema).validate(
        result.source_record.model_dump()
    )


def test_09_duplicate_bytes_are_detected(tmp_path: Path) -> None:
    ledger, first = _register(tmp_path)
    duplicate = ledger.register_source(
        DUPLICATE_COPY,
        storage_reference="qa://day11/duplicate-copy",
        metadata=_metadata(DUPLICATE_COPY.name),
        governance=_governance(False),
        evidence_status="VERIFIED",
        ingestion_timestamp=datetime(2026, 8, 10, 5, 0, tzinfo=timezone.utc),
    )
    assert duplicate.status == ledger_mod.RegistrationStatus.DUPLICATE
    assert duplicate.appended is False
    assert duplicate.source_record == first.source_record


def test_10_duplicate_does_not_append_second_line(tmp_path: Path) -> None:
    ledger, _ = _register(tmp_path)
    ledger.register_source(
        DUPLICATE_COPY,
        storage_reference="qa://day11/duplicate-copy",
        metadata=_metadata(DUPLICATE_COPY.name),
        governance=_governance(False),
        evidence_status="VERIFIED",
    )
    assert len(ledger.ledger_path.read_text(encoding="utf-8").splitlines()) == 1


def test_11_duplicate_does_not_overwrite_first_seen_filename(tmp_path: Path) -> None:
    ledger, first = _register(tmp_path)
    duplicate = ledger.register_source(
        DUPLICATE_COPY,
        storage_reference="qa://day11/duplicate-copy",
        metadata=_metadata("renamed-source.csv"),
        governance=_governance(False),
        evidence_status="VERIFIED",
    )
    assert duplicate.source_record.original_filename == first.source_record.original_filename
    assert duplicate.source_record.original_filename != "renamed-source.csv"


def test_12_same_filename_different_bytes_get_new_identity(tmp_path: Path) -> None:
    ledger, first = _register(tmp_path)
    second = ledger.register_source(
        MUTATED,
        storage_reference="qa://day11/mutated",
        metadata=_metadata(first.source_record.original_filename),
        governance=_governance(False),
        evidence_status="VERIFIED",
    )
    assert second.status == ledger_mod.RegistrationStatus.REGISTERED
    assert second.source_record.source_id != first.source_record.source_id


def test_13_verify_source_passes_for_unchanged_bytes(tmp_path: Path) -> None:
    source = tmp_path / "raw.csv"
    source.write_bytes(GOLDEN.read_bytes())
    ledger, result = _register(tmp_path, source)
    ledger.verify_source(source, result.source_record)


def test_14_verify_source_detects_byte_mutation(tmp_path: Path) -> None:
    source = tmp_path / "raw.csv"
    source.write_bytes(GOLDEN.read_bytes())
    ledger, result = _register(tmp_path, source)
    source.write_bytes(source.read_bytes() + b"MUTATION")
    with pytest.raises(ledger_mod.SourceIntegrityError):
        ledger.verify_source(source, result.source_record)


def test_15_missing_source_is_typed_failure(tmp_path: Path) -> None:
    with pytest.raises(ledger_mod.InvalidSourcePathError):
        ledger_mod.sha256_file(tmp_path / "missing.csv")


def test_16_directory_source_is_typed_failure(tmp_path: Path) -> None:
    with pytest.raises(ledger_mod.InvalidSourcePathError):
        ledger_mod.sha256_file(tmp_path)


def test_17_naive_ingestion_timestamp_is_rejected(tmp_path: Path) -> None:
    ledger = ledger_mod.JsonlSourceLedger(tmp_path / "ledger.jsonl")
    with pytest.raises(ValueError):
        ledger.register_source(
            GOLDEN,
            storage_reference="qa://day11/synthetic",
            metadata=_metadata(),
            governance=_governance(False),
            evidence_status="VERIFIED",
            ingestion_timestamp=datetime(2026, 8, 10, 4, 0),
        )


def test_18_malformed_ledger_fails_closed(tmp_path: Path) -> None:
    ledger_path = tmp_path / "ledger.jsonl"
    ledger_path.write_text('{"this":"is not a SourceRecord"}\n', encoding="utf-8")
    ledger = ledger_mod.JsonlSourceLedger(ledger_path)
    with pytest.raises(ledger_mod.LedgerCorruptionError):
        ledger.get_by_source_id("src_sha256_" + "0" * 64)


def test_19_blank_ledger_line_fails_closed(tmp_path: Path) -> None:
    ledger_path = tmp_path / "ledger.jsonl"
    ledger_path.write_text("\n", encoding="utf-8")
    ledger = ledger_mod.JsonlSourceLedger(ledger_path)
    with pytest.raises(ledger_mod.LedgerCorruptionError):
        ledger.get_by_source_id("x")


def test_20_get_by_source_id_round_trip(tmp_path: Path) -> None:
    ledger, result = _register(tmp_path)
    loaded = ledger.get_by_source_id(result.source_record.source_id)
    assert loaded == result.source_record


def test_21_default_unknown_research_permission_is_not_true() -> None:
    governance = _governance(None)
    assert governance.research_reuse_eligible is None
    assert governance.research_reuse_eligible is not True


def test_22_source_record_immutable_raw_is_true(tmp_path: Path) -> None:
    _, result = _register(tmp_path)
    assert result.source_record.immutable_raw is True


def test_23_original_filename_is_not_source_identity(tmp_path: Path) -> None:
    ledger, first = _register(tmp_path)
    duplicate = ledger.register_source(
        DUPLICATE_COPY,
        storage_reference="qa://day11/another",
        metadata=_metadata("completely-different-name.csv"),
        governance=_governance(False),
        evidence_status="VERIFIED",
    )
    assert duplicate.source_record.source_id == first.source_record.source_id


def test_24_policy_forbids_raw_filter_resample_overwrite() -> None:
    text = POLICY_PATH.read_text(encoding="utf-8").lower()
    for token in ["resample", "filter", "overwrite", "read-only", "fail closed"]:
        assert token in text


def test_25_retention_policy_denies_unknown_permission() -> None:
    text = RETENTION_PATH.read_text(encoding="utf-8")
    assert "null" in text
    assert "NOT AUTHORIZED FOR RESEARCH REUSE" in text
    assert "Không pretrain SSL" in text


def test_26_retention_policy_does_not_claim_ood_model() -> None:
    text = RETENTION_PATH.read_text(encoding="utf-8").lower()
    assert "data-readiness only" in text
    assert "does not authorize model training" in text


def test_27_traceability_contains_all_day11_requirements() -> None:
    text = TRACE_PATH.read_text(encoding="utf-8")
    for req in ["FR-007", "FR-008", "FR-053", "NFR-002", "NFR-003", "AC-09"]:
        assert req in text


def test_28_module_contains_no_parser_or_dsp_scope() -> None:
    text = MODULE_PATH.read_text(encoding="utf-8").lower()
    assert "does not parse mr4" in text
    assert "resample" in text
    assert "filter" in text
    assert ".fit(" not in text


def test_29_source_schema_keeps_domain_context_out_of_scope() -> None:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    props = schema["properties"]
    for future_field in ["protocol_version", "task", "load", "speed", "layout_id"]:
        assert future_field not in props


def test_30_hashing_uses_file_digest() -> None:
    text = MODULE_PATH.read_text(encoding="utf-8")
    assert "hashlib.file_digest" in text


def test_31_no_real_patient_artifact_extensions_in_day11_managed_fixture_dirs() -> None:
    fixture_root = ROOT / "qa-validation/test-data"
    forbidden = {".mat", ".c3d", ".npz", ".npy", ".joblib", ".pt", ".pth"}
    offenders = [
        path
        for path in fixture_root.rglob("*")
        if path.is_file() and path.suffix.lower() in forbidden
    ]
    assert offenders == []


def test_32_synthetic_fixture_is_explicitly_nonclinical() -> None:
    readme = (
        ROOT
        / "qa-validation/test-data/golden/provenance/day11/README.md"
    ).read_text(encoding="utf-8").lower()
    assert "synthetic" in readme
    assert "not clinical evidence" in readme
