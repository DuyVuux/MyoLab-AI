/**
 * Dashboard Page — `/dashboard`
 * Per Section 6.2: Session stats, QC fails, pending reviews, quick actions
 */
'use client';

import Link from 'next/link';
import {
  Plus,
  ClipboardList,
  AlertTriangle,
  BarChart3,
  Clock,
  CheckCircle,
  MessageSquare,
  Upload,
  ArrowRight,
} from 'lucide-react';
import { Card, CardContent } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { useAuth } from '@/lib/auth';
import { ROUTES } from '@/config/useCaseRoutes';
import styles from './dashboard.module.css';

// ASSUMPTION: Mock data — will be replaced by API calls
const MOCK_STATS = {
  sessionsPreparing: 3,
  importsPendingMapping: 2,
  qcFailAbstained: 1,
  analysisRunning: 1,
  reviewPending: 4,
  feedbackPendingAdjudication: 2,
};

interface RecentSession {
  id: string;
  subjectRef: string;
  useCase: string;
  useCaseLabel: string;
  importState: string;
  qcState: string | null;
  analysisState: string | null;
  reviewState: string | null;
  updatedAt: string;
}

const MOCK_RECENT_SESSIONS: RecentSession[] = [
  {
    id: 'S-001',
    subjectRef: 'SUBJ-001',
    useCase: 'uc1',
    useCaseLabel: 'UC1 · Biofeedback',
    importState: 'Completed',
    qcState: 'Pass',
    analysisState: 'Completed',
    reviewState: 'Pending',
    updatedAt: '2026-07-23T08:30:00',
  },
  {
    id: 'S-002',
    subjectRef: 'SUBJ-002',
    useCase: 'uc2',
    useCaseLabel: 'UC2 · Đánh giá',
    importState: 'Completed',
    qcState: 'Fail',
    analysisState: 'Abstained',
    reviewState: null,
    updatedAt: '2026-07-23T07:15:00',
  },
  {
    id: 'S-003',
    subjectRef: 'SUBJ-003',
    useCase: 'uc2',
    useCaseLabel: 'UC2 · Đánh giá',
    importState: 'Mapping required',
    qcState: null,
    analysisState: null,
    reviewState: null,
    updatedAt: '2026-07-23T06:45:00',
  },
];

function getStateBadgeVariant(state: string | null): 'success' | 'warning' | 'error' | 'abstention' | 'neutral' {
  if (!state) return 'neutral';
  switch (state.toLowerCase()) {
    case 'completed':
    case 'pass':
    case 'approved':
      return 'success';
    case 'pending':
    case 'mapping required':
    case 'warning':
      return 'warning';
    case 'fail':
    case 'failed':
    case 'rejected':
      return 'error';
    case 'abstained':
      return 'abstention';
    default:
      return 'neutral';
  }
}

export default function DashboardPage() {
  const { user } = useAuth();

  return (
    <div className="page-container">
      <div className="page-header">
        <div className="page-header__left">
          <h1 className="page-title">Tổng quan</h1>
          <p className="page-subtitle">
            Xin chào, {user?.name}. Đây là bảng điều khiển MyoLab-AI.
          </p>
        </div>
        <div className="page-header__right">
          <Link href={ROUTES.SESSION_NEW}>
            <Button icon={<Plus size={16} />}>
              Tạo phiên mới
            </Button>
          </Link>
        </div>
      </div>

      {/* Stats grid */}
      <div className={styles.statsGrid}>
        <StatCard
          icon={<ClipboardList size={20} />}
          label="Phiên đang chuẩn bị"
          value={MOCK_STATS.sessionsPreparing}
          href={ROUTES.SESSIONS}
        />
        <StatCard
          icon={<Upload size={20} />}
          label="Import cần mapping"
          value={MOCK_STATS.importsPendingMapping}
          href={ROUTES.IMPORTS}
          variant={MOCK_STATS.importsPendingMapping > 0 ? 'warning' : undefined}
        />
        <StatCard
          icon={<AlertTriangle size={20} />}
          label="QC fail / abstained"
          value={MOCK_STATS.qcFailAbstained}
          href={ROUTES.DATA_QUALITY}
          variant={MOCK_STATS.qcFailAbstained > 0 ? 'error' : undefined}
        />
        <StatCard
          icon={<BarChart3 size={20} />}
          label="Analysis đang chạy"
          value={MOCK_STATS.analysisRunning}
          href={ROUTES.ANALYSES}
        />
        <StatCard
          icon={<Clock size={20} />}
          label="Review đang chờ"
          value={MOCK_STATS.reviewPending}
          href={ROUTES.SESSIONS}
          variant={MOCK_STATS.reviewPending > 0 ? 'warning' : undefined}
        />
        <StatCard
          icon={<MessageSquare size={20} />}
          label="Feedback cần adjudication"
          value={MOCK_STATS.feedbackPendingAdjudication}
          href={ROUTES.FEEDBACK_INBOX}
        />
      </div>

      {/* Recent sessions */}
      <section className={styles.section}>
        <div className={styles.sectionHeader}>
          <h2 className={styles.sectionTitle}>Phiên đánh giá gần đây</h2>
          <Link href={ROUTES.SESSIONS} className={styles.sectionLink}>
            Xem tất cả <ArrowRight size={14} />
          </Link>
        </div>

        <div className={styles.sessionList}>
          {MOCK_RECENT_SESSIONS.map((session) => (
            <Link
              key={session.id}
              href={`/sessions/${session.id}/context`}
              className={styles.sessionCard}
            >
              <Card hoverable padding="md">
                <CardContent>
                  <div className={styles.sessionTop}>
                    <span className={styles.sessionId}>{session.id}</span>
                    <Badge variant={session.useCase === 'uc1' ? 'tier1' : 'tier1'}>
                      {session.useCaseLabel}
                    </Badge>
                  </div>
                  <div className={styles.sessionSubject}>
                    Subject: {session.subjectRef}
                  </div>
                  <div className={styles.sessionStates}>
                    <StateChip label="Import" state={session.importState} />
                    <StateChip label="QC" state={session.qcState} />
                    <StateChip label="Analysis" state={session.analysisState} />
                    <StateChip label="Review" state={session.reviewState} />
                  </div>
                </CardContent>
              </Card>
            </Link>
          ))}
        </div>
      </section>
    </div>
  );
}

function StatCard({
  icon,
  label,
  value,
  href,
  variant,
}: {
  icon: React.ReactNode;
  label: string;
  value: number;
  href: string;
  variant?: 'warning' | 'error';
}) {
  return (
    <Link href={href} className={styles.statLink}>
      <Card hoverable padding="md">
        <CardContent>
          <div className={styles.statTop}>
            <span className={[styles.statIcon, variant ? styles[`statIcon--${variant}`] : ''].filter(Boolean).join(' ')}>
              {icon}
            </span>
          </div>
          <div className={styles.statValue}>{value}</div>
          <div className={styles.statLabel}>{label}</div>
        </CardContent>
      </Card>
    </Link>
  );
}

function StateChip({ label, state }: { label: string; state: string | null }) {
  return (
    <div className={styles.stateChip}>
      <span className={styles.stateLabel}>{label}</span>
      <Badge variant={getStateBadgeVariant(state)} size="sm">
        {state || '—'}
      </Badge>
    </div>
  );
}
