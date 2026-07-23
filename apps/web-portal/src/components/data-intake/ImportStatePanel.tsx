import type { SignalImportRecord } from "../../schemas/import-workflow.schema";
import { Alert } from "../ui/Alert";

export interface ImportStatePanelProps {
  readonly record: SignalImportRecord;
}

export const ImportStatePanel = ({ record }: ImportStatePanelProps): JSX.Element => {
  const tone = record.state === "import_rejected" ? "error" : record.state === "mapping_required" ? "warning" : "info";
  return (
    <Alert title={`Import: ${record.state}`} variant={tone}>
      <dl>
        <dt>Import ID</dt><dd>{record.importId}</dd>
        <dt>File</dt><dd>{record.sanitizedFilename}</dd>
        <dt>Source hash</dt><dd><code>{record.sourceHashSha256}</code></dd>
        <dt>Error code</dt><dd>{record.errorCode ?? "Không có"}</dd>
      </dl>
    </Alert>
  );
};
