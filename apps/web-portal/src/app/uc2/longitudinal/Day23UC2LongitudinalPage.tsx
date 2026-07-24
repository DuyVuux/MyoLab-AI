import {
  AccessibleMetricChart,
} from '../../../components/uc2/AccessibleMetricChart';
import { SessionCompatibilityTable } from '../../../components/uc2/SessionCompatibilityTable';
import type { UC2QuantitativeAssessment } from '../../../schemas/uc2-assessment.schema';

export interface Day23UC2LongitudinalPageProps {
  readonly assessment: UC2QuantitativeAssessment;
}

export function Day23UC2LongitudinalPage({
  assessment,
}: Day23UC2LongitudinalPageProps): JSX.Element {
  const fatigue = assessment.metrics.find((metric) => metric.metricId === 'time_to_fatigue_change');
  const points = [
    { label: 'Baseline', value: 60 },
    { label: 'Week 4', value: 72 },
  ];

  return (
    <main>
      <h1>Theo dõi dọc UC2</h1>
      <SessionCompatibilityTable result={assessment.compatibility} />
      {assessment.compatibility.conclusionAllowed ? (
        <section>
          <h2>Mẫu minh họa Endurance (giờ)</h2>
          <AccessibleMetricChart
            title="Thay đổi thời gian tới mệt"
            unit="giây"
            points={points}
          />
          {fatigue?.value === null ? <p>Không có metric fatigue có thể diễn giải.</p> : null}
          <p>
            Chỉ số delta: {fatigue && fatigue.value !== null ? `${fatigue.value.toFixed(1)}%` : 'N/A'}
          </p>
        </section>
      ) : (
        <p role="status">Không tạo trend longitudinal vì session không tương thích.</p>
      )}
    </main>
  );
}
