import type { Identifier, IsoDateTime } from "./common";

export type TechnicalReviewAction =
  | "ACCEPTED_TECHNICAL"
  | "REPROCESS_REQUESTED"
  | "REMEASURE_SUGGESTED"
  | "INCONCLUSIVE";

export interface ReviewActionRequest {
  action: TechnicalReviewAction;
  reason_code: string;
  note?: string;
  expected_revision: number;
  idempotency_key: string;
}

export interface ReviewCaseDetail {
  case_id: Identifier;
  session_id: Identifier;
  state:
    | "NEW" | "NEEDS_REVIEW" | "REVIEWING"
    | "REPROCESS_REQUESTED" | "REMEASURE_SUGGESTED"
    | "INCONCLUSIVE" | "ACCEPTED_TECHNICAL" | "FINALIZED_DEMO";
  reason_codes: string[];
  revision: number;
  created_at?: IsoDateTime;
  updated_at?: IsoDateTime;
  evidence_ref?: string;
}

export interface ReviewActionReceipt {
  case_id: Identifier;
  session_id: Identifier;
  action: TechnicalReviewAction;
  state: ReviewCaseDetail["state"];
  revision: number;
  audit_event_id: Identifier;
  idempotency_key: string;
  accepted: boolean;
  evidence_ref?: string;
}
