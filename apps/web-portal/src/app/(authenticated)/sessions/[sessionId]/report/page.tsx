/**
 * Report Page — `/sessions/[sessionId]/report`
 * PDF-like view. Strict separation of AI vs Clinical output. Immutable after finalized.
 */
'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { FileText, Download, Printer, FileSignature, ShieldCheck, FileKey } from 'lucide-react';
import { Card, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { Alert } from '@/components/ui/Alert';
import * as MockWorkflowRepository from '@/services/mock/MockWorkflowRepository';
import type { ReportDocument } from '@/schemas/report';
import type { SessionContext } from '@/schemas/session';
import type { ClinicalReview, TechnicalReview } from '@/schemas/review';
import { RoleGuard } from '@/components/auth/RoleGuard';
import styles from './report.module.css';

export default function ReportPage() {
  const params = useParams();
  const router = useRouter();
  const sessionId = params.sessionId as string;

  const [loading, setLoading] = useState(true);
  const [session, setSession] = useState<SessionContext | null>(null);
  const [report, setReport] = useState<ReportDocument | null>(null);
  const [clinicalReview, setClinicalReview] = useState<ClinicalReview | null>(null);

  useEffect(() => {
    setSession(MockWorkflowRepository.getSession(sessionId));
    setReport(MockWorkflowRepository.getReport(sessionId));
    setClinicalReview(MockWorkflowRepository.getClinicalReview(sessionId));
    setLoading(false);
  }, [sessionId]);

  const handleFinalize = () => {
    if (!report) return;
    const finalReport: ReportDocument = {
      ...report,
      state: 'finalized',
      watermark: 'FINALIZED',
      reportHash: 'sha256:final-document-hash-' + Date.now(),
      finalizedAt: new Date().toISOString()
    };
    MockWorkflowRepository.saveReport(finalReport);
    setReport(finalReport);
  };

  if (loading) return <div className="page-container">Đang tải...</div>;

  if (!report) {
    return (
      <div className="page-container">
        <Alert variant="warning" title="Không tìm thấy Report">
          Phiên {sessionId} chưa tạo Report Draft. Bạn cần hoàn thành Clinical Sign-off trước.
        </Alert>
        <Button onClick={() => router.push(`/sessions/${sessionId}/review`)}>Đi tới Clinical Review</Button>
      </div>
    );
  }

  const isFinalized = report.state === 'finalized';

  return (
    <RoleGuard allowedRoles={['doctor', 'admin']}>
      <div className="page-container">
        <div className="page-header">
        <div className="page-header__left">
          <h1 className="page-title">Clinical Report</h1>
          <p className="page-subtitle">Báo cáo kết quả lâm sàng (Template v{report.templateVersion})</p>
        </div>
        <div className="page-header__right">
          {!isFinalized && clinicalReview && (
            <Button onClick={handleFinalize} icon={<FileSignature size={16} />} variant="primary">
              Ký & Phát hành (Finalize)
            </Button>
          )}
          <Button variant="secondary" icon={<Printer size={16} />}>In ấn</Button>
          <Button variant="secondary" icon={<Download size={16} />}>Tải PDF</Button>
        </div>
      </div>

      <div className={styles.paper}>
        {/* Watermark overlay */}
        {!isFinalized && <div className={styles.watermark}>{report.watermark}</div>}

        <div className={styles.headerRow}>
          <div className={styles.hospitalInfo}>
            <h2>MyoLab-AI Medical Center</h2>
            <p>123 Medical Boulevard, City</p>
          </div>
          <div className={styles.reportMeta}>
            <p><strong>Bệnh nhân:</strong> {session?.subjectRef}</p>
            <p><strong>Session ID:</strong> {sessionId}</p>
            <p><strong>Ngày tạo:</strong> {new Date(report.createdAt).toLocaleDateString('vi-VN')}</p>
            <Badge variant={isFinalized ? 'success' : 'warning'}>{report.state.toUpperCase()}</Badge>
          </div>
        </div>

        <hr className={styles.divider} />

        <div className={styles.section}>
          <h3 className={styles.sectionTitle}>1. Thông tin quy trình</h3>
          <table className={styles.table}>
            <tbody>
              <tr>
                <td><strong>Protocol:</strong> {session?.protocolId}</td>
                <td><strong>Phiên:</strong> {session?.sessionType}</td>
              </tr>
              <tr>
                <td><strong>Bên tổn thương:</strong> {session?.affectedSide}</td>
                <td><strong>Nhóm cơ:</strong> {session?.targetMuscles.join(', ')}</td>
              </tr>
            </tbody>
          </table>
        </div>

        <div className={styles.section}>
          <h3 className={styles.sectionTitle}>2. Kết luận Lâm sàng (Bác sĩ chuyên khoa)</h3>
          <div className={styles.clinicalConclusion}>
            {report.clinicianApprovedConclusion}
          </div>
          {clinicalReview?.structuredOverride && (
            <div className={styles.overrideDetail}>
              <strong>[Ngoại lệ kỹ thuật]:</strong> {clinicalReview.structuredOverride.code} - {clinicalReview.structuredOverride.detail}
            </div>
          )}
        </div>

        <div className={styles.section}>
          <h3 className={styles.sectionTitle}>3. Tóm tắt Kỹ thuật AI (Tham khảo)</h3>
          <Alert variant="info" title="Khuyến cáo (Disclaimer)">
            Kết quả kỹ thuật dưới đây sinh ra từ mô hình AI, không thay thế chẩn đoán y khoa.
          </Alert>
          <div className={styles.aiSummary}>
            {report.aiTechnicalSummary}
          </div>
        </div>

        <hr className={styles.divider} />

        <div className={styles.footerRow}>
          <div className={styles.signatures}>
            <div className={styles.sigBlock}>
              <p><strong>Kỹ thuật viên thực hiện</strong></p>
              <p className={styles.sigName}>{session?.operator}</p>
            </div>
            <div className={styles.sigBlock}>
              <p><strong>Bác sĩ chuyên khoa</strong></p>
              <p className={styles.sigName}>{clinicalReview ? 'Bác sĩ Đã duyệt' : 'Chưa ký'}</p>
              {clinicalReview?.signOffHash && <span className={styles.hashLine}><FileKey size={12}/> {clinicalReview.signOffHash.substring(0, 16)}</span>}
            </div>
          </div>
        </div>

        {isFinalized && (
          <div className={styles.provenanceFooter}>
            <ShieldCheck size={14} />
            Document Hash: {report.reportHash} | Finalized At: {report.finalizedAt ? new Date(report.finalizedAt).toLocaleString('vi-VN') : ''}
          </div>
        )}
      </div>
      </div>
    </RoleGuard>
  );
}
