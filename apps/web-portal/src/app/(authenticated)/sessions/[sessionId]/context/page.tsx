/**
 * Session Context — `/sessions/[sessionId]/context`
 * Pre-populated from session creation. All required fields must be confirmed.
 * Navigation: → Data Source only when valid.
 */
'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { CheckCircle, AlertTriangle, ArrowRight, Save } from 'lucide-react';
import { Card, CardContent, CardHeader } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Badge } from '@/components/ui/Badge';
import { Alert } from '@/components/ui/Alert';
import { useAuth } from '@/lib/auth';
import { validateSessionContext } from '@/schemas/session';
import type { SessionContext as SessionContextType, SessionDraft } from '@/schemas/session';
import type { Side, ConsentScope, ElectrodeLayout, ElectrodePosition } from '@/schemas/common';
import { CANONICAL_MUSCLES } from '@/schemas/common';
import { USE_CASE_CONFIGS } from '@/config/useCaseRoutes';
import * as SessionService from '@/services/mock/MockSessionService';
import { createSessionFixture } from '@/services/mock/fixtures';
import * as repo from '@/services/mock/MockWorkflowRepository';
import styles from './context.module.css';

const MOCK_PROTOCOLS = [
  { id: 'PROT-UC1-001', name: 'Gesture Recognition Standard', version: '1.2', useCases: ['uc1'] },
  { id: 'PROT-UC1-002', name: 'Biofeedback Simplified', version: '1.0', useCases: ['uc1'] },
  { id: 'PROT-UC2-001', name: 'Upper Limb Assessment Full', version: '2.0', useCases: ['uc2'] },
  { id: 'PROT-UC2-002', name: 'Fatigue Monitoring Basic', version: '1.1', useCases: ['uc2'] },
  { id: 'PROT-UC3-001', name: 'Prosthetic Feasibility', version: '0.5', useCases: ['uc3'] },
  { id: 'PROT-UC4-001', name: 'Sterile HMI Feasibility', version: '0.3', useCases: ['uc4'] },
];

