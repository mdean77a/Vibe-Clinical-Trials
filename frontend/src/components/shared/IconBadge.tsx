import React from 'react';

type BadgeSize = 'sm' | 'md' | 'lg';

interface IconBadgeProps {
  children: React.ReactNode;
  size?: BadgeSize;
  backgroundColor?: string;
}

const sizeMap = {
  sm: { width: '40px', height: '40px', fontSize: '1.125rem' },
  md: { width: '64px', height: '64px', fontSize: '2rem' },
  lg: { width: '80px', height: '80px', fontSize: '2.5rem' }
};

/**
 * Reusable circular icon badge with size variants
 */
export default function IconBadge({
  children,
  size = 'md',
  backgroundColor = '#e9d5ff'
}: IconBadgeProps) {
  const dimensions = sizeMap[size];

  return (
    <div style={{
      width: dimensions.width,
      height: dimensions.height,
      background: backgroundColor,
      borderRadius: '50%',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      margin: '0 auto 24px'
    }}>
      <span style={{ fontSize: dimensions.fontSize }}>
        {children}
      </span>
    </div>
  );
}
