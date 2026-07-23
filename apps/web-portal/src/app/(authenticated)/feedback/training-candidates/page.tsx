/**
 * Training Candidates Page — `/feedback/training-candidates`
 */
'use client';

import { useRouter } from 'next/navigation';
import { Database, ShieldCheck, ArrowLeft, Filter } from 'lucide-react';
import { Card, CardContent, CardHeader } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { Alert } from '@/components/ui/Alert';

export default function TrainingCandidatesPage() {
  const router = useRouter();

  return (
    <div className="page-container">
      <div className="page-header">
        <div className="page-header__left">
          <h1 className="page-title">Hàng đợi Training Candidates</h1>
          <p className="page-subtitle">Danh sách dữ liệu dán nhãn đủ điều kiện đề xuất huấn luyện lại mô hình AI</p>
        </div>
        <div className="page-header__right">
          <Badge variant="success">PRIVACY & CONSENT VERIFIED</Badge>
        </div>
      </div>

      <Alert variant="info" title="Chính sách An toàn Huấn luyện">
        Dữ liệu trong danh sách này đã đi qua 2 tầng trọng tài (Clinical & ML QA), đạt sự đồng ý của bệnh nhân (Patient Consent), và được bảo toàn chuỗi băm nguồn (Source Hash Traceability).
      </Alert>

      <Card padding="md">
        <CardHeader>
          <h2>Danh sách mẫu thử đủ điều kiện</h2>
        </CardHeader>
        <CardContent>
          <div style={{ color: 'var(--color-text-muted)', fontSize: '0.875rem' }}>
            Hiện tại chưa có mẫu thử mới được đẩy vào tập huấn luyện. Tất cả các dữ liệu đều giữ nguyên trạng thái bất biến.
          </div>
        </CardContent>
      </Card>

      <div style={{ marginTop: '1.5rem' }}>
        <Button variant="secondary" onClick={() => router.push('/feedback/inbox')} icon={<ArrowLeft size={16} />}>
          Quay lại Hộp thư Phản hồi
        </Button>
      </div>
    </div>
  );
}
