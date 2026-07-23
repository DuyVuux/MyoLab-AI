/**
 * Signal Acquisition Page — `/sessions/[sessionId]/acquisition`
 * Real-time or simulated live stream signal acquisition interface.
 */
'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { Activity, ShieldAlert, Play, Square, CheckCircle, ArrowRight } from 'lucide-react';
import { Card, CardContent, CardHeader } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { Alert } from '@/components/ui/Alert';
import * as SessionService from '@/services/mock/MockSessionService';
import { SignalPreviewChart } from '@/components/charts/SignalPreviewChart';

export default function SignalAcquisitionPage() {
  const params = useParams();
  const router = useRouter();
  const sessionId = params.sessionId as string;

  const [isStreaming, setIsStreaming] = useState(false);
  const [samplesAcquired, setSamplesAcquired] = useState(0);

  useEffect(() => {
    let interval: NodeJS.Timeout;
    if (isStreaming) {
      interval = setInterval(() => {
        setSamplesAcquired((prev) => prev + 1000);
      }, 500);
    }
    return () => clearInterval(interval);
  }, [isStreaming]);

  return (
    <div className="page-container">
      <div className="page-header">
        <div className="page-header__left">
          <h1 className="page-title">Signal Acquisition</h1>
          <p className="page-subtitle">Thu nhận và hiển thị tín hiệu sEMG trực tiếp (Live Stream Mock)</p>
        </div>
        <div className="page-header__right">
          <Badge variant={isStreaming ? 'success' : 'neutral'}>
            {isStreaming ? 'STREAMING ACTIVE' : 'STOPPED'}
          </Badge>
        </div>
      </div>

      <Alert variant="info" title="Live Stream Mode">
        Chế độ thu nhận trực tiếp phục vụ mô phỏng kiểm thử. Tín hiệu được kiểm soát qua mock buffer stream.
      </Alert>

      <Card padding="md">
        <CardHeader>
          <h2>Tín hiệu sEMG thời gian thực</h2>
        </CardHeader>
        <CardContent>
          <SignalPreviewChart samplingRate={2000} durationSeconds={10} activeChannels={4} />
          <div style={{ marginTop: '1rem', display: 'flex', gap: '1rem', alignItems: 'center' }}>
            {!isStreaming ? (
              <Button onClick={() => setIsStreaming(true)} icon={<Play size={16} />}>
                Bắt đầu Stream
              </Button>
            ) : (
              <Button variant="danger" onClick={() => setIsStreaming(false)} icon={<Square size={16} />}>
                Dừng Stream
              </Button>
            )}
            <span style={{ fontSize: '0.875rem', color: 'var(--color-text-muted)' }}>
              Mẫu đã thu nhận: {samplesAcquired.toLocaleString()} samples
            </span>
          </div>
        </CardContent>
      </Card>

      <div style={{ marginTop: '1.5rem', display: 'flex', justifyContent: 'flex-end' }}>
        <Button onClick={() => router.push(`/sessions/${sessionId}/preflight`)} icon={<ArrowRight size={16} />}>
          Chuyển sang Preflight
        </Button>
      </div>
    </div>
  );
}
