import { WindowIdentity, Series, Point, MaskInterval, SignalViewerModel } from './types';

export type BuiltSeries = Omit<
  Required<Series>,
  'mask' | 'units' | 'manifest_id' | 'profile_id'
> & {
  readonly units: string;
  readonly manifest_id: string | null;
  readonly profile_id: string | null;
  readonly mask: boolean[];
};

export function finiteOrNull(v: number | null | undefined): number | null {
  return typeof v === 'number' && Number.isFinite(v) ? v : null;
}

export function validateWindowIdentity(w: Partial<WindowIdentity>): boolean {
  const required: (keyof WindowIdentity)[] = [
    'window_id', 'session_id', 'channel_id', 'source_id',
    'start_sample', 'end_sample_exclusive',
    'context_start_sample', 'context_end_sample_exclusive',
    'sampling_rate_hz'
  ];
  
  for (const key of required) {
    if (w?.[key] === undefined || w?.[key] === null) {
      throw new Error(`WINDOW_IDENTITY_MISSING_${key.toUpperCase()}`);
    }
  }
  
  if (!(w.end_sample_exclusive! > w.start_sample!)) throw new Error('WINDOW_IDENTITY_RANGE_INVALID');
  if (!(w.context_start_sample! <= w.start_sample! && w.context_end_sample_exclusive! >= w.end_sample_exclusive!)) throw new Error('WINDOW_CONTEXT_INVALID');
  if (!(w.sampling_rate_hz! > 0)) throw new Error('WINDOW_FS_INVALID');
  
  return true;
}

export function buildSeries(params: Series): BuiltSeries {
  const { kind, values, fs_hz, units, source_ref, manifest_id = null, profile_id = null, mask = null, start_time_s = 0 } = params;
  
  if (!['RAW', 'PROCESSED'].includes(kind)) throw new Error('SERIES_KIND_REQUIRED_RAW_OR_PROCESSED');
  if (!(fs_hz > 0)) throw new Error('SERIES_FS_REQUIRED');
  if (!Array.isArray(values) || values.length < 2) throw new Error('SERIES_VALUES_REQUIRED');
  if (mask != null && (!Array.isArray(mask) || mask.length !== values.length)) throw new Error('MASK_ALIGNMENT_INVALID');
  if (kind === 'PROCESSED' && !manifest_id) throw new Error('PROCESSED_SERIES_REQUIRES_MANIFEST_ID');
  
  return {
    kind,
    fs_hz,
    units: units ?? 'UNKNOWN_UNIT',
    source_ref,
    manifest_id,
    profile_id,
    start_time_s,
    values: values.map(finiteOrNull),
    mask: mask ? [...mask] : values.map(() => false),
  };
}

export function toPoints(series: BuiltSeries): Point[] {
  return series.values.map((y, i) => ({
    x: series.start_time_s + i / series.fs_hz,
    y: y as number,
    masked: Boolean(series.mask[i])
  }));
}

export function decimateMinMax(points: Point[], maxPoints: number = 2000): Point[] {
  if (points.length <= maxPoints) return points;
  if (maxPoints < 4) throw new Error('MAX_POINTS_TOO_SMALL');
  
  const bucket = Math.ceil(points.length / (maxPoints / 2));
  const out: Point[] = [];
  
  for (let i = 0; i < points.length; i += bucket) {
    const slice = points.slice(i, Math.min(points.length, i + bucket));
    let min: Point | null = null, max: Point | null = null;
    
    for (const p of slice) {
      if (p.y == null) continue;
      if (min == null || p.y < min.y) min = p;
      if (max == null || p.y > max.y) max = p;
    }
    
    if (min == null && max == null) { out.push(slice[0]); continue; }
    if (min && max && min.x <= max.x) { out.push(min); if (max !== min) out.push(max); }
    else { if (max) out.push(max); if (min && min !== max) out.push(min); }
  }
  
  return out.slice(0, maxPoints);
}

export function maskIntervals(series: BuiltSeries): MaskInterval[] {
  const intervals: MaskInterval[] = [];
  let start: number | null = null;
  
  for (let i = 0; i < series.mask.length; i++) {
    if (series.mask[i] && start === null) start = i;
    if ((!series.mask[i] || i === series.mask.length - 1) && start !== null) {
      const end = series.mask[i] && i === series.mask.length - 1 ? i + 1 : i;
      intervals.push({
        start_s: series.start_time_s + start / series.fs_hz,
        end_s: series.start_time_s + end / series.fs_hz
      });
      start = null;
    }
  }
  
  return intervals;
}

export function buildSignalViewerModel({ window_identity, raw, processed, max_points = 2000 }: { window_identity: WindowIdentity, raw: BuiltSeries, processed: BuiltSeries, max_points?: number }): SignalViewerModel {
  validateWindowIdentity(window_identity);
  if (raw.kind !== 'RAW') throw new Error('RAW_PANEL_REQUIRES_RAW_SERIES');
  if (processed.kind !== 'PROCESSED') throw new Error('PROCESSED_PANEL_REQUIRES_PROCESSED_SERIES');
  
  const rawDuration = (raw.values.length - 1) / raw.fs_hz;
  const processedDuration = (processed.values.length - 1) / processed.fs_hz;
  const tolerance = Math.max(1 / raw.fs_hz, 1 / processed.fs_hz) * 2;
  
  if (Math.abs(rawDuration - processedDuration) > tolerance) throw new Error('RAW_PROCESSED_TIME_ALIGNMENT_MISMATCH');
  
  return {
    claim_scope: 'RESEARCH_ONLY',
    window_identity: { ...window_identity },
    panels: [
      {
        kind: 'RAW',
        units: raw.units,
        fs_hz: raw.fs_hz,
        source_ref: raw.source_ref,
        manifest_id: null,
        profile_id: null,
        points: decimateMinMax(toPoints(raw), max_points),
        source_sample_count: raw.values.length,
        mask_intervals: maskIntervals(raw),
      },
      {
        kind: 'PROCESSED',
        units: processed.units,
        fs_hz: processed.fs_hz,
        source_ref: processed.source_ref,
        manifest_id: processed.manifest_id,
        profile_id: processed.profile_id,
        points: decimateMinMax(toPoints(processed), max_points),
        source_sample_count: processed.values.length,
        mask_intervals: maskIntervals(processed),
      },
    ],
  };
}
