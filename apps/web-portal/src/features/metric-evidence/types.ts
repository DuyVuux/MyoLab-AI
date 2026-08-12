export type MetricStatus =
  | 'AVAILABLE'
  | 'BLOCKED'
  | 'NOT_AVAILABLE'
  | 'UNSUPPORTED'
  | 'REVIEW_REQUIRED'
  | 'ABSTAINED';

export interface Uncertainty {
  uncertainty_type?: 'RULE_CONFIDENCE' | string;
  calibrated_probability?: number | null;
  calibration_status?: 'CALIBRATED' | 'UNCALIBRATED' | string;
  conformal_set?: any;
  rule_confidence_level?: string;
  [key: string]: any;
}

export interface DistributionSupport {
  status?: string;
  method_status?: string;
  ood_method_status?: string;
  score?: number | null;
  ood_score?: number | null;
  reason_codes?: string[];
}

export interface QualityEligibility {
  metric_handoff_status?: string;
  processing_permission?: string;
  qc_signal_quality?: string;
  qc_supportability?: string;
  reason_codes?: string[];
}

export interface MetricInput {
  metric_name: string;
  status: MetricStatus;
  value?: number | string | null;
  units?: string | null;
  reason_codes?: string[];
  evidence_class?: string;
  manifest_id?: string;
}

export interface MetricEvidenceParams {
  metric: MetricInput;
  quality_eligibility?: QualityEligibility | null;
  distribution_support?: DistributionSupport | null;
  uncertainty?: Uncertainty | null;
  claim_scope?: string;
}

export interface MetricEvidenceView {
  metric_name: string;
  metric_status: MetricStatus;
  status_label: string;
  value: number | string | null;
  units: string | null;
  reason_codes: readonly string[];
  metric_handoff_status: string | null;
  processing_permission: string | null;
  qc_signal_quality: string | null;
  qc_supportability: string | null;
  distribution_support: Readonly<{
    status: string;
    method_status: string;
    score: number | null;
    reason_codes: readonly string[];
  }>;
  uncertainty: Readonly<Uncertainty>;
  claim_scope: string;
  evidence_class: string;
  manifest_id: string | null;
}
