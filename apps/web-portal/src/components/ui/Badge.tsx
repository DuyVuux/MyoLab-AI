/**
 * Badge Component
 * Per Section 12.1: tier/status/source/review/feasibility variants
 */
import type { ReactNode } from 'react';
import styles from './Badge.module.css';

export type BadgeVariant =
  | 'tier1'
  | 'tier2'
  | 'success'
  | 'warning'
  | 'error'
  | 'info'
  | 'abstention'
  | 'neutral'
  | 'source-synthetic'
  | 'source-deidentified'
  | 'source-local'
  | 'review-pending'
  | 'review-approved'
  | 'review-rejected';

export interface BadgeProps {
  variant: BadgeVariant;
  children: ReactNode;
  icon?: ReactNode;
  size?: 'sm' | 'md';
  className?: string;
}

export function Badge({ variant, children, icon, size = 'sm', className }: BadgeProps) {
  return (
    <span
      className={[styles.badge, styles[`badge--${variant}`], styles[`badge--${size}`], className]
        .filter(Boolean)
        .join(' ')}
      role="status"
    >
      {icon && <span className={styles.icon} aria-hidden="true">{icon}</span>}
      {children}
    </span>
  );
}
