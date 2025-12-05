import React from 'react';
import Button from '@/components/Button';

interface BackToSelectionButtonProps {
  onClick: () => void;
}

/**
 * Reusable "Back to Document Selection" button
 * Used across dashboard components for consistent navigation
 */
export default function BackToSelectionButton({ onClick }: BackToSelectionButtonProps) {
  const handleClick = () => {
    console.log('[BackToSelectionButton] Button clicked');
    console.log('[BackToSelectionButton] onClick handler:', onClick);

    if (onClick) {
      onClick();
    } else {
      console.error('[BackToSelectionButton] No onClick handler provided!');
    }
  };

  return (
    <Button
      onClick={handleClick}
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
  );
}
