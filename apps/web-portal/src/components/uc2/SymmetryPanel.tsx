import type { QuantitativeMetric } from '../../schemas/uc2-assessment.schema';

export interface SymmetryPanelProps {
  readonly metric?: QuantitativeMetric;
}

export function SymmetryPanel({ metric }: SymmetryPanelProps): JSX.Element {
  return (
    <section>
      <h2>Đối xứng affected/reference</h2>
      <p>
        {metric?.value === null || metric === undefined
          ? 'Không khả dụng'
          : `${metric.value.toFixed(1)} ${metric.unit ?? ''}`}
      </p>
      <p>Chỉ diễn giải khi hai bên cùng protocol, đơn vị và chuẩn hóa.</p>
    </section>
  );
}
