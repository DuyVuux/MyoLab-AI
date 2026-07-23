/**
 * Admin Users — `/admin/users`
 */
'use client';

import { Settings, Users, Plus, Shield } from 'lucide-react';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { Alert } from '@/components/ui/Alert';

const MOCK_USERS = [
  { id: 'USR-KTV-001', name: 'Trần Thị B', role: 'ktv', displayRole: 'KTV PHCN', status: 'active', lastLogin: '2026-07-23' },
  { id: 'USR-DOC-001', name: 'BS. Lê Văn C', role: 'doctor', displayRole: 'Bác sĩ', status: 'active', lastLogin: '2026-07-23' },
  { id: 'USR-PAT-001', name: 'Nguyễn Văn A', role: 'patient', displayRole: 'Bệnh nhân', status: 'active', lastLogin: '2026-07-22' },
  { id: 'USR-RES-001', name: 'ThS. Phạm Thị D', role: 'researcher', displayRole: 'Nghiên cứu viên', status: 'active', lastLogin: '2026-07-22' },
  { id: 'USR-ADM-001', name: 'Admin Hệ thống', role: 'admin', displayRole: 'Admin', status: 'active', lastLogin: '2026-07-23' },
];

export default function AdminUsersPage() {
  return (
    <div className="page-container">
      <div className="page-header">
        <div className="page-header__left">
          <h1 className="page-title">Quản lý người dùng</h1>
          <p className="page-subtitle">Admin — Quản lý tài khoản và phân quyền.</p>
        </div>
        <div className="page-header__right">
          <Button icon={<Plus size={16} />} variant="secondary">Thêm người dùng</Button>
        </div>
      </div>

      <Alert variant="info" title="Prototype Mode">
        Trong prototype, tất cả người dùng đều là mock. Không có authentication thực.
      </Alert>

      <div style={{ overflowX: 'auto', border: '1px solid var(--color-border)', borderRadius: 'var(--radius-lg)', backgroundColor: 'var(--color-surface)', marginTop: 'var(--space-4)' }}>
        <table style={{ width: '100%', minWidth: '600px' }}>
          <thead>
            <tr>
              <th style={{ textAlign: 'left', padding: 'var(--space-3) var(--space-4)', fontSize: 'var(--font-size-xs)', fontWeight: 600, color: 'var(--color-text-secondary)', textTransform: 'uppercase', letterSpacing: '0.05em', borderBottom: '1px solid var(--color-border)', backgroundColor: 'var(--color-background)' }}>User ID</th>
              <th style={{ textAlign: 'left', padding: 'var(--space-3) var(--space-4)', fontSize: 'var(--font-size-xs)', fontWeight: 600, color: 'var(--color-text-secondary)', textTransform: 'uppercase', letterSpacing: '0.05em', borderBottom: '1px solid var(--color-border)', backgroundColor: 'var(--color-background)' }}>Tên</th>
              <th style={{ textAlign: 'left', padding: 'var(--space-3) var(--space-4)', fontSize: 'var(--font-size-xs)', fontWeight: 600, color: 'var(--color-text-secondary)', textTransform: 'uppercase', letterSpacing: '0.05em', borderBottom: '1px solid var(--color-border)', backgroundColor: 'var(--color-background)' }}>Vai trò</th>
              <th style={{ textAlign: 'left', padding: 'var(--space-3) var(--space-4)', fontSize: 'var(--font-size-xs)', fontWeight: 600, color: 'var(--color-text-secondary)', textTransform: 'uppercase', letterSpacing: '0.05em', borderBottom: '1px solid var(--color-border)', backgroundColor: 'var(--color-background)' }}>Trạng thái</th>
              <th style={{ textAlign: 'left', padding: 'var(--space-3) var(--space-4)', fontSize: 'var(--font-size-xs)', fontWeight: 600, color: 'var(--color-text-secondary)', textTransform: 'uppercase', letterSpacing: '0.05em', borderBottom: '1px solid var(--color-border)', backgroundColor: 'var(--color-background)' }}>Login gần nhất</th>
            </tr>
          </thead>
          <tbody>
            {MOCK_USERS.map((u) => (
              <tr key={u.id}>
                <td style={{ padding: 'var(--space-3) var(--space-4)', fontSize: 'var(--font-size-sm)', borderBottom: '1px solid var(--color-border-subtle)', fontFamily: 'var(--font-mono)' }}>{u.id}</td>
                <td style={{ padding: 'var(--space-3) var(--space-4)', fontSize: 'var(--font-size-sm)', borderBottom: '1px solid var(--color-border-subtle)' }}>{u.name}</td>
                <td style={{ padding: 'var(--space-3) var(--space-4)', fontSize: 'var(--font-size-sm)', borderBottom: '1px solid var(--color-border-subtle)' }}><Badge variant="neutral" size="sm">{u.displayRole}</Badge></td>
                <td style={{ padding: 'var(--space-3) var(--space-4)', fontSize: 'var(--font-size-sm)', borderBottom: '1px solid var(--color-border-subtle)' }}><Badge variant="success" size="sm">{u.status}</Badge></td>
                <td style={{ padding: 'var(--space-3) var(--space-4)', fontSize: 'var(--font-size-sm)', borderBottom: '1px solid var(--color-border-subtle)', fontFamily: 'var(--font-mono)' }}>{u.lastLogin}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
