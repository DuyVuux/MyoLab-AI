/**
 * Protocol Detail Page — `/protocols/[protocolId]`
 */
'use client';

import { useParams, useRouter } from 'next/navigation';
import { FileText, ArrowLeft, CheckCircle } from 'lucide-react';
import { Card, CardContent, CardHeader } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';

export default function ProtocolDetailPage() {
  const params = useParams();
  const router = useRouter();
  const protocolId = params.protocolId as string;

  return (
    <div className="page-container">
      <div className="page-header">
        <div className="page-header__left">
          <h1 className="page-title">Chi tiết Giao thức ({protocolId})</h1>
          <p className="page-subtitle">Quy trình đo lâm sàng và vị trí dán điện cực chuẩn hóa</p>
        </div>
        <div className="page-header__right">
          <Badge variant="info">APPROVED SPEC v2.0</Badge>
        </div>
      </div>

      <Card padding="md">
        <CardHeader>
          <h2>Cấu hình giao thức</h2>
        </CardHeader>
        <CardContent>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '1rem' }}>
            <div>
              <strong>Mã Giao thức:</strong> {protocolId}
            </div>
            <div>
              <strong>Tên Giao thức:</strong> Isometric Fatigue Assessment (Biceps/Triceps)
            </div>
            <div>
              <strong>Yêu cầu Hiệu chuẩn MVC:</strong> Bắt buộc (Mandatory)
            </div>
            <div>
              <strong>Thời gian co cơ mục tiêu:</strong> 60 Giây Isometric Contraction
            </div>
            <div>
              <strong>Tần số lấy mẫu tiêu chuẩn:</strong> 2000 Hz
            </div>
          </div>
        </CardContent>
      </Card>

      <div style={{ marginTop: '1.5rem' }}>
        <Button variant="secondary" onClick={() => router.back()} icon={<ArrowLeft size={16} />}>
          Quay lại danh sách giao thức
        </Button>
      </div>
    </div>
  );
}
