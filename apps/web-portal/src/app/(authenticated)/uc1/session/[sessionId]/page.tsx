/**
 * UC1 Session Page — `/uc1/session/[sessionId]`
 * Real-time/playback gesture feed, segment analysis, fatigue safety rail.
 */
'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { AlertTriangle, Activity, CheckCircle, Flag, Info, ArrowRight, ShieldAlert } from 'lucide-react';
import { Card, CardContent, CardHeader } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { Alert } from '@/components/ui/Alert';
import type { SignalSegment } from '@/schemas/segment';
import * as MockWorkflowRepository from '@/services/mock/MockWorkflowRepository';
import styles from './uc1-session.module.css';

// Mock generation for UC1 segments
function generateMockSegments(sessionId: string): SignalSegment[] {
  return [
    {
      id: `SEG-${Date.now()}-1`,
      sessionId,
      analysisId: 'AN-001',
      startSample: 1000,
      endSample: 2000,
      startTimeS: 1.0,
      endTimeS: 2.0,
      channelIds: ['CH1', 'CH2'],
      sourceHash: 'sha256:dummy1',
      modelVersion: 'v1.0.0',
      featureVersion: 'v2.1.0',
      targetGesture: 'Nắm tay',
      predictedGesture: 'Nắm tay',
      engineeringConfidence: 0.95,
      fatigueIndex: 0.1,
      reasoning: ['High amplitude on CH1', 'Clear onset'],
      qualityContext: { hasQCWarning: false, reasonCodes: [] },
    },
    {
      id: `SEG-${Date.now()}-2`,
      sessionId,
      analysisId: 'AN-001',
      startSample: 3000,
      endSample: 4000,
      startTimeS: 3.0,
      endTimeS: 4.0,
      channelIds: ['CH1', 'CH2'],
      sourceHash: 'sha256:dummy1',
      modelVersion: 'v1.0.0',
      featureVersion: 'v2.1.0',
      targetGesture: 'Duỗi ngón',
      predictedGesture: 'Nắm tay', // AI predicts wrong
      engineeringConfidence: 0.45,
      fatigueIndex: 0.3,
      reasoning: ['Ambiguous activation', 'Low SNR'],
      qualityContext: { hasQCWarning: true, reasonCodes: ['QC_SNR_LOW'] },
    },
    {
      id: `SEG-${Date.now()}-3`,
      sessionId,
      analysisId: 'AN-001',
      startSample: 5000,
      endSample: 6000,
      startTimeS: 5.0,
      endTimeS: 6.0,
      channelIds: ['CH1', 'CH2'],
      sourceHash: 'sha256:dummy1',
      modelVersion: 'v1.0.0',
      featureVersion: 'v2.1.0',
      targetGesture: 'Nắm tay',
      predictedGesture: 'Nắm tay',
      engineeringConfidence: 0.88,
      fatigueIndex: 0.85, // High fatigue
      reasoning: ['Frequency shift detected', 'Amplitude drop'],
      qualityContext: { hasQCWarning: false, reasonCodes: [] },
    },
  ];
}

export default function UC1SessionPage() {
  const params = useParams();
  const router = useRouter();
  const sessionId = params.sessionId as string;

  const [segments, setSegments] = useState<SignalSegment[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const existing = MockWorkflowRepository.getSegments(sessionId);
    if (existing && existing.length > 0) {
      setSegments(existing);
    } else {
      const mock = generateMockSegments(sessionId);
      MockWorkflowRepository.saveSegments(sessionId, mock);
      setSegments(mock);
    }
    setLoading(false);
  }, [sessionId]);

  const handleFinish = () => {
    // Navigate to Technical Review
    router.push(`/uc1/review/${sessionId}`);
  };

  if (loading) return <div className="page-container">Đang tải session...</div>;

  const hasHighFatigue = segments.some(s => (s.fatigueIndex ?? 0) > 0.8);

  return (
    <div className="page-container">
      <div className="page-header">
        <div className="page-header__left">
          <h1 className="page-title">UC1: Gesture Session Workspace</h1>
          <p className="page-subtitle">Giám sát nhận diện cử chỉ, Activity Gate & an toàn mỏi cơ.</p>
        </div>
      </div>

      {hasHighFatigue && (
        <Alert variant="error" title="Fatigue Safety Rail Kích Hoạt">
          <div className={styles.alertContent}>
            <ShieldAlert size={20} />
            <span>Phát hiện dấu hiệu mỏi cơ cao (&gt;80%). Đề xuất cho bệnh nhân nghỉ ngơi.</span>
          </div>
        </Alert>
      )}

      <div className={styles.segmentsGrid}>
        {segments.map((seg, idx) => {
          const isHighFatigue = (seg.fatigueIndex ?? 0) > 0.8;
          const confVariant = seg.engineeringConfidence > 0.8 ? 'success' : seg.engineeringConfidence > 0.5 ? 'warning' : 'error';

          return (
            <Card key={seg.id} padding="md">
              <div className={styles.segHeader}>
                <Badge variant="neutral">Rep {idx + 1}</Badge>
                <Badge variant="neutral">{seg.startTimeS.toFixed(1)}s - {seg.endTimeS.toFixed(1)}s</Badge>
                {seg.qualityContext.hasQCWarning && <Badge variant="warning">QC Warn</Badge>}
              </div>

              <div className={styles.segBody}>
                <div className={styles.metric}>
                  <span className={styles.label}>Target Gesture</span>
                  <span className={styles.value}>{seg.targetGesture}</span>
                </div>
                
                <div className={styles.metric}>
                  <span className={styles.label}>AI Prediction</span>
                  <div className={styles.predictionRow}>
                    <span className={styles.value}>{seg.predictedGesture}</span>
                    <Badge variant={confVariant}>{(seg.engineeringConfidence * 100).toFixed(0)}% Conf</Badge>
                  </div>
                </div>

                <div className={styles.metric}>
                  <span className={styles.label}>Fatigue Index</span>
                  <div className={styles.fatigueRow}>
                    <div className={styles.fatigueBar}>
                      <div className={styles.fatigueFill} style={{ width: `${(seg.fatigueIndex ?? 0) * 100}%`, backgroundColor: isHighFatigue ? 'var(--color-error)' : 'var(--color-primary)' }} />
                    </div>
                    <span>{((seg.fatigueIndex ?? 0) * 100).toFixed(0)}%</span>
                  </div>
                </div>

                <div className={styles.explainability}>
                  <strong><Info size={14} /> Explainability:</strong>
                  <ul>
                    {seg.reasoning.map((r, i) => <li key={i}>{r}</li>)}
                  </ul>
                  <div className={styles.provenance}>
                    <span>Model: {seg.modelVersion} | Feature: {seg.featureVersion}</span>
                  </div>
                </div>
              </div>
            </Card>
          );
        })}
      </div>

      <div className={styles.actions}>
        <Button onClick={handleFinish} icon={<ArrowRight size={16} />} iconPosition="right">
          Kết thúc Session & Chuyển sang Technical Review
        </Button>
      </div>
    </div>
  );
}
