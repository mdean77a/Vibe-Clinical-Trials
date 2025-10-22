import React from 'react';

interface DashboardHeaderProps {
  title: string;
  subtitle: string;
}

/**
 * Reusable dashboard page header with gradient title and subtitle
 */
export default function DashboardHeader({ title, subtitle }: DashboardHeaderProps) {
  return (
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
        {title}
      </h1>
      <p style={{ color: '#6b7280', fontSize: '1.125rem' }}>
        {subtitle}
      </p>
    </div>
  );
}
