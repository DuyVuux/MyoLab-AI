/**
 * Import Detail — `/imports/[importId]`
 * Shows import metadata, hash, state timeline, file info.
 */
'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { FileText, Hash, Clock, ArrowLeft, CheckCircle, XCircle, ArrowRight } from 'lucide-react';
import { Card, CardContent, CardHeader } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { Alert } from '@/components/ui/Alert';
import type { ImportRecord } from '@/schemas/import';
import { isImportError } from '@/schemas/import';
import * as ImportService from '@/services/mock/MockImportService';
import styles from './import-detail.module.css';

export default function ImportDetailPage() {
  const params = useParams();
  const router = useRouter();
  const importId = params.importId as string;

  const [record, setRecord] = useState<ImportRecord | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const rec = ImportService.getImport(importId);
    setRecord(rec);
    setLoading(false);
  }, [importId]);

  if (loading) return <div className="page-container"><p>Đang tải...</p></div>;
  if (!record) return (
    <div className="page-container">
      <Alert variant="error" title="Import không tồn tại">
        Import ID: <code>{importId}</code> không tìm thấy.
      </Alert>
      <Button variant="ghost" onClick={() => router.back()} icon={<ArrowLeft size={16} />}>Quay lại</Button>
    </div>
  );

  const isError = isImportError(record.state);

  return (
    <div className="page-container">
      <div className="page-header">
        <div className="page-header__left">
          <h1 className="page-title">Chi tiết Import</h1>
          <p className="page-subtitle">Import ID: <code>{record.importId}</code></p>
        </div>
        <div className="page-header__right">
          <Badge variant={record.state === 'qc_ready' ? 'success' : isError ? 'error' : 'info'}>
            {record.state}
          </Badge>
        </div>
      </div>

      <div className={styles.grid}>
        <Card padding="md">
          <CardHeader><h2 style={{ fontSize: 'var(--font-size-md)', fontWeight: 600 }}>File Metadata</h2></CardHeader>
          <CardContent>
            <div className={styles.metaGrid}>
              <span>Filename:</span><span>{record.filename}</span>
              <span>Size:</span><span>{(record.fileSizeBytes / 1024).toFixed(1)} KB</span>
              <span>MIME:</span><span>{record.mimeType}</span>
              <span>Source:</span><Badge variant="neutral" size="sm">{record.sourceType}</Badge>
              <span>Session:</span><code>{record.sessionId}</code>
              <span>Created:</span><span>{new Date(record.createdAt).toLocaleString('vi-VN')}</span>
              <span>Updated:</span><span>{new Date(record.updatedAt).toLocaleString('vi-VN')}</span>
            </div>
          </CardContent>
        </Card>

        <Card padding="md">
          <CardHeader><h2 style={{ fontSize: 'var(--font-size-md)', fontWeight: 600 }}>Signal Info</h2></CardHeader>
          <CardContent>
            <div className={styles.metaGrid}>
              <span>Channels:</span><span>{record.channels || '—'}</span>
              <span>Samples:</span><span>{record.samples?.toLocaleString() || '—'}</span>
              <span>Sampling rate:</span><span>{record.samplingRateHz ? `${record.samplingRateHz} Hz` : '—'}</span>
              <span>Duration:</span><span>{record.durationSeconds ? `${record.durationSeconds}s` : '—'}</span>
              <span>Progress:</span><span>{record.progress}%</span>
            </div>
          </CardContent>
        </Card>
      </div>

      <Card padding="md">
        <CardHeader><h2 style={{ fontSize: 'var(--font-size-md)', fontWeight: 600 }}>Integrity</h2></CardHeader>
        <CardContent>
          <div className={styles.hashDisplay}>
            <Hash size={16} />
            <span>SHA-256:</span>
            <code className={styles.hashCode}>{record.sha256}</code>
          </div>
          {record.duplicateOfImportId && (
            <Alert variant="warning" title="Trùng lặp">
              Duplicate of: <code>{record.duplicateOfImportId}</code>
            </Alert>
          )}
          {record.rejectReason && (
            <Alert variant="error" title="Bị từ chối">
              Reason code: <code>{record.rejectReason}</code>
              {record.errorMessage && <p>{record.errorMessage}</p>}
            </Alert>
          )}
        </CardContent>
      </Card>

      {/* State history timeline */}
      <Card padding="md">
        <CardHeader><h2 style={{ fontSize: 'var(--font-size-md)', fontWeight: 600 }}>State Timeline</h2></CardHeader>
        <CardContent>
          <div className={styles.stateTimeline}>
            {record.stateHistory.map((t, idx) => (
              <div key={idx} className={styles.stateEntry}>
                <div className={styles.stateIcon}>
                  {isImportError(t.to) ? <XCircle size={14} style={{ color: 'var(--color-error)' }} /> : <CheckCircle size={14} style={{ color: 'var(--color-success)' }} />}
                </div>
                <div>
                  <span className={styles.stateTransition}>{t.from} → <strong>{t.to}</strong></span>
                  <span className={styles.stateTime}>{new Date(t.timestamp).toLocaleTimeString('vi-VN')}</span>
                  {t.detail && <span className={styles.stateDetail}>{t.detail}</span>}
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      <div className={styles.actions}>
        <Button variant="ghost" onClick={() => router.back()} icon={<ArrowLeft size={16} />}>Quay lại</Button>
        {record.state === 'qc_ready' && (
          <Button onClick={() => router.push(`/sessions/${record.sessionId}/mapping`)} icon={<ArrowRight size={16} />} iconPosition="right">
            Đến Mapping
          </Button>
        )}
      </div>
    </div>
  );
}
