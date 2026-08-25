import {
  deriveAutoDataUiState,
  mappingCanAutoAdvance,
  qualityBlocksDownstream,
  qualityNeedsHumanReview,
} from "../flow";

describe("UI-I2 auto-data flow", () => {
  test("import failure is fail-closed", () => {
    expect(deriveAutoDataUiState({
      importJob: { import_id: "I1", status: "FAILED" },
    })).toBe("FAILED");
  });

  test("preflight FAIL blocks automation", () => {
    expect(deriveAutoDataUiState({
      importJob: { import_id: "I1", session_id: "S1", status: "READY_FOR_QC" },
      preflight: {
        session_id: "S1",
        overall_status: "FAIL",
        can_proceed: false,
        checks: [],
      },
    })).toBe("BLOCKED");
  });

  test("unresolved mappings interrupt happy path", () => {
    expect(deriveAutoDataUiState({
      importJob: { import_id: "I1", session_id: "S1", status: "READY_FOR_QC" },
      preflight: {
        session_id: "S1",
        overall_status: "PASS",
        can_proceed: true,
        checks: [],
      },
      mapping: {
        session_id: "S1",
        resolved_count: 13,
        unresolved_count: 1,
        candidates: [],
      },
    })).toBe("MAPPING_REVIEW");
  });

  test("quality semantics preserve FAIL/WARNING/UNKNOWN behavior", () => {
    expect(qualityBlocksDownstream({
      session_id: "S1", overall_status: "FAIL", findings: [],
    })).toBe(true);
    expect(qualityNeedsHumanReview({
      session_id: "S1", overall_status: "WARNING", findings: [],
    })).toBe(true);
    expect(qualityNeedsHumanReview({
      session_id: "S1", overall_status: "UNKNOWN", findings: [],
    })).toBe(true);
  });

  test("mapping only auto-advances when no unresolved candidate remains", () => {
    expect(mappingCanAutoAdvance({
      session_id: "S1", resolved_count: 14, unresolved_count: 0, candidates: [],
    })).toBe(true);
  });
});
