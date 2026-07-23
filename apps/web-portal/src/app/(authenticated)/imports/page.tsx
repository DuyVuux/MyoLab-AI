/**
 * Import List Page — `/imports`
 * Per Section 6.6: Import history with status tracking
 */
'use client';

import Link from 'next/link';
import { Upload, Search, Clock, CheckCircle, AlertTriangle, XCircle, FileText, ArrowRight } from 'lucide-react';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { Card, CardContent } from '@/components/ui/Card';
import { ROUTES } from '@/config/useCaseRoutes';
import styles from './imports.module.css';

interface ImportRecord {
  id: string;
  sessionId: string;
  filename: string;
  sourceType: 'noraxon_mock' | 'csv' | 'synthetic';
  channels: number;
  samples: number;
  duration: string;
  state: 'uploaded' | 'mapping_required' | 'mapped' | 'validated' | 'failed';
  errorMessage?: string;
  createdAt: string;
}

const MOCK_IMPORTS: ImportRecord[] = [
  {
    id: 'IMP-001', sessionId: 'S-001', filename: 'noraxon_export_uc1_001.csv',
    sourceType: 'noraxon_mock', channels: 4, samples: 12000, duration: '60s',
    state: 'validated', createdAt: '2026-07-23T08:30:00',
  },
  {
    id: 'IMP-002', sessionId: 'S-002', filename: 'uc2_assessment_bilateral.csv',
    sourceType: 'csv', channels: 8, samples: 24000, duration: '120s',
    state: 'mapping_required', createdAt: '2026-07-23T07:15:00',
  },
  {
    id: 'IMP-003', sessionId: 'S-003', filename: 'synthetic_demo_004.csv',
    sourceType: 'synthetic', channels: 4, samples: 6000, duration: '30s',
    state: 'failed', errorMessage: 'Column count mismatch: expected 5, got 3',
    createdAt: '2026-07-22T16:45:00',
  },
  {
    id: 'IMP-004', sessionId: 'S-001', filename: 'noraxon_export_uc1_002.csv',
    sourceType: 'noraxon_mock', channels: 4, samples: 18000, duration: '90s',
    state: 'mapped', createdAt: '2026-07-22T14:00:00',
  },
];

function getStateInfo(state: ImportRecord['state']) {
  switch (state) {
    case 'validated': return { variant: 'success' as const, label: 'Validated', icon: CheckCircle };
    case 'mapped': return { variant: 'success' as const, label: 'Mapped', icon: CheckCircle };
    case 'mapping_required': return { variant: 'warning' as const, label: 'Cần mapping', icon: AlertTriangle };
    case 'uploaded': return { variant: 'info' as const, label: 'Uploaded', icon: Clock };
    case 'failed': return { variant: 'error' as const, label: 'Failed', icon: XCircle };
    default: return { variant: 'neutral' as const, label: state, icon: Clock };
  }
}

function getSourceLabel(source: ImportRecord['sourceType']) {
  switch (source) {
    case 'noraxon_mock': return 'Noraxon mock';
    case 'csv': return 'Generic CSV';
    case 'synthetic': return 'Synthetic';
    default: return source;
  }
}

export default function ImportsPage() {
  return (
    <div className="page-container">
      <div className="page-header">
        <div className="page-header__left">
          <h1 className="page-title">Import dữ liệu</h1>
          <p className="page-subtitle">Lịch sử import và trạng thái xử lý.</p>
        </div>
        <div className="page-header__right">
          <Link href={ROUTES.SESSION_NEW}>
            <Button icon={<Upload size={16} />}>Import mới</Button>
          </Link>
        </div>
      </div>

      <div className={styles.tableWrap}>
        <table className={styles.table}>
          <thead>
            <tr>
              <th>Import ID</th>
              <th>Session</th>
              <th>Tệp</th>
              <th>Nguồn</th>
              <th>Kênh</th>
              <th>Mẫu</th>
              <th>Trạng thái</th>
              <th>Hành động</th>
            </tr>
          </thead>
          <tbody>
            {MOCK_IMPORTS.map((imp) => {
              const stateInfo = getStateInfo(imp.state);
              return (
                <tr key={imp.id}>
                  <td>
                    <span className={styles.monoText}>{imp.id}</span>
                  </td>
                  <td>
                    <Link href={`/sessions/${imp.sessionId}/context`} className={styles.link}>
                      {imp.sessionId}
                    </Link>
                  </td>
                  <td>
                    <div className={styles.fileCell}>
                      <FileText size={14} />
                      <span className={styles.filename}>{imp.filename}</span>
                    </div>
                  </td>
                  <td>
                    <Badge variant={
                      imp.sourceType === 'synthetic' ? 'source-synthetic'
                        : imp.sourceType === 'noraxon_mock' ? 'source-local'
                          : 'neutral'
                    } size="sm">
                      {getSourceLabel(imp.sourceType)}
                    </Badge>
                  </td>
                  <td>{imp.channels}</td>
                  <td>{imp.samples.toLocaleString()}</td>
                  <td>
                    <Badge variant={stateInfo.variant} size="sm">{stateInfo.label}</Badge>
                    {imp.errorMessage && (
                      <div className={styles.errorText}>{imp.errorMessage}</div>
                    )}
                  </td>
                  <td>
                    {imp.state === 'mapping_required' ? (
                      <Link href={`/sessions/${imp.sessionId}/mapping`}>
                        <Button variant="ghost" size="sm">Mapping</Button>
                      </Link>
                    ) : imp.state === 'failed' ? (
                      <Button variant="ghost" size="sm">Thử lại</Button>
                    ) : (
                      <Link href={`/sessions/${imp.sessionId}/context`}>
                        <Button variant="ghost" size="sm" icon={<ArrowRight size={12} />}>Xem</Button>
                      </Link>
                    )}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
