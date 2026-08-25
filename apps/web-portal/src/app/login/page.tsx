/**
 * Login Page — Role Selection
 * Mock authentication for prototype
 * Per Section 1.3: 5 persona roles
 */
'use client';

import { useRouter } from 'next/navigation';
import Image from 'next/image';
import {
  User,
  Stethoscope,
  UserCircle,
  FlaskConical,
  Settings,
  Activity,
} from 'lucide-react';
import { useAuth, type UserRole } from '@/lib/auth';
import styles from './login.module.css';

interface RoleOption {
  role: UserRole;
  label: string;
  description: string;
  icon: React.ElementType;
  permissions: string[];
}

const ROLE_OPTIONS: RoleOption[] = [
  {
    role: 'ktv',
    label: 'KTV Phục hồi chức năng',
    description: 'Thiết lập phiên, import dữ liệu, mapping kênh, kiểm tra chất lượng, xem kết quả phân tích.',
    icon: UserCircle,
    permissions: ['Tạo phiên', 'Upload dữ liệu', 'Map kênh', 'Chạy QC/AI', 'Technical review'],
  },
  {
    role: 'doctor',
    label: 'Bác sĩ PHCN',
    description: 'Xem tổng hợp, trend và ghi chú human review trong phạm vi research demo.',
    icon: Stethoscope,
    permissions: ['Xem summary/trend', 'Human review', 'Xác nhận đã xem', 'Override kỹ thuật (theo policy)'],
  },
  {
    role: 'patient',
    label: 'Bệnh nhân',
    description: 'Xem biofeedback đơn giản UC1, phản hồi trải nghiệm.',
    icon: User,
    permissions: ['Xem biofeedback UC1', 'Phản hồi trải nghiệm'],
  },
  {
    role: 'researcher',
    label: 'Nghiên cứu viên / ML QA',
    description: 'Xem bằng chứng de-identified, dataset candidates, comment/review.',
    icon: FlaskConical,
    permissions: ['Xem evidence', 'Comment/review candidate', 'Replay de-identified'],
  },
  {
    role: 'admin',
    label: 'Quản trị viên',
    description: 'Quản lý audit, user, config, protocol, device template.',
    icon: Settings,
    permissions: ['Audit log', 'User management', 'Protocol/device config'],
  },
];

export default function LoginPage() {
  const router = useRouter();
  const { login } = useAuth();

  const handleLogin = (role: UserRole) => {
    login(role);
    router.push('/dashboard');
  };

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <Image src="/VINMEC_logo.png" alt="Vinmec Logo" width={80} height={48} className={styles.logo} style={{ objectFit: 'contain', backgroundColor: 'white', padding: '6px', borderRadius: '8px' }} />
        <h1 className={styles.title}>MyoLab-AI</h1>
        <p className={styles.subtitle}>sEMG Quality Intelligence Research Portal</p>
        <p className={styles.note}>
          Research-only prototype với dữ liệu mô phỏng — Chọn vai trò để đăng nhập
        </p>
      </div>

      <div className={styles.grid}>
        {ROLE_OPTIONS.map((option) => {
          const Icon = option.icon;
          return (
            <button
              key={option.role}
              className={styles.roleCard}
              onClick={() => handleLogin(option.role)}
              aria-label={`Đăng nhập với vai trò ${option.label}`}
            >
              <div className={styles.roleIcon}>
                <Icon size={28} />
              </div>
              <h2 className={styles.roleLabel}>{option.label}</h2>
              <p className={styles.roleDescription}>{option.description}</p>
              <ul className={styles.permissionList}>
                {option.permissions.map((p) => (
                  <li key={p} className={styles.permissionItem}>
                    {p}
                  </li>
                ))}
              </ul>
            </button>
          );
        })}
      </div>

      <footer className={styles.footer}>
        <p>Dữ liệu prototype / mô phỏng. Không dùng cho chẩn đoán, điều trị hoặc quyết định lâm sàng.</p>
        <p>Human review bắt buộc. Không có dữ liệu bệnh nhân thật.</p>
      </footer>
    </div>
  );
}
