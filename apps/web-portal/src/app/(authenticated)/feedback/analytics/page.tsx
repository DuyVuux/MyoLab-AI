/**
 * Feedback Analytics — `/feedback/analytics`
 * Per Section 10.5: Correction rates, model performance, trend
 */
'use client';

import { BarChart3, TrendingUp, TrendingDown, AlertTriangle, Brain, Users, CheckCircle } from 'lucide-react';
import { Card, CardContent, CardHeader } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Alert } from '@/components/ui/Alert';
import styles from './analytics.module.css';

const MOCK_STATS = {
  totalFeedback: 47,
  correctionRate: 12.5,
  correctionTrend: -2.3,
  topCorrectedGesture: 'Gập cổ tay',
  abstentionRate: 8.2,
  avgConfidenceCorrections: 0.68,
  adjudicationPending: 4,
  trainingCandidates: 12,
};

const MOCK_BREAKDOWN = [
  { gesture: 'Nắm tay (Fist)', total: 120, corrections: 3, rate: 2.5 },
  { gesture: 'Mở tay (Open)', total: 98, corrections: 5, rate: 5.1 },
  { gesture: 'Gập cổ tay (Flexion)', total: 45, corrections: 12, rate: 26.7 },
  { gesture: 'Duỗi ngón (Extension)', total: 67, corrections: 4, rate: 6.0 },
  { gesture: 'Pronation', total: 22, corrections: 3, rate: 13.6 },
];

export default function FeedbackAnalyticsPage() {
  return (
    <div className="page-container">
      <div className="page-header">
        <div className="page-header__left">
          <h1 className="page-title">Feedback Analytics</h1>
          <p className="page-subtitle">Thống kê phản hồi, tỷ lệ sửa lỗi, và xu hướng hiệu suất model.</p>
        </div>
      </div>

      <Alert variant="info" title="Dữ liệu mô phỏng">
        Thống kê bên dưới là dữ liệu synthetic minh họa. Trong production, sẽ aggregated từ feedback thực.
      </Alert>

      {/* KPI cards */}
      <div className={styles.kpiGrid}>
        <Card padding="md">
          <CardContent>
            <div className={styles.kpiIcon}><Brain size={20} /></div>
            <div className={styles.kpiValue}>{MOCK_STATS.correctionRate}%</div>
            <div className={styles.kpiLabel}>Tỷ lệ sửa lỗi</div>
            <div className={[styles.kpiTrend, MOCK_STATS.correctionTrend < 0 ? styles['kpiTrend--good'] : styles['kpiTrend--bad']].join(' ')}>
              {MOCK_STATS.correctionTrend < 0 ? <TrendingDown size={14} /> : <TrendingUp size={14} />}
              {Math.abs(MOCK_STATS.correctionTrend)}% so với tuần trước
            </div>
          </CardContent>
        </Card>

        <Card padding="md">
          <CardContent>
            <div className={styles.kpiIcon}><AlertTriangle size={20} /></div>
            <div className={styles.kpiValue}>{MOCK_STATS.abstentionRate}%</div>
            <div className={styles.kpiLabel}>Tỷ lệ Abstention</div>
            <div className={styles.kpiSubtext}>AI từ chối đưa ra kết quả</div>
          </CardContent>
        </Card>

        <Card padding="md">
          <CardContent>
            <div className={styles.kpiIcon}><BarChart3 size={20} /></div>
            <div className={styles.kpiValue}>{MOCK_STATS.totalFeedback}</div>
            <div className={styles.kpiLabel}>Tổng feedback</div>
            <div className={styles.kpiSubtext}>{MOCK_STATS.adjudicationPending} đang chờ adjudication</div>
          </CardContent>
        </Card>

        <Card padding="md">
          <CardContent>
            <div className={styles.kpiIcon}><CheckCircle size={20} /></div>
            <div className={styles.kpiValue}>{MOCK_STATS.trainingCandidates}</div>
            <div className={styles.kpiLabel}>Training Candidates</div>
            <div className={styles.kpiSubtext}>Đã adjudicated, sẵn sàng export</div>
          </CardContent>
        </Card>
      </div>

      {/* Breakdown table */}
      <Card padding="md">
        <CardHeader>
          <h2 style={{ fontSize: 'var(--font-size-md)', fontWeight: 600 }}>Correction Rate theo Gesture</h2>
        </CardHeader>
        <CardContent>
          <div style={{ overflowX: 'auto' }}>
            <table className={styles.table}>
              <thead>
                <tr>
                  <th>Gesture</th>
                  <th>Tổng inferences</th>
                  <th>Corrections</th>
                  <th>Rate</th>
                  <th>Đánh giá</th>
                </tr>
              </thead>
              <tbody>
                {MOCK_BREAKDOWN.map((row) => (
                  <tr key={row.gesture}>
                    <td style={{ fontWeight: 500 }}>{row.gesture}</td>
                    <td>{row.total}</td>
                    <td>{row.corrections}</td>
                    <td style={{ fontFamily: 'var(--font-mono)' }}>{row.rate.toFixed(1)}%</td>
                    <td>
                      <Badge variant={row.rate < 5 ? 'success' : row.rate < 15 ? 'warning' : 'error'} size="sm">
                        {row.rate < 5 ? 'Tốt' : row.rate < 15 ? 'Cần theo dõi' : 'Cần cải thiện'}
                      </Badge>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
