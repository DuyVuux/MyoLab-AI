"""DAY50 deterministic Session Evidence Bundle builder."""
from __future__ import annotations
import hashlib, json
from typing import Any, Mapping, Sequence

def _canon(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()

def _bundle_id(body: Mapping[str, Any]) -> str:
    return "seb_sha256_" + hashlib.sha256(_canon(body)).hexdigest()

def _metric_status_guard(metric: Mapping[str, Any]) -> None:
    status = metric["status"]
    value = metric.get("value")
    reasons = metric.get("reason_codes", [])
    if status in {"NOT_AVAILABLE", "UNSUPPORTED"}:
        if value is not None or not reasons:
            raise ValueError("UNAVAILABLE_METRIC_MUST_BE_NULL_WITH_REASON")
    elif status in {"AVAILABLE", "RESEARCH_ONLY"} and value is None:
        raise ValueError("AVAILABLE_METRIC_REQUIRES_VALUE")

def _uncertainty_guard(u: Mapping[str, Any]) -> None:
    kind=u["uncertainty_type"]
    p=u.get("calibrated_probability")
    cset=u.get("conformal_set")
    ref=u.get("calibration_ref")
    level=u.get("rule_confidence_level")
    if kind == "RULE_CONFIDENCE":
        if p is not None or cset is not None or ref is not None or level is None:
            raise ValueError("RULE_CONFIDENCE_IS_NOT_PROBABILITY")
    elif kind == "NOT_APPLICABLE":
        if any(v is not None for v in (p,cset,ref,level)):
            raise ValueError("NOT_APPLICABLE_UNCERTAINTY_HAS_PAYLOAD")
    elif kind == "CALIBRATED_PROBABILITY":
        if u.get("calibration_status") != "CALIBRATED" or p is None or ref is None:
            raise ValueError("CALIBRATED_PROBABILITY_REQUIRES_CALIBRATION_EVIDENCE")
    elif kind == "CONFORMAL_SET":
        if u.get("calibration_status") != "CALIBRATED" or not cset or ref is None:
            raise ValueError("CONFORMAL_SET_REQUIRES_CALIBRATION_EVIDENCE")

def build_session_evidence_bundle(*, session_id: str, source_refs: Sequence[str], qc: Mapping[str, Any], processing: Mapping[str, Any], metrics: Sequence[Mapping[str, Any]], distribution_support: Mapping[str, Any], uncertainty: Mapping[str, Any], unsupported_capabilities: Sequence[Mapping[str, Any]], limitations: Sequence[str], event_correlation_id: str, evidence_refs: Sequence[str]) -> dict[str, Any]:
    if not source_refs or not evidence_refs:
        raise ValueError("PROVENANCE_REQUIRED")
    if processing.get("outcome") != "COMPLETED":
        raise ValueError("PROCESSING_MUST_BE_COMPLETED")
    manifest_id=processing.get("manifest_id")
    for metric in metrics:
        _metric_status_guard(metric)
        if metric.get("manifest_id") != manifest_id:
            raise ValueError("ORPHAN_METRIC_MANIFEST_REF")
    if distribution_support.get("score") is not None:
        raise ValueError("FAKE_OOD_SCORE_FORBIDDEN")
    _uncertainty_guard(uncertainty)
    body={"schema_version":"0.1","claim_scope":"RESEARCH_ONLY","session_id":session_id,"source_refs":sorted(set(source_refs)),"qc":dict(qc),"processing":dict(processing),"metrics":[dict(x) for x in metrics],"distribution_support":dict(distribution_support),"uncertainty":dict(uncertainty),"unsupported_capabilities":[dict(x) for x in unsupported_capabilities],"limitations":list(limitations),"event_correlation_id":event_correlation_id,"evidence_refs":sorted(set(evidence_refs))}
    return {"bundle_id":_bundle_id(body),**body}

def render_human_summary(bundle: Mapping[str, Any]) -> str:
    lines=[f"Session: {bundle['session_id']}",f"QC: {bundle['qc']['signal_quality']} / {bundle['qc']['supportability']}",f"Processing manifest: {bundle['processing']['manifest_id']}","Metrics:"]
    for m in bundle["metrics"]:
        value="null" if m["value"] is None else f"{m['value']} {m['units'] or ''}".strip()
        reasons=",".join(m["reason_codes"]) if m["reason_codes"] else "none"
        lines.append(f"- {m['metric_name']}: {m['status']} value={value} reasons={reasons}")
    lines.append(f"Distribution support: {bundle['distribution_support']['status']} ({bundle['distribution_support']['method_status']})")
    lines.append(f"Uncertainty: {bundle['uncertainty']['uncertainty_type']} probability={bundle['uncertainty']['calibrated_probability']}")
    lines.append("Limitations:")
    lines.extend(f"- {x}" for x in bundle["limitations"])
    return "\n".join(lines)+"\n"
