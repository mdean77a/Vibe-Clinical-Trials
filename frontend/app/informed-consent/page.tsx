'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import ICFGenerationDashboard from '@/components/icf/ICFGenerationDashboard';
import { getProtocolId } from '@/utils/mockData';
import type { Protocol } from '@/utils/mockData';

export default function InformedConsentPage() {
  const router = useRouter();
  const [selectedProtocol, setSelectedProtocol] = useState<Protocol | null>(null);

  useEffect(() => {
    // Get protocol from localStorage
    const savedProtocol = localStorage.getItem('selectedProtocol');
    if (savedProtocol) {
      try {
        setSelectedProtocol(JSON.parse(savedProtocol));
      } catch (error) {
        console.error('Error parsing selected protocol:', error);
        // Redirect back to home if no valid protocol
        router.push('/');
      }
    } else {
      // No protocol selected, redirect to home
      router.push('/');
    }
  }, [router]);

  const handleReturnToDocumentSelection = () => {
    if (selectedProtocol) {
      const protocolId = getProtocolId(selectedProtocol);
      const params = new URLSearchParams({
        protocolId: protocolId,
        studyAcronym: selectedProtocol.study_acronym
      });
      router.push(`/document-selection?${params.toString()}`);
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
}