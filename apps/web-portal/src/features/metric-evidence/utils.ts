import {
  MetricEvidenceParams,
  MetricEvidenceView,
  MetricStatus,
  Uncertainty
} from './types';

const METRIC_STATUS_LABELS: Record<MetricStatus, string> = {
  AVAILABLE: 'Available for research interpretation',
  BLOCKED: 'Blocked by eligibility gate',
  NOT_AVAILABLE: 'Not available',
  UNSUPPORTED: 'Unsupported for this case',
  REVIEW_REQUIRED: 'Review required',
  ABSTAINED: 'Abstained',
};

export function validateUncertainty(uncertainty?: Uncertainty | null): boolean {
  const u = uncertainty ?? {};
  
  if (u.uncertainty_type === 'RULE_CONFIDENCE') {
    if (u.calibrated_probability != null) {
      throw new Error('RULE_CONFIDENCE_MUST_NOT_BE_PROBABILITY');
    }
    if (u.conformal_set != null) {
      throw new Error('RULE_CONFIDENCE_MUST_NOT_BE_CONFORMAL');
    }
  }
  
  if (u.calibrated_probability != null && u.calibration_status !== 'CALIBRATED') {
    throw new Error('UNCALIBRATED_PROBABILITY_FORBIDDEN');
  }
  
  return true;
}

export function buildMetricEvidenceView({
  metric,
  quality_eligibility = null,
  distribution_support,
  uncertainty,
  claim_scope = 'RESEARCH_ONLY',
}: MetricEvidenceParams): MetricEvidenceView {
  
  if (claim_scope !== 'RESEARCH_ONLY') {
    throw new Error('RESEARCH_ONLY_REQUIRED');
  }
  
  validateUncertainty(uncertainty);
  
  if (!metric?.metric_name || !metric?.status) {
    throw new Error('METRIC_IDENTITY_REQUIRED');
  }
  
  if (
    ['NOT_AVAILABLE', 'UNSUPPORTED', 'BLOCKED', 'ABSTAINED'].includes(metric.status) &&
    metric.value != null
  ) {
    throw new Error('UNSUPPORTED_OR_BLOCKED_METRIC_MUST_BE_NULL');
  }
  
  const reasons = [
    ...(metric.reason_codes ?? []),
    ...(quality_eligibility?.reason_codes ?? []),
  ];
  const uniqueReasons = Array.from(new Set(reasons));
  
  return Object.freeze({
    metric_name: metric.metric_name,
    metric_status: metric.status,
    status_label: METRIC_STATUS_LABELS[metric.status] ?? metric.status,
    value: metric.value ?? null,
    units: metric.units ?? null,
    reason_codes: Object.freeze(uniqueReasons),
    metric_handoff_status: quality_eligibility?.metric_handoff_status ?? null,
    processing_permission: quality_eligibility?.processing_permission ?? null,
    qc_signal_quality: quality_eligibility?.qc_signal_quality ?? null,
    qc_supportability: quality_eligibility?.qc_supportability ?? null,
    distribution_support: Object.freeze({
      status: distribution_support?.status ?? 'NOT_EVALUATED',
      method_status:
        distribution_support?.method_status ??
        distribution_support?.ood_method_status ??
        'NOT_IMPLEMENTED',
      score: distribution_support?.score ?? distribution_support?.ood_score ?? null,
      reason_codes: Object.freeze([...(distribution_support?.reason_codes ?? [])]),
    }),
    uncertainty: Object.freeze({ ...uncertainty }),
    claim_scope,
    evidence_class: metric.evidence_class ?? 'NOT_VERIFIED',
    manifest_id: metric.manifest_id ?? null,
  });
}

export function explainMetric(view: MetricEvidenceView): string {
  const parts = [`${view.metric_name}: ${view.status_label}.`];
  
  if (view.value == null) {
    parts.push('No numeric value is presented.');
  }
  
  if (view.reason_codes.length) {
    parts.push(`Reason: ${view.reason_codes.join(', ')}.`);
  }
  
  parts.push(`Distribution support: ${view.distribution_support.status}.`);
  
  if (view.uncertainty?.uncertainty_type === 'RULE_CONFIDENCE') {
    parts.push('Rule confidence is ordinal evidence, not a calibrated probability.');
  }
  
  if (view.distribution_support.score == null) {
    parts.push('No validated OOD score is available.');
  }
  
  return parts.join(' ');
}
