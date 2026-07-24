import {
  metricDisplay,
  type QuantitativeMetric,
} from '../../schemas/uc2-assessment.schema';

export interface QuantitativeKpiRowProps {
  readonly metrics: readonly QuantitativeMetric[];
}

export function QuantitativeKpiRow({ metrics }: QuantitativeKpiRowProps): JSX.Element {
  return (
    <section aria-labelledby="uc2-kpis">
      <h2 id="uc2-kpis">Chỉ số định lượng</h2>
      <div>
        {metrics.slice(0, 6).map((metric) => (
          <article key={metric.metricId}>
            <h3>{metric.labelVi}</h3>
            <strong>{metricDisplay(metric)}</strong>
            <p>Trạng thái: {metric.status}</p>
            <small>
              {metric.formulaVersion} · {metric.validationStatus}
            </small>
          </article>
        ))}
      </div>
    </section>
  );
}
