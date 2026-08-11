from __future__ import annotations

import csv
import importlib.util
import json
import shutil
import sys
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[3]
MODULE_PATH = ROOT / "qa-validation/lib/day34_weak_label_analysis.py"
MANIFEST_PATH = ROOT / "qa-validation/evidence/research-benchmark-corpus-v0.1.manifest.yaml"
CORPUS_ROOT = ROOT / "qa-validation/test-data/research/day33/corpus"


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


D = _load("day34_analysis_under_test", MODULE_PATH)
MANIFEST = D.load_manifest(MANIFEST_PATH)
DEV_ITEMS = D.development_items(MANIFEST)
FAMILY_ROWS, INTEGRITY_ROWS = D.run_evaluation(
    MANIFEST_PATH,
    CORPUS_ROOT,
    repo_root=ROOT,
)
PERFORMANCE = D.performance_rows(FAMILY_ROWS)
CORRELATIONS = D.correlation_rows(FAMILY_ROWS)
CANDIDATES = D.review_candidate_rows(FAMILY_ROWS, INTEGRITY_ROWS)


def _row_for(family: str):
    return next(row for row in PERFORMANCE if row["family_id"] == family)


def _item_scenario(scenario: str):
    return next(item for item in DEV_ITEMS if item["synthetic_truth"]["scenario"] == scenario)


def _family_scenario(family: str, scenario: str):
    return next(
        row
        for row in FAMILY_ROWS
        if row.family_id == family and row.scenario == scenario
    )


def test_manifest_claim_scope_research_only():
    assert MANIFEST["claim_scope"] == "RESEARCH_ONLY"


def test_development_item_count_is_12():
    assert len(DEV_ITEMS) == 12


def test_locked_item_count_is_6():
    assert sum(item["partition"] == D.LOCKED_PARTITION for item in MANIFEST["items"]) == 6


def test_development_loader_excludes_locked_items():
    assert all(item["partition"] == D.DEVELOPMENT_PARTITION for item in DEV_ITEMS)


def test_locked_item_access_is_rejected():
    locked = next(item for item in MANIFEST["items"] if item["partition"] == D.LOCKED_PARTITION)
    with pytest.raises(D.Day34AnalysisError, match="LOCKED_PARTITION"):
        D.reject_locked_item(locked)


def test_family_output_count_is_72():
    assert len(FAMILY_ROWS) == 72


def test_integrity_output_count_is_12():
    assert len(INTEGRITY_ROWS) == 12


def test_exact_six_canonical_families():
    observed = tuple(sorted({row.family_id for row in FAMILY_ROWS}))
    expected = tuple(sorted(D.CANONICAL_FAMILIES))
    assert observed == expected


@pytest.mark.parametrize(
    "scenario",
    [item["synthetic_truth"]["scenario"] for item in DEV_ITEMS],
)
def test_each_development_item_has_six_family_outputs(scenario: str):
    rows = [row for row in FAMILY_ROWS if row.scenario == scenario]
    assert len(rows) == 6
    assert {row.family_id for row in rows} == set(D.CANONICAL_FAMILIES)


def test_no_locked_item_id_appears_in_family_outputs():
    locked_ids = {
        item["item_id"]
        for item in MANIFEST["items"]
        if item["partition"] == D.LOCKED_PARTITION
    }
    assert not locked_ids.intersection({row.item_id for row in FAMILY_ROWS})


def test_evidence_refs_anchor_exact_window_id():
    assert all(row.evidence_refs and row.evidence_refs[0] == row.window_id for row in FAMILY_ROWS)


def test_performance_has_six_rows():
    assert len(PERFORMANCE) == 6


def test_powerline_known_truth_is_detected():
    row = _row_for("LF_POWERLINE")
    assert row["scorable_truth_positive_count"] == 1
    assert row["tp"] == 1
    assert row["recall_effective"] == 1.0


def test_motion_known_truth_is_detected():
    row = _row_for("LF_LOW_FREQUENCY_CONTAMINATION")
    assert row["scorable_truth_positive_count"] == 2
    assert row["tp"] == 2
    assert row["recall_effective"] == 1.0


def test_dropout_positive_truth_has_localization_gap():
    row = _row_for("LF_MISSING_DROPOUT")
    assert row["declared_truth_positive_count"] == 3
    assert row["truth_localization_gap_count"] == 3
    assert row["scorable_truth_positive_count"] == 0
    assert row["recall_effective"] is None


