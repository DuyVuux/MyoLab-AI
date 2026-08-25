import type {
  ImportJob,
  PipelineJob,
  QualityAssessment,
  SessionMappingState,
  SessionPreflight,
} from "../../contracts/automation";

export type AutoDataUiState =
  | "IDLE"
  | "IMPORTING"
  | "WAITING_FOR_PIPELINE"
  | "PREFLIGHT"
  | "MAPPING_REVIEW"
  | "QC_RUNNING"
  | "QUALITY_READY"
  | "BLOCKED"
  | "FAILED";

export function deriveAutoDataUiState(input: {
  importJob?: ImportJob | null;
  pipelineJob?: PipelineJob | null;
  preflight?: SessionPreflight | null;
  mapping?: SessionMappingState | null;
  quality?: QualityAssessment | null;
}): AutoDataUiState {
  const { importJob, pipelineJob, preflight, mapping, quality } = input;

  if (!importJob) return "IDLE";
  if (importJob.status === "FAILED" || pipelineJob?.status === "FAILED") return "FAILED";
  if (importJob.status === "BLOCKED" || pipelineJob?.status === "BLOCKED") return "BLOCKED";

  // Once later-stage evidence exists, do not let a stale initial ImportJob status
  // hide the true automation state.
  if (quality) return "QUALITY_READY";

  if (preflight) {
    if (!preflight.can_proceed || preflight.overall_status === "FAIL") return "BLOCKED";
    if (mapping?.unresolved_count && mapping.unresolved_count > 0) return "MAPPING_REVIEW";
    if (mapping && mapping.unresolved_count === 0) return "QC_RUNNING";
    return "PREFLIGHT";
  }

  if (pipelineJob?.status === "RUNNING" || pipelineJob?.status === "QUEUED") {
    return "WAITING_FOR_PIPELINE";
  }

  return importJob.status === "READY_FOR_QC" ? "PREFLIGHT" : "IMPORTING";
}

export function qualityNeedsHumanReview(quality: QualityAssessment): boolean {
  return quality.overall_status === "WARNING" || quality.overall_status === "UNKNOWN";
}

export function qualityBlocksDownstream(quality: QualityAssessment): boolean {
  return quality.overall_status === "FAIL";
}

export function mappingCanAutoAdvance(mapping: SessionMappingState): boolean {
  return mapping.unresolved_count === 0;
}
