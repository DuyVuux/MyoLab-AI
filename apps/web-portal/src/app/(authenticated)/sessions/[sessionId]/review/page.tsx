/**
 * Human Review Page — `/sessions/[sessionId]/review`
 * Reviewer records research-demo notes. Includes guardrails for low confidence/QC fail.
 */
'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { FileSignature, ShieldAlert, CheckCircle, AlertTriangle, ArrowRight } from 'lucide-react';
import { Card, CardContent, CardHeader } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { Alert } from '@/components/ui/Alert';
import * as MockWorkflowRepository from '@/services/mock/MockWorkflowRepository';
import type { QCResult } from '@/schemas/quality';
import type { AnalysisJob } from '@/schemas/analysis';
import type { TechnicalReview, ClinicalReview, OverridePolicyCode } from '@/schemas/review';
import { RoleGuard } from '@/components/auth/RoleGuard';
import styles from './review.module.css';

export default function ClinicalReviewPage() {
  const params = useParams();
  const router = useRouter();
  const sessionId = params.sessionId as string;

  const [loading, setLoading] = useState(true);
  const [qc, setQc] = useState<QCResult | null>(null);
  const [analysis, setAnalysis] = useState<AnalysisJob | null>(null);
  const [techReview, setTechReview] = useState<TechnicalReview | null>(null);

  // Form State
  const [conclusion, setConclusion] = useState('');
  const [overrideCode, setOverrideCode] = useState<OverridePolicyCode | ''>('');
  const [overrideDetail, setOverrideDetail] = useState('');
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setQc(MockWorkflowRepository.getQCResult(sessionId));
    setAnalysis(MockWorkflowRepository.getAnalysisJob(sessionId));
    setTechReview(MockWorkflowRepository.getTechnicalReview(sessionId));
    
    // Check if already reviewed
    const existing = MockWorkflowRepository.getClinicalReview(sessionId);
    if (existing) {
      setConclusion(existing.clinicalConclusion);
      if (existing.structuredOverride) {
        setOverrideCode(existing.structuredOverride.code);
        setOverrideDetail(existing.structuredOverride.detail);
      }
    }
    
    setLoading(false);
  }, [sessionId]);

  const isQCFail = qc?.overallVerdict === 'fail';
  const isLowConfidence = (analysis?.output?.engineeringConfidence ?? 1) < 0.6;
  const requiresOverride = isQCFail || isLowConfidence;

  const handleSignOff = () => {
    if (!conclusion.trim()) {
      setError('Vui lòng nhập ghi chú human review.');
      return;
    }
    
    // Guardrail Enforcement
    if (requiresOverride) {
      if (!overrideCode) {
        setError('Bắt buộc chọn mã ghi đè (Override Policy) do QC Fail hoặc độ tin cậy thấp.');
        return;
      }
      if (overrideDetail.trim().length < 10) {
        setError('Chi tiết ghi đè phải trên 10 ký tự.');
        return;
      }
      // Guardrail: no positive on QC fail (we simulate this by checking if conclusion contains 'bình thường' etc, but simple alert here)
      if (isQCFail && conclusion.toLowerCase().includes('bình thường')) {
        setError('Không được ghi "bình thường" khi QC FAILED. Vui lòng giải thích ngoại lệ kỹ thuật rõ ràng.');
        return;
      }
    }

    const review: ClinicalReview = {
      id: `CREV-${Date.now()}`,
      sessionId,
      reviewerId: 'DR-001', // Mock
      state: 'clinical_approved',
      clinicalConclusion: conclusion,
      structuredOverride: requiresOverride && overrideCode ? {
        code: overrideCode as OverridePolicyCode,
        detail: overrideDetail
      } : undefined,
      signOffAt: new Date().toISOString(),
      signOffHash: 'mock-signature-hash-123456789'
    };

    MockWorkflowRepository.saveClinicalReview(review);
    
    // Generate Report Draft implicitly
    if (!MockWorkflowRepository.getReport(sessionId)) {
      MockWorkflowRepository.saveReport({
        id: `REP-${Date.now()}`,
        sessionId,
        state: 'pending_signoff', // needs final report generation step
        templateVersion: 'v1.2',
        reportVersion: 1,
        aiTechnicalSummary: analysis?.output?.technicalConclusion || '',
        clinicianApprovedConclusion: conclusion,
        watermark: 'DRAFT - PENDING SIGNOFF',
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString()
      });
    }

    router.push(`/sessions/${sessionId}/report`);
  };

  if (loading) return <div className="page-container">Đang tải...</div>;

  return (
    <RoleGuard allowedRoles={['doctor', 'admin']}>
      <div className="page-container">
        <div className="page-header">
          <div className="page-header__left">
            <h1 className="page-title">Human Review Research Check</h1>
            <p className="page-subtitle">Ghi nhận phần review của bác sĩ trong phạm vi research-only demo.</p>
          </div>
        </div>

        <div className={styles.grid}>
          {/* Left Column: Context */}
          <div className={styles.contextColumn}>
            <Card padding="md">
              <CardHeader><h3 className={styles.cardTitle}>QC & Technical Context</h3></CardHeader>
              <CardContent>
                <div className={styles.contextList}>
                  <div className={styles.contextItem}>
                    <span>QC Verdict:</span>
                    <Badge variant={qc?.overallVerdict === 'pass' ? 'success' : qc?.overallVerdict === 'warning' ? 'warning' : 'error'}>
                    {qc?.overallVerdict || 'Unknown'}
                  </Badge>
                </div>
                <div className={styles.contextItem}>
                  <span>AI Confidence:</span>
                  <Badge variant={isLowConfidence ? 'error' : 'success'}>
                    {((analysis?.output?.engineeringConfidence ?? 0) * 100).toFixed(0)}%
                  </Badge>
                </div>
                <div className={styles.contextItem}>
                  <span>Technical Review:</span>
                  <Badge variant={techReview?.state === 'technical_approved' ? 'success' : 'warning'}>
                    {techReview?.state || 'Pending'}
                  </Badge>
                </div>
              </div>
              
              {techReview?.notes && (
                <div className={styles.techNotes}>
                  <strong>Ghi chú từ KTV:</strong>
                  <p>{techReview.notes}</p>
                </div>
              )}
            </CardContent>
          </Card>

          <Card padding="md">
            <CardHeader><h3 className={styles.cardTitle}>AI Technical Conclusion</h3></CardHeader>
            <CardContent>
              <Alert variant="info" title="Lưu ý">Đây là kết luận kỹ thuật không thể thay đổi (Immutable).</Alert>
              <p className={styles.aiText}>{analysis?.output?.technicalConclusion || 'Không có dữ liệu phân tích.'}</p>
            </CardContent>
          </Card>
        </div>

        {/* Right Column: Human review input */}
        <div className={styles.inputColumn}>
          <Card padding="md">
            <CardHeader><h3 className={styles.cardTitle}>Ghi chú human review</h3></CardHeader>
            <CardContent>
              <textarea 
                className={styles.textarea}
                placeholder="Nhập ghi chú chuyên môn trong phạm vi research demo. Đây không phải kết luận lâm sàng..."
                value={conclusion}
                onChange={(e) => { setConclusion(e.target.value); setError(null); }}
                rows={6}
              />

              {requiresOverride && (
                <div className={styles.overrideBox}>
                  <Alert variant="warning" title="Guardrail Triggered">
                    Dữ liệu có độ tin cậy thấp hoặc QC Fail. Bắt buộc sử dụng Structured Override Policy.
                  </Alert>
                  
                  <div className={styles.formGroup}>
                    <label>Mã Override:</label>
                    <select 
                      className={styles.select}
                      value={overrideCode}
                      onChange={(e) => setOverrideCode(e.target.value as OverridePolicyCode)}
                    >
                      <option value="">-- Chọn mã ghi đè --</option>
                      <option value="OVR_ARTIFACT">Artifact đã có giải thích kỹ thuật kèm reason code</option>
                      <option value="OVR_FATIGUE_MASK">Tín hiệu nhiễu đã được ghi nhận, chỉ dùng trong demo kỹ thuật</option>
                      <option value="OVR_CROSSTALK">Crosstalk đã được kiểm tra bằng bằng chứng kỹ thuật</option>
                      <option value="OVR_CLINICAL_CORRELATION">Phù hợp hồ sơ kỹ thuật quan sát được, không phải clinical claim</option>
                      <option value="OVR_OTHER">Lý do khác</option>
                    </select>
                  </div>
                  
                  <div className={styles.formGroup}>
                    <label>Chi tiết lý do ghi đè (Bắt buộc):</label>
                    <textarea 
                      className={styles.textareaSmall}
                      value={overrideDetail}
                      onChange={(e) => setOverrideDetail(e.target.value)}
                      rows={3}
                    />
                  </div>
                </div>
              )}

              {error && <div className={styles.errorMessage}>{error}</div>}

              <div className={styles.actions}>
                <Button onClick={handleSignOff} icon={<FileSignature size={16} />} iconPosition="left">
                  Ghi nhận review & chuyển sang report
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
