export type IssueCategory = 'qc_warning' | 'qc_fail' | 'import_error' | 'device_disconnect' | 'protocol_violation';
export type IssueStatus = 'open' | 'investigating' | 'resolved' | 'ignored';

export interface DataQualityIssue {
  id: string;
  category: IssueCategory;
  sessionId: string;
  importId?: string;
  
  description: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  
  // E.g., reason codes from QC
  reasonCodes: string[];
  
  status: IssueStatus;
  createdAt: string;
  resolvedAt?: string;
}
