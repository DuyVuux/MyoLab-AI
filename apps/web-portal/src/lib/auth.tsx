/**
 * MyoLab-AI Authentication Context
 * Mock auth for prototype — no real authentication
 *
 * Roles per Section 1.3 of the UI/UX spec:
 * - patient: Biofeedback view only
 * - ktv: Session setup, import, mapping, QC, output, drill-down
 * - doctor: Summary, trend, review, report, clinical sign-off
 * - researcher: De-identified evidence, candidate dataset
 * - admin: Audit, user/config/protocol/device template
 */
'use client';

import { createContext, useContext, useState, useCallback, useEffect, type ReactNode } from 'react';

export type UserRole = 'patient' | 'ktv' | 'doctor' | 'researcher' | 'admin';

export interface AuthUser {
  id: string;
  name: string;
  role: UserRole;
  displayRole: string;
}

export interface AuthContextValue {
  user: AuthUser | null;
  isAuthenticated: boolean;
  isReady: boolean;
  login: (role: UserRole) => void;
  logout: () => void;
  switchRole: (role: UserRole) => void;
}

const MOCK_USERS: Record<UserRole, AuthUser> = {
  patient: {
    id: 'USR-PAT-001',
    name: 'Nguyễn Văn A (Bệnh nhân)',
    role: 'patient',
    displayRole: 'Bệnh nhân',
  },
  ktv: {
    id: 'USR-KTV-001',
    name: 'Trần Thị B (KTV PHCN)',
    role: 'ktv',
    displayRole: 'KTV Phục hồi chức năng',
  },
  doctor: {
    id: 'USR-DOC-001',
    name: 'BS. Lê Văn C',
    role: 'doctor',
    displayRole: 'Bác sĩ',
  },
  researcher: {
    id: 'USR-RES-001',
    name: 'ThS. Phạm Thị D (Researcher)',
    role: 'researcher',
    displayRole: 'Nghiên cứu viên / ML QA',
  },
  admin: {
    id: 'USR-ADM-001',
    name: 'Admin Hệ thống',
    role: 'admin',
    displayRole: 'Quản trị viên',
  },
};

const AuthContext = createContext<AuthContextValue | undefined>(undefined);
const MOCK_ROLE_STORAGE_KEY = 'myolab-ai.mock-role';

function isUserRole(value: string | null): value is UserRole {
  return value !== null && Object.prototype.hasOwnProperty.call(MOCK_USERS, value);
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [isReady, setIsReady] = useState(false);

  useEffect(() => {
    const storedRole = window.sessionStorage.getItem(MOCK_ROLE_STORAGE_KEY);
    if (isUserRole(storedRole)) {
      setUser(MOCK_USERS[storedRole]);
    } else if (storedRole !== null) {
      window.sessionStorage.removeItem(MOCK_ROLE_STORAGE_KEY);
    }
    setIsReady(true);
  }, []);

  const login = useCallback((role: UserRole) => {
    window.sessionStorage.setItem(MOCK_ROLE_STORAGE_KEY, role);
    setUser(MOCK_USERS[role]);
  }, []);

  const logout = useCallback(() => {
    window.sessionStorage.removeItem(MOCK_ROLE_STORAGE_KEY);
    setUser(null);
  }, []);

  const switchRole = useCallback((role: UserRole) => {
    window.sessionStorage.setItem(MOCK_ROLE_STORAGE_KEY, role);
    setUser(MOCK_USERS[role]);
  }, []);

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated: user !== null,
        isReady,
        login,
        logout,
        switchRole,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}

export { MOCK_USERS };
