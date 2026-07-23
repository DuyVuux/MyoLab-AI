/**
 * Mapping domain types.
 * Per spec Section 6.8.
 */
import type { Side, CanonicalMuscle, SignalUnit, FunctionalRole, ElectrodePosition } from './common';

export interface ChannelMapping {
  sourceChannelIndex: number;
  sourceChannelLabel: string;
  canonicalChannelId: string;
  muscle: CanonicalMuscle | '';
  side: Side | '';
  unit: SignalUnit;
  functionalRole: FunctionalRole;
  electrodePosition: ElectrodePosition | '';
  autoMapped: boolean;
  confirmed: boolean;
}

export type MappingState =
  | 'pending'
  | 'auto_mapped'
  | 'partially_confirmed'
  | 'all_confirmed'
  | 'blocked'; // unknown unit or missing muscle/side

export interface MappingValidation {
  state: MappingState;
  valid: boolean;
  blockers: MappingBlocker[];
  warnings: string[];
}

export interface MappingBlocker {
  channelIndex: number;
  channelLabel: string;
  reason: 'unknown_unit' | 'missing_muscle' | 'missing_side' | 'missing_electrode_position';
  message: string;
}

export function validateMapping(mappings: ChannelMapping[]): MappingValidation {
  const blockers: MappingBlocker[] = [];
  const warnings: string[] = [];

  for (const m of mappings) {
    if (m.unit === 'unknown') {
      blockers.push({
        channelIndex: m.sourceChannelIndex,
        channelLabel: m.sourceChannelLabel,
        reason: 'unknown_unit',
        message: `Kênh ${m.sourceChannelLabel}: Đơn vị chưa xác định. Không tự đoán từ biên độ.`,
      });
    }
    if (!m.muscle) {
      blockers.push({
        channelIndex: m.sourceChannelIndex,
        channelLabel: m.sourceChannelLabel,
        reason: 'missing_muscle',
        message: `Kênh ${m.sourceChannelLabel}: Chưa gán cơ mục tiêu.`,
      });
    }
    if (!m.side) {
      blockers.push({
        channelIndex: m.sourceChannelIndex,
        channelLabel: m.sourceChannelLabel,
        reason: 'missing_side',
        message: `Kênh ${m.sourceChannelLabel}: Chưa chọn bên (Left/Right/Bilateral).`,
      });
    }
  }

  const allConfirmed = mappings.every((m) => m.confirmed);
  const someConfirmed = mappings.some((m) => m.confirmed);

  let state: MappingState;
  if (blockers.length > 0) state = 'blocked';
  else if (allConfirmed) state = 'all_confirmed';
  else if (someConfirmed) state = 'partially_confirmed';
  else state = 'pending';

  return {
    state,
    valid: blockers.length === 0 && allConfirmed,
    blockers,
    warnings,
  };
}
