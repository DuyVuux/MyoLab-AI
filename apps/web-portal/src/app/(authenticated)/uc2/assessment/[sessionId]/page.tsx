/**
 * UC2 Assessment Page — `/uc2/assessment/[sessionId]`
 * 7 Tabs: Overview, Repertoire, Repeatability, Reference, Symmetry, Fatigue, Provenance
 */
'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { Activity, ArrowRight, CheckCircle, ShieldAlert, FileText } from 'lucide-react';
import { Card, CardContent, CardHeader } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { Alert } from '@/components/ui/Alert';
import * as MockWorkflowRepository from '@/services/mock/MockWorkflowRepository';
import type { SessionContext } from '@/schemas/session';
import type { CalibrationWizard } from '@/schemas/calibration';
import type { AnalysisJob } from '@/schemas/analysis';
import styles from './uc2-assessment.module.css';

const TABS = [
  'Overview',
  'Gesture Repertoire',
  'Repeatability',
  'Reference Similarity',
  'Co-contraction & Symmetry',
  'Fatigue & Endurance',
  'Signal & Provenance'
];

export default function UC2AssessmentPage() {
  const params = useParams();
  const router = useRouter();
  const sessionId = params.sessionId as string;

  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState(TABS[0]);
  const [session, setSession] = useState<SessionContext | null>(null);
  const [calibration, setCalibration] = useState<CalibrationWizard | null>(null);
  const [analysis, setAnalysis] = useState<AnalysisJob | null>(null);

  useEffect(() => {
    setSession(MockWorkflowRepository.getSession(sessionId));
    setCalibration(MockWorkflowRepository.getCalibration(sessionId));
    setAnalysis(MockWorkflowRepository.getAnalysisJob(sessionId));
    setLoading(false);
  }, [sessionId]);

  if (loading) return <div className="page-container">Đang tải...</div>;
  if (!session) return <div className="page-container">Session không tồn tại.</div>;

  const hasMVC = calibration && calibration.summary && Object.keys(calibration.summary.mvcEstimates).length > 0;

  return (
    <div className="page-container">
      <div className="page-header">
        <div className="page-header__left">
          <h1 className="page-title">UC2: Motor Assessment</h1>
          <p className="page-subtitle">Đánh giá chức năng vận động chi tiết.</p>
        </div>
      </div>

      <div className={styles.tabContainer}>
        <div className={styles.tabList}>
          {TABS.map(tab => (
            <button 
              key={tab} 
              className={[styles.tabButton, activeTab === tab ? styles.activeTab : ''].join(' ')}
              onClick={() => setActiveTab(tab)}
            >
              {tab}
            </button>
          ))}
        </div>

        <div className={styles.tabContent}>
          {activeTab === 'Overview' && (
            <div className={styles.panel}>
              <h2 className={styles.panelTitle}>Overview</h2>
              <div className={styles.grid}>
                <Card padding="md">
                  <div className={styles.metricLabel}>Peak Amplitude</div>
                  <div className={styles.metricValue}>
                    {hasMVC ? '72% MVC' : '450 µV'}
                  </div>
                  {!hasMVC && <span className={styles.note}>*Không có MVC reference</span>}
                </Card>
                <Card padding="md">
                  <div className={styles.metricLabel}>Time to Peak</div>
                  <div className={styles.metricValue}>250 ms</div>
                </Card>
                <Card padding="md">
                  <div className={styles.metricLabel}>Activation Duration</div>
                  <div className={styles.metricValue}>1.2 s</div>
                </Card>
              </div>
              
              <Alert variant="info" title="Clinical AI Output">
                {analysis?.output?.technicalConclusion || 'Phân tích chức năng vận động đạt ngưỡng tin cậy kỹ thuật cao.'}
              </Alert>
            </div>
          )}

          {activeTab === 'Gesture Repertoire' && (
            <div className={styles.panel}>
              <h2 className={styles.panelTitle}>Gesture Repertoire</h2>
              <p>Phân tích khả năng thực hiện đa dạng các cử chỉ của bệnh nhân.</p>
              <Card padding="md">
                <ul>
                  <li>Nắm tay: <Badge variant="success">Hoàn thành tốt</Badge></li>
                  <li>Duỗi ngón: <Badge variant="warning">Biên độ yếu</Badge></li>
                </ul>
              </Card>
            </div>
          )}

          {activeTab === 'Repeatability' && (
            <div className={styles.panel}>
              <h2 className={styles.panelTitle}>Repeatability</h2>
              <p>Độ ổn định qua các lần lặp lại cùng một cử chỉ.</p>
              <Card padding="md">
                <div className={styles.metricLabel}>CV (Coefficient of Variation)</div>
                <div className={styles.metricValue}>12%</div>
              </Card>
            </div>
          )}

          {activeTab === 'Reference Similarity' && (
            <div className={styles.panel}>
              <h2 className={styles.panelTitle}>Reference Similarity</h2>
              <p>So sánh mẫu kích hoạt cơ hiện tại với CSDL chuẩn.</p>
              <Card padding="md">
                <div className={styles.metricLabel}>Correlation Score</div>
                <div className={styles.metricValue}>0.85</div>
              </Card>
            </div>
          )}

          {activeTab === 'Co-contraction & Symmetry' && (
            <div className={styles.panel}>
              <h2 className={styles.panelTitle}>Co-contraction & Symmetry</h2>
              <p>So sánh bên {session.affectedSide} và bên {session.referenceSide}.</p>
              <div className={styles.grid}>
                <Card padding="md">
                  <div className={styles.metricLabel}>{session.affectedSide} (Affected)</div>
                  <div className={styles.metricValue}>Peak: {hasMVC ? '40% MVC' : '200 µV'}</div>
                </Card>
                <Card padding="md">
                  <div className={styles.metricLabel}>{session.referenceSide} (Reference)</div>
                  <div className={styles.metricValue}>Peak: {hasMVC ? '85% MVC' : '450 µV'}</div>
                </Card>
              </div>
            </div>
          )}

          {activeTab === 'Fatigue & Endurance' && (
            <div className={styles.panel}>
              <h2 className={styles.panelTitle}>Fatigue & Endurance</h2>
              <Card padding="md">
                <div className={styles.metricLabel}>Median Frequency Shift</div>
                <div className={styles.metricValue}>-15 Hz</div>
                <span className={styles.note}>Dấu hiệu mỏi cơ xuất hiện sau 15 giây.</span>
              </Card>
            </div>
          )}

          {activeTab === 'Signal & Provenance' && (
            <div className={styles.panel}>
              <h2 className={styles.panelTitle}>Signal & Provenance</h2>
              <Card padding="md">
                <ul className={styles.provenanceList}>
                  <li><strong>Session ID:</strong> {sessionId}</li>
                  <li><strong>Protocol:</strong> {session.protocolId} (v{session.protocolVersion})</li>
                  <li><strong>Calibration ID:</strong> {calibration?.sessionId || 'N/A'}</li>
                  <li><strong>Analysis Hash:</strong> {analysis?.output?.provenance.dataHash.substring(0, 20)}...</li>
                </ul>
              </Card>
            </div>
          )}
        </div>
      </div>

      <div className={styles.actions}>
        <Button onClick={() => router.push(`/uc2/longitudinal/${session.subjectRef}`)} icon={<ArrowRight size={16} />} iconPosition="right">
          Xem biểu đồ Longitudinal
        </Button>
      </div>
    </div>
  );
}
