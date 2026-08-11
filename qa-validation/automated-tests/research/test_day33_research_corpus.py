from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

import jsonschema
import numpy as np
import pytest
import yaml


ROOT = Path(__file__).resolve().parents[3]
CATALOG = ROOT / "data-platform/datasets/public-sEMG-catalog.v0.1.yaml"
MANIFEST = ROOT / "qa-validation/evidence/research-benchmark-corpus-v0.1.manifest.yaml"
CORPUS_ROOT = ROOT / "qa-validation/test-data/research/day33/corpus"
SCHEMA = ROOT / "packages/common-schemas/json/research-benchmark-corpus.v0.1.schema.json"
READINESS = ROOT / "qa-validation/evidence/day33-data-readiness.reference.yaml"
VERIFICATION = ROOT / "qa-validation/evidence/day33-public-source-verification.v0.1.yaml"
BUILDER = ROOT / "scripts/data/build_research_benchmark_corpus.py"
SEMANTICS = ROOT / "qa-validation/lib/day33_corpus_semantics.py"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def catalog():
    return yaml.safe_load(CATALOG.read_text())


@pytest.fixture(scope="module")
def manifest():
    return yaml.safe_load(MANIFEST.read_text())


@pytest.fixture(scope="module")
def schema():
    return json.loads(SCHEMA.read_text())


@pytest.fixture(scope="module")
def sem():
    return load_module("day33_semantics_test", SEMANTICS)


def test_01_mandatory_catalog_exists():
    assert CATALOG.exists()


def test_02_mandatory_manifest_exists():
    assert MANIFEST.exists()


def test_03_mandatory_readme_exists():
    assert (ROOT / "qa-validation/test-data/research/day33/README.md").exists()


def test_04_mandatory_builder_exists():
    assert BUILDER.exists()


def test_05_dataset_cards_exist():
    cards = list((ROOT / "docs/05-data/dataset-cards").glob("*.md"))
    assert len(cards) >= 4


def test_06_manifest_schema_valid(manifest, schema):
    jsonschema.Draft202012Validator(schema).validate(manifest)


def test_07_catalog_semantics_valid(catalog, sem):
    sem.validate_catalog(catalog)


def test_08_manifest_semantics_valid(manifest, sem):
    sem.validate_manifest(manifest, CORPUS_ROOT)


def test_09_day33_readiness_upgraded():
    payload = yaml.safe_load(READINESS.read_text())
    assert payload["day33_data_readiness"] == "RESEARCH_READY"


def test_10_readiness_does_not_claim_public_payload_acquired():
    payload = yaml.safe_load(READINESS.read_text())
    assert payload["public_payload_acquired"] is False


def test_11_public_source_count_at_least_one(catalog):
    active = [x for x in catalog["datasets"] if x["corpus_eligible"]]
    assert len(active) >= 1


@pytest.mark.parametrize(
    "dataset_id,license_name",
    [
        ("GRABMYO_V1_1_0", "CC BY 4.0"),
        ("HYSER_V2_0_0", "Open Data Commons Attribution License v1.0"),
        ("MENDELEY_4CH_HAND_GESTURE_V2", "CC BY 4.0"),
        ("CERQUEIRA_FATIGUE_V2", "CC BY 4.0"),
    ],
)
def test_12_15_selected_licenses_verified(catalog, dataset_id, license_name):
    item = next(x for x in catalog["datasets"] if x["dataset_id"] == dataset_id)
    assert item["license"] == license_name
    assert item["license_status"] == "VERIFIED"


@pytest.mark.parametrize("dataset", [0, 1, 2, 3])
def test_16_19_public_raw_never_in_repo(catalog, dataset):
    assert catalog["datasets"][dataset]["raw_payload_in_repo"] is False


def test_20_ninapro_deferred_for_license():
    catalog = yaml.safe_load(CATALOG.read_text())
    deferred = {x["dataset_id"]: x for x in catalog["excluded_or_deferred"]}
    assert deferred["NINAPRO_FAMILY"]["default_corpus_eligible"] is False


def test_21_putemg_not_default_due_noncommercial():
    catalog = yaml.safe_load(CATALOG.read_text())
    deferred = {x["dataset_id"]: x for x in catalog["excluded_or_deferred"]}
    assert deferred["PUTEMG"]["default_corpus_eligible"] is False


def test_22_physiomio_restricted_not_default():
    catalog = yaml.safe_load(CATALOG.read_text())
    deferred = {x["dataset_id"]: x for x in catalog["excluded_or_deferred"]}
    assert deferred["PHYSIOMIO"]["default_corpus_eligible"] is False


