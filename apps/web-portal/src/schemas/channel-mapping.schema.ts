export type SignalUnit = "uV" | "mV" | "V";
export type ChannelRole = "flexor" | "extensor" | "compensation" | "reference" | "other";
export type MappingSide = "left" | "right" | "bilateral" | "not_applicable";

export interface ChannelMapping {
  readonly sourceChannel: string;
  readonly canonicalChannelId: string;
  readonly muscle: string;
  readonly side: MappingSide;
  readonly unit: SignalUnit;
  readonly functionalRole: ChannelRole;
  readonly electrodePosition?: string;
}

export interface MappingValidationResult {
  readonly completeness: number;
  readonly reasonCodes: readonly string[];
  readonly valid: boolean;
}

export const validateChannelMappings = (
  mappings: readonly ChannelMapping[],
  expectedSourceChannels: readonly string[],
): MappingValidationResult => {
  const reasons: string[] = [];
  const sourceIds = new Set<string>();
  const canonicalIds = new Set<string>();
  let completeCount = 0;

  for (const mapping of mappings) {
    if (sourceIds.has(mapping.sourceChannel)) reasons.push("DUPLICATE_SOURCE_CHANNEL");
    if (canonicalIds.has(mapping.canonicalChannelId)) reasons.push("DUPLICATE_CANONICAL_CHANNEL");
    sourceIds.add(mapping.sourceChannel);
    canonicalIds.add(mapping.canonicalChannelId);
    if (
      mapping.sourceChannel &&
      mapping.canonicalChannelId &&
      mapping.muscle &&
      mapping.side &&
      mapping.unit &&
      mapping.functionalRole
    ) completeCount += 1;
  }

  for (const channel of expectedSourceChannels) {
    if (!sourceIds.has(channel)) reasons.push(`UNMAPPED:${channel}`);
  }
  const denominator = expectedSourceChannels.length || 1;
  const completeness = completeCount / denominator;
  if (completeness < 1) reasons.push("MAPPING_INCOMPLETE");
  return { completeness, reasonCodes: [...new Set(reasons)], valid: reasons.length === 0 };
};
