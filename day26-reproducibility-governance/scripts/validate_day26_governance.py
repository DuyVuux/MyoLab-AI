#!/usr/bin/env python3
"""Validate Day 26 governance schemas, examples, hashes and scope locks."""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / 'validation' / 'VALIDATION_REPORT.md'


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def load_yaml(path: Path) -> Any:
    return yaml.safe_load(path.read_text(encoding='utf-8'))


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding='utf-8'))


def validate(schema_path: Path, instance_path: Path) -> list[str]:
    schema = load_json(schema_path)
    instance = load_yaml(instance_path) if instance_path.suffix in {'.yaml', '.yml'} else load_json(instance_path)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    return [f"{list(err.absolute_path)}: {err.message}" for err in sorted(validator.iter_errors(instance), key=lambda e: list(e.absolute_path))]


def verify_artifact_refs(instance: Any, errors: list[str], prefix: str = '') -> None:
    if isinstance(instance, dict):
        keys = set(instance)
        if {'uri', 'sha256', 'size_bytes', 'artifact_id', 'role'}.issubset(keys):
            path = ROOT / instance['uri']
            if not path.is_file():
                errors.append(f"{prefix or instance['artifact_id']}: referenced file missing: {path}")
            else:
                actual_hash = sha256_file(path)
                if actual_hash != instance['sha256']:
                    errors.append(f"{prefix or instance['artifact_id']}: SHA-256 mismatch")
                if path.stat().st_size != instance['size_bytes']:
                    errors.append(f"{prefix or instance['artifact_id']}: size mismatch")
        for key, value in instance.items():
            verify_artifact_refs(value, errors, f'{prefix}.{key}' if prefix else key)
    elif isinstance(instance, list):
        for index, value in enumerate(instance):
            verify_artifact_refs(value, errors, f'{prefix}[{index}]')


