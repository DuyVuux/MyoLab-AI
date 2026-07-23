/**
 * Preflight domain types.
 * Per spec Section 6.9.
 */

export type PreflightOutcome = 'ready' | 'mapping_required' | 'import_blocked';

export type PreflightCheckId =
  | 'sampling_rate'
  | 'duration'
  | 'channel_count'
  | 'timestamp_validity'
  | 'nan_inf'
  | 'flatline'
  | 'clipping_suspicion'
  | 'powerline_noise'
  | 'motion_artifact'
  | 'source_hash';

export type PreflightCheckStatus = 'pass' | 'warning' | 'fail';

export interface PreflightCheck {
  id: PreflightCheckId;
  label: string;
  status: PreflightCheckStatus;
  value: string;
  expected: string;
  detail?: string;
}

export interface PreflightChannelPreview {
  channelId: string;
  channelLabel: string;
  muscle: string;
  side: string;
  samplingRateHz: number;
  durationSeconds: number;
  sampleCount: number;
  minAmplitude: number;
  maxAmplitude: number;
  meanAmplitude: number;
}

export interface PreflightResult {
  sessionId: string;
  importId: string;
  outcome: PreflightOutcome;
  checks: PreflightCheck[];
  channelPreviews: PreflightChannelPreview[];
  sourceHash: string;
  overallSamplingRateHz: number;
  overallDurationSeconds: number;
  overallChannelCount: number;
  timestamp: string;
}

export function computePreflightOutcome(checks: PreflightCheck[]): PreflightOutcome {
  if (checks.some((c) => c.id === 'channel_count' && c.status === 'fail')) return 'mapping_required';
  if (checks.some((c) => c.status === 'fail')) return 'import_blocked';
  return 'ready';
}
