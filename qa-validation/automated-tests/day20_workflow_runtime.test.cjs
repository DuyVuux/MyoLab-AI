const assert = require("node:assert/strict");
const path = require("node:path");
const base = path.resolve(process.cwd(), ".day20-build");
const importWorkflow = require(path.join(base, "workflows/importWorkflowReducer.js"));
const mapping = require(path.join(base, "schemas/channel-mapping.schema.js"));
const preflight = require(path.join(base, "schemas/preflight.schema.js"));
const calibration = require(path.join(base, "schemas/calibration.schema.js"));
const calibrationWorkflow = require(path.join(base, "workflows/calibrationWorkflowReducer.js"));
const quality = require(path.join(base, "schemas/quality-gate.schema.js"));

let state = "draft";
for (const event of ["SELECT_FILE", "START_HASH", "HASH_COMPLETE", "LOCAL_VALIDATION_PASS", "START_UPLOAD", "UPLOAD_COMPLETE", "MAPPING_REQUIRED", "MAPPING_COMPLETE", "MARK_QC_READY"]) {
  state = importWorkflow.nextImportState(state, event);
}
assert.equal(state, "qc_ready");
assert.throws(() => importWorkflow.nextImportState("import_rejected", "MARK_QC_READY"), /INVALID_IMPORT_TRANSITION/);

const goodMappings = [
  { sourceChannel: "S1", canonicalChannelId: "CH01", muscle: "Flexor", side: "right", unit: "uV", functionalRole: "flexor" },
  { sourceChannel: "S2", canonicalChannelId: "CH02", muscle: "Extensor", side: "right", unit: "uV", functionalRole: "extensor" },
];
assert.equal(mapping.validateChannelMappings(goodMappings, ["S1", "S2"]).valid, true);
assert.equal(mapping.validateChannelMappings([goodMappings[0], { ...goodMappings[1], canonicalChannelId: "CH01" }], ["S1", "S2"]).valid, false);

assert.equal(preflight.derivePreflightState({ samplingRateHz: 1000, durationS: 60, channelCount: 2, timestampMonotonic: true, mappingCompleteness: 1 }), "ready");
assert.equal(preflight.derivePreflightState({ samplingRateHz: 1000, durationS: 60, channelCount: 2, timestampMonotonic: true, mappingCompleteness: 0.5 }), "mapping_required");
assert.equal(preflight.derivePreflightState({ samplingRateHz: undefined, durationS: 60, channelCount: 2, timestampMonotonic: true, mappingCompleteness: 1 }), "import_blocked");
assert.ok(preflight.downsamplePreview(Array.from({ length: 70000 }, (_, i) => i), 1000, 500).length <= 500);

assert.equal(calibration.usableRepetitionRatio(13, 15), 13 / 15);
let calState = "not_started";
for (const event of ["START", "SETUP_PASS", "REST_COMPLETE", "FINISH_REPETITIONS", "SUMMARY_PASS"]) {
  calState = calibrationWorkflow.nextCalibrationState(calState, event);
}
assert.equal(calState, "pass");

const warning = {
  schemaVersion: "detailed-quality-result.v0.1", qualityResultId: "Q", sessionId: "S", status: "warning",
  usableWindowRatio: 0.8, badChannels: [], artifactFlags: [], reasonCodes: ["POWERLINE_NOISE_HIGH"],
  mfcvEligibility: "not_eligible", recommendedActionsVi: [], qcVersion: "qc_v0.1",
};
assert.equal(quality.canProceedFromQuality(warning, "ktv"), false);
assert.equal(quality.canProceedFromQuality({ ...warning, warningAcknowledgedBy: "KTV", warningAcknowledgementReason: "Đã kiểm tra" }, "ktv"), true);

console.log("DAY20 WORKFLOW RUNTIME TESTS PASSED");
