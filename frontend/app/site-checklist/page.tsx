'use client';

import React from 'react';
import SiteChecklistDashboard from '@/components/site-checklist/SiteChecklistDashboard';
import ProtocolPageLayout from '@/components/ProtocolPageLayout';
import { useProtocolLoader } from '@/hooks/useProtocolLoader';

export default function SiteChecklistPage() {
  const { protocol, isLoading } = useProtocolLoader();

  return (
    <ProtocolPageLayout protocol={protocol} isLoading={isLoading}>
      {({ protocol: selectedProtocol, handleReturnToDocumentSelection }) => (
        <SiteChecklistDashboard
          protocol={selectedProtocol}
          onReturnToSelection={handleReturnToDocumentSelection}
        />
      )}
    </ProtocolPageLayout>
  );
}