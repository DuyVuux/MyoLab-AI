import type { Identifier, IsoDateTime, QCStatus, ProvenanceRef } from "./common";

export type SessionAutomationState =
  | "SOURCE_RECEIVED"
  | "INGESTING"
  | "VALIDATING"
  | "QC_RUNNING"
  | "PROCESSING"
  | "METRICS_RUNNING"
  | "EVIDENCE_READY"
  | "REVIEW_REQUIRED"
  | "BLOCKED"
  | "UNKNOWN";

export interface SessionSummary {
  session_id: Identifier;
  display_name?: string;
  source_type?: string;
  automation_state: SessionAutomationState;
  qc_status?: QCStatus;
  created_at?: IsoDateTime;
  updated_at?: IsoDateTime;
  provenance?: ProvenanceRef;
}

export interface SessionDetail extends SessionSummary {
  signal_count?: number;
  warning_count?: number;
  blocked_reason_codes?: string[];
  limitations?: string[];
}
