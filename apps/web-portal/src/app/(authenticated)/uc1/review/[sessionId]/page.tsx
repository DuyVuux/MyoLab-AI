/**
 * UC1 Technical Review — `/uc1/review/[sessionId]`
 * Technical review of segments by KTV.
 */
'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { Check, Edit3, Shield, ArrowRight, Save } from 'lucide-react';
import { Card, CardContent, CardHeader } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { Alert } from '@/components/ui/Alert';
import { RoleGuard } from '@/components/auth/RoleGuard';
import type { SignalSegment } from '@/schemas/segment';
import type { TechnicalReview } from '@/schemas/review';
import * as MockWorkflowRepository from '@/services/mock/MockWorkflowRepository';
import styles from './uc1-review.module.css';

export default function UC1TechnicalReviewPage() {
  const params = useParams();
  const router = useRouter();
  const sessionId = params.sessionId as string;

  const [segments, setSegments] = useState<SignalSegment[]>([]);
  const [loading, setLoading] = useState(true);
  const [reviewNotes, setReviewNotes] = useState('');

  useEffect(() => {
    const existing = MockWorkflowRepository.getSegments(sessionId);
    setSegments(existing ?? []);
    setLoading(false);
  }, [sessionId]);

  const handleSubmit = () => {
    // KTV saves technical review
    const techReview: TechnicalReview = {
      id: `TREV-${Date.now()}`,
      sessionId,
      reviewerId: 'KTV-001',
      state: 'technical_approved',
      flaggedSegmentIds: [], // Would map from actual UI selection
      notes: reviewNotes,
      reviewedAt: new Date().toISOString(),
    };
    MockWorkflowRepository.saveTechnicalReview(techReview);
    
    // Redirect to Clinical Review for the Clinician
    router.push(`/sessions/${sessionId}/review`);
  };

  if (loading) return <div className="page-container">Đang tải...</div>;

  return (
    <RoleGuard allowedRoles={['ktv', 'admin']}>
      <div className="page-container">
        <div className="page-header">
          <div className="page-header__left">
            <h1 className="page-title">Technical Review (UC1)</h1>
            <p className="page-subtitle">Kỹ thuật viên duyệt chất lượng kỹ thuật trước khi trình Bác sĩ.</p>
          </div>
        </div>

      <Alert variant="info" title="Nhiệm vụ KTV">
        Kiểm tra các phân đoạn nhận diện (segments). Nếu thấy nhiễu hoặc sai lệch rõ ràng, hãy thêm ghi chú kỹ thuật. Bạn không có quyền ký duyệt kết quả lâm sàng (Clinical Sign-off).
      </Alert>

      <div className={styles.content}>
        <Card padding="md">
          <CardHeader>
            <h2 className={styles.sectionTitle}>Segments ({segments.length})</h2>
          </CardHeader>
          <CardContent>
            <div className={styles.segmentList}>
              {segments.map((seg, idx) => (
                <div key={seg.id} className={styles.segmentItem}>
                  <div className={styles.segInfo}>
                    <strong>Rep {idx + 1}</strong>
                    <span>{seg.startTimeS.toFixed(1)}s - {seg.endTimeS.toFixed(1)}s</span>
                  </div>
                  <div className={styles.segResult}>
                    <span>AI: {seg.predictedGesture}</span>
                    <Badge variant={seg.engineeringConfidence > 0.8 ? 'success' : 'warning'}>
                      {(seg.engineeringConfidence * 100).toFixed(0)}%
                    </Badge>
                  </div>
                  {seg.qualityContext.hasQCWarning && (
                    <Badge variant="warning">QC Warn</Badge>
                  )}
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card padding="md">
          <CardHeader>
            <h2 className={styles.sectionTitle}>Ghi chú kỹ thuật</h2>
          </CardHeader>
          <CardContent>
            <textarea 
              className={styles.textarea}
              placeholder="Ghi chú về chất lượng tín hiệu, nhiễu, artifact, hoặc bất thường kỹ thuật..."
              value={reviewNotes}
              onChange={(e) => setReviewNotes(e.target.value)}
              rows={5}
            />
          </CardContent>
        </Card>
      </div>

      <div className={styles.actions}>
        <Button onClick={handleSubmit} icon={<ArrowRight size={16} />} iconPosition="right">
          Hoàn tất Technical Review & Chuyển Bác Sĩ
        </Button>
      </div>
      </div>
    </RoleGuard>
  );
}