def test_23_all_items_exact_day32_tier(manifest):
    assert {x["evidence_tier"] for x in manifest["items"]} == {
        "SYNTHETIC_KNOWN_TRUTH"
    }


def test_24_all_items_window_with_context(manifest):
    assert all(
        x["window_context"]["annotation_unit_type"] == "QC_WINDOW_WITH_CONTEXT"
        for x in manifest["items"]
    )


def test_25_all_window_ids_canonical(manifest):
    assert all(
        x["window_context"]["window_id"].startswith("qcw_sha256_")
        for x in manifest["items"]
    )


def test_26_no_direct_identifiers(manifest):
    assert all(
        x["source_context"]["direct_identifiers_present"] is False
        for x in manifest["items"]
    )


def test_27_no_clinical_evidence(manifest):
    assert all(
        x["source_context"]["clinical_evidence"] is False
        for x in manifest["items"]
    )


def test_28_claim_scope_research_only(manifest):
    assert manifest["claim_scope"] == "RESEARCH_ONLY"
    assert all(x["claim_scope"] == "RESEARCH_ONLY" for x in manifest["items"])


def test_29_development_truth_visible(manifest):
    dev = [x for x in manifest["items"] if x["partition"] == "benchmark-development"]
    assert dev and all(x["synthetic_truth"] is not None for x in dev)


def test_30_locked_truth_hidden(manifest):
    locked = [x for x in manifest["items"] if x["partition"] == "benchmark-locked"]
    assert locked and all(x["synthetic_truth"] is None for x in locked)


def test_31_locked_commitment_complete(manifest):
    locked = {x["item_id"] for x in manifest["items"] if x["partition"] == "benchmark-locked"}
    committed = {x["item_id"] for x in manifest["locked_truth_commitments"]}
    assert locked == committed


def test_32_partition_seeds_disjoint(manifest):
    dev = {
        x["provenance"]["seed"]
        for x in manifest["items"]
        if x["partition"] == "benchmark-development"
    }
    locked = {
        x["provenance"]["seed"]
        for x in manifest["items"]
        if x["partition"] == "benchmark-locked"
    }
    assert not dev & locked


def test_33_low_amplitude_not_called_pathology(manifest):
    dev = [x for x in manifest["items"] if x["synthetic_truth"]]
    item = next(
        x for x in dev
        if x["synthetic_truth"]["scenario"] == "SYNTHETIC_LOW_AMPLITUDE_STRESS"
    )
    text = json.dumps(item).lower()
    for forbidden in ("stroke", "paresis", "paralysis", "atrophy"):
        assert forbidden not in text


@pytest.mark.parametrize(
    "scenario",
    [
        "MISSING",
        "CLIPPING",
        "POWERLINE_50HZ",
        "MOTION_DRIFT",
        "TIMESTAMP_DUPLICATE",
        "SYNTHETIC_LOW_AMPLITUDE_STRESS",
    ],
)
def test_34_39_required_challenge_scenarios_present(manifest, scenario):
    visible = {
        x["synthetic_truth"]["scenario"]
        for x in manifest["items"]
        if x["synthetic_truth"] is not None
    }
    assert scenario in visible


def test_40_signal_hashes_match(manifest):
    for item in manifest["items"]:
        path = CORPUS_ROOT / item["signal_artifact"]["relative_path"]
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        assert digest == item["signal_artifact"]["sha256"]


def test_41_no_public_raw_file_under_day33_corpus():
    paths = [p.name.lower() for p in CORPUS_ROOT.rglob("*") if p.is_file()]
    assert not any("grabmyo" in name or "hyser" in name for name in paths)


def test_42_npz_contains_samples_and_time(manifest):
    item = manifest["items"][0]
    path = CORPUS_ROOT / item["signal_artifact"]["relative_path"]
    with np.load(path) as payload:
        assert set(payload.files) == {"samples", "time_seconds"}


def test_43_builder_has_no_network_download():
    text = BUILDER.read_text().lower()
    for token in ("requests.get", "urllib.request", "wget ", "curl ", "subprocess.run"):
        assert token not in text


def test_44_builder_does_not_train_model():
    text = BUILDER.read_text().lower()
    for token in (".fit(", "optimizer", "backward(", "train_model"):
        assert token not in text


def test_45_source_verification_has_four_sources():
    payload = yaml.safe_load(VERIFICATION.read_text())
    assert len(payload["sources"]) == 4


def test_46_source_verification_claim_boundary():
    payload = yaml.safe_load(VERIFICATION.read_text())
    assert payload["claim_boundary"]["clinical_validation"] is False
    assert payload["claim_boundary"]["site_representativeness"] is False


