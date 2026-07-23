import type { ImportState, SignalImportRecord } from "../schemas/import-workflow.schema";

export type ImportEvent =
  | "SELECT_FILE"
  | "START_HASH"
  | "HASH_COMPLETE"
  | "LOCAL_VALIDATION_PASS"
  | "LOCAL_VALIDATION_FAIL"
  | "START_UPLOAD"
  | "UPLOAD_COMPLETE"
  | "UPLOAD_FAIL"
  | "MAPPING_REQUIRED"
  | "NORMALIZED"
  | "MAPPING_COMPLETE"
  | "MARK_QC_READY"
  | "DUPLICATE_FOUND"
  | "QUARANTINE"
  | "CANCEL";

const transitions: Readonly<Record<ImportState, Partial<Record<ImportEvent, ImportState>>>> = {
  draft: { SELECT_FILE: "file_selected", CANCEL: "cancelled" },
  file_selected: { START_HASH: "hashing", CANCEL: "cancelled" },
  hashing: { HASH_COMPLETE: "local_validation", UPLOAD_FAIL: "upload_failed" },
  local_validation: {
    LOCAL_VALIDATION_PASS: "ready_to_upload",
    LOCAL_VALIDATION_FAIL: "unsupported_format",
    DUPLICATE_FOUND: "duplicate_detected",
  },
  ready_to_upload: { START_UPLOAD: "uploading", CANCEL: "cancelled" },
  uploading: { UPLOAD_COMPLETE: "server_validation", UPLOAD_FAIL: "upload_failed" },
  server_validation: {
    MAPPING_REQUIRED: "mapping_required",
    NORMALIZED: "normalized",
    LOCAL_VALIDATION_FAIL: "import_rejected",
    QUARANTINE: "quarantined",
  },
  mapping_required: { MAPPING_COMPLETE: "normalized", CANCEL: "cancelled" },
  normalized: { MARK_QC_READY: "qc_ready" },
  qc_ready: {},
  cancelled: { SELECT_FILE: "file_selected" },
  upload_failed: { START_UPLOAD: "uploading", SELECT_FILE: "file_selected" },
  unsupported_format: { SELECT_FILE: "file_selected" },
  metadata_missing: { SELECT_FILE: "file_selected" },
  duplicate_detected: { SELECT_FILE: "file_selected", START_UPLOAD: "uploading", CANCEL: "cancelled" },
  import_rejected: { SELECT_FILE: "file_selected" },
  quarantined: {},
};

export const nextImportState = (current: ImportState, event: ImportEvent): ImportState => {
  const next = transitions[current][event];
  if (!next) throw new Error(`INVALID_IMPORT_TRANSITION:${current}:${event}`);
  return next;
};

export const importWorkflowReducer = (
  state: SignalImportRecord,
  action: { readonly event: ImportEvent; readonly patch?: Partial<SignalImportRecord> },
): SignalImportRecord => ({
  ...state,
  ...action.patch,
  state: nextImportState(state.state, action.event),
});
