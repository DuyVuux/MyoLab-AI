/**
 * Session Creation — `/sessions/new`
 * Per Section 6.4: Stepper with subject, use case, protocol, side, muscles, consent
 * Blocker: Cannot proceed without required fields
 */
'use client';

import { useState, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import * as MockSessionService from '@/services/mock/MockSessionService';
import type { SessionDraft as SchemaSessionDraft } from '@/schemas/session';
import {
  User,
  Layers,
  FileText,
  Activity,
  MapPin,
  Shield,
  ChevronRight,
  ChevronLeft,
  Check,
} from 'lucide-react';
import { Card, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Alert } from '@/components/ui/Alert';
import { Badge } from '@/components/ui/Badge';
import { useAuth } from '@/lib/auth';
import { RoleGuard } from '@/components/auth/RoleGuard';
import { USE_CASE_CONFIGS } from '@/config/useCaseRoutes';
import styles from './new-session.module.css';

interface SessionDraft {
  subjectRef: string;
  useCaseId: string;
  protocolId: string;
  protocolVersion: string;
  affectedSide: string;
  referenceSide: string;
  targetMuscles: string[];
  sessionType: string;
  operator: string;
  consentScope: string[];
  dataSourceIntent: string;
}

const INITIAL_DRAFT: SessionDraft = {
  subjectRef: '',
  useCaseId: '',
  protocolId: '',
  protocolVersion: '',
  affectedSide: '',
  referenceSide: '',
  targetMuscles: [],
  sessionType: 'baseline',
  operator: '',
  consentScope: [],
  dataSourceIntent: '',
};

const STEPS = [
  { id: 'subject', label: 'Đối tượng', icon: User },
  { id: 'usecase', label: 'Use Case & Protocol', icon: Layers },
  { id: 'setup', label: 'Cấu hình', icon: Activity },
  { id: 'consent', label: 'Đồng thuận', icon: Shield },
  { id: 'confirm', label: 'Xác nhận', icon: Check },
];

// ASSUMPTION: Mock protocols per Section 6.4
const MOCK_PROTOCOLS = [
  { id: 'PROT-UC1-001', name: 'Gesture Recognition Standard', version: '1.2', useCases: ['uc1'] },
  { id: 'PROT-UC1-002', name: 'Biofeedback Simplified', version: '1.0', useCases: ['uc1'] },
  { id: 'PROT-UC2-001', name: 'Upper Limb Assessment Full', version: '2.0', useCases: ['uc2'] },
  { id: 'PROT-UC2-002', name: 'Fatigue Monitoring Basic', version: '1.1', useCases: ['uc2'] },
  { id: 'PROT-UC3-001', name: 'Prosthetic Feasibility', version: '0.5', useCases: ['uc3'] },
  { id: 'PROT-UC4-001', name: 'Sterile HMI Feasibility', version: '0.3', useCases: ['uc4'] },
];

const MOCK_MUSCLES = [
  'Flexor carpi radialis',
  'Extensor carpi radialis',
  'Biceps brachii',
  'Upper trapezius',
  'Flexor digitorum superficialis',
  'Extensor digitorum communis',
  'Deltoid (anterior)',
  'Triceps brachii',
];

const DEMO_SUBJECTS = ['SUBJ-001', 'SUBJ-002', 'SUBJ-003', 'DEMO-001', 'DEMO-002'];

export default function NewSessionPage() {
  const router = useRouter();
  const { user } = useAuth();
  const [step, setStep] = useState(0);
  const [draft, setDraft] = useState<SessionDraft>({
    ...INITIAL_DRAFT,
    operator: user?.id || '',
  });
  const [errors, setErrors] = useState<Partial<Record<keyof SessionDraft, string>>>({});

  const updateDraft = useCallback((key: keyof SessionDraft, value: string | string[]) => {
    setDraft((prev) => ({ ...prev, [key]: value }));
    setErrors((prev) => ({ ...prev, [key]: undefined }));
  }, []);

  const compatibleProtocols = MOCK_PROTOCOLS.filter((p) =>
    p.useCases.includes(draft.useCaseId)
  );

  const validateStep = (stepIndex: number): boolean => {
    const newErrors: Partial<Record<keyof SessionDraft, string>> = {};

    if (stepIndex === 0) {
      if (!draft.subjectRef.trim()) newErrors.subjectRef = 'Vui lòng chọn hoặc nhập mã đối tượng.';
    }
    if (stepIndex === 1) {
      if (!draft.useCaseId) newErrors.useCaseId = 'Vui lòng chọn use case.';
      if (!draft.protocolId) newErrors.protocolId = 'Vui lòng chọn protocol.';
    }
    if (stepIndex === 2) {
      if (!draft.affectedSide) newErrors.affectedSide = 'Vui lòng chọn bên ảnh hưởng.';
      if (draft.targetMuscles.length === 0) newErrors.targetMuscles = 'Vui lòng chọn ít nhất 1 cơ.';
    }
    if (stepIndex === 3) {
      if (draft.consentScope.length === 0) newErrors.consentScope = 'Vui lòng xác nhận phạm vi đồng thuận.';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleNext = () => {
    if (validateStep(step)) {
      setStep((s) => Math.min(s + 1, STEPS.length - 1));
    }
  };

  const handleBack = () => setStep((s) => Math.max(s - 1, 0));

  const handleCreate = () => {
    const schemaDraft: SchemaSessionDraft = {
      subjectRef: draft.subjectRef,
      useCaseId: draft.useCaseId as SchemaSessionDraft['useCaseId'],
      protocolId: draft.protocolId,
      protocolVersion: draft.protocolVersion,
      affectedSide: (draft.affectedSide || 'Left') as SchemaSessionDraft['affectedSide'],
      referenceSide: (draft.referenceSide || 'Right') as SchemaSessionDraft['referenceSide'],
      targetMuscles: draft.targetMuscles,
      sessionType: (draft.sessionType || 'baseline') as SchemaSessionDraft['sessionType'],
      operator: draft.operator || user?.id || 'Unknown',
      consentScope: draft.consentScope as SchemaSessionDraft['consentScope'],
      dataSourceIntent: (draft.dataSourceIntent || undefined) as SchemaSessionDraft['dataSourceIntent'],
    };
    const created = MockSessionService.createSession(schemaDraft);
    router.push(`/sessions/${created.sessionId}/context`);
  };

  return (
    <RoleGuard allowedRoles={['ktv', 'admin']}>
      <div className="page-container">
        <div className="page-header">
          <div className="page-header__left">
            <h1 className="page-title">Tạo phiên đánh giá mới</h1>
            <p className="page-subtitle">Thiết lập thông tin phiên trước khi import dữ liệu.</p>
          </div>
        </div>

        {/* Stepper */}
        <div className={styles.stepper}>
          {STEPS.map((s, i) => {
            const Icon = s.icon;
            const isActive = i === step;
            const isCompleted = i < step;
            return (
              <div
                key={s.id}
                className={[
                  styles.stepItem,
                  isActive ? styles['stepItem--active'] : '',
                  isCompleted ? styles['stepItem--completed'] : '',
                ].filter(Boolean).join(' ')}
              >
                <div className={styles.stepIcon}>
                  {isCompleted ? <Check size={16} /> : <Icon size={16} />}
                </div>
                <span className={styles.stepLabel}>{s.label}</span>
                {i < STEPS.length - 1 && <div className={styles.stepConnector} />}
              </div>
            );
          })}
        </div>

        {/* Step content */}
        <Card padding="lg">
          <CardContent>
            {/* Step 0: Subject */}
            {step === 0 && (
              <div className={styles.stepContent}>
                <h2 className={styles.stepTitle}>Chọn hoặc tạo đối tượng</h2>
                <p className={styles.stepDesc}>Chọn đối tượng demo hoặc nhập mã pseudonymous mới.</p>

                <div className={styles.subjectOptions}>
                  {DEMO_SUBJECTS.map((subj) => (
                    <button
                      key={subj}
                      className={[
                        styles.subjectChip,
                        draft.subjectRef === subj ? styles['subjectChip--active'] : '',
                      ].filter(Boolean).join(' ')}
                      onClick={() => updateDraft('subjectRef', subj)}
                    >
                      {subj}
                  </button>
                ))}
              </div>

              <Input
                label="Hoặc nhập mã đối tượng mới"
                value={draft.subjectRef}
                onChange={(e) => updateDraft('subjectRef', e.target.value)}
                placeholder="VD: SUBJ-NEW-001"
                error={errors.subjectRef}
                hint="Mã ẩn danh — không nhập tên hoặc thông tin nhận diện."
              />
            </div>
          )}

          {/* Step 1: Use Case & Protocol */}
          {step === 1 && (
            <div className={styles.stepContent}>
              <h2 className={styles.stepTitle}>Chọn Use Case và Protocol</h2>

              <div className={styles.ucGrid}>
                {USE_CASE_CONFIGS.map((uc) => (
                  <button
                    key={uc.id}
                    className={[
                      styles.ucOption,
                      draft.useCaseId === uc.id ? styles['ucOption--active'] : '',
                    ].filter(Boolean).join(' ')}
                    onClick={() => {
                      updateDraft('useCaseId', uc.id);
                      updateDraft('protocolId', '');
                    }}
                  >
                    <Badge variant={uc.tier === 1 ? 'tier1' : 'tier2'} size="sm">
                      Tầng {uc.tier}
                    </Badge>
                    <div className={styles.ucOptionName}>{uc.name}</div>
                  </button>
                ))}
              </div>
              {errors.useCaseId && <p className={styles.fieldError}>{errors.useCaseId}</p>}

              {draft.useCaseId && (
                <>
                  <h3 className={styles.subTitle}>Protocol tương thích</h3>
                  {compatibleProtocols.length === 0 ? (
                    <Alert variant="warning">Không có protocol tương thích cho use case đã chọn.</Alert>
                  ) : (
                    <div className={styles.protocolList}>
                      {compatibleProtocols.map((p) => (
                        <button
                          key={p.id}
                          className={[
                            styles.protocolOption,
                            draft.protocolId === p.id ? styles['protocolOption--active'] : '',
                          ].filter(Boolean).join(' ')}
                          onClick={() => {
                            updateDraft('protocolId', p.id);
                            updateDraft('protocolVersion', p.version);
                          }}
                        >
                          <div>{p.name}</div>
                          <Badge variant="neutral" size="sm">v{p.version}</Badge>
                        </button>
                      ))}
                    </div>
                  )}
                  {errors.protocolId && <p className={styles.fieldError}>{errors.protocolId}</p>}
                </>
              )}
            </div>
          )}

          {/* Step 2: Setup */}
          {step === 2 && (
            <div className={styles.stepContent}>
              <h2 className={styles.stepTitle}>Cấu hình phiên</h2>

              <div className={styles.formGrid}>
                <div>
                  <label className={styles.fieldLabel}>Bên ảnh hưởng *</label>
                  <div className={styles.sideOptions}>
                    {['Left', 'Right', 'Bilateral'].map((side) => (
                      <button
                        key={side}
                        className={[
                          styles.sideBtn,
                          draft.affectedSide === side ? styles['sideBtn--active'] : '',
                        ].filter(Boolean).join(' ')}
                        onClick={() => {
                          updateDraft('affectedSide', side);
                          updateDraft('referenceSide', side === 'Left' ? 'Right' : side === 'Right' ? 'Left' : 'Bilateral');
                        }}
                      >
                        {side === 'Left' ? 'Trái' : side === 'Right' ? 'Phải' : 'Hai bên'}
                      </button>
                    ))}
                  </div>
                  {errors.affectedSide && <p className={styles.fieldError}>{errors.affectedSide}</p>}
                </div>

                <div>
                  <label className={styles.fieldLabel}>Loại phiên</label>
                  <div className={styles.sideOptions}>
                    {[
                      { value: 'baseline', label: 'Baseline' },
                      { value: 'follow_up', label: 'Follow-up' },
                      { value: 'replay', label: 'Replay' },
                      { value: 'research', label: 'Research' },
                    ].map((opt) => (
                      <button
                        key={opt.value}
                        className={[
                          styles.sideBtn,
                          draft.sessionType === opt.value ? styles['sideBtn--active'] : '',
                        ].filter(Boolean).join(' ')}
                        onClick={() => updateDraft('sessionType', opt.value)}
                      >
                        {opt.label}
                      </button>
                    ))}
                  </div>
                </div>
              </div>

              <div>
                <label className={styles.fieldLabel}>Cơ mục tiêu *</label>
                <div className={styles.muscleGrid}>
                  {MOCK_MUSCLES.map((m) => (
                    <button
                      key={m}
                      className={[
                        styles.muscleChip,
                        draft.targetMuscles.includes(m) ? styles['muscleChip--active'] : '',
                      ].filter(Boolean).join(' ')}
                      onClick={() => {
                        const updated = draft.targetMuscles.includes(m)
                          ? draft.targetMuscles.filter((x) => x !== m)
                          : [...draft.targetMuscles, m];
                        updateDraft('targetMuscles', updated);
                      }}
                    >
                      {m}
                    </button>
                  ))}
                </div>
                {errors.targetMuscles && <p className={styles.fieldError}>{errors.targetMuscles}</p>}
              </div>
            </div>
          )}

          {/* Step 3: Consent */}
          {step === 3 && (
            <div className={styles.stepContent}>
              <h2 className={styles.stepTitle}>Phạm vi đồng thuận</h2>
              <p className={styles.stepDesc}>
                Xác nhận phạm vi sử dụng dữ liệu trong phiên này.
              </p>

              {['quality_improvement', 'model_training', 'research_export'].map((scope) => {
                const labels: Record<string, { title: string; desc: string }> = {
                  quality_improvement: {
                    title: 'Cải thiện chất lượng',
                    desc: 'Dữ liệu có thể được sử dụng để đánh giá và cải thiện quy trình.',
                  },
                  model_training: {
                    title: 'Huấn luyện model',
                    desc: 'Dữ liệu de-identified có thể trở thành training candidate sau adjudication.',
                  },
                  research_export: {
                    title: 'Xuất nghiên cứu',
                    desc: 'Dữ liệu de-identified có thể được xuất cho mục đích nghiên cứu.',
                  },
                };
                const info = labels[scope];
                const isChecked = draft.consentScope.includes(scope);

                return (
                  <label key={scope} className={styles.consentItem}>
                    <input
                      type="checkbox"
                      checked={isChecked}
                      onChange={() => {
                        const updated = isChecked
                          ? draft.consentScope.filter((s) => s !== scope)
                          : [...draft.consentScope, scope];
                        updateDraft('consentScope', updated);
                      }}
                      className={styles.checkbox}
                    />
                    <div>
                      <div className={styles.consentTitle}>{info.title}</div>
                      <div className={styles.consentDesc}>{info.desc}</div>
                    </div>
                  </label>
                );
              })}
              {errors.consentScope && <p className={styles.fieldError}>{errors.consentScope}</p>}

              <Alert variant="info">
                model_training mặc định không được chọn nếu chưa có đồng thuận rõ ràng.
              </Alert>
            </div>
          )}

          {/* Step 4: Confirm */}
          {step === 4 && (
            <div className={styles.stepContent}>
              <h2 className={styles.stepTitle}>Xác nhận thông tin phiên</h2>

              <div className={styles.summaryGrid}>
                <SummaryRow label="Đối tượng" value={draft.subjectRef} />
                <SummaryRow label="Use Case" value={USE_CASE_CONFIGS.find(u => u.id === draft.useCaseId)?.name || draft.useCaseId} />
                <SummaryRow label="Protocol" value={`${MOCK_PROTOCOLS.find(p => p.id === draft.protocolId)?.name || draft.protocolId} (v${draft.protocolVersion})`} />
                <SummaryRow label="Bên ảnh hưởng" value={draft.affectedSide} />
                <SummaryRow label="Loại phiên" value={draft.sessionType} />
                <SummaryRow label="Cơ mục tiêu" value={draft.targetMuscles.join(', ')} />
                <SummaryRow label="Đồng thuận" value={draft.consentScope.join(', ')} />
                <SummaryRow label="Operator" value={user?.name || draft.operator} />
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Navigation buttons */}
      <div className={styles.actions}>
        {step > 0 && (
          <Button variant="secondary" onClick={handleBack} icon={<ChevronLeft size={16} />}>
            Quay lại
          </Button>
        )}
        <div className={styles.spacer} />
        {step < STEPS.length - 1 ? (
          <Button onClick={handleNext} icon={<ChevronRight size={16} />} iconPosition="right">
            Tiếp theo
          </Button>
        ) : (
          <Button onClick={handleCreate} icon={<Check size={16} />}>
            Tạo phiên
          </Button>
        )}
      </div>
      </div>
    </RoleGuard>
  );
}

function SummaryRow({ label, value }: { label: string; value: string }) {
  return (
    <div className={styles.summaryRow}>
      <dt className={styles.summaryLabel}>{label}</dt>
      <dd className={styles.summaryValue}>{value || '—'}</dd>
    </div>
  );
}
