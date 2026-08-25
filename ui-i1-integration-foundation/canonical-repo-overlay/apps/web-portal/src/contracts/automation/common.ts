export type Identifier = string;
export type IsoDateTime = string;

export type DataMode = "mock" | "real";
export type Availability = "AVAILABLE" | "NOT_ELIGIBLE" | "UNKNOWN";
export type QCStatus = "PASS" | "WARNING" | "FAIL" | "UNKNOWN";
export type PipelineJobStatus = "QUEUED" | "RUNNING" | "COMPLETED" | "FAILED" | "BLOCKED";

export interface ProvenanceRef {
  source_hash?: string;
  source_id?: Identifier;
  processing_manifest_id?: Identifier;
  config_version?: string;
  contract_version?: string;
}

export interface PageResult<T> {
  items: T[];
  next_cursor?: string | null;
}
