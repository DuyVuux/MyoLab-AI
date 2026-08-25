import type { Identifier, QCStatus } from "./common";

export type PreflightCheckStatus = "PASS" | "WARNING" | "FAIL" | "UNKNOWN";

export interface PreflightCheck {
  check_id: string;
  label: string;
  status: PreflightCheckStatus;
  reason_code?: string;
  message?: string;
}

export interface SessionPreflight {
  session_id: Identifier;
  overall_status: PreflightCheckStatus;
  can_proceed: boolean;
  checks: PreflightCheck[];
  evidence_ref?: string;
}
