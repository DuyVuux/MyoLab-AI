import type { Identifier, IsoDateTime } from "./common";

export type ReviewState =
  | "NEW"
  | "NEEDS_REVIEW"
  | "REVIEWING"
  | "REPROCESS_REQUESTED"
  | "REMEASURE_SUGGESTED"
  | "INCONCLUSIVE"
  | "ACCEPTED_TECHNICAL"
  | "FINALIZED_DEMO";

export interface ReviewCase {
  case_id: Identifier;
  session_id: Identifier;
  state: ReviewState;
  reason_codes: string[];
  created_at?: IsoDateTime;
  updated_at?: IsoDateTime;
}
