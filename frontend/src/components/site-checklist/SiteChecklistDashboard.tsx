import React from 'react';
import Card from '@/components/Card';
import Button from '@/components/Button';
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
    <div style={{
      padding: '24px',
      maxWidth: '1024px',
      margin: '0 auto',
      minHeight: '100vh'
    }}>
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

      <Card style={{ marginBottom: '24px' }}>
        <div style={{
          padding: '16px',
          background: 'linear-gradient(to right, #faf5ff, #f3e8ff)',
          border: '1px solid #d8b4fe',
          borderRadius: '12px',
          boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1)'
        }}>
          <div style={{ display: 'flex', alignItems: 'center' }}>
            <div style={{
              width: '40px',
              height: '40px',
              background: '#e9d5ff',
              borderRadius: '50%',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              marginRight: '12px'
            }}>
              <span style={{ color: '#8b5cf6', fontWeight: '600', fontSize: '0.875rem' }}>
                {protocol.study_acronym.substring(0, 2).toUpperCase()}
              </span>
            </div>
            <div>
              <p style={{ color: '#7c3aed', fontWeight: '600' }}>
                {protocol.study_acronym}
              </p>
              <p style={{ color: '#6d28d9', fontSize: '0.875rem' }}>
                {protocol.protocol_title}
              </p>
            </div>
          </div>
        </div>
      </Card>

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

            <Button
              onClick={onReturnToSelection}
              style={{
                background: 'linear-gradient(to right, #6b7280, #4b5563)',
                color: 'white',
                fontWeight: '600',
                padding: '12px 24px',
                borderRadius: '8px',
                boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
                border: 'none',
                cursor: 'pointer',
                transition: 'all 0.2s'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.background = 'linear-gradient(to right, #4b5563, #374151)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.background = 'linear-gradient(to right, #6b7280, #4b5563)';
              }}
            >
              ← Back to Document Selection
            </Button>
          </div>
        </div>
      </Card>
    </div>
  );
}