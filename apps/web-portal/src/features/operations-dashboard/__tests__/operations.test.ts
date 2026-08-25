import { parseOperationsSummary } from "../../../contracts/automation/ui-i4-validators";

describe("UI-I4 operations contract", () => {
  test("canonical summary parses", () => {
    expect(parseOperationsSummary({
      generated_at: "2026-08-25T00:00:00Z",
      sessions_total: 10,
      imports_running: 1,
      qc_warning: 2,
      blocked: 1,
      awaiting_review: 2,
      completed: 6,
      unknown: 0,
      source: "CANONICAL_READ_MODEL",
      limitations: [],
    }).completed).toBe(6);
  });

  test("negative operational count fails closed", () => {
    expect(() => parseOperationsSummary({
      generated_at: "2026-08-25T00:00:00Z",
      sessions_total: 1,
      imports_running: -1,
      qc_warning: 0,
      blocked: 0,
      awaiting_review: 0,
      completed: 1,
      unknown: 0,
      source: "CANONICAL_READ_MODEL",
      limitations: [],
    })).toThrow();
  });
});
