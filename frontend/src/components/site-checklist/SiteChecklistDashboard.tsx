import React from 'react';
import Card from '@/components/Card';
import Button from '@/components/Button';
import DashboardContainer from '@/components/shared/DashboardContainer';
import ProtocolInfoCard from '@/components/shared/ProtocolInfoCard';
import BackToSelectionButton from '@/components/shared/BackToSelectionButton';
import type { Protocol } from '@/types/protocol';

interface SiteChecklistDashboardProps {
  protocol: Protocol;
  onReturnToSelection: () => void;
}

/**
 * Dashboard for site initiation checklist generation
 * Currently displays "Coming Soon" placeholder UI
 */
export default function SiteChecklistDashboard({
  protocol,
  onReturnToSelection
}: SiteChecklistDashboardProps) {
  const handleMakeChecklist = () => {
    alert('This is not yet implemented.');
  };

  return (
    <DashboardContainer>
      <div style={{ textAlign: 'center', marginBottom: '32px' }}>
        <h1 style={{
          fontSize: '2.5rem',
          fontWeight: 'bold',
          background: 'linear-gradient(to right, #2563eb, #9333ea)',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent',
          backgroundClip: 'text',
          marginBottom: '8px'
        }}>
          Site Initiation Checklist
        </h1>
        <p style={{ color: '#6b7280', fontSize: '1.125rem' }}>
          Generate comprehensive site initiation checklists
        </p>
      </div>

      <ProtocolInfoCard protocol={protocol} />

      <Card>
        <div style={{
          padding: '48px',
          textAlign: 'center',
          background: 'white',
          border: '1px solid #e5e7eb',
          borderRadius: '12px'
        }}>
          <div style={{
            width: '80px',
            height: '80px',
            background: '#ddd6fe',
            borderRadius: '50%',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            margin: '0 auto 24px'
          }}>
            <span style={{ color: '#7c3aed', fontSize: '2.5rem' }}>✅</span>
          </div>

          <h2 style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#1f2937', marginBottom: '16px' }}>
            Coming Soon
          </h2>

          <p style={{ color: '#6b7280', marginBottom: '32px', maxWidth: '600px', margin: '0 auto 32px' }}>
            The Site Initiation Checklist feature is currently and perpetually, I might add, under development.
            This will generate comprehensive checklists to ensure all necessary steps
            are completed before initiating a clinical trial at each clinical site.
          </p>

          <div style={{ display: 'flex', gap: '16px', justifyContent: 'center' }}>
            <Button
              onClick={handleMakeChecklist}
              style={{
                background: 'linear-gradient(to right, #d1d5db, #9ca3af)',
                color: 'white',
                fontWeight: '600',
                padding: '12px 24px',
                borderRadius: '8px',
                boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
                border: 'none',
                cursor: 'not-allowed',
                opacity: 0.6
              }}
              disabled
            >
              Generate Checklist (Coming Soon)
            </Button>

            <BackToSelectionButton onClick={onReturnToSelection} />
          </div>
        </div>
      </Card>
    </DashboardContainer>
  );
}