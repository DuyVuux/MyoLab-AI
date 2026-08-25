import type { Identifier } from "./common";

export type MappingDecision = "AUTO_MATCHED" | "REVIEW_REQUIRED" | "UNRESOLVED";

export interface ChannelMappingCandidate {
  vendor_signal_name: string;
  canonical_channel_id?: Identifier;
  canonical_label?: string;
  confidence?: number | null;
  decision: MappingDecision;
  reason_code?: string;
}

export interface SessionMappingState {
  session_id: Identifier;
  ontology_version?: string;
  resolved_count: number;
  unresolved_count: number;
  candidates: ChannelMappingCandidate[];
  evidence_ref?: string;
}

export interface MappingResolutionRequest {
  vendor_signal_name: string;
  canonical_channel_id: Identifier;
  reason_code: string;
}

export interface MappingResolutionReceipt {
  session_id: Identifier;
  vendor_signal_name: string;
  canonical_channel_id: Identifier;
  accepted: boolean;
  revision?: number;
  evidence_ref?: string;
}
