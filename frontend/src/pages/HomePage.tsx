import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import Card from '../components/Card';
import Button from '../components/Button';

const HomePage: React.FC = () => {
  const [uploadedFileName, setUploadedFileName] = useState<string | null>(null);
  const navigate = useNavigate();
  const location = useLocation();

  // Load uploaded file from localStorage on component mount
  useEffect(() => {
    const savedFileName = localStorage.getItem('uploadedFileName');
    if (savedFileName) {
      setUploadedFileName(savedFileName);
    }
  }, []);

  // Also check if we're returning from another page with state
  useEffect(() => {
    if (location.state?.uploadedFileName) {
      setUploadedFileName(location.state.uploadedFileName);
      localStorage.setItem('uploadedFileName', location.state.uploadedFileName);
    }
  }, [location.state]);

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setUploadedFileName(file.name);
      // Save to localStorage for persistence
      localStorage.setItem('uploadedFileName', file.name);

      // Placeholder for sending the file to the backend
      const formData = new FormData();
      formData.append('file', file);

      try {
        const response = await fetch('/upload', {
          method: 'POST',
          body: formData,
        });

        if (response.ok) {
          console.log('File uploaded successfully');
        } else {
          console.error('File upload failed');
        }
      } catch (error) {
        console.error('Error uploading file:', error);
      }
    }
  };

  const handleInformedConsentClick = () => {
    navigate('/informed-consent', { 
      state: { uploadedFileName } 
    });
  };

  const handleSiteChecklistClick = () => {
    navigate('/site-checklist', { 
      state: { uploadedFileName } 
    });
  };

  const handleRestart = () => {
    // Clear the uploaded file state
    setUploadedFileName(null);
    // Clear from localStorage
    localStorage.removeItem('uploadedFileName');
    // Clear the file input
    const fileInput = document.querySelector('input[type="file"]') as HTMLInputElement;
    if (fileInput) {
      fileInput.value = '';
    }
  };

  return (
    <div style={{ 
      padding: '24px', 
      maxWidth: '1024px', 
      margin: '0 auto',
      minHeight: '100vh'
    }}>
      <div style={{ textAlign: 'center', marginBottom: '32px' }}>
        <h1 style={{
          fontSize: '2.5rem',
          fontWeight: 'bold',
          background: 'linear-gradient(to right, #2563eb, #9333ea)',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent',
          backgroundClip: 'text',
          marginBottom: '8px'
        }}>
          Clinical Trial Accelerator
        </h1>
        <p style={{ color: '#6b7280', fontSize: '1.125rem' }}>
          Streamline your clinical trial document generation
        </p>
      </div>
      
      {!uploadedFileName && (
        <Card>
          <div style={{
            padding: '24px',
            background: 'white',
            border: '1px solid #dbeafe',
            borderRadius: '12px',
            boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1)'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', marginBottom: '16px' }}>
              <div style={{
                width: '40px',
                height: '40px',
                background: '#dbeafe',
                borderRadius: '50%',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                marginRight: '12px'
              }}>
                <span style={{ fontSize: '1.25rem' }}>📄</span>
              </div>
              <h2 style={{ fontSize: '1.25rem', fontWeight: '600', color: '#1f2937' }}>
                Upload Protocol PDF
              </h2>
            </div>
            <div style={{
              border: '2px dashed #93c5fd',
              borderRadius: '8px',
              padding: '24px',
              background: '#eff6ff',
              transition: 'background-color 0.2s'
            }}>
              <input 
                type="file" 
                accept="application/pdf" 
                onChange={handleFileUpload}
                style={{ width: '100%', color: '#374151' }}
              />
              <p style={{ fontSize: '0.875rem', color: '#6b7280', marginTop: '8px' }}>
                Select your clinical trial protocol PDF file
              </p>
            </div>
          </div>
        </Card>
      )}
      
      {uploadedFileName && (
        <>
          <Card style={{ marginBottom: '24px' }}>
            <div style={{
              padding: '24px',
              background: 'linear-gradient(to right, #ecfdf5, #d1fae5)',
              border: '1px solid #bbf7d0',
              borderRadius: '12px',
              boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1)'
            }}>
              <div style={{ display: 'flex', alignItems: 'center' }}>
                <div style={{
                  width: '40px',
                  height: '40px',
                  background: '#dcfce7',
                  borderRadius: '50%',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  marginRight: '12px'
                }}>
                  <span style={{ color: '#16a34a', fontSize: '1.25rem' }}>✓</span>
                </div>
                <div>
                  <p style={{ color: '#166534', fontWeight: '600' }}>
                    Protocol Uploaded Successfully
                  </p>
                  <p style={{ color: '#15803d', fontSize: '0.875rem' }}>
                    {uploadedFileName}
                  </p>
                </div>
              </div>
            </div>
          </Card>
          
          <Card style={{ marginBottom: '24px' }}>
            <div style={{
              padding: '24px',
              background: 'white',
              border: '1px solid #c7d2fe',
              borderRadius: '12px',
              boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1)'
            }}>
              <div style={{ display: 'flex', alignItems: 'center', marginBottom: '24px' }}>
                <div style={{
                  width: '40px',
                  height: '40px',
                  background: '#e0e7ff',
                  borderRadius: '50%',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  marginRight: '12px'
                }}>
                  <span style={{ color: '#4f46e5', fontSize: '1.25rem' }}>🚀</span>
                </div>
                <h2 style={{ fontSize: '1.25rem', fontWeight: '600', color: '#1f2937' }}>
                  Select Document Type to Generate
                </h2>
              </div>
              <div style={{ 
                display: 'grid', 
                gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', 
                gap: '16px' 
              }}>
                <Button 
                  onClick={handleInformedConsentClick}
                  style={{
                    background: 'linear-gradient(to right, #3b82f6, #2563eb)',
                    color: 'white',
                    fontWeight: '600',
                    padding: '16px 24px',
                    borderRadius: '8px',
                    boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
                    border: 'none',
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    transition: 'all 0.2s',
                    transform: 'scale(1)'
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.background = 'linear-gradient(to right, #2563eb, #1d4ed8)';
                    e.currentTarget.style.transform = 'scale(1.05)';
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.background = 'linear-gradient(to right, #3b82f6, #2563eb)';
                    e.currentTarget.style.transform = 'scale(1)';
                  }}
                >
                  <span style={{ marginRight: '8px' }}>📋</span>
                  Informed Consent
                </Button>
                <Button 
                  onClick={handleSiteChecklistClick}
                  style={{
                    background: 'linear-gradient(to right, #8b5cf6, #7c3aed)',
                    color: 'white',
                    fontWeight: '600',
                    padding: '16px 24px',
                    borderRadius: '8px',
                    boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
                    border: 'none',
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    transition: 'all 0.2s',
                    transform: 'scale(1)'
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.background = 'linear-gradient(to right, #7c3aed, #6d28d9)';
                    e.currentTarget.style.transform = 'scale(1.05)';
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.background = 'linear-gradient(to right, #8b5cf6, #7c3aed)';
                    e.currentTarget.style.transform = 'scale(1)';
                  }}
                >
                  <span style={{ marginRight: '8px' }}>✅</span>
                  Site Checklist
                </Button>
              </div>
            </div>
          </Card>

          <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '32px' }}>
            <Button 
              onClick={handleRestart}
              style={{
                background: 'linear-gradient(to right, #ef4444, #dc2626)',
                color: 'white',
                fontWeight: '500',
                padding: '8px 16px',
                borderRadius: '8px',
                boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
                border: 'none',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                transition: 'all 0.2s',
                transform: 'scale(1)'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.background = 'linear-gradient(to right, #dc2626, #b91c1c)';
                e.currentTarget.style.transform = 'scale(1.05)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.background = 'linear-gradient(to right, #ef4444, #dc2626)';
                e.currentTarget.style.transform = 'scale(1)';
              }}
            >
              <span style={{ marginRight: '8px' }}>🔄</span>
              Start Over
            </Button>
          </div>
        </>
      )}
    </div>
  );
};

export default HomePage; 