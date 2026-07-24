'use client';

import { useEffect, useMemo, useState } from 'react';
import { useParams } from 'next/navigation';
import { ReviewReportClient } from '@/lib/review-report-client';
import { Day24ReportPreviewPage } from '@/app/reports/Day24ReportPreviewPage';
import type {
  ClinicalReportPackageContract,
  ReviewCaseContract,
} from '@/schemas/review-report.schema';

const RESULT_HASH = 'a'.repeat(64);
const REVIEWER_HASH = 'b'.repeat(64);
const client = new ReviewReportClient(process.env.NEXT_PUBLIC_API_BASE_URL ?? '');

function approvedReviewCase(reportId: string): ReviewCaseContract {
  return {
    schemaVersion: 'review-workflow.v0.1',
    caseId: `REV-${reportId.replace(/[^A-Za-z0-9_-]/g, '').slice(0, 24) || 'DAY24REPORT'}`,
    analysisId: `AN-${reportId}`,
    originalResultHash: RESULT_HASH,
    analysisStatus: reportId.includes('abstain') ? 'abstained' : 'completed',
    state: reportId.includes('draft') ? 'pending_clinical_review' : 'approved',
    events: reportId.includes('draft')
      ? []
      : [
          {
            eventId: 'REVT-clinical-approved-demo',
            reviewType: 'clinical',
            action: 'approve',
            reviewerRole: 'physician',
            reviewerIdHash: REVIEWER_HASH,
            sourceResultHash: RESULT_HASH,
            checklistVersion: 'clinical-review-checklist.v0.1',
            checklistResponses: {
              intended_use_respected: true,
              limitations_visible: true,
              no_treatment_recommendation: true,
            },
            reasonCodes: [],
            comment: null,
            createdAt: new Date().toISOString(),
            immutable: true,
          },
        ],
    safety: {
      originalResultImmutable: true,
      humanReviewRequired: true,
      rawSamplesIncluded: false,
      clinicalUseAllowed: false,
    },
  };
}

export default function Day24AuthenticatedReportRoute() {
  const params = useParams();
  const reportId = params.reportId as string;
  const [report, setReport] = useState<ClinicalReportPackageContract | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const finalize = !reportId.includes('draft');

  const request = useMemo(() => ({
    reviewCase: approvedReviewCase(reportId),
    analysisSummary: {
      summaryVi: 'Kết quả kỹ thuật cần được đọc cùng workflow review Day24.',
      protocolVersion: 'upper-limb-review@0.2.0',
      modelOrRuleVersion: 'day24-review-boundary-v0.1',
      qualityGateVersion: 'quality-gate-v0.1',
    },
    finalize,
    templateVersion: 'clinical-report-v0.2-review-workflow',
  }), [finalize, reportId]);

  useEffect(() => {
    let mounted = true;
    setLoading(true);
    setError(null);
    const load = finalize
      ? client.finalizeReport(request)
      : client.previewReport(request);
    load
      .then((item) => {
        if (mounted) setReport(item);
      })
      .catch((ex) => {
        if (mounted) setError((ex as Error).message);
      })
      .finally(() => {
        if (mounted) setLoading(false);
      });

    return () => {
      mounted = false;
    };
  }, [finalize, request]);

  return (
    <div className="page-container">
      <div className="page-header">
        <div className="page-header__left">
          <h1 className="page-title">Report Day24</h1>
          <p className="page-subtitle">Report route: {reportId}</p>
        </div>
      </div>
      {loading ? <p role="status">Đang dựng report preview...</p> : null}
      {error ? <p role="alert">{error}</p> : null}
      {report ? <Day24ReportPreviewPage report={report} /> : null}
    </div>
  );
}
