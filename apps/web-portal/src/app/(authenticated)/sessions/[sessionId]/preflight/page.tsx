/**
 * Preflight — `/sessions/[sessionId]/preflight`
 * 10 checks, signal preview per channel, 3 outcomes: ready | mapping_required | import_blocked.
 */
'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { CheckCircle, AlertTriangle, XCircle, ArrowRight, ArrowLeft, Activity, RefreshCw } from 'lucide-react';
import { Card, CardContent, CardHeader } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { Alert } from '@/components/ui/Alert';
import type { PreflightResult, PreflightOutcome } from '@/schemas/preflight';
import * as SessionService from '@/services/mock/MockSessionService';
import * as ImportService from '@/services/mock/MockImportService';
import * as SignalService from '@/services/mock/MockSignalWorkflowService';
import styles from './preflight.module.css';

const OUTCOME_CONFIG: Record<PreflightOutcome, { variant: 'success' | 'warning' | 'error'; label: string; message: string }> = {
  ready: { variant: 'success', label: 'READY ✓', message: 'Tất cả kiểm tra đều pass. Có thể tiếp tục.' },
  mapping_required: { variant: 'warning', label: 'MAPPING REQUIRED', message: 'Số kênh không khớp protocol. Quay lại Mapping để sửa.' },
  import_blocked: { variant: 'error', label: 'IMPORT BLOCKED', message: 'Lỗi nghiêm trọng trong dữ liệu. Cần import lại với file khác.' },
};

