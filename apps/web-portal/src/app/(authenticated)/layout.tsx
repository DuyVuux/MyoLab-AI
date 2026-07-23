/**
 * Dashboard Layout — wraps all authenticated routes with AppShell
 * Redirects to login if not authenticated
 */
'use client';

import { useEffect, type ReactNode } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import { useAuth } from '@/lib/auth';
import { canAccessRoute } from '@/lib/permissions';
import { AppShell } from '@/components/layout/AppShell';
import { Alert } from '@/components/ui/Alert';

export default function DashboardLayout({ children }: { children: ReactNode }) {
  const { user, isAuthenticated } = useAuth();
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    if (!isAuthenticated) {
      router.replace('/login');
    }
  }, [isAuthenticated, router]);

  if (!isAuthenticated || !user) {
    return null;
  }

  const isAllowed = canAccessRoute(user.role, pathname);

  if (!isAllowed) {
    return (
      <AppShell>
        <div style={{ padding: '2rem' }}>
          <Alert variant="error" title="Truy cập bị từ chối (403)">
            Vai trò hiện tại ({user.role}) không có quyền truy cập vào đường dẫn ({pathname}). Vui lòng liên hệ quản trị viên.
          </Alert>
        </div>
      </AppShell>
    );
  }

  return <AppShell>{children}</AppShell>;
}
