import type { Availability, Identifier, ProvenanceRef } from "./common";

export interface MetricEvidence {
  metric_id: Identifier;
  metric_name: string;
  value: number | null;
  unit: string | null;
  eligibility: Availability;
  reason_code?: string;
  channel_id?: Identifier;
  source_window_id?: Identifier;
  provenance?: ProvenanceRef;
}
