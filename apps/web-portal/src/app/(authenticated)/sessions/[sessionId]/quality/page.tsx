/**
 * Quality Gate — `/sessions/[sessionId]/quality`
 * QC fail blocks analysis. QC warning requires structured acknowledgement (reason codes).
 * Distinct: import_rejected vs warning vs abstained vs failed.
 */
'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { CheckCircle, AlertTriangle, XCircle, ArrowRight, ArrowLeft, Shield } from 'lucide-react';
import { Card, CardContent, CardHeader } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { Alert } from '@/components/ui/Alert';
import type { QCResult, QCVerdict, QCAcknowledgementReason, QCChannelResult } from '@/schemas/quality';
import { QC_ACKNOWLEDGEMENT_LABELS } from '@/schemas/quality';
import * as SessionService from '@/services/mock/MockSessionService';
import * as ImportService from '@/services/mock/MockImportService';
import * as SignalService from '@/services/mock/MockSignalWorkflowService';
import { useAuth } from '@/lib/auth';
import styles from './quality.module.css';

const VERDICT_CONFIG: Record<QCVerdict, { variant: 'success' | 'warning' | 'error'; label: string; icon: typeof CheckCircle }> = {
  pass: { variant: 'success', label: 'QC PASS ✓', icon: CheckCircle },
  warning: { variant: 'warning', label: 'QC WARNING ⚠', icon: AlertTriangle },
  fail: { variant: 'error', label: 'QC FAIL ✗', icon: XCircle },
};

