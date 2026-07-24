'use client';

import { useEffect, useMemo, useState } from 'react';
import {
  usePathname,
  useParams,
  useRouter,
  useSearchParams,
} from 'next/navigation';
import { Alert } from '@/components/ui/Alert';
import { Button } from '@/components/ui/Button';
import { Day23UC2LongitudinalPage } from '@/app/uc2/longitudinal/Day23UC2LongitudinalPage';
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

export default function UC2LongitudinalPage() {
  const params = useParams();
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const subjectRef = params.subjectRef as string;

  const initialScenario = useMemo<UC2Scenario>(() => {
    const queryScenario = searchParams.get('scenario');
    if (queryScenario && SCENARIOS.includes(queryScenario as UC2Scenario)) {
      return queryScenario as UC2Scenario;
    }
    return 'golden_uc2_longitudinal';
  }, [searchParams]);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [scenario, setScenario] = useState<UC2Scenario>(initialScenario);
  const [assessment, setAssessment] = useState<UC2QuantitativeAssessment | null>(null);

  useEffect(() => {
    const query = new URLSearchParams(searchParams);
    query.set('scenario', scenario);
    const nextQuery = query.toString();
    const nextUrl = nextQuery ? `${pathname}?${nextQuery}` : pathname;
    router.replace(nextUrl, { scroll: false });

    let mounted = true;
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
  }, [scenario, pathname, router, searchParams]);

  return (
    <div className="page-container">
      <div className="page-header">
        <div className="page-header__left">
          <h1 className="page-title">Longitudinal Trend</h1>
          <p className="page-subtitle">Chủ đề theo dõi: {subjectRef}</p>
        </div>
        <div className="page-header__right">
          <label>
            Scenario:
            <select
              value={scenario}
              onChange={(event) => setScenario(event.target.value as UC2Scenario)}
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

      {loading ? <Alert variant="info">Đang tạo dữ liệu so sánh...</Alert> : null}
      {error ? <Alert variant="error">{error}</Alert> : null}

      {assessment ? <Day23UC2LongitudinalPage assessment={assessment} /> : null}

      <div style={{ marginTop: '1rem', display: 'flex', justifyContent: 'flex-end' }}>
        <Button variant="secondary" onClick={() => router.back()}>
          Quay lại
        </Button>
      </div>
    </div>
  );
}
