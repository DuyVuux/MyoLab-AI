/**
 * Import Center — `/sessions/[sessionId]/import`
 * Full state machine: 9 success + 5 error states.
 * Drag-drop, SHA-256 via Web Crypto, duplicate detection, progress, retry, receipt.
 */
'use client';

import { useState, useEffect, useCallback, useRef } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { Upload, FileText, Hash, CheckCircle, XCircle, AlertTriangle, RefreshCw, ArrowRight, ArrowLeft, Copy, Loader } from 'lucide-react';
import { Card, CardContent, CardHeader } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { Alert } from '@/components/ui/Alert';
import type { ImportRecord, ImportState } from '@/schemas/import';
import { IMPORT_SUCCESS_STATES, isImportError } from '@/schemas/import';
import * as SessionService from '@/services/mock/MockSessionService';
import * as ImportService from '@/services/mock/MockImportService';
import * as SignalService from '@/services/mock/MockSignalWorkflowService';
import * as repo from '@/services/mock/MockWorkflowRepository';
import styles from './import.module.css';

const STATE_LABELS: Record<ImportState, string> = {
  file_selected: 'File đã chọn',
  hashing: 'Đang tính SHA-256...',
  local_validation: 'Kiểm tra cục bộ',
  ready_to_upload: 'Sẵn sàng upload',
  uploading: 'Đang upload...',
  server_validation: 'Server đang validate',
  mapping_required: 'Cần mapping kênh',
  normalized: 'Đã chuẩn hóa',
  qc_ready: 'Sẵn sàng QC',
  upload_failed: 'Upload thất bại',
  import_rejected: 'Bị từ chối',
  duplicate_detected: 'Trùng lặp phát hiện',
  quarantined: 'Đã cách ly',
  cancelled: 'Đã hủy',
};

export default function ImportCenterPage() {
  const params = useParams();
  const router = useRouter();
  const sessionId = params.sessionId as string;
  const fileInputRef = useRef<HTMLInputElement>(null);

  const [importRecord, setImportRecord] = useState<ImportRecord | null>(null);
  const [dragOver, setDragOver] = useState(false);
  const [processing, setProcessing] = useState(false);
  const [hashProgress, setHashProgress] = useState('');
  const [error, setError] = useState('');

  useEffect(() => {
    const session = SessionService.getSession(sessionId);
    if (!session || session.state === 'draft') {
      router.replace(`/sessions/${sessionId}/context`);
      return;
    }
    // Check existing import
    const existing = ImportService.getImportsBySession(sessionId);
    const active = existing.find((i) => i.state !== 'cancelled');
    if (active) setImportRecord(active);
  }, [sessionId, router]);

  const processFile = useCallback(async (file: File) => {
    setProcessing(true);
    setError('');
    setHashProgress('Đang tính SHA-256...');

    // Real SHA-256 via Web Crypto
    let sha256: string;
    try {
      sha256 = await ImportService.computeSHA256(file);
    } catch {
      sha256 = ImportService.syntheticHash(file.name);
    }
    setHashProgress(`SHA-256: ${sha256.substring(0, 16)}...`);

    // Check duplicate
    const dup = ImportService.checkDuplicate(sha256);
    if (dup) {
      const rec = ImportService.createImport(sessionId, file.name, file.size, file.type || 'text/csv', 'csv_json', sha256);
      rec.state = 'duplicate_detected';
      rec.duplicateOfImportId = dup.importId;
      rec.stateHistory.push({ from: 'file_selected', to: 'duplicate_detected', timestamp: new Date().toISOString(), detail: `Duplicate of ${dup.importId}` });
      repo.saveImport(rec);
      setImportRecord(rec);
      setProcessing(false);
      return;
    }

    // Determine scenario
    const ext = file.name.split('.').pop()?.toLowerCase();
    let scenario: 'happy_path' | 'import_rejected' | 'duplicate_detected' | 'timeout_retry' | 'default' = 'happy_path';
    if (ext === 'xlsx' || ext === 'xls') scenario = 'import_rejected';
    else if (file.size > 3 * 1024 * 1024) scenario = 'timeout_retry';

    const rec = ImportService.createImport(sessionId, file.name, file.size, file.type || 'text/csv', 'csv_json', sha256);
    setImportRecord(rec);

    // Simulate pipeline with delays
    const states: ImportState[] = ['hashing', 'local_validation', 'ready_to_upload', 'uploading', 'server_validation', 'mapping_required', 'normalized', 'qc_ready'];

    for (const state of states) {
      await new Promise((resolve) => setTimeout(resolve, 400));
      const result = await ImportService.simulateImportPipeline(rec.importId, scenario);
      if (result) {
        setImportRecord({ ...result });
        if (isImportError(result.state)) break;
      }
      break; // Pipeline runs all at once in the service, just update the final state
    }

    // Get final state
    const final = ImportService.getImport(rec.importId);
    if (final) {
      setImportRecord({ ...final });
      if (final.state === 'qc_ready') {
        SignalService.initializeMappings(sessionId, final.channels || 4, 'happy_path');
        repo.updateSessionState(sessionId, 'import_complete');
      }
    }
    setProcessing(false);
  }, [sessionId]);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    const file = e.dataTransfer.files[0];
    if (file) processFile(file);
  }, [processFile]);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) processFile(file);
  };

  const handleRetry = async () => {
    if (!importRecord) return;
    setProcessing(true);
    const retried = ImportService.retryImport(importRecord.importId);
    if (retried) {
      const result = await ImportService.simulateImportPipeline(retried.importId, 'happy_path');
      if (result) setImportRecord({ ...result });
    }
    setProcessing(false);
  };

  const handleCancel = () => {
    if (!importRecord) return;
    ImportService.cancelImport(importRecord.importId);
    setImportRecord(null);
  };

  const handleContinue = () => {
    router.push(`/sessions/${sessionId}/mapping`);
  };

  const progressPct = importRecord ? importRecord.progress : 0;
  const isComplete = importRecord?.state === 'qc_ready';
  const isError = importRecord ? isImportError(importRecord.state) : false;
  const isDuplicate = importRecord?.state === 'duplicate_detected';

  return (
    <div className="page-container">
      <div className="page-header">
        <div className="page-header__left">
          <h1 className="page-title">Import Center</h1>
          <p className="page-subtitle">Session: <code>{sessionId}</code> — Tải lên file dữ liệu sEMG.</p>
        </div>
      </div>

      {/* Drop zone */}
      {!importRecord && (
        <div
          className={[styles.dropZone, dragOver ? styles['dropZone--active'] : ''].filter(Boolean).join(' ')}
          onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
          onDragLeave={() => setDragOver(false)}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
          role="button"
          tabIndex={0}
          onKeyDown={(e) => { if (e.key === 'Enter' || e.key === ' ') fileInputRef.current?.click(); }}
          aria-label="Kéo thả file hoặc nhấn để chọn"
        >
          <Upload size={48} className={styles.dropIcon} />
          <p className={styles.dropTitle}>Kéo thả file vào đây</p>
          <p className={styles.dropHint}>hoặc nhấn để chọn file — CSV, JSON hỗ trợ</p>
          <input ref={fileInputRef} type="file" accept=".csv,.json,.txt" onChange={handleFileSelect} className={styles.hiddenInput} />
        </div>
      )}

      {/* Import progress & state */}
      {importRecord && (
        <Card padding="lg">
          <CardHeader>
            <div className={styles.importHeader}>
              <FileText size={20} />
              <div>
                <h3 className={styles.importFilename}>{importRecord.filename}</h3>
                <p className={styles.importMeta}>
                  {(importRecord.fileSizeBytes / 1024).toFixed(1)} KB · Import ID: <code>{importRecord.importId}</code>
                </p>
              </div>
              <Badge variant={isComplete ? 'success' : isError ? 'error' : 'info'}>
                {STATE_LABELS[importRecord.state]}
              </Badge>
            </div>
          </CardHeader>
          <CardContent>
            {/* SHA-256 */}
            <div className={styles.hashRow}>
              <Hash size={14} />
              <span>SHA-256: <code>{importRecord.sha256.substring(0, 32)}...</code></span>
            </div>

            {/* Progress bar */}
            <div className={styles.progressContainer}>
              <div className={styles.progressBar}>
                <div className={[styles.progressFill, isError ? styles['progressFill--error'] : ''].filter(Boolean).join(' ')} style={{ width: `${progressPct}%` }} />
              </div>
              <span className={styles.progressLabel}>{progressPct}%</span>
            </div>

            {/* State timeline */}
            <div className={styles.timeline}>
              {IMPORT_SUCCESS_STATES.map((state, idx) => {
                const currentIdx = IMPORT_SUCCESS_STATES.indexOf(importRecord.state as typeof state);
                const isPast = !isError && currentIdx >= 0 && idx <= currentIdx;
                const isCurrent = !isError && idx === currentIdx;
                return (
                  <div key={state} className={[styles.timelineStep, isPast ? styles['timelineStep--done'] : '', isCurrent ? styles['timelineStep--current'] : ''].filter(Boolean).join(' ')}>
                    <div className={styles.timelineDot}>
                      {isPast && !isCurrent ? <CheckCircle size={14} /> : <span className={styles.dotInner} />}
                    </div>
                    <span className={styles.timelineLabel}>{STATE_LABELS[state]}</span>
                  </div>
                );
              })}
            </div>

            {/* Error details */}
            {isError && !isDuplicate && (
              <Alert variant="error" title={STATE_LABELS[importRecord.state]}>
                {importRecord.errorMessage || `Import thất bại ở trạng thái: ${importRecord.state}`}
                {importRecord.rejectReason && <p>Lý do: <code>{importRecord.rejectReason}</code></p>}
              </Alert>
            )}

            {/* Duplicate warning */}
            {isDuplicate && (
              <Alert variant="warning" title="Phát hiện trùng lặp — Import bị chặn">
                File này đã tồn tại trong hệ thống với Import ID: <code>{importRecord.duplicateOfImportId}</code>.
                <br />Không tự ghi đè. Vui lòng mở import hiện có hoặc chọn file khác.
                <div style={{ marginTop: 'var(--space-3)' }}>
                  <Button variant="secondary" size="sm" onClick={() => router.push(`/imports/${importRecord.duplicateOfImportId}`)}>
                    Mở import hiện có
                  </Button>
                </div>
              </Alert>
            )}

            {/* Actions */}
            <div className={styles.importActions}>
              {importRecord.state === 'upload_failed' && (
                <Button variant="secondary" onClick={handleRetry} icon={<RefreshCw size={16} />} disabled={processing}>
                  {processing ? 'Đang thử lại...' : 'Thử lại'}
                </Button>
              )}
              {!isComplete && (
                <Button variant="ghost" onClick={handleCancel}>Hủy & chọn file khác</Button>
              )}
            </div>

            {/* Receipt */}
            {isComplete && (
              <div className={styles.receipt}>
                <CheckCircle size={20} className={styles.receiptIcon} />
                <div>
                  <h4 className={styles.receiptTitle}>Import hoàn tất</h4>
                  <div className={styles.receiptGrid}>
                    <span>Import ID:</span><code>{importRecord.importId}</code>
                    <span>Kênh:</span><span>{importRecord.channels}</span>
                    <span>Mẫu:</span><span>{importRecord.samples?.toLocaleString()}</span>
                    <span>Tần số:</span><span>{importRecord.samplingRateHz} Hz</span>
                    <span>Thời lượng:</span><span>{importRecord.durationSeconds}s</span>
                    <span>SHA-256:</span><code>{importRecord.sha256.substring(0, 24)}...</code>
                  </div>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      <div className={styles.actions}>
        <Button variant="ghost" onClick={() => router.push(`/sessions/${sessionId}/data-source`)} icon={<ArrowLeft size={16} />}>Quay lại</Button>
        <div className={styles.spacer} />
        {isComplete && (
          <Button onClick={handleContinue} icon={<ArrowRight size={16} />} iconPosition="right">
            Tiếp tục → Channel Mapping
          </Button>
        )}
      </div>
    </div>
  );
}
