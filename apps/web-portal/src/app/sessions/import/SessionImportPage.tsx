import { ImportStatePanel } from "../../../components/data-intake/ImportStatePanel";
import { goldenImport } from "../../../mocks/day20ScenarioRegistry";

export const SessionImportPage = (): JSX.Element => (
  <main>
    <h1>Import dữ liệu</h1>
    <p>Chọn fixture deterministic hoặc file export mock. Không lưu raw bytes trong browser storage.</p>
    <ImportStatePanel record={goldenImport} />
  </main>
);
