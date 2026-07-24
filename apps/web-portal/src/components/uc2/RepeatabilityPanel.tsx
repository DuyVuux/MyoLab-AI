import type { QuantitativeMetric } from '../../schemas/uc2-assessment.schema';

export interface RepeatabilityPanelProps {
  readonly metric?: QuantitativeMetric;
}

export function RepeatabilityPanel({ metric }: RepeatabilityPanelProps): JSX.Element {
  return (
    <section>
      <h2>Repeatability</h2>
      <p>
        {metric?.value === null || metric === undefined
          ? 'Chưa có dữ liệu'
          : `${metric.value.toFixed(2)} ${metric.unit ?? ''}`}
      </p>
      <p>CoV thấp thường biểu thị ổn định hơn; đây là chỉ số kỹ thuật.</p>
    </section>
  );
}
