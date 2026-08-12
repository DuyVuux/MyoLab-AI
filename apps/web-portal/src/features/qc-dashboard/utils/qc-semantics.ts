import { AttentionLevel, CaseRecord, QueueItem, QueueSummary } from '../types/qc-semantics';

export const PRIORITY: Record<AttentionLevel, number> = Object.freeze({
  FAIL: 0,
  BLOCKED: 0,
  WARNING: 1,
  NEEDS_REVIEW: 1,
  UNKNOWN: 2,
  NOT_EVALUATED: 2,
  INSUFFICIENT_EVIDENCE: 2,
  PASS: 3,
});

export const SAFE_LABELS: Record<AttentionLevel, string> = Object.freeze({
  FAIL: 'Data quality fail',
  BLOCKED: 'Processing blocked',
  WARNING: 'Review warning',
  NEEDS_REVIEW: 'Needs review',
  UNKNOWN: 'Unknown supportability',
  NOT_EVALUATED: 'Not evaluated',
  INSUFFICIENT_EVIDENCE: 'Insufficient evidence',
  PASS: 'Quality pass',
});

export function classifyAttention(caseRecord: CaseRecord): AttentionLevel {
  const qc = caseRecord.qc ?? {};
  const reviewState = caseRecord.review_state ?? null;
  
  if (qc.signal_quality === 'FAIL' || qc.supportability === 'BLOCKED') return 'FAIL';
  if (reviewState === 'NEEDS_REVIEW') return 'NEEDS_REVIEW';
  if (qc.signal_quality === 'WARNING' || qc.supportability === 'REVIEW_REQUIRED') return 'WARNING';
  if (qc.evaluation_status === 'INSUFFICIENT_EVIDENCE') return 'INSUFFICIENT_EVIDENCE';
  if (qc.evaluation_status === 'NOT_EVALUATED') return 'NOT_EVALUATED';
  if (qc.supportability === 'UNKNOWN' || qc.supportability == null) return 'UNKNOWN';
  if (qc.signal_quality === 'PASS' && qc.supportability === 'SUPPORTABLE') return 'PASS';
  
  return 'UNKNOWN';
}

export function buildQueueItem(caseRecord: CaseRecord): QueueItem {
  const attention = classifyAttention(caseRecord);
  const qc = caseRecord.qc ?? {};
  
  return Object.freeze({
    case_id: String(caseRecord.case_id),
    attention,
    priority: PRIORITY[attention],
    label: SAFE_LABELS[attention],
    reason_codes: Object.freeze([...(qc.reason_codes ?? [])]),
    supportability: qc.supportability ?? 'UNKNOWN',
    evaluation_status: qc.evaluation_status ?? 'NOT_EVALUATED',
    claim_scope: caseRecord.claim_scope ?? 'RESEARCH_ONLY',
    review_state: caseRecord.review_state ?? 'NEW',
    source_refs: Object.freeze([...(caseRecord.source_refs ?? [])]),
  });
}

export function buildQueueSummary(caseRecords: CaseRecord[]): QueueSummary {
  const items = caseRecords.map(buildQueueItem);
  items.sort((a, b) => (a.priority - b.priority) || a.case_id.localeCompare(b.case_id));
  
  const counts = Object.fromEntries(
    Object.keys(PRIORITY).map((k) => [k, 0])
  ) as Record<AttentionLevel, number>;
  
  for (const item of items) {
    counts[item.attention] += 1;
  }
  
  return Object.freeze({
    claim_scope: 'RESEARCH_ONLY',
    sort_policy: 'EXCEPTION_FIRST_V0_1',
    attention_order: Object.freeze(['FAIL/BLOCKED', 'WARNING/NEEDS_REVIEW', 'UNKNOWN/NOT_EVALUATED', 'PASS']),
    counts: Object.freeze(counts),
    items: Object.freeze(items),
    scripted_demo_max_clicks_to_reason: 3,
  });
}

/**
 * Enforces safety semantics ensuring we never falsely display a successful state
 * for unknown/insufficient data. Throws if a violation is detected.
 */
export function assertNoFalseFinalState(item: QueueItem): boolean {
  if (['UNKNOWN', 'NOT_EVALUATED', 'INSUFFICIENT_EVIDENCE'].includes(item.attention) && item.label.includes('Pass')) {
    throw new Error('UNKNOWN_MUST_NOT_RENDER_AS_PASS');
  }
  if (item.claim_scope !== 'RESEARCH_ONLY') {
    throw new Error('RESEARCH_ONLY_BANNER_REQUIRED');
  }
  return true;
}
