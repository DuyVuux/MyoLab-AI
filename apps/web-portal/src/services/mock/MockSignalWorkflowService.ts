/**
 * MockSignalWorkflowService — Mapping, Preflight, and QC gate.
 */
import type { ChannelMapping, MappingValidation } from '@/schemas/mapping';
import { validateMapping } from '@/schemas/mapping';
import type { PreflightResult, PreflightCheck } from '@/schemas/preflight';
import { computePreflightOutcome } from '@/schemas/preflight';
import type { QCResult, QCChannelResult, QCAcknowledgement } from '@/schemas/quality';
import { computeOverallVerdict } from '@/schemas/quality';
import type { ScenarioId } from './fixtures';
import { createMappingFixture, createPreflightChecks, createQCChannelResults } from './fixtures';
import * as repo from './MockWorkflowRepository';

// ── Mapping ──

export function initializeMappings(sessionId: string, channels: number, scenario: ScenarioId): ChannelMapping[] {
  const mappings = createMappingFixture(scenario, channels);
  repo.saveMappings(sessionId, mappings);
  return mappings;
}

export function getMappings(sessionId: string): ChannelMapping[] | null {
  return repo.getMappings(sessionId);
}

export function updateMapping(sessionId: string, channelIndex: number, updates: Partial<ChannelMapping>): ChannelMapping[] | null {
  const mappings = repo.getMappings(sessionId);
  if (!mappings) return null;

  const idx = mappings.findIndex((m) => m.sourceChannelIndex === channelIndex);
  if (idx === -1) return mappings;

  mappings[idx] = { ...mappings[idx], ...updates, autoMapped: false };
  repo.saveMappings(sessionId, mappings);
  return mappings;
}

export function confirmAllMappings(sessionId: string): ChannelMapping[] | null {
  const mappings = repo.getMappings(sessionId);
  if (!mappings) return null;

  for (const m of mappings) {
    m.confirmed = true;
  }
  repo.saveMappings(sessionId, mappings);
  repo.updateSessionState(sessionId, 'mapping_complete');
  return mappings;
}

export function validateMappings(sessionId: string): MappingValidation | null {
  const mappings = repo.getMappings(sessionId);
  if (!mappings) return null;
  return validateMapping(mappings);
}

// ── Preflight ──

export function runPreflight(sessionId: string, importId: string, scenario: ScenarioId): PreflightResult {
  const checks = createPreflightChecks(scenario);
  const imp = repo.getImport(importId);
  const outcome = computePreflightOutcome(checks);

  const result: PreflightResult = {
    sessionId,
    importId,
    outcome,
    checks,
    channelPreviews: [
      { channelId: 'CH1', channelLabel: 'CH1', muscle: 'Flexor carpi radialis', side: 'Left', samplingRateHz: 2000, durationSeconds: 60, sampleCount: 120000, minAmplitude: -2.1, maxAmplitude: 2.3, meanAmplitude: 0.02 },
      { channelId: 'CH2', channelLabel: 'CH2', muscle: 'Extensor carpi radialis', side: 'Left', samplingRateHz: 2000, durationSeconds: 60, sampleCount: 120000, minAmplitude: -1.8, maxAmplitude: 1.9, meanAmplitude: -0.01 },
      { channelId: 'CH3', channelLabel: 'CH3', muscle: 'Biceps brachii', side: 'Left', samplingRateHz: 2000, durationSeconds: 60, sampleCount: 120000, minAmplitude: -1.5, maxAmplitude: 1.6, meanAmplitude: 0.03 },
      { channelId: 'CH4', channelLabel: 'CH4', muscle: 'Upper trapezius', side: 'Left', samplingRateHz: 2000, durationSeconds: 60, sampleCount: 120000, minAmplitude: -0.9, maxAmplitude: 1.1, meanAmplitude: 0.01 },
    ],
    sourceHash: imp?.sha256 ?? 'N/A',
    overallSamplingRateHz: 2000,
    overallDurationSeconds: 60,
    overallChannelCount: imp?.channels ?? 4,
    timestamp: new Date().toISOString(),
  };

  repo.savePreflight(result);

  if (outcome === 'ready') {
    repo.updateSessionState(sessionId, 'preflight_pass');
  }

  return result;
}

export function getPreflight(sessionId: string): PreflightResult | null {
  return repo.getPreflight(sessionId);
}

// ── QC ──

export function runQC(sessionId: string, importId: string, scenario: ScenarioId): QCResult {
  const channelResults = createQCChannelResults(scenario);
  const overallVerdict = computeOverallVerdict(channelResults);

  const result: QCResult = {
    sessionId,
    importId,
    overallVerdict,
    channelResults,
    timestamp: new Date().toISOString(),
  };

  repo.saveQCResult(result);

  if (overallVerdict === 'pass') {
    repo.updateSessionState(sessionId, 'qc_pass');
  } else if (overallVerdict === 'fail') {
    repo.updateSessionState(sessionId, 'qc_fail');
  }

  return result;
}

export function acknowledgeQCWarning(sessionId: string, ack: QCAcknowledgement): QCResult | null {
  const result = repo.getQCResult(sessionId);
  if (!result || result.overallVerdict !== 'warning') return null;

  result.acknowledgement = ack;
  repo.saveQCResult(result);
  repo.updateSessionState(sessionId, 'qc_warning_acknowledged');
  repo.logAudit('qc.acknowledge', sessionId, `Reason: ${ack.reasonCode}`);
  return result;
}

export function getQCResult(sessionId: string): QCResult | null {
  return repo.getQCResult(sessionId);
}
