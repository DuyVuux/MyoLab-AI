import type { Identifier, IsoDateTime } from "./common";

export interface AuditEvent {
  event_id: Identifier;
  session_id?: Identifier;
  event_type: string;
  timestamp: IsoDateTime;
  actor_type: "SYSTEM" | "USER" | "UNKNOWN";
  actor_ref?: string;
  artifact_ref?: string;
  config_version?: string;
  reason_codes?: string[];
}
