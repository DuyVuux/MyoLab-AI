import React from 'react';
import { PanelModel, Point, SignalViewerModel } from './types';
import styles from './SignalViewer.module.css';

function getPolylinePoints(points: Point[], width: number = 800, height: number = 180): string {
  const valid = points.filter(p => p.y != null);
  if (!valid.length) return '';
  const xs = valid.map(p => p.x);
  const ys = valid.map(p => p.y);
  const xmin = Math.min(...xs);
  const xmax = Math.max(...xs);
  const ymin = Math.min(...ys);
  const ymax = Math.max(...ys);
  const xr = xmax - xmin || 1;
  const yr = ymax - ymin || 1;
  
  return valid.map(p => `${((p.x - xmin) / xr * width).toFixed(2)},${(height - (p.y - ymin) / yr * height).toFixed(2)}`).join(' ');
}

interface SignalPanelProps {
  panel: PanelModel;
}

export function SignalPanel({ panel }: SignalPanelProps) {
  const mask = panel.mask_intervals.map((m, i) => (
    <li key={i}>{m.start_s.toFixed(6)}–{m.end_s.toFixed(6)} s</li>
  ));

  return (
    <figure data-series-kind={panel.kind} aria-label={`${panel.kind} waveform`} className={styles.panel}>
      <figcaption className={styles.panelTitle}>{panel.kind} waveform — unit: {panel.units}</figcaption>
      
      <div className={styles.plotContainer}>
        <svg viewBox="0 0 800 180" className={styles.svgPlot} role="img" aria-label={`${panel.kind} signal plot`}>
          <polyline fill="none" stroke="currentColor" className={styles.polyline} strokeWidth="1.5" points={getPolylinePoints(panel.points)} />
        </svg>
      </div>

      <div className={styles.metaInfo}>
        <p>Source ref: <a href={`#evidence-${panel.source_ref}`} className={styles.link}>{panel.source_ref}</a></p>
        
        {panel.kind === 'PROCESSED' && (
          <>
            <p>Processing manifest: <a href={`#manifest-${panel.manifest_id}`} className={styles.link}>{panel.manifest_id}</a></p>
            <p>Profile: {panel.profile_id ?? 'UNKNOWN_PROFILE'}</p>
          </>
        )}

        <details className={styles.maskDetails}>
          <summary className={styles.maskSummary}>Masked intervals</summary>
          <ul className={styles.maskList}>
            {mask.length > 0 ? mask : <li>None</li>}
          </ul>
        </details>
      </div>
    </figure>
  );
}

interface SignalViewerProps {
  model: SignalViewerModel;
}

export function SignalViewer({ model }: SignalViewerProps) {
  const w = model.window_identity;

  return (
    <main aria-labelledby="signal-viewer-title" className={styles.container}>
      <aside role="note" className={styles.researchBadge}>
        <strong>RESEARCH ONLY</strong>
      </aside>
      
      <h1 id="signal-viewer-title" className={styles.title}>Raw vs processed signal evidence</h1>
      
      <section aria-label="Window identity" className={styles.windowIdentity}>
        <code>{w.window_id}</code> · channel {w.channel_id} · samples {w.start_sample}:{w.end_sample_exclusive}
      </section>

      <div className={styles.panelsContainer}>
        {model.panels.map((panel, idx) => (
          <SignalPanel key={idx} panel={panel} />
        ))}
      </div>
    </main>
  );
}
