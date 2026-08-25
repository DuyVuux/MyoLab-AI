import { AutomationProblemError, contractProblem } from "./problem";
import type { SessionSummary, SessionDetail } from "./session";
import type { PipelineJob, PipelineStage } from "./pipeline-job";
import type { QualityAssessment, QCFinding } from "./quality";
import type { SignalWindow } from "./signal";
import type { MetricEvidence } from "./metric";
import type { ReviewCase } from "./review";
import type { AuditEvent } from "./audit";
import type { ImportJob } from "./import";
import type { SessionEvidenceBundle } from "./evidence";
import type { SessionPreflight, PreflightCheck } from "./preflight";
import type {
  ChannelMappingCandidate,
  MappingResolutionReceipt,
  SessionMappingState,
} from "./mapping";

export type UnknownRecord = Record<string, unknown>;

function fail(message: string): never {
  throw new AutomationProblemError(contractProblem(message));
}

export function isRecord(value: unknown): value is UnknownRecord {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function record(value: unknown, label: string): UnknownRecord {
  if (!isRecord(value)) fail(`${label} must be an object`);
  return value;
}

function stringValue(obj: UnknownRecord, key: string, required = true): string | undefined {
  const value = obj[key];
  if (value === undefined || value === null) {
    if (required) fail(`${key} is required`);
    return undefined;
  }
  if (typeof value !== "string") fail(`${key} must be a string`);
  return value;
}

function numberValue(obj: UnknownRecord, key: string, required = true): number | undefined {
  const value = obj[key];
  if (value === undefined || value === null) {
    if (required) fail(`${key} is required`);
    return undefined;
  }
  if (typeof value !== "number" || !Number.isFinite(value)) fail(`${key} must be a finite number`);
  return value;
}


function firstStringValue(obj: UnknownRecord, keys: string[], required = true): string | undefined {
  for (const key of keys) {
    const value = stringValue(obj, key, false);
    if (value !== undefined) return value;
  }
  if (required) fail(`${keys[0]} is required`);
  return undefined;
}

function normalizePipelineStatus(value: string): PipelineJob["status"] {
  const normalized = value.toUpperCase();
  if (normalized === "COMPLETED_WITH_WARNINGS") return "COMPLETED";
  if (normalized === "ABSTAINED" || normalized === "CANCELLED") return "BLOCKED";
  return normalized as PipelineJob["status"];
}

function booleanValue(obj: UnknownRecord, key: string, required = true): boolean | undefined {
  const value = obj[key];
  if (value === undefined || value === null) {
    if (required) fail(`${key} is required`);
    return undefined;
  }
  if (typeof value !== "boolean") fail(`${key} must be a boolean`);
  return value;
}

function stringArray(obj: UnknownRecord, key: string): string[] | undefined {
  const value = obj[key];
  if (value === undefined || value === null) return undefined;
  if (!Array.isArray(value) || !value.every((x) => typeof x === "string")) {
    fail(`${key} must be string[]`);
  }
  return value as string[];
}

export function unwrapItems(value: unknown): unknown[] {
  if (Array.isArray(value)) return value;
  const obj = record(value, "collection response");
  if (Array.isArray(obj.items)) return obj.items;
  if (Array.isArray(obj.data)) return obj.data;
  fail("collection response must be an array or contain items/data array");
}

export function parseSessionSummary(value: unknown): SessionSummary {
  const obj = record(value, "session");
  return {
    session_id: stringValue(obj, "session_id")!,
    display_name: stringValue(obj, "display_name", false),
    source_type: stringValue(obj, "source_type", false),
    automation_state:
      (stringValue(obj, "automation_state", false) ?? "UNKNOWN") as SessionSummary["automation_state"],
    qc_status: stringValue(obj, "qc_status", false) as SessionSummary["qc_status"],
    created_at: stringValue(obj, "created_at", false),
    updated_at: stringValue(obj, "updated_at", false),
  };
}

export function parseSessionDetail(value: unknown): SessionDetail {
  const obj = record(value, "session detail");
  return {
    ...parseSessionSummary(obj),
    signal_count: numberValue(obj, "signal_count", false),
    warning_count: numberValue(obj, "warning_count", false),
    blocked_reason_codes: stringArray(obj, "blocked_reason_codes"),
    limitations: stringArray(obj, "limitations"),
  };
}

export function parseImportJob(value: unknown): ImportJob {
  const obj = record(value, "import job");
  return {
    import_id: stringValue(obj, "import_id")!,
    session_id: stringValue(obj, "session_id", false),
    pipeline_job_id: stringValue(obj, "pipeline_job_id", false),
    status: stringValue(obj, "status")! as ImportJob["status"],
    detected_format: stringValue(obj, "detected_format", false) as ImportJob["detected_format"],
    source_hash: stringValue(obj, "source_hash", false),
    signal_count: numberValue(obj, "signal_count", false),
    reason_codes: stringArray(obj, "reason_codes"),
    created_at: stringValue(obj, "created_at", false),
    updated_at: stringValue(obj, "updated_at", false),
  };
}

function parsePipelineStage(value: unknown): PipelineStage {
  const obj = record(value, "pipeline stage");
  return {
    name: stringValue(obj, "name")!,
    status: stringValue(obj, "status")! as PipelineStage["status"],
    started_at: stringValue(obj, "started_at", false),
    finished_at: stringValue(obj, "finished_at", false),
    reason_codes: stringArray(obj, "reason_codes"),
  };
}

export function parsePipelineJob(value: unknown): PipelineJob {
  const obj = record(value, "pipeline job");
  const stages = obj.stages;
  const reasonCodes = stringArray(obj, "reason_codes") ?? stringArray(obj, "reasonCodes");
  const warningCodes = stringArray(obj, "warningCodes");
  return {
    job_id: firstStringValue(obj, ["job_id", "analysisId"])!,
    session_id: firstStringValue(obj, ["session_id", "sessionId"], false),
    status: normalizePipelineStatus(stringValue(obj, "status")!),
    current_stage: firstStringValue(obj, ["current_stage", "currentStage"], false),
    stages: Array.isArray(stages) ? stages.map(parsePipelineStage) : undefined,
    reason_codes: reasonCodes ?? warningCodes,
    evidence_ref: firstStringValue(obj, ["evidence_ref"], false),
    updated_at: firstStringValue(obj, ["updated_at", "updatedAt"], false),
  };
}

function parseQCFinding(value: unknown): QCFinding {
  const obj = record(value, "QC finding");
  const start = numberValue(obj, "start_s", false);
  const end = numberValue(obj, "end_s", false);
  if (start !== undefined && end !== undefined && end <= start) {
    fail("QC finding end_s must be greater than start_s");
  }
  return {
    finding_id: stringValue(obj, "finding_id", false),
    scope: stringValue(obj, "scope")! as QCFinding["scope"],
    status: stringValue(obj, "status")! as QCFinding["status"],
    reason_code: stringValue(obj, "reason_code")!,
    channel_id: stringValue(obj, "channel_id", false),
    start_s: start,
    end_s: end,
    message: stringValue(obj, "message", false),
  };
}

export function parseQualityAssessment(value: unknown): QualityAssessment {
  const obj = record(value, "quality assessment");
  const findings = obj.findings;
  if (!Array.isArray(findings)) fail("quality findings must be an array");
  const eligible = obj.eligible_window_fraction;
  if (
    eligible !== undefined &&
    eligible !== null &&
    (typeof eligible !== "number" || eligible < 0 || eligible > 1)
  ) {
    fail("eligible_window_fraction must be within [0,1] or null");
  }
  return {
    session_id: stringValue(obj, "session_id")!,
    overall_status: stringValue(obj, "overall_status")! as QualityAssessment["overall_status"],
    eligible_window_fraction: eligible as number | null | undefined,
    findings: findings.map(parseQCFinding),
    ruleset_version: stringValue(obj, "ruleset_version", false),
    evidence_ref: stringValue(obj, "evidence_ref", false),
  };
}

export function parsePreflightCheck(value: unknown): PreflightCheck {
  const obj = record(value, "preflight check");
  return {
    check_id: stringValue(obj, "check_id")!,
    label: stringValue(obj, "label")!,
    status: stringValue(obj, "status")! as PreflightCheck["status"],
    reason_code: stringValue(obj, "reason_code", false),
    message: stringValue(obj, "message", false),
  };
}

export function parseSessionPreflight(value: unknown): SessionPreflight {
  const obj = record(value, "session preflight");
  if (!Array.isArray(obj.checks)) fail("preflight checks must be an array");
  const overall = stringValue(obj, "overall_status")! as SessionPreflight["overall_status"];
  const canProceed = booleanValue(obj, "can_proceed")!;
  if (overall === "FAIL" && canProceed) {
    fail("preflight FAIL cannot have can_proceed=true");
  }
  return {
    session_id: stringValue(obj, "session_id")!,
    overall_status: overall,
    can_proceed: canProceed,
    checks: obj.checks.map(parsePreflightCheck),
    evidence_ref: stringValue(obj, "evidence_ref", false),
  };
}

export function parseMappingCandidate(value: unknown): ChannelMappingCandidate {
  const obj = record(value, "mapping candidate");
  const confidence = obj.confidence;
  if (
    confidence !== undefined &&
    confidence !== null &&
    (typeof confidence !== "number" || confidence < 0 || confidence > 1)
  ) {
    fail("mapping confidence must be within [0,1] or null");
  }
  return {
    vendor_signal_name: stringValue(obj, "vendor_signal_name")!,
    canonical_channel_id: stringValue(obj, "canonical_channel_id", false),
    canonical_label: stringValue(obj, "canonical_label", false),
    confidence: confidence as number | null | undefined,
    decision: stringValue(obj, "decision")! as ChannelMappingCandidate["decision"],
    reason_code: stringValue(obj, "reason_code", false),
  };
}

export function parseSessionMappingState(value: unknown): SessionMappingState {
  const obj = record(value, "mapping state");
  if (!Array.isArray(obj.candidates)) fail("mapping candidates must be an array");
  return {
    session_id: stringValue(obj, "session_id")!,
    ontology_version: stringValue(obj, "ontology_version", false),
    resolved_count: numberValue(obj, "resolved_count")!,
    unresolved_count: numberValue(obj, "unresolved_count")!,
    candidates: obj.candidates.map(parseMappingCandidate),
    evidence_ref: stringValue(obj, "evidence_ref", false),
  };
}

export function parseMappingResolutionReceipt(value: unknown): MappingResolutionReceipt {
  const obj = record(value, "mapping resolution receipt");
  return {
    session_id: stringValue(obj, "session_id")!,
    vendor_signal_name: stringValue(obj, "vendor_signal_name")!,
    canonical_channel_id: stringValue(obj, "canonical_channel_id")!,
    accepted: booleanValue(obj, "accepted")!,
    revision: numberValue(obj, "revision", false),
    evidence_ref: stringValue(obj, "evidence_ref", false),
  };
}

export function parseSignalWindow(value: unknown): SignalWindow {
  const obj = record(value, "signal window");
  const samples = obj.samples;
  if (!Array.isArray(samples) || !samples.every((x) => typeof x === "number" && Number.isFinite(x))) {
    fail("signal samples must be finite number[]");
  }
  const fs = numberValue(obj, "sampling_rate_hz")!;
  if (fs <= 0) fail("sampling_rate_hz must be > 0");
  const start = numberValue(obj, "start_s")!;
  const end = numberValue(obj, "end_s")!;
  if (end <= start) fail("signal window end_s must be greater than start_s");
  const provenance = record(obj.provenance, "signal provenance");
  const representation = stringValue(obj, "representation")! as SignalWindow["representation"];
  if (representation === "PROCESSED" && typeof provenance.processing_manifest_id !== "string") {
    fail("PROCESSED signal requires processing_manifest_id");
  }
  return {
    session_id: stringValue(obj, "session_id")!,
    channel_id: stringValue(obj, "channel_id")!,
    representation,
    sampling_rate_hz: fs,
    unit: stringValue(obj, "unit")!,
    start_s: start,
    end_s: end,
    samples: samples as number[],
    provenance: {
      source_hash: stringValue(provenance, "source_hash", false),
      source_id: stringValue(provenance, "source_id", false),
      processing_manifest_id: stringValue(provenance, "processing_manifest_id", false),
      config_version: stringValue(provenance, "config_version", false),
      contract_version: stringValue(provenance, "contract_version", false),
    },
  };
}

export function parseMetricEvidence(value: unknown): MetricEvidence {
  const obj = record(value, "metric evidence");
  const eligibility = stringValue(obj, "eligibility")! as MetricEvidence["eligibility"];
  const raw = obj.value;
  if (
    raw !== null &&
    raw !== undefined &&
    (typeof raw !== "number" || !Number.isFinite(raw))
  ) fail("metric value must be finite number or null");
  if (eligibility !== "AVAILABLE" && raw !== null) {
    fail("non-AVAILABLE metric must use value=null");
  }
  if (eligibility !== "AVAILABLE" && typeof obj.reason_code !== "string") {
    fail("non-AVAILABLE metric requires reason_code");
  }
  return {
    metric_id: stringValue(obj, "metric_id")!,
    metric_name: stringValue(obj, "metric_name")!,
    value: raw == null ? null : raw as number,
    unit: obj.unit == null ? null : stringValue(obj, "unit")!,
    eligibility,
    reason_code: stringValue(obj, "reason_code", false),
    channel_id: stringValue(obj, "channel_id", false),
    source_window_id: stringValue(obj, "source_window_id", false),
  };
}

export function parseReviewCase(value: unknown): ReviewCase {
  const obj = record(value, "review case");
  return {
    case_id: stringValue(obj, "case_id")!,
    session_id: stringValue(obj, "session_id")!,
    state: stringValue(obj, "state")! as ReviewCase["state"],
    reason_codes: stringArray(obj, "reason_codes") ?? [],
    created_at: stringValue(obj, "created_at", false),
    updated_at: stringValue(obj, "updated_at", false),
  };
}

export function parseAuditEvent(value: unknown): AuditEvent {
  const obj = record(value, "audit event");
  return {
    event_id: stringValue(obj, "event_id")!,
    session_id: stringValue(obj, "session_id", false),
    event_type: stringValue(obj, "event_type")!,
    timestamp: stringValue(obj, "timestamp")!,
    actor_type: (stringValue(obj, "actor_type", false) ?? "UNKNOWN") as AuditEvent["actor_type"],
    actor_ref: stringValue(obj, "actor_ref", false),
    artifact_ref: stringValue(obj, "artifact_ref", false),
    config_version: stringValue(obj, "config_version", false),
    reason_codes: stringArray(obj, "reason_codes"),
  };
}

export function parseSessionEvidenceBundle(value: unknown): SessionEvidenceBundle {
  const obj = record(value, "session evidence bundle");
  const provenance = record(obj.provenance, "session evidence provenance");
  const metrics = obj.metrics;
  if (!Array.isArray(metrics)) fail("session evidence metrics must be an array");
  return {
    session_id: stringValue(obj, "session_id")!,
    provenance: {
      source_hash: stringValue(provenance, "source_hash", false),
      source_id: stringValue(provenance, "source_id", false),
      processing_manifest_id: stringValue(provenance, "processing_manifest_id", false),
      config_version: stringValue(provenance, "config_version", false),
      contract_version: stringValue(provenance, "contract_version", false),
    },
    quality: obj.quality == null ? undefined : parseQualityAssessment(obj.quality),
    metrics: metrics.map(parseMetricEvidence),
    limitations: stringArray(obj, "limitations") ?? [],
    review_case_ids: stringArray(obj, "review_case_ids"),
    evidence_refs: stringArray(obj, "evidence_refs"),
  };
}
