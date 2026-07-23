/**
 * Input Component
 * Per Section 12.1: label, error, readonly, counter
 * Per Section 13: Every form input has associated label
 */
'use client';

import { forwardRef, type InputHTMLAttributes } from 'react';
import styles from './Input.module.css';

export interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label: string;
  error?: string;
  hint?: string;
  counter?: { current: number; max: number };
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ label, error, hint, counter, id, className, ...props }, ref) => {
    const inputId = id || `input-${label.toLowerCase().replace(/\s+/g, '-')}`;
    const errorId = error ? `${inputId}-error` : undefined;
    const hintId = hint ? `${inputId}-hint` : undefined;

    return (
      <div className={[styles.field, error ? styles['field--error'] : '', className].filter(Boolean).join(' ')}>
        <label htmlFor={inputId} className={styles.label}>
          {label}
          {props.required && <span className={styles.required} aria-hidden="true"> *</span>}
        </label>
        <input
          ref={ref}
          id={inputId}
          className={styles.input}
          aria-invalid={!!error}
          aria-describedby={[errorId, hintId].filter(Boolean).join(' ') || undefined}
          {...props}
        />
        <div className={styles.footer}>
          <div>
            {error && (
              <p id={errorId} className={styles.error} role="alert">
                {error}
              </p>
            )}
            {!error && hint && (
              <p id={hintId} className={styles.hint}>
                {hint}
              </p>
            )}
          </div>
          {counter && (
            <span className={styles.counter}>
              {counter.current}/{counter.max}
            </span>
          )}
        </div>
      </div>
    );
  }
);

Input.displayName = 'Input';