export default function SessionContextPage() {
  const params = useParams();
  const router = useRouter();
  const { user } = useAuth();
  const sessionId = params.sessionId as string;

  const [session, setSession] = useState<SessionContextType | null>(null);
  const [loading, setLoading] = useState(true);
  const [errors, setErrors] = useState<Partial<Record<keyof SessionDraft, string>>>({});
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    let ctx = SessionService.getSession(sessionId);
    if (!ctx) {
      // Auto-create from fixture for demo
      const fixture = createSessionFixture('happy_path', sessionId);
      ctx = repo.createSession(fixture);
    }
    setSession(ctx);
    setLoading(false);
  }, [sessionId]);

  if (loading) return <div className="page-container"><p>Đang tải...</p></div>;
  if (!session) return <div className="page-container"><Alert variant="error" title="Không tìm thấy session">Session ID: {sessionId}</Alert></div>;

  const updateField = <K extends keyof SessionContextType>(key: K, value: SessionContextType[K]) => {
    setSession((prev) => prev ? { ...prev, [key]: value } : prev);
    setErrors((prev) => ({ ...prev, [key]: undefined }));
    setSaved(false);
  };

  const toggleMuscle = (muscle: string) => {
    const current = session.targetMuscles;
    const updated = current.includes(muscle) ? current.filter((m) => m !== muscle) : [...current, muscle];
    updateField('targetMuscles', updated);
  };

  const toggleConsent = (scope: ConsentScope) => {
    const current = session.consentScope;
    const updated = current.includes(scope) ? current.filter((s) => s !== scope) : [...current, scope];
    updateField('consentScope', updated);
  };

  const handleSave = () => {
    const validation = validateSessionContext(session);
    if (!validation.valid) {
      setErrors(validation.errors);
      return;
    }
    SessionService.confirmContext(sessionId, session);
    setSaved(true);
    setErrors({});
  };

  const handleContinue = () => {
    const validation = validateSessionContext(session);
    if (!validation.valid) {
      setErrors(validation.errors);
      return;
    }
    if (!saved) handleSave();
    router.push(`/sessions/${sessionId}/data-source`);
  };

  const compatibleProtocols = MOCK_PROTOCOLS.filter((p) => p.useCases.includes(session.useCaseId));
  const isConfirmed = session.state !== 'draft';

  return (
    <div className="page-container">
      <div className="page-header">
        <div className="page-header__left">
          <h1 className="page-title">Context phiên đánh giá</h1>
          <p className="page-subtitle">Xác nhận thông tin trước khi import dữ liệu. Session: <code>{sessionId}</code></p>
        </div>
        <div className="page-header__right">
          {isConfirmed && <Badge variant="success" icon={<CheckCircle size={12} />}>Đã xác nhận</Badge>}
        </div>
      </div>

      {/* Subject */}
      <Card padding="md">
        <CardHeader><h2 className={styles.sectionTitle}>Đối tượng</h2></CardHeader>
        <CardContent>
          <Input
            label="Mã đối tượng (pseudonymous) *"
            value={session.subjectRef}
            onChange={(e) => updateField('subjectRef', e.target.value)}
            error={errors.subjectRef}
            hint="Mã ẩn danh — không nhập tên hoặc thông tin nhận diện."
          />
          <div className={styles.fieldRow}>
            <div className={styles.fieldGroup}>
              <label className={styles.label}>Loại phiên</label>
              <div className={styles.chipRow}>
                {(['baseline', 'follow_up', 'replay', 'research'] as const).map((t) => (
                  <button key={t} className={[styles.chip, session.sessionType === t ? styles['chip--active'] : ''].filter(Boolean).join(' ')} onClick={() => updateField('sessionType', t)}>
                    {t === 'baseline' ? 'Baseline' : t === 'follow_up' ? 'Follow-up' : t === 'replay' ? 'Replay' : 'Research'}
                  </button>
                ))}
              </div>
            </div>
            <Input label="Operator" value={session.operator} onChange={(e) => updateField('operator', e.target.value)} />
          </div>
        </CardContent>
      </Card>

      {/* Use Case + Protocol */}
      <Card padding="md">
        <CardHeader><h2 className={styles.sectionTitle}>Use Case & Protocol *</h2></CardHeader>
        <CardContent>
          <div className={styles.ucGrid}>
            {USE_CASE_CONFIGS.map((uc) => (
              <button key={uc.id} className={[styles.ucCard, session.useCaseId === uc.id ? styles['ucCard--active'] : ''].filter(Boolean).join(' ')} onClick={() => { updateField('useCaseId', uc.id); updateField('protocolId', ''); }}>
                <Badge variant={uc.tier === 1 ? 'tier1' : 'tier2'} size="sm">Tầng {uc.tier}</Badge>
                <div className={styles.ucName}>{uc.name}</div>
              </button>
            ))}
          </div>
          {errors.useCaseId && <p className={styles.error}>{errors.useCaseId}</p>}

          {session.useCaseId && (
            <div className={styles.protocolList}>
              <label className={styles.label}>Protocol tương thích *</label>
              {compatibleProtocols.map((p) => (
                <button key={p.id} className={[styles.protocolItem, session.protocolId === p.id ? styles['protocolItem--active'] : ''].filter(Boolean).join(' ')} onClick={() => { updateField('protocolId', p.id); updateField('protocolVersion', p.version); }}>
                  <span>{p.name}</span>
                  <Badge variant="neutral" size="sm">v{p.version}</Badge>
                </button>
              ))}
              {errors.protocolId && <p className={styles.error}>{errors.protocolId}</p>}
              {session.protocolId && (
                <div className={styles.calNote}>
                  {session.requiresCalibration
                    ? <Badge variant="warning" size="sm">Yêu cầu Calibration</Badge>
                    : <Badge variant="neutral" size="sm">Không yêu cầu Calibration</Badge>}
                </div>
              )}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Side + Muscles */}
      <Card padding="md">
        <CardHeader><h2 className={styles.sectionTitle}>Cấu hình *</h2></CardHeader>
        <CardContent>
          <div className={styles.fieldRow}>
            <div className={styles.fieldGroup}>
              <label className={styles.label}>Bên ảnh hưởng *</label>
              <div className={styles.chipRow}>
                {(['Left', 'Right', 'Bilateral'] as Side[]).map((s) => (
                  <button key={s} className={[styles.chip, session.affectedSide === s ? styles['chip--active'] : ''].filter(Boolean).join(' ')} onClick={() => { updateField('affectedSide', s); updateField('referenceSide', s === 'Left' ? 'Right' : s === 'Right' ? 'Left' : 'Bilateral'); }}>
                    {s === 'Left' ? 'Trái' : s === 'Right' ? 'Phải' : 'Hai bên'}
                  </button>
                ))}
              </div>
              {errors.affectedSide && <p className={styles.error}>{errors.affectedSide}</p>}
            </div>
            <div className={styles.fieldGroup}>
              <label className={styles.label}>Bên tham chiếu</label>
              <Badge variant="neutral">{session.referenceSide || '—'}</Badge>
            </div>
          </div>

          <label className={styles.label}>Cơ mục tiêu * (chọn ≥ 1)</label>
          <div className={styles.muscleGrid}>
            {CANONICAL_MUSCLES.map((m) => (
              <button key={m} className={[styles.muscleChip, session.targetMuscles.includes(m) ? styles['muscleChip--active'] : ''].filter(Boolean).join(' ')} onClick={() => toggleMuscle(m)}>
                {m}
              </button>
            ))}
          </div>
          {errors.targetMuscles && <p className={styles.error}>{errors.targetMuscles}</p>}
        </CardContent>
      </Card>

      {/* Consent */}
      <Card padding="md">
        <CardHeader><h2 className={styles.sectionTitle}>Phạm vi đồng thuận *</h2></CardHeader>
        <CardContent>
          {([
            { scope: 'quality_improvement' as ConsentScope, title: 'Cải thiện chất lượng', desc: 'Dữ liệu có thể được sử dụng để đánh giá và cải thiện quy trình.' },
            { scope: 'model_training' as ConsentScope, title: 'Huấn luyện model', desc: 'Dữ liệu de-identified có thể trở thành training candidate sau adjudication.' },
            { scope: 'research_export' as ConsentScope, title: 'Xuất nghiên cứu', desc: 'Dữ liệu de-identified có thể được xuất cho mục đích nghiên cứu.' },
          ]).map((item) => (
            <label key={item.scope} className={styles.consentItem}>
              <input type="checkbox" checked={session.consentScope.includes(item.scope)} onChange={() => toggleConsent(item.scope)} className={styles.checkbox} />
              <div>
                <div className={styles.consentTitle}>{item.title}</div>
                <div className={styles.consentDesc}>{item.desc}</div>
              </div>
            </label>
          ))}
          {errors.consentScope && <p className={styles.error}>{errors.consentScope}</p>}
        </CardContent>
      </Card>

      {/* Actions */}
      <div className={styles.actions}>
        <Button variant="secondary" onClick={handleSave} icon={<Save size={16} />}>Lưu context</Button>
        {saved && <Badge variant="success">Đã lưu</Badge>}
        <div className={styles.spacer} />
        <Button onClick={handleContinue} icon={<ArrowRight size={16} />} iconPosition="right">
          Tiếp tục → Chọn nguồn dữ liệu
        </Button>
      </div>
    </div>
  );
}
