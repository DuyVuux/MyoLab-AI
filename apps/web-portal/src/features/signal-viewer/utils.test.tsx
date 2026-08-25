import { buildSeries, buildSignalViewerModel, decimateMinMax, toPoints } from './utils';
import { WindowIdentity } from './types';
import { render } from '@testing-library/react';
import { SignalViewer } from './SignalViewer';
import React from 'react';

const wi: WindowIdentity = {
  window_id: 'qcw_sha256_demo',
  session_id: 's1',
  channel_id: 'ch1',
  source_id: 'src_sha256_demo',
  start_sample: 1000,
  end_sample_exclusive: 1500,
  context_start_sample: 500,
  context_end_sample_exclusive: 2000,
  sampling_rate_hz: 2000
};

const raw = buildSeries({
  kind: 'RAW',
  values: [0, 1, 2, null, 1, 0],
  fs_hz: 2000,
  units: 'uV',
  source_ref: 'src_sha256_demo',
  mask: [false, false, false, true, false, false]
});

const processed = buildSeries({
  kind: 'PROCESSED',
  values: [0, 0.5, 1, null, 0.5, 0],
  fs_hz: 2000,
  units: 'uV',
  source_ref: 'part_sha256_demo',
  manifest_id: 'pman_sha256_demo',
  profile_id: 'research-v0.1',
  mask: [false, false, false, true, false, false]
});

describe('Signal Viewer Logic', () => {
  it('raw and processed panels stay explicitly distinct', () => {
    const m = buildSignalViewerModel({ window_identity: wi, raw, processed });
    expect(m.panels.map(p => p.kind)).toEqual(['RAW', 'PROCESSED']);
    expect(m.panels[0].manifest_id).toBeNull();
    expect(m.panels[1].manifest_id).toBe('pman_sha256_demo');
  });

  it('processed cannot be labeled RAW and raw cannot masquerade as processed', () => {
    // @ts-expect-error Intentionally invalid kind logic test
    expect(() => buildSignalViewerModel({ window_identity: wi, raw: processed, processed })).toThrow(/RAW_PANEL_REQUIRES_RAW_SERIES/);
  });

  it('mask intervals preserve 1:1 sample semantics', () => {
    const m = buildSignalViewerModel({ window_identity: wi, raw, processed });
    expect(m.panels[0].mask_intervals).toHaveLength(1);
    expect(m.panels[1].mask_intervals).toHaveLength(1);
  });

  it('time alignment mismatch fails closed', () => {
    const p = buildSeries({
      kind: 'PROCESSED',
      values: new Array(30).fill(0),
      fs_hz: 2000,
      units: 'uV',
      source_ref: 'p',
      manifest_id: 'm'
    });
    expect(() => buildSignalViewerModel({ window_identity: wi, raw, processed: p })).toThrow(/TIME_ALIGNMENT_MISMATCH/);
  });

  it('large signal min-max decimation performance smoke test', () => {
    const values = Array.from({ length: 100000 }, (_, i) => Math.sin(i * 0.01));
    const s = buildSeries({ kind: 'RAW', values, fs_hz: 2000, units: 'uV', source_ref: 'big' });
    const t0 = performance.now();
    const out = decimateMinMax(toPoints(s), 2000);
    const elapsed = performance.now() - t0;
    
    expect(out.length).toBeLessThanOrEqual(2000);
    expect(elapsed).toBeLessThan(1000); // 1s threshold
  });
});

describe('Signal Viewer Rendering', () => {
  it('unknown units are displayed unknown rather than guessed', () => {
    const r = buildSeries({ kind: 'RAW', values: [1, 2, 3], fs_hz: 1000, units: null, source_ref: 's' });
    const p = buildSeries({ kind: 'PROCESSED', values: [1, 2, 3], fs_hz: 1000, units: null, source_ref: 'p', manifest_id: 'm' });
    const m = buildSignalViewerModel({
      window_identity: { ...wi, start_sample: 0, end_sample_exclusive: 3, context_start_sample: 0, context_end_sample_exclusive: 3, sampling_rate_hz: 1000 },
      raw: r,
      processed: p
    });
    
    const { container } = render(<SignalViewer model={m} />);
    expect(container.textContent).toMatch(/UNKNOWN_UNIT/);
    expect(container.textContent).toMatch(/fs: 1000 Hz/);
    expect(container.textContent).not.toMatch(/unit: uV/);
  });

  it('evidence references and profile are navigable/visible', () => {
    const { container } = render(<SignalViewer model={buildSignalViewerModel({ window_identity: wi, raw, processed })} />);
    
    expect(container.querySelector('a[href="#evidence-src_sha256_demo"]')).not.toBeNull();
    expect(container.querySelector('a[href="#manifest-pman_sha256_demo"]')).not.toBeNull();
    expect(container.textContent).toMatch(/research-v0.1/);
  });

  it('discloses visual decimation without changing analysis semantics', () => {
    const values = Array.from({ length: 50 }, (_, i) => Math.sin(i));
    const r = buildSeries({ kind: 'RAW', values, fs_hz: 1000, units: 'uV', source_ref: 'r' });
    const p = buildSeries({ kind: 'PROCESSED', values, fs_hz: 1000, units: 'uV', source_ref: 'p', manifest_id: 'm' });
    const { container } = render(<SignalViewer model={buildSignalViewerModel({ window_identity: { ...wi, start_sample: 0, end_sample_exclusive: 50, context_start_sample: 0, context_end_sample_exclusive: 50, sampling_rate_hz: 1000 }, raw: r, processed: p, max_points: 10 })} />);

    expect(container.textContent).toMatch(/Rendered points:/);
    expect(container.textContent).toMatch(/Visual decimation only/);
  });

  it('rendered figures label series kind explicitly', () => {
    const { container } = render(<SignalViewer model={buildSignalViewerModel({ window_identity: wi, raw, processed })} />);
    
    expect(container.querySelector('[data-series-kind="RAW"]')).not.toBeNull();
    expect(container.querySelector('[data-series-kind="PROCESSED"]')).not.toBeNull();
    expect(container.textContent).not.toMatch(/diagnosis|pathology/i);
  });
});
