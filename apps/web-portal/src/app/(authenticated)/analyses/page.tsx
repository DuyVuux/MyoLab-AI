/**
 * Analyses Page — `/analyses`
 * Per Section 6.10: Analysis job list with pipeline status
 */
'use client';

import Link from 'next/link';
import { BarChart3, Clock, CheckCircle, XCircle, Loader2, HelpCircle } from 'lucide-react';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import styles from './analyses.module.css';

interface AnalysisJob {
  id: string;
  sessionId: string;
  useCase: string;
  pipeline: string;
  state: 'queued' | 'running' | 'completed' | 'failed' | 'abstained';
  progress: number;
  startedAt: string;
  duration: string;
  modelVersion: string;
}

const MOCK_JOBS: AnalysisJob[] = [
  { id: 'AJ-001', sessionId: 'S-001', useCase: 'UC1', pipeline: 'Gesture Recognition', state: 'completed', progress: 100, startedAt: '2026-07-23T08:31:00', duration: '2m 15s', modelVersion: 'v1.2.0' },
  { id: 'AJ-002', sessionId: 'S-002', useCase: 'UC2', pipeline: 'Motor Assessment', state: 'abstained', progress: 30, startedAt: '2026-07-23T07:16:00', duration: '0m 45s', modelVersion: 'v1.2.0' },
  { id: 'AJ-003', sessionId: 'S-003', useCase: 'UC2', pipeline: 'Motor Assessment', state: 'queued', progress: 0, startedAt: '—', duration: '—', modelVersion: 'v1.2.0' },
  { id: 'AJ-004', sessionId: 'S-001', useCase: 'UC1', pipeline: 'Fatigue Analysis', state: 'running', progress: 67, startedAt: '2026-07-23T09:00:00', duration: '1m 30s', modelVersion: 'v1.2.0' },
];

function getStateInfo(state: AnalysisJob['state']) {
  switch (state) {
    case 'completed': return { variant: 'success' as const, icon: CheckCircle, label: 'Completed' };
    case 'running': return { variant: 'info' as const, icon: Loader2, label: 'Running' };
    case 'queued': return { variant: 'neutral' as const, icon: Clock, label: 'Queued' };
    case 'failed': return { variant: 'error' as const, icon: XCircle, label: 'Failed' };
    case 'abstained': return { variant: 'abstention' as const, icon: HelpCircle, label: 'Abstained' };
  }
}

export default function AnalysesPage() {
  return (
    <div className="page-container">
      <div className="page-header">
        <div className="page-header__left">
          <h1 className="page-title">Phiên phân tích</h1>
          <p className="page-subtitle">Danh sách analysis jobs và trạng thái pipeline.</p>
        </div>
      </div>

      <div className={styles.tableWrap}>
        <table className={styles.table}>
          <thead>
            <tr>
              <th>Job ID</th>
              <th>Session</th>
              <th>Use Case</th>
              <th>Pipeline</th>
              <th>Trạng thái</th>
              <th>Tiến trình</th>
              <th>Thời gian</th>
              <th>Model</th>
            </tr>
          </thead>
          <tbody>
            {MOCK_JOBS.map((job) => {
              const info = getStateInfo(job.state);
              return (
                <tr key={job.id}>
                  <td><span className={styles.mono}>{job.id}</span></td>
                  <td><Link href={`/sessions/${job.sessionId}/context`} className={styles.link}>{job.sessionId}</Link></td>
                  <td><Badge variant="tier1" size="sm">{job.useCase}</Badge></td>
                  <td>{job.pipeline}</td>
                  <td><Badge variant={info.variant} size="sm">{info.label}</Badge></td>
                  <td>
                    <div className={styles.progressWrap}>
                      <div className={styles.progressTrack}>
                        <div className={styles.progressFill} style={{ width: `${job.progress}%` }} />
                      </div>
                      <span className={styles.progressText}>{job.progress}%</span>
                    </div>
                  </td>
                  <td><span className={styles.mono}>{job.duration}</span></td>
                  <td><Badge variant="neutral" size="sm">{job.modelVersion}</Badge></td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
