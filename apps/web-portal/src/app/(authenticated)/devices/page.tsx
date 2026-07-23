/**
 * Devices Page — `/devices`
 */
'use client';

import { Cpu, Plus, CheckCircle, XCircle, Clock } from 'lucide-react';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { Card, CardContent } from '@/components/ui/Card';

const MOCK_DEVICES = [
  { id: 'DEV-001', name: 'Noraxon Ultium EMG', type: 'sEMG Sensor', channels: 8, status: 'active', firmware: 'v3.2.1', lastCalibrated: '2026-07-20' },
  { id: 'DEV-002', name: 'Noraxon Ultium EMG (Unit 2)', type: 'sEMG Sensor', channels: 4, status: 'maintenance', firmware: 'v3.2.0', lastCalibrated: '2026-07-15' },
  { id: 'DEV-003', name: 'MyoLab Mock Adapter', type: 'Software Adapter', channels: 8, status: 'active', firmware: 'v1.0.0-mock', lastCalibrated: 'N/A' },
];

export default function DevicesPage() {
  return (
    <div className="page-container">
      <div className="page-header">
        <div className="page-header__left">
          <h1 className="page-title">Thiết bị</h1>
          <p className="page-subtitle">Quản lý thiết bị sEMG và adapter kết nối.</p>
        </div>
        <div className="page-header__right">
          <Button icon={<Plus size={16} />} variant="secondary">Thêm thiết bị</Button>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', gap: 'var(--space-4)' }}>
        {MOCK_DEVICES.map((dev) => (
          <Card key={dev.id} padding="md" hoverable>
            <CardContent>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 'var(--space-3)' }}>
                <Cpu size={24} style={{ color: 'var(--color-primary)' }} />
                <Badge variant={dev.status === 'active' ? 'success' : 'warning'} size="sm">
                  {dev.status === 'active' ? 'Active' : 'Maintenance'}
                </Badge>
              </div>
              <h3 style={{ fontSize: 'var(--font-size-md)', fontWeight: 600, marginBottom: 'var(--space-2)' }}>{dev.name}</h3>
              <div style={{ fontSize: 'var(--font-size-xs)', color: 'var(--color-text-muted)', display: 'flex', flexDirection: 'column', gap: '4px' }}>
                <span>ID: {dev.id}</span>
                <span>Loại: {dev.type}</span>
                <span>Kênh: {dev.channels}</span>
                <span>Firmware: {dev.firmware}</span>
                <span>Calibrated: {dev.lastCalibrated}</span>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
