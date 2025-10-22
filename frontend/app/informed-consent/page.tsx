'use client';

import React from 'react';
import ICFGenerationDashboard from '@/components/icf/ICFGenerationDashboard';
import ProtocolPageLayout from '@/components/ProtocolPageLayout';
import { useProtocolLoader } from '@/hooks/useProtocolLoader';

export default function InformedConsentPage() {
  const { protocol, isLoading } = useProtocolLoader();

  return (
    <ProtocolPageLayout protocol={protocol} isLoading={isLoading}>
      {({ protocol: selectedProtocol, handleReturnToDocumentSelection }) => (
        <ICFGenerationDashboard
          protocol={selectedProtocol}
          onReturnToSelection={handleReturnToDocumentSelection}
        />
      )}
    </ProtocolPageLayout>
  );
}
