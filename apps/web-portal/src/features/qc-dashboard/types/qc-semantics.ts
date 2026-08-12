export type AttentionLevel = 
  | 'FAIL' 
  | 'BLOCKED' 
  | 'WARNING' 
  | 'NEEDS_REVIEW' 
  | 'UNKNOWN' 
  | 'NOT_EVALUATED' 
  | 'INSUFFICIENT_EVIDENCE' 
  | 'PASS';

export interface QCData {
  signal_quality?: string;
  supportability?: string;
  evaluation_status?: string;
  reason_codes?: string[];
}

export interface CaseRecord {
  case_id: string;
  qc?: QCData;
  review_state?: string;
  claim_scope?: string;
  source_refs?: string[];
}

export interface QueueItem {
  case_id: string;
  attention: AttentionLevel;
  priority: number;
  label: string;
  reason_codes: readonly string[];
  supportability: string;
  evaluation_status: string;
  claim_scope: string;
  review_state: string;
  source_refs: readonly string[];
}

export interface QueueSummary {
  claim_scope: 'RESEARCH_ONLY';
  sort_policy: 'EXCEPTION_FIRST_V0_1';
  attention_order: readonly string[];
  counts: Readonly<Record<AttentionLevel, number>>;
  items: readonly QueueItem[];
  scripted_demo_max_clicks_to_reason: number;
}
