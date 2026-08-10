from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest
import yaml
from pydantic import ValidationError


ROOT = Path(__file__).resolve().parents[3]
MODULE = ROOT / "services/signal-ingestion-service/src/normalization/channel_mapper.py"
ONTOLOGY = ROOT / "clinical/ontologies/muscle-channel-ontology.v0.1.yaml"
POLICY = ROOT / "configs/validation/metadata-policy.v0.1.yaml"
LAYOUT = ROOT / "data-platform/contracts/channel-layout-context.v0.1.yaml"
RETENTION = ROOT / "data-platform/storage/unlabeled-corpus-retention-policy.v0.1.md"


def load_module():
    spec = importlib.util.spec_from_file_location("day14_channel_mapper", MODULE)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def mod():
    return load_module()


@pytest.fixture(scope="module")
def ontology(mod):
    return mod.load_ontology(ONTOLOGY)


@pytest.fixture(scope="module")
def policy(mod):
    return mod.load_metadata_policy(POLICY)


def test_01_core_artifacts_exist():
    for path in (MODULE, ONTOLOGY, POLICY, LAYOUT, RETENTION):
        assert path.is_file()


def test_02_ontology_is_versioned(ontology):
    assert ontology["version"] == "0.1.0"
    assert ontology["mapping_version"] == "motionlab-vendor-map.v0.1"


def test_03_fuzzy_matching_is_disabled(ontology):
    assert ontology["principles"]["fuzzy_matching_allowed"] is False


def test_04_unknown_must_abstain(ontology):
    assert ontology["principles"]["unknown_must_abstain"] is True


def test_05_site_coverage_not_claimed_complete(ontology):
    assert ontology["principles"]["site_mapping_coverage_complete"] is False


def test_06_known_alias_maps_exactly(mod, ontology):
    result = mod.map_vendor_signal("Ultium_EMG-LT_BICEPS_FEM.", ontology)
    assert result.mapping_status.value == "MAPPED"
    assert result.canonical_muscle_id == "BICEPS_FEMORIS"
    assert result.side == "LEFT"


def test_07_vendor_text_is_preserved(mod, ontology):
    source = "Ultium_EMG-LT_BICEPS_FEM."
    result = mod.map_vendor_signal(source, ontology)
    assert result.vendor_signal_name_raw == source


def test_08_case_variant_does_not_fuzzy_map(mod, ontology):
    result = mod.map_vendor_signal("ultium_emg-lt_biceps_fem.", ontology)
    assert result.mapping_status.value == "UNMAPPED"


def test_09_whitespace_variant_does_not_silent_normalize(mod, ontology):
    result = mod.map_vendor_signal(" Ultium_EMG-LT_BICEPS_FEM. ", ontology)
    assert result.mapping_status.value == "UNMAPPED"


def test_10_unknown_alias_preserves_unknown_side(mod, ontology):
    result = mod.map_vendor_signal("UNKNOWN", ontology)
    assert result.side == "UNKNOWN"
    assert result.canonical_muscle_id is None


def test_11_unknown_alias_has_typed_reason(mod, ontology):
    result = mod.map_vendor_signal("UNKNOWN", ontology)
    assert result.reason_code == "VENDOR_ALIAS_NOT_IN_APPROVED_MAPPING"


def test_12_mapping_id_is_deterministic(mod, ontology):
    first = mod.map_vendor_signal("Ultium_EMG-LT_BICEPS_FEM.", ontology)
    second = mod.map_vendor_signal("Ultium_EMG-LT_BICEPS_FEM.", ontology)
    assert first.mapping_result_id == second.mapping_result_id


def test_13_mapping_result_is_frozen(mod, ontology):
    result = mod.map_vendor_signal("UNKNOWN", ontology)
    with pytest.raises(ValidationError):
        result.side = "LEFT"


def test_14_duplicate_alias_rejected(mod, tmp_path):
    payload = yaml.safe_load(ONTOLOGY.read_text(encoding="utf-8"))
    payload["vendor_mappings"].append(dict(payload["vendor_mappings"][0]))
    path = tmp_path / "ontology.yaml"
    path.write_text(yaml.safe_dump(payload), encoding="utf-8")
    with pytest.raises(ValueError, match="Duplicate vendor alias"):
        mod.load_ontology(path)


