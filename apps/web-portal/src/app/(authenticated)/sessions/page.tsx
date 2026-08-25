/**
 * Session List — `/sessions`
 * Per Section 6.3: Table/card list with filters
 */
'use client';

import { useState } from 'react';
import Link from 'next/link';
import { Plus, Search, UploadCloud } from 'lucide-react';
import { Card, CardContent } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { ROUTES } from '@/config/useCaseRoutes';
import styles from './sessions.module.css';

// ASSUMPTION: Mock data per Section 17
interface SessionListItem {
  id: string;
  subjectRef: string;
  useCase: string;
  useCaseLabel: string;
  sourceType: string;
  importState: string;
  qcState: string | null;
  analysisState: string | null;
  reviewState: string | null;
  action: string;
  actionHref: string;
  updatedAt: string;
}

const MOCK_SESSIONS: SessionListItem[] = [
  {
    id: 'S-001', subjectRef: 'SUBJ-001', useCase: 'uc1', useCaseLabel: 'UC1',
    sourceType: 'Synthetic', importState: 'Completed', qcState: 'Pass',
    analysisState: 'Completed', reviewState: 'Pending', action: 'Review',
    actionHref: '/sessions/S-001/review', updatedAt: '2026-07-23',
  },
  {
    id: 'S-002', subjectRef: 'SUBJ-002', useCase: 'uc2', useCaseLabel: 'UC2',
    sourceType: 'CSV', importState: 'Completed', qcState: 'Fail',
    analysisState: 'Abstained', reviewState: null, action: 'Đo lại',
    actionHref: '/sessions/S-002/quality', updatedAt: '2026-07-23',
  },
  {
    id: 'S-003', subjectRef: 'SUBJ-003', useCase: 'uc2', useCaseLabel: 'UC2',
    sourceType: 'Noraxon mock', importState: 'Mapping required', qcState: null,
    analysisState: null, reviewState: null, action: 'Mapping',
    actionHref: '/sessions/S-003/mapping', updatedAt: '2026-07-22',
  },
  {
    id: 'S-004', subjectRef: 'DEMO-004', useCase: 'uc1', useCaseLabel: 'UC1',
    sourceType: 'Synthetic', importState: 'Upload failed', qcState: null,
    analysisState: null, reviewState: null, action: 'Thử lại',
    actionHref: '/sessions/S-004/import', updatedAt: '2026-07-22',
  },
];

function getStateVariant(state: string | null) {
  if (!state) return 'neutral' as const;
  const s = state.toLowerCase();
  if (['completed', 'pass', 'approved'].includes(s)) return 'success' as const;
  if (['pending', 'mapping required', 'warning'].includes(s)) return 'warning' as const;
  if (['fail', 'failed', 'rejected', 'upload failed'].includes(s)) return 'error' as const;
  if (s === 'abstained') return 'abstention' as const;
  return 'neutral' as const;
}

export default function SessionsPage() {
  const [search, setSearch] = useState('');

  const filtered = MOCK_SESSIONS.filter(
    (s) =>
      s.id.toLowerCase().includes(search.toLowerCase()) ||
      s.subjectRef.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="page-container">
      <div className="page-header">
        <div className="page-header__left">
          <h1 className="page-title">Phiên đánh giá</h1>
          <p className="page-subtitle">Quản lý và theo dõi tất cả các phiên đánh giá sEMG.</p>
        </div>
        <div className="page-header__right">
          <Link href="/sessions/auto-intake">
            <Button variant="secondary" icon={<UploadCloud size={16} />}>Auto intake</Button>
          </Link>
          <Link href={ROUTES.SESSION_NEW}>
            <Button icon={<Plus size={16} />}>Tạo phiên mới</Button>
          </Link>
        </div>
      </div>

      {/* Filters */}
      <div className={styles.filters}>
        <div className={styles.searchWrap}>
          <Search size={16} className={styles.searchIcon} />
          <input
            type="search"
            placeholder="Tìm theo Session ID hoặc Subject..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className={styles.searchInput}
            aria-label="Tìm kiếm phiên"
          />
        </div>
      </div>

      {/* Session table */}
      <div className={styles.tableWrap}>
        <table className={styles.table}>
          <thead>
            <tr>
              <th>Session</th>
              <th>Subject</th>
              <th>Use Case</th>
              <th>Import</th>
              <th>QC</th>
              <th>Analysis</th>
              <th>Review</th>
              <th>Hành động</th>
            </tr>
          </thead>
          <tbody>
            {filtered.map((s) => (
              <tr key={s.id}>
                <td>
                  <Link href={`/sessions/${s.id}/context`} className={styles.sessionLink}>
                    {s.id}
                  </Link>
                </td>
                <td>{s.subjectRef}</td>
                <td><Badge variant={s.useCase.includes('uc1') ? 'tier1' : 'tier1'}>{s.useCaseLabel}</Badge></td>
                <td><Badge variant={getStateVariant(s.importState)} size="sm">{s.importState}</Badge></td>
                <td><Badge variant={getStateVariant(s.qcState)} size="sm">{s.qcState || '—'}</Badge></td>
                <td><Badge variant={getStateVariant(s.analysisState)} size="sm">{s.analysisState || '—'}</Badge></td>
                <td><Badge variant={getStateVariant(s.reviewState)} size="sm">{s.reviewState || '—'}</Badge></td>
                <td>
                  <Link href={s.actionHref}>
                    <Button variant="ghost" size="sm">{s.action}</Button>
                  </Link>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {filtered.length === 0 && (
        <div className={styles.empty}>
          <p>Không tìm thấy phiên nào phù hợp.</p>
        </div>
      )}
    </div>
  );
}
