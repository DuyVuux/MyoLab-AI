/**
 * Common domain types shared across schemas.
 * Per spec Section 4–6.
 */

export type Side = 'Left' | 'Right' | 'Bilateral';

export type ConsentScope =
  | 'quality_improvement'
  | 'model_training'
  | 'research_export';

export type DataSourceType =
  | 'synthetic'
  | 'csv_json'
  | 'noraxon_mock'
  | 'deidentified_replay'
  | 'live_stream';

export type FunctionalRole =
  | 'agonist'
  | 'antagonist'
  | 'synergist'
  | 'stabilizer'
  | 'reference'
  | 'unknown';

export type ElectrodePosition =
  | 'belly'
  | 'distal_third'
  | 'proximal_third'
  | 'reference_bony'
  | 'custom';

export interface ElectrodeLayout {
  muscleId: string;
  muscle: string;
  side: Side;
  electrodePosition: ElectrodePosition;
  interElectrodeDistance: number; // mm
}

export interface AuditEntry {
  id: string;
  timestamp: string;
  actor: string;
  actorRole: string;
  action: string;
  resource: string;
  detail: string;
}

export type SessionType = 'baseline' | 'follow_up' | 'replay' | 'research';

export const CANONICAL_MUSCLES = [
  'Flexor carpi radialis',
  'Extensor carpi radialis',
  'Biceps brachii',
  'Upper trapezius',
  'Flexor digitorum superficialis',
  'Extensor digitorum communis',
  'Deltoid (anterior)',
  'Triceps brachii',
  'Pronator teres',
  'Supinator',
] as const;

export type CanonicalMuscle = (typeof CANONICAL_MUSCLES)[number];

export const UNITS = ['mV', 'µV', 'V', 'unknown'] as const;
export type SignalUnit = (typeof UNITS)[number];
