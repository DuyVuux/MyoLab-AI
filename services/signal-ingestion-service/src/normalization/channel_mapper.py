"""DAY14 vendor-to-canonical channel mapping and metadata completeness.

Safety boundary
---------------
This module performs deterministic, versioned, exact mapping only. It does not
perform fuzzy matching, infer anatomy from a vendor label, calculate OOD scores,
or claim that a channel layout is clinically/site verified.
"""
from __future__ import annotations

import hashlib
import json
from enum import StrEnum
from pathlib import Path
from typing import Any, Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field, model_validator


class MappingStatus(StrEnum):
    MAPPED = "MAPPED"
    UNMAPPED = "UNMAPPED"


class CompletenessStatus(StrEnum):
    PASS = "PASS"
    WARNING = "WARNING"
    FAIL = "FAIL"


class EvidenceStatus(StrEnum):
    VERIFIED = "VERIFIED"
    DOCUMENTED = "DOCUMENTED"
    NOT_VERIFIED = "NOT_VERIFIED"
    UNKNOWN = "UNKNOWN"


class MetadataFinding(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    field_name: str
    status: CompletenessStatus
    reason_code: str
    observed_present: bool


class MetadataCompletenessResult(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    profile_id: str
    policy_id: str
    policy_version: str
    status: CompletenessStatus
    findings: tuple[MetadataFinding, ...]


class ChannelMappingResult(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    vendor_signal_name_raw: str
    mapping_status: MappingStatus
    canonical_muscle_id: str | None = None
    side: Literal["LEFT", "RIGHT", "BILATERAL", "MIDLINE", "UNKNOWN"] = "UNKNOWN"
    signal_role: str | None = None
    ontology_id: str
    ontology_version: str
    mapping_version: str
    evidence_status: EvidenceStatus
    reason_code: str
    mapping_result_id: str


class ChannelLayoutContext(BaseModel):
    """Metadata-only layout context for later distribution/OOD support analysis."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    schema_version: Literal["channel-layout-context.v0.1"] = "channel-layout-context.v0.1"
    layout_id: str | None = None
    mapping_version: str
    channel_count: int | None = Field(default=None, ge=1)
    geometry_status: EvidenceStatus = EvidenceStatus.UNKNOWN
    placement_status: EvidenceStatus = EvidenceStatus.UNKNOWN
    electrode_model: str | None = None
    inter_electrode_distance_mm: float | None = Field(default=None, gt=0)
    orientation_description: str | None = None
    evidence_refs: tuple[str, ...] = ()
    readiness_level: Literal["METADATA_CONTRACT_ONLY"] = "METADATA_CONTRACT_ONLY"

    @model_validator(mode="after")
    def verified_states_require_evidence(self) -> "ChannelLayoutContext":
        if (
            self.geometry_status == EvidenceStatus.VERIFIED
            or self.placement_status == EvidenceStatus.VERIFIED
        ) and not self.evidence_refs:
            raise ValueError("VERIFIED geometry/placement requires evidence_refs")
        return self


def _canonical_json(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def _stable_id(prefix: str, value: Any) -> str:
    digest = hashlib.sha256(_canonical_json(value)).hexdigest()
    return f"{prefix}_{digest}"


def load_ontology(path: Path) -> dict[str, Any]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("Ontology must be a mapping")

    required = {
        "ontology_id",
        "version",
        "mapping_version",
        "canonical_muscles",
        "vendor_mappings",
    }
    missing = sorted(required - payload.keys())
    if missing:
        raise ValueError(f"Ontology missing fields: {missing}")

    muscles = payload["canonical_muscles"]
    mappings = payload["vendor_mappings"]
    if not isinstance(muscles, list) or not isinstance(mappings, list):
        raise ValueError("canonical_muscles and vendor_mappings must be lists")

    muscle_ids = [item.get("muscle_id") for item in muscles]
    if any(not value for value in muscle_ids) or len(set(muscle_ids)) != len(muscle_ids):
        raise ValueError("Canonical muscle IDs must be present and unique")

    aliases: set[str] = set()
    for item in mappings:
        if item.get("match_mode") != "EXACT":
            raise ValueError("DAY14 v0.1 only allows EXACT vendor mapping")
        alias = item.get("vendor_signal_name")
        if not isinstance(alias, str) or not alias:
            raise ValueError("vendor_signal_name must be a non-empty string")
        if alias in aliases:
            raise ValueError(f"Duplicate vendor alias: {alias}")
        aliases.add(alias)
        if item.get("canonical_muscle_id") not in set(muscle_ids):
            raise ValueError("Mapping references unknown canonical muscle")
        if item.get("side") not in {"LEFT", "RIGHT", "BILATERAL", "MIDLINE", "UNKNOWN"}:
            raise ValueError("Invalid side")
        if item.get("evidence_status") not in {e.value for e in EvidenceStatus}:
            raise ValueError("Invalid evidence_status")

    return payload


def map_vendor_signal(vendor_signal_name: str, ontology: dict[str, Any]) -> ChannelMappingResult:
    """Map only an exact approved alias; preserve the original vendor text."""
    candidates = [
        item
        for item in ontology["vendor_mappings"]
        if item["vendor_signal_name"] == vendor_signal_name
    ]

    if not candidates:
        body = {
            "vendor_signal_name_raw": vendor_signal_name,
            "mapping_status": MappingStatus.UNMAPPED.value,
            "ontology_id": ontology["ontology_id"],
            "ontology_version": ontology["version"],
            "mapping_version": ontology["mapping_version"],
        }
        return ChannelMappingResult(
            vendor_signal_name_raw=vendor_signal_name,
            mapping_status=MappingStatus.UNMAPPED,
            ontology_id=ontology["ontology_id"],
            ontology_version=ontology["version"],
            mapping_version=ontology["mapping_version"],
            evidence_status=EvidenceStatus.UNKNOWN,
            reason_code="VENDOR_ALIAS_NOT_IN_APPROVED_MAPPING",
            mapping_result_id=_stable_id("map", body),
        )

    item = candidates[0]
    body = {
        "vendor_signal_name_raw": vendor_signal_name,
        "mapping_status": MappingStatus.MAPPED.value,
        "canonical_muscle_id": item["canonical_muscle_id"],
        "side": item["side"],
        "signal_role": item["signal_role"],
        "ontology_id": ontology["ontology_id"],
        "ontology_version": ontology["version"],
        "mapping_version": ontology["mapping_version"],
        "evidence_status": item["evidence_status"],
    }
    return ChannelMappingResult(
        vendor_signal_name_raw=vendor_signal_name,
        mapping_status=MappingStatus.MAPPED,
        canonical_muscle_id=item["canonical_muscle_id"],
        side=item["side"],
        signal_role=item["signal_role"],
        ontology_id=ontology["ontology_id"],
        ontology_version=ontology["version"],
        mapping_version=ontology["mapping_version"],
        evidence_status=EvidenceStatus(item["evidence_status"]),
        reason_code="EXACT_APPROVED_VENDOR_ALIAS",
        mapping_result_id=_stable_id("map", body),
    )


def load_metadata_policy(path: Path) -> dict[str, Any]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("Metadata policy must be a mapping")
    for field in ("policy_id", "version", "profiles"):
        if field not in payload:
            raise ValueError(f"Metadata policy missing {field}")
    if not isinstance(payload["profiles"], dict) or not payload["profiles"]:
        raise ValueError("Metadata policy profiles must be non-empty")

    allowed = {"OPTIONAL", "WARNING_IF_MISSING", "FAIL_IF_MISSING"}
    for profile in payload["profiles"].values():
        if "fields" not in profile or not isinstance(profile["fields"], dict):
            raise ValueError("Every metadata profile needs fields")
        for field_cfg in profile["fields"].values():
            if field_cfg.get("requirement") not in allowed:
                raise ValueError("Invalid metadata requirement")
    return payload


def evaluate_metadata(
    metadata: dict[str, Any],
    profile_id: str,
    policy: dict[str, Any],
) -> MetadataCompletenessResult:
    """Evaluate presence only; never fill or infer missing metadata."""
    try:
        profile = policy["profiles"][profile_id]
    except KeyError as exc:
        raise ValueError(f"Unknown metadata profile: {profile_id}") from exc

    findings: list[MetadataFinding] = []
    for field_name, rule in profile["fields"].items():
        present = field_name in metadata and metadata[field_name] not in (None, "")
        requirement = rule["requirement"]
        if present or requirement == "OPTIONAL":
            status = CompletenessStatus.PASS
            reason = "PRESENT_OR_OPTIONAL"
        elif requirement == "WARNING_IF_MISSING":
            status = CompletenessStatus.WARNING
            reason = "METADATA_MISSING_WARNING"
        else:
            status = CompletenessStatus.FAIL
            reason = "METADATA_MISSING_REQUIRED"
        findings.append(
            MetadataFinding(
                field_name=field_name,
                status=status,
                reason_code=reason,
                observed_present=present,
            )
        )

    statuses = {item.status for item in findings}
    if CompletenessStatus.FAIL in statuses:
        overall = CompletenessStatus.FAIL
    elif CompletenessStatus.WARNING in statuses:
        overall = CompletenessStatus.WARNING
    else:
        overall = CompletenessStatus.PASS

    return MetadataCompletenessResult(
        profile_id=profile_id,
        policy_id=policy["policy_id"],
        policy_version=policy["version"],
        status=overall,
        findings=tuple(findings),
    )


def build_layout_context(
    explicit_metadata: dict[str, Any],
    mapping_version: str,
) -> ChannelLayoutContext:
    """Build a layout context from explicit facts only; never infer layout identity."""
    if "layout_id" not in explicit_metadata:
        explicit_metadata = {**explicit_metadata, "layout_id": None}
    return ChannelLayoutContext(mapping_version=mapping_version, **explicit_metadata)
