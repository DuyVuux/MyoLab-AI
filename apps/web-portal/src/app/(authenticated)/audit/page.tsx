/**
 * Audit Viewer — `/audit`
 * Per Section 11: Hash-chain audit log viewer
 */
'use client';

import { Shield, CheckCircle, AlertTriangle, Search, Clock, User, Activity } from 'lucide-react';
import { Badge } from '@/components/ui/Badge';
import { Card, CardContent } from '@/components/ui/Card';
import { Alert } from '@/components/ui/Alert';
import styles from './audit.module.css';

interface AuditEntry {
  id: string;
  timestamp: string;
  actor: string;
  actorRole: string;
  action: string;
  resource: string;
  detail: string;
  entryHash: string;
  previousHash: string;
  chainValid: boolean;
}

const MOCK_AUDIT: AuditEntry[] = [
  { id: 'AUD-007', timestamp: '2026-07-23T09:15:00', actor: 'Trần Thị B', actorRole: 'ktv', action: 'feedback.create', resource: 'FB-001', detail: 'Created correction feedback for session S-001', entryHash: 'a3f8c2...e91d', previousHash: 'b7d1a5...4f2c', chainValid: true },
  { id: 'AUD-006', timestamp: '2026-07-23T08:32:00', actor: 'System', actorRole: 'system', action: 'analysis.complete', resource: 'AJ-001', detail: 'Gesture recognition completed for session S-001', entryHash: 'b7d1a5...4f2c', previousHash: 'c4e9b3...8a7d', chainValid: true },
  { id: 'AUD-005', timestamp: '2026-07-23T08:30:00', actor: 'Trần Thị B', actorRole: 'ktv', action: 'qc.pass', resource: 'S-001', detail: 'QC passed for session S-001 (4/4 channels)', entryHash: 'c4e9b3...8a7d', previousHash: 'd2f7a1...6b3e', chainValid: true },
  { id: 'AUD-004', timestamp: '2026-07-23T07:20:00', actor: 'System', actorRole: 'system', action: 'qc.fail', resource: 'S-002', detail: 'QC failed: CH3 SNR=5.2dB, CH4 saturation=8.3%', entryHash: 'd2f7a1...6b3e', previousHash: 'e5c8d4...2a9f', chainValid: true },
  { id: 'AUD-003', timestamp: '2026-07-23T07:16:00', actor: 'System', actorRole: 'system', action: 'analysis.abstain', resource: 'AJ-002', detail: 'AI abstained: QC prerequisite not met', entryHash: 'e5c8d4...2a9f', previousHash: 'f1b6e7...5c4a', chainValid: true },
  { id: 'AUD-002', timestamp: '2026-07-23T07:15:00', actor: 'Trần Thị B', actorRole: 'ktv', action: 'import.complete', resource: 'IMP-002', detail: 'Import completed for S-002 (8 channels, 24000 samples)', entryHash: 'f1b6e7...5c4a', previousHash: 'g0a5d9...3b8c', chainValid: true },
  { id: 'AUD-001', timestamp: '2026-07-23T06:45:00', actor: 'Trần Thị B', actorRole: 'ktv', action: 'session.create', resource: 'S-003', detail: 'Created session S-003 for SUBJ-003 (UC2)', entryHash: 'g0a5d9...3b8c', previousHash: '0000000...0000', chainValid: true },
];

const allValid = MOCK_AUDIT.every((e) => e.chainValid);

export default function AuditPage() {
  return (
    <div className="page-container">
      <div className="page-header">
        <div className="page-header__left">
          <h1 className="page-title">Audit Log</h1>
          <p className="page-subtitle">
            Nhật ký kiểm toán hash-chain chống giả mạo — mọi hành động được ghi lại.
          </p>
        </div>
      </div>

      {/* Chain integrity */}
      <Alert
        variant={allValid ? 'success' : 'error'}
        title={allValid ? 'Hash-chain integrity: VALID ✓' : 'Hash-chain integrity: BROKEN ✗'}
      >
        {allValid
          ? `Toàn bộ ${MOCK_AUDIT.length} bản ghi đã được verify. Không phát hiện tampering.`
          : 'CẢNH BÁO: Phát hiện bất thường trong chuỗi hash. Liên hệ admin ngay lập tức.'}
      </Alert>

      {/* Audit log */}
      <div className={styles.logList}>
        {MOCK_AUDIT.map((entry) => (
          <div key={entry.id} className={styles.logEntry}>
            <div className={styles.logTime}>
              <Clock size={12} />
              <span>{new Date(entry.timestamp).toLocaleString('vi-VN')}</span>
            </div>
            <div className={styles.logContent}>
              <div className={styles.logHeader}>
                <span className={styles.logId}>{entry.id}</span>
                <Badge variant={entry.action.includes('fail') || entry.action.includes('abstain') ? 'warning' : 'success'} size="sm">
                  {entry.action}
                </Badge>
                <span className={styles.logActor}>
                  <User size={12} /> {entry.actor} ({entry.actorRole})
                </span>
              </div>
              <p className={styles.logDetail}>{entry.detail}</p>
              <div className={styles.logHash}>
                <span>Hash: <code>{entry.entryHash}</code></span>
                <span>Prev: <code>{entry.previousHash}</code></span>
                {entry.chainValid && <CheckCircle size={12} className={styles.hashValid} />}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
