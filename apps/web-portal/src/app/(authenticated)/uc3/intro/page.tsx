/**
 * UC3 Intro — `/uc3/intro`
 * Per Section 9.1: Prosthetics feasibility — Tier 2
 */
'use client';

import { FlaskConical, AlertTriangle, Cpu, Users, Shield, ArrowRight } from 'lucide-react';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { Card, CardContent } from '@/components/ui/Card';
import { Alert } from '@/components/ui/Alert';
import styles from './uc3-intro.module.css';

export default function UC3IntroPage() {
  return (
    <div className="page-container">
      <div className="page-header">
        <div className="page-header__left">
          <h1 className="page-title">UC3 · Điều khiển chi giả cơ điện</h1>
          <p className="page-subtitle">
            Nghiên cứu khả thi nhận diện ý định cử chỉ để điều khiển chi giả — offline replay only.
          </p>
          <div style={{ display: 'flex', gap: '8px', marginTop: '8px' }}>
            <Badge variant="tier2">Tầng 2 — Nghiên cứu</Badge>
            <Badge variant="source-deidentified">De-identified</Badge>
          </div>
        </div>
      </div>

      <Alert variant="warning" title="⚠️ Nghiên cứu khả thi">
        UC3 KHÔNG điều khiển thiết bị thật. Chỉ phân tích offline trên dữ liệu replay. 
        Cần wearable sEMG và hardware chi giả chưa xác nhận.
      </Alert>

      <div className={styles.grid}>
        <Card padding="md">
          <CardContent>
            <div className={styles.cardIcon}><Users size={20} /></div>
            <h3 className={styles.cardTitle}>Đối tượng</h3>
            <p className={styles.cardText}>Nghiên cứu viên, Kỹ sư y sinh, Chuyên gia prosthetics.</p>
          </CardContent>
        </Card>
        <Card padding="md">
          <CardContent>
            <div className={styles.cardIcon}><Cpu size={20} /></div>
            <h3 className={styles.cardTitle}>Phần cứng</h3>
            <p className={styles.cardText}>Hệ thống sEMG + chi giả cơ điện (chưa xác nhận). Hiện chỉ dùng replay data.</p>
          </CardContent>
        </Card>
        <Card padding="md">
          <CardContent>
            <div className={styles.cardIcon}><FlaskConical size={20} /></div>
            <h3 className={styles.cardTitle}>Phạm vi</h3>
            <p className={styles.cardText}>Offline intent recognition, replay analysis, expert review. Không real-time control.</p>
          </CardContent>
        </Card>
        <Card padding="md">
          <CardContent>
            <div className={styles.cardIcon}><Shield size={20} /></div>
            <h3 className={styles.cardTitle}>Safety</h3>
            <p className={styles.cardText}>Không kết nối thiết bị thật. Mọi kết quả chỉ để nghiên cứu, không ứng dụng lâm sàng.</p>
          </CardContent>
        </Card>
      </div>

      <div className={styles.ctaSection}>
        <Button variant="secondary" size="lg" disabled disabledReason="Chưa có dữ liệu replay UC3">
          Xem nghiên cứu khả thi (Sắp ra mắt)
        </Button>
      </div>
    </div>
  );
}
