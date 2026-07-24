from __future__ import annotations

from hashlib import sha256
from typing import Any

from schemas.day24_review_report_schema import ClinicalReportPackage, ReportBuildRequest
from services.day24_review_workflow_service import can_finalize_report
from day24_report_hash import compute_report_hash


FORBIDDEN_PHRASES = (
    "chẩn đoán mỏi cơ",
    "bắt buộc dừng tập",
    "đủ điều kiện thi đấu",
    "xác suất bệnh nhân bị mỏi",
)


def _safe_sections(summary: dict[str, Any], analysis_status: str) -> dict[str, Any]:
    if analysis_status == "abstained":
        return {
            "summaryVi": "Dữ liệu không đủ điều kiện phân tích.",
            "evidence": [],
            "recommendedReviewVi": (
                "Kiểm tra setup, điện cực, protocol và cân nhắc thực hiện đo lại."
            ),
        }
    return {
        "summaryVi": summary.get(
            "summaryVi", "Kết quả kỹ thuật cần được bác sĩ/KTV xem xét."
        ),
        "evidence": summary.get("evidence", []),
        "recommendedReviewVi": summary.get(
            "recommendedReviewVi",
            "Đối chiếu với đánh giá lâm sàng và protocol hiện tại trước khi ra quyết định.",
        ),
    }


def build_report(request: ReportBuildRequest) -> ClinicalReportPackage:
    case = request.reviewCase
    if request.finalize and not can_finalize_report(case):
        raise ValueError("REPORT_FINALIZATION_REQUIRES_APPROVED_REVIEW")

    status = "final" if request.finalize else "draft"
    report_id = "RPT-" + sha256(
        f"{case.caseId}:{case.analysisId}:{status}:{request.templateVersion}".encode()
    ).hexdigest()[:16]
    sections = _safe_sections(request.analysisSummary, case.analysisStatus)
    combined_text = " ".join(str(value).lower() for value in sections.values())
    for phrase in FORBIDDEN_PHRASES:
        if phrase in combined_text:
            raise ValueError(f"PROHIBITED_REPORT_PHRASE:{phrase}")

    payload: dict[str, Any] = {
        "schemaVersion": "clinical-report-package.v0.1",
        "reportId": report_id,
        "analysisId": case.analysisId,
        "status": status,
        "watermark": None if status == "final" else "BẢN NHÁP — CHƯA KÝ DUYỆT",
        "templateVersion": request.templateVersion,
        "source": {
            "originalResultHash": case.originalResultHash,
            "analysisStatus": case.analysisStatus,
            "protocolVersion": request.analysisSummary.get("protocolVersion", "unknown"),
            "modelOrRuleVersion": request.analysisSummary.get("modelOrRuleVersion", "unknown"),
            "qualityGateVersion": request.analysisSummary.get("qualityGateVersion", "unknown"),
        },
        "sections": sections,
        "review": {
            "caseId": case.caseId,
            "state": case.state,
            "eventCount": len(case.events),
            "clinicalReviewerPresent": any(
                event.reviewerRole == "physician" for event in case.events
            ),
        },
        "limitations": [
            "Kết quả là hỗ trợ đánh giá, không thay thế quyết định của bác sĩ/KTV.",
            "Ngưỡng và model/rule hiện chưa được xác thực lâm sàng trên dữ liệu bệnh nhân địa phương.",
        ],
        "safety": {
            "rawSamplesIncluded": False,
            "clinicalUseAllowed": False,
            "humanReviewRequired": True,
            "automaticTreatmentRecommendation": False,
        },
        "reportHashSha256": "0" * 64,
    }
    payload["reportHashSha256"] = compute_report_hash(payload)
    return ClinicalReportPackage.model_validate(payload)
