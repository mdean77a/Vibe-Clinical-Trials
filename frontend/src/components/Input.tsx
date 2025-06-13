import React from 'react';

interface InputProps {
  type?: string;
  placeholder?: string;
  value?: string;
  onChange?: (e: React.ChangeEvent<HTMLInputElement>) => void;
  className?: string;
  disabled?: boolean;
  style?: React.CSSProperties;
}

const Input: React.FC<InputProps> = ({ type = 'text', placeholder, value, onChange, className = '', disabled = false, style }) => {
  return (
    <input
      type={type}
      placeholder={placeholder}
      value={value}
      onChange={onChange}
      disabled={disabled}
      className={`px-3 py-2 border rounded ${className}`}
      style={style}
    />
  );
};

export default Input;
