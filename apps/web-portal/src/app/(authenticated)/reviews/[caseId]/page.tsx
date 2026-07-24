'use client';

import { useEffect, useMemo, useState } from 'react';
import { useParams } from 'next/navigation';
import { useAuth, type UserRole } from '@/lib/auth';
import {
  ReviewReportClient,
  type CreateReviewCaseRequest,
} from '@/lib/review-report-client';
import { Day24ReviewPage } from '@/app/reviews/Day24ReviewPage';
import type {
  ReviewCaseContract,
  ReviewEventContract,
  ReviewerRole,
} from '@/schemas/review-report.schema';

const RESULT_HASH = 'a'.repeat(64);
const REVIEWER_HASH = 'b'.repeat(64);
const client = new ReviewReportClient(process.env.NEXT_PUBLIC_API_BASE_URL ?? '');

function reviewerRoleFromUser(role: UserRole | undefined): ReviewerRole {
  if (role === 'doctor') return 'physician';
  if (role === 'researcher') return 'ml_qa';
  if (role === 'admin') return 'admin';
  return 'ktv';
}

function eventId(prefix: string): string {
  return `REVT-${prefix}-${Date.now().toString(36)}`;
}

function buildEvent(
  reviewCase: ReviewCaseContract,
  reviewType: 'technical' | 'clinical',
  action: ReviewEventContract['action'],
  reviewerRole: ReviewerRole,
): ReviewEventContract {
  const needsReason = action === 'reject' || action === 'request_remeasurement' || action === 'supersede';
  return {
    eventId: eventId(`${reviewType}-${action}`),
    reviewType,
    action,
    reviewerRole,
    reviewerIdHash: REVIEWER_HASH,
    sourceResultHash: reviewCase.originalResultHash,
    checklistVersion:
      reviewType === 'technical'
        ? 'technical-review-checklist.v0.1'
        : 'clinical-review-checklist.v0.1',
    checklistResponses:
      reviewType === 'technical'
        ? {
            source_hash_verified: true,
            protocol_version_confirmed: true,
            qc_reviewed: true,
            traceability_present: true,
          }
        : {
            intended_use_respected: true,
            non_diagnostic_wording: true,
            limitations_visible: true,
            no_treatment_recommendation: true,
          },
    reasonCodes: needsReason ? ['REMEASURE_OR_REJECT_REASON_REQUIRED'] : [],
    comment: needsReason ? 'Yêu cầu review lại theo governance Day24.' : null,
    createdAt: new Date().toISOString(),
    immutable: true,
  };
}

export default function Day24AuthenticatedReviewRoute() {
  const params = useParams();
  const { user } = useAuth();
  const caseId = params.caseId as string;
  const currentRole = reviewerRoleFromUser(user?.role);
  const [reviewCase, setReviewCase] = useState<ReviewCaseContract | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const createRequest = useMemo<CreateReviewCaseRequest>(() => ({
    analysisId: caseId.startsWith('AN-') ? caseId : `AN-${caseId}`,
    originalResultHash: RESULT_HASH,
    analysisStatus: 'completed_with_warnings',
  }), [caseId]);

  useEffect(() => {
    let mounted = true;
    setLoading(true);
    setError(null);
    const load = caseId.startsWith('REV-')
      ? client.getReviewCase(caseId).catch(() => client.createReviewCase(createRequest))
      : client.createReviewCase(createRequest);

    load
      .then((item) => {
        if (mounted) setReviewCase(item);
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
  }, [caseId, createRequest]);

  const appendEvent = (event: ReviewEventContract) => {
    if (!reviewCase) return;
    setLoading(true);
    setError(null);
    client
      .addReviewEvent(reviewCase.caseId, event)
      .then(setReviewCase)
      .catch((ex) => setError((ex as Error).message))
      .finally(() => setLoading(false));
  };

  return (
    <div className="page-container">
      <div className="page-header">
        <div className="page-header__left">
          <h1 className="page-title">Review Day24</h1>
          <p className="page-subtitle">Case: {reviewCase?.caseId ?? caseId}</p>
        </div>
      </div>
      {loading ? <p role="status">Đang tải workflow review...</p> : null}
      {error ? <p role="alert">{error}</p> : null}
      {reviewCase ? (
        <Day24ReviewPage
          reviewCase={reviewCase}
          currentRole={currentRole}
          onTechnicalApprove={() => appendEvent(buildEvent(reviewCase, 'technical', 'approve', currentRole))}
          onTechnicalRemeasure={() => appendEvent(buildEvent(reviewCase, 'technical', 'request_remeasurement', currentRole))}
          onClinicalApprove={() => appendEvent(buildEvent(reviewCase, 'clinical', 'approve', currentRole))}
          onClinicalReject={() => appendEvent(buildEvent(reviewCase, 'clinical', 'reject', currentRole))}
        />
      ) : null}
    </div>
  );
}