def test_clipping_positive_truth_has_localization_gap():
    row = _row_for("LF_CLIPPING_SATURATION")
    assert row["declared_truth_positive_count"] == 1
    assert row["truth_localization_gap_count"] == 1
    assert row["scorable_truth_positive_count"] == 0


def test_baseline_truth_is_scorable_but_unresolved_without_threshold():
    row = _row_for("LF_BASELINE_NOISE")
    assert row["scorable_truth_positive_count"] == 1
    assert row["positive_unresolved"] == 1
    assert row["recall_effective"] == 0.0


def test_poor_contact_has_no_positive_truth_fixture():
    row = _row_for("LF_POOR_CONTACT")
    assert row["declared_truth_positive_count"] == 0
    assert row["truth_status"] == "NEGATIVE_ONLY_NO_POSITIVE_FIXTURE"


def test_poor_contact_is_not_scored_without_cross_channel_peers():
    row = _row_for("LF_POOR_CONTACT")
    assert row["evaluated_binary_count"] == 0
    assert all(
        r.applicability_status == "NOT_SCORABLE_NO_CROSS_CHANNEL_PEERS"
        for r in FAMILY_ROWS
        if r.family_id == "LF_POOR_CONTACT"
    )


def test_integrity_timestamp_recall_is_one():
    row = D.integrity_performance_rows(INTEGRITY_ROWS)[0]
    assert row["recall"] == 1.0


def test_integrity_timestamp_specificity_is_one():
    row = D.integrity_performance_rows(INTEGRITY_ROWS)[0]
    assert row["specificity"] == 1.0


@pytest.mark.parametrize("scenario", ["TIMESTAMP_DUPLICATE", "TIMESTAMP_NON_MONOTONIC"])
def test_timestamp_corruption_blocks_day29_integrity(scenario: str):
    row = next(value for value in INTEGRITY_ROWS if value.scenario == scenario)
    assert row.binary_block_vote == 1
    assert row.signal_quality == "FAIL"
    assert row.gate_status == "BLOCKED"


def test_clean_timestamp_integrity_passes():
    row = next(value for value in INTEGRITY_ROWS if value.scenario == "CLEAN")
    assert row.binary_block_vote == 0
    assert row.signal_quality == "PASS"


def test_low_amplitude_stress_is_not_poor_contact_truth():
    assert "LOW_AMPLITUDE_ENGINEERING_STRESS" not in D.TRUTH_POSITIVES["LF_POOR_CONTACT"]


def test_four_corpus_truth_window_misalignment_cases_exist():
    misaligned = {
        row.item_id
        for row in FAMILY_ROWS
        if row.truth_localization_status == "LOCAL_TRUTH_OUTSIDE_WINDOW_CORE_NOT_SCORABLE"
    }
    assert len(misaligned) == 4


@pytest.mark.parametrize("scenario", ["MISSING", "ZERO_DROPOUT", "FLATLINE", "CLIPPING"])
def test_local_corruption_is_outside_core(scenario: str):
    rows = [row for row in FAMILY_ROWS if row.scenario == scenario]
    assert {row.truth_localization_status for row in rows} == {
        "LOCAL_TRUTH_OUTSIDE_WINDOW_CORE_NOT_SCORABLE"
    }


def test_motion_transient_truth_overlaps_core():
    rows = [row for row in FAMILY_ROWS if row.scenario == "MOTION_TRANSIENT"]
    assert {row.truth_localization_status for row in rows} == {
        "LOCAL_TRUTH_OVERLAPS_WINDOW_CORE"
    }


def test_corpus_repair_candidates_are_not_sent_to_expert_review():
    repair = [row for row in CANDIDATES if row["review_target"] == "ENGINEERING_CORPUS_REPAIR"]
    assert len(repair) == 4
    assert all(row["selected_for_future_review"] is False for row in repair)


def test_low_amplitude_candidate_uses_physiology_ambiguity_stratum():
    row = next(row for row in CANDIDATES if row["scenario"] == "SYNTHETIC_LOW_AMPLITUDE_STRESS")
    assert row["acquisition_stratum"] == "ARTIFACT_VS_PHYSIOLOGY_AMBIGUITY"
    assert "PHYSIOLOGY_PRESERVATION_SENTINEL" in row["selection_reasons"]


