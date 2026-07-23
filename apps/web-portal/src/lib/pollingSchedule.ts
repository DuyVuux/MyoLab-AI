export function pollingDelayMs(attempt: number): number {
  if (!Number.isInteger(attempt) || attempt < 0) {
    throw new Error("POLLING_ATTEMPT_INVALID");
  }
  if (attempt < 10) return 1_000;
  if (attempt < 25) return 2_000;
  return 5_000;
}
