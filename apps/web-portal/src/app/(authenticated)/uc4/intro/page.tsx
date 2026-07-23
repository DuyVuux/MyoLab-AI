/**
 * UC4 Intro — `/uc4/intro`
 * Per Section 9.2: Medical HMI feasibility — Tier 2
 */
'use client';

import { Monitor, AlertTriangle, Cpu, Users, Shield } from 'lucide-react';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { Card, CardContent } from '@/components/ui/Card';
import { Alert } from '@/components/ui/Alert';
import styles from './uc4-intro.module.css';

export default function UC4IntroPage() {
  return (
    <div className="page-container">
      <div className="page-header">
        <div className="page-header__left">
          <h1 className="page-title">UC4 · Giao diện người–máy trong môi trường y tế</h1>
          <p className="page-subtitle">
            Nghiên cứu khả thi ra lệnh bằng cử chỉ trong môi trường vô trùng và nhận dạng chuỗi ký hiệu.
          </p>
          <div style={{ display: 'flex', gap: '8px', marginTop: '8px' }}>
            <Badge variant="tier2">Tầng 2 — Nghiên cứu</Badge>
          </div>
        </div>
      </div>

      <Alert variant="warning" title="⚠️ Nghiên cứu khả thi — Cần wearable mới">
        UC4 cần phát triển wearable sEMG chuyên dụng cho môi trường vô trùng.
        Hiện chỉ có thiết kế concept và feasibility analysis.
      </Alert>

      <div className={styles.grid}>
        <Card padding="md">
          <CardContent>
            <div className={styles.cardIcon}><Users size={20} /></div>
            <h3 className={styles.cardTitle}>Đối tượng</h3>
            <p className={styles.cardText}>Nghiên cứu viên, Phẫu thuật viên (khảo sát), Kỹ sư y sinh.</p>
          </CardContent>
        </Card>
        <Card padding="md">
          <CardContent>
            <div className={styles.cardIcon}><Cpu size={20} /></div>
            <h3 className={styles.cardTitle}>Phần cứng</h3>
            <p className={styles.cardText}>Wearable sEMG chuyên dụng (cần phát triển). Phải tương thích môi trường vô trùng.</p>
          </CardContent>
        </Card>
        <Card padding="md">
          <CardContent>
            <div className={styles.cardIcon}><Monitor size={20} /></div>
            <h3 className={styles.cardTitle}>Phạm vi</h3>
            <p className={styles.cardText}>Sterile command recognition, sign sequence analysis, concept validation.</p>
          </CardContent>
        </Card>
        <Card padding="md">
          <CardContent>
            <div className={styles.cardIcon}><Shield size={20} /></div>
            <h3 className={styles.cardTitle}>Safety</h3>
            <p className={styles.cardText}>Không kết nối thiết bị phẫu thuật. Feasibility only — không ứng dụng lâm sàng.</p>
          </CardContent>
        </Card>
      </div>

      <div className={styles.ctaSection}>
        <Button variant="secondary" size="lg" disabled disabledReason="Chưa có wearable prototype UC4">
          Xem nghiên cứu khả thi (Sắp ra mắt)
        </Button>
      </div>
    </div>
  );
}
