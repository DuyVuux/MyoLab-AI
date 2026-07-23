/**
 * UC2 Longitudinal Page — `/uc2/longitudinal/[subjectRef]`
 * Compares sessions for the same subject over time.
 * Includes Compatibility Gate (blocks comparison if protocol/layout differs).
 */
'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { LineChart, Activity, AlertTriangle, ArrowLeft } from 'lucide-react';
import { Card, CardContent, CardHeader } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { Alert } from '@/components/ui/Alert';
import * as MockWorkflowRepository from '@/services/mock/MockWorkflowRepository';
import type { SessionContext } from '@/schemas/session';
import styles from './uc2-longitudinal.module.css';

export default function UC2LongitudinalPage() {
  const params = useParams();
  const router = useRouter();
  const subjectRef = params.subjectRef as string;

  const [loading, setLoading] = useState(true);
  const [sessions, setSessions] = useState<SessionContext[]>([]);
  const [compatibilityError, setCompatibilityError] = useState<string | null>(null);

  useEffect(() => {
    // 1. Auto-query sessions for subject
    const store = (MockWorkflowRepository as any).getStore?.(); 
    // Hack: since we didn't expose getSessionsBySubject, we will simulate it by querying all and filtering
    // In a real app we'd add getSessionsBySubject(subjectRef)
    const allSessions: SessionContext[] = store ? Object.values(store.sessions) : [];
    
    // Fallback if store empty (for demonstration)
    const subjectSessions = allSessions.filter(s => s.subjectRef === subjectRef);
    
    if (subjectSessions.length < 2) {
      // Mock some historical sessions if we only have 0 or 1
      const historical: SessionContext = {
        sessionId: `S-HIST-${Date.now()}`,
        subjectRef,
        useCaseId: 'uc2',
        protocolId: 'PROT-UC2-001',
        protocolVersion: '2.0',
        affectedSide: 'Left',
        referenceSide: 'Right',
        targetMuscles: ['Biceps brachii', 'Triceps brachii'],
        electrodeLayout: [],
        requiresCalibration: true,
        dataSourceIntent: 'synthetic',
        sessionType: 'baseline',
        operator: 'KTV-001',
        consentScope: ['quality_improvement'],
        state: 'analysis_complete',
        createdAt: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString() // 30 days ago
      };
      
      const current: SessionContext = {
        sessionId: `S-CURR-${Date.now()}`,
        subjectRef,
        useCaseId: 'uc2',
        protocolId: 'PROT-UC2-001',
        protocolVersion: '2.0',
        affectedSide: 'Left',
        referenceSide: 'Right',
        targetMuscles: ['Biceps brachii', 'Triceps brachii'],
        electrodeLayout: [],
        requiresCalibration: true,
        dataSourceIntent: 'synthetic',
        sessionType: 'follow_up',
        operator: 'KTV-001',
        consentScope: ['quality_improvement'],
        state: 'analysis_complete',
        createdAt: new Date().toISOString()
      };
      setSessions([historical, current]);
    } else {
      setSessions(subjectSessions.sort((a, b) => new Date(a.createdAt).getTime() - new Date(b.createdAt).getTime()));
    }
    
    setLoading(false);
  }, [subjectRef]);

  // Compatibility Gate Check
  useEffect(() => {
    if (sessions.length < 2) return;
    
    const base = sessions[0];
    for (let i = 1; i < sessions.length; i++) {
      const s = sessions[i];
      if (s.protocolId !== base.protocolId || s.protocolVersion !== base.protocolVersion) {
        setCompatibilityError(`Protocol mismatch: ${base.protocolId} (v${base.protocolVersion}) vs ${s.protocolId} (v${s.protocolVersion})`);
        return;
      }
      // Simple check for muscle array equality
      if (s.targetMuscles.join(',') !== base.targetMuscles.join(',')) {
        setCompatibilityError(`Electrode layout mismatch: ${base.targetMuscles.join(', ')} vs ${s.targetMuscles.join(', ')}`);
        return;
      }
    }
    setCompatibilityError(null);
  }, [sessions]);

  if (loading) return <div className="page-container">Đang tải...</div>;

  return (
    <div className="page-container">
      <div className="page-header">
        <div className="page-header__left">
          <h1 className="page-title">Longitudinal Trend</h1>
          <p className="page-subtitle">Theo dõi tiến triển bệnh nhân {subjectRef}</p>
        </div>
        <div className="page-header__right">
          <Badge variant="neutral">{sessions.length} sessions</Badge>
        </div>
      </div>

      {compatibilityError ? (
        <Alert variant="error" title="Compatibility Gate Failed">
          {compatibilityError}
          <br/>
          Không thể so sánh dữ liệu longitudinal do cấu hình các phiên không đồng nhất.
        </Alert>
      ) : (
        <div className={styles.dashboard}>
          <Card padding="md">
            <CardHeader><h2 className={styles.cardTitle}>Peak Amplitude (%MVC) Trend</h2></CardHeader>
            <CardContent>
              <div className={styles.chartMock}>
                {/* SVG Mock of a Line Chart */}
                <svg viewBox="0 0 400 150" className={styles.chartSvg}>
                  {/* Grid */}
                  <line x1="0" y1="25" x2="400" y2="25" stroke="var(--color-border-subtle)" strokeWidth="1" />
                  <line x1="0" y1="75" x2="400" y2="75" stroke="var(--color-border-subtle)" strokeWidth="1" />
                  <line x1="0" y1="125" x2="400" y2="125" stroke="var(--color-border-subtle)" strokeWidth="1" />
                  
                  {/* Line */}
                  <polyline points="0,100 100,110 200,80 300,50 400,30" fill="none" stroke="var(--color-primary)" strokeWidth="3" />
                  
                  {/* Dots */}
                  <circle cx="0" cy="100" r="4" fill="var(--color-primary)" />
                  <circle cx="100" cy="110" r="4" fill="var(--color-primary)" />
                  <circle cx="200" cy="80" r="4" fill="var(--color-primary)" />
                  <circle cx="300" cy="50" r="4" fill="var(--color-primary)" />
                  <circle cx="400" cy="30" r="4" fill="var(--color-primary)" />
                </svg>
                <div className={styles.chartLabels}>
                  <span>Tuần 1</span>
                  <span>Tuần 2</span>
                  <span>Tuần 3</span>
                  <span>Tuần 4</span>
                  <span>Hiện tại</span>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card padding="md">
            <CardHeader><h2 className={styles.cardTitle}>Symmetry Index Trend</h2></CardHeader>
            <CardContent>
              <div className={styles.chartMock}>
                {/* SVG Mock of a Bar Chart */}
                <svg viewBox="0 0 400 150" className={styles.chartSvg}>
                  {/* Grid */}
                  <line x1="0" y1="75" x2="400" y2="75" stroke="var(--color-border)" strokeWidth="1" strokeDasharray="4 4" />
                  
                  {/* Bars (progressing toward 0 symmetry difference) */}
                  <rect x="20" y="20" width="40" height="55" fill="var(--color-error)" />
                  <rect x="100" y="30" width="40" height="45" fill="var(--color-warning)" />
                  <rect x="180" y="50" width="40" height="25" fill="var(--color-warning)" />
                  <rect x="260" y="65" width="40" height="10" fill="var(--color-success)" />
                  <rect x="340" y="70" width="40" height="5" fill="var(--color-success)" />
                </svg>
                <div className={styles.chartLabels}>
                  <span>Tuần 1</span>
                  <span>Tuần 2</span>
                  <span>Tuần 3</span>
                  <span>Tuần 4</span>
                  <span>Hiện tại</span>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      <div className={styles.actions}>
        <Button variant="secondary" onClick={() => router.back()} icon={<ArrowLeft size={16} />}>
          Quay lại
        </Button>
      </div>
    </div>
  );
}
