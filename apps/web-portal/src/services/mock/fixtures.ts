/**
 * Deterministic test fixtures for 8 scenarios.
 * Each fixture provides pre-configured data for the entire pipeline.
 */
import type { SessionContext } from '@/schemas/session';
import type { ImportRecord, ImportState } from '@/schemas/import';
import type { ChannelMapping } from '@/schemas/mapping';
import type { PreflightCheck } from '@/schemas/preflight';
import type { QCChannelResult, QCCheck } from '@/schemas/quality';
import type { RepetitionResult, SetupCheckResult, BaselineResult } from '@/schemas/calibration';
import type { Side, CanonicalMuscle, SignalUnit } from '@/schemas/common';

// ── Scenario Identifiers ──
export type ScenarioId =
  | 'happy_path'
  | 'mapping_required'
  | 'duplicate_detected'
  | 'import_rejected'
  | 'qc_warning'
  | 'qc_fail'
  | 'calibration_warning'
  | 'timeout_retry';

// ── Session Fixtures ──
export function createSessionFixture(scenario: ScenarioId, sessionId: string): SessionContext {
  const base: SessionContext = {
    sessionId,
    subjectRef: 'SUBJ-DEMO-001',
    useCaseId: 'uc1',
    protocolId: 'PROT-UC1-001',
    protocolVersion: '1.2',
    affectedSide: 'Left' as Side,
    referenceSide: 'Right' as Side,
    targetMuscles: ['Flexor carpi radialis', 'Extensor carpi radialis', 'Biceps brachii', 'Upper trapezius'],
    sessionType: 'baseline',
    operator: 'KTV Trần Thị B',
    consentScope: ['quality_improvement'],
    dataSourceIntent: '',
    createdAt: new Date().toISOString(),
    electrodeLayout: [],
    requiresCalibration: true,
    state: 'draft',
  };

  switch (scenario) {
    case 'happy_path':
      return { ...base, subjectRef: 'SUBJ-HP-001' };
    case 'mapping_required':
      return { ...base, subjectRef: 'SUBJ-MAP-001' };
    case 'qc_warning':
      return { ...base, subjectRef: 'SUBJ-QCW-001', useCaseId: 'uc2', protocolId: 'PROT-UC2-001', protocolVersion: '2.0' };
    case 'qc_fail':
      return { ...base, subjectRef: 'SUBJ-QCF-001' };
    case 'calibration_warning':
      return { ...base, subjectRef: 'SUBJ-CAL-001' };
    default:
      return base;
  }
}

