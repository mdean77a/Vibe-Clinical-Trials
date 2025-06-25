import React, { useState, useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import ICFGenerationDashboard from '../components/icf/ICFGenerationDashboard';
import type { Protocol } from '../utils/mockData';

const InformedConsentPage: React.FC = () => {
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
    <ICFGenerationDashboard
      protocol={selectedProtocol}
      onReturnToSelection={handleReturnToDocumentSelection}
    />
  );
};

export default InformedConsentPage; 