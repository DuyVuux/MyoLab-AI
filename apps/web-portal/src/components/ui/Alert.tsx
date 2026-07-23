/**
 * Alert Component
 * Per Section 12.1: info/success/warning/error/abstention
 * Each alert has icon + text + reason code — never color alone
 */
import type { ReactNode } from 'react';
import { Info, CheckCircle, AlertTriangle, XCircle, HelpCircle } from 'lucide-react';
import styles from './Alert.module.css';

export type AlertVariant = 'info' | 'success' | 'warning' | 'error' | 'abstention';

export interface AlertProps {
  variant: AlertVariant;
  title?: string;
  children: ReactNode;
  reasonCode?: string;
  action?: ReactNode;
  dismissible?: boolean;
  onDismiss?: () => void;
  className?: string;
}

const VARIANT_ICONS: Record<AlertVariant, React.ElementType> = {
  info: Info,
  success: CheckCircle,
  warning: AlertTriangle,
  error: XCircle,
  abstention: HelpCircle,
};

const VARIANT_LABELS: Record<AlertVariant, string> = {
  info: 'Thông tin',
  success: 'Thành công',
  warning: 'Cảnh báo',
  error: 'Lỗi',
  abstention: 'Không khả dụng',
};

export function Alert({
  variant,
  title,
  children,
  reasonCode,
  action,
  dismissible = false,
  onDismiss,
  className,
}: AlertProps) {
  const Icon = VARIANT_ICONS[variant];

  return (
    <div
      className={[styles.alert, styles[`alert--${variant}`], className].filter(Boolean).join(' ')}
      role="alert"
      aria-live={variant === 'error' ? 'assertive' : 'polite'}
    >
      <div className={styles.iconContainer}>
        <Icon size={20} aria-hidden="true" />
      </div>
      <div className={styles.content}>
        {title && <div className={styles.title}>{title}</div>}
        <div className={styles.message}>{children}</div>
        {reasonCode && (
          <code className={styles.reasonCode}>Mã: {reasonCode}</code>
        )}
      </div>
      {action && <div className={styles.action}>{action}</div>}
      {dismissible && (
        <button
          className={styles.dismiss}
          onClick={onDismiss}
          aria-label={`Đóng thông báo: ${VARIANT_LABELS[variant]}`}
        >
          <XCircle size={16} />
        </button>
      )}
    </div>
  );
}
