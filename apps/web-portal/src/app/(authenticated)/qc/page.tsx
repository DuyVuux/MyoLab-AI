import React from 'react';
import { QCDashboard } from '@/features/qc-dashboard';
import { buildQueueSummary } from '@/features/qc-dashboard/utils/qc-semantics';
import type { CaseRecord } from '@/features/qc-dashboard/types/qc-semantics';

// Mock data to demonstrate the dashboard
const mockCases: CaseRecord[] = [
  {
    case_id: 'C-001',
    qc: { signal_quality: 'FAIL', supportability: 'BLOCKED', reason_codes: ['ARTIFACT_OVERLOAD'] },
    claim_scope: 'RESEARCH_ONLY',
  },
  {
    case_id: 'C-002',
    qc: { signal_quality: 'WARNING', supportability: 'SUPPORTABLE', reason_codes: ['HIGH_NOISE'] },
    claim_scope: 'RESEARCH_ONLY',
  },
  {
    case_id: 'C-003',
    qc: { evaluation_status: 'NOT_EVALUATED' },
    claim_scope: 'RESEARCH_ONLY',
  },
  {
    case_id: 'C-004',
    qc: { signal_quality: 'PASS', supportability: 'SUPPORTABLE' },
    claim_scope: 'RESEARCH_ONLY',
  },
];

export default function QCPage() {
  const summary = buildQueueSummary(mockCases);

  return (
    <div className="min-h-screen bg-gray-100 py-8">
      <QCDashboard summary={summary} />
    </div>
  );
}
