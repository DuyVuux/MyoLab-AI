import type { UseCaseId } from "./analysis-envelope.schema";
import type { UserRole } from "./role.schema";

export type SessionType = "baseline" | "follow_up" | "replay" | "research";
export type BodySide = "left" | "right" | "bilateral" | "not_applicable";
export type DataSourceIntent =
  | "synthetic_demo"
  | "generic_csv_manifest"
  | "noraxon_export_mock"
  | "deidentified_replay";

export interface ConsentScope {
  readonly qualityImprovement: boolean;
  readonly modelTraining: boolean;
  readonly researchExport: boolean;
}

export interface ProtocolRef {
  readonly protocolId: string;
  readonly protocolVersion: string;
}

export interface SessionDraft {
  readonly subjectRef: string;
  readonly useCaseId: UseCaseId | null;
  readonly protocol: ProtocolRef | null;
  readonly affectedSide: BodySide | null;
  readonly referenceSide: BodySide | null;
  readonly targetMuscles: readonly string[];
  readonly sessionType: SessionType;
  readonly operatorRef: string;
  readonly consent: ConsentScope;
  readonly dataSourceIntent: DataSourceIntent | null;
  readonly previousSessionId?: string;
}

export interface SessionRecord extends SessionDraft {
  readonly schemaVersion: "session-record.v0.1";
  readonly sessionId: string;
  readonly workflowStatus:
    | "draft"
    | "intake_in_progress"
    | "mapping_required"
    | "preflight_ready"
    | "calibration_required"
    | "quality_ready"
    | "analysis_ready"
    | "abstained";
  readonly createdAt: string;
  readonly containsDirectIdentifier: false;
}

export interface ValidationIssue {
  readonly code: string;
  readonly field: string;
  readonly messageVi: string;
}

const directIdentifierPattern = /@|\b\d{9,12}\b/;

export const validateSessionDraft = (
  draft: SessionDraft,
  role: UserRole,
): readonly ValidationIssue[] => {
  const issues: ValidationIssue[] = [];
  const add = (code: string, field: string, messageVi: string): void => {
    issues.push({ code, field, messageVi });
  };

  if (!draft.subjectRef.trim()) add("SUBJECT_REF_REQUIRED", "subjectRef", "Cần mã đối tượng ẩn danh.");
  if (directIdentifierPattern.test(draft.subjectRef)) add("DIRECT_IDENTIFIER_NOT_ALLOWED", "subjectRef", "Không nhập email, điện thoại hoặc mã hồ sơ trực tiếp.");
  if (!draft.useCaseId) add("USE_CASE_REQUIRED", "useCaseId", "Cần chọn use case.");
  if (!draft.protocol) add("PROTOCOL_REQUIRED", "protocol", "Cần chọn protocol và phiên bản.");
  if (!draft.affectedSide) add("AFFECTED_SIDE_REQUIRED", "affectedSide", "Cần xác nhận bên đánh giá.");
  if (draft.targetMuscles.length === 0) add("TARGET_MUSCLE_REQUIRED", "targetMuscles", "Cần ít nhất một cơ mục tiêu.");
  if (!draft.operatorRef.trim()) add("OPERATOR_REQUIRED", "operatorRef", "Cần mã người vận hành.");
  if (!draft.dataSourceIntent) add("DATA_SOURCE_REQUIRED", "dataSourceIntent", "Cần chọn nguồn dữ liệu dự kiến.");
  if (!draft.consent.qualityImprovement && !draft.consent.modelTraining && !draft.consent.researchExport) {
    add("CONSENT_SCOPE_REQUIRED", "consent", "Cần ghi nhận phạm vi sử dụng dữ liệu.");
  }
  if (draft.sessionType === "follow_up" && !draft.previousSessionId) {
    add("PREVIOUS_SESSION_REQUIRED", "previousSessionId", "Buổi follow-up cần tham chiếu buổi trước tương thích.");
  }
  if (role === "patient") add("ROLE_NOT_ALLOWED", "role", "Bệnh nhân không có quyền tạo phiên đánh giá lâm sàng.");
  if ((draft.useCaseId === "uc3" || draft.useCaseId === "uc4") && !["research", "replay"].includes(draft.sessionType)) {
    add("FEASIBILITY_SESSION_ONLY", "sessionType", "UC3/UC4 chỉ dùng phiên research hoặc replay.");
  }
  return issues;
};
