import sys
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "services/report-generation-service/src"))

from schemas.day24_review_report_schema import ReportBuildRequest, ReviewCase
from day24_report_builder import build_report
from day24_report_hash import verify_report_hash

HASH = "a" * 64


def test_draft_report_has_watermark():
    case = ReviewCase(
        caseId="REV-12345678",
        analysisId="AN-1",
        originalResultHash=HASH,
        analysisStatus="completed",
    )
    report = build_report(
        ReportBuildRequest(
            reviewCase=case,
            analysisSummary={"summaryVi": "Kết quả kỹ thuật cần review."},
        )
    )
    assert report.status == "draft" and report.watermark
    assert verify_report_hash(report.model_dump(mode="json"))


def test_final_requires_approved():
    case = ReviewCase(
        caseId="REV-12345678",
        analysisId="AN-1",
        originalResultHash=HASH,
        analysisStatus="completed",
    )
    with pytest.raises(ValueError):
        build_report(
            ReportBuildRequest(reviewCase=case, analysisSummary={}, finalize=True)
        )


def test_abstained_report_has_no_conclusion():
    case = ReviewCase(
        caseId="REV-12345678",
        analysisId="AN-2",
        originalResultHash=HASH,
        analysisStatus="abstained",
    )
    report = build_report(
        ReportBuildRequest(
            reviewCase=case,
            analysisSummary={"summaryVi": "ignored"},
        )
    )
    assert report.sections["summaryVi"] == "Dữ liệu không đủ điều kiện phân tích."
    assert report.sections["evidence"] == []
