export interface OperationsSummary {
  generated_at: string;
  sessions_total: number;
  imports_running: number;
  qc_warning: number;
  blocked: number;
  awaiting_review: number;
  completed: number;
  unknown: number;
  source: "CANONICAL_READ_MODEL";
  limitations: string[];
}
