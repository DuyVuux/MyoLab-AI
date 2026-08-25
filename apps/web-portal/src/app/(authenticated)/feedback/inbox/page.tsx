/**
 * Feedback Inbox Page — `/feedback/inbox`
 * Append-only log of all feedback submitted by Clinicians/KTVs.
 */
'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { MessageSquare, ArrowRight, CheckCircle, Clock, Search, Filter } from 'lucide-react';
import { Card, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { Input } from '@/components/ui/Input';
import * as MockWorkflowRepository from '@/services/mock/MockWorkflowRepository';
import type { FeedbackEvent } from '@/schemas/feedback';
import { RoleGuard } from '@/components/auth/RoleGuard';
import styles from './inbox.module.css';

export default function FeedbackInboxPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [events, setEvents] = useState<FeedbackEvent[]>([]);

  useEffect(() => {
    let list = MockWorkflowRepository.getFeedbackEvents();
    if (list.length === 0) {
      // Mock initial data if empty
      const mock: FeedbackEvent = {
        id: `FB-${Date.now()}`,
        analysisId: 'AN-001',
        sessionId: 'S-DEMO-123',
        segmentId: 'SEG-123-1',
        sourceHash: 'sha256:abcd1234efgh5678',
        originalResultHash: 'sha256:orig9876',
        modelVersion: 'v1.0.0',
        originalPrediction: 'Duỗi ngón',
        correctedPrediction: 'Nắm tay',
        reviewerCertainty: 'high',
        hasPatientConsent: true,
        reviewStatus: 'pending',
        createdAt: new Date().toISOString(),
        createdBy: 'KTV-001'
      };
      MockWorkflowRepository.saveFeedbackEvent(mock);
      list = [mock];
    }
    setEvents(list.sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime()));
    setLoading(false);
  }, []);

  if (loading) return <div className="page-container">Đang tải...</div>;

  return (
    <RoleGuard allowedRoles={['researcher', 'admin']}>
      <div className="page-container">
        <div className="page-header">
          <div className="page-header__left">
            <h1 className="page-title">ML Feedback Inbox</h1>
            <p className="page-subtitle">Danh sách phản hồi research-demo từ reviewer và người vận hành.</p>
          </div>
        </div>

        <div className={styles.controls}>
          <Input label="Tìm kiếm" placeholder="Tìm kiếm theo Session ID hoặc Segment ID..." className={styles.search} />
          <Button variant="secondary" icon={<Filter size={16} />}>Lọc</Button>
        </div>

        <div className={styles.list}>
          {events.map(fb => (
            <Card key={fb.id} padding="md" className={styles.eventCard}>
              <div className={styles.eventMain}>
                <div className={styles.eventHeader}>
                  <span className={styles.eventId}>{fb.id}</span>
                  <Badge variant={fb.reviewStatus === 'pending' ? 'warning' : fb.reviewStatus === 'accepted' ? 'success' : 'neutral'}>
                    {fb.reviewStatus.toUpperCase()}
                  </Badge>
                </div>
                <div className={styles.eventBody}>
                  <p><strong>Session:</strong> {fb.sessionId}</p>
                  <p><strong>Dự đoán gốc:</strong> <span className={styles.deleted}>{fb.originalPrediction}</span></p>
                  <p><strong>Sửa thành:</strong> <span className={styles.added}>{fb.correctedPrediction}</span></p>
                  <p><strong>Độ tự tin của Reviewer:</strong> {fb.reviewerCertainty}</p>
                </div>
              </div>
              <div className={styles.eventAction}>
                <div className={styles.meta}>
                  <span>Bởi: {fb.createdBy}</span>
                  <span>{new Date(fb.createdAt).toLocaleDateString('vi-VN')}</span>
                </div>
                <Button onClick={() => router.push(`/feedback/${fb.id}`)} variant="secondary" size="sm" icon={<ArrowRight size={14} />} iconPosition="right">
                  Adjudicate
                </Button>
              </div>
            </Card>
          ))}
        </div>
      </div>
    </RoleGuard>
  );
}
