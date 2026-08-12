import React from 'react';
import { Card, CardContent } from '../../../components/ui/Card';
import { Badge } from '../../../components/ui/Badge';
import { MetricEvidenceView } from '../types';
import { explainMetric } from '../utils';
import styles from './MetricEvidenceCard.module.css';

interface MetricEvidenceCardProps {
  view: MetricEvidenceView;
  className?: string;
}

function getStatusVariant(status: string): 'success' | 'warning' | 'error' | 'abstention' | 'neutral' {
  switch (status) {
    case 'AVAILABLE':
      return 'success';
    case 'BLOCKED':
    case 'UNSUPPORTED':
      return 'error';
    case 'REVIEW_REQUIRED':
      return 'warning';
    case 'ABSTAINED':
      return 'abstention';
    case 'NOT_AVAILABLE':
    default:
      return 'neutral';
  }
}

export function MetricEvidenceCard({ view, className }: MetricEvidenceCardProps) {
  const ds = view.distribution_support;
  const u = view.uncertainty ?? {};
  
  const isRuleConfidence = u.uncertainty_type === 'RULE_CONFIDENCE';
  const uncertaintyText = isRuleConfidence
    ? `RULE_CONFIDENCE = ${u.rule_confidence_level ?? 'UNKNOWN'} — not probability.`
    : `${u.uncertainty_type ?? 'NOT_APPLICABLE'} / calibration ${u.calibration_status ?? 'NOT_APPLICABLE'}`;

  const oodText = ds.score == null ? 'OOD score: NOT AVAILABLE' : `OOD score: ${ds.score}`;

  return (
    <Card 
      variant="default" 
      className={[styles.card, className].filter(Boolean).join(' ')}
      data-status={view.metric_status}
      aria-label={`Metric evidence for ${view.metric_name}`}
    >
      <CardContent>
        <div className={styles.header}>
          <div className={styles.titleGroup}>
            <h2 className={styles.title}>{view.metric_name}</h2>
            <div className={styles.statusLabel}>
              <Badge variant={getStatusVariant(view.metric_status)}>
                {view.status_label}
              </Badge>
            </div>
          </div>
          <div className={styles.researchBadge}>
            <Badge variant="neutral" size="sm">RESEARCH ONLY</Badge>
          </div>
        </div>

        <div className={styles.contentRow}>
          <div className={styles.valueLabel}>Value:</div>
          {view.value == null ? (
            <div className={styles.valueUnavailable} data-value="unavailable">
              Unavailable
            </div>
          ) : (
            <div className={styles.valueText} data-value="available">
              {view.value} {view.units ?? ''}
            </div>
          )}
        </div>

        {view.reason_codes.length > 0 ? (
          <div className={styles.contentRow}>
            <div className={styles.valueLabel}>Blocking Reasons:</div>
            <ul className={styles.reasonList} aria-label="Metric reason codes">
              {view.reason_codes.map((r) => (
                <li key={r}><code>{r}</code></li>
              ))}
            </ul>
          </div>
        ) : (
          <p className={styles.sectionText}>No blocking reason code.</p>
        )}

        <section className={styles.section} aria-label="Distribution support">
          <h3 className={styles.sectionTitle}>Distribution support</h3>
          <p className={styles.sectionText}>Status: {ds.status}</p>
          <p className={styles.sectionText}>Method: {ds.method_status}</p>
          <p className={styles.sectionText}>{oodText}</p>
        </section>

        <section className={styles.section} aria-label="Uncertainty semantics">
          <h3 className={styles.sectionTitle}>Uncertainty</h3>
          <p className={styles.sectionText}>{uncertaintyText}</p>
          {isRuleConfidence && (
            <p className={styles.sectionText}>
              <strong>RULE_CONFIDENCE ≠ PROBABILITY</strong>
            </p>
          )}
        </section>

        <p className={styles.explanation}>
          {explainMetric(view)}
        </p>
      </CardContent>
    </Card>
  );
}