def main() -> int:
    schema_examples = [
        ('experiment-manifest.schema.json', 'experiment-manifest.example.yaml'),
        ('model-registry-record.schema.json', 'model-registry-record.example.yaml'),
        ('release-manifest.schema.json', 'release-manifest.example.yaml'),
        ('rollback-record.schema.json', 'rollback-record.example.yaml'),
    ]

    failures: list[str] = []
    checks: list[tuple[str, str]] = []

    for schema_name, example_name in schema_examples:
        schema_path = ROOT / 'schemas' / schema_name
        example_path = ROOT / 'examples' / example_name
        errs = validate(schema_path, example_path)
        if errs:
            failures.extend([f'{example_name}: {e}' for e in errs])
            checks.append((f'Schema validation: {example_name}', 'FAIL'))
        else:
            checks.append((f'Schema validation: {example_name}', 'PASS'))

    experiment = load_yaml(ROOT / 'examples' / 'experiment-manifest.example.yaml')
    artifact_errors: list[str] = []
    verify_artifact_refs(experiment, artifact_errors)
    if artifact_errors:
        failures.extend(artifact_errors)
        checks.append(('Experiment artifact references and hashes', 'FAIL'))
    else:
        checks.append(('Experiment artifact references and hashes', 'PASS'))

    model_record = load_yaml(ROOT / 'examples' / 'model-registry-record.example.yaml')
    expected_exp_hash = sha256_file(ROOT / 'examples' / 'experiment-manifest.example.yaml')
    if model_record['parent_experiment']['manifest_sha256'] != expected_exp_hash:
        failures.append('Model registry parent experiment manifest hash mismatch')
        checks.append(('Registry → experiment lineage hash', 'FAIL'))
    else:
        checks.append(('Registry → experiment lineage hash', 'PASS'))

    release = load_yaml(ROOT / 'examples' / 'release-manifest.example.yaml')
    expected_model_hash = sha256_file(ROOT / 'examples' / 'model-registry-record.example.yaml')
    if release['registry_records'][0]['record_sha256'] != expected_model_hash:
        failures.append('Release registry-record hash mismatch')
        checks.append(('Release → registry lineage hash', 'FAIL'))
    else:
        checks.append(('Release → registry lineage hash', 'PASS'))

    # Day 26 training lock across machine-readable configs/examples.
    training_violations: list[str] = []
    for path in list((ROOT / 'configs').glob('*.yaml')) + list((ROOT / 'examples').glob('*.yaml')) + list((ROOT / 'fixtures').glob('*.yaml')) + list((ROOT / 'fixtures').glob('*.json')):
        try:
            obj = load_yaml(path) if path.suffix in {'.yaml', '.yml'} else load_json(path)
        except Exception:
            continue
        if isinstance(obj, dict) and obj.get('training_allowed') is not False:
            training_violations.append(str(path.relative_to(ROOT)))
    if training_violations:
        failures.append(f'training_allowed is not false in: {training_violations}')
        checks.append(('Day 26 training lock', 'FAIL'))
    else:
        checks.append(('Day 26 training lock', 'PASS'))

    # Exact registry state list and prohibited state absence in machine value list.
    policy = load_yaml(ROOT / 'configs' / 'registry-state-machine.research.yaml')
    expected_states = ['draft', 'research', 'candidate', 'validated-for-engineering', 'pilot-candidate', 'rejected', 'archived']
    if policy['states'] != expected_states:
        failures.append('Registry state list differs from the locked sequence')
        checks.append(('Registry state machine', 'FAIL'))
    else:
        checks.append(('Registry state machine', 'PASS'))

    # Environment contract requires a real resolved uv.lock before training but Day 26 must not fake one.
    env = load_yaml(ROOT / 'configs' / 'environment-lock.research.yaml')
    uv_lock_path = ROOT / env['resolved_lock']['expected_path']
    if uv_lock_path.exists():
        checks.append(('Resolved uv.lock Day 26 state', 'WARN: present; verify it was resolver-generated'))
    elif env['resolved_lock']['required_before_training'] and env['resolved_lock']['status'] == 'NOT_GENERATED_DAY26':
        checks.append(('Resolved uv.lock Day 26 state', 'PASS: honestly absent; hard gate documented'))
    else:
        failures.append('Resolved lock absence is not represented as a hard pre-training gate')
        checks.append(('Resolved uv.lock Day 26 state', 'FAIL'))

    # Ensure no real model-looking binary exists.
    forbidden_extensions = {'.pkl', '.pickle', '.joblib', '.onnx', '.pt', '.pth', '.ckpt'}
    binaries = [p.relative_to(ROOT).as_posix() for p in ROOT.rglob('*') if p.is_file() and p.suffix.lower() in forbidden_extensions]
    if binaries:
        failures.append(f'Real/model-like artifact files found: {binaries}')
        checks.append(('No model artifact created', 'FAIL'))
    else:
        checks.append(('No model artifact created', 'PASS'))

    # Blueprint hash-ledger integrity.
    blueprint_ledger_path = ROOT / 'fixtures' / 'hash-ledger.blueprint.json'
    ledger_errors: list[str] = []
    if blueprint_ledger_path.exists():
        blueprint_ledger = load_json(blueprint_ledger_path)
        for row in blueprint_ledger.get('files', []):
            path = ROOT / row['path']
            if not path.is_file():
                ledger_errors.append(f'Blueprint ledger missing file: {row["path"]}')
                continue
            if path.stat().st_size != row['size_bytes']:
                ledger_errors.append(f'Blueprint ledger size mismatch: {row["path"]}')
            if sha256_file(path) != row['sha256']:
                ledger_errors.append(f'Blueprint ledger hash mismatch: {row["path"]}')
    else:
        ledger_errors.append('Blueprint hash ledger is missing')
    if ledger_errors:
        failures.extend(ledger_errors)
        checks.append(('Blueprint hash-ledger integrity', 'FAIL'))
    else:
        checks.append(('Blueprint hash-ledger integrity', 'PASS'))

    # Package manifest integrity, when present.
    package_manifest_path = ROOT / 'PACKAGE_MANIFEST.json'
    if package_manifest_path.exists():
        package_manifest = load_json(package_manifest_path)
        manifest_errors: list[str] = []
        listed = set()
        for row in package_manifest.get('files', []):
            rel = row['path']
            listed.add(rel)
            path = ROOT / rel
            if not path.is_file():
                manifest_errors.append(f'Package manifest missing file: {rel}')
                continue
            if path.stat().st_size != row['size_bytes']:
                manifest_errors.append(f'Package manifest size mismatch: {rel}')
            if sha256_file(path) != row['sha256']:
                manifest_errors.append(f'Package manifest hash mismatch: {rel}')
        expected = {
            p.relative_to(ROOT).as_posix()
            for p in ROOT.rglob('*')
            if p.is_file()
            and p != package_manifest_path
            and p != REPORT
            and '.pytest_cache' not in p.parts
            and '__pycache__' not in p.parts
        }
        missing_entries = sorted(expected - listed)
        extra_entries = sorted(listed - expected)
        if missing_entries:
            manifest_errors.append(f'Package manifest missing entries: {missing_entries}')
        if extra_entries:
            manifest_errors.append(f'Package manifest has extra entries: {extra_entries}')
        if manifest_errors:
            failures.extend(manifest_errors)
            checks.append(('Package manifest integrity', 'FAIL'))
        else:
            checks.append(('Package manifest integrity', 'PASS'))

    # Machine-readable config metadata completeness.
    meta_fields = {'schema_version', 'status', 'rationale', 'evidence_ids', 'open_questions', 'training_allowed'}
    metadata_errors: list[str] = []
    for path in (ROOT / 'configs').glob('*.yaml'):
        obj = load_yaml(path)
        missing = sorted(meta_fields - set(obj))
        if missing:
            metadata_errors.append(f'{path.name}: {missing}')
    if metadata_errors:
        failures.extend(metadata_errors)
        checks.append(('Config governance metadata', 'FAIL'))
    else:
        checks.append(('Config governance metadata', 'PASS'))

    REPORT.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        '# Day 26 Governance Package Validation Report',
        '',
        '- schema_version: `1.0`',
        '- status: `' + ('PASS' if not failures else 'FAIL') + '`',
        '- trainingAllowed: `false`',
        '',
        '## Checks',
        '',
        '| Check | Result |',
        '|---|---|',
    ]
    for name, result in checks:
        lines.append(f'| {name} | {result} |')
    lines.extend(['', '## Failures', ''])
    if failures:
        lines.extend([f'- {failure}' for failure in failures])
    else:
        lines.append('- None.')
    lines.extend([
        '',
        '## Important pre-Day29 condition',
        '',
        'A real resolver-generated `environment/uv.lock` is intentionally not included in Day 26. '
        'It remains a hard gate before any authorized training execution.',
        '',
    ])
    REPORT.write_text('\n'.join(lines), encoding='utf-8')
    print(REPORT)
    if failures:
        for failure in failures:
            print(f'FAIL: {failure}')
        return 1
    print('All Day 26 blueprint validations passed.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
