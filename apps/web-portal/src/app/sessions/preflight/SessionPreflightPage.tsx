import { PreflightSummaryPanel } from "../../../components/data-intake/PreflightSummaryPanel";
import { goldenPreflight } from "../../../mocks/day20ScenarioRegistry";

export const SessionPreflightPage = (): JSX.Element => (
  <main>
    <h1>Preflight Signal Preview</h1>
    <PreflightSummaryPanel summary={goldenPreflight} />
    <button type="button" disabled={goldenPreflight.state !== "ready"}>Tiếp tục hiệu chỉnh / Quality Gate</button>
  </main>
);
