import React from 'react';
import Card from '@/components/Card';
import DashboardContainer from '@/components/shared/DashboardContainer';
import DashboardHeader from '@/components/shared/DashboardHeader';
import ProtocolInfoCard from '@/components/shared/ProtocolInfoCard';
import IconBadge from '@/components/shared/IconBadge';
import ActionButtonRow from '@/components/shared/ActionButtonRow';
import GradientButton from '@/components/shared/GradientButton';
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
      <DashboardHeader
        title="Site Initiation Checklist"
        subtitle="Generate comprehensive site initiation checklists"
      />

      <ProtocolInfoCard protocol={protocol} />

      <Card>
        <div style={{
          padding: '48px',
          textAlign: 'center',
          background: 'white',
          border: '1px solid #e5e7eb',
          borderRadius: '12px'
        }}>
          <IconBadge size="lg" backgroundColor="#ddd6fe">
            <span style={{ color: '#7c3aed' }}>✅</span>
          </IconBadge>

          <h2 style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#1f2937', marginBottom: '16px' }}>
            Coming Soon
          </h2>

          <p style={{ color: '#6b7280', marginBottom: '32px', maxWidth: '600px', margin: '0 auto 32px' }}>
            The Site Initiation Checklist feature is currently and perpetually, I might add, under development.
            This will generate comprehensive checklists to ensure all necessary steps
            are completed before initiating a clinical trial at each clinical site.
          </p>

          <ActionButtonRow>
            <GradientButton
              onClick={handleMakeChecklist}
              disabled
              variant="secondary"
            >
              Generate Checklist (Coming Soon)
            </GradientButton>

            <BackToSelectionButton onClick={onReturnToSelection} />
          </ActionButtonRow>
        </div>
      </Card>
    </DashboardContainer>
  );
}