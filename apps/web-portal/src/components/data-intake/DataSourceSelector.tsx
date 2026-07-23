import type { DataSourceIntent } from "../../schemas/session-intake.schema";

export interface DataSourceOption {
  readonly value: DataSourceIntent;
  readonly label: string;
  readonly description: string;
}

export interface DataSourceSelectorProps {
  readonly selected: DataSourceIntent | null;
  readonly onSelect: (value: DataSourceIntent) => void;
}

const options: readonly DataSourceOption[] = [
  { value: "synthetic_demo", label: "Synthetic deterministic", description: "Dùng cho demo và test." },
  { value: "generic_csv_manifest", label: "Generic CSV + manifest", description: "Contract chuẩn của platform." },
  { value: "noraxon_export_mock", label: "Import file xuất từ Noraxon/myoRESEARCH", description: "Không phải kết nối SDK trực tiếp." },
  { value: "deidentified_replay", label: "De-identified replay", description: "Replay offline đã được duyệt." },
];

export const DataSourceSelector = ({ selected, onSelect }: DataSourceSelectorProps): JSX.Element => (
  <fieldset>
    <legend>Chọn nguồn dữ liệu</legend>
    {options.map((option) => (
      <label key={option.value}>
        <input
          type="radio"
          name="data-source"
          checked={selected === option.value}
          onChange={() => onSelect(option.value)}
        />
        <span>{option.label}</span>
        <small>{option.description}</small>
      </label>
    ))}
  </fieldset>
);
