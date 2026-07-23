'use client';

import { type ReactNode } from 'react';
import { useAuth, type UserRole } from '@/lib/auth';
import { Alert } from '@/components/ui/Alert';

interface RoleGuardProps {
  allowedRoles: UserRole[];
  children: ReactNode;
  fallback?: ReactNode;
}

export function RoleGuard({ allowedRoles, children, fallback }: RoleGuardProps) {
  const { user } = useAuth();

  if (!user || !allowedRoles.includes(user.role)) {
    if (fallback !== undefined) {
      return <>{fallback}</>;
    }
    return (
      <div style={{ padding: '2rem' }}>
        <Alert variant="error" title="Truy cập bị từ chối">
          Bạn không có quyền truy cập vào chức năng này. Vui lòng liên hệ quản trị viên.
        </Alert>
      </div>
    );
  }

  return <>{children}</>;
}
