/**
 * Data Quality Issues Page — `/data-quality/issues`
 * Dashboard for Data Quality issues (QC failures, import errors, device sync).
 */
'use client';

import { useState, useEffect } from 'react';
import { ShieldAlert, CheckCircle, Search, Filter, AlertTriangle } from 'lucide-react';
import { Card, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { Input } from '@/components/ui/Input';
import * as MockWorkflowRepository from '@/services/mock/MockWorkflowRepository';
import type { DataQualityIssue } from '@/schemas/issue';
import { RoleGuard } from '@/components/auth/RoleGuard';
import styles from './issues.module.css';

export default function DataQualityIssuesPage() {
  const [loading, setLoading] = useState(true);
  const [issues, setIssues] = useState<DataQualityIssue[]>([]);

  useEffect(() => {
    let list = MockWorkflowRepository.getIssues();
    if (list.length === 0) {
      // Mock initial data
      const mockIssue1: DataQualityIssue = {
        id: `DQI-${Date.now()}-1`,
        sessionId: 'S-DEMO-123',
        category: 'qc_fail',
        reasonCodes: ['50HZ_NOISE'],
        severity: 'high',
        description: 'Tỷ lệ nhiễu điện lưới (50Hz) vượt ngưỡng 30% trong suốt phiên đo.',
        status: 'open',
        createdAt: new Date().toISOString()
      };
      const mockIssue2: DataQualityIssue = {
        id: `DQI-${Date.now()}-2`,
        sessionId: 'S-DEMO-123',
        importId: 'IMP-001',
        category: 'import_error',
        reasonCodes: ['MISSING_META'],
        severity: 'medium',
        description: 'File European_Dataset.edf thiếu thông tin Protocol ID.',
        status: 'resolved',
        createdAt: new Date(Date.now() - 86400000).toISOString(),
        resolvedAt: new Date().toISOString()
      };
      MockWorkflowRepository.saveIssue(mockIssue1);
      MockWorkflowRepository.saveIssue(mockIssue2);
      list = [mockIssue1, mockIssue2];
    }
    setIssues(list.sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime()));
    setLoading(false);
  }, []);

  if (loading) return <div className="page-container">Đang tải...</div>;

  return (
    <RoleGuard allowedRoles={['ktv', 'doctor', 'researcher', 'admin']}>
      <div className="page-container">
        <div className="page-header">
          <div className="page-header__left">
            <h1 className="page-title">Data Quality Issues</h1>
            <p className="page-subtitle">Quản lý các vấn đề chất lượng dữ liệu phát sinh (QC Warnings/Errors).</p>
          </div>
        </div>

      <div className={styles.controls}>
        <Input label="Tìm kiếm" placeholder="Tìm kiếm theo Issue ID hoặc Session ID..." className={styles.search} />
        <Button variant="secondary" icon={<Filter size={16} />}>Lọc (Open)</Button>
      </div>

      <div className={styles.list}>
        {issues.map(issue => (
          <Card key={issue.id} padding="md" className={styles.issueCard}>
            <div className={styles.issueHeader}>
              <div className={styles.titleRow}>
                {issue.severity === 'high' ? <ShieldAlert size={18} className={styles.iconHigh} /> : <AlertTriangle size={18} className={styles.iconMed} />}
                <strong>{issue.id}</strong>
                <Badge variant={issue.status === 'open' ? 'error' : 'success'}>{issue.status.toUpperCase()}</Badge>
              </div>
              <span className={styles.date}>{new Date(issue.createdAt).toLocaleString('vi-VN')}</span>
            </div>
            
            <div className={styles.issueBody}>
              <p><strong>Danh mục lỗi:</strong> {issue.category.toUpperCase()}</p>
              <p><strong>Nguồn (Session):</strong> {issue.sessionId}</p>
              <p><strong>Mô tả:</strong> {issue.description}</p>
            </div>

            {issue.status === 'resolved' && (
              <div className={styles.resolution}>
                <CheckCircle size={14} className={styles.iconSuccess} />
                <span><strong>Đã giải quyết</strong></span>
                <span className={styles.resolvedDate}>({issue.resolvedAt ? new Date(issue.resolvedAt).toLocaleDateString('vi-VN') : ''})</span>
              </div>
            )}
            
            {issue.status === 'open' && (
              <div className={styles.actions}>
                <Button variant="secondary" size="sm">Mark as Resolved</Button>
              </div>
            )}
          </Card>
        ))}
      </div>
      </div>
    </RoleGuard>
  );
}
