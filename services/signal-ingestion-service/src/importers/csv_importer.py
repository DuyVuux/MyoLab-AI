"""Generic CSV + sidecar manifest importer, version 0.1."""

from __future__ import annotations

from pathlib import Path

from semg_core.io import NormalizedSignal
from semg_core.validation import (
    ValidationIssue,
    has_blocking_issues,
    validate_normalized_signal,
    validate_time_axis,
)

from importers.base_importer import ImportResult, SignalImporter
from normalizers.channel_mapper import build_normalized_channel
from normalizers.metadata_extractor import extract_session_metadata
from validators.file_format_validator import parse_generic_csv
from validators.metadata_validator import load_manifest, validate_manifest


class CSVImporter(SignalImporter):
    """Import Generic CSV v0.1 into a canonical, unit-normalized object."""

    def __init__(self, *, sampling_rate_relative_tolerance: float = 0.01) -> None:
        if sampling_rate_relative_tolerance <= 0:
            raise ValueError("sampling_rate_relative_tolerance must be positive")
        self._sampling_rate_relative_tolerance = sampling_rate_relative_tolerance

    def import_session(self, manifest_path: Path) -> ImportResult:
        manifest_path = Path(manifest_path)
        manifest, issues = load_manifest(manifest_path)
        if manifest is None:
            return ImportResult(signal=None, issues=tuple(issues))

        issues.extend(validate_manifest(manifest))
        if has_blocking_issues(issues):
            return ImportResult(signal=None, issues=tuple(issues))

        try:
            metadata = extract_session_metadata(manifest)
        except (KeyError, TypeError, ValueError) as exc:
            issues.append(
                ValidationIssue(
                    "REQUIRED_METADATA_MISSING",
                    f"Manifest could not be converted to typed metadata: {exc}",
                )
            )
            return ImportResult(signal=None, issues=tuple(issues))

        parsed, parse_issues = parse_generic_csv(
            metadata.resolve_signal_path(manifest_path),
            time_column=metadata.time_column,
            channel_columns=[spec.column for spec in metadata.channels],
        )
        issues.extend(parse_issues)
        if parsed is None or has_blocking_issues(issues):
            return ImportResult(signal=None, issues=tuple(issues))

        if (
            metadata.declared_source_hash_sha256 is not None
            and metadata.declared_source_hash_sha256 != parsed.source_hash_sha256
        ):
            issues.append(
                ValidationIssue(
                    "SOURCE_HASH_MISMATCH",
                    (
                        f"Declared hash {metadata.declared_source_hash_sha256} does not "
                        f"match computed hash {parsed.source_hash_sha256}"
                    ),
                )
            )
            return ImportResult(signal=None, issues=tuple(issues))

        issues.extend(
            validate_time_axis(
                parsed.time_s,
                metadata.sampling_rate_hz,
                relative_tolerance=self._sampling_rate_relative_tolerance,
            )
        )
        if has_blocking_issues(issues):
            return ImportResult(signal=None, issues=tuple(issues))

        try:
            normalized_channels = {
                spec.channel_id: build_normalized_channel(
                    spec,
                    parsed.channels[spec.column],
                )
                for spec in metadata.channels
            }
        except (KeyError, ValueError) as exc:
            issues.append(ValidationIssue("CHANNEL_NORMALIZATION_FAILED", str(exc)))
            return ImportResult(signal=None, issues=tuple(issues))

        try:
            normalized = NormalizedSignal(
                session_id=metadata.session_id,
                sampling_rate_hz=metadata.sampling_rate_hz,
                time_s=parsed.time_s,
                channels=normalized_channels,
                protocol_ref=metadata.protocol_ref,
                phase_markers=metadata.phase_markers,
                data_source=metadata.data_source,
                source_file_name=metadata.signal_file,
                source_hash_sha256=parsed.source_hash_sha256,
                processing_history=metadata.processing_history,
                source_manifest=metadata.raw_manifest,
            )
        except (TypeError, ValueError) as exc:
            issues.append(ValidationIssue("NORMALIZED_OBJECT_INVALID", str(exc)))
            return ImportResult(signal=None, issues=tuple(issues))

        issues.extend(validate_normalized_signal(normalized))
        if has_blocking_issues(issues):
            return ImportResult(signal=None, issues=tuple(issues))
        return ImportResult(signal=normalized, issues=tuple(issues))
