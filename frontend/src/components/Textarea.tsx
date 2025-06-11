import React from 'react';

interface TextareaProps {
  placeholder?: string;
  value?: string;
  onChange?: (e: React.ChangeEvent<HTMLTextAreaElement>) => void;
  className?: string;
}

const Textarea: React.FC<TextareaProps> = ({ placeholder, value, onChange, className = '' }) => {
  return (
    <textarea
      placeholder={placeholder}
      value={value}
      onChange={onChange}
      className={`px-3 py-2 border rounded ${className}`}
    />
  );
};

export default Textarea;
