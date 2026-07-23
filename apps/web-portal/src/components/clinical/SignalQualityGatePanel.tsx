import type { DetailedQualityResult } from "../../schemas/quality-gate.schema";
import { Alert } from "../ui/Alert";

export interface SignalQualityGatePanelProps {
  readonly result: DetailedQualityResult;
}

export const SignalQualityGatePanel = ({ result }: SignalQualityGatePanelProps): JSX.Element => {
  const tone = result.status === "pass" ? "success" : result.status === "warning" ? "warning" : "abstention";
  return (
    <section>
      <Alert title={`Signal Quality Gate: ${result.status}`} variant={tone}>
        <p>Usable windows: {Math.round(result.usableWindowRatio * 100)}%</p>
        <p>Bad channels: {result.badChannels.join(", ") || "Không có"}</p>
        <p>Reason codes: {result.reasonCodes.join(", ") || "Không có"}</p>
        <p>MFCV: {result.mfcvEligibility}</p>
        <p>{result.recommendedActionsVi.join(" ")}</p>
      </Alert>
    </section>
  );
};
