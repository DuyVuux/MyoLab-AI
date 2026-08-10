#!/usr/bin/env python3
"""DAY15 deterministic Noraxon fault-injection fixture factory.

This module creates SYNTHETIC fixtures only. It does not contain patient data and does
not implement the production MR4 parser scheduled for DAY16/DAY17.

The factory deliberately distinguishes two classes:
1. INVALID_MUST_FAIL_CLOSED: malformed inputs that a future parser must reject.
2. VALID_EDGE_MUST_ACCEPT: unusual-but-legal inputs (for example UTF-8 BOM and mixed
   per-signal sampling rates) that must not be falsely rejected.

Python 3.11+.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import random
from dataclasses import dataclass
from enum import StrEnum
from io import StringIO
from pathlib import Path
from typing import Iterable

import yaml

FACTORY_VERSION = "day15-noraxon-corruption-factory.v0.1.0"
DEFAULT_SEED = 1501
DEFAULT_PROPERTY_CASES = 64


class FactoryError(ValueError):
    """Typed error for invalid factory configuration or unsafe output paths."""


class FixtureClass(StrEnum):
    INVALID_MUST_FAIL_CLOSED = "INVALID_MUST_FAIL_CLOSED"
    VALID_EDGE_MUST_ACCEPT = "VALID_EDGE_MUST_ACCEPT"
    GOLDEN_CONTROL = "GOLDEN_CONTROL"


class Mutation(StrEnum):
    MALFORMED_HEADER = "MALFORMED_HEADER"
    COUNT_MISMATCH = "COUNT_MISMATCH"
    DUPLICATE_TIMESTAMP = "DUPLICATE_TIMESTAMP"
    OUT_OF_ORDER_TIMESTAMP = "OUT_OF_ORDER_TIMESTAMP"
    MISSING_ROW = "MISSING_ROW"
    UNKNOWN_UNIT = "UNKNOWN_UNIT"
    SIGNAL_2D_WRONG_SHAPE = "SIGNAL_2D_WRONG_SHAPE"
    BINARY_GARBAGE = "BINARY_GARBAGE"
    UTF8_BOM = "UTF8_BOM"
    MIXED_FS = "MIXED_FS"
    MISSING_VALUE_PRESERVED = "MISSING_VALUE_PRESERVED"
    UNKNOWN_FIELD_PRESERVED = "UNKNOWN_FIELD_PRESERVED"


@dataclass(frozen=True)
class FixtureRecord:
    fixture_id: str
    relative_path: str
    mutation: Mutation | None
    fixture_class: FixtureClass
    expected_status: str
    expected_reason: str | None
    sha256: str
    size_bytes: int
    representation_level: str
    clinical_evidence: bool = False
    site_verified: bool = False
    evidence_status: str = "SYNTHETIC"

    def to_dict(self) -> dict[str, object]:
        return {
            "fixture_id": self.fixture_id,
            "relative_path": self.relative_path,
            "mutation": self.mutation.value if self.mutation else None,
            "fixture_class": self.fixture_class.value,
            "expected_status": self.expected_status,
            "expected_reason": self.expected_reason,
            "sha256": self.sha256,
            "size_bytes": self.size_bytes,
            "representation_level": self.representation_level,
            "clinical_evidence": self.clinical_evidence,
            "site_verified": self.site_verified,
            "evidence_status": self.evidence_status,
        }


BASE_SINGLE_CSV = (
    "type,begin_time,frequency,count,created with version,exported with version,"
    "measurement_date,record_name\n"
    "record,0.00000,2000,3,Noraxon MR 4.0.22,4.0.22,"
    "2025-08-26T17:29:12.325+07:00,SYNTHETIC_DAY15\n"
    "\n"
    "time,Activity,Marker,LT BICEPS FEM.,RT BICEPS FEM.\n"
    "0.00000,REST,,12.5,11.7\n"
    "0.00050,,,13.1,12.2\n"
    "0.00100,,M1,12.8,12.0\n"
).encode("utf-8")

BASE_SIGNAL = {
    "fixture_id": "D15-SEED-SIGNAL-001",
    "data_class": "SYNTHETIC_CONTRACT_FIXTURE",
    "metadata": {
        "type": "signal",
        "name": "Ultium_EMG-LT_BICEPS_FEM.",
        "time_units": "s",
        "begin_time": "0.00000",
        "frequency": 2000,
        "count": 3,
        "units": "uV",
    },
    "columns": ["time", "value"],
    "rows": [[0.0, 12.5], [0.0005, 13.1], [0.001, 12.8]],
    "clinical_evidence": False,
}

BASE_SIGNAL_2D = {
    "fixture_id": "D15-SEED-SIGNAL2D-001",
    "data_class": "SYNTHETIC_CONTRACT_FIXTURE",
    "metadata": {
        "type": "signal_2d",
        "name": "Pressure_Platform-Contacts-Foot_LT-LT_COP",
        "time_units": "s",
        "begin_time": "0.00000",
        "frequency": 100,
        "count": 3,
        "units": "mm",
    },
    "columns": ["time", "x", "y"],
    "rows": [[0.0, 1.0, 2.0], [0.01, 1.2, 2.1], [0.02, 1.4, 2.3]],
    "clinical_evidence": False,
}

KNOWN_UNITS = {"s", "V", "uV", "N", "mm", "m/s", "N/cm^2", "FS"}


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: Path) -> str:
    with path.open("rb") as file_obj:
        return hashlib.file_digest(file_obj, "sha256").hexdigest()


def _csv_rows(payload: bytes) -> list[list[str]]:
    text = payload.decode("utf-8-sig")
    return list(csv.reader(StringIO(text)))


def _rows_to_bytes(rows: Iterable[Iterable[str]], *, bom: bool = False) -> bytes:
    buffer = StringIO(newline="")
    writer = csv.writer(buffer, lineterminator="\n")
    for row in rows:
        writer.writerow(list(row))
    data = buffer.getvalue().encode("utf-8")
    return (b"\xef\xbb\xbf" + data) if bom else data


def mutate_single_csv(source: bytes, mutation: Mutation, rng: random.Random) -> bytes:
    """Return mutated copies; source bytes are never modified in place."""
    if mutation is Mutation.BINARY_GARBAGE:
        return b"\x00\xff\x10DAY15\x80\x81"
    rows = _csv_rows(source)
    if len(rows) < 7:
        raise FactoryError("single-CSV seed must have at least seven rows")

    if mutation is Mutation.MALFORMED_HEADER:
        rows[0] = rows[0][:-1]
    elif mutation is Mutation.COUNT_MISMATCH:
        count_index = rows[0].index("count")
        rows[1][count_index] = str(int(rows[1][count_index]) + rng.choice([1, 2, 3]))
    elif mutation is Mutation.DUPLICATE_TIMESTAMP:
        rows[5][0] = rows[4][0]
    elif mutation is Mutation.OUT_OF_ORDER_TIMESTAMP:
        rows[5][0] = "-0.00050"
    elif mutation is Mutation.MISSING_ROW:
        rows.pop(5)
    elif mutation is Mutation.UTF8_BOM:
        return _rows_to_bytes(rows, bom=True)
    elif mutation is Mutation.MISSING_VALUE_PRESERVED:
        rows[5][3] = ""
    elif mutation is Mutation.UNKNOWN_FIELD_PRESERVED:
        rows[0].append("future_vendor_field")
        rows[1].append("opaque-value")
        rows[3].append("FutureSensor-A")
        for data_row in rows[4:]:
            data_row.append("7.1")
    else:
        raise FactoryError(f"mutation {mutation.value} is not a single-CSV mutation")
    return _rows_to_bytes(rows)


def build_logical_fixture(mutation: Mutation, rng: random.Random) -> dict[str, object]:
    if mutation is Mutation.UNKNOWN_UNIT:
        payload = json.loads(json.dumps(BASE_SIGNAL))
        payload["fixture_id"] = "D15-UNKNOWN-UNIT"
        payload["metadata"]["units"] = rng.choice(["mV?", "UNKNOWN_UNIT", "arb?"])
        return payload
    if mutation is Mutation.SIGNAL_2D_WRONG_SHAPE:
        payload = json.loads(json.dumps(BASE_SIGNAL_2D))
        payload["fixture_id"] = "D15-SIGNAL2D-WRONG-SHAPE"
        payload["columns"] = ["time", "value"]
        payload["rows"] = [[0.0, 1.0], [0.01, 1.2], [0.02, 1.4]]
        return payload
    if mutation is Mutation.MIXED_FS:
        emg = json.loads(json.dumps(BASE_SIGNAL))
        cop = json.loads(json.dumps(BASE_SIGNAL_2D))
        emg["metadata"]["frequency"] = rng.choice([1000, 2000, 4000])
        cop["metadata"]["frequency"] = rng.choice([50, 100, 200])
        if emg["metadata"]["frequency"] == cop["metadata"]["frequency"]:
            cop["metadata"]["frequency"] = 100
        return {
            "fixture_id": "D15-MIXED-FS",
            "data_class": "SYNTHETIC_CONTRACT_FIXTURE",
            "signals": [emg, cop],
            "clinical_evidence": False,
        }
    raise FactoryError(f"mutation {mutation.value} is not a logical-contract mutation")


def _fixed_specifications() -> list[tuple[Mutation | None, FixtureClass, str, str | None]]:
    return [
        (None, FixtureClass.GOLDEN_CONTROL, "ACCEPTED", None),
        (Mutation.MALFORMED_HEADER, FixtureClass.INVALID_MUST_FAIL_CLOSED,
         "REJECTED", "INGEST_SCHEMA_ERROR"),
        (Mutation.COUNT_MISMATCH, FixtureClass.INVALID_MUST_FAIL_CLOSED,
         "REJECTED", "COUNT_MISMATCH"),
        (Mutation.DUPLICATE_TIMESTAMP, FixtureClass.INVALID_MUST_FAIL_CLOSED,
         "REJECTED", "TIMESTAMP_INVALID"),
        (Mutation.OUT_OF_ORDER_TIMESTAMP, FixtureClass.INVALID_MUST_FAIL_CLOSED,
         "REJECTED", "TIMESTAMP_INVALID"),
        (Mutation.MISSING_ROW, FixtureClass.INVALID_MUST_FAIL_CLOSED,
         "REJECTED", "COUNT_MISMATCH"),
        (Mutation.UNKNOWN_UNIT, FixtureClass.INVALID_MUST_FAIL_CLOSED,
         "REJECTED", "UNIT_MISMATCH"),
        (Mutation.SIGNAL_2D_WRONG_SHAPE, FixtureClass.INVALID_MUST_FAIL_CLOSED,
         "REJECTED", "INGEST_SCHEMA_ERROR"),
        (Mutation.BINARY_GARBAGE, FixtureClass.INVALID_MUST_FAIL_CLOSED,
         "REJECTED", "INGEST_SCHEMA_ERROR"),
        (Mutation.UTF8_BOM, FixtureClass.VALID_EDGE_MUST_ACCEPT,
         "ACCEPTED", None),
        (Mutation.MIXED_FS, FixtureClass.VALID_EDGE_MUST_ACCEPT,
         "ACCEPTED", None),
        (Mutation.MISSING_VALUE_PRESERVED, FixtureClass.VALID_EDGE_MUST_ACCEPT,
         "ACCEPTED_WITH_MISSING_PRESERVED", None),
        (Mutation.UNKNOWN_FIELD_PRESERVED, FixtureClass.VALID_EDGE_MUST_ACCEPT,
         "ACCEPTED_WITH_UNKNOWN_PRESERVED", None),
    ]


def _safe_output_path(root: Path, relative_path: str) -> Path:
    path = (root / relative_path).resolve()
    root_resolved = root.resolve()
    if root_resolved not in [path, *path.parents]:
        raise FactoryError("output path escapes requested output directory")
    return path


def _write_bytes(root: Path, relative: str, payload: bytes, overwrite: bool) -> Path:
    path = _safe_output_path(root, relative)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and not overwrite:
        raise FactoryError(f"refusing to overwrite existing fixture: {path}")
    path.write_bytes(payload)
    return path


def _write_yaml(root: Path, relative: str, payload: dict[str, object], overwrite: bool) -> Path:
    text = yaml.safe_dump(payload, sort_keys=False, allow_unicode=True)
    return _write_bytes(root, relative, text.encode("utf-8"), overwrite)


def _record(
    root: Path,
    path: Path,
    fixture_id: str,
    mutation: Mutation | None,
    fixture_class: FixtureClass,
    expected_status: str,
    expected_reason: str | None,
    representation_level: str,
) -> FixtureRecord:
    return FixtureRecord(
        fixture_id=fixture_id,
        relative_path=path.relative_to(root).as_posix(),
        mutation=mutation,
        fixture_class=fixture_class,
        expected_status=expected_status,
        expected_reason=expected_reason,
        sha256=sha256_file(path),
        size_bytes=path.stat().st_size,
        representation_level=representation_level,
    )


def generate_fixed_fixtures(
    output_dir: Path,
    *,
    seed: int = DEFAULT_SEED,
    overwrite: bool = False,
    single_seed_path: Path | None = None,
) -> list[FixtureRecord]:
    """Generate fixed golden/adversarial/corrupted fixtures deterministically."""
    rng = random.Random(seed)
    source = single_seed_path.read_bytes() if single_seed_path else BASE_SINGLE_CSV
    source_hash_before = sha256_bytes(source)
    source_file_hash_before = sha256_file(single_seed_path) if single_seed_path else None
    records: list[FixtureRecord] = []

    for index, (mutation, fixture_class, status, reason) in enumerate(
        _fixed_specifications(), start=1
    ):
        fixture_id = f"D15-FIX-{index:03d}"
        if mutation is None:
            relative = "golden/base_single_control.csv"
            path = _write_bytes(output_dir, relative, bytes(source), overwrite)
            level = "BYTE_LEVEL_SINGLE_CSV"
        elif mutation in {
            Mutation.UNKNOWN_UNIT,
            Mutation.SIGNAL_2D_WRONG_SHAPE,
            Mutation.MIXED_FS,
        }:
            class_dir = (
                "corrupted"
                if fixture_class is FixtureClass.INVALID_MUST_FAIL_CLOSED
                else "golden"
            )
            relative = f"{class_dir}/{mutation.value.lower()}.yaml"
            payload = build_logical_fixture(mutation, rng)
            path = _write_yaml(output_dir, relative, payload, overwrite)
            level = "LOGICAL_CONTRACT_LEVEL_SEPARATED"
        else:
            class_dir = (
                "corrupted"
                if fixture_class is FixtureClass.INVALID_MUST_FAIL_CLOSED
                else "golden"
            )
            relative = f"{class_dir}/{mutation.value.lower()}.csv"
            payload = mutate_single_csv(source, mutation, rng)
            path = _write_bytes(output_dir, relative, payload, overwrite)
            level = "BYTE_LEVEL_SINGLE_CSV"
        records.append(
            _record(
                output_dir,
                path,
                fixture_id,
                mutation,
                fixture_class,
                status,
                reason,
                level,
            )
        )

    if sha256_bytes(source) != source_hash_before:
        raise FactoryError("factory mutated source bytes in memory")
    if single_seed_path and sha256_file(single_seed_path) != source_file_hash_before:
        raise FactoryError("factory mutated source seed file")
    return records


def generate_property_cases(*, seed: int, count: int) -> list[dict[str, object]]:
    """Generate constrained cases for dependency-light property testing."""
    if count < 1:
        raise FactoryError("property case count must be >= 1")
    rng = random.Random(seed)
    candidates = [
        Mutation.COUNT_MISMATCH,
        Mutation.DUPLICATE_TIMESTAMP,
        Mutation.OUT_OF_ORDER_TIMESTAMP,
        Mutation.UNKNOWN_UNIT,
        Mutation.SIGNAL_2D_WRONG_SHAPE,
        Mutation.BINARY_GARBAGE,
        Mutation.UTF8_BOM,
        Mutation.MIXED_FS,
        Mutation.MISSING_VALUE_PRESERVED,
        Mutation.UNKNOWN_FIELD_PRESERVED,
    ]
    result: list[dict[str, object]] = []
    invalid = {
        Mutation.COUNT_MISMATCH: "COUNT_MISMATCH",
        Mutation.DUPLICATE_TIMESTAMP: "TIMESTAMP_INVALID",
        Mutation.OUT_OF_ORDER_TIMESTAMP: "TIMESTAMP_INVALID",
        Mutation.UNKNOWN_UNIT: "UNIT_MISMATCH",
        Mutation.SIGNAL_2D_WRONG_SHAPE: "INGEST_SCHEMA_ERROR",
        Mutation.BINARY_GARBAGE: "INGEST_SCHEMA_ERROR",
    }
    for index in range(count):
        mutation = rng.choice(candidates)
        is_invalid = mutation in invalid
        result.append(
            {
                "case_id": f"D15-PROP-{index:04d}",
                "seed": seed,
                "mutation": mutation.value,
                "fixture_class": (
                    FixtureClass.INVALID_MUST_FAIL_CLOSED.value
                    if is_invalid
                    else FixtureClass.VALID_EDGE_MUST_ACCEPT.value
                ),
                "expected_status": "REJECTED" if is_invalid else "ACCEPTED",
                "expected_reason": invalid.get(mutation),
                "clinical_evidence": False,
                "site_verified": False,
                "evidence_status": "SYNTHETIC",
            }
        )
    return result


def build_package_fixture_set(
    output_dir: Path,
    *,
    seed: int = DEFAULT_SEED,
    property_cases: int = DEFAULT_PROPERTY_CASES,
    overwrite: bool = False,
    single_seed_path: Path | None = None,
) -> dict[str, object]:
    output_dir.mkdir(parents=True, exist_ok=True)
    fixed = generate_fixed_fixtures(
        output_dir,
        seed=seed,
        overwrite=overwrite,
        single_seed_path=single_seed_path,
    )
    property_payload = generate_property_cases(seed=seed, count=property_cases)
    property_path = _write_bytes(
        output_dir,
        "property-cases.jsonl",
        (
            "\n".join(
                json.dumps(item, sort_keys=True) for item in property_payload
            )
            + "\n"
        ).encode("utf-8"),
        overwrite,
    )
    manifest = {
        "schema_version": "1.0",
        "factory_version": FACTORY_VERSION,
        "seed": seed,
        "property_case_count": property_cases,
        "data_class": "SYNTHETIC_ONLY",
        "clinical_evidence": False,
        "site_verified": False,
        "production_parser_bound": False,
        "fixed_fixtures": [item.to_dict() for item in fixed],
        "property_cases_path": property_path.relative_to(output_dir).as_posix(),
        "property_cases_sha256": sha256_file(property_path),
    }
    manifest_path = _write_bytes(
        output_dir,
        "fixture-manifest.json",
        (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode("utf-8"),
        overwrite,
    )
    report = {
        "factory_version": FACTORY_VERSION,
        "status": "PASS",
        "fixed_fixture_count": len(fixed),
        "property_case_count": property_cases,
        "invalid_fixed_count": sum(
            item.fixture_class is FixtureClass.INVALID_MUST_FAIL_CLOSED for item in fixed
        ),
        "valid_edge_fixed_count": sum(
            item.fixture_class is FixtureClass.VALID_EDGE_MUST_ACCEPT for item in fixed
        ),
        "manifest_sha256": sha256_file(manifest_path),
        "raw_mutation_performed": False,
        "patient_data_used": False,
        "training_executed": False,
    }
    _write_bytes(
        output_dir,
        "generation-report.json",
        (json.dumps(report, indent=2, sort_keys=True) + "\n").encode("utf-8"),
        overwrite,
    )
    return manifest


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument("--property-cases", type=int, default=DEFAULT_PROPERTY_CASES)
    parser.add_argument("--single-seed", type=Path)
    parser.add_argument("--overwrite", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    manifest = build_package_fixture_set(
        args.output_dir,
        seed=args.seed,
        property_cases=args.property_cases,
        overwrite=args.overwrite,
        single_seed_path=args.single_seed,
    )
    print(
        json.dumps(
            {
                "status": "PASS",
                "factory_version": FACTORY_VERSION,
                "fixed_fixtures": len(manifest["fixed_fixtures"]),
                "property_cases": manifest["property_case_count"],
                "production_parser_bound": False,
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
