import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import Card from '../components/Card';
import Button from '../components/Button';

const SiteChecklistPage: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const uploadedFileName = location.state?.uploadedFileName || localStorage.getItem('uploadedFileName');

  const handleMakeChecklist = () => {
    alert('This is not yet implemented.');
  };

  const handleReturnToMain = () => {
    navigate('/', { 
      state: { uploadedFileName } 
    });
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
          Site Initiation Checklist
        </h1>
        <p style={{ color: '#6b7280', fontSize: '1.125rem' }}>
          Generate comprehensive site initiation checklists
        </p>
      </div>
      
      {uploadedFileName && (
        <Card style={{ marginBottom: '24px' }}>
          <div style={{
            padding: '16px',
            background: 'linear-gradient(to right, #faf5ff, #f3e8ff)',
            border: '1px solid #d8b4fe',
            borderRadius: '12px',
            boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1)'
          }}>
            <div style={{ display: 'flex', alignItems: 'center' }}>
              <div style={{
                width: '40px',
                height: '40px',
                background: '#e9d5ff',
                borderRadius: '50%',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                marginRight: '12px'
              }}>
                <span style={{ color: '#8b5cf6', fontSize: '1.25rem' }}>📄</span>
              </div>
              <div>
                <p style={{ color: '#7c3aed', fontWeight: '600' }}>
                  Working with Protocol
                </p>
                <p style={{ color: '#6d28d9', fontSize: '0.875rem' }}>
                  {uploadedFileName}
                </p>
              </div>
            </div>
          </div>
        </Card>
      )}
      
      <Card>
        <div style={{
          padding: '32px',
          background: 'white',
          border: '1px solid #d8b4fe',
          borderRadius: '12px',
          boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1)'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', marginBottom: '24px' }}>
            <div style={{
              width: '48px',
              height: '48px',
              background: '#e9d5ff',
              borderRadius: '50%',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              marginRight: '16px'
            }}>
              <span style={{ color: '#8b5cf6', fontSize: '1.5rem' }}>✅</span>
            </div>
            <div>
              <h2 style={{ fontSize: '1.5rem', fontWeight: '600', color: '#1f2937' }}>
                Site Initiation Checklist
              </h2>
              <p style={{ color: '#6b7280' }}>
                Generate a site initiation checklist based on your uploaded protocol document.
              </p>
            </div>
          </div>
          
          <div style={{
            background: '#faf5ff',
            border: '1px solid #d8b4fe',
            borderRadius: '8px',
            padding: '24px',
            marginBottom: '24px'
          }}>
            <h3 style={{ fontWeight: '600', color: '#7c3aed', marginBottom: '8px' }}>
              What will be generated:
            </h3>
            <ul style={{ color: '#6d28d9', fontSize: '0.875rem', margin: 0, paddingLeft: '20px' }}>
              <li style={{ marginBottom: '4px' }}>Regulatory requirements and documentation</li>
              <li style={{ marginBottom: '4px' }}>Staff training and certification needs</li>
              <li style={{ marginBottom: '4px' }}>Equipment and supplies checklist</li>
              <li style={{ marginBottom: '4px' }}>Site preparation and setup tasks</li>
            </ul>
          </div>
          
          <div style={{ 
            display: 'flex', 
            flexDirection: 'column',
            gap: '16px'
          }}>
            <Button 
              onClick={handleMakeChecklist}
              style={{
                background: 'linear-gradient(to right, #8b5cf6, #7c3aed)',
                color: 'white',
                fontWeight: '600',
                padding: '16px 32px',
                borderRadius: '8px',
                boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
                border: 'none',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                transition: 'all 0.2s',
                transform: 'scale(1)',
                width: '100%'
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
              <span style={{ marginRight: '8px' }}>🚀</span>
              Make Checklist
            </Button>
            <Button 
              onClick={handleReturnToMain} 
              style={{
                background: 'linear-gradient(to right, #6b7280, #4b5563)',
                color: 'white',
                fontWeight: '600',
                padding: '16px 32px',
                borderRadius: '8px',
                boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
                border: 'none',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                transition: 'all 0.2s',
                transform: 'scale(1)',
                width: '100%'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.background = 'linear-gradient(to right, #4b5563, #374151)';
                e.currentTarget.style.transform = 'scale(1.05)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.background = 'linear-gradient(to right, #6b7280, #4b5563)';
                e.currentTarget.style.transform = 'scale(1)';
              }}
            >
              <span style={{ marginRight: '8px' }}>←</span>
              Return to Main Page
            </Button>
          </div>
        </div>
      </Card>
    </div>
  );
};

export default SiteChecklistPage; 