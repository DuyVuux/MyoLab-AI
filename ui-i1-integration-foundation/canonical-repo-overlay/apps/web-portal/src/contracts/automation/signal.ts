import type { Identifier, ProvenanceRef } from "./common";

export type SignalRepresentation = "RAW" | "PROCESSED";

export interface SignalWindowRequest {
  session_id: Identifier;
  channel_id: Identifier;
  start_s: number;
  end_s: number;
  representation: SignalRepresentation;
}

export interface SignalMaskInterval {
  start_s: number;
  end_s: number;
  reason_code: string;
}

export interface SignalWindow {
  session_id: Identifier;
  channel_id: Identifier;
  representation: SignalRepresentation;
  sampling_rate_hz: number;
  unit: string;
  start_s: number;
  end_s: number;
  samples: number[];
  masks?: SignalMaskInterval[];
  provenance: ProvenanceRef;
}
