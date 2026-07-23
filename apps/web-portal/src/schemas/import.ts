/**
 * Import domain types.
 * Per spec Section 6.6–6.7.
 * 9 success states + 5 error/terminal states = 14 total.
 */
import type { DataSourceType } from './common';

/** Success path states (ordered) */
export type ImportSuccessState =
  | 'file_selected'
  | 'hashing'
  | 'local_validation'
  | 'ready_to_upload'
  | 'uploading'
  | 'server_validation'
  | 'mapping_required'
  | 'normalized'
  | 'qc_ready';

/** Error/terminal states */
export type ImportErrorState =
  | 'upload_failed'
  | 'import_rejected'
  | 'duplicate_detected'
  | 'quarantined'
  | 'cancelled';

export type ImportState = ImportSuccessState | ImportErrorState;

/** Reason codes for import_rejected */
export type ImportRejectReason =
  | 'unsupported_format'
  | 'metadata_missing'
  | 'schema_violation'
  | 'encoding_error'
  | 'empty_file';

export interface ImportRecord {
  importId: string;
  sessionId: string;
  filename: string;
  fileSizeBytes: number;
  mimeType: string;
  sourceType: DataSourceType;
  channels: number;
  samples: number;
  samplingRateHz: number;
  durationSeconds: number;
  state: ImportState;
  progress: number; // 0–100
  sha256: string;
  rejectReason?: ImportRejectReason;
  duplicateOfImportId?: string;
  errorMessage?: string;
  stateHistory: ImportStateTransition[];
  createdAt: string;
  updatedAt: string;
}

export interface ImportStateTransition {
  from: ImportState | 'init';
  to: ImportState;
  timestamp: string;
  detail?: string;
}

/** File metadata extracted before upload */
export interface ImportFileMetadata {
  filename: string;
  fileSizeBytes: number;
  mimeType: string;
  lastModified: string;
}

export const IMPORT_SUCCESS_STATES: ImportSuccessState[] = [
  'file_selected', 'hashing', 'local_validation', 'ready_to_upload',
  'uploading', 'server_validation', 'mapping_required', 'normalized', 'qc_ready',
];

export const IMPORT_ERROR_STATES: ImportErrorState[] = [
  'upload_failed', 'import_rejected', 'duplicate_detected', 'quarantined', 'cancelled',
];

export function isImportTerminal(state: ImportState): boolean {
  return state === 'qc_ready' || IMPORT_ERROR_STATES.includes(state as ImportErrorState);
}

export function isImportError(state: ImportState): boolean {
  return IMPORT_ERROR_STATES.includes(state as ImportErrorState);
}
