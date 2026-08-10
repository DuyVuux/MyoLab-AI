"""DAY15 safety-property harness for ingestion adapters.

This is test infrastructure, not a production MR4 parser. DAY16/DAY17 adapters should
bind their real parser outputs to ``SafetyObservation`` and reuse the assertions here.
"""
from __future__ import annotations

import csv
import hashlib
from dataclasses import dataclass
from enum import StrEnum
from io import StringIO
from pathlib import Path
from typing import Protocol

import yaml


class AdapterStatus(StrEnum):
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"


@dataclass(frozen=True)
class SafetyObservation:
    status: AdapterStatus
    reason_code: str | None
    final_looking_output: bool
    inferred_unit: str | None = None
    missing_values_preserved: bool | None = None
    unknown_fields_preserved: bool | None = None
    sampling_rates_hz: tuple[float, ...] = ()


class IngestionAdapter(Protocol):
    def ingest(self, path: Path) -> SafetyObservation: ...


@dataclass(frozen=True)
class PropertyCase:
    case_id: str
    path: Path
    fixture_class: str
    mutation: str | None
    expected_status: str
    expected_reason: str | None


class Day15ContractProbe:
    """Small test oracle proving the harness itself; never use as production parser."""

    known_units = {"s", "V", "uV", "N", "mm", "m/s", "N/cm^2", "FS"}

    def ingest(self, path: Path) -> SafetyObservation:
        try:
            if path.suffix.lower() == ".csv":
                return self._probe_csv(path)
            if path.suffix.lower() in {".yaml", ".yml"}:
                return self._probe_yaml(path)
            return self._reject("INGEST_SCHEMA_ERROR")
        except (UnicodeDecodeError, csv.Error, ValueError, TypeError, KeyError, yaml.YAMLError):
            return self._reject("INGEST_SCHEMA_ERROR")

    def _probe_csv(self, path: Path) -> SafetyObservation:
        raw = path.read_bytes()
        try:
            text = raw.decode("utf-8-sig")
        except UnicodeDecodeError:
            return self._reject("INGEST_SCHEMA_ERROR")
        rows = list(csv.reader(StringIO(text)))
        if len(rows) < 5 or not rows[0] or not rows[1]:
            return self._reject("INGEST_SCHEMA_ERROR")
        if len(rows[0]) != len(rows[1]):
            return self._reject("INGEST_SCHEMA_ERROR")
        if len(rows) < 4 or rows[2] != []:
            return self._reject("INGEST_SCHEMA_ERROR")
        if not rows[3] or rows[3][0] != "time":
            return self._reject("INGEST_SCHEMA_ERROR")
        try:
            count_index = rows[0].index("count")
            expected_count = int(rows[1][count_index])
        except (ValueError, IndexError):
            return self._reject("INGEST_SCHEMA_ERROR")
        data_rows = rows[4:]
        if expected_count != len(data_rows):
            return self._reject("COUNT_MISMATCH")
        timestamps: list[float] = []
        for row in data_rows:
            if not row:
                return self._reject("INGEST_SCHEMA_ERROR")
            timestamps.append(float(row[0]))
        if any(b <= a for a, b in zip(timestamps, timestamps[1:])):
            return self._reject("TIMESTAMP_INVALID")
        missing = any(cell == "" for row in data_rows for cell in row[1:])
        unknown_preserved = "future_vendor_field" in rows[0] or "FutureSensor-A" in rows[3]
        return SafetyObservation(
            status=AdapterStatus.ACCEPTED,
            reason_code=None,
            final_looking_output=False,
            missing_values_preserved=missing if missing else None,
            unknown_fields_preserved=unknown_preserved if unknown_preserved else None,
        )

    def _probe_yaml(self, path: Path) -> SafetyObservation:
        payload = yaml.safe_load(path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            return self._reject("INGEST_SCHEMA_ERROR")
        if "signals" in payload:
            frequencies: list[float] = []
            for signal in payload["signals"]:
                frequency = signal.get("metadata", {}).get("frequency")
                if not isinstance(frequency, (int, float)) or frequency <= 0:
                    return self._reject("INGEST_SCHEMA_ERROR")
                frequencies.append(float(frequency))
            return SafetyObservation(
                status=AdapterStatus.ACCEPTED,
                reason_code=None,
                final_looking_output=False,
                sampling_rates_hz=tuple(frequencies),
            )
        metadata = payload.get("metadata")
        columns = payload.get("columns")
        rows = payload.get("rows")
        if (
            not isinstance(metadata, dict)
            or not isinstance(columns, list)
            or not isinstance(rows, list)
        ):
            return self._reject("INGEST_SCHEMA_ERROR")
        signal_type = metadata.get("type")
        expected_columns = (
            ["time", "value"]
            if signal_type == "signal"
            else ["time", "x", "y"]
        )
        if signal_type not in {"signal", "signal_2d"} or columns != expected_columns:
            return self._reject("INGEST_SCHEMA_ERROR")
        if any(len(row) != len(expected_columns) for row in rows):
            return self._reject("INGEST_SCHEMA_ERROR")
        if metadata.get("count") != len(rows):
            return self._reject("COUNT_MISMATCH")
        unit = metadata.get("units")
        if unit not in self.known_units:
            return SafetyObservation(
                status=AdapterStatus.REJECTED,
                reason_code="UNIT_MISMATCH",
                final_looking_output=False,
                inferred_unit=None,
            )
        return SafetyObservation(
            status=AdapterStatus.ACCEPTED,
            reason_code=None,
            final_looking_output=False,
        )

    @staticmethod
    def _reject(reason: str) -> SafetyObservation:
        return SafetyObservation(
            status=AdapterStatus.REJECTED,
            reason_code=reason,
            final_looking_output=False,
        )


def sha256_file(path: Path) -> str:
    with path.open("rb") as file_obj:
        return hashlib.file_digest(file_obj, "sha256").hexdigest()


def assert_safety_properties(case: PropertyCase, adapter: IngestionAdapter) -> SafetyObservation:
    """Apply DAY15 invariants to one adapter/case pair."""
    before = sha256_file(case.path)
    try:
        observation = adapter.ingest(case.path)
    except Exception as exc:  # This is intentionally broad: any escape violates INV-003.
        raise AssertionError(
            f"NO_SILENT_CRASH violated for {case.case_id}: {type(exc).__name__}"
        ) from exc
    after = sha256_file(case.path)
    if before != after:
        raise AssertionError(f"RAW_IMMUTABLE violated for {case.case_id}")

    if case.fixture_class == "INVALID_MUST_FAIL_CLOSED":
        if observation.status is not AdapterStatus.REJECTED:
            raise AssertionError(f"FAIL_CLOSED violated for {case.case_id}")
        if observation.final_looking_output:
            raise AssertionError(f"final-looking output produced for {case.case_id}")
        if not observation.reason_code:
            raise AssertionError(f"typed reason missing for {case.case_id}")
        if case.expected_reason and observation.reason_code != case.expected_reason:
            raise AssertionError(
                f"reason mismatch for {case.case_id}: "
                f"{observation.reason_code} != {case.expected_reason}"
            )

    if case.mutation == "UNKNOWN_UNIT" and observation.inferred_unit is not None:
        raise AssertionError(f"UNKNOWN_UNIT_NEVER_INFERRED violated for {case.case_id}")

    if case.fixture_class in {"VALID_EDGE_MUST_ACCEPT", "GOLDEN_CONTROL"}:
        if observation.status is not AdapterStatus.ACCEPTED:
            raise AssertionError(f"valid edge falsely blocked: {case.case_id}")

    return observation