def test_15_non_exact_mapping_mode_rejected(mod, tmp_path):
    payload = yaml.safe_load(ONTOLOGY.read_text(encoding="utf-8"))
    payload["vendor_mappings"][0]["match_mode"] = "REGEX"
    path = tmp_path / "ontology.yaml"
    path.write_text(yaml.safe_dump(payload), encoding="utf-8")
    with pytest.raises(ValueError, match="only allows EXACT"):
        mod.load_ontology(path)


def test_16_unknown_canonical_reference_rejected(mod, tmp_path):
    payload = yaml.safe_load(ONTOLOGY.read_text(encoding="utf-8"))
    payload["vendor_mappings"][0]["canonical_muscle_id"] = "FABRICATED"
    path = tmp_path / "ontology.yaml"
    path.write_text(yaml.safe_dump(payload), encoding="utf-8")
    with pytest.raises(ValueError, match="unknown canonical muscle"):
        mod.load_ontology(path)


def test_17_metadata_policy_has_three_profiles(policy):
    assert set(policy["profiles"]) == {
        "INGESTION_BASE",
        "SEMG_QC_CONTEXT",
        "PROTOCOL_METRIC_CONTEXT",
    }


def test_18_ingestion_base_missing_required_fails(mod, policy):
    result = mod.evaluate_metadata({}, "INGESTION_BASE", policy)
    assert result.status.value == "FAIL"


def test_19_ingestion_base_complete_passes(mod, policy):
    metadata = {
        "source_record_id": "src",
        "vendor_signal_name": "signal",
        "sampling_rate_hz": 2000,
        "unit": "uV",
    }
    result = mod.evaluate_metadata(metadata, "INGESTION_BASE", policy)
    assert result.status.value == "PASS"


def test_20_qc_context_missing_anatomy_warns_not_autofills(mod, policy):
    metadata = {"source_record_id": "src", "vendor_signal_name": "signal"}
    result = mod.evaluate_metadata(metadata, "SEMG_QC_CONTEXT", policy)
    assert result.status.value == "WARNING"
    assert "canonical_muscle_id" not in metadata


def test_21_protocol_metric_context_missing_muscle_fails(mod, policy):
    metadata = {
        "source_record_id": "src",
        "side": "LEFT",
        "protocol_id": "p",
        "task": "t",
    }
    result = mod.evaluate_metadata(metadata, "PROTOCOL_METRIC_CONTEXT", policy)
    assert result.status.value == "FAIL"


def test_22_unknown_profile_rejected(mod, policy):
    with pytest.raises(ValueError, match="Unknown metadata profile"):
        mod.evaluate_metadata({}, "UNKNOWN_PROFILE", policy)


def test_23_policy_disallows_autofill(policy):
    assert policy["safety"]["autofill_missing_metadata"] is False


def test_24_policy_does_not_treat_pathology_as_failure(policy):
    assert policy["safety"]["treat_pathology_as_metadata_failure"] is False


def test_25_layout_contract_is_metadata_only():
    payload = yaml.safe_load(LAYOUT.read_text(encoding="utf-8"))
    assert payload["status"] == "OOD_METADATA_CONTRACT_READINESS_ONLY"


def test_26_layout_contract_forbids_ood_score():
    payload = yaml.safe_load(LAYOUT.read_text(encoding="utf-8"))
    assert "ood_score" in payload["forbidden_at_day14"]


def test_27_layout_contract_has_shift_axes():
    payload = yaml.safe_load(LAYOUT.read_text(encoding="utf-8"))
    assert "layout_id" in payload["future_shift_axes"]
    assert "mapping_version" in payload["future_shift_axes"]


def test_28_default_layout_geometry_not_verified():
    payload = yaml.safe_load(LAYOUT.read_text(encoding="utf-8"))
    assert payload["default_site_state"]["geometry_status"] == "NOT_VERIFIED"


def test_29_build_unknown_layout_is_safe(mod):
    ctx = mod.build_layout_context(
        {
            "geometry_status": "NOT_VERIFIED",
            "placement_status": "NOT_VERIFIED",
            "evidence_refs": [],
        },
        "motionlab-vendor-map.v0.1",
    )
    assert ctx.layout_id is None
    assert ctx.readiness_level == "METADATA_CONTRACT_ONLY"


