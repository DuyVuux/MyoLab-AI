/**
 * MyoLab-AI Feature Flags
 * Controls prototype feature visibility per Section 0.3
 * 
 * ASSUMPTION: All live/hardware integrations are disabled by default.
 * Only mock/replay/offline features are enabled.
 */

export interface FeatureFlags {
  /** P1: Live device stream mock (simulated connection) */
  liveStreamMock: boolean;
  /** P1: C3D/MAT/vendor adapter mock */
  vendorAdapterMock: boolean;
  /** P0: Noraxon export mock (file import simulation) */
  noraxonExportMock: boolean;
  /** P0: Synthetic demo data */
  syntheticDemo: boolean;
  /** P0: Generic CSV import */
  genericCsvImport: boolean;
  /** P0: De-identified offline replay */
  offlineReplay: boolean;
  /** P1: UC2 batch import */
  uc2BatchImport: boolean;
  /** P1: Longitudinal compatibility gate */
  longitudinalGate: boolean;
  /** Show UC3/UC4 feasibility screens */
  showFeasibilityScreens: boolean;
}

export const DEFAULT_FEATURE_FLAGS: FeatureFlags = {
  // P0 — enabled
  syntheticDemo: true,
  genericCsvImport: true,
  noraxonExportMock: true,
  offlineReplay: true,
  showFeasibilityScreens: true,

  // P1 — disabled by default
  liveStreamMock: false,
  vendorAdapterMock: false,
  uc2BatchImport: false,
  longitudinalGate: false,
};

// ASSUMPTION: Feature flags are static in prototype. 
// In production, these would come from a config service.
let currentFlags: FeatureFlags = { ...DEFAULT_FEATURE_FLAGS };

export function getFeatureFlags(): FeatureFlags {
  return { ...currentFlags };
}

export function isFeatureEnabled(flag: keyof FeatureFlags): boolean {
  return currentFlags[flag];
}

export function setFeatureFlag(flag: keyof FeatureFlags, value: boolean): void {
  currentFlags = { ...currentFlags, [flag]: value };
}
