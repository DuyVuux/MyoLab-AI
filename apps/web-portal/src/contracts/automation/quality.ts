import type { Identifier, QCStatus } from "./common";

export type QCScope = "SESSION" | "CHANNEL" | "WINDOW";

export interface QCFinding {
  finding_id?: Identifier;
  scope: QCScope;
  status: QCStatus;
  reason_code: string;
  channel_id?: Identifier;
  start_s?: number;
  end_s?: number;
  message?: string;
}

export interface QualityAssessment {
  session_id: Identifier;
  overall_status: QCStatus;
  eligible_window_fraction?: number | null;
  findings: QCFinding[];
  ruleset_version?: string;
  evidence_ref?: string;
}
