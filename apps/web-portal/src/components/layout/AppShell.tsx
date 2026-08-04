/**
 * AppShell — Global Layout Shell
 * Per Section 5.1: Sidebar 280px dark teal, collapsible, with disclaimer footer.
 * Header: breadcrumbs, page title, tier badge, source badge, QC/review status.
 */
'use client';

import { useState, type ReactNode } from 'react';
import Link from 'next/link';
import Image from 'next/image';
import { usePathname } from 'next/navigation';
import {
  LayoutDashboard,
  Layers,
  ClipboardList,
  Upload,
  BarChart3,
  MessageSquare,
  AlertTriangle,
  Activity,
  Stethoscope,
  FlaskConical,
  Monitor,
  Cpu,
  FileText,
  Shield,
  Settings,
  ChevronLeft,
  ChevronRight,
  LogOut,
  UserCircle,
  Menu,
  X,
} from 'lucide-react';
import { useAuth } from '@/lib/auth';
import { ROUTES } from '@/config/useCaseRoutes';
import styles from './AppShell.module.css';

interface NavItem {
  label: string;
  href: string;
  icon: React.ElementType;
  badge?: number;
  tier?: 1 | 2;
}

interface NavGroup {
  title?: string;
  items: NavItem[];
}

const NAV_GROUPS: NavGroup[] = [
  {
    items: [
      { label: 'Tổng quan', href: ROUTES.DASHBOARD, icon: LayoutDashboard },
      { label: 'Danh mục Use Case', href: ROUTES.USE_CASES, icon: Layers },
      { label: 'Phiên đánh giá', href: ROUTES.SESSIONS, icon: ClipboardList },
      { label: 'Import dữ liệu', href: ROUTES.IMPORTS, icon: Upload },
      { label: 'Phiên phân tích', href: ROUTES.ANALYSES, icon: BarChart3 },
      { label: 'Phản hồi', href: ROUTES.FEEDBACK_INBOX, icon: MessageSquare },
      { label: 'Data Quality Issues', href: ROUTES.DATA_QUALITY, icon: AlertTriangle },
    ],
  },
  {
    title: 'Use Cases',
    items: [
      { label: 'UC1 · Biofeedback cử chỉ', href: ROUTES.UC1_INTRO, icon: Activity, tier: 1 },
      { label: 'UC2 · Đánh giá định lượng', href: ROUTES.UC2_INTRO, icon: Stethoscope, tier: 1 },
      { label: 'UC3 · Chi giả — Nghiên cứu', href: ROUTES.UC3_INTRO, icon: FlaskConical, tier: 2 },
      { label: 'UC4 · Medical HMI — Nghiên cứu', href: ROUTES.UC4_INTRO, icon: Monitor, tier: 2 },
    ],
  },
  {
    title: 'Quản trị',
    items: [
      { label: 'Thiết bị', href: ROUTES.DEVICES, icon: Cpu },
      { label: 'Protocol', href: ROUTES.PROTOCOLS, icon: FileText },
      { label: 'Audit', href: ROUTES.AUDIT, icon: Shield },
      { label: 'Admin', href: ROUTES.ADMIN_USERS, icon: Settings },
    ],
  },
];

export interface AppShellProps {
  children: ReactNode;
}

