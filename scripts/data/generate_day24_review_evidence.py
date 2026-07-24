#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from schemas.day24_review_report_schema import ReportBuildRequest, ReviewCase, ReviewEvent
from services.day24_review_workflow_service import apply_review_event
from day24_report_builder import build_report

ROOT = Path(__file__).resolve().parents[2]
HASH = "a" * 64
RID_KTV = "b" * 64
RID_MD = "c" * 64
FIXED_TIME = datetime(2026, 7, 24, 9, 0, tzinfo=timezone.utc)

case = ReviewCase(
    caseId="REV-DAY24EVIDENCE",
    analysisId="AN-DAY24-GOLDEN",
    originalResultHash=HASH,
    analysisStatus="completed_with_warnings",
)
case = apply_review_event(
    case,
    ReviewEvent(
        eventId="REVT-DAY24TECH01",
        reviewType="technical",
        action="approve",
        reviewerRole="ktv",
        reviewerIdHash=RID_KTV,
        sourceResultHash=HASH,
        checklistVersion="technical-review-checklist.v0.1",
        checklistResponses={
            "source_and_protocol_verified": True,
            "quality_gate_reviewed": True,
            "warnings_acknowledged": True,
        },
        reasonCodes=["POWERLINE_WARNING_ACKNOWLEDGED"],
        comment="Đã đối chiếu nguồn và cảnh báo kỹ thuật.",
        createdAt=FIXED_TIME,
    ),
)
case = apply_review_event(
    case,
    ReviewEvent(
        eventId="REVT-DAY24CLIN01",
        reviewType="clinical",
        action="approve",
        reviewerRole="physician",
        reviewerIdHash=RID_MD,
        sourceResultHash=HASH,
        checklistVersion="clinical-review-checklist.v0.1",
        checklistResponses={
            "interpretation_readable": True,
            "limitations_visible": True,
            "no_automatic_treatment": True,
        },
        reasonCodes=[],
        comment="Phê duyệt để sinh báo cáo kỹ thuật cuối.",
        createdAt=FIXED_TIME,
    ),
)
summary = {
    "summaryVi": "Mẫu thay đổi đa miền được quan sát trong protocol hiện tại.",
    "evidence": [
        {"code": "MDF_DECLINING", "value": -0.31, "unit": "Hz/s"},
        {"code": "RMS_INCREASING", "value": 0.42, "unit": "uV/s"},
    ],
    "recommendedReviewVi": (
        "Đối chiếu với chức năng vận động, tải tập và đánh giá của bác sĩ/KTV."
    ),
    "protocolVersion": "quad-isometric-60s.v0.1",
    "modelOrRuleVersion": "fatigue_rule_v0.1",
    "qualityGateVersion": "qc_v0.1",
}
draft = build_report(
    ReportBuildRequest(reviewCase=case, analysisSummary=summary, finalize=False)
)
final = build_report(
    ReportBuildRequest(reviewCase=case, analysisSummary=summary, finalize=True)
)

out = ROOT / "qa-validation/evidence"
out.mkdir(parents=True, exist_ok=True)
(out / "day24-review-case.json").write_text(
    json.dumps(case.model_dump(mode="json"), ensure_ascii=False, indent=2) + "\n",
    encoding="utf-8",
)
(out / "day24-report-draft.json").write_text(
    json.dumps(draft.model_dump(mode="json"), ensure_ascii=False, indent=2) + "\n",
    encoding="utf-8",
)
(out / "day24-report-final.json").write_text(
    json.dumps(final.model_dump(mode="json"), ensure_ascii=False, indent=2) + "\n",
    encoding="utf-8",
)
print(case.state, draft.status, final.status, final.reportHashSha256)
