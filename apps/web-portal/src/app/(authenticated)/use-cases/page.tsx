/**
 * Use Case Portfolio — `/use-cases`
 * Per Section 6.1: 4 use case cards with tier badges, CTAs, disclaimers
 * UC3/UC4 visually distinct from UC1/UC2
 */
'use client';

import Link from 'next/link';
import {
  Activity,
  Stethoscope,
  FlaskConical,
  Monitor,
  Users,
  Cpu,
  Shield,
  RefreshCcw,
  CheckCircle,
} from 'lucide-react';
import { Card, CardContent, CardFooter } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { USE_CASE_CONFIGS } from '@/config/useCaseRoutes';
import styles from './use-cases.module.css';

const UC_ICONS: Record<string, React.ElementType> = {
  uc1: Activity,
  uc2: Stethoscope,
  uc3: FlaskConical,
  uc4: Monitor,
};

export default function UseCasesPage() {
  return (
    <div className="page-container">
      <div className="page-header">
        <div className="page-header__left">
          <h1 className="page-title">Danh mục Use Case</h1>
          <p className="page-subtitle">
            Bốn use case canonical của MyoLab-AI — từ biofeedback kỹ thuật đến nghiên cứu khả thi.
          </p>
        </div>
      </div>

      {/* Global badges per Section 6.1 */}
      <div className={styles.globalBadges}>
        <Badge variant="info" icon={<Users size={12} />}>
          Human-in-the-loop
        </Badge>
        <Badge variant="info" icon={<RefreshCcw size={12} />}>
          No auto-retraining
        </Badge>
        <Badge variant="info" icon={<CheckCircle size={12} />}>
          Signal quality before AI
        </Badge>
      </div>

      {/* Use case grid */}
      <div className={styles.grid}>
        {USE_CASE_CONFIGS.map((uc) => {
          const Icon = UC_ICONS[uc.id] || Activity;
          const isTier2 = uc.tier === 2;

          return (
            <Card
              key={uc.id}
              variant={isTier2 ? 'outlined' : 'default'}
              padding="lg"
              className={[styles.ucCard, isTier2 ? styles['ucCard--tier2'] : ''].filter(Boolean).join(' ')}
            >
              <CardContent>
                <div className={styles.ucHeader}>
                  <div className={styles.ucIconContainer}>
                    <Icon size={24} />
                  </div>
                  <Badge variant={isTier2 ? 'tier2' : 'tier1'}>
                    Tầng {uc.tier} {isTier2 ? '— Nghiên cứu' : '— MVP'}
                  </Badge>
                </div>

                <h2 className={styles.ucName}>{uc.name}</h2>
                <p className={styles.ucDescription}>{uc.description}</p>

                <div className={styles.ucMeta}>
                  <div className={styles.ucMetaItem}>
                    <Users size={14} aria-hidden="true" />
                    <span>{uc.targetAudience}</span>
                  </div>
                  <div className={styles.ucMetaItem}>
                    <Cpu size={14} aria-hidden="true" />
                    <span>{uc.hardware}</span>
                  </div>
                  <div className={styles.ucMetaItem}>
                    <Shield size={14} aria-hidden="true" />
                    <span>{uc.status}</span>
                  </div>
                </div>

                <p className={styles.ucDisclaimer}>{uc.disclaimer}</p>
              </CardContent>

              <CardFooter>
                <Link href={uc.introRoute}>
                  <Button variant={isTier2 ? 'secondary' : 'primary'}>
                    {uc.cta}
                  </Button>
                </Link>
              </CardFooter>
            </Card>
          );
        })}
      </div>
    </div>
  );
}
