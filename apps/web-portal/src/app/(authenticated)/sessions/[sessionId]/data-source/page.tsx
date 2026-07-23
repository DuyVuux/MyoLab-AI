/**
 * Data Source Selector — `/sessions/[sessionId]/data-source`
 * Different navigation branches per source type.
 * Live stream: DISABLED (feature flag, does NOT enter Import Center).
 */
'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { Database, FileText, RefreshCw, Radio, TestTube2, ArrowRight, ArrowLeft, Lock } from 'lucide-react';
import { Card, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { Alert } from '@/components/ui/Alert';
import type { DataSourceType } from '@/schemas/common';
import type { SessionContext } from '@/schemas/session';
import * as SessionService from '@/services/mock/MockSessionService';
import * as ImportService from '@/services/mock/MockImportService';
import { syntheticHash } from '@/services/mock/MockImportService';
import { createImportFixture, createMappingFixture } from '@/services/mock/fixtures';
import * as SignalService from '@/services/mock/MockSignalWorkflowService';
import * as repo from '@/services/mock/MockWorkflowRepository';
import styles from './data-source.module.css';

interface SourceOption {
  type: DataSourceType;
  title: string;
  description: string;
  icon: React.ElementType;
  disabled: boolean;
  disabledReason?: string;
  navigatesTo: 'import' | 'synthetic' | 'disabled';
}

const SOURCES: SourceOption[] = [
  { type: 'synthetic', title: 'Dữ liệu Synthetic (Demo)', description: 'Tạo dữ liệu mô phỏng ngay lập tức. Không cần file thật. Phù hợp để thử nghiệm luồng.', icon: TestTube2, disabled: false, navigatesTo: 'synthetic' },
  { type: 'csv_json', title: 'CSV + JSON Manifest', description: 'Import file CSV dữ liệu sEMG kèm JSON manifest chứa metadata. Định dạng generic.', icon: FileText, disabled: false, navigatesTo: 'import' },
  { type: 'noraxon_mock', title: 'Noraxon / myoRESEARCH Export', description: 'Import file export từ phần mềm Noraxon myoRESEARCH. Tự động detect format.', icon: Database, disabled: false, navigatesTo: 'import' },
  { type: 'deidentified_replay', title: 'De-identified Offline Replay', description: 'Replay dữ liệu đã de-identified từ phiên trước. Chỉ đọc, không sửa đổi.', icon: RefreshCw, disabled: false, navigatesTo: 'import' },
  { type: 'live_stream', title: 'Live Stream (Chưa tích hợp)', description: 'Kết nối trực tiếp với thiết bị sEMG. Chức năng này chưa tích hợp trong prototype.', icon: Radio, disabled: true, disabledReason: 'Chưa tích hợp — cần hardware adapter và protocol kết nối thực.', navigatesTo: 'disabled' },
];

export default function DataSourcePage() {
  const params = useParams();
  const router = useRouter();
  const sessionId = params.sessionId as string;

  const [session, setSession] = useState<SessionContext | null>(null);
  const [selected, setSelected] = useState<DataSourceType | ''>('');
  const [loading, setLoading] = useState(true);
  const [processing, setProcessing] = useState(false);

  useEffect(() => {
    const ctx = SessionService.getSession(sessionId);
    if (!ctx) {
      router.replace(`/sessions/${sessionId}/context`);
      return;
    }
    // Route guard: must have confirmed context
    if (ctx.state === 'draft') {
      router.replace(`/sessions/${sessionId}/context`);
      return;
    }
    setSession(ctx);
    if (ctx.dataSourceIntent) setSelected(ctx.dataSourceIntent);
    setLoading(false);
  }, [sessionId, router]);

  const handleSelect = (type: DataSourceType) => {
    const source = SOURCES.find((s) => s.type === type);
    if (source?.disabled) return;
    setSelected(type);
  };

  const handleContinue = async () => {
    if (!selected || !session) return;
    setProcessing(true);

    SessionService.setDataSource(sessionId, selected);
    const source = SOURCES.find((s) => s.type === selected);

    if (source?.navigatesTo === 'synthetic') {
      // Generate synthetic fixture → skip file upload → auto-map → go to mapping
      const hash = syntheticHash(`synthetic-${sessionId}`);
      const imp = ImportService.createImport(sessionId, 'synthetic_emg_4ch_60s.csv', 245760, 'text/csv', 'synthetic', hash);
      await ImportService.simulateImportPipeline(imp.importId, 'happy_path');

      // Auto-initialize mappings
      SignalService.initializeMappings(sessionId, 4, 'happy_path');
      repo.updateSessionState(sessionId, 'import_complete');

      setProcessing(false);
      router.push(`/sessions/${sessionId}/mapping`);
    } else if (source?.navigatesTo === 'import') {
      setProcessing(false);
      router.push(`/sessions/${sessionId}/import`);
    }
  };

  if (loading) return <div className="page-container"><p>Đang tải...</p></div>;

  return (
    <div className="page-container">
      <div className="page-header">
        <div className="page-header__left">
          <h1 className="page-title">Chọn nguồn dữ liệu</h1>
          <p className="page-subtitle">Session: <code>{sessionId}</code> — Chọn phương thức nhập dữ liệu sEMG.</p>
        </div>
      </div>

      <div className={styles.sourceGrid}>
        {SOURCES.map((source) => {
          const Icon = source.icon;
          const isSelected = selected === source.type;
          return (
            <button
              key={source.type}
              className={[
                styles.sourceCard,
                isSelected ? styles['sourceCard--active'] : '',
                source.disabled ? styles['sourceCard--disabled'] : '',
              ].filter(Boolean).join(' ')}
              onClick={() => handleSelect(source.type)}
              disabled={source.disabled}
              aria-label={source.title}
            >
              <div className={styles.sourceIcon}>
                {source.disabled ? <Lock size={24} /> : <Icon size={24} />}
              </div>
              <div className={styles.sourceContent}>
                <div className={styles.sourceTitle}>
                  {source.title}
                  {source.type === 'synthetic' && <Badge variant="info" size="sm">Nhanh</Badge>}
                </div>
                <p className={styles.sourceDesc}>{source.description}</p>
                {source.disabledReason && (
                  <Alert variant="warning" title="">{source.disabledReason}</Alert>
                )}
              </div>
            </button>
          );
        })}
      </div>

      <div className={styles.actions}>
        <Button variant="ghost" onClick={() => router.push(`/sessions/${sessionId}/context`)} icon={<ArrowLeft size={16} />}>Quay lại Context</Button>
        <div className={styles.spacer} />
        <Button onClick={handleContinue} disabled={!selected || processing} icon={<ArrowRight size={16} />} iconPosition="right">
          {processing ? 'Đang xử lý...' : selected === 'synthetic' ? 'Tạo synthetic → Mapping' : 'Tiếp tục → Import'}
        </Button>
      </div>
    </div>
  );
}
