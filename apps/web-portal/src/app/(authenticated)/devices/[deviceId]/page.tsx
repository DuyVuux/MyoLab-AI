/**
 * Device Detail Page — `/devices/[deviceId]`
 */
'use client';

import { useParams, useRouter } from 'next/navigation';
import { Cpu, ArrowLeft, CheckCircle, ShieldCheck } from 'lucide-react';
import { Card, CardContent, CardHeader } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';

export default function DeviceDetailPage() {
  const params = useParams();
  const router = useRouter();
  const deviceId = params.deviceId as string;

  return (
    <div className="page-container">
      <div className="page-header">
        <div className="page-header__left">
          <h1 className="page-title">Chi tiết Thiết bị ({deviceId})</h1>
          <p className="page-subtitle">Thông số kỹ thuật và chứng nhận hiệu chuẩn phần cứng</p>
        </div>
        <div className="page-header__right">
          <Badge variant="success">CALIBRATED & READY</Badge>
        </div>
      </div>

      <Card padding="md">
        <CardHeader>
          <h2>Thông số phần cứng</h2>
        </CardHeader>
        <CardContent>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
            <div>
              <strong>Mã thiết bị:</strong> {deviceId}
            </div>
            <div>
              <strong>Model:</strong> MyoSensor PRO-X8
            </div>
            <div>
              <strong>Số kênh sEMG:</strong> 8 Kênh đối xứng
            </div>
            <div>
              <strong>Tần số lấy mẫu tối đa:</strong> 4000 Hz
            </div>
            <div>
              <strong>Độ phân giải ADC:</strong> 24-bit
            </div>
            <div>
              <strong>Kết nối:</strong> USB-C / BLE 5.2 Medical Grade
            </div>
          </div>
        </CardContent>
      </Card>

      <div style={{ marginTop: '1.5rem' }}>
        <Button variant="secondary" onClick={() => router.back()} icon={<ArrowLeft size={16} />}>
          Quay lại danh sách thiết bị
        </Button>
      </div>
    </div>
  );
}
