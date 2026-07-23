'use client';

import { useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';

export default function UC1CalibrationPage() {
  const params = useParams();
  const router = useRouter();
  const sessionId = params.sessionId as string;

  useEffect(() => {
    // Alias route to canonical session calibration wizard
    router.replace(`/sessions/${sessionId}/calibration`);
  }, [sessionId, router]);

  return (
    <div className="page-container" style={{ padding: '3rem', textAlign: 'center' }}>
      <p style={{ color: 'var(--color-text-secondary)' }}>Đang chuyển hướng sang luồng Hiệu chuẩn (Calibration Wizard)...</p>
    </div>
  );
}
