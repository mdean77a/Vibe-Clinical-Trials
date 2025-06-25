import React, { useState, useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import Card from '../components/Card';
import Button from '../components/Button';
import type { Protocol } from '../utils/mockData';

const SiteChecklistPage: React.FC = () => {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [selectedProtocol, setSelectedProtocol] = useState<Protocol | null>(null);

  useEffect(() => {
    // Get protocol from localStorage using the protocolId from searchParams
    const protocolId = searchParams.get('protocolId');
    const studyAcronym = searchParams.get('studyAcronym');
    
    if (protocolId && studyAcronym) {
      // Try to get the full protocol from localStorage
      const savedProtocol = localStorage.getItem('selectedProtocol');
      if (savedProtocol) {
        try {
          const protocol = JSON.parse(savedProtocol);
          // Verify it matches the expected protocol
          if (protocol.id === protocolId || protocol.study_acronym === studyAcronym) {
            setSelectedProtocol(protocol);
          } else {
            // Protocol mismatch, redirect to home
            router.push('/');
          }
        } catch (error) {
          console.error('Error parsing selected protocol:', error);
          // Redirect back to home if no valid protocol
          router.push('/');
        }
      } else {
        // No protocol in localStorage, redirect to home
        router.push('/');
      }
    } else {
      // No protocol ID in URL, redirect to home
      router.push('/');
    }
  }, [searchParams, router]);

  const handleMakeChecklist = () => {
    alert('This is not yet implemented.');
  };

  const handleReturnToDocumentSelection = () => {
    if (selectedProtocol) {
      router.push(`/document-selection?protocolId=${selectedProtocol.id}&studyAcronym=${encodeURIComponent(selectedProtocol.study_acronym)}`);
    } else {
      router.push('/document-selection');
    }
  };

  if (!selectedProtocol) {
    return (
      <div style={{ 
        minHeight: '100vh', 
        display: 'flex', 
        alignItems: 'center', 
        justifyContent: 'center',
        padding: '24px',
        maxWidth: '1024px',
        margin: '0 auto'
      }}>
        <div style={{ textAlign: 'center' }}>
          <div style={{
            width: '48px',
            height: '48px',
            border: '2px solid #d8b4fe',
            borderTop: '2px solid #8b5cf6',
            borderRadius: '50%',
            animation: 'spin 1s linear infinite',
            margin: '0 auto 16px'
          }}></div>
          <p style={{ color: '#6b7280' }}>Loading protocol...</p>
        </div>
      </div>
    );
  }

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
              <span style={{ color: '#8b5cf6', fontWeight: '600' }}>
                {selectedProtocol.study_acronym.substring(0, 2).toUpperCase()}
              </span>
            </div>
            <div>
              <p style={{ color: '#7c3aed', fontWeight: '600', fontSize: '1.125rem' }}>
                {selectedProtocol.study_acronym}
              </p>
              <p style={{ color: '#6d28d9', fontSize: '0.875rem' }}>
                {selectedProtocol.protocol_title}
              </p>
              <p style={{ color: '#8b5cf6', fontSize: '0.75rem' }}>
                Status: {selectedProtocol.status}
              </p>
            </div>
          </div>
        </div>
      </Card>
      
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
              Some of the sections that will be included in the site initiation checklist:
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
              onClick={handleReturnToDocumentSelection} 
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
              Return to Document Selection
            </Button>
          </div>
        </div>
      </Card>
    </div>
  );
};

export default SiteChecklistPage; 