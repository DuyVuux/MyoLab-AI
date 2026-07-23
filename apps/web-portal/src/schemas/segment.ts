export interface SignalSegment {
  id: string; // e.g. SEG-001
  sessionId: string;
  analysisId: string;
  
  // Exact reference
  startSample: number;
  endSample: number;
  startTimeS: number;
  endTimeS: number;
  channelIds: string[];
  
  // Provenance
  sourceHash: string;
  calibrationId?: string;
  modelVersion: string;
  featureVersion: string;

  // AI Output
  targetGesture?: string;
  predictedGesture: string;
  engineeringConfidence: number; // 0.0 - 1.0 (Not clinical probability)
  fatigueIndex?: number;
  
  // Explainability & Context
  reasoning: string[];
  qualityContext: {
    hasQCWarning: boolean;
    reasonCodes: string[];
  };
}
