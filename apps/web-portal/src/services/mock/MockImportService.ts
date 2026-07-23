/**
 * MockImportService — Import lifecycle with SHA-256 via Web Crypto.
 * Synthetic fixtures use deterministic hash; real files use browser Web Crypto.
 */
import type { ImportRecord, ImportState, ImportStateTransition } from '@/schemas/import';
import type { DataSourceType } from '@/schemas/common';
import * as repo from './MockWorkflowRepository';
import { EXISTING_DUPLICATE_IMPORT } from './fixtures';

// Seed the duplicate import for duplicate_detected scenario
if (typeof window !== 'undefined') {
  if (!repo.getImport(EXISTING_DUPLICATE_IMPORT.importId)) {
    repo.saveImport(EXISTING_DUPLICATE_IMPORT);
  }
}

/** Compute SHA-256 of a File using Web Crypto API. */
export async function computeSHA256(file: File): Promise<string> {
  const buffer = await file.arrayBuffer();
  const hashBuffer = await crypto.subtle.digest('SHA-256', buffer);
  const hashArray = Array.from(new Uint8Array(hashBuffer));
  return hashArray.map((b) => b.toString(16).padStart(2, '0')).join('');
}

/** Deterministic hash for synthetic data. */
export function syntheticHash(scenarioId: string): string {
  // Deterministic — not random
  const chars = 'abcdef0123456789';
  let hash = '';
  for (let i = 0; i < 64; i++) {
    hash += chars[(scenarioId.charCodeAt(i % scenarioId.length) + i) % chars.length];
  }
  return hash;
}

export function checkDuplicate(sha256: string): ImportRecord | null {
  return repo.findImportByHash(sha256);
}

function transition(rec: ImportRecord, to: ImportState, detail?: string): void {
  const t: ImportStateTransition = {
    from: rec.state,
    to,
    timestamp: new Date().toISOString(),
    detail,
  };
  rec.stateHistory.push(t);
  rec.state = to;
  rec.updatedAt = new Date().toISOString();
}

export function createImport(
  sessionId: string,
  filename: string,
  fileSizeBytes: number,
  mimeType: string,
  sourceType: DataSourceType,
  sha256: string,
): ImportRecord {
  const importId = `IMP-${Date.now().toString(36).toUpperCase()}`;
  const rec: ImportRecord = {
    importId,
    sessionId,
    filename,
    fileSizeBytes,
    mimeType,
    sourceType,
    channels: 0,
    samples: 0,
    samplingRateHz: 0,
    durationSeconds: 0,
    state: 'file_selected',
    progress: 0,
    sha256,
    stateHistory: [{ from: 'init', to: 'file_selected', timestamp: new Date().toISOString() }],
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  };
  repo.saveImport(rec);
  repo.logAudit('import.create', importId, `File: ${filename}, SHA-256: ${sha256.substring(0, 16)}...`);
  return rec;
}

/**
 * Simulate the full import pipeline with delays.
 * Returns a function that advances to the next state each call.
 */
export async function simulateImportPipeline(
  importId: string,
  scenario: 'happy_path' | 'import_rejected' | 'duplicate_detected' | 'timeout_retry' | 'default',
): Promise<ImportRecord | null> {
  const rec = repo.getImport(importId);
  if (!rec) return null;

  // Step 1: Hashing
  transition(rec, 'hashing');
  rec.progress = 10;
  repo.saveImport(rec);

  // Check duplicate
  if (scenario === 'duplicate_detected') {
    const dup = checkDuplicate(rec.sha256);
    if (dup && dup.importId !== rec.importId) {
      transition(rec, 'duplicate_detected', `Trùng với import ${dup.importId}`);
      rec.duplicateOfImportId = dup.importId;
      rec.progress = 10;
      repo.saveImport(rec);
      repo.logAudit('import.duplicate', importId, `Duplicate of ${dup.importId}`);
      return rec;
    }
  }

  // Step 2: Local validation
  transition(rec, 'local_validation');
  rec.progress = 20;
  repo.saveImport(rec);

  // Check format
  if (scenario === 'import_rejected') {
    transition(rec, 'import_rejected', 'Định dạng không được hỗ trợ');
    rec.rejectReason = 'unsupported_format';
    rec.errorMessage = 'Chỉ hỗ trợ CSV, JSON. File .xlsx không được chấp nhận.';
    rec.progress = 20;
    repo.saveImport(rec);
    repo.logAudit('import.rejected', importId, `Reason: unsupported_format`);
    return rec;
  }

  // Step 3: Ready to upload
  transition(rec, 'ready_to_upload');
  rec.progress = 30;
  repo.saveImport(rec);

  // Step 4: Uploading
  transition(rec, 'uploading');
  rec.progress = 50;
  repo.saveImport(rec);

  if (scenario === 'timeout_retry') {
    transition(rec, 'upload_failed', 'Connection timeout after 30s');
    rec.errorMessage = 'Upload timeout — vui lòng thử lại.';
    rec.progress = 50;
    repo.saveImport(rec);
    repo.logAudit('import.upload_failed', importId, 'Timeout');
    return rec;
  }

  // Step 5: Server validation
  transition(rec, 'server_validation');
  rec.progress = 70;
  rec.channels = 4;
  rec.samples = 12000;
  rec.samplingRateHz = 2000;
  rec.durationSeconds = 60;
  repo.saveImport(rec);

  // Step 6: Mapping required
  transition(rec, 'mapping_required');
  rec.progress = 80;
  repo.saveImport(rec);

  // Step 7: Normalized
  transition(rec, 'normalized');
  rec.progress = 90;
  repo.saveImport(rec);

  // Step 8: QC ready
  transition(rec, 'qc_ready');
  rec.progress = 100;
  repo.saveImport(rec);
  repo.logAudit('import.complete', importId, `${rec.channels} channels, ${rec.samples} samples`);

  return rec;
}

export function retryImport(importId: string): ImportRecord | null {
  const rec = repo.getImport(importId);
  if (!rec) return null;
  if (rec.state !== 'upload_failed') return rec;

  transition(rec, 'ready_to_upload', 'Retry initiated');
  rec.progress = 30;
  rec.errorMessage = undefined;
  repo.saveImport(rec);
  repo.logAudit('import.retry', importId, 'Retry after upload_failed');
  return rec;
}

export function cancelImport(importId: string): void {
  const rec = repo.getImport(importId);
  if (!rec) return;
  transition(rec, 'cancelled', 'User cancelled');
  rec.progress = 0;
  repo.saveImport(rec);
  repo.logAudit('import.cancel', importId, 'User cancelled');
}

export function getImport(id: string): ImportRecord | null {
  return repo.getImport(id);
}

export function getImportsBySession(sessionId: string): ImportRecord[] {
  return repo.getImportsBySession(sessionId);
}
