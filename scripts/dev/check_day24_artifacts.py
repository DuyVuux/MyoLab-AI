#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REQUIRED = [
    "docs/plans/DAY24_EXECUTION_PLAN.md",
    "clinical/review-templates/technical-review-checklist.v0.1.yaml",
    "clinical/review-templates/clinical-review-checklist.v0.1.yaml",
    "packages/common-schemas/json/review-workflow.v0.1.schema.json",
    "packages/common-schemas/json/clinical-report-package.v0.1.schema.json",
    "packages/common-schemas/json/feedback-adjudication.v0.1.schema.json",
    "services/api-server/src/services/day24_review_workflow_service.py",
    "services/api-server/src/services/day24_feedback_adjudication_service.py",
    "apps/web-portal/src/components/review/TechnicalReviewPanel.tsx",
    "apps/web-portal/src/components/review/ClinicalSignoffPanel.tsx",
    "reports/templates/clinical_report_v0.2-review-workflow.md",
    "services/api-server/src/schemas/day24_review_report_schema.py",
    "services/api-server/src/mock_api/day24_app.py",
    "services/report-generation-service/src/day24_report_builder.py",
    "services/report-generation-service/src/day24_report_hash.py",
    "apps/web-portal/e2e/day24-review-report-regression.spec.ts",
    "apps/web-portal/src/schemas/review-report.schema.ts",
    "apps/web-portal/src/lib/review-report-client.ts",
    "apps/web-portal/src/app/reviews/Day24ReviewPage.tsx",
    "apps/web-portal/src/app/reports/Day24ReportPreviewPage.tsx",
    "apps/web-portal/src/app/(authenticated)/reviews/[caseId]/page.tsx",
    "apps/web-portal/src/app/(authenticated)/reports/[reportId]/page.tsx",
    "reports/wording/day24-approved-phrases.md",
    "reports/wording/day24-prohibited-claims.md",
    "qa-validation/requirements/day24-acceptance-criteria.md",
]
missing = [p for p in REQUIRED if not (ROOT / p).is_file()]
if missing:
    print("Thiếu artifact Day 24:", *missing, sep="\n- ", file=sys.stderr)
    raise SystemExit(1)

for rel in [
    "qa-validation/evidence/day24-review-case.json",
    "qa-validation/evidence/day24-report-draft.json",
    "qa-validation/evidence/day24-report-final.json",
]:
    path = ROOT / rel
    if not path.is_file():
        print(f"Thiếu evidence: {rel}", file=sys.stderr)
        raise SystemExit(1)
    payload = json.loads(path.read_text(encoding="utf-8"))
    text = json.dumps(payload, ensure_ascii=False).lower()
    if '"rawsamplesincluded": true' in text:
        raise SystemExit(f"Safety fail raw samples: {rel}")
    if '"clinicaluseallowed": true' in text:
        raise SystemExit(f"Safety fail clinical use: {rel}")
    if '"humanreviewrequired": false' in text:
        raise SystemExit(f"Safety fail human review: {rel}")

final = json.loads(
    (ROOT / "qa-validation/evidence/day24-report-final.json").read_text(encoding="utf-8")
)
if final["status"] != "final" or final["review"]["state"] != "approved":
    raise SystemExit("Final report không gắn với review approved.")
if final["watermark"] is not None:
    raise SystemExit("Final report không được giữ draft watermark.")

draft = json.loads(
    (ROOT / "qa-validation/evidence/day24-report-draft.json").read_text(encoding="utf-8")
)
if draft["status"] != "draft" or not draft["watermark"]:
    raise SystemExit("Draft report phải có watermark.")



scan_roots = [
    "services/api-server/src/schemas/day24_review_report_schema.py",
    "services/api-server/src/services/day24_review_workflow_service.py",
    "services/api-server/src/services/day24_feedback_adjudication_service.py",
    "apps/web-portal/src/schemas/review-report.schema.ts",
    "apps/web-portal/src/lib/review-report-client.ts",
    "apps/web-portal/src/components/review",
    "apps/web-portal/src/app/reviews",
    "apps/web-portal/src/app/reports",
    "apps/web-portal/src/app/(authenticated)/reviews",
    "apps/web-portal/src/app/(authenticated)/reports",
]
forbidden_fragments = [
    "chẩn đoán mỏi cơ",
    "bắt buộc dừng tập",
    "đủ điều kiện thi đấu",
    "xác suất bệnh nhân bị mỏi",
    "rawSamplesIncluded: true",
    "clinicalUseAllowed: true",
    '"rawSamplesIncluded": true',
    '"clinicalUseAllowed": true',
]
violations = []
for rel in scan_roots:
    source = ROOT / rel
    candidates = [source] if source.is_file() else [p for p in source.rglob("*") if p.suffix in {".py", ".ts", ".tsx", ".json", ".md"}]
    for candidate in candidates:
        body = candidate.read_text(encoding="utf-8")
        for fragment in forbidden_fragments:
            if fragment in body:
                violations.append(f"{candidate.relative_to(ROOT)}: {fragment}")
if violations:
    print("Day 24 wording/privacy scan fail:", *violations, sep="\n- ", file=sys.stderr)
    raise SystemExit(1)

print("Day 24 artifact and safety check passed.")
