/**
 * Calibration Wizard — `/sessions/[sessionId]/calibration`
 * 5-step wizard: Setup → Baseline → Repetitions → Summary → Result.
 * Conditional: only shown if protocol requires calibration.
 */
'use client';

import { useState, useEffect, useCallback } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { CheckCircle, AlertTriangle, XCircle, ArrowRight, ArrowLeft, Play, RefreshCw, Timer } from 'lucide-react';
import { Card, CardContent, CardHeader } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { Alert } from '@/components/ui/Alert';
import type { CalibrationWizard, CalibrationStep, RepetitionResult } from '@/schemas/calibration';
import { CALIBRATION_STEPS } from '@/schemas/calibration';
import * as SessionService from '@/services/mock/MockSessionService';
import * as CalibrationService from '@/services/mock/MockCalibrationService';
import styles from './calibration.module.css';

export default function CalibrationPage() {
  const params = useParams();
  const router = useRouter();
  const sessionId = params.sessionId as string;

  const [wizard, setWizard] = useState<CalibrationWizard | null>(null);
  const [loading, setLoading] = useState(true);
  const [countdown, setCountdown] = useState<number | null>(null);
  const [activeRep, setActiveRep] = useState<number | null>(null);

  useEffect(() => {
    const session = SessionService.getSession(sessionId);
    if (!session) { router.replace(`/sessions/${sessionId}/context`); return; }
    if (!session.requiresCalibration) {
      SessionService.advanceState(sessionId, 'calibration_skipped');
      router.replace(`/sessions/${sessionId}/quality`);
      return;
    }

    let cal = CalibrationService.getCalibration(sessionId);
    if (!cal) {
      cal = CalibrationService.startCalibration(sessionId, 'happy_path');
    }
    setWizard(cal);
    setLoading(false);
  }, [sessionId, router]);

  const runCountdown = useCallback((seconds: number): Promise<void> => {
    return new Promise((resolve) => {
      let remaining = seconds;
      setCountdown(remaining);
      const interval = setInterval(() => {
        remaining--;
        setCountdown(remaining);
        if (remaining <= 0) {
          clearInterval(interval);
          setCountdown(null);
          resolve();
        }
      }, 1000);
    });
  }, []);

  const handleSetupCheck = async () => {
    await runCountdown(3);
    const updated = CalibrationService.runSetupCheck(sessionId, 'happy_path');
    if (updated) setWizard({ ...updated });
  };

  const handleBaseline = async () => {
    await runCountdown(5);
    const updated = CalibrationService.recordBaseline(sessionId, 'happy_path');
    if (updated) {
      CalibrationService.loadRepetitions(sessionId, 'happy_path');
      const withReps = CalibrationService.getCalibration(sessionId);
      if (withReps) setWizard({ ...withReps });
    }
  };

  const handleAcceptRep = (idx: number) => {
    const updated = CalibrationService.acceptRepetition(sessionId, idx);
    if (updated) setWizard({ ...updated });
  };

  const handleRepeatRep = (idx: number) => {
    const updated = CalibrationService.repeatRepetition(sessionId, idx);
    if (updated) setWizard({ ...updated });
  };

  const handleFinish = () => {
    const updated = CalibrationService.finishCalibration(sessionId);
    if (updated) setWizard({ ...updated });
  };

  const handleContinue = () => {
    router.push(`/sessions/${sessionId}/quality`);
  };

  if (loading) return <div className="page-container"><p>Đang tải...</p></div>;
  if (!wizard) return <div className="page-container"><Alert variant="error" title="Lỗi">Không thể khởi tạo calibration.</Alert></div>;

  const currentStepIdx = CALIBRATION_STEPS.findIndex((s) => s.id === wizard.currentStep);

  return (
    <div className="page-container">
      <div className="page-header">
        <div className="page-header__left">
          <h1 className="page-title">Calibration</h1>
          <p className="page-subtitle">Calibration ID: <code>{wizard.calibrationId}</code></p>
        </div>
        <div className="page-header__right">
          <Badge variant={wizard.status === 'pass' ? 'success' : wizard.status === 'warning' ? 'warning' : wizard.status === 'fail' ? 'error' : 'info'}>
            {wizard.status.toUpperCase()}
          </Badge>
        </div>
      </div>

      {/* Step indicator */}
      <div className={styles.stepper}>
        {CALIBRATION_STEPS.map((step, idx) => (
          <div key={step.id} className={[styles.step, idx < currentStepIdx ? styles['step--done'] : idx === currentStepIdx ? styles['step--active'] : ''].filter(Boolean).join(' ')}>
            <div className={styles.stepDot}>
              {idx < currentStepIdx ? <CheckCircle size={16} /> : <span>{idx + 1}</span>}
            </div>
            <span className={styles.stepLabel}>{step.label}</span>
          </div>
        ))}
      </div>

      {/* Countdown overlay */}
      {countdown !== null && (
        <div className={styles.countdownOverlay}>
          <Timer size={48} />
          <div className={styles.countdownValue}>{countdown}</div>
          <p>Đang thu thập...</p>
        </div>
      )}

      {/* Step 1: Setup Check */}
      {wizard.currentStep === 'setup_check' && (
        <Card padding="lg">
          <CardHeader><h2 className={styles.sectionTitle}>Bước 1: Kiểm tra Setup</h2></CardHeader>
          <CardContent>
            <p className={styles.stepDesc}>Kiểm tra impedance, số kênh, và chất lượng contact điện cực trước khi bắt đầu calibration.</p>
            {wizard.setupResult ? (
              <div className={styles.resultBox}>
                <div className={styles.resultItem}><span>Impedance:</span><Badge variant={wizard.setupResult.impedanceOk ? 'success' : 'warning'}>{wizard.setupResult.impedanceOk ? 'OK' : 'Cần kiểm tra'}</Badge></div>
                <div className={styles.resultItem}><span>Kênh phát hiện:</span><strong>{wizard.setupResult.channelsDetected} / {wizard.setupResult.channelsExpected}</strong></div>
                <div className={styles.resultItem}><span>Skin contact:</span><Badge variant={wizard.setupResult.skinContact === 'good' ? 'success' : 'warning'}>{wizard.setupResult.skinContact}</Badge></div>
                <p className={styles.resultDetail}>{wizard.setupResult.detail}</p>
              </div>
            ) : (
              <Button onClick={handleSetupCheck} icon={<Play size={16} />} disabled={countdown !== null}>Chạy kiểm tra Setup</Button>
            )}
          </CardContent>
        </Card>
      )}

      {/* Step 2: Rest Baseline */}
      {wizard.currentStep === 'rest_baseline' && (
        <Card padding="lg">
          <CardHeader><h2 className={styles.sectionTitle}>Bước 2: Baseline nghỉ</h2></CardHeader>
          <CardContent>
            <p className={styles.stepDesc}>Thu thập tín hiệu baseline khi cơ hoàn toàn thư giãn (5 giây).</p>
            {wizard.baselineResult ? (
              <div className={styles.resultBox}>
                <div className={styles.resultItem}><span>Baseline noise RMS:</span><strong>{wizard.baselineResult.baselineNoiseRms.toFixed(1)} µV</strong></div>
                <div className={styles.resultItem}><span>Thời lượng:</span><strong>{wizard.baselineResult.baselineDuration}s</strong></div>
                <div className={styles.resultItem}><span>Chấp nhận:</span><Badge variant={wizard.baselineResult.acceptable ? 'success' : 'error'}>{wizard.baselineResult.acceptable ? 'OK' : 'Không đạt'}</Badge></div>
              </div>
            ) : (
              <Button onClick={handleBaseline} icon={<Play size={16} />} disabled={countdown !== null}>Thu baseline</Button>
            )}
          </CardContent>
        </Card>
      )}

      {/* Step 3: Gesture Repetitions */}
      {wizard.currentStep === 'gesture_repetitions' && (
        <Card padding="lg">
          <CardHeader><h2 className={styles.sectionTitle}>Bước 3: Lặp cử chỉ</h2></CardHeader>
          <CardContent>
            <p className={styles.stepDesc}>Thực hiện các cử chỉ theo hướng dẫn. Mỗi repetition được đánh giá chất lượng.</p>
            <div className={styles.repList}>
              {wizard.repetitions.map((rep, idx) => (
                <div key={rep.repetitionId} className={[styles.repCard, styles[`repCard--${rep.quality}`]].join(' ')}>
                  <div className={styles.repHeader}>
                    <code className={styles.repId}>{rep.repetitionId}</code>
                    <Badge variant={rep.quality === 'pass' ? 'success' : rep.quality === 'warning' ? 'warning' : 'error'} size="sm">
                      {rep.quality.toUpperCase()}
                    </Badge>
                  </div>
                  <div className={styles.repInfo}>
                    <span className={styles.repGesture}>{rep.gesture}</span>
                    <span className={styles.repMeta}>Peak: {rep.peakAmplitude} µV · {rep.duration}s</span>
                  </div>
                  {rep.reason && <p className={styles.repReason}>{rep.reason}</p>}
                  <div className={styles.repActions}>
                    {rep.accepted ? (
                      <Badge variant="success" icon={<CheckCircle size={12} />}>Accepted</Badge>
                    ) : (
                      <>
                        <Button size="sm" variant="secondary" onClick={() => handleAcceptRep(idx)}>Accept</Button>
                        <Button size="sm" variant="ghost" onClick={() => handleRepeatRep(idx)} icon={<RefreshCw size={14} />}>Lặp lại</Button>
                      </>
                    )}
                  </div>
                </div>
              ))}
            </div>
            {wizard.repetitions.every((r) => r.accepted) && (
              <div style={{ marginTop: 'var(--space-4)' }}>
                <Button onClick={handleFinish} icon={<ArrowRight size={16} />}>Hoàn tất Calibration</Button>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Step 4-5: Summary + Result */}
      {(wizard.currentStep === 'summary' || wizard.currentStep === 'result') && wizard.summary && (
        <Card padding="lg">
          <CardHeader><h2 className={styles.sectionTitle}>Kết quả Calibration</h2></CardHeader>
          <CardContent>
            <Alert
              variant={wizard.summary.overallStatus === 'pass' ? 'success' : wizard.summary.overallStatus === 'warning' ? 'warning' : 'error'}
              title={`Calibration: ${wizard.summary.overallStatus.toUpperCase()}`}
            >
              {wizard.summary.detail}
            </Alert>
            <div className={styles.summaryGrid}>
              <div className={styles.summaryItem}><span>Tổng repetitions:</span><strong>{wizard.summary.totalRepetitions}</strong></div>
              <div className={styles.summaryItem}><span>Pass:</span><strong className={styles.passText}>{wizard.summary.passedRepetitions}</strong></div>
              <div className={styles.summaryItem}><span>Warning:</span><strong className={styles.warnText}>{wizard.summary.warningRepetitions}</strong></div>
              <div className={styles.summaryItem}><span>Failed:</span><strong className={styles.failText}>{wizard.summary.failedRepetitions}</strong></div>
            </div>
            <h3 className={styles.subTitle}>MVC Estimates</h3>
            <div className={styles.mvcGrid}>
              {Object.entries(wizard.summary.mvcEstimates).map(([muscle, value]) => (
                <div key={muscle} className={styles.mvcItem}>
                  <span>{muscle}</span>
                  <strong>{value} µV</strong>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      <div className={styles.actions}>
        <Button variant="ghost" onClick={() => router.push(`/sessions/${sessionId}/preflight`)} icon={<ArrowLeft size={16} />}>Quay lại Preflight</Button>
        <div className={styles.spacer} />
        {wizard.currentStep === 'result' && (wizard.status === 'pass' || wizard.status === 'warning') && (
          <Button onClick={handleContinue} icon={<ArrowRight size={16} />} iconPosition="right">
            Tiếp tục → Quality Check
          </Button>
        )}
      </div>
    </div>
  );
}
