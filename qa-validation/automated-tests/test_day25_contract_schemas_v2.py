from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator, ValidationError

ROOT = Path(__file__).resolve().parents[2]
SCHEMA_DIR = ROOT / "packages/common-schemas/json"


def schema(name: str) -> dict:
    return json.loads((SCHEMA_DIR / name).read_text(encoding="utf-8"))


def instance(relative: str) -> dict:
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def validate(schema_name: str, payload: dict) -> None:
    Draft202012Validator(schema(schema_name)).validate(payload)


def test_manifest_template_validates() -> None:
    validate(
        "research-dataset-manifest.v0.2.schema.json",
        instance("data-platform/manifests/public-dataset-manifest.template.json"),
    )


def test_manifest_rejects_direct_identifier_property() -> None:
    payload = instance("data-platform/manifests/public-dataset-manifest.template.json")
    payload["patientName"] = "Không được phép"
    with pytest.raises(ValidationError):
        validate("research-dataset-manifest.v0.2.schema.json", payload)


def test_manifest_rejects_raw_samples_property() -> None:
    payload = instance("data-platform/manifests/public-dataset-manifest.template.json")
    payload["rawSamples"] = [1, 2, 3]
    with pytest.raises(ValidationError):
        validate("research-dataset-manifest.v0.2.schema.json", payload)


def test_site_evidence_template_validates() -> None:
    validate(
        "site-export-evidence-bundle.v0.1.schema.json",
        instance("integrations/devices/noraxon/site-export-evidence-bundle.template.json"),
    )


def test_generated_split_and_gate_validate() -> None:
    validate(
        "subject-group-split.v0.2.schema.json",
        instance("qa-validation/evidence/day25-subject-group-split-v0.2.json"),
    )
    validate(
        "data-readiness-gate.v0.2.schema.json",
        instance("qa-validation/evidence/day25-data-readiness-gate-v0.2.json"),
    )
