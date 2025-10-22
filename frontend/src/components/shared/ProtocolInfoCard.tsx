import React from 'react';
import Card from '@/components/Card';
import type { Protocol } from '@/types/protocol';

interface ProtocolInfoCardProps {
  protocol: Protocol;
}

/**
 * Reusable protocol information card
 * Displays study acronym and protocol title with purple gradient styling
 */
export default function ProtocolInfoCard({ protocol }: ProtocolInfoCardProps) {
  return (
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
  );
}
