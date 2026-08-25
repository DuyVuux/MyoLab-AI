import { parseMetricEvidence, parseQualityAssessment, parseSignalWindow } from "../../../contracts/automation/validators";

describe("UI-I1 automation contract safety", () => {
  test("unsupported metric must be null + reason", () => {
    expect(() => parseMetricEvidence({
      metric_id: "mfcv", metric_name: "MFCV", value: 0, unit: "m/s",
      eligibility: "NOT_ELIGIBLE", reason_code: "ELECTRODE_GEOMETRY_NOT_VERIFIED",
    })).toThrow();
    expect(parseMetricEvidence({
      metric_id: "mfcv", metric_name: "MFCV", value: null, unit: null,
      eligibility: "NOT_ELIGIBLE", reason_code: "ELECTRODE_GEOMETRY_NOT_VERIFIED",
    }).value).toBeNull();
  });

  test("processed signal requires manifest", () => {
    expect(() => parseSignalWindow({
      session_id: "S1", channel_id: "C1", representation: "PROCESSED",
      sampling_rate_hz: 2000, unit: "uV", start_s: 0, end_s: 1,
      samples: [0, 1], provenance: { source_hash: "abc" },
    })).toThrow();
  });

  test("QC eligible fraction is bounded", () => {
    expect(() => parseQualityAssessment({
      session_id: "S1", overall_status: "PASS", eligible_window_fraction: 1.1, findings: [],
    })).toThrow();
  });
});
