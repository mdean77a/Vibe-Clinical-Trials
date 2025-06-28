import React, { useState } from 'react';
import Card from './Card';
import Button from './Button';
import type { Protocol } from '../types/protocol';
import { getProtocolId } from '../types/protocol';

interface ProtocolSelectorProps {
  protocols: Protocol[];
  onProtocolSelect: (protocol: Protocol) => void;
  onUploadNew: () => void;
}

const ProtocolSelector: React.FC<ProtocolSelectorProps> = ({ 
  protocols, 
  onProtocolSelect, 
  onUploadNew
}) => {
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);

  const handleProtocolClick = (protocol: Protocol) => {
    setIsDropdownOpen(false);
    // Immediately trigger selection and navigation
    onProtocolSelect(protocol);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: 'numeric',
      minute: '2-digit',
      hour12: true
    });
  };

  const truncateText = (text: string, maxLength: number) => {
    return text.length > maxLength 
      ? text.substring(0, maxLength) + '...' 
      : text;
  };

  const truncateAcronym = (acronym: string) => {
    return truncateText(acronym, 15);
  };

  const truncateFilename = (title: string, maxLength: number = 35) => {
    return truncateText(title, maxLength);
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      <div style={{ textAlign: 'center' }}>
        <h2 style={{ fontSize: '1.5rem', fontWeight: '600', color: '#1f2937', marginBottom: '8px' }}>
          Select Protocol
        </h2>
        <p style={{ color: '#6b7280' }}>
          Choose an existing protocol or upload a new one to get started
        </p>
      </div>

      <Card>
        <div style={{
          padding: '32px',
          background: 'white',
          border: '1px solid #d8b4fe',
          borderRadius: '12px',
          boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1)'
        }}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
            <div>
              <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: '600', color: '#374151', marginBottom: '8px' }}>
                Existing Protocols
              </label>
              <div style={{ position: 'relative' }}>
                <button
                  onClick={() => setIsDropdownOpen(!isDropdownOpen)}
                  disabled={protocols.length === 0}
                  style={{
                    width: '100%',
                    background: 'white',
                    border: '1px solid #d1d5db',
                    borderRadius: '8px',
                    padding: '12px 16px',
                    textAlign: 'left',
                    boxShadow: '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
                    cursor: protocols.length > 0 ? 'pointer' : 'not-allowed',
                    transition: 'all 0.2s',
                    fontSize: '0.875rem'
                  }}
                  onMouseEnter={(e) => {
                    if (protocols.length > 0) {
                      e.currentTarget.style.borderColor = '#9ca3af';
                    }
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.borderColor = '#d1d5db';
                  }}
                  onFocus={(e) => {
                    if (protocols.length > 0) {
                      e.currentTarget.style.outline = '2px solid #8b5cf6';
                      e.currentTarget.style.outlineOffset = '2px';
                      e.currentTarget.style.borderColor = '#8b5cf6';
                    }
                  }}
                  onBlur={(e) => {
                    e.currentTarget.style.outline = 'none';
                    e.currentTarget.style.borderColor = '#d1d5db';
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                    <span style={{ color: '#6b7280' }}>
                      {protocols.length > 0 
                        ? 'Select a protocol...'
                        : 'No existing protocols found'
                      }
                    </span>
                    {protocols.length > 0 && (
                      <svg 
                        style={{
                          width: '20px',
                          height: '20px',
                          color: '#9ca3af',
                          transition: 'transform 0.2s',
                          transform: isDropdownOpen ? 'rotate(180deg)' : 'rotate(0deg)'
                        }}
                        fill="none" 
                        stroke="currentColor" 
                        viewBox="0 0 24 24"
                      >
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                      </svg>
                    )}
                  </div>
                </button>

                {isDropdownOpen && protocols.length > 0 && (
                  <div style={{
                    position: 'absolute',
                    zIndex: 10,
                    width: '100%',
                    marginTop: '4px',
                    background: 'white',
                    border: '1px solid #d1d5db',
                    borderRadius: '8px',
                    boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1)',
                    maxHeight: '240px',
                    overflowY: 'auto'
                  }}>
                    {protocols.map((protocol, index) => (
                      <button
                        key={getProtocolId(protocol)}
                        onClick={() => handleProtocolClick(protocol)}
                        style={{
                          width: '100%',
                          padding: '12px 16px',
                          textAlign: 'left',
                          background: 'white',
                          border: 'none',
                          borderBottom: index < protocols.length - 1 ? '1px solid #f3f4f6' : 'none',
                          cursor: 'pointer',
                          transition: 'background-color 0.2s',
                          fontSize: '0.875rem'
                        }}
                        onMouseEnter={(e) => {
                          e.currentTarget.style.background = '#faf5ff';
                        }}
                        onMouseLeave={(e) => {
                          e.currentTarget.style.background = 'white';
                        }}
                        onFocus={(e) => {
                          e.currentTarget.style.background = '#faf5ff';
                          e.currentTarget.style.outline = 'none';
                        }}
                      >
                        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', width: '100%', fontFamily: 'monospace' }}>
                          <div style={{ display: 'flex', alignItems: 'center', flex: 1, minWidth: 0 }}>
                            <span style={{ fontWeight: '600', color: '#1f2937', width: '17ch', flexShrink: 0, display: 'inline-block' }}>
                              {truncateAcronym(protocol.study_acronym)}
                            </span>
                            <span style={{ fontSize: '0.75rem', color: '#6b7280', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                              {truncateFilename(protocol.protocol_title)}
                            </span>
                          </div>
                          <span style={{ fontSize: '0.75rem', color: '#6b7280', flexShrink: 0, marginLeft: '8px' }}>
                            {formatDate(protocol.upload_date)}
                          </span>
                        </div>
                      </button>
                    ))}
                  </div>
                )}
              </div>
            </div>

            <div style={{ position: 'relative' }}>
              <div style={{
                position: 'absolute',
                inset: 0,
                display: 'flex',
                alignItems: 'center'
              }}>
                <div style={{ width: '100%', borderTop: '1px solid #d1d5db' }} />
              </div>
              <div style={{
                position: 'relative',
                display: 'flex',
                justifyContent: 'center',
                fontSize: '0.875rem'
              }}>
                <span style={{ padding: '0 8px', background: 'white', color: '#6b7280' }}>or</span>
              </div>
            </div>

            <div style={{ textAlign: 'center' }}>
              <Button 
                onClick={onUploadNew}
                style={{
                  background: 'linear-gradient(to right, #8b5cf6, #7c3aed)',
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
                  e.currentTarget.style.background = 'linear-gradient(to right, #7c3aed, #6d28d9)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.background = 'linear-gradient(to right, #8b5cf6, #7c3aed)';
                }}
              >
                Upload New Protocol
              </Button>
              <p style={{ fontSize: '0.875rem', color: '#6b7280', marginTop: '8px' }}>
                Upload a new clinical trial protocol PDF with custom acronym
              </p>
            </div>
          </div>
        </div>
      </Card>
    </div>
  );
};

export default ProtocolSelector; 