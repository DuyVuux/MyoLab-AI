from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest
import yaml
from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]

CASES = [
    ('experiment-manifest.schema.json', 'experiment-manifest.example.yaml'),
    ('model-registry-record.schema.json', 'model-registry-record.example.yaml'),
    ('release-manifest.schema.json', 'release-manifest.example.yaml'),
    ('rollback-record.schema.json', 'rollback-record.example.yaml'),
]


def load_schema(name: str):
    return json.loads((ROOT / 'schemas' / name).read_text(encoding='utf-8'))


def load_example(name: str):
    return yaml.safe_load((ROOT / 'examples' / name).read_text(encoding='utf-8'))


def errors(schema_name: str, instance):
    validator = Draft202012Validator(load_schema(schema_name), format_checker=FormatChecker())
    return list(validator.iter_errors(instance))


@pytest.mark.parametrize(('schema_name', 'example_name'), CASES)
def test_examples_validate(schema_name: str, example_name: str):
    assert errors(schema_name, load_example(example_name)) == []


def test_blueprint_experiment_cannot_enable_training():
    instance = load_example('experiment-manifest.example.yaml')
    instance['training_allowed'] = True
    assert errors('experiment-manifest.schema.json', instance)


def test_blueprint_experiment_cannot_have_run_metrics():
    instance = load_example('experiment-manifest.example.yaml')
    instance['metrics']['execution_status'] = 'COMPLETE'
    assert errors('experiment-manifest.schema.json', instance)


def test_registry_rejects_clinical_validated_state():
    instance = load_example('model-registry-record.example.yaml')
    instance['registry_state'] = 'clinical-validated'
    assert errors('model-registry-record.schema.json', instance)


def test_pilot_candidate_requires_human_review_and_license_pass():
    instance = load_example('model-registry-record.example.yaml')
    instance['registry_state'] = 'pilot-candidate'
    instance['human_review_required'] = False
    assert errors('model-registry-record.schema.json', instance)


def test_approved_release_rejects_untrusted_deserialization():
    instance = load_example('release-manifest.example.yaml')
    instance['release_state'] = 'approved'
    instance['security_gate']['untrusted_deserialization_present'] = True
    assert errors('release-manifest.schema.json', instance)


def test_all_configs_have_governance_metadata_and_training_disabled():
    required = {'schema_version', 'status', 'rationale', 'evidence_ids', 'open_questions', 'training_allowed'}
    for path in (ROOT / 'configs').glob('*.yaml'):
        obj = yaml.safe_load(path.read_text(encoding='utf-8'))
        assert required.issubset(obj), path.name
        assert obj['training_allowed'] is False, path.name


def test_no_model_binary_is_present():
    forbidden = {'.pkl', '.pickle', '.joblib', '.onnx', '.pt', '.pth', '.ckpt'}
    found = [p for p in ROOT.rglob('*') if p.is_file() and p.suffix.lower() in forbidden]
    assert found == []