export default function PreflightPage() {
  const params = useParams();
  const router = useRouter();
  const sessionId = params.sessionId as string;

  const [result, setResult] = useState<PreflightResult | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const session = SessionService.getSession(sessionId);
    if (!session || session.state === 'draft') {
      router.replace(`/sessions/${sessionId}/context`);
      return;
    }

    let pf = SignalService.getPreflight(sessionId);
    if (!pf) {
      const imports = ImportService.getImportsBySession(sessionId);
      const activeImport = imports.find((i) => i.state === 'qc_ready' || i.state === 'normalized');
      const importId = activeImport?.importId ?? 'IMP-MOCK';
      pf = SignalService.runPreflight(sessionId, importId, 'happy_path');
    }
    setResult(pf);
    setLoading(false);
  }, [sessionId, router]);

  if (loading) return <div className="page-container"><p>Đang chạy preflight...</p></div>;
  if (!result) return <div className="page-container"><Alert variant="error" title="Lỗi">Không thể chạy preflight.</Alert></div>;

  const outcomeConfig = OUTCOME_CONFIG[result.outcome];
  const session = SessionService.getSession(sessionId);
  const nextRoute = session?.requiresCalibration
    ? `/sessions/${sessionId}/calibration`
    : `/sessions/${sessionId}/quality`;

  return (
    <div className="page-container">
      <div className="page-header">
        <div className="page-header__left">
          <h1 className="page-title">Preflight Check</h1>
          <p className="page-subtitle">Kiểm tra tín hiệu trước khi xử lý. Session: <code>{sessionId}</code></p>
        </div>
        <div className="page-header__right">
          <Badge variant={outcomeConfig.variant} size="md">{outcomeConfig.label}</Badge>
        </div>
      </div>

      <Alert variant={outcomeConfig.variant} title={outcomeConfig.label}>
        {outcomeConfig.message}
      </Alert>

      {/* Overview stats */}
      <div className={styles.statsRow}>
        <div className={styles.stat}>
          <span className={styles.statLabel}>Sampling Rate</span>
          <span className={styles.statValue}>{result.overallSamplingRateHz} Hz</span>
        </div>
        <div className={styles.stat}>
          <span className={styles.statLabel}>Duration</span>
          <span className={styles.statValue}>{result.overallDurationSeconds}s</span>
        </div>
        <div className={styles.stat}>
          <span className={styles.statLabel}>Channels</span>
          <span className={styles.statValue}>{result.overallChannelCount}</span>
        </div>
        <div className={styles.stat}>
          <span className={styles.statLabel}>Source Hash</span>
          <code className={styles.statHash}>{result.sourceHash.substring(0, 16)}...</code>
        </div>
      </div>

      {/* Check grid */}
      <Card padding="md">
        <CardHeader><h2 className={styles.sectionTitle}>Kiểm tra chất lượng (10 checks)</h2></CardHeader>
        <CardContent>
          <div className={styles.checkGrid}>
            {result.checks.map((check) => (
              <div key={check.id} className={[styles.checkItem, styles[`checkItem--${check.status}`]].join(' ')}>
                <div className={styles.checkIcon}>
                  {check.status === 'pass' ? <CheckCircle size={16} /> :
                   check.status === 'warning' ? <AlertTriangle size={16} /> :
                   <XCircle size={16} />}
                </div>
                <div className={styles.checkContent}>
                  <div className={styles.checkLabel}>{check.label}</div>
                  <div className={styles.checkValues}>
                    <span>Giá trị: <strong>{check.value}</strong></span>
                    <span>Kỳ vọng: {check.expected}</span>
                  </div>
                  {check.detail && <div className={styles.checkDetail}>{check.detail}</div>}
                </div>
                <Badge variant={check.status === 'pass' ? 'success' : check.status === 'warning' ? 'warning' : 'error'} size="sm">
                  {check.status.toUpperCase()}
                </Badge>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Channel previews */}
      <Card padding="md">
        <CardHeader><h2 className={styles.sectionTitle}>Signal Preview</h2></CardHeader>
        <CardContent>
          <div className={styles.previewGrid}>
            {result.channelPreviews.map((ch) => (
              <div key={ch.channelId} className={styles.previewCard}>
                <div className={styles.previewHeader}>
                  <Activity size={14} />
                  <strong>{ch.channelLabel}</strong>
                  <span className={styles.previewMuscle}>{ch.muscle} ({ch.side})</span>
                </div>
                {/* Mock waveform SVG */}
                <svg viewBox="0 0 200 50" className={styles.waveform} aria-label={`Waveform for ${ch.channelLabel}`}>
                  <path d={generateMockWaveform(ch.channelId)} fill="none" stroke="var(--color-primary)" strokeWidth="1.5" />
                  <line x1="0" y1="25" x2="200" y2="25" stroke="var(--color-border)" strokeWidth="0.5" strokeDasharray="4" />
                </svg>
                <div className={styles.previewStats}>
                  <span>{ch.samplingRateHz} Hz</span>
                  <span>{ch.durationSeconds}s</span>
                  <span>Min: {ch.minAmplitude.toFixed(2)}</span>
                  <span>Max: {ch.maxAmplitude.toFixed(2)}</span>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      <div className={styles.actions}>
        <Button variant="ghost" onClick={() => router.push(`/sessions/${sessionId}/mapping`)} icon={<ArrowLeft size={16} />}>Quay lại Mapping</Button>
        {result.outcome === 'mapping_required' && (
          <Button variant="secondary" onClick={() => router.push(`/sessions/${sessionId}/mapping`)} icon={<RefreshCw size={16} />}>Sửa Mapping</Button>
        )}
        <div className={styles.spacer} />
        {result.outcome === 'ready' && (
          <Button onClick={() => router.push(nextRoute)} icon={<ArrowRight size={16} />} iconPosition="right">
            Tiếp tục → {session?.requiresCalibration ? 'Calibration' : 'Quality Check'}
          </Button>
        )}
      </div>
    </div>
  );
}

function generateMockWaveform(channelId: string): string {
  const seed = channelId.charCodeAt(channelId.length - 1);
  const points: string[] = [];
  for (let x = 0; x <= 200; x += 2) {
    const y = 25 + Math.sin(x * 0.15 + seed) * 12 + Math.sin(x * 0.4 + seed * 2) * 6 + (Math.sin(x * 0.05) * 3);
    points.push(`${x === 0 ? 'M' : 'L'}${x},${y.toFixed(1)}`);
  }
  return points.join(' ');
}
