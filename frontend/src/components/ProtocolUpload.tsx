import React, { useState, useRef } from 'react';
import Card from './Card';
import Button from './Button';
import Input from './Input';
import { protocolsApi } from '../utils/api';

interface ProtocolUploadProps {
  onUploadComplete: (fileName: string, acronym: string) => void;
  onCancel: () => void;
}

const ProtocolUpload: React.FC<ProtocolUploadProps> = ({ 
  onUploadComplete, 
  onCancel 
}) => {
  const [isDragOver, setIsDragOver] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [acronym, setAcronym] = useState('');
  const fileInputRef = useRef<HTMLInputElement>(null);

  const validateFile = (file: File): string | null => {
    // Check file type
    if (file.type !== 'application/pdf') {
      return 'Please select a PDF file only.';
    }
    
    // Check file size (50MB max)
    const maxSize = 50 * 1024 * 1024; // 50MB in bytes
    if (file.size > maxSize) {
      return 'File size must be less than 50MB.';
    }
    
    return null;
  };

  const validateAcronym = (acronym: string): string | null => {
    if (!acronym.trim()) {
      return 'Protocol acronym is required.';
    }
    
    if (acronym.trim().length < 2) {
      return 'Protocol acronym must be at least 2 characters.';
    }
    
    if (acronym.trim().length > 20) {
      return 'Protocol acronym must be 20 characters or less.';
    }
    
    // Check for valid characters (letters, numbers, hyphens, underscores)
    if (!/^[A-Za-z0-9\-_]+$/.test(acronym.trim())) {
      return 'Protocol acronym can only contain letters, numbers, hyphens, and underscores.';
    }
    
    return null;
  };

  const handleFileUpload = async () => {
    if (!selectedFile) {
      setError('Please select a file first.');
      return;
    }

    const fileValidationError = validateFile(selectedFile);
    if (fileValidationError) {
      setError(fileValidationError);
      return;
    }

    const acronymValidationError = validateAcronym(acronym);
    if (acronymValidationError) {
      setError(acronymValidationError);
      return;
    }

    setError(null);
    setIsUploading(true);
    setUploadProgress(0);

    try {
      // Start upload progress animation
      const progressInterval = setInterval(() => {
        setUploadProgress(prev => {
          if (prev >= 85) {
            clearInterval(progressInterval);
            return 85;
          }
          return prev + 15;
        });
      }, 300);

      // Actual API call to upload and process the PDF
      await protocolsApi.upload(selectedFile, {
        study_acronym: acronym.trim().toUpperCase(),
        protocol_title: `Protocol ${acronym.trim().toUpperCase()}`,
      });

      clearInterval(progressInterval);
      setUploadProgress(100);
      
      // Complete upload successfully
      setTimeout(() => {
        onUploadComplete(selectedFile.name, acronym.trim().toUpperCase());
      }, 500);

    } catch (uploadError) {
      console.error('Upload error:', uploadError);
      setError(uploadError instanceof Error ? uploadError.message : 'Failed to upload and process protocol. Please try again.');
      setIsUploading(false);
      setUploadProgress(0);
    }
  };

  const handleFileSelect = (file: File) => {
    const validationError = validateFile(file);
    if (validationError) {
      setError(validationError);
      return;
    }
    
    setSelectedFile(file);
    setError(null);
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragOver(false);
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      handleFileSelect(files[0]);
    }
  };

  const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragOver(false);
  };

  const handleFileInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      handleFileSelect(files[0]);
    }
  };

  const handleBrowseClick = () => {
    fileInputRef.current?.click();
  };

  const handleRemoveFile = () => {
    setSelectedFile(null);
    setError(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div>
          <h2 style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#1f2937' }}>
            Upload New Protocol
          </h2>
          <p style={{ color: '#6b7280', marginTop: '4px' }}>
            Upload a clinical trial protocol PDF and provide an acronym
          </p>
        </div>
        <Button 
          onClick={onCancel}
          style={{
            color: '#6b7280',
            padding: '8px 16px',
            border: '1px solid #d1d5db',
            borderRadius: '8px',
            background: 'white',
            cursor: 'pointer',
            transition: 'all 0.2s'
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.color = '#374151';
            e.currentTarget.style.background = '#f9fafb';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.color = '#6b7280';
            e.currentTarget.style.background = 'white';
          }}
        >
          Back to Protocols
        </Button>
      </div>

      {/* Upload Form */}
      <Card>
        <div style={{
          padding: '32px',
          background: 'white',
          border: '1px solid #d8b4fe',
          borderRadius: '12px',
          boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1)',
          display: 'flex',
          flexDirection: 'column',
          gap: '24px'
        }}>
          {/* Protocol Acronym Input */}
          <div>
            <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: '600', color: '#374151', marginBottom: '8px' }}>
              Protocol Acronym *
            </label>
            <Input
              type="text"
              value={acronym}
              onChange={(e) => setAcronym(e.target.value)}
              placeholder="e.g., CARDIO-TRIAL, ONCO-STUDY"
              disabled={isUploading}
              style={{
                width: '100%',
                padding: '12px',
                border: '1px solid #d1d5db',
                borderRadius: '8px',
                fontSize: '1rem'
              }}
            />
            <p style={{ fontSize: '0.875rem', color: '#6b7280', marginTop: '4px' }}>
              Enter a short, memorable acronym for this protocol (2-20 characters, letters/numbers/hyphens/underscores only)
            </p>
          </div>

          {/* File Upload Area */}
          <div>
            <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: '600', color: '#374151', marginBottom: '8px' }}>
              Protocol Document *
            </label>
            
            {!selectedFile ? (
              <div
                style={{
                  border: '2px dashed ' + (isDragOver ? '#c084fc' : '#d1d5db'),
                  borderRadius: '8px',
                  padding: '48px',
                  textAlign: 'center',
                  transition: 'all 0.2s',
                  background: isDragOver ? '#faf5ff' : '#f9fafb',
                  cursor: !isUploading ? 'pointer' : 'default',
                  pointerEvents: isUploading ? 'none' : 'auto',
                  opacity: isUploading ? 0.75 : 1
                }}
                onDrop={handleDrop}
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onClick={!isUploading ? handleBrowseClick : undefined}
                onMouseEnter={(e) => {
                  if (!isUploading) {
                    e.currentTarget.style.borderColor = '#c084fc';
                    e.currentTarget.style.background = '#faf5ff';
                  }
                }}
                onMouseLeave={(e) => {
                  if (!isUploading && !isDragOver) {
                    e.currentTarget.style.borderColor = '#d1d5db';
                    e.currentTarget.style.background = '#f9fafb';
                  }
                }}
              >
                <input
                  ref={fileInputRef}
                  type="file"
                  accept="application/pdf"
                  onChange={handleFileInputChange}
                  style={{ display: 'none' }}
                  disabled={isUploading}
                />
                
                <div style={{
                  width: '64px',
                  height: '64px',
                  background: '#e9d5ff',
                  borderRadius: '50%',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  margin: '0 auto 16px'
                }}>
                  <svg style={{ width: '32px', height: '32px', color: '#8b5cf6' }} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                  </svg>
                </div>
                <h3 style={{ fontSize: '1.125rem', fontWeight: '600', color: '#1f2937', marginBottom: '8px' }}>
                  Drop your PDF here, or click to browse
                </h3>
                <p style={{ color: '#6b7280', marginBottom: '16px' }}>
                  Select your clinical trial protocol PDF file
                </p>
                <p style={{ fontSize: '0.875rem', color: '#6b7280' }}>
                  Maximum file size: 50MB • PDF files only
                </p>
              </div>
            ) : (
              <div style={{
                border: '1px solid #d1d5db',
                borderRadius: '8px',
                padding: '16px',
                background: '#f9fafb'
              }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                    <div style={{
                      width: '40px',
                      height: '40px',
                      background: '#e9d5ff',
                      borderRadius: '8px',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center'
                    }}>
                      <svg style={{ width: '24px', height: '24px', color: '#8b5cf6' }} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                      </svg>
                    </div>
                    <div>
                      <p style={{ fontWeight: '600', color: '#1f2937' }}>{selectedFile.name}</p>
                      <p style={{ fontSize: '0.875rem', color: '#6b7280' }}>
                        {(selectedFile.size / (1024 * 1024)).toFixed(2)} MB
                      </p>
                    </div>
                  </div>
                  {!isUploading && (
                    <Button
                      onClick={handleRemoveFile}
                      style={{
                        color: '#6b7280',
                        padding: '4px',
                        background: 'transparent',
                        border: 'none',
                        cursor: 'pointer',
                        transition: 'color 0.2s'
                      }}
                      onMouseEnter={(e) => {
                        e.currentTarget.style.color = '#dc2626';
                      }}
                      onMouseLeave={(e) => {
                        e.currentTarget.style.color = '#6b7280';
                      }}
                    >
                      <svg style={{ width: '20px', height: '20px' }} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                      </svg>
                    </Button>
                  )}
                </div>
              </div>
            )}
          </div>

          {/* Upload Progress */}
          {isUploading && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <span style={{ fontSize: '0.875rem', fontWeight: '600', color: '#374151' }}>Uploading...</span>
                <span style={{ fontSize: '0.875rem', color: '#6b7280' }}>{uploadProgress}%</span>
              </div>
              <div style={{ width: '100%', background: '#e5e7eb', borderRadius: '9999px', height: '8px' }}>
                <div 
                  style={{
                    background: '#8b5cf6',
                    height: '8px',
                    borderRadius: '9999px',
                    transition: 'width 0.3s',
                    width: `${uploadProgress}%`
                  }}
                ></div>
              </div>
            </div>
          )}

          {/* Error Message */}
          {error && (
            <div style={{
              padding: '16px',
              background: '#fef2f2',
              border: '1px solid #fecaca',
              borderRadius: '8px'
            }}>
              <div style={{ display: 'flex', alignItems: 'center' }}>
                <svg style={{ width: '20px', height: '20px', color: '#dc2626', marginRight: '8px' }} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <p style={{ color: '#b91c1c', fontSize: '0.875rem' }}>{error}</p>
              </div>
            </div>
          )}

          {/* Upload Button */}
          <div style={{ display: 'flex', gap: '16px' }}>
            <Button
              onClick={handleFileUpload}
              disabled={!selectedFile || !acronym.trim() || isUploading}
              style={{
                flex: 1,
                padding: '12px 24px',
                borderRadius: '8px',
                fontWeight: '600',
                transition: 'all 0.2s',
                border: 'none',
                cursor: (!selectedFile || !acronym.trim() || isUploading) ? 'not-allowed' : 'pointer',
                background: (!selectedFile || !acronym.trim() || isUploading) 
                  ? '#d1d5db' 
                  : 'linear-gradient(to right, #8b5cf6, #7c3aed)',
                color: (!selectedFile || !acronym.trim() || isUploading) ? '#6b7280' : 'white'
              }}
              onMouseEnter={(e) => {
                if (selectedFile && acronym.trim() && !isUploading) {
                  e.currentTarget.style.background = 'linear-gradient(to right, #7c3aed, #6d28d9)';
                }
              }}
              onMouseLeave={(e) => {
                if (selectedFile && acronym.trim() && !isUploading) {
                  e.currentTarget.style.background = 'linear-gradient(to right, #8b5cf6, #7c3aed)';
                }
              }}
            >
              {isUploading ? 'Uploading...' : 'Upload Protocol'}
            </Button>
          </div>

          {/* Upload Requirements */}
          <div style={{
            padding: '16px',
            background: '#faf5ff',
            border: '1px solid #d8b4fe',
            borderRadius: '8px'
          }}>
            <h4 style={{ fontWeight: '600', color: '#7c3aed', marginBottom: '8px' }}>Upload Requirements:</h4>
            <ul style={{ fontSize: '0.875rem', color: '#6d28d9', margin: 0, padding: 0, listStyle: 'none' }}>
              <li style={{ display: 'flex', alignItems: 'center', marginBottom: '4px' }}>
                <span style={{ width: '6px', height: '6px', background: '#8b5cf6', borderRadius: '50%', marginRight: '8px' }}></span>
                PDF format only
              </li>
              <li style={{ display: 'flex', alignItems: 'center', marginBottom: '4px' }}>
                <span style={{ width: '6px', height: '6px', background: '#8b5cf6', borderRadius: '50%', marginRight: '8px' }}></span>
                Maximum file size: 50MB
              </li>
              <li style={{ display: 'flex', alignItems: 'center', marginBottom: '4px' }}>
                <span style={{ width: '6px', height: '6px', background: '#8b5cf6', borderRadius: '50%', marginRight: '8px' }}></span>
                Protocol acronym (2-20 characters)
              </li>
              <li style={{ display: 'flex', alignItems: 'center' }}>
                <span style={{ width: '6px', height: '6px', background: '#8b5cf6', borderRadius: '50%', marginRight: '8px' }}></span>
                Clinical trial protocol document
              </li>
            </ul>
          </div>
        </div>
      </Card>
    </div>
  );
};

export default ProtocolUpload; 