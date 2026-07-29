from __future__ import annotations

import csv
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def run_script(path: str, *arguments: str) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        [sys.executable, path, *arguments],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    return result


def test_tooling_smoke_and_artifact_inventory_pass() -> None:
    smoke = run_script("scripts/dev/day30_tooling_smoke.py")
    assert json.loads(smoke.stdout)["pass"] is True
    artifact = run_script("scripts/dev/check_day30_artifacts.py")
    assert json.loads(artifact.stdout)["pass"] is True


def test_manifest_builder_is_deterministic_and_excludes_reference_pack(
    tmp_path: Path,
) -> None:
    manifest = tmp_path / "manifest.json"
    ledger = tmp_path / "ledger.json"
    run_script(
        "scripts/dev/build_day30_manifest.py",
        "--manifest",
        str(manifest),
        "--ledger",
        str(ledger),
    )
    first = manifest.read_text(encoding="utf-8")
    run_script(
        "scripts/dev/build_day30_manifest.py",
        "--manifest",
        str(manifest),
        "--ledger",
        str(ledger),
    )
    assert manifest.read_text(encoding="utf-8") == first
    document = json.loads(first)
    assert document["artifact_count"] >= 40
    assert all(
        not item["path"].startswith("day30_dual_dataset_harmonization_pack/")
        for item in document["artifacts"]
    )


def test_shell_runner_uses_portable_interpreter_resolution() -> None:
    runner = (ROOT / "scripts/dev/run_day30_checks.sh").read_text(
        encoding="utf-8"
    )
    assert "command -v python3" in runner
    assert 'run "$PYTHON_BIN"' in runner
    assert "stress_test_day30.py" in runner
    assert "--records 5000" in runner
    assert "DAY30_CHECKS_PASS" in runner


def test_requirement_traceability_targets_are_complete_and_resolvable() -> None:
    requirements_path = ROOT / "qa-validation/requirements/day30-requirements.csv"
    traceability_path = (
        ROOT / "qa-validation/traceability/day30-requirement-test-traceability.csv"
    )
    acceptance_path = ROOT / "qa-validation/requirements/day30-acceptance-criteria.md"

    with requirements_path.open(encoding="utf-8", newline="") as stream:
        requirement_ids = {row["requirement_id"] for row in csv.DictReader(stream)}
    with traceability_path.open(encoding="utf-8", newline="") as stream:
        trace_rows = list(csv.DictReader(stream))

    assert {row["requirement_id"] for row in trace_rows} == requirement_ids
    mapped_acceptance: set[str] = set()
    for row in trace_rows:
        mapped_acceptance.update(row["acceptance_criteria"].split(";"))
        targets = row["verification_targets"].split("|")
        assert targets
        for target in targets:
            relative_path, separator, symbol = target.partition("::")
            resolved = ROOT / relative_path
            assert resolved.is_file(), target
            if separator:
                content = resolved.read_text(encoding="utf-8")
                assert f"def {symbol}(" in content, target

    acceptance_ids = set(
        re.findall(r"AC-\d{2}", acceptance_path.read_text(encoding="utf-8"))
    )
    assert mapped_acceptance == acceptance_ids