def test_baseline_known_truth_is_unresolved_not_false_allow():
    row = next(row for row in CANDIDATES if row["scenario"] == "BASELINE_NOISE")
    assert "KNOWN_TRUTH_TARGET_UNRESOLVED_FAIL_CLOSED" in row["selection_reasons"]
    assert "KNOWN_TRUTH_TARGET_FALSE_ALLOW" not in row["selection_reasons"]


def test_summary_forbids_expert_agreement_claim(tmp_path: Path):
    summary = D.write_outputs(tmp_path, FAMILY_ROWS, INTEGRITY_ROWS)
    assert summary["expert_agreement_status"] == "NOT_PERFORMED"
    assert summary["cohen_kappa_status"].startswith("NOT_APPLICABLE")


def test_summary_label_model_training_false(tmp_path: Path):
    summary = D.write_outputs(tmp_path, FAMILY_ROWS, INTEGRITY_ROWS)
    assert summary["label_model_training"] is False


def test_summary_threshold_tuning_false(tmp_path: Path):
    summary = D.write_outputs(tmp_path, FAMILY_ROWS, INTEGRITY_ROWS)
    assert summary["threshold_tuning"] is False


def test_summary_event_localization_metric_not_claimed(tmp_path: Path):
    summary = D.write_outputs(tmp_path, FAMILY_ROWS, INTEGRITY_ROWS)
    assert summary["event_localization_metrics"].startswith("NOT_APPLICABLE")


def test_correlation_output_is_6_by_6_long_form():
    assert len(CORRELATIONS) == 36


def test_poor_contact_has_zero_pairwise_coevaluation():
    rows = [
        row
        for row in CORRELATIONS
        if row["left_family"] == "LF_POOR_CONTACT"
        and row["right_family"] != "LF_POOR_CONTACT"
    ]
    assert all(row["co_evaluated_count"] == 0 for row in rows)


def test_powerline_motion_are_coevaluated_on_all_development_items():
    row = next(
        row
        for row in CORRELATIONS
        if row["left_family"] == "LF_POWERLINE"
        and row["right_family"] == "LF_LOW_FREQUENCY_CONTAMINATION"
    )
    assert row["co_evaluated_count"] == 12


def test_correlation_is_deterministic():
    assert D.correlation_rows(FAMILY_ROWS) == D.correlation_rows(FAMILY_ROWS)


def test_candidate_ranking_is_deterministic():
    assert CANDIDATES == D.review_candidate_rows(FAMILY_ROWS, INTEGRITY_ROWS)


def test_candidate_ranks_are_contiguous():
    assert [row["rank"] for row in CANDIDATES] == list(range(1, 13))


def test_written_outputs_are_deterministic(tmp_path: Path):
    first = tmp_path / "a"
    second = tmp_path / "b"
    first.mkdir()
    second.mkdir()
    D.write_outputs(first, FAMILY_ROWS, INTEGRITY_ROWS)
    D.write_outputs(second, FAMILY_ROWS, INTEGRITY_ROWS)
    names = sorted(path.name for path in first.iterdir())
    assert names == sorted(path.name for path in second.iterdir())
    assert D.stable_output_digest(first / name for name in names) == D.stable_output_digest(
        second / name for name in names
    )


def test_written_performance_csv_recomputes(tmp_path: Path):
    D.write_outputs(tmp_path, FAMILY_ROWS, INTEGRITY_ROWS)
    with (tmp_path / "lf-performance-synthetic-v0.1.csv").open(
        encoding="utf-8", newline=""
    ) as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 6
    power = next(row for row in rows if row["family_id"] == "LF_POWERLINE")
    assert power["tp"] == "1"
    assert power["recall_effective"] == "1.0"


def test_non_synthetic_evidence_tier_rejected():
    manifest = json.loads(json.dumps(MANIFEST))
    dev = next(item for item in manifest["items"] if item["partition"] == D.DEVELOPMENT_PARTITION)
    dev["evidence_tier"] = "WEAK_LABEL_CANDIDATE"
    with pytest.raises(D.Day34AnalysisError, match="SYNTHETIC_KNOWN_TRUTH"):
        D.development_items(manifest)


