/**
 * Button Component
 * Per Section 12.1: primary/secondary/danger/ghost, loading, disabled reason
 */
'use client';

import { forwardRef, type ButtonHTMLAttributes, type ReactNode } from 'react';
import { Loader2 } from 'lucide-react';
import styles from './Button.module.css';

export type ButtonVariant = 'primary' | 'secondary' | 'danger' | 'ghost';
export type ButtonSize = 'sm' | 'md' | 'lg';

export interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant;
  size?: ButtonSize;
  loading?: boolean;
  loadingText?: string;
  disabledReason?: string;
  icon?: ReactNode;
  iconPosition?: 'left' | 'right';
  fullWidth?: boolean;
}

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  (
    {
      variant = 'primary',
      size = 'md',
      loading = false,
      loadingText,
      disabledReason,
      icon,
      iconPosition = 'left',
      fullWidth = false,
      disabled,
      children,
      className,
      ...props
    },
    ref
  ) => {
    const isDisabled = disabled || loading;

    return (
      <button
        ref={ref}
        className={[
          styles.button,
          styles[`button--${variant}`],
          styles[`button--${size}`],
          loading ? styles['button--loading'] : '',
          fullWidth ? styles['button--full-width'] : '',
          className,
        ]
          .filter(Boolean)
          .join(' ')}
        disabled={isDisabled}
        aria-disabled={isDisabled}
        aria-busy={loading}
        title={isDisabled && disabledReason ? disabledReason : undefined}
        {...props}
      >
        {loading ? (
          <>
            <Loader2 size={size === 'sm' ? 14 : 16} className={styles.spinner} aria-hidden="true" />
            <span>{loadingText || 'Đang xử lý...'}</span>
          </>
        ) : (
          <>
            {icon && iconPosition === 'left' && (
              <span className={styles.icon} aria-hidden="true">{icon}</span>
            )}
            <span>{children}</span>
            {icon && iconPosition === 'right' && (
              <span className={styles.icon} aria-hidden="true">{icon}</span>
            )}
          </>
        )}
      </button>
    );
  }
);

Button.displayName = 'Button';
