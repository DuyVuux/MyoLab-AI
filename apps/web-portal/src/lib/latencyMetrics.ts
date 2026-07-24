import type { LatencyBreakdown } from "../schemas/gesture-inference.schema";

function assertFiniteNonNegative(value: number, label: string): void {
  if (!Number.isFinite(value) || value < 0) {
    throw new RangeError(`${label}_MUST_BE_FINITE_AND_NON_NEGATIVE`);
  }
}

export function nearestRankPercentile(
  values: readonly number[],
  percentile: number,
): number {
  if (values.length === 0) {
    throw new RangeError("PERCENTILE_VALUES_MUST_NOT_BE_EMPTY");
  }
  if (!Number.isFinite(percentile) || percentile <= 0 || percentile > 1) {
    throw new RangeError("PERCENTILE_MUST_BE_IN_OPEN_CLOSED_UNIT_INTERVAL");
  }

  const sorted = values.map((value) => {
    assertFiniteNonNegative(value, "LATENCY");
    return value;
  });
  sorted.sort((left, right) => left - right);

  const nearestRankIndex = Math.ceil(percentile * sorted.length) - 1;
  return sorted[nearestRankIndex];
}

export function totalLatencyMs(
  acquisitionMs: number,
  windowMs: number,
  preprocessMs: number,
  inferenceMs: number,
  transportRenderMs: number,
): number {
  const components = [
    acquisitionMs,
    windowMs,
    preprocessMs,
    inferenceMs,
    transportRenderMs,
  ] as const;
  components.forEach((value) => assertFiniteNonNegative(value, "LATENCY"));
  return components.reduce((total, value) => total + value, 0);
}

export function isLatencyBreakdownValid(
  latency: LatencyBreakdown,
  toleranceMs = 1e-9,
): boolean {
  if (!Number.isFinite(toleranceMs) || toleranceMs < 0) {
    return false;
  }

  try {
    assertFiniteNonNegative(latency.totalMs, "LATENCY_TOTAL");
    const computed = totalLatencyMs(
      latency.acquisitionMs,
      latency.windowMs,
      latency.preprocessMs,
      latency.inferenceMs,
      latency.transportRenderMs,
    );
    return Math.abs(latency.totalMs - computed) <= toleranceMs;
  } catch {
    return false;
  }
}