def test_missing_development_truth_rejected():
    manifest = json.loads(json.dumps(MANIFEST))
    dev = next(item for item in manifest["items"] if item["partition"] == D.DEVELOPMENT_PARTITION)
    dev["synthetic_truth"] = None
    with pytest.raises(D.Day34AnalysisError, match="lacks visible synthetic truth"):
        D.development_items(manifest)


def test_synthetic_clinical_truth_claim_rejected():
    manifest = json.loads(json.dumps(MANIFEST))
    dev = next(item for item in manifest["items"] if item["partition"] == D.DEVELOPMENT_PARTITION)
    dev["synthetic_truth"]["clinical_truth_claim"] = True
    with pytest.raises(D.Day34AnalysisError, match="clinical truth"):
        D.development_items(manifest)


def test_unknown_partition_rejected():
    manifest = json.loads(json.dumps(MANIFEST))
    dev = next(item for item in manifest["items"] if item["partition"] == D.DEVELOPMENT_PARTITION)
    dev["partition"] = "mystery"
    with pytest.raises(D.Day34AnalysisError, match="unknown corpus partition"):
        D.development_items(manifest)


def test_signal_hash_mismatch_rejected(tmp_path: Path):
    item = json.loads(json.dumps(_item_scenario("CLEAN")))
    source = CORPUS_ROOT / item["signal_artifact"]["relative_path"]
    signal_dir = tmp_path / "signals"
    signal_dir.mkdir()
    target = signal_dir / source.name
    shutil.copy2(source, target)
    target.write_bytes(target.read_bytes() + b"tamper")
    with pytest.raises(D.Day34AnalysisError, match="hash mismatch"):
        D._load_signal(item, tmp_path)


@pytest.mark.parametrize(
    ("candidate", "expected"),
    [
        ("FAIL_CANDIDATE", 1),
        ("WARNING_CANDIDATE", 1),
        ("PASS_CANDIDATE", 0),
        ("UNKNOWN", None),
        ("ABSTAIN", None),
    ],
)
def test_binary_candidate_semantics(candidate: str, expected: int | None):
    assert D._family_binary(candidate) == expected


def test_non_applicable_family_has_no_binary_vote():
    assert D._family_binary("PASS_CANDIDATE", applicable=False) is None


def test_baseline_output_exposes_threshold_not_verified():
    row = _family_scenario("LF_BASELINE_NOISE", "BASELINE_NOISE")
    assert "BASELINE_NOISE_THRESHOLD_NOT_VERIFIED" in row.reason_codes
    assert row.label_candidate == "UNKNOWN"


def test_powerline_output_is_positive_for_injected_50hz():
    row = _family_scenario("LF_POWERLINE", "POWERLINE_50HZ")
    assert row.binary_vote == 1
    assert "POWERLINE_INTERFERENCE_SUSPECTED" in row.reason_codes


@pytest.mark.parametrize("scenario", ["MOTION_DRIFT", "MOTION_TRANSIENT"])
def test_motion_output_positive_for_known_motion_truth(scenario: str):
    row = _family_scenario("LF_LOW_FREQUENCY_CONTAMINATION", scenario)
    assert row.binary_vote == 1
    assert "MOTION_ARTIFACT_SUSPECTED" in row.reason_codes


def test_clean_window_has_no_positive_scorable_weak_family():
    rows = [row for row in FAMILY_ROWS if row.scenario == "CLEAN" and row.binary_vote is not None]
    assert rows
    assert all(row.binary_vote == 0 for row in rows)


def test_performance_rows_never_claim_clinical_evidence():
    assert all(row["clinical_claim"] is False for row in PERFORMANCE)
    assert all(row["expert_reference"] is False for row in PERFORMANCE)


def test_integrity_performance_never_claims_clinical_evidence():
    assert D.integrity_performance_rows(INTEGRITY_ROWS)[0]["clinical_claim"] is False


def test_valid_claim_language_passes():
    D.validate_claim_language("research-only synthetic known-truth engineering evidence")


@pytest.mark.parametrize(
    "text",
    [
        "clinically validated detector",
        "validated at Vinmec",
        "diagnostic accuracy is high",
        "gold standard annotations",
    ],
)
def test_forbidden_claim_language_rejected(text: str):
    with pytest.raises(D.Day34AnalysisError, match="forbidden clinical claim"):
        D.validate_claim_language(text)
