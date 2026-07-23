import type { DataSourceIntent } from "./session-intake.schema";

export const importStates = [
  "draft",
  "file_selected",
  "hashing",
  "local_validation",
  "ready_to_upload",
  "uploading",
  "server_validation",
  "mapping_required",
  "normalized",
  "qc_ready",
  "cancelled",
  "upload_failed",
  "unsupported_format",
  "metadata_missing",
  "duplicate_detected",
  "import_rejected",
  "quarantined",
] as const;

export type ImportState = (typeof importStates)[number];

export interface DetectedSignalMetadata {
  readonly samplingRateHz?: number;
  readonly durationS?: number;
  readonly channelCount?: number;
  readonly signalUnit?: "uV" | "mV" | "V";
  readonly timeColumn?: string;
  readonly signalColumns: readonly string[];
  readonly deviceVendor?: string;
  readonly timestampMonotonic?: boolean;
}

export interface SignalImportRecord {
  readonly schemaVersion: "signal-import-record.v0.1";
  readonly importId: string;
  readonly sessionId: string;
  readonly sourceType: DataSourceIntent;
  readonly state: ImportState;
  readonly sanitizedFilename: string;
  readonly sizeBytes: number;
  readonly sourceHashSha256: string;
  readonly detectedMetadata: DetectedSignalMetadata;
  readonly errorCode?: string;
  readonly retryFromState?: ImportState;
  readonly rawSamplesIncluded: false;
  readonly containsDirectIdentifier: false;
}
