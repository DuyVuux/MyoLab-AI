/**
 * Channel Mapping — `/sessions/[sessionId]/mapping`
 * Maps: source channel → canonical → muscle → side → unit → functional role → electrode position.
 * Unknown unit or missing muscle/side BLOCKS proceed.
 */
'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { ArrowRight, ArrowLeft, CheckCircle, AlertTriangle, XCircle, Save } from 'lucide-react';
import { Card, CardContent, CardHeader } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { Alert } from '@/components/ui/Alert';
import type { ChannelMapping } from '@/schemas/mapping';
import type { MappingValidation } from '@/schemas/mapping';
import type { CanonicalMuscle, Side, SignalUnit, FunctionalRole, ElectrodePosition } from '@/schemas/common';
import { CANONICAL_MUSCLES, UNITS } from '@/schemas/common';
import * as SessionService from '@/services/mock/MockSessionService';
import * as SignalService from '@/services/mock/MockSignalWorkflowService';
import styles from './mapping.module.css';

const ROLES: FunctionalRole[] = ['agonist', 'antagonist', 'synergist', 'stabilizer', 'reference', 'unknown'];
const POSITIONS: ElectrodePosition[] = ['belly', 'distal_third', 'proximal_third', 'reference_bony', 'custom'];

export default function MappingPage() {
  const params = useParams();
  const router = useRouter();
  const sessionId = params.sessionId as string;

  const [mappings, setMappings] = useState<ChannelMapping[]>([]);
  const [validation, setValidation] = useState<MappingValidation | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const session = SessionService.getSession(sessionId);
    if (!session) { router.replace(`/sessions/${sessionId}/context`); return; }

    let m = SignalService.getMappings(sessionId);
    if (!m) {
      m = SignalService.initializeMappings(sessionId, 4, 'happy_path');
    }
    setMappings(m);
    setValidation(SignalService.validateMappings(sessionId));
    setLoading(false);
  }, [sessionId, router]);

  const updateChannel = (idx: number, field: string, value: string) => {
    const updated = SignalService.updateMapping(sessionId, idx, { [field]: value, confirmed: false });
    if (updated) {
      setMappings([...updated]);
      setValidation(SignalService.validateMappings(sessionId));
    }
  };

  const toggleConfirm = (idx: number) => {
    const m = mappings[idx];
    const updated = SignalService.updateMapping(sessionId, idx, { confirmed: !m.confirmed });
    if (updated) {
      setMappings([...updated]);
      setValidation(SignalService.validateMappings(sessionId));
    }
  };

  const confirmAll = () => {
    const updated = SignalService.confirmAllMappings(sessionId);
    if (updated) {
      setMappings([...updated]);
      setValidation(SignalService.validateMappings(sessionId));
    }
  };

  const handleContinue = () => {
    if (!validation?.valid) return;
    router.push(`/sessions/${sessionId}/preflight`);
  };

  if (loading) return <div className="page-container"><p>Đang tải...</p></div>;

  const canProceed = validation?.valid ?? false;
  const hasBlockers = (validation?.blockers.length ?? 0) > 0;

  return (
    <div className="page-container">
      <div className="page-header">
        <div className="page-header__left">
          <h1 className="page-title">Channel Mapping</h1>
          <p className="page-subtitle">Gán kênh nguồn → cơ mục tiêu, bên, đơn vị, vai trò, vị trí điện cực.</p>
        </div>
        <div className="page-header__right">
          <Badge variant={canProceed ? 'success' : hasBlockers ? 'error' : 'warning'}>
            {canProceed ? 'Sẵn sàng' : hasBlockers ? 'Bị chặn' : validation?.state ?? 'pending'}
          </Badge>
        </div>
      </div>

      {hasBlockers && (
        <Alert variant="error" title="Không thể tiếp tục — Cần sửa lỗi mapping">
          {validation?.blockers.map((b, i) => (
            <p key={i}>• {b.message}</p>
          ))}
        </Alert>
      )}

      {/* Mapping table */}
      <div className={styles.tableWrap}>
        <table className={styles.table}>
          <thead>
            <tr>
              <th>Kênh nguồn</th>
              <th>Canonical ID</th>
              <th>Cơ mục tiêu *</th>
              <th>Bên *</th>
              <th>Đơn vị *</th>
              <th>Vai trò</th>
              <th>Vị trí điện cực</th>
              <th>Xác nhận</th>
            </tr>
          </thead>
          <tbody>
            {mappings.map((m, idx) => {
              const hasError = validation?.blockers.some((b) => b.channelIndex === idx);
              return (
                <tr key={idx} className={hasError ? styles['row--error'] : m.confirmed ? styles['row--confirmed'] : ''}>
                  <td>
                    <code className={styles.channelLabel}>{m.sourceChannelLabel}</code>
                    {m.autoMapped && <Badge variant="neutral" size="sm">auto</Badge>}
                  </td>
                  <td><code>{m.canonicalChannelId}</code></td>
                  <td>
                    <select
                      value={m.muscle}
                      onChange={(e) => updateChannel(idx, 'muscle', e.target.value)}
                      className={[styles.select, !m.muscle ? styles['select--error'] : ''].filter(Boolean).join(' ')}
                      aria-label={`Muscle for ${m.sourceChannelLabel}`}
                    >
                      <option value="">— Chọn cơ —</option>
                      {CANONICAL_MUSCLES.map((muscle) => (
                        <option key={muscle} value={muscle}>{muscle}</option>
                      ))}
                    </select>
                  </td>
                  <td>
                    <select
                      value={m.side}
                      onChange={(e) => updateChannel(idx, 'side', e.target.value)}
                      className={[styles.select, !m.side ? styles['select--error'] : ''].filter(Boolean).join(' ')}
                      aria-label={`Side for ${m.sourceChannelLabel}`}
                    >
                      <option value="">— Chọn —</option>
                      <option value="Left">Trái</option>
                      <option value="Right">Phải</option>
                      <option value="Bilateral">Hai bên</option>
                    </select>
                  </td>
                  <td>
                    <select
                      value={m.unit}
                      onChange={(e) => updateChannel(idx, 'unit', e.target.value)}
                      className={[styles.select, m.unit === 'unknown' ? styles['select--error'] : ''].filter(Boolean).join(' ')}
                      aria-label={`Unit for ${m.sourceChannelLabel}`}
                    >
                      {UNITS.map((u) => (
                        <option key={u} value={u}>{u === 'unknown' ? '⚠ unknown' : u}</option>
                      ))}
                    </select>
                  </td>
                  <td>
                    <select value={m.functionalRole} onChange={(e) => updateChannel(idx, 'functionalRole', e.target.value)} className={styles.select} aria-label={`Role for ${m.sourceChannelLabel}`}>
                      {ROLES.map((r) => <option key={r} value={r}>{r}</option>)}
                    </select>
                  </td>
                  <td>
                    <select value={m.electrodePosition} onChange={(e) => updateChannel(idx, 'electrodePosition', e.target.value)} className={styles.select} aria-label={`Position for ${m.sourceChannelLabel}`}>
                      <option value="">— Chọn —</option>
                      {POSITIONS.map((p) => <option key={p} value={p}>{p}</option>)}
                    </select>
                  </td>
                  <td>
                    <button
                      className={[styles.confirmBtn, m.confirmed ? styles['confirmBtn--active'] : ''].filter(Boolean).join(' ')}
                      onClick={() => toggleConfirm(idx)}
                      disabled={!m.muscle || !m.side || m.unit === 'unknown'}
                      aria-label={`Confirm ${m.sourceChannelLabel}`}
                    >
                      {m.confirmed ? <CheckCircle size={18} /> : <span className={styles.confirmEmpty} />}
                    </button>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {/* Validation summary */}
      <div className={styles.summary}>
        <div className={styles.summaryItem}>
          <span>Đã xác nhận:</span>
          <strong>{mappings.filter((m) => m.confirmed).length} / {mappings.length}</strong>
        </div>
        <div className={styles.summaryItem}>
          <span>Lỗi chặn:</span>
          <strong className={hasBlockers ? styles.errorText : ''}>{validation?.blockers.length ?? 0}</strong>
        </div>
        <div className={styles.summaryItem}>
          <span>Cảnh báo:</span>
          <strong>{validation?.warnings.length ?? 0}</strong>
        </div>
      </div>

      <Alert variant="info" title="Lưu ý bảo mật đơn vị">
        Hệ thống <strong>không tự đoán đơn vị từ biên độ</strong>. Nếu đơn vị là &quot;unknown&quot;, bạn phải chọn đúng đơn vị trước khi tiếp tục.
      </Alert>

      <div className={styles.actions}>
        <Button variant="ghost" onClick={() => router.push(`/sessions/${sessionId}/import`)} icon={<ArrowLeft size={16} />}>Quay lại Import</Button>
        {!canProceed && mappings.every((m) => m.muscle && m.side && m.unit !== 'unknown') && (
          <Button variant="secondary" onClick={confirmAll} icon={<CheckCircle size={16} />}>Xác nhận tất cả</Button>
        )}
        <div className={styles.spacer} />
        <Button onClick={handleContinue} disabled={!canProceed} icon={<ArrowRight size={16} />} iconPosition="right">
          Tiếp tục → Preflight
        </Button>
      </div>
    </div>
  );
}