// ── Import Fixtures ──
export function createImportFixture(scenario: ScenarioId, sessionId: string, importId: string): ImportRecord {
  const base: ImportRecord = {
    importId,
    sessionId,
    filename: 'noraxon_export_uc1_001.csv',
    fileSizeBytes: 245760,
    mimeType: 'text/csv',
    sourceType: 'noraxon_mock',
    channels: 4,
    samples: 12000,
    samplingRateHz: 2000,
    durationSeconds: 60,
    state: 'file_selected' as ImportState,
    progress: 0,
    sha256: 'a3f8c2d1e4b5a6f7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1',
    stateHistory: [],
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  };

  switch (scenario) {
    case 'duplicate_detected':
      return { ...base, sha256: 'DUPLICATE_HASH_a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8' };
    case 'import_rejected':
      return { ...base, filename: 'invalid_data.xlsx', mimeType: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' };
    case 'mapping_required':
      return { ...base, filename: 'generic_emg_data.csv', channels: 6 };
    case 'timeout_retry':
      return { ...base, filename: 'large_recording_10min.csv', fileSizeBytes: 4194304, samples: 120000, durationSeconds: 600 };
    default:
      return base;
  }
}

// ── Channel Mapping Fixtures ──
export function createMappingFixture(scenario: ScenarioId, channels: number): ChannelMapping[] {
  const defaultMappings: ChannelMapping[] = [
    { sourceChannelIndex: 0, sourceChannelLabel: 'CH1', canonicalChannelId: 'C001', muscle: 'Flexor carpi radialis', side: 'Left', unit: 'mV', functionalRole: 'agonist', electrodePosition: 'belly', autoMapped: true, confirmed: false },
    { sourceChannelIndex: 1, sourceChannelLabel: 'CH2', canonicalChannelId: 'C002', muscle: 'Extensor carpi radialis', side: 'Left', unit: 'mV', functionalRole: 'antagonist', electrodePosition: 'belly', autoMapped: true, confirmed: false },
    { sourceChannelIndex: 2, sourceChannelLabel: 'CH3', canonicalChannelId: 'C003', muscle: 'Biceps brachii', side: 'Left', unit: 'mV', functionalRole: 'synergist', electrodePosition: 'belly', autoMapped: true, confirmed: false },
    { sourceChannelIndex: 3, sourceChannelLabel: 'CH4', canonicalChannelId: 'C004', muscle: 'Upper trapezius', side: 'Left', unit: 'mV', functionalRole: 'stabilizer', electrodePosition: 'belly', autoMapped: true, confirmed: false },
  ];

  if (scenario === 'mapping_required') {
    return Array.from({ length: channels }, (_, i) => ({
      sourceChannelIndex: i,
      sourceChannelLabel: `Col_${i + 1}`,
      canonicalChannelId: `C${String(i + 1).padStart(3, '0')}`,
      muscle: (i < 4 ? defaultMappings[i].muscle : '') as CanonicalMuscle | '',
      side: (i < 4 ? 'Left' : '') as Side | '',
      unit: (i < 4 ? 'mV' : 'unknown') as SignalUnit,
      functionalRole: i < 4 ? defaultMappings[i].functionalRole : 'unknown' as const,
      electrodePosition: i < 4 ? 'belly' as const : '' as const,
      autoMapped: i < 4,
      confirmed: false,
    }));
  }

  return defaultMappings.slice(0, channels);
}

// ── Preflight Check Fixtures ──
export function createPreflightChecks(scenario: ScenarioId): PreflightCheck[] {
  const checks: PreflightCheck[] = [
    { id: 'sampling_rate', label: 'Tần số lấy mẫu', status: 'pass', value: '2000 Hz', expected: '≥ 1000 Hz' },
    { id: 'duration', label: 'Thời lượng', status: 'pass', value: '60s', expected: '≥ 10s' },
    { id: 'channel_count', label: 'Số kênh', status: 'pass', value: '4', expected: '≥ 2' },
    { id: 'timestamp_validity', label: 'Timestamp hợp lệ', status: 'pass', value: 'Monotonic', expected: 'Monotonic increasing' },
    { id: 'nan_inf', label: 'NaN/Inf', status: 'pass', value: '0 found', expected: '0' },
    { id: 'flatline', label: 'Flatline', status: 'pass', value: '0 segments', expected: '0' },
    { id: 'clipping_suspicion', label: 'Clipping suspicion', status: 'pass', value: '0.0%', expected: '< 2%' },
    { id: 'powerline_noise', label: 'Powerline noise (50/60Hz)', status: 'pass', value: '-45 dB', expected: '< -30 dB' },
    { id: 'motion_artifact', label: 'Motion artifact', status: 'pass', value: '0 events', expected: '< 5 events' },
    { id: 'source_hash', label: 'Source hash', status: 'pass', value: 'SHA-256 verified', expected: 'Match' },
  ];

  if (scenario === 'mapping_required') {
    checks[2] = { ...checks[2], status: 'fail', value: '6', expected: '4 (per protocol)', detail: 'Số kênh không khớp protocol. Cần mapping lại.' };
  }

  return checks;
}

// ── QC Channel Result Fixtures ──
export function createQCChannelResults(scenario: ScenarioId): QCChannelResult[] {
  const makeChecks = (snr: number, baseline: number, sat: number): QCCheck[] => [
    { id: 'snr', label: 'SNR', value: snr, unit: 'dB', threshold: 10, thresholdDirection: 'gte', status: snr >= 10 ? 'pass' : snr >= 7 ? 'warning' : 'fail' },
    { id: 'baseline_noise', label: 'Baseline noise', value: baseline, unit: 'µV', threshold: 20, thresholdDirection: 'lte', status: baseline <= 20 ? 'pass' : baseline <= 35 ? 'warning' : 'fail' },
    { id: 'saturation', label: 'Saturation', value: sat, unit: '%', threshold: 2, thresholdDirection: 'lte', status: sat <= 2 ? 'pass' : sat <= 5 ? 'warning' : 'fail' },
    { id: 'artifact', label: 'Artifact score', value: 0.1, unit: '', threshold: 0.3, thresholdDirection: 'lte', status: 'pass' },
  ];

  const goodChannel = (label: string, muscle: string): QCChannelResult => ({
    channelId: label, channelLabel: label, muscle, side: 'Left',
    checks: makeChecks(18.5, 8.2, 0.3), verdict: 'pass',
  });

  if (scenario === 'qc_fail') {
    return [
      goodChannel('CH1', 'Flexor carpi radialis'),
      goodChannel('CH2', 'Extensor carpi radialis'),
      { channelId: 'CH3', channelLabel: 'CH3', muscle: 'Biceps brachii', side: 'Left', checks: makeChecks(5.2, 42, 1.1), verdict: 'fail' },
      { channelId: 'CH4', channelLabel: 'CH4', muscle: 'Upper trapezius', side: 'Left', checks: makeChecks(3.8, 55, 8.3), verdict: 'fail' },
    ];
  }

  if (scenario === 'qc_warning') {
    return [
      goodChannel('CH1', 'Flexor carpi radialis'),
      goodChannel('CH2', 'Extensor carpi radialis'),
      { channelId: 'CH3', channelLabel: 'CH3', muscle: 'Biceps brachii', side: 'Left', checks: makeChecks(8.5, 28, 1.5), verdict: 'warning' },
      goodChannel('CH4', 'Upper trapezius'),
    ];
  }

  return [
    goodChannel('CH1', 'Flexor carpi radialis'),
    goodChannel('CH2', 'Extensor carpi radialis'),
    goodChannel('CH3', 'Biceps brachii'),
    goodChannel('CH4', 'Upper trapezius'),
  ];
}

// ── Calibration Fixtures ──
export function createRepetitionFixtures(scenario: ScenarioId): RepetitionResult[] {
  const reps: RepetitionResult[] = [
    { repetitionId: 'REP-001', index: 0, gesture: 'Nắm tay (Fist)', quality: 'pass', peakAmplitude: 850, duration: 3.2, accepted: true, needsRepeat: false },
    { repetitionId: 'REP-002', index: 1, gesture: 'Mở tay (Open)', quality: 'pass', peakAmplitude: 620, duration: 2.8, accepted: true, needsRepeat: false },
    { repetitionId: 'REP-003', index: 2, gesture: 'Gập cổ tay (Flexion)', quality: 'pass', peakAmplitude: 730, duration: 3.0, accepted: true, needsRepeat: false },
    { repetitionId: 'REP-004', index: 3, gesture: 'Duỗi ngón (Extension)', quality: 'pass', peakAmplitude: 580, duration: 2.5, accepted: true, needsRepeat: false },
    { repetitionId: 'REP-005', index: 4, gesture: 'Nắm tay (Fist)', quality: 'pass', peakAmplitude: 840, duration: 3.1, accepted: true, needsRepeat: false },
  ];

  if (scenario === 'calibration_warning') {
    reps[2] = { ...reps[2], quality: 'warning', peakAmplitude: 280, needsRepeat: true, accepted: false, reason: 'Biên độ thấp bất thường' };
    reps[4] = { ...reps[4], quality: 'warning', peakAmplitude: 310, needsRepeat: true, accepted: false, reason: 'Tín hiệu không ổn định' };
  }

  return reps;
}

export function createSetupCheckFixture(scenario: ScenarioId): SetupCheckResult {
  return {
    impedanceOk: scenario !== 'calibration_warning',
    channelsDetected: 4,
    channelsExpected: 4,
    skinContact: scenario === 'calibration_warning' ? 'fair' : 'good',
    detail: scenario === 'calibration_warning' ? 'Impedance cao ở CH3 — kiểm tra lại contact gel.' : 'Tất cả kênh hoạt động bình thường.',
  };
}

export function createBaselineFixture(scenario: ScenarioId): BaselineResult {
  return {
    baselineNoiseRms: scenario === 'calibration_warning' ? 18.5 : 6.2,
    baselineDuration: 5.0,
    acceptable: true,
    detail: 'Baseline thu thập thành công.',
  };
}

// ── Pre-seeded duplicate for duplicate_detected scenario ──
export const EXISTING_DUPLICATE_IMPORT: ImportRecord = {
  importId: 'IMP-EXISTING-DUP',
  sessionId: 'S-OLD-001',
  filename: 'noraxon_export_uc1_001.csv',
  fileSizeBytes: 245760,
  mimeType: 'text/csv',
  sourceType: 'noraxon_mock',
  channels: 4,
  samples: 12000,
  samplingRateHz: 2000,
  durationSeconds: 60,
  state: 'qc_ready',
  progress: 100,
  sha256: 'DUPLICATE_HASH_a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8',
  stateHistory: [],
  createdAt: '2026-07-22T10:00:00Z',
  updatedAt: '2026-07-22T10:05:00Z',
};
