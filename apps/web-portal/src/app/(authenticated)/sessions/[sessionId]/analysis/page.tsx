/**
 * Analysis Gate — `/sessions/[sessionId]/analysis`
 * Prerequisites checklist, start analysis, structured output with provenance.
 * Engineering confidence explicitly NOT clinical probability.
 */
'use client';

import { useState, useEffect, useCallback } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { CheckCircle, XCircle, Play, ArrowLeft, Shield, AlertTriangle, Activity, Clock, FileText } from 'lucide-react';
import { Card, CardContent, CardHeader } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { Alert } from '@/components/ui/Alert';
import type { AnalysisJob, AnalysisPrerequisite } from '@/schemas/analysis';
import * as SessionService from '@/services/mock/MockSessionService';
import * as AnalysisService from '@/services/mock/MockAnalysisService';
import type { AnalysisEligibility } from '@/services/mock/MockAnalysisService';
import styles from './analysis.module.css';

export default function AnalysisPage() {
  const params = useParams();
  const router = useRouter();
  const sessionId = params.sessionId as string;

  const [eligibility, setEligibility] = useState<AnalysisEligibility | null>(null);
  const [job, setJob] = useState<AnalysisJob | null>(null);
  const [loading, setLoading] = useState(true);
  const [running, setRunning] = useState(false);

  useEffect(() => {
    const session = SessionService.getSession(sessionId);
    if (!session || session.state === 'draft') {
      router.replace(`/sessions/${sessionId}/context`);
      return;
    }

    const el = AnalysisService.canStartAnalysis(sessionId);
    setEligibility(el);

    const existing = AnalysisService.getAnalysisJob(sessionId);
    if (existing) setJob(existing);

    setLoading(false);
  }, [sessionId, router]);

  const handleStartAnalysis = useCallback(async () => {
    setRunning(true);
    const started = AnalysisService.startAnalysis(sessionId);
    if (started) {
      setJob({ ...started });

      // Simulate progress
      for (let p = 10; p <= 90; p += 20) {
        await new Promise((resolve) => setTimeout(resolve, 600));
        setJob((prev) => prev ? { ...prev, progress: p } : prev);
      }

      // Complete
      await new Promise((resolve) => setTimeout(resolve, 800));
      const completed = AnalysisService.completeAnalysis(sessionId);
      if (completed) setJob({ ...completed });
    }
    setRunning(false);
  }, [sessionId]);

  if (loading) return <div className="page-container"><p>Đang kiểm tra prerequisites...</p></div>;

  return (
    <div className="page-container">
      <div className="page-header">
        <div className="page-header__left">
          <h1 className="page-title">Analysis Gate</h1>
          <p className="page-subtitle">Kiểm tra điều kiện và kích hoạt analysis pipeline.</p>
        </div>
        <div className="page-header__right">
          {job?.state === 'completed' && <Badge variant="success">COMPLETED ✓</Badge>}
          {job?.state === 'running' && <Badge variant="info">RUNNING...</Badge>}
          {!job && eligibility?.allowed && <Badge variant="success">READY</Badge>}
          {!job && !eligibility?.allowed && <Badge variant="error">BLOCKED</Badge>}
        </div>
      </div>

      {/* Prerequisites checklist */}
      <Card padding="md">
        <CardHeader><h2 className={styles.sectionTitle}>Prerequisites</h2></CardHeader>
        <CardContent>
          <div className={styles.prereqList}>
            {eligibility?.prerequisites.map((prereq) => (
              <div key={prereq.id} className={[styles.prereqItem, prereq.met ? styles['prereqItem--met'] : styles['prereqItem--unmet']].join(' ')}>
                {prereq.met ? <CheckCircle size={18} className={styles.prereqIcon} /> : <XCircle size={18} className={styles.prereqIconFail} />}
                <div>
                  <div className={styles.prereqLabel}>{prereq.label}</div>
                  <div className={styles.prereqDetail}>{prereq.detail}</div>
                </div>
              </div>
            ))}
          </div>

          {eligibility && !eligibility.allowed && (
            <Alert variant="error" title="Không thể chạy analysis">
              {eligibility.blockers.map((b, i) => <p key={i}>• {b}</p>)}
            </Alert>
          )}
        </CardContent>
      </Card>

      {/* Start / Progress */}
      {!job && (
        <Card padding="lg">
          <CardContent>
            <div className={styles.startSection}>
              <Activity size={48} className={styles.startIcon} />
              <h3 className={styles.startTitle}>Kích hoạt Analysis Pipeline</h3>
              <p className={styles.startDesc}>Pipeline sẽ xử lý dữ liệu sEMG và trả về kết quả kỹ thuật.</p>
              <Button onClick={handleStartAnalysis} disabled={!eligibility?.allowed || running} icon={<Play size={16} />} size="lg">
                {running ? 'Đang chạy...' : 'Bắt đầu Analysis'}
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Running progress */}
      {job && job.state === 'running' && (
        <Card padding="lg">
          <CardContent>
            <div className={styles.progressSection}>
              <div className={styles.spinner} />
              <h3>Đang xử lý...</h3>
              <div className={styles.progressContainer}>
                <div className={styles.progressBar}>
                  <div className={styles.progressFill} style={{ width: `${job.progress}%` }} />
                </div>
                <span>{job.progress}%</span>
              </div>
              <p className={styles.progressHint}>Pipeline: {job.pipeline} · Job: {job.jobId}</p>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Completed output */}
      {job?.state === 'completed' && job.output && (
        <>
          <Alert variant="success" title="Analysis hoàn tất">
            Job <code>{job.jobId}</code> đã hoàn thành lúc {job.completedAt ? new Date(job.completedAt).toLocaleString('vi-VN') : '—'}.
          </Alert>

          <Card padding="md">
            <CardHeader><h2 className={styles.sectionTitle}>Kết quả kỹ thuật</h2></CardHeader>
            <CardContent>
              <div className={styles.outputGrid}>
                <div className={styles.outputItem}>
                  <span className={styles.outputLabel}>Status</span>
                  <Badge variant={job.output.status === 'completed' ? 'success' : 'warning'}>{job.output.status}</Badge>
                </div>
                <div className={styles.outputItem}>
                  <span className={styles.outputLabel}>Engineering Confidence</span>
                  <div className={styles.confidenceBar}>
                    <div className={styles.confidenceFill} style={{ width: `${job.output.engineeringConfidence * 100}%` }} />
                    <span>{(job.output.engineeringConfidence * 100).toFixed(0)}%</span>
                  </div>
                </div>
              </div>

              <Alert variant="warning" title="⚠ Quan trọng">
                Engineering confidence KHÔNG phải xác suất lâm sàng. Đây là chỉ số kỹ thuật đánh giá chất lượng xử lý tín hiệu, không thay thế đánh giá của bác sĩ/KTV.
              </Alert>

              <h3 className={styles.subTitle}>Technical Conclusion</h3>
              <p className={styles.conclusion}>{job.output.technicalConclusion}</p>

              <h3 className={styles.subTitle}>Reason Codes</h3>
              <div className={styles.codeList}>
                {job.output.reasonCodes.map((code) => (
                  <Badge key={code} variant="neutral" size="sm">{code}</Badge>
                ))}
              </div>

              <h3 className={styles.subTitle}>Limitations</h3>
              <ul className={styles.limitList}>
                {job.output.limitations.map((lim, i) => (
                  <li key={i}>{lim}</li>
                ))}
              </ul>

              <h3 className={styles.subTitle}>MFCV Eligibility</h3>
              <div className={styles.mfcvBox}>
                <Badge variant={job.output.mfcvEligibility.eligible ? 'success' : 'warning'}>
                  {job.output.mfcvEligibility.eligible ? 'Eligible' : 'Not Eligible'}
                </Badge>
                <span>{job.output.mfcvEligibility.reason}</span>
                {!job.output.mfcvEligibility.blocksBasicSEMG && (
                  <span className={styles.mfcvNote}>Không block basic sEMG analysis.</span>
                )}
              </div>

              <h3 className={styles.subTitle}>Provenance</h3>
              <div className={styles.provenanceGrid}>
                <span>Model version:</span><code>{job.output.provenance.modelVersion}</code>
                <span>Pipeline version:</span><code>{job.output.provenance.pipelineVersion}</code>
                <span>Data hash:</span><code>{job.output.provenance.dataHash.substring(0, 24)}...</code>
                {job.output.provenance.calibrationId && <><span>Calibration ID:</span><code>{job.output.provenance.calibrationId}</code></>}
              </div>
            </CardContent>
          </Card>
        </>
      )}

      <div className={styles.actions}>
        <Button variant="ghost" onClick={() => router.push(`/sessions/${sessionId}/quality`)} icon={<ArrowLeft size={16} />}>Quay lại QC</Button>
        <div className={styles.spacer} />
        {job?.state === 'completed' && (
          <Button variant="secondary" onClick={() => router.push(`/sessions`)}>
            Quay về danh sách Sessions
          </Button>
        )}
      </div>
    </div>
  );
}
