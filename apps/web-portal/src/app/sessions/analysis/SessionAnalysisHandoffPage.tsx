import { AnalysisHandoffPanel } from "../../../components/clinical/AnalysisHandoffPanel";
import { queuedHandoff } from "../../../mocks/day20ScenarioRegistry";

export const SessionAnalysisHandoffPage = (): JSX.Element => (
  <main><h1>Bàn giao phân tích</h1><AnalysisHandoffPanel handoff={queuedHandoff} /></main>
);
