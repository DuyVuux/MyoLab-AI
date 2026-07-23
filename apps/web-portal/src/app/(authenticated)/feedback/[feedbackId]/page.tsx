/**
 * Feedback Adjudication Page — `/feedback/[feedbackId]`
 * ML QA reviews clinical feedback and adjudicates for training pipeline.
 */
'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { ShieldCheck, ArrowLeft, XCircle, CheckCircle, Database } from 'lucide-react';
import { Card, CardContent, CardHeader } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { Alert } from '@/components/ui/Alert';
import * as MockWorkflowRepository from '@/services/mock/MockWorkflowRepository';
import type { FeedbackEvent, MLAdjudication } from '@/schemas/feedback';
import { RoleGuard } from '@/components/auth/RoleGuard';
import styles from './adjudication.module.css';

export default function FeedbackAdjudicationPage() {
  const params = useParams();
  const router = useRouter();
  const feedbackId = params.feedbackId as string;

  const [loading, setLoading] = useState(true);
  const [event, setEvent] = useState<FeedbackEvent | null>(null);
  const [adjudication, setAdjudication] = useState<MLAdjudication | null>(null);

  // Form State
  const [resolution, setResolution] = useState<'accepted' | 'rejected' | 'needs_info'>('accepted');
  const [notes, setNotes] = useState('');
  const [includeInTraining, setIncludeInTraining] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const ev = MockWorkflowRepository.getFeedbackEvent(feedbackId);
    if (ev) setEvent(ev);

    const adj = MockWorkflowRepository.getAdjudication(feedbackId);
    if (adj) {
      setAdjudication(adj);
      setResolution(adj.status as any);
      setNotes(adj.reasoning);
      setIncludeInTraining(adj.isTrainingCandidate);
    }
    setLoading(false);
  }, [feedbackId]);

  const handleSubmit = () => {
    if (!event) return;

    if (includeInTraining && !event.hasPatientConsent) {
      setError('Bệnh nhân CHƯA ĐỒNG Ý (No Consent). Không thể đưa vào tập huấn luyện.');
      return;
    }

    const decision: MLAdjudication = {
      feedbackId,
      mlQaId: 'MLQA-001',
      status: resolution as any,
      reasoning: notes,
      isTrainingCandidate: includeInTraining,
      adjudicatedAt: new Date().toISOString()
    };

    MockWorkflowRepository.saveAdjudication(decision);
    
    // Update event status
    event.reviewStatus = resolution as any;
    MockWorkflowRepository.saveFeedbackEvent(event);
    
    router.push('/feedback/inbox');
  };

  if (loading) return <div className="page-container">Đang tải...</div>;
  if (!event) return <div className="page-container">Không tìm thấy Feedback Event.</div>;

  return (
    <RoleGuard allowedRoles={['researcher', 'admin']}>
    <div className="page-container">
      <div className="page-header">
        <div className="page-header__left">
          <Button variant="ghost" onClick={() => router.back()} icon={<ArrowLeft size={16} />} className={styles.backBtn}>Quay lại</Button>
          <h1 className="page-title">Adjudicate Feedback: {feedbackId}</h1>
          <p className="page-subtitle">Phân loại lỗi mô hình (Dành cho ML QA)</p>
        </div>
      </div>

      <div className={styles.grid}>
        <div className={styles.contextColumn}>
          <Card padding="md">
            <CardHeader><h3 className={styles.cardTitle}>Chi tiết phản hồi</h3></CardHeader>
            <CardContent>
              <table className={styles.table}>
                <tbody>
                  <tr>
                    <td><strong>Session ID:</strong></td>
                    <td>{event.sessionId}</td>
                  </tr>
                  <tr>
                    <td><strong>Segment ID:</strong></td>
                    <td>{event.segmentId}</td>
                  </tr>
                  <tr>
                    <td><strong>Model Version:</strong></td>
                    <td>{event.modelVersion}</td>
                  </tr>
                  <tr>
                    <td><strong>Original Prediction:</strong></td>
                    <td><span className={styles.deleted}>{event.originalPrediction}</span></td>
                  </tr>
                  <tr>
                    <td><strong>Corrected By KTV/Dr:</strong></td>
                    <td><span className={styles.added}>{event.correctedPrediction}</span></td>
                  </tr>
                  <tr>
                    <td><strong>Reviewer Certainty:</strong></td>
                    <td><Badge variant="neutral">{event.reviewerCertainty.toUpperCase()}</Badge></td>
                  </tr>
                </tbody>
              </table>
            </CardContent>
          </Card>

          <Card padding="md">
            <CardHeader><h3 className={styles.cardTitle}>Data Provenance & Privacy</h3></CardHeader>
            <CardContent>
              <div className={styles.privacyBox}>
                <div className={styles.privacyItem}>
                  <span>Data Source Hash:</span>
                  <code className={styles.hash}>{event.sourceHash}</code>
                </div>
                <div className={styles.privacyItem}>
                  <span>Patient Consent for ML Training:</span>
                  {event.hasPatientConsent ? (
                    <Badge variant="success">GRANTED</Badge>
                  ) : (
                    <Badge variant="error">DENIED</Badge>
                  )}
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        <div className={styles.inputColumn}>
          <Card padding="md">
            <CardHeader><h3 className={styles.cardTitle}>Adjudication Decision</h3></CardHeader>
            <CardContent>
              <div className={styles.formGroup}>
                <label>Kết luận (Resolution):</label>
                <select 
                  className={styles.select}
                  value={resolution}
                  onChange={(e) => setResolution(e.target.value as any)}
                >
                  <option value="accepted">Chấp nhận (Label đúng, Model sai)</option>
                  <option value="rejected">Từ chối (Label sai, Model đúng)</option>
                  <option value="needs_info">Không thể kết luận</option>
                </select>
              </div>

              <div className={styles.formGroup}>
                <label>Ghi chú của ML QA:</label>
                <textarea 
                  className={styles.textarea}
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  rows={4}
                  placeholder="Phân tích nguyên nhân lỗi (nếu có)..."
                />
              </div>

              <div className={styles.checkboxGroup}>
                <input 
                  type="checkbox" 
                  id="includeTraining" 
                  checked={includeInTraining}
                  onChange={(e) => {
                    setIncludeInTraining(e.target.checked);
                    setError(null);
                  }}
                  disabled={!event.hasPatientConsent || resolution !== 'accepted'}
                />
                <label htmlFor="includeTraining">
                  <strong>Đưa vào tập huấn luyện (Training Candidate)</strong>
                  <p className={styles.helpText}>Chỉ cho phép nếu bệnh nhân đồng ý và phản hồi được chấp nhận.</p>
                </label>
              </div>

              {error && <div className={styles.errorMessage}>{error}</div>}

              <div className={styles.actions}>
                <Button onClick={handleSubmit} icon={<ShieldCheck size={16} />} iconPosition="left">
                  Lưu Adjudication
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
      </div>
    </RoleGuard>
  );
}
