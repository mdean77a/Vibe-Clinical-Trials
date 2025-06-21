import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import ICFGenerationDashboard from '../components/icf/ICFGenerationDashboard';
import type { Protocol } from '../utils/mockData';

const InformedConsentPage: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const [selectedProtocol, setSelectedProtocol] = useState<Protocol | null>(null);

  useEffect(() => {
    // First try to get protocol from navigation state
    if (location.state?.protocol) {
      setSelectedProtocol(location.state.protocol);
    } else {
      // Fallback to localStorage
      const savedProtocol = localStorage.getItem('selectedProtocol');
      if (savedProtocol) {
        try {
          setSelectedProtocol(JSON.parse(savedProtocol));
        } catch (error) {
          console.error('Error parsing selected protocol:', error);
          // Redirect back to home if no valid protocol
          navigate('/');
        }
      } else {
        // No protocol selected, redirect to home
        navigate('/');
      }
    }
  }, [location.state, navigate]);

  const handleReturnToDocumentSelection = () => {
    navigate('/document-selection', {
      state: selectedProtocol ? { protocol: selectedProtocol } : undefined
    });
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
    <ICFGenerationDashboard
      protocol={selectedProtocol}
      onReturnToSelection={handleReturnToDocumentSelection}
    />
  );
};

export default InformedConsentPage; 