import { SignalQualityGatePanel } from "../../../components/clinical/SignalQualityGatePanel";
import { qualityWarning } from "../../../mocks/day20ScenarioRegistry";

export const SessionQualityPage = (): JSX.Element => (
  <main>
    <h1>Signal Quality Gate</h1>
    <SignalQualityGatePanel result={qualityWarning} />
    <button type="button">Xác nhận cảnh báo với lý do</button>
  </main>
);
