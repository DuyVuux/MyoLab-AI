export type PreflightState = "ready" | "mapping_required" | "import_blocked";

export interface PreviewPoint {
  readonly timeS: number;
  readonly valueUv: number;
}

export interface PreflightSummary {
  readonly schemaVersion: "preflight-summary.v0.1";
  readonly preflightId: string;
  readonly sessionId: string;
  readonly importId: string;
  readonly state: PreflightState;
  readonly samplingRateHz: number | null;
  readonly durationS: number | null;
  readonly channelCount: number | null;
  readonly mappingCompleteness: number;
  readonly timestampMonotonic: boolean;
  readonly nonFiniteRatio: number;
  readonly flatlineSuspected: boolean;
  readonly clippingSuspected: boolean;
  readonly powerlineWarning: boolean;
  readonly motionArtifactWarning: boolean;
  readonly sourceHashSha256: string;
  readonly preview: readonly PreviewPoint[];
  readonly reasonCodes: readonly string[];
  readonly rawSamplesIncluded: false;
}

export const derivePreflightState = (input: {
  readonly samplingRateHz?: number;
  readonly durationS?: number;
  readonly channelCount?: number;
  readonly timestampMonotonic?: boolean;
  readonly mappingCompleteness: number;
}): PreflightState => {
  if (!input.samplingRateHz || !input.durationS || !input.channelCount || input.timestampMonotonic !== true) {
    return "import_blocked";
  }
  return input.mappingCompleteness < 1 ? "mapping_required" : "ready";
};

export const downsamplePreview = (
  samples: readonly number[],
  samplingRateHz: number,
  maxPoints: number,
): readonly PreviewPoint[] => {
  if (samplingRateHz <= 0 || maxPoints <= 0) throw new Error("INVALID_PREVIEW_CONFIG");
  const stride = Math.max(1, Math.ceil(samples.length / maxPoints));
  const output: PreviewPoint[] = [];
  for (let index = 0; index < samples.length; index += stride) {
    output.push({ timeS: index / samplingRateHz, valueUv: samples[index] ?? 0 });
  }
  return output;
};
