import React from 'react';

interface ActionButtonRowProps {
  children: React.ReactNode;
}

/**
 * Reusable horizontal flex container for button groups
 * Centers buttons with consistent spacing
 */
export default function ActionButtonRow({ children }: ActionButtonRowProps) {
  return (
    <div style={{ display: 'flex', gap: '16px', justifyContent: 'center' }}>
      {children}
    </div>
  );
}
