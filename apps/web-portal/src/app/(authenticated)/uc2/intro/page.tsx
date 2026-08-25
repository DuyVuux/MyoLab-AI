/**
 * UC2 Intro Page — `/uc2/intro`
 * Per Section 8.1: Quantitative motor assessment overview
 */
'use client';

import Link from 'next/link';
import {
  Stethoscope,
  Cpu,
  Users,
  Shield,
  ArrowRight,
  BarChart3,
  TrendingUp,
  Activity,
  CheckCircle,
  ClipboardList,
  Repeat,
  Gauge,
} from 'lucide-react';
import { Card, CardContent } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { Alert } from '@/components/ui/Alert';
import { ROUTES } from '@/config/useCaseRoutes';
import styles from './uc2-intro.module.css';

const UC2_KPIS = [
  { icon: Gauge, label: 'Motor Quality Index', desc: 'Chỉ số tổng hợp chất lượng vận động' },
  { icon: Repeat, label: 'Repeatability Score', desc: 'Đánh giá tính ổn định lặp lại' },
  { icon: BarChart3, label: 'Symmetry Index', desc: 'So sánh bên ảnh hưởng vs. bên tham chiếu' },
  { icon: TrendingUp, label: 'Fatigue Resistance', desc: 'Khả năng chống mệt mỏi cơ' },
  { icon: Activity, label: 'Activation Pattern', desc: 'Mẫu kích hoạt cơ so với norm' },
];

export default function UC2IntroPage() {
  return (
    <div className="page-container">
      <div className="page-header">
        <div className="page-header__left">
          <h1 className="page-title">UC2 · Đánh giá định lượng chức năng vận động tay</h1>
          <p className="page-subtitle">
            Phân tích định lượng chất lượng vận động, repeatability, symmetry và fatigue qua nhiều phiên.
          </p>
          <div style={{ display: 'flex', gap: '8px', marginTop: '8px' }}>
            <Badge variant="tier1">Tầng 1 — MVP</Badge>
            <Badge variant="source-synthetic">Dữ liệu Synthetic</Badge>
          </div>
        </div>
        <div className="page-header__right">
          <Link href={ROUTES.SESSION_NEW}>
            <Button icon={<ArrowRight size={16} />} iconPosition="right">
              Bắt đầu phiên mới
            </Button>
          </Link>
        </div>
      </div>

      <Alert variant="warning" title="Lưu ý quan trọng">
        Chỉ số kỹ thuật — không dùng cho chẩn đoán, điều trị hoặc quyết định lâm sàng.
        Human review bắt buộc.
      </Alert>

      {/* KPI preview */}
      <section className={styles.kpiSection}>
        <h2 className={styles.sectionTitle}>Chỉ số đánh giá chính (KPIs)</h2>
        <div className={styles.kpiGrid}>
          {UC2_KPIS.map((kpi) => {
            const Icon = kpi.icon;
            return (
              <Card key={kpi.label} padding="md" hoverable>
                <CardContent>
                  <div className={styles.kpiIcon}>
                    <Icon size={20} />
                  </div>
                  <h3 className={styles.kpiLabel}>{kpi.label}</h3>
                  <p className={styles.kpiDesc}>{kpi.desc}</p>
                </CardContent>
              </Card>
            );
          })}
        </div>
      </section>

      {/* Pipeline */}
      <section className={styles.pipelineSection}>
        <h2 className={styles.sectionTitle}>Pipeline phiên UC2</h2>
        <div className={styles.pipeline}>
          {[
            { step: 1, label: 'Tạo phiên', desc: 'Subject, protocol UC2, side, muscles' },
            { step: 2, label: 'Import dữ liệu', desc: 'Noraxon / CSV / Synthetic (batch supported)' },
            { step: 3, label: 'QC & Calibration', desc: 'Kiểm tra chất lượng + tham chiếu MVC' },
            { step: 4, label: 'Phân tích định lượng', desc: '5 KPI + envelope, spectrum, fatigue' },
            { step: 5, label: 'So sánh dọc', desc: 'Longitudinal trend qua nhiều phiên' },
            { step: 6, label: 'Human review', desc: 'Technical evidence → research report' },
          ].map((item) => (
            <div key={item.step} className={styles.pipelineStep}>
              <div className={styles.pipelineNumber}>{item.step}</div>
              <div>
                <div className={styles.pipelineLabel}>{item.label}</div>
                <div className={styles.pipelineDesc}>{item.desc}</div>
              </div>
            </div>
          ))}
        </div>
      </section>

      <div className={styles.ctaSection}>
        <Link href={ROUTES.SESSION_NEW}>
          <Button size="lg" icon={<ArrowRight size={18} />} iconPosition="right">
            Tạo phiên UC2 mới
          </Button>
        </Link>
        <Link href={ROUTES.SESSIONS}>
          <Button variant="secondary" size="lg">
            Xem phiên đang có
          </Button>
        </Link>
      </div>
    </div>
  );
}