def test_30_verified_geometry_requires_evidence(mod):
    with pytest.raises(ValidationError):
        mod.build_layout_context(
            {
                "layout_id": "layout_001",
                "geometry_status": "VERIFIED",
                "placement_status": "NOT_VERIFIED",
                "evidence_refs": [],
            },
            "motionlab-vendor-map.v0.1",
        )


def test_31_layout_model_rejects_ood_score_extra_field(mod):
    with pytest.raises(ValidationError):
        mod.ChannelLayoutContext(
            mapping_version="motionlab-vendor-map.v0.1",
            geometry_status="UNKNOWN",
            placement_status="UNKNOWN",
            ood_score=0.9,
        )


def test_32_layout_context_is_frozen(mod):
    ctx = mod.ChannelLayoutContext(mapping_version="m1")
    with pytest.raises(ValidationError):
        ctx.layout_id = "later"


def test_33_retention_policy_is_backfilled():
    text = RETENTION.read_text(encoding="utf-8")
    assert "Unlabeled Corpus Retention Policy v0.1" in text


def test_34_retention_policy_does_not_authorize_ssl_training():
    text = RETENTION.read_text(encoding="utf-8").lower()
    assert "không" in text and "train" in text
    assert "data-readiness only" in text


def test_35_retention_policy_unknown_is_not_eligible():
    text = RETENTION.read_text(encoding="utf-8")
    assert "UNKNOWN" in text
    assert "NOT AUTHORIZED FOR RESEARCH REUSE" in text


def test_36_day14_module_has_no_training_dependency():
    text = MODULE.read_text(encoding="utf-8").lower()
    for token in ("torch", "tensorflow", "sklearn", ".fit("):
        assert token not in text


def test_37_day14_module_has_no_csv_parser_implementation():
    text = MODULE.read_text(encoding="utf-8").lower()
    assert "csv.reader" not in text
    assert "pandas.read_csv" not in text


def test_38_ontology_does_not_claim_site_verified():
    text = ONTOLOGY.read_text(encoding="utf-8")
    assert "SITE_COVERAGE_NOT_VERIFIED" in text


def test_39_ood_is_not_pathology_semantics():
    text = LAYOUT.read_text(encoding="utf-8").lower()
    assert "not a pathology" in text


def test_40_no_fuzzy_term_in_runtime_algorithm(mod, ontology):
    assert ontology["principles"]["match_policy"] == "EXACT_APPROVED_ALIAS_ONLY"
    result = mod.map_vendor_signal("BICEPS", ontology)
    assert result.mapping_status.value == "UNMAPPED"


def test_41_mapping_evidence_is_not_upgraded_to_verified(mod, ontology):
    result = mod.map_vendor_signal("Ultium_EMG-LT_BICEPS_FEM.", ontology)
    assert result.evidence_status.value == "DOCUMENTED"


def test_42_layout_id_is_never_synthesized(mod):
    ctx = mod.build_layout_context(
        {"geometry_status": "UNKNOWN", "placement_status": "UNKNOWN"},
        "m1",
    )
    assert ctx.layout_id is None


def test_43_metadata_evaluation_is_deterministic(mod, policy):
    metadata = {"source_record_id": "src", "vendor_signal_name": "signal"}
    first = mod.evaluate_metadata(metadata, "SEMG_QC_CONTEXT", policy)
    second = mod.evaluate_metadata(metadata, "SEMG_QC_CONTEXT", policy)
    assert first == second


def test_44_corrupted_fixture_with_ood_score_is_invalid_for_runtime(mod):
    path = ROOT / "qa-validation/test-data/corrupted/day14/layout-with-ood-score.yaml"
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    with pytest.raises(ValidationError):
        mod.ChannelLayoutContext(**payload)


def test_45_golden_known_alias_fixture_matches_runtime(mod, ontology):
    path = ROOT / "qa-validation/test-data/golden/day14/known-exact-alias.yaml"
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    result = mod.map_vendor_signal(payload["vendor_signal_name"], ontology)
    assert result.mapping_status.value == payload["expected"]["mapping_status"]


def test_46_golden_metadata_warning_fixture_matches_runtime(mod, policy):
    path = ROOT / "qa-validation/test-data/golden/day14/metadata-qc-warning.yaml"
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    result = mod.evaluate_metadata(payload["metadata"], payload["profile_id"], policy)
    assert result.status.value == payload["expected_status"]
