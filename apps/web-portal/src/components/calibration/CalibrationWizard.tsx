import type { CalibrationRecord } from "../../schemas/calibration.schema";
import { Alert } from "../ui/Alert";

export interface CalibrationWizardProps {
  readonly record: CalibrationRecord;
}

export const CalibrationWizard = ({ record }: CalibrationWizardProps): JSX.Element => {
  const tone = record.state === "pass" ? "success" : record.state === "warning" ? "warning" : "error";
  return (
    <section aria-labelledby="calibration-title">
      <h2 id="calibration-title">Hiệu chỉnh cá nhân</h2>
      <Alert title={`Calibration: ${record.state}`} variant={tone}>
        <p>Calibration ID: <code>{record.calibrationId}</code></p>
        <p>Repetition dùng được: {record.acceptedRepetitions}/{record.plannedRepetitions}</p>
        <p>Usable ratio: {Math.round(record.usableRepetitionRatio * 100)}%</p>
        <p>Thời gian: {record.durationS} giây</p>
        <p>Đây là reference của phiên prototype, không phải model training lâm sàng.</p>
      </Alert>
    </section>
  );
};
