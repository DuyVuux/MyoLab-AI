import type { Identifier, IsoDateTime, ProvenanceRef } from "./common";

export type ImportFormat =
  | "NORAXON_SINGLE_CSV"
  | "NORAXON_SEPARATED_CSV"
  | "VICON_CSV"
  | "UNKNOWN";

export type ImportStatus =
  | "WAITING"
  | "HASHING"
  | "DETECTING_FORMAT"
  | "PARSING"
  | "VALIDATING"
  | "CANONICALIZING"
  | "READY_FOR_QC"
  | "FAILED"
  | "BLOCKED";

export interface CreateImportRequest {
  source_name: string;
  source_kind: "UPLOAD" | "WORKSPACE_PATH" | "DEMO_FIXTURE";
  workspace_path?: string;
  expected_format?: ImportFormat;
}

export interface UploadImportRequest {
  file: File;
  expected_format?: ImportFormat;
}

export interface ImportJob {
  import_id: Identifier;
  session_id?: Identifier;
  pipeline_job_id?: Identifier;
  status: ImportStatus;
  detected_format?: ImportFormat;
  source_hash?: string;
  signal_count?: number;
  reason_codes?: string[];
  created_at?: IsoDateTime;
  updated_at?: IsoDateTime;
  provenance?: ProvenanceRef;
}
