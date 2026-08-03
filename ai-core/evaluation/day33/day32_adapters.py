from __future__ import annotations

import csv
import gzip
import hashlib
import json
import re
import zipfile
from pathlib import Path

MENDELEY_CLASS_ORDER = ["rest", "hand_close", "wrist_flexion", "wrist_extension"]


def _sha256_file(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def _read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _zip_json(archive, name):
    data = archive.read(name)
    return json.loads(data.decode("utf-8")), _sha256_bytes(data)


def _day_from_record(record_id):
    match = re.search(r"-D(\d+)-", record_id or "")
    return f"D{match.group(1)}" if match else ""


def adapt_mendeley_oof_windows(experiment_dir):
    base = Path(experiment_dir)
    evidence = _read_json(base / "day32-baseline-evidence.json")
    selection = _read_json(base / "day32-model-selection.json")
    fold_hash = evidence.get("cross_validation", {}).get("fold_contract_sha256", _sha256_file(base / "day32-cv-fold-contract.json"))
    matrix_hash = evidence.get("input", {}).get("matrix_sha256", "")
    model_config_hash = selection.get("benchmark_config_hash") or evidence.get("benchmark", {}).get("configuration_hash", "")
    model_id = selection.get("selected_model_id", "unknown_model")
    feature_arm = selection.get("selected_feature_arm", "unknown_feature_arm")
    run_id = evidence.get("run_id", base.name)

    rows = []
    with gzip.open(base / "day32-selected-oof-window-predictions.csv.gz", "rt", newline="", encoding="utf-8") as handle:
        for source in csv.DictReader(handle):
            if source.get("feature_arm") != feature_arm or source.get("model_id") != model_id:
                continue
            rows.append({
                "dataset_id": "mendeley-4channel-hand-gesture-v2",
                "dataset_view_id": "mendeley-primary-fall14-v1",
                "run_id": run_id,
                "model_id": model_id,
                "feature_arm": feature_arm,
                "outer_fold": source["fold_id"],
                "subject_id": source["subject_id"],
                "day_id": "",
                "session_id": "",
                "repetition_id": source["repetition_id"],
                "record_id": source["record_id"],
                "window_id": source["window_id"],
                "y_true": source["y_true"],
                "y_pred": source["y_pred"],
                "split_name": "development_outer_validation",
                "score_type": "label_only",
                "class_order_json": json.dumps(MENDELEY_CLASS_ORDER),
                "class_scores_json": "",
                "qc_flags_json": "[]",
                "source_matrix_sha256": matrix_hash,
                "fold_manifest_sha256": fold_hash,
                "model_config_sha256": model_config_hash,
            })
    return rows


def adapt_grabmyo_oof_trials(zip_path):
    archive_path = Path(zip_path)
    with zipfile.ZipFile(archive_path) as archive:
        evidence, _ = _zip_json(archive, "grabmyo-baseline-evidence.json")
        selection, selection_hash = _zip_json(archive, "grabmyo-model-selection.json")
        fold_hash = _sha256_bytes(archive.read("grabmyo-cv-fold-contract.json"))
        input_gate = evidence.get("input_gate", {})
        matrix_hash = input_gate.get("npz_sha256", "")
        run_id = evidence.get("run_id", archive_path.parent.name)
        model_id = selection.get("selected_model_name", "unknown_model")
        feature_arm = selection.get("selected_feature_arm", "unknown_feature_arm")
        dataset_view_id = input_gate.get("dataset_view_id", "grabmyo-primary4-forearm16-fall14-v1")
        with archive.open("grabmyo-selected-oof-trial-predictions.csv") as raw:
            text = (line.decode("utf-8") for line in raw)
            reader = csv.DictReader(text)
            score_columns = [name for name in reader.fieldnames or [] if name.startswith("score__")]
            class_order = [name.removeprefix("score__") for name in score_columns]
            rows = []
            for source in reader:
                scores = {cls: float(source[f"score__{cls}"]) for cls in class_order}
                qc_flags = []
                if str(source.get("low_coverage_flag", "")).lower() == "true":
                    qc_flags.append("LOW_COVERAGE")
                rows.append({
                    "dataset_id": "grabmyo-physionet-v1.1.0",
                    "dataset_view_id": dataset_view_id,
                    "run_id": run_id,
                    "model_id": model_id,
                    "feature_arm": feature_arm,
                    "outer_fold": 0,
                    "subject_id": source["subject_id"],
                    "day_id": _day_from_record(source.get("record_id", "")),
                    "session_id": source.get("session_id", ""),
                    "repetition_id": source["repetition_id"],
                    "record_id": source["record_id"],
                    "window_id": source["trial_id"],
                    "y_true": source["y_true"],
                    "y_pred": source["y_pred"],
                    "split_name": "development_outer_validation",
                    "score_type": "decision_function",
                    "class_order_json": json.dumps(class_order),
                    "class_scores_json": json.dumps(scores, sort_keys=True),
                    "qc_flags_json": json.dumps(qc_flags),
                    "source_matrix_sha256": matrix_hash,
                    "fold_manifest_sha256": fold_hash,
                    "model_config_sha256": selection_hash,
                    "source_window_count": source.get("valid_window_count", ""),
                })
    return rows
