import React from 'react';

interface GradientButtonProps {
  onClick: () => void;
  disabled?: boolean;
  children: React.ReactNode;
  variant?: 'primary' | 'secondary';
}

/**
 * Reusable gradient button with hover states
 * Primary variant uses purple gradient, secondary uses gray
 */
export default function GradientButton({
  onClick,
  disabled = false,
  children,
  variant = 'primary'
}: GradientButtonProps) {
  const gradients = {
    primary: {
      default: 'linear-gradient(to right, #8b5cf6, #7c3aed)',
      hover: 'linear-gradient(to right, #7c3aed, #6d28d9)'
    },
    secondary: {
      default: 'linear-gradient(to right, #d1d5db, #9ca3af)',
      hover: 'linear-gradient(to right, #9ca3af, #6b7280)'
    }
  };

  const gradient = gradients[variant];

  return (
    <button
      onClick={onClick}
      disabled={disabled}
      style={{
        background: gradient.default,
        color: 'white',
        fontWeight: '600',
        padding: '16px 32px',
        borderRadius: '8px',
        border: 'none',
        cursor: disabled ? 'not-allowed' : 'pointer',
        fontSize: '1rem',
        opacity: disabled ? 0.6 : 1,
        transition: 'all 0.2s',
        boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
      }}
      onMouseEnter={(e) => {
        if (!disabled) {
          e.currentTarget.style.background = gradient.hover;
        }
      }}
      onMouseLeave={(e) => {
        if (!disabled) {
          e.currentTarget.style.background = gradient.default;
        }
      }}
    >
      {children}
    </button>
  );
}
