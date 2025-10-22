import React from 'react';

interface DashboardContainerProps {
  children: React.ReactNode;
  maxWidth?: string;
}

/**
 * Reusable container for dashboard pages
 * Provides consistent padding, centering, and responsive layout
 */
export default function DashboardContainer({
  children,
  maxWidth = '1024px'
}: DashboardContainerProps) {
  return (
    <div style={{
      padding: '24px',
      maxWidth,
      margin: '0 auto',
      minHeight: '100vh'
    }}>
      {children}
    </div>
  );
}
