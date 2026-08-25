import { AutomationProblemError, contractProblem } from "./problem";
import type { OperationsSummary } from "./operations";

function fail(message: string): never {
  throw new AutomationProblemError(contractProblem(message));
}

export function parseOperationsSummary(value: unknown): OperationsSummary {
  if (!value || typeof value !== "object" || Array.isArray(value)) {
    fail("operations summary must be an object");
  }
  const o = value as Record<string, unknown>;
  const counts = [
    "sessions_total", "imports_running", "qc_warning",
    "blocked", "awaiting_review", "completed", "unknown",
  ] as const;

  for (const key of counts) {
    const v = o[key];
    if (typeof v !== "number" || !Number.isInteger(v) || v < 0) {
      fail(`${key} must be a non-negative integer`);
    }
  }
  if (typeof o.generated_at !== "string") fail("generated_at is required");
  if (o.source !== "CANONICAL_READ_MODEL") fail("operations source must be CANONICAL_READ_MODEL");
  if (!Array.isArray(o.limitations) || !o.limitations.every((x) => typeof x === "string")) {
    fail("limitations must be string[]");
  }

  const accounted =
    Number(o.completed) + Number(o.blocked) + Number(o.awaiting_review) +
    Number(o.imports_running) + Number(o.unknown);

  if (accounted > Number(o.sessions_total) + Number(o.imports_running)) {
    fail("operational counts are internally inconsistent");
  }

  return o as unknown as OperationsSummary;
}
