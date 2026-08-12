export interface WindowIdentity {
  window_id: string;
  session_id: string;
  channel_id: string;
  source_id: string;
  start_sample: number;
  end_sample_exclusive: number;
  context_start_sample: number;
  context_end_sample_exclusive: number;
  sampling_rate_hz: number;
}

export type SeriesKind = 'RAW' | 'PROCESSED';

export interface Series {
  kind: SeriesKind;
  values: (number | null)[];
  fs_hz: number;
  units?: string | null;
  source_ref: string;
  manifest_id?: string | null;
  profile_id?: string | null;
  mask?: boolean[] | null;
  start_time_s?: number;
}

export interface MaskInterval {
  start_s: number;
  end_s: number;
}

export interface Point {
  x: number;
  y: number;
  masked?: boolean;
}

export interface PanelModel {
  kind: SeriesKind;
  units: string;
  source_ref: string;
  manifest_id: string | null;
  profile_id: string | null;
  points: Point[];
  mask_intervals: MaskInterval[];
}

export interface SignalViewerModel {
  claim_scope: 'RESEARCH_ONLY';
  window_identity: WindowIdentity;
  panels: PanelModel[];
}