export default function QualityPage() {
  const params = useParams();
  const router = useRouter();
  const { user } = useAuth();
  const sessionId = params.sessionId as string;

  const [qcResult, setQcResult] = useState<QCResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedReason, setSelectedReason] = useState<QCAcknowledgementReason | ''>('');
  const [additionalNote, setAdditionalNote] = useState('');

  useEffect(() => {
    const session = SessionService.getSession(sessionId);
    if (!session || session.state === 'draft') {
      router.replace(`/sessions/${sessionId}/context`);
      return;
    }

    let result = SignalService.getQCResult(sessionId);
    if (!result) {
      const imports = ImportService.getImportsBySession(sessionId);
      const activeImport = imports.find((i) => i.state === 'qc_ready' || i.state === 'normalized');
      const importId = activeImport?.importId ?? 'IMP-MOCK';
      result = SignalService.runQC(sessionId, importId, 'happy_path');
    }
    setQcResult(result);
    setLoading(false);
  }, [sessionId, router]);

  const handleAcknowledge = () => {
    if (!selectedReason || !qcResult) return;
    const updated = SignalService.acknowledgeQCWarning(sessionId, {
      reasonCode: selectedReason,
      additionalNote,
      acknowledgedBy: user?.name ?? 'Unknown',
      timestamp: new Date().toISOString(),
    });
    if (updated) setQcResult({ ...updated });
  };

  const handleContinue = () => {
    router.push(`/sessions/${sessionId}/analysis`);
  };

  if (loading) return <div className="page-container"><p>Đang chạy QC...</p></div>;
  if (!qcResult) return <div className="page-container"><Alert variant="error" title="Lỗi">Không thể chạy QC.</Alert></div>;

  const verdict = VERDICT_CONFIG[qcResult.overallVerdict];
  const VerdictIcon = verdict.icon;
  const canProceed = qcResult.overallVerdict === 'pass' || (qcResult.overallVerdict === 'warning' && !!qcResult.acknowledgement);
  const needsAck = qcResult.overallVerdict === 'warning' && !qcResult.acknowledgement;
  const isBlocked = qcResult.overallVerdict === 'fail';

  return (
    <div className="page-container">
      <div className="page-header">
        <div className="page-header__left">
          <h1 className="page-title">Quality Gate</h1>
          <p className="page-subtitle">Đánh giá chất lượng tín hiệu trước analysis.</p>
        </div>
        <div className="page-header__right">
          <Badge variant={verdict.variant} size="md">{verdict.label}</Badge>
        </div>
      </div>

      {/* Verdict banner */}
      <Alert variant={verdict.variant} title={verdict.label}>
        {qcResult.overallVerdict === 'pass' && 'Tất cả kênh đều pass kiểm tra chất lượng. Sẵn sàng analysis.'}
        {qcResult.overallVerdict === 'warning' && 'Một số kênh có cảnh báo. Cần xác nhận lý do trước khi tiếp tục.'}
        {qcResult.overallVerdict === 'fail' && 'QC thất bại — không thể chạy analysis. Cần import dữ liệu mới hoặc kiểm tra thiết bị.'}
      </Alert>

      {/* Per-channel results */}
      <Card padding="md">
        <CardHeader><h2 className={styles.sectionTitle}>Kết quả theo kênh</h2></CardHeader>
        <CardContent>
          <div className={styles.channelGrid}>
            {qcResult.channelResults.map((ch) => (
              <ChannelCard key={ch.channelId} channel={ch} />
            ))}
          </div>
        </CardContent>
      </Card>

      {/* QC Warning Acknowledgement */}
      {needsAck && (
        <Card padding="lg">
          <CardHeader>
            <h2 className={styles.sectionTitle}>Xác nhận QC Warning</h2>
          </CardHeader>
          <CardContent>
            <p className={styles.ackDesc}>Chọn lý do chấp nhận cảnh báo QC. Hành động này được ghi audit log.</p>
            <div className={styles.reasonList}>
              {(Object.entries(QC_ACKNOWLEDGEMENT_LABELS) as [QCAcknowledgementReason, string][]).map(([code, label]) => (
                <label key={code} className={[styles.reasonItem, selectedReason === code ? styles['reasonItem--active'] : ''].filter(Boolean).join(' ')}>
                  <input
                    type="radio"
                    name="ackReason"
                    value={code}
                    checked={selectedReason === code}
                    onChange={() => setSelectedReason(code)}
                    className={styles.radioInput}
                  />
                  <div>
                    <div className={styles.reasonCode}>{code}</div>
                    <div className={styles.reasonLabel}>{label}</div>
                  </div>
                </label>
              ))}
            </div>
            <div className={styles.noteField}>
              <label className={styles.noteLabel}>Ghi chú bổ sung (tùy chọn)</label>
              <textarea
                value={additionalNote}
                onChange={(e) => setAdditionalNote(e.target.value)}
                className={styles.textarea}
                placeholder="Thêm ghi chú nếu cần..."
                rows={2}
              />
            </div>
            <Button onClick={handleAcknowledge} disabled={!selectedReason} icon={<Shield size={16} />}>
              Xác nhận & Tiếp tục
            </Button>
          </CardContent>
        </Card>
      )}

      {/* Acknowledged badge */}
      {qcResult.acknowledgement && (
        <Alert variant="info" title="Đã xác nhận QC Warning">
          Lý do: <strong>{QC_ACKNOWLEDGEMENT_LABELS[qcResult.acknowledgement.reasonCode]}</strong>
          <br />Người xác nhận: {qcResult.acknowledgement.acknowledgedBy}
          <br />Thời gian: {new Date(qcResult.acknowledgement.timestamp).toLocaleString('vi-VN')}
          {qcResult.acknowledgement.additionalNote && <><br />Ghi chú: {qcResult.acknowledgement.additionalNote}</>}
        </Alert>
      )}

      {/* Blocked message */}
      {isBlocked && (
        <Alert variant="error" title="Analysis bị chặn">
          QC fail — không thể chạy analysis. Vui lòng:
          <ul style={{ marginTop: 'var(--space-2)' }}>
            <li>Kiểm tra lại thiết bị và kết nối điện cực</li>
            <li>Import lại dữ liệu từ phiên thu mới</li>
            <li>Liên hệ senior KTV để hỗ trợ</li>
          </ul>
        </Alert>
      )}

      <div className={styles.actions}>
        <Button variant="ghost" onClick={() => router.push(`/sessions/${sessionId}/calibration`)} icon={<ArrowLeft size={16} />}>Quay lại Calibration</Button>
        <div className={styles.spacer} />
        <Button onClick={handleContinue} disabled={!canProceed} icon={<ArrowRight size={16} />} iconPosition="right">
          {isBlocked ? 'Analysis bị chặn' : 'Tiếp tục → Analysis'}
        </Button>
      </div>
    </div>
  );
}

function ChannelCard({ channel }: { channel: QCChannelResult }) {
  return (
    <div className={[styles.channelCard, styles[`channelCard--${channel.verdict}`]].join(' ')}>
      <div className={styles.channelHeader}>
        <strong>{channel.channelLabel}</strong>
        <span className={styles.channelMuscle}>{channel.muscle} ({channel.side})</span>
        <Badge variant={channel.verdict === 'pass' ? 'success' : channel.verdict === 'warning' ? 'warning' : 'error'} size="sm">
          {channel.verdict.toUpperCase()}
        </Badge>
      </div>
      <div className={styles.checksGrid}>
        {channel.checks.map((check) => (
          <div key={check.id} className={styles.checkRow}>
            <span className={styles.checkLabel}>{check.label}</span>
            <span className={styles.checkValue}>
              {typeof check.value === 'number' ? check.value.toFixed(1) : check.value} {check.unit}
            </span>
            <span className={styles.checkThreshold}>
              {check.thresholdDirection === 'gte' ? '≥' : '≤'} {check.threshold} {check.unit}
            </span>
            <Badge variant={check.status === 'pass' ? 'success' : check.status === 'warning' ? 'warning' : 'error'} size="sm">
              {check.status}
            </Badge>
          </div>
        ))}
      </div>
    </div>
  );
}