def test_47_cards_do_not_claim_clinical_validation():
    text = "\n".join(
        p.read_text().lower()
        for p in (ROOT / "docs/05-data/dataset-cards").glob("*.md")
    )
    assert "clinically validated" not in text


def test_48_manifest_has_no_home_directory_leak(manifest):
    text = yaml.safe_dump(manifest).lower()
    assert "/home/" not in text
    assert "duyvd" not in text


def test_49_reference_manifest_has_no_raw_patient_data(manifest):
    assert all(x["signal_artifact"]["raw_patient_data"] is False for x in manifest["items"])


def test_50_rebuild_is_deterministic(tmp_path):
    out1 = tmp_path / "a"
    out2 = tmp_path / "b"
    env = dict(**os_environ_with_pythonpath())
    for target in (out1, out2):
        subprocess.run(
            [
                sys.executable,
                str(BUILDER),
                "--catalog",
                str(CATALOG),
                "--output-root",
                str(target),
            ],
            check=True,
            env=env,
            capture_output=True,
            text=True,
        )
    one = (out1 / "research-benchmark-corpus-v0.1.manifest.yaml").read_text()
    two = (out2 / "research-benchmark-corpus-v0.1.manifest.yaml").read_text()
    assert one == two
    files1 = sorted(
        (p.relative_to(out1), hashlib.sha256(p.read_bytes()).hexdigest())
        for p in out1.rglob("*.npz")
    )
    files2 = sorted(
        (p.relative_to(out2), hashlib.sha256(p.read_bytes()).hexdigest())
        for p in out2.rglob("*.npz")
    )
    assert files1 == files2


def os_environ_with_pythonpath():
    import os
    env = os.environ.copy()
    semg = str(ROOT / "packages/semg-core")
    env["PYTHONPATH"] = semg + os.pathsep + env.get("PYTHONPATH", "")
    return env


@pytest.mark.parametrize("index", range(4))
def test_51_54_dataset_card_metadata_complete(catalog, index):
    dataset = catalog["datasets"][index]
    for key in (
        "dataset_id",
        "version",
        "doi",
        "license",
        "license_status",
        "access_status",
        "channel_summary",
        "task_summary",
    ):
        assert dataset.get(key) not in (None, "") or key == "sampling_rate_hz"


def test_55_cerqueira_sampling_rate_1259(catalog):
    item = next(x for x in catalog["datasets"] if x["dataset_id"] == "CERQUEIRA_FATIGUE_V2")
    assert item["sampling_rate_hz"] == 1259


def test_56_grabmyo_multiday_metadata(catalog):
    item = next(x for x in catalog["datasets"] if x["dataset_id"] == "GRABMYO_V1_1_0")
    assert item["subjects"] == 43
    assert item["sessions_per_subject"] == 3
    assert item["sampling_rate_hz"] == 2048


def test_57_hyser_cross_day_metadata(catalog):
    item = next(x for x in catalog["datasets"] if x["dataset_id"] == "HYSER_V2_0_0")
    assert item["subjects"] == 20
    assert item["sessions_per_subject"] == 2
    assert item["sampling_rate_hz"] == 2048


def test_58_mendeley_sampling_rate_not_guessed(catalog):
    item = next(
        x
        for x in catalog["datasets"]
        if x["dataset_id"] == "MENDELEY_4CH_HAND_GESTURE_V2"
    )
    assert item["sampling_rate_hz"] is None


def test_59_no_excluded_dataset_is_active(catalog):
    active = {x["dataset_id"] for x in catalog["datasets"] if x["corpus_eligible"]}
    excluded = {x["dataset_id"] for x in catalog["excluded_or_deferred"]}
    assert not active & excluded


def test_60_public_sources_are_not_corpus_items(manifest):
    assert all(
        x["source_context"]["source_class"] == "SYNTHETIC_FIXTURE"
        for x in manifest["items"]
    )


def test_61_no_weak_label_or_expert_promotion(manifest):
    assert all(x["evidence_tier"] == "SYNTHETIC_KNOWN_TRUTH" for x in manifest["items"])


def test_62_locked_item_names_do_not_encode_truth(manifest):
    for item in manifest["items"]:
        if item["partition"] == "benchmark-locked":
            lowered = item["signal_artifact"]["relative_path"].lower()
            for token in ("missing", "clip", "powerline", "motion", "low_amplitude"):
                assert token not in lowered


def test_63_all_public_sources_license_verified_in_manifest(manifest):
    assert all(x["license_status"] == "VERIFIED" for x in manifest["public_sources"])


def test_64_all_public_sources_raw_payload_false(manifest):
    assert all(x["raw_payload_in_repo"] is False for x in manifest["public_sources"])
