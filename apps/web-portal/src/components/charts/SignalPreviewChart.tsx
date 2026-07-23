'use client';

import React from 'react';

interface SignalPreviewChartProps {
  samplingRate?: number;
  durationSeconds?: number;
  activeChannels?: number;
  height?: number;
}

export function SignalPreviewChart({
  samplingRate = 2000,
  durationSeconds = 5,
  activeChannels = 4,
  height = 160,
}: SignalPreviewChartProps) {
  return (
    <div
      style={{
        width: '100%',
        height: `${height}px`,
        backgroundColor: 'var(--color-surface-subtle, #1e293b)',
        borderRadius: '8px',
        border: '1px solid var(--color-border-subtle, #334155)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        color: 'var(--color-text-secondary, #94a3b8)',
        fontSize: '0.875rem',
      }}
    >
      <svg viewBox="0 0 400 100" style={{ width: '100%', height: '100%' }}>
        <polyline
          fill="none"
          stroke="var(--color-primary, #06b6d4)"
          strokeWidth="2"
          points="0,50 20,40 40,60 60,30 80,70 100,20 120,80 140,45 160,55 180,35 200,65 220,50 240,40 260,60 280,30 300,70 320,20 340,80 360,45 380,55 400,50"
        />
      </svg>
    </div>
  );
}
