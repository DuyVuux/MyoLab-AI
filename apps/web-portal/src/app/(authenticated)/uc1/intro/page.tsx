/**
 * UC1 Intro Page — `/uc1/intro`
 * Per Section 7.1: Use case overview, hardware requirements, start flow
 */
'use client';

import Link from 'next/link';
import {
  Activity,
  Cpu,
  Users,
  Shield,
  AlertTriangle,
  CheckCircle,
  ClipboardList,
  ArrowRight,
} from 'lucide-react';
import { Card, CardContent } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { Alert } from '@/components/ui/Alert';
import { ROUTES } from '@/config/useCaseRoutes';
import styles from './uc1-intro.module.css';

export default function UC1IntroPage() {
  return (
    <div className="page-container">
      <div className="page-header">
        <div className="page-header__left">
          <h1 className="page-title">
            UC1 · Biofeedback cử chỉ trong PHCN đột quỵ
          </h1>
          <p className="page-subtitle">
            Nhận diện cử chỉ tay theo thời gian thực hỗ trợ tập luyện phục hồi chức năng sau đột quỵ.
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

      {/* Disclaimers — mandatory per spec */}
      <Alert variant="warning" title="Lưu ý quan trọng">
        Research-only prototype với dữ liệu mô phỏng. Kết quả hỗ trợ kỹ thuật và không dùng cho quyết định lâm sàng.
        Human review bắt buộc để ghi nhận giới hạn bằng chứng.
      </Alert>

      {/* Use case overview */}
      <div className={styles.overviewGrid}>
        <Card padding="md">
          <CardContent>
            <div className={styles.cardIcon}>
              <Users size={20} />
            </div>
            <h3 className={styles.cardTitle}>Đối tượng</h3>
            <p className={styles.cardText}>
              KTV Phục hồi chức năng (thao tác chính), người tham gia demo (biofeedback thụ động), bác sĩ PHCN (human review research-only).
            </p>
          </CardContent>
        </Card>

        <Card padding="md">
          <CardContent>
            <div className={styles.cardIcon}>
              <Cpu size={20} />
            </div>
            <h3 className={styles.cardTitle}>Phần cứng</h3>
            <p className={styles.cardText}>
              Noraxon Ultium sEMG (4–8 kênh). Prototype sử dụng Noraxon export mock hoặc synthetic data.
            </p>
          </CardContent>
        </Card>

        <Card padding="md">
          <CardContent>
            <div className={styles.cardIcon}>
              <Activity size={20} />
            </div>
            <h3 className={styles.cardTitle}>Luồng chính</h3>
            <p className={styles.cardText}>
              Tạo phiên → Import dữ liệu → Mapping kênh → QC Signal → Phân tích AI → Biofeedback → Review → Report.
            </p>
          </CardContent>
        </Card>

        <Card padding="md">
          <CardContent>
            <div className={styles.cardIcon}>
              <Shield size={20} />
            </div>
            <h3 className={styles.cardTitle}>Safety</h3>
            <p className={styles.cardText}>
              Model phải vượt QC signal quality trước khi chạy. Abstain nếu confidence thấp. Bias &amp; fairness monitoring per Section 6.14.
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Pipeline steps */}
      <section className={styles.pipelineSection}>
        <h2 className={styles.sectionTitle}>Pipeline phiên UC1</h2>
        <div className={styles.pipeline}>
          {[
            { step: 1, label: 'Tạo phiên', desc: 'Subject, protocol, side, muscles', icon: ClipboardList },
            { step: 2, label: 'Import dữ liệu', desc: 'Noraxon export / CSV / Synthetic', icon: Cpu },
            { step: 3, label: 'Mapping kênh', desc: 'Gán kênh EMG → cơ giải phẫu', icon: Activity },
            { step: 4, label: 'QC Signal', desc: 'SNR, baseline noise, saturation check', icon: AlertTriangle },
            { step: 5, label: 'AI Analysis', desc: 'Gesture recognition + confidence', icon: Activity },
            { step: 6, label: 'Biofeedback', desc: 'Hiển thị kết quả thời gian thực', icon: Activity },
            { step: 7, label: 'Human review', desc: 'KTV/BS xem xét và ghi nhận giới hạn', icon: CheckCircle },
          ].map((item) => {
            const Icon = item.icon;
            return (
              <div key={item.step} className={styles.pipelineStep}>
                <div className={styles.pipelineNumber}>{item.step}</div>
                <div>
                  <div className={styles.pipelineLabel}>{item.label}</div>
                  <div className={styles.pipelineDesc}>{item.desc}</div>
                </div>
              </div>
            );
          })}
        </div>
      </section>

      {/* CTA */}
      <div className={styles.ctaSection}>
        <Link href={ROUTES.SESSION_NEW}>
          <Button size="lg" icon={<ArrowRight size={18} />} iconPosition="right">
            Tạo phiên UC1 mới
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
