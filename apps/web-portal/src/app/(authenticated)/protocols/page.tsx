/**
 * Protocols Page — `/protocols`
 */
'use client';

import { FileText, Plus, CheckCircle } from 'lucide-react';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { Card, CardContent } from '@/components/ui/Card';

const MOCK_PROTOCOLS = [
  { id: 'PROT-UC1-001', name: 'Gesture Recognition Standard', version: '1.2', useCase: 'UC1', channels: 4, status: 'published' },
  { id: 'PROT-UC1-002', name: 'Biofeedback Simplified', version: '1.0', useCase: 'UC1', channels: 4, status: 'published' },
  { id: 'PROT-UC2-001', name: 'Upper Limb Assessment Full', version: '2.0', useCase: 'UC2', channels: 8, status: 'published' },
  { id: 'PROT-UC2-002', name: 'Fatigue Monitoring Basic', version: '1.1', useCase: 'UC2', channels: 4, status: 'draft' },
  { id: 'PROT-UC3-001', name: 'Prosthetic Feasibility', version: '0.5', useCase: 'UC3', channels: 8, status: 'draft' },
  { id: 'PROT-UC4-001', name: 'Sterile HMI Feasibility', version: '0.3', useCase: 'UC4', channels: 4, status: 'draft' },
];

export default function ProtocolsPage() {
  return (
    <div className="page-container">
      <div className="page-header">
        <div className="page-header__left">
          <h1 className="page-title">Protocol</h1>
          <p className="page-subtitle">Quản lý protocol đánh giá cho các use case.</p>
        </div>
        <div className="page-header__right">
          <Button icon={<Plus size={16} />} variant="secondary">Tạo protocol mới</Button>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: 'var(--space-4)' }}>
        {MOCK_PROTOCOLS.map((p) => (
          <Card key={p.id} padding="md" hoverable>
            <CardContent>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 'var(--space-3)' }}>
                <FileText size={24} style={{ color: 'var(--color-primary)' }} />
                <div style={{ display: 'flex', gap: '8px' }}>
                  <Badge variant={p.useCase.includes('1') || p.useCase.includes('2') ? 'tier1' : 'tier2'} size="sm">{p.useCase}</Badge>
                  <Badge variant={p.status === 'published' ? 'success' : 'warning'} size="sm">{p.status}</Badge>
                </div>
              </div>
              <h3 style={{ fontSize: 'var(--font-size-md)', fontWeight: 600, marginBottom: 'var(--space-2)' }}>{p.name}</h3>
              <div style={{ fontSize: 'var(--font-size-xs)', color: 'var(--color-text-muted)', display: 'flex', flexDirection: 'column', gap: '4px' }}>
                <span>ID: {p.id}</span>
                <span>Version: v{p.version}</span>
                <span>Kênh yêu cầu: {p.channels}</span>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
