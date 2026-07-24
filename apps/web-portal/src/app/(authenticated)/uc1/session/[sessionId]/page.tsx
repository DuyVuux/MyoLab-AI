import { UC1SessionWorkspace } from "@/components/uc1/UC1SessionWorkspace";
import { Alert } from "@/components/ui/Alert";
import { isUC1ReplayScenarioId } from "@/schemas/gesture-inference.schema";

interface PageProps {
  readonly params: { readonly sessionId: string };
  readonly searchParams: {
    readonly analysisId?: string | readonly string[];
    readonly scenarioId?: string | readonly string[];
  };
}

function queryValue(value: string | readonly string[] | undefined): string | null {
  const candidate = Array.isArray(value) ? value[0] : value;
  return typeof candidate === "string" && candidate.trim()
    ? candidate.trim()
    : null;
}

export default function UC1SessionPage({ params, searchParams }: PageProps) {
  const analysisId = queryValue(searchParams.analysisId);
  const scenarioId = queryValue(searchParams.scenarioId) ?? "uc1_golden_correct";
  if (analysisId === null || !isUC1ReplayScenarioId(scenarioId)) {
    const errorCode =
      analysisId === null
        ? "ANALYSIS_ID_REQUIRED"
        : "UNKNOWN_REPLAY_SCENARIO";
    return (
      <div className="page-container">
        <h1>UC1 · Biofeedback cử chỉ — Replay kỹ thuật</h1>
        <Alert
          variant="error"
          title="Không tải được kết quả kỹ thuật"
          reasonCode={errorCode}
        >
          Route cần analysis và scenario hợp lệ do server cấp. Giao diện không
          tự sinh provenance hoặc tự chuyển một scenario không biết sang golden.
        </Alert>
      </div>
    );
  }

  return (
    <UC1SessionWorkspace
      sessionId={params.sessionId}
      analysisId={analysisId}
      scenarioId={scenarioId}
    />
  );
}
