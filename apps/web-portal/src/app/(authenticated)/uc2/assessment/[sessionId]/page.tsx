'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { ArrowRight } from 'lucide-react';
import { Alert } from '@/components/ui/Alert';
import { Button } from '@/components/ui/Button';
import * as MockWorkflowRepository from '@/services/mock/MockWorkflowRepository';
import type { SessionContext } from '@/schemas/session';
import { Day23UC2AssessmentPage } from '@/app/uc2/assessment/Day23UC2AssessmentPage';
import {
  UC2AssessmentClient,
  type UC2Scenario,
} from '@/lib/uc2-assessment-client';
import type { UC2QuantitativeAssessment } from '@/schemas/uc2-assessment.schema';

const SCENARIOS: UC2Scenario[] = [
  'golden_uc2_longitudinal',
  'uc2_protocol_incompatible',
  'uc2_missing_baseline',
  'uc2_qc_fail_session',
  'uc2_bilateral_unavailable',
];

const client = new UC2AssessmentClient(process.env.NEXT_PUBLIC_API_BASE_URL ?? '');

export default function UC2AssessmentPage() {
  const params = useParams();
  const router = useRouter();
  const sessionId = params.sessionId as string;

  const [session, setSession] = useState<SessionContext | null>(null);
  const [scenario, setScenario] = useState<UC2Scenario>('golden_uc2_longitudinal');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [assessment, setAssessment] = useState<UC2QuantitativeAssessment | null>(null);

  useEffect(() => {
    setSession(MockWorkflowRepository.getSession(sessionId));
  }, [sessionId]);

  useEffect(() => {
    let mounted = true;
    if (!session) {
      return;
    }
    setLoading(true);
    setError(null);
    client
      .create(scenario)
      .then((item) => {
        if (!mounted) return;
        setAssessment(item);
      })
      .catch((ex) => {
        if (!mounted) return;
        setError((ex as Error).message);
      })
      .finally(() => {
        if (!mounted) return;
        setLoading(false);
      });

    return () => {
      mounted = false;
    };
  }, [scenario, session]);

  if (!session) {
    return <div className="page-container">Session không tồn tại.</div>;
  }

  const hasSessionError = Boolean(error);

  return (
    <div className="page-container">
      <div className="page-header">
        <div className="page-header__left">
          <h1 className="page-title">UC2: Dashboard định lượng</h1>
          <p className="page-subtitle">Session: {sessionId}</p>
        </div>
        <div className="page-header__right">
          <label>
            Scenario:
            <select
              value={scenario}
              onChange={(event) =>
                setScenario(event.target.value as UC2Scenario)
              }
            >
              {SCENARIOS.map((item) => (
                <option key={item} value={item}>
                  {item}
                </option>
              ))}
            </select>
          </label>
        </div>
      </div>

      {loading ? <Alert variant="info">Đang tạo assessment...</Alert> : null}
      {hasSessionError ? <Alert variant="error">{error}</Alert> : null}

      {assessment ? <Day23UC2AssessmentPage assessment={assessment} /> : null}

      <div style={{ marginTop: '1rem', display: 'flex', justifyContent: 'flex-end' }}>
        <Button
          onClick={() =>
            router.push(
              `/uc2/longitudinal/${session.subjectRef}?scenario=${scenario}`,
            )
          }
          icon={<ArrowRight size={16} />}
          iconPosition="right"
        >
          Xem longitudinal
        </Button>
      </div>
    </div>
  );
}
