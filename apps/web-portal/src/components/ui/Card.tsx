/**
 * Card Component
 * Per Section 12.1: surface, border, shadow, semantic variants
 */
import type { ReactNode, HTMLAttributes } from 'react';
import styles from './Card.module.css';

export type CardVariant = 'default' | 'elevated' | 'outlined' | 'success' | 'warning' | 'error' | 'abstention' | 'info';

export interface CardProps extends HTMLAttributes<HTMLDivElement> {
  variant?: CardVariant;
  padding?: 'none' | 'sm' | 'md' | 'lg';
  hoverable?: boolean;
  children: ReactNode;
}

export function Card({
  variant = 'default',
  padding = 'md',
  hoverable = false,
  children,
  className,
  ...props
}: CardProps) {
  return (
    <div
      className={[
        styles.card,
        styles[`card--${variant}`],
        styles[`card--pad-${padding}`],
        hoverable ? styles['card--hoverable'] : '',
        className,
      ]
        .filter(Boolean)
        .join(' ')}
      {...props}
    >
      {children}
    </div>
  );
}

export function CardHeader({ children, className, ...props }: HTMLAttributes<HTMLDivElement>) {
  return (
    <div className={[styles.cardHeader, className].filter(Boolean).join(' ')} {...props}>
      {children}
    </div>
  );
}

export function CardContent({ children, className, ...props }: HTMLAttributes<HTMLDivElement>) {
  return (
    <div className={[styles.cardContent, className].filter(Boolean).join(' ')} {...props}>
      {children}
    </div>
  );
}

export function CardFooter({ children, className, ...props }: HTMLAttributes<HTMLDivElement>) {
  return (
    <div className={[styles.cardFooter, className].filter(Boolean).join(' ')} {...props}>
      {children}
    </div>
  );
}
