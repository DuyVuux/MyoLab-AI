import {
  QuantitativeKpiRow,
} from '../../../components/uc2/QuantitativeKpiRow';
import {
  SessionCompatibilityTable,
} from '../../../components/uc2/SessionCompatibilityTable';
import {
  RepeatabilityPanel,
} from '../../../components/uc2/RepeatabilityPanel';
import {
  SymmetryPanel,
} from '../../../components/uc2/SymmetryPanel';
import {
  FatigueEndurancePanel,
} from '../../../components/uc2/FatigueEndurancePanel';
import type { UC2QuantitativeAssessment } from '../../../schemas/uc2-assessment.schema';

export interface Day23UC2AssessmentPageProps {
  readonly assessment: UC2QuantitativeAssessment;
}

export function Day23UC2AssessmentPage({
  assessment,
}: Day23UC2AssessmentPageProps): JSX.Element {
  const metricById = new Map(assessment.metrics.map((m) => [m.metricId, m]));

  return (
    <main>
      <h1>UC2 — Đánh giá định lượng</h1>
      <p>
        Trạng thái: {assessment.status}. Human review bắt buộc: true
      </p>
      <QuantitativeKpiRow metrics={assessment.metrics} />
      <SessionCompatibilityTable result={assessment.compatibility} />
      <RepeatabilityPanel metric={metricById.get('repeatability_cov')} />
      <SymmetryPanel metric={metricById.get('symmetry_ratio')} />
      <FatigueEndurancePanel metric={metricById.get('time_to_fatigue_change')} />
      <section>
        <h2>Giới hạn</h2>
        <ul>
          {assessment.limitations.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
      </section>
    </main>
  );
}
