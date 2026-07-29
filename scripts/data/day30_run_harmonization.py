#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from hashlib import sha256
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "ai-core" / "data"))

from day30.contracts import PROJECT_CLASS_ORDER
from day30.ontology import build_ontology_report, load_supported_canonical_labels
from day30.policy_validation import (
    validate_channel_policy,
    validate_sampling_policy,
    validate_storage_contract,
    validate_windowing_policy,
)
from day30.preflight import validate_pre_day30_report
from day30.readiness import decide_readiness
from day30.view_registry import build_view_registry


def _read_yaml(path: Path) -> dict[str, Any]:
    document = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(document, dict):
        raise ValueError(f"YAML root must be an object: {path}")
    return document


def _sha256(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _validate_schema(document: dict[str, Any], schema_name: str) -> None:
    schema_path = ROOT / "packages/common-schemas/json" / schema_name
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    Draft202012Validator(schema).validate(document)


def _write_json(path: Path, document: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(document, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    parser.add_argument("--report", required=True)
    parser.add_argument(
        "--mendeley-labels",
        default=(
            "data-platform/manifests/public-datasets/"
            "mendeley-4channel-hand-gesture-v2/label-dictionary.yaml"
        ),
    )
    parser.add_argument(
        "--grabmyo-labels",
        default=(
            "data-platform/manifests/public-datasets/"
            "grabmyo-canonical/label-dictionary.yaml"
        ),
    )
    parser.add_argument(
        "--evidence-dir", default="qa-validation/evidence/day30"
    )
    args = parser.parse_args()
    try:
        config_path = Path(args.config)
        report_path = Path(args.report)
        mendeley_path = Path(args.mendeley_labels)
        grabmyo_path = Path(args.grabmyo_labels)
        config = _read_yaml(config_path)
        report = json.loads(report_path.read_text(encoding="utf-8"))
        preflight = validate_pre_day30_report(report)

        policy_paths = {
            name: ROOT / path for name, path in config["policies"].items()
        }
        policy_results = {
            "sampling": validate_sampling_policy(policy_paths["sampling"]),
            "channels": validate_channel_policy(policy_paths["channels"]),
            "windowing": validate_windowing_policy(policy_paths["windowing"]),
            "storage": validate_storage_contract(policy_paths["storage"]),
        }
        policy_results["pass"] = all(
            result["pass"] for result in policy_results.values()
        )

        ontology = build_ontology_report(
            load_supported_canonical_labels(mendeley_path),
            load_supported_canonical_labels(grabmyo_path),
            PROJECT_CLASS_ORDER,
        )
        registry = build_view_registry(ontology)
        authorization = _read_yaml(
            ROOT / "ai-core/configs/day30_training_authorization.research.yaml"
        )
        checks = {
            "input_gate_passed": preflight["pass"],
            "common_ontology_built": bool(ontology["intersection"]),
            "channel_policy_validated": policy_results["channels"]["pass"],
            "sampling_policy_validated": policy_results["sampling"]["pass"],
            "window_policy_validated": policy_results["windowing"]["pass"],
            "view_registry_built": bool(registry["views"]),
            "storage_contract_validated": policy_results["storage"]["pass"],
            "test_seals_unopened": (
                preflight["test_set_opened"] is False
                and report.get("real_data_signal_rows_read") == 0
            ),
            "pooled_training_disabled": (
                registry["pooled_training_allowed"] is False
                and config.get("pooled_training_allowed") is False
            ),
            "full_subject_index_verified": config["coverage"].get(
                "full_population_coverage_verified"
            ),
            "split_hashes_verified": authorization.get("split_hashes_verified"),
            "resolved_dependency_lock_verified": authorization.get(
                "resolved_dependency_lock_verified"
            ),
            "day31_training_authorization_present": authorization.get(
                "authorization_record_present"
            ),
        }
        readiness = decide_readiness(checks)

        input_paths = {
            "config": config_path,
            "report": report_path,
            "mendeley_labels": mendeley_path,
            "grabmyo_labels": grabmyo_path,
            **{f"policy_{name}": path for name, path in policy_paths.items()},
        }
        provenance = {name: _sha256(path) for name, path in input_paths.items()}
        run = {
            "schema_version": "day30-harmonization-run.v1",
            "preflight": preflight,
            "ontology": ontology,
            "view_registry": registry,
            "policy_validation": policy_results,
            "readiness": readiness,
            "input_provenance": provenance,
            "real_data_signal_rows_read": 0,
            "training_allowed": False,
            "pooled_training_allowed": False,
        }

        for document, schema_name in (
            (preflight, "day30-preflight.v1.schema.json"),
            (ontology, "day30-common-ontology.v1.schema.json"),
            (registry, "day30-dataset-view-registry.v1.schema.json"),
            (readiness, "day30-readiness-decision.v1.schema.json"),
            (run, "day30-harmonization-run.v1.schema.json"),
        ):
            _validate_schema(document, schema_name)

        evidence = Path(args.evidence_dir)
        evidence.mkdir(parents=True, exist_ok=True)
        _write_json(evidence / "day30-preflight.json", preflight)
        _write_json(evidence / "day30-common-ontology.json", ontology)
        _write_json(evidence / "day30-dataset-view-registry.json", registry)
        _write_json(evidence / "day30-readiness-decision.json", readiness)
        _write_json(evidence / "day30-harmonization-run.json", run)
        print(json.dumps(run, ensure_ascii=False, indent=2))
        return 0 if readiness["status"] != "BLOCKED_WITH_EVIDENCE" else 2
    except (
        OSError,
        ValueError,
        TypeError,
        KeyError,
    ) as error:
        print(f"day30 harmonization failed: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
