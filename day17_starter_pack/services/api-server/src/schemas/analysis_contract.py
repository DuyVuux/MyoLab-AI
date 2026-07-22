"""Canonical API-facing analysis summary v0.1.

Module chỉ chuyển đổi offline package đã kiểm chứng thành summary ổn định cho
API/UI/report. Không thực hiện lại DSP hoặc inference.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


Conclusion = Literal["supported_pattern", "no_supported_pattern", "inconclusive", "abstained"]
AnalysisStatus = Literal["completed", "completed_with_warnings", "abstained", "blocked_by_wording_guard"]


def canonical_hash(payload: Any) -> str:
    encoded = json.dumps(payload, sort_keys=True, ensure_ascii=False, allow_nan=False, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class SignalQualitySummary(StrictModel):
    status: Literal["pass", "warning", "fail", "import_rejected"]
    analysis_allowed: bool
    reason_codes: list[str]
    mfcv_eligible: bool
    mfcv_reason_codes: list[str]


class TrendSummary(StrictModel):
    feature_name: Literal["rms", "mav", "mdf", "mnf"]
    source_profile_id: Literal["time_domain", "frequency_domain"]
    slope_per_min: float
    slope_unit: str
    percent_change: float
    r_squared: float = Field(ge=0.0, le=1.0)


class ChannelSummary(StrictModel):
    channel_id: str
    muscle: str
    side: str
    role: str
    phase_id: str
    trends: list[TrendSummary]
    evidence_pattern: str | None
    technical_conclusion: Conclusion | None


class ConfidenceSummary(StrictModel):
    final_score_0_to_1: float | None = Field(default=None, ge=0.0, le=1.0)
    category: Literal["engineering_high", "engineering_moderate", "engineering_low", "engineering_very_low", "not_available"]
    score_is_probability: Literal[False] = False
    clinical_calibration_status: Literal["not_calibrated"] = "not_calibrated"

    @model_validator(mode="after")
    def check_abstained(self):
        if self.category == "not_available" and self.final_score_0_to_1 is not None:
            raise ValueError("not_available phải có score=null")
        return self


class ExplainabilitySummary(StrictModel):
    summary_vi: str
    decision_basis: list[dict[str, Any]]
    counterevidence: list[dict[str, Any]]
    wording_guard_status: Literal["passed", "failed"]


class SafetySummary(StrictModel):
    clinical_use_allowed: Literal[False] = False
    human_review_required: Literal[True] = True
    is_diagnosis: Literal[False] = False
    is_treatment_recommendation: Literal[False] = False
    is_return_to_play_decision: Literal[False] = False
    synthetic_data_is_clinical_evidence: Literal[False] = False


class ProvenanceSummary(StrictModel):
    analysis_fingerprint_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    source_hash_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    pipeline_config_id: str
    config_hashes: dict[str, str]


class SessionAnalysisSummary(StrictModel):
    schema_version: Literal["session-analysis-summary.v0.1"]
    analysis_id: str
    session_id: str
    status: AnalysisStatus
    technical_conclusion: Conclusion
    signal_quality: SignalQualitySummary
    channels: list[ChannelSummary]
    confidence: ConfidenceSummary
    explainability: ExplainabilitySummary
    provenance: ProvenanceSummary
    safety: SafetySummary
    limitations: list[str]
    links: dict[str, str]
    summary_hash_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")

    @model_validator(mode="after")
    def check_abstention(self):
        if self.status == "abstained":
            if self.technical_conclusion != "abstained":
                raise ValueError("status abstained phải conclusion abstained")
            if self.confidence.category != "not_available":
                raise ValueError("abstained phải confidence not_available")
        return self


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_session_analysis_summary(analysis_dir: Path, *, base_url: str = "/v1") -> SessionAnalysisSummary:
    manifest = _load(analysis_dir / "11-analysis-manifest.json")
    qc = _load(analysis_dir / "01-qc-result.json")
    trends = _load(analysis_dir / "07-trend-features.json")
    evidence = _load(analysis_dir / "08-fatigue-evidence.json")
    rule = _load(analysis_dir / "09-fatigue-rule.json")
    inference = _load(analysis_dir / "10-explainable-inference.json")

    evidence_by_channel = {
        item["channel"]["channel_id"]: item for item in evidence.get("channels", [])
    }
    rule_by_channel = {
        item["channel"]["channel_id"]: item for item in rule.get("channels", [])
    }
    channels: list[ChannelSummary] = []
    for item in trends.get("channels", []):
        if item.get("status") != "computed":
            continue
        channel = item["channel"]
        trend_items: list[TrendSummary] = []
        for feature_name, record in item.get("trends", {}).items():
            if record.get("status") != "computed" or not record.get("metrics"):
                continue
            metrics = record["metrics"]
            trend_items.append(TrendSummary(
                feature_name=feature_name,
                source_profile_id=record["source_profile_id"],
                slope_per_min=float(metrics["linear_fit"]["slope_per_min"]["value"]),
                slope_unit=str(metrics["linear_fit"]["slope_per_min"]["unit"]),
                percent_change=float(metrics["early_late_summary"]["percent_change"]["value"]),
                r_squared=float(metrics["linear_fit"]["r_squared"]),
            ))
        ev = evidence_by_channel.get(channel["channel_id"])
        rl = rule_by_channel.get(channel["channel_id"])
        channels.append(ChannelSummary(
            channel_id=channel["channel_id"], muscle=channel["muscle"], side=channel["side"], role=channel["role"],
            phase_id=item["phase_id"], trends=trend_items,
            evidence_pattern=ev.get("pattern_category") if ev else None,
            technical_conclusion=rl.get("technical_conclusion") if rl else None,
        ))

    confidence_payload = inference["technical_confidence"]
    explain = inference["explainability"]
    analysis_id = str(manifest["analysis_id"])
    payload_without_hash = {
        "schema_version": "session-analysis-summary.v0.1",
        "analysis_id": analysis_id,
        "session_id": str(manifest["session_id"]),
        "status": str(manifest["status"]),
        "technical_conclusion": str(manifest["final"]["technical_conclusion"]),
        "signal_quality": {
            "status": str(qc["status"]),
            "analysis_allowed": bool(qc.get("analysis_allowed", False)),
            "reason_codes": list(qc.get("reason_codes", [])),
            "mfcv_eligible": bool(qc.get("mfcv", {}).get("eligible", False)),
            "mfcv_reason_codes": list(qc.get("mfcv", {}).get("reason_codes", [])),
        },
        "channels": [x.model_dump(mode="json") for x in channels],
        "confidence": {
            "final_score_0_to_1": confidence_payload.get("final_score_0_to_1"),
            "category": confidence_payload["category"],
            "score_is_probability": False,
            "clinical_calibration_status": "not_calibrated",
        },
        "explainability": {
            "summary_vi": explain["summary_vi"],
            "decision_basis": list(explain.get("decision_basis", [])),
            "counterevidence": list(explain.get("counterevidence", [])),
            "wording_guard_status": str(explain["wording_guard"]["status"]),
        },
        "provenance": {
            "analysis_fingerprint_sha256": manifest["analysis_fingerprint_sha256"],
            "source_hash_sha256": manifest["source"]["source_hash_sha256"],
            "pipeline_config_id": manifest["pipeline"]["config_id"],
            "config_hashes": dict(manifest["pipeline"]["config_hashes"]),
        },
        "safety": {
            "clinical_use_allowed": False,
            "human_review_required": True,
            "is_diagnosis": False,
            "is_treatment_recommendation": False,
            "is_return_to_play_decision": False,
            "synthetic_data_is_clinical_evidence": False,
        },
        "limitations": list(dict.fromkeys(list(manifest.get("limitations", [])) + list(inference.get("limitations", [])))),
        "links": {
            "self": f"{base_url}/analyses/{analysis_id}/summary",
            "analysis": f"{base_url}/analyses/{analysis_id}",
            "manifest": f"{base_url}/analyses/{analysis_id}/manifest",
        },
    }
    payload_without_hash["summary_hash_sha256"] = canonical_hash(payload_without_hash)
    return SessionAnalysisSummary.model_validate(payload_without_hash)
