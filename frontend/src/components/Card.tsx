import React from 'react';

interface CardProps {
  children: React.ReactNode;
  className?: string;
  style?: React.CSSProperties;
}

const Card: React.FC<CardProps> = ({ children, className = '', style }) => {
  return (
    <div className={`p-4 bg-white shadow rounded ${className}`} style={style}>
      {children}
    </div>
  );
};

export default Card;
