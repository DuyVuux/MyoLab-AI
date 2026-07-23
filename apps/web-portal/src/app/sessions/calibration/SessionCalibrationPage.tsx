import { CalibrationWizard } from "../../../components/calibration/CalibrationWizard";
import { goldenCalibration } from "../../../mocks/day20ScenarioRegistry";

export const SessionCalibrationPage = (): JSX.Element => (
  <main><h1>Calibration Wizard</h1><CalibrationWizard record={goldenCalibration} /></main>
);
