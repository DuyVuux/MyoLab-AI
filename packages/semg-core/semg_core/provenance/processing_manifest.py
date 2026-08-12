"""DAY45 raw-to-processed provenance and deterministic processing events.

The module records lineage; it does not implement DSP itself. It converges the
DAY11 immutable source identity, DAY19 event style, DAY40 profile contract and
DAY41-44 processors without mutating any upstream contract.

Safety properties:
- exact raw SourceRecord references remain content-addressed;
- processing run identity is deterministic from execution facts;
- step input/output hashes form an unbroken chain;
- mask lineage is explicit and sample-count preserving unless resampling is
  explicitly declared;
- failed processing cannot expose a processed-looking artifact;
- events contain references/reason codes, never waveform samples or file paths.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, fields, is_dataclass
from datetime import datetime, timezone
from enum import StrEnum
import hashlib
import json
import re
from typing import Any, Mapping, Protocol, Sequence

SCHEMA_VERSION = "0.1"
MANIFEST_CONTRACT_VERSION = "0.1.0"
HASH_ALGORITHM = "sha256"
SOURCE_ID_PATTERN = re.compile(r"^src_sha256_[0-9a-f]{64}$")
HEX64_PATTERN = re.compile(r"^[0-9a-f]{64}$")
PROFILE_FINGERPRINT_PATTERN = re.compile(
    r"^(?:pprof|precipe)_sha256_[0-9a-f]{64}$"
)


class ProcessingProvenanceError(ValueError):
    """Base typed error for malformed provenance."""


class BrokenLineageError(ProcessingProvenanceError):
    """Raised when a manifest cannot prove an unbroken hash lineage."""


class ProcessingOutcome(StrEnum):
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class ProcessingEventType(StrEnum):
    PROCESSING_STARTED = "PROCESSING_STARTED"
    PROCESSING_COMPLETED = "PROCESSING_COMPLETED"
    PROCESSING_FAILED = "PROCESSING_FAILED"
    REPROCESS_TRIGGERED = "REPROCESS_TRIGGERED"


@dataclass(frozen=True, slots=True)
class RawSourceRef:
    source_id: str
    sha256: str
    immutable_raw: bool = True


@dataclass(frozen=True, slots=True)
class WindowRef:
    window_id: str
    session_id: str
    channel_id: str
    start_sample: int
    end_sample_exclusive: int


@dataclass(frozen=True, slots=True)
class ProcessingProfileRef:
    profile_id: str
    version: str
    config_fingerprint: str
    claim_scope: str = "RESEARCH_ONLY"
    site_binding: None = None


@dataclass(frozen=True, slots=True)
class CodeComponentRef:
    component_id: str
    version: str
    artifact_sha256: str


@dataclass(frozen=True, slots=True)
class ProcessingStepRecord:
    sequence: int
    step_id: str
    processor: str
    processor_version: str
    method: str
    parameters: Mapping[str, Any]
    config_sha256: str
    input_sha256: str
    output_sha256: str
    input_mask_sha256: str
    output_mask_sha256: str
    status: str
    effect: Mapping[str, Any]
    reference_ids: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class ProcessedArtifactRef:
    artifact_id: str
    output_sha256: str
    mask_sha256: str
    sample_count: int
    units: str


@dataclass(frozen=True, slots=True)
class ProcessingManifest:
    schema_version: str
    manifest_contract_version: str
    manifest_id: str
    processing_run_id: str
    outcome: ProcessingOutcome
    correlation_id: str
    source: RawSourceRef
    window: WindowRef
    profile: ProcessingProfileRef
    code_components: tuple[CodeComponentRef, ...]
    input_sha256: str
    input_mask_sha256: str
    native_fs_hz: float
    processed_fs_hz: float | None
    input_units: str
    output_units: str | None
    is_resampled: bool
    partition: str
    evidence_tier: str
    qc_eligibility_ref: str
    normalization_eligibility_ref: str | None
    fitting_performed: bool
    steps: tuple[ProcessingStepRecord, ...]
    final_artifact: ProcessedArtifactRef | None
    reason_codes: tuple[str, ...]
    reprocess_of_run_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        payload = _to_plain(self)
        payload["outcome"] = self.outcome.value
        return payload


@dataclass(frozen=True, slots=True)
class ProcessingEvent:
    schema_version: str
    event_id: str
    event_type: ProcessingEventType
    processing_run_id: str
    processing_manifest_id: str | None
    manifest_contract_version: str
    correlation_id: str
    session_id: str
    source_refs: tuple[str, ...]
    profile_id: str
    profile_fingerprint: str
    emitted_at_utc: str
    outcome_status: str | None
    reason_code: str | None
    sequence: int
    reprocess_of_run_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        payload = _to_plain(self)
        payload["event_type"] = self.event_type.value
        return payload


class ProcessingEventSink(Protocol):
    def emit(self, event: ProcessingEvent) -> None: ...


class CollectingProcessingEventSink:
    """Test/reference sink only; persistent event storage belongs to DAY53."""

    def __init__(self) -> None:
        self.events: list[ProcessingEvent] = []
        self._ids: set[str] = set()

    def emit(self, event: ProcessingEvent) -> None:
        if event.event_id in self._ids:
            raise ProcessingProvenanceError("DUPLICATE_PROCESSING_EVENT_ID")
        _validate_event_privacy(event)
        self._ids.add(event.event_id)
        self.events.append(event)


def _to_plain(value: Any) -> Any:
    if isinstance(value, StrEnum):
        return value.value
    if is_dataclass(value):
        return {field.name: _to_plain(getattr(value, field.name)) for field in fields(value)}
    if isinstance(value, Mapping):
        return {str(key): _to_plain(item) for key, item in value.items()}
    if isinstance(value, tuple | list):
        return [_to_plain(item) for item in value]
    return value


def _canonical_json(value: Any) -> bytes:
    return json.dumps(
        _to_plain(value),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(_canonical_json(value)).hexdigest()


def _require_hex64(value: str, field_name: str) -> None:
    if HEX64_PATTERN.fullmatch(value) is None:
        raise ProcessingProvenanceError(f"{field_name}_MUST_BE_SHA256_HEX")


def _validate_source(source: RawSourceRef) -> None:
    _require_hex64(source.sha256, "SOURCE_SHA256")
    expected = f"src_sha256_{source.sha256}"
    if source.source_id != expected or SOURCE_ID_PATTERN.fullmatch(source.source_id) is None:
        raise BrokenLineageError("SOURCE_ID_HASH_MISMATCH")
    if source.immutable_raw is not True:
        raise BrokenLineageError("RAW_SOURCE_MUST_BE_IMMUTABLE")


def _validate_window(window: WindowRef) -> None:
    if not window.window_id or not window.session_id or not window.channel_id:
        raise ProcessingProvenanceError("WINDOW_IDENTITY_REQUIRED")
    if window.start_sample < 0 or window.end_sample_exclusive <= window.start_sample:
        raise ProcessingProvenanceError("WINDOW_SAMPLE_BOUNDS_INVALID")


def _validate_profile(profile: ProcessingProfileRef) -> None:
    if not profile.profile_id or not profile.version:
        raise ProcessingProvenanceError("PROFILE_ID_VERSION_REQUIRED")
    if PROFILE_FINGERPRINT_PATTERN.fullmatch(profile.config_fingerprint) is None:
        raise ProcessingProvenanceError("PROFILE_FINGERPRINT_INVALID")
    if profile.claim_scope != "RESEARCH_ONLY":
        raise ProcessingProvenanceError("DAY45_CLAIM_SCOPE_RESEARCH_ONLY")
    if profile.site_binding is not None:
        raise ProcessingProvenanceError("SITE_BINDING_NOT_VERIFIED")


def _code_bundle_payload(code_components: Sequence[CodeComponentRef]) -> list[dict[str, Any]]:
    items = sorted(code_components, key=lambda item: item.component_id)
    for component in items:
        _require_hex64(component.artifact_sha256, "CODE_ARTIFACT_SHA256")
        if not component.component_id or not component.version:
            raise ProcessingProvenanceError("CODE_COMPONENT_ID_VERSION_REQUIRED")
    return [_to_plain(item) for item in items]


def compute_processing_run_id(
    *,
    source: RawSourceRef,
    window: WindowRef,
    profile: ProcessingProfileRef,
    code_components: Sequence[CodeComponentRef],
    input_sha256: str,
    input_mask_sha256: str,
    native_fs_hz: float,
    input_units: str,
    partition: str,
    qc_eligibility_ref: str,
    normalization_eligibility_ref: str | None,
    reprocess_of_run_id: str | None = None,
) -> str:
    """Return content-addressed identity for an exact processing request."""

    _validate_source(source)
    _validate_window(window)
    _validate_profile(profile)
    _require_hex64(input_sha256, "INPUT_SHA256")
    _require_hex64(input_mask_sha256, "INPUT_MASK_SHA256")
    if native_fs_hz <= 0:
        raise ProcessingProvenanceError("NATIVE_FS_REQUIRED_POSITIVE")
    if not input_units:
        raise ProcessingProvenanceError("INPUT_UNITS_REQUIRED")
    if not qc_eligibility_ref:
        raise ProcessingProvenanceError("QC_ELIGIBILITY_REF_REQUIRED")
    if partition == "benchmark-locked" and normalization_eligibility_ref is not None:
        # A reference to a no-fitting eligibility decision is allowed. The run
        # identity itself does not authorize fitting; fitting_performed is later
        # required to be false for all locked runs.
        pass

    payload = {
        "source": _to_plain(source),
        "window": _to_plain(window),
        "profile": _to_plain(profile),
        "code_components": _code_bundle_payload(code_components),
        "input_sha256": input_sha256,
        "input_mask_sha256": input_mask_sha256,
        "native_fs_hz": float(native_fs_hz),
        "input_units": input_units,
        "partition": partition,
        "qc_eligibility_ref": qc_eligibility_ref,
        "normalization_eligibility_ref": normalization_eligibility_ref,
        "reprocess_of_run_id": reprocess_of_run_id,
    }
    return "prun_sha256_" + canonical_sha256(payload)


def _validate_step_chain(
    steps: Sequence[ProcessingStepRecord],
    *,
    initial_hash: str,
    initial_mask_hash: str,
) -> tuple[str, str]:
    current_hash = initial_hash
    current_mask_hash = initial_mask_hash
    expected_sequence = 0
    for step in steps:
        if step.sequence != expected_sequence:
            raise BrokenLineageError("PROCESSING_STEP_SEQUENCE_BROKEN")
        expected_sequence += 1
        if step.status != "COMPLETED":
            raise BrokenLineageError("MANIFEST_STEP_MUST_BE_COMPLETED")
        if step.input_sha256 != current_hash:
            raise BrokenLineageError("STEP_INPUT_HASH_DOES_NOT_MATCH_PREVIOUS_OUTPUT")
        if step.input_mask_sha256 != current_mask_hash:
            raise BrokenLineageError("STEP_INPUT_MASK_HASH_DOES_NOT_MATCH_PREVIOUS_MASK")
        for field_name, digest in (
            ("STEP_CONFIG_SHA256", step.config_sha256),
            ("STEP_INPUT_SHA256", step.input_sha256),
            ("STEP_OUTPUT_SHA256", step.output_sha256),
            ("STEP_INPUT_MASK_SHA256", step.input_mask_sha256),
            ("STEP_OUTPUT_MASK_SHA256", step.output_mask_sha256),
        ):
            _require_hex64(digest, field_name)
        if canonical_sha256(step.parameters) != step.config_sha256:
            raise BrokenLineageError("STEP_CONFIG_HASH_MISMATCH")
        if not step.step_id or not step.processor or not step.processor_version or not step.method:
            raise ProcessingProvenanceError("STEP_ID_PROCESSOR_METHOD_REQUIRED")
        current_hash = step.output_sha256
        current_mask_hash = step.output_mask_sha256
    return current_hash, current_mask_hash


def _semantic_manifest_payload(manifest: ProcessingManifest) -> dict[str, Any]:
    payload = manifest.to_dict()
    payload.pop("manifest_id", None)
    return payload


def _manifest_id(manifest: ProcessingManifest) -> str:
    return "pman_sha256_" + canonical_sha256(_semantic_manifest_payload(manifest))


def validate_processing_manifest(manifest: ProcessingManifest) -> None:
    _validate_source(manifest.source)
    _validate_window(manifest.window)
    _validate_profile(manifest.profile)
    _code_bundle_payload(manifest.code_components)
    _require_hex64(manifest.input_sha256, "INPUT_SHA256")
    _require_hex64(manifest.input_mask_sha256, "INPUT_MASK_SHA256")
    if manifest.schema_version != SCHEMA_VERSION:
        raise ProcessingProvenanceError("UNSUPPORTED_MANIFEST_SCHEMA_VERSION")
    if manifest.manifest_contract_version != MANIFEST_CONTRACT_VERSION:
        raise ProcessingProvenanceError("UNSUPPORTED_MANIFEST_CONTRACT_VERSION")
    if manifest.native_fs_hz <= 0:
        raise ProcessingProvenanceError("NATIVE_FS_REQUIRED_POSITIVE")
    if not manifest.input_units or not manifest.partition or not manifest.evidence_tier:
        raise ProcessingProvenanceError("PROCESSING_CONTEXT_REQUIRED")
    if not manifest.qc_eligibility_ref:
        raise ProcessingProvenanceError("QC_ELIGIBILITY_REF_REQUIRED")
    if manifest.fitting_performed:
        if manifest.partition == "benchmark-locked":
            raise BrokenLineageError("NO_LOCKED_SET_FITTING")
        raise BrokenLineageError("DAY45_PROCESSING_FITTING_NOT_AUTHORIZED")

    expected_run_id = compute_processing_run_id(
        source=manifest.source,
        window=manifest.window,
        profile=manifest.profile,
        code_components=manifest.code_components,
        input_sha256=manifest.input_sha256,
        input_mask_sha256=manifest.input_mask_sha256,
        native_fs_hz=manifest.native_fs_hz,
        input_units=manifest.input_units,
        partition=manifest.partition,
        qc_eligibility_ref=manifest.qc_eligibility_ref,
        normalization_eligibility_ref=manifest.normalization_eligibility_ref,
        reprocess_of_run_id=manifest.reprocess_of_run_id,
    )
    if manifest.processing_run_id != expected_run_id:
        raise BrokenLineageError("PROCESSING_RUN_ID_CONTENT_MISMATCH")

    if manifest.outcome is ProcessingOutcome.FAILED:
        if manifest.final_artifact is not None:
            raise BrokenLineageError("FAILED_PROCESSING_MUST_NOT_HAVE_ARTIFACT")
        if manifest.processed_fs_hz is not None or manifest.output_units is not None:
            raise BrokenLineageError("FAILED_PROCESSING_MUST_NOT_LOOK_PROCESSED")
        if not manifest.reason_codes:
            raise ProcessingProvenanceError("FAILED_PROCESSING_REASON_REQUIRED")
        if manifest.steps:
            raise BrokenLineageError("FAILED_MANIFEST_MUST_NOT_CLAIM_COMPLETED_STEPS")
    else:
        if manifest.final_artifact is None:
            raise BrokenLineageError("COMPLETED_PROCESSING_REQUIRES_ARTIFACT")
        if manifest.processed_fs_hz is None or manifest.processed_fs_hz <= 0:
            raise ProcessingProvenanceError("PROCESSED_FS_REQUIRED_ON_COMPLETION")
        if manifest.output_units is None:
            raise ProcessingProvenanceError("OUTPUT_UNITS_REQUIRED_ON_COMPLETION")
        if manifest.reason_codes:
            raise ProcessingProvenanceError("COMPLETED_PROCESSING_REASON_CODES_MUST_BE_EMPTY")
        final_hash, final_mask_hash = _validate_step_chain(
            manifest.steps,
            initial_hash=manifest.input_sha256,
            initial_mask_hash=manifest.input_mask_sha256,
        )
        artifact = manifest.final_artifact
        if final_hash != artifact.output_sha256:
            raise BrokenLineageError("FINAL_ARTIFACT_HASH_NOT_LAST_STEP_OUTPUT")
        if final_mask_hash != artifact.mask_sha256:
            raise BrokenLineageError("FINAL_ARTIFACT_MASK_NOT_LAST_STEP_MASK")
        _require_hex64(artifact.output_sha256, "FINAL_OUTPUT_SHA256")
        _require_hex64(artifact.mask_sha256, "FINAL_MASK_SHA256")
        if artifact.sample_count <= 0:
            raise ProcessingProvenanceError("FINAL_SAMPLE_COUNT_REQUIRED_POSITIVE")
        if not artifact.units:
            raise ProcessingProvenanceError("FINAL_UNITS_REQUIRED")
        expected_artifact_id = (
            "part_sha256_"
            + canonical_sha256(
                {
                    "processing_run_id": manifest.processing_run_id,
                    "output_sha256": artifact.output_sha256,
                    "mask_sha256": artifact.mask_sha256,
                    "sample_count": artifact.sample_count,
                    "units": artifact.units,
                }
            )
        )
        if artifact.artifact_id != expected_artifact_id:
            raise BrokenLineageError("PROCESSED_ARTIFACT_ID_CONTENT_MISMATCH")
        if manifest.is_resampled is False and manifest.processed_fs_hz != manifest.native_fs_hz:
            raise BrokenLineageError("GRID_CHANGED_WITHOUT_RESAMPLING_DECLARATION")

    if manifest.manifest_id != _manifest_id(manifest):
        raise BrokenLineageError("PROCESSING_MANIFEST_ID_CONTENT_MISMATCH")


def build_processing_manifest(
    *,
    outcome: ProcessingOutcome,
    correlation_id: str,
    source: RawSourceRef,
    window: WindowRef,
    profile: ProcessingProfileRef,
    code_components: Sequence[CodeComponentRef],
    input_sha256: str,
    input_mask_sha256: str,
    native_fs_hz: float,
    processed_fs_hz: float | None,
    input_units: str,
    output_units: str | None,
    is_resampled: bool,
    partition: str,
    evidence_tier: str,
    qc_eligibility_ref: str,
    normalization_eligibility_ref: str | None,
    steps: Sequence[ProcessingStepRecord],
    final_output_sha256: str | None,
    final_mask_sha256: str | None,
    final_sample_count: int | None,
    reason_codes: Sequence[str] = (),
    reprocess_of_run_id: str | None = None,
) -> ProcessingManifest:
    """Construct and validate a deterministic ProcessingManifest."""

    code_tuple = tuple(code_components)
    run_id = compute_processing_run_id(
        source=source,
        window=window,
        profile=profile,
        code_components=code_tuple,
        input_sha256=input_sha256,
        input_mask_sha256=input_mask_sha256,
        native_fs_hz=native_fs_hz,
        input_units=input_units,
        partition=partition,
        qc_eligibility_ref=qc_eligibility_ref,
        normalization_eligibility_ref=normalization_eligibility_ref,
        reprocess_of_run_id=reprocess_of_run_id,
    )

    artifact: ProcessedArtifactRef | None = None
    if outcome is ProcessingOutcome.COMPLETED:
        if final_output_sha256 is None or final_mask_sha256 is None or final_sample_count is None:
            raise ProcessingProvenanceError("COMPLETED_ARTIFACT_FIELDS_REQUIRED")
        _require_hex64(final_output_sha256, "FINAL_OUTPUT_SHA256")
        _require_hex64(final_mask_sha256, "FINAL_MASK_SHA256")
        if output_units is None:
            raise ProcessingProvenanceError("OUTPUT_UNITS_REQUIRED_ON_COMPLETION")
        artifact = ProcessedArtifactRef(
            artifact_id=(
                "part_sha256_"
                + canonical_sha256(
                    {
                        "processing_run_id": run_id,
                        "output_sha256": final_output_sha256,
                        "mask_sha256": final_mask_sha256,
                        "sample_count": int(final_sample_count),
                        "units": output_units,
                    }
                )
            ),
            output_sha256=final_output_sha256,
            mask_sha256=final_mask_sha256,
            sample_count=int(final_sample_count),
            units=output_units,
        )

    draft = ProcessingManifest(
        schema_version=SCHEMA_VERSION,
        manifest_contract_version=MANIFEST_CONTRACT_VERSION,
        manifest_id="PENDING",
        processing_run_id=run_id,
        outcome=outcome,
        correlation_id=correlation_id,
        source=source,
        window=window,
        profile=profile,
        code_components=code_tuple,
        input_sha256=input_sha256,
        input_mask_sha256=input_mask_sha256,
        native_fs_hz=float(native_fs_hz),
        processed_fs_hz=(float(processed_fs_hz) if processed_fs_hz is not None else None),
        input_units=input_units,
        output_units=output_units,
        is_resampled=bool(is_resampled),
        partition=partition,
        evidence_tier=evidence_tier,
        qc_eligibility_ref=qc_eligibility_ref,
        normalization_eligibility_ref=normalization_eligibility_ref,
        fitting_performed=False,
        steps=tuple(steps),
        final_artifact=artifact,
        reason_codes=tuple(sorted(set(reason_codes))),
        reprocess_of_run_id=reprocess_of_run_id,
    )
    manifest = ProcessingManifest(
        schema_version=draft.schema_version,
        manifest_contract_version=draft.manifest_contract_version,
        manifest_id=_manifest_id(draft),
        processing_run_id=draft.processing_run_id,
        outcome=draft.outcome,
        correlation_id=draft.correlation_id,
        source=draft.source,
        window=draft.window,
        profile=draft.profile,
        code_components=draft.code_components,
        input_sha256=draft.input_sha256,
        input_mask_sha256=draft.input_mask_sha256,
        native_fs_hz=draft.native_fs_hz,
        processed_fs_hz=draft.processed_fs_hz,
        input_units=draft.input_units,
        output_units=draft.output_units,
        is_resampled=draft.is_resampled,
        partition=draft.partition,
        evidence_tier=draft.evidence_tier,
        qc_eligibility_ref=draft.qc_eligibility_ref,
        normalization_eligibility_ref=draft.normalization_eligibility_ref,
        fitting_performed=draft.fitting_performed,
        steps=draft.steps,
        final_artifact=draft.final_artifact,
        reason_codes=draft.reason_codes,
        reprocess_of_run_id=draft.reprocess_of_run_id,
    )
    validate_processing_manifest(manifest)
    return manifest


def build_lineage_graph(manifest: ProcessingManifest) -> dict[str, Any]:
    validate_processing_manifest(manifest)
    nodes: list[dict[str, str]] = [
        {"id": manifest.source.source_id, "type": "RAW_SOURCE"},
        {"id": manifest.window.window_id, "type": "WINDOW"},
        {"id": manifest.processing_run_id, "type": "PROCESSING_RUN"},
    ]
    edges: list[dict[str, str]] = [
        {
            "from": manifest.source.source_id,
            "to": manifest.window.window_id,
            "relation": "CONTAINS",
        },
        {
            "from": manifest.window.window_id,
            "to": manifest.processing_run_id,
            "relation": "INPUT_TO",
        },
    ]
    previous = manifest.processing_run_id
    for step in manifest.steps:
        step_node = f"{manifest.processing_run_id}:step:{step.sequence}:{step.step_id}"
        nodes.append({"id": step_node, "type": "PROCESSING_STEP"})
        edges.append({"from": previous, "to": step_node, "relation": "NEXT"})
        previous = step_node
    if manifest.final_artifact is not None:
        nodes.append(
            {
                "id": manifest.final_artifact.artifact_id,
                "type": "PROCESSED_ARTIFACT",
            }
        )
        edges.append(
            {
                "from": previous,
                "to": manifest.final_artifact.artifact_id,
                "relation": "PRODUCES",
            }
        )
    return {
        "processing_run_id": manifest.processing_run_id,
        "nodes": nodes,
        "edges": edges,
    }


def _normalize_timestamp(value: datetime | None) -> str:
    timestamp = value or datetime.now(timezone.utc)
    if timestamp.tzinfo is None:
        raise ProcessingProvenanceError("EVENT_TIMESTAMP_MUST_BE_TIMEZONE_AWARE")
    return timestamp.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _event_id(
    processing_run_id: str,
    event_type: ProcessingEventType,
    sequence: int,
    correlation_id: str,
) -> str:
    return "pevt_sha256_" + canonical_sha256(
        {
            "processing_run_id": processing_run_id,
            "event_type": event_type.value,
            "sequence": sequence,
            "correlation_id": correlation_id,
        }
    )


def _validate_event_privacy(event: ProcessingEvent) -> None:
    payload = event.to_dict()
    forbidden = {
        "raw_payload",
        "waveform",
        "values",
        "source_path",
        "patient_name",
        "mrn",
        "clinical_note",
    }
    if forbidden.intersection(payload):
        raise ProcessingProvenanceError("PROCESSING_EVENT_FORBIDDEN_PAYLOAD_FIELD")
    for source_ref in event.source_refs:
        if SOURCE_ID_PATTERN.fullmatch(source_ref) is None:
            raise ProcessingProvenanceError("EVENT_SOURCE_REF_MUST_BE_SOURCE_ID")


def build_processing_event(
    *,
    event_type: ProcessingEventType,
    processing_run_id: str,
    correlation_id: str,
    session_id: str,
    source_refs: Sequence[str],
    profile: ProcessingProfileRef,
    sequence: int,
    manifest_id: str | None = None,
    outcome_status: str | None = None,
    reason_code: str | None = None,
    emitted_at: datetime | None = None,
    reprocess_of_run_id: str | None = None,
) -> ProcessingEvent:
    if not processing_run_id.startswith("prun_sha256_"):
        raise ProcessingProvenanceError("PROCESSING_RUN_ID_REQUIRED")
    if not correlation_id or not session_id:
        raise ProcessingProvenanceError("EVENT_CORRELATION_SESSION_REQUIRED")
    if sequence < 0:
        raise ProcessingProvenanceError("EVENT_SEQUENCE_INVALID")
    if event_type is ProcessingEventType.PROCESSING_STARTED:
        if manifest_id is not None or outcome_status is not None or reason_code is not None:
            raise ProcessingProvenanceError("STARTED_EVENT_MUST_NOT_LOOK_TERMINAL")
    elif event_type is ProcessingEventType.PROCESSING_COMPLETED:
        if manifest_id is None or outcome_status != ProcessingOutcome.COMPLETED.value:
            raise ProcessingProvenanceError("COMPLETED_EVENT_REQUIRES_COMPLETED_MANIFEST")
        if reason_code is not None:
            raise ProcessingProvenanceError("COMPLETED_EVENT_REASON_MUST_BE_NULL")
    elif event_type is ProcessingEventType.PROCESSING_FAILED:
        if (
            manifest_id is None
            or outcome_status != ProcessingOutcome.FAILED.value
            or not reason_code
        ):
            raise ProcessingProvenanceError("FAILED_EVENT_REQUIRES_FAILED_MANIFEST_REASON")
    elif event_type is ProcessingEventType.REPROCESS_TRIGGERED:
        if reprocess_of_run_id is None:
            raise ProcessingProvenanceError("REPROCESS_EVENT_REQUIRES_PARENT_RUN")
        if outcome_status is not None:
            raise ProcessingProvenanceError("REPROCESS_TRIGGER_IS_NOT_TERMINAL")

    event = ProcessingEvent(
        schema_version=SCHEMA_VERSION,
        event_id=_event_id(processing_run_id, event_type, sequence, correlation_id),
        event_type=event_type,
        processing_run_id=processing_run_id,
        processing_manifest_id=manifest_id,
        manifest_contract_version=MANIFEST_CONTRACT_VERSION,
        correlation_id=correlation_id,
        session_id=session_id,
        source_refs=tuple(source_refs),
        profile_id=profile.profile_id,
        profile_fingerprint=profile.config_fingerprint,
        emitted_at_utc=_normalize_timestamp(emitted_at),
        outcome_status=outcome_status,
        reason_code=reason_code,
        sequence=sequence,
        reprocess_of_run_id=reprocess_of_run_id,
    )
    _validate_event_privacy(event)
    return event
