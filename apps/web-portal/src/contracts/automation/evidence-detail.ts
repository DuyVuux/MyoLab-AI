import type { Identifier, ProvenanceRef } from "./common";
import type { MetricEvidence } from "./metric";
import type { QualityAssessment } from "./quality";

export interface SignalDescriptor {
  channel_id: Identifier;
  label?: string;
  unit: string;
  sampling_rate_hz: number;
  sample_count?: number;
  duration_s?: number;
  raw_available: boolean;
  processed_available: boolean;
  processing_manifest_id?: Identifier;
}

export interface SignalIndex {
  session_id: Identifier;
  signals: SignalDescriptor[];
  source_hash?: string;
  evidence_ref?: string;
}

export interface ProcessingStepEvidence {
  step_name: string;
  status: "APPLIED" | "SKIPPED" | "FAILED" | "NOT_APPLICABLE";
  config_version?: string;
  reason_code?: string;
}

export interface ProcessingManifestEvidence {
  processing_manifest_id: Identifier;
  session_id: Identifier;
  source_hash: string;
  profile_id?: string;
  profile_version?: string;
  code_version?: string;
  config_hash?: string;
  steps: ProcessingStepEvidence[];
  created_at?: string;
}

export interface SessionEvidenceDetail {
  session_id: Identifier;
  source_hash?: string;
  quality?: QualityAssessment;
  metrics: MetricEvidence[];
  signal_index?: SignalIndex;
  processing_manifests?: ProcessingManifestEvidence[];
  review_case_ids?: Identifier[];
  limitations: string[];
  evidence_refs?: string[];
  provenance?: ProvenanceRef;
}