export function AppShell({ children }: AppShellProps) {
  const pathname = usePathname();
  const { user, logout } = useAuth();
  const [collapsed, setCollapsed] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);

  return (
    <div className={styles.layout}>
      {/* Mobile overlay */}
      {mobileOpen && (
        <div
          className={styles.overlay}
          onClick={() => setMobileOpen(false)}
          aria-hidden="true"
        />
      )}

      {/* Sidebar */}
      <aside
        className={[
          styles.sidebar,
          collapsed ? styles['sidebar--collapsed'] : '',
          mobileOpen ? styles['sidebar--mobile-open'] : '',
        ].filter(Boolean).join(' ')}
        role="navigation"
        aria-label="Điều hướng chính"
      >
        {/* Logo / Brand */}
        <div className={styles.brand}>
          {!collapsed && (
            <div className={styles.brandContent}>
              <Image src="/VINMEC_logo.png" alt="Vinmec Logo" width={54} height={32} className={styles.brandIcon} style={{ objectFit: 'contain', backgroundColor: 'white', padding: '4px', borderRadius: '6px' }} />
              <div>
                <div className={styles.brandName}>MyoLab-AI</div>
                <div className={styles.brandSubtitle}>sEMG Clinical Intelligence</div>
              </div>
            </div>
          )}
          {collapsed && <Image src="/VINMEC_logo.png" alt="Vinmec Logo" width={54} height={32} className={styles.brandIcon} style={{ objectFit: 'contain', backgroundColor: 'white', padding: '4px', borderRadius: '6px' }} />}
          
          {/* Mobile close */}
          <button
            className={styles.mobileClose}
            onClick={() => setMobileOpen(false)}
            aria-label="Đóng menu"
          >
            <X size={20} />
          </button>
        </div>

        {/* Navigation */}
        <nav className={styles.nav}>
          {NAV_GROUPS.map((group, gi) => (
            <div key={gi} className={styles.navGroup}>
              {group.title && !collapsed && (
                <div className={styles.navGroupTitle}>{group.title}</div>
              )}
              {group.items.map((item) => {
                const isActive = pathname === item.href || pathname.startsWith(item.href + '/');
                const Icon = item.icon;
                return (
                  <Link
                    key={item.href}
                    href={item.href}
                    className={[styles.navItem, isActive ? styles['navItem--active'] : ''].filter(Boolean).join(' ')}
                    aria-current={isActive ? 'page' : undefined}
                    title={collapsed ? item.label : undefined}
                    onClick={() => setMobileOpen(false)}
                  >
                    <Icon size={20} aria-hidden="true" />
                    {!collapsed && (
                      <>
                        <span className={styles.navLabel}>{item.label}</span>
                        {item.tier && (
                          <span className={[styles.tierDot, styles[`tierDot--${item.tier}`]].join(' ')} aria-label={`Tầng ${item.tier}`} />
                        )}
                        {item.badge !== undefined && item.badge > 0 && (
                          <span className={styles.navBadge}>{item.badge}</span>
                        )}
                      </>
                    )}
                  </Link>
                );
              })}
            </div>
          ))}
        </nav>

        {/* User section */}
        {user && !collapsed && (
          <div className={styles.userSection}>
            <div className={styles.userInfo}>
              <UserCircle size={20} aria-hidden="true" />
              <div className={styles.userName}>
                <div className={styles.userDisplayName}>{user.name}</div>
                <div className={styles.userRole}>{user.displayRole}</div>
              </div>
            </div>
            <button className={styles.logoutBtn} onClick={logout} aria-label="Đăng xuất">
              <LogOut size={18} />
            </button>
          </div>
        )}

        {/* Disclaimer footer — Section 5.1 mandatory */}
        {!collapsed && (
          <div className={styles.disclaimer}>
            <p>Dữ liệu prototype / mô phỏng.</p>
            <p>Kết quả không thay thế quyết định bác sĩ hoặc KTV.</p>
            <p>Human review bắt buộc.</p>
          </div>
        )}

        {/* Collapse toggle (desktop) */}
        <button
          className={styles.collapseBtn}
          onClick={() => setCollapsed(!collapsed)}
          aria-label={collapsed ? 'Mở rộng sidebar' : 'Thu gọn sidebar'}
        >
          {collapsed ? <ChevronRight size={16} /> : <ChevronLeft size={16} />}
        </button>
      </aside>

      {/* Main Content */}
      <main
        className={[styles.main, collapsed ? styles['main--expanded'] : ''].filter(Boolean).join(' ')}
      >
        {/* Mobile header */}
        <div className={styles.mobileHeader}>
          <button
            className={styles.menuBtn}
            onClick={() => setMobileOpen(true)}
            aria-label="Mở menu"
          >
            <Menu size={24} />
          </button>
          <span className={styles.mobileTitle}>MyoLab-AI</span>
        </div>

        {children}
      </main>
    </div>
  );
}
