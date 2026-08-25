import {
  parseSessionMappingState,
  parseSessionPreflight,
  parsePipelineJob,
} from "../../../contracts/automation/validators";

describe("UI-I2 contracts", () => {
  test("preflight FAIL cannot claim can_proceed", () => {
    expect(() => parseSessionPreflight({
      session_id: "S1",
      overall_status: "FAIL",
      can_proceed: true,
      checks: [],
    })).toThrow();
  });

  test("mapping confidence is bounded", () => {
    expect(() => parseSessionMappingState({
      session_id: "S1",
      resolved_count: 0,
      unresolved_count: 1,
      candidates: [{
        vendor_signal_name: "EMG1",
        confidence: 1.2,
        decision: "REVIEW_REQUIRED",
      }],
    })).toThrow();
  });
  test("pipeline parser accepts live day21 analysis job shape", () => {
    const job = parsePipelineJob({
      analysisId: "AN21-live",
      sessionId: "S1",
      status: "queued",
      currentStage: null,
      reasonCodes: [],
      warningCodes: [],
      updatedAt: "2026-08-25T00:00:00Z",
    });

    expect(job.job_id).toBe("AN21-live");
    expect(job.session_id).toBe("S1");
    expect(job.status).toBe("QUEUED");
  });

});
