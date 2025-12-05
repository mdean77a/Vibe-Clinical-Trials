import React from 'react';
import { useRouter } from 'next/navigation';
import { getProtocolId } from '@/types/protocol';
import type { Protocol } from '@/types/protocol';

interface ProtocolPageLayoutProps {
  protocol: Protocol | null;
  isLoading: boolean;
  children: (props: {
    protocol: Protocol;
    handleReturnToDocumentSelection: () => void;
  }) => React.ReactNode;
}

/**
 * Shared layout component for protocol-based pages
 * Handles loading state and provides navigation helper
 */
export default function ProtocolPageLayout({
  protocol,
  isLoading,
  children
}: ProtocolPageLayoutProps) {
  const router = useRouter();

  const handleReturnToDocumentSelection = () => {
    console.log('[ProtocolPageLayout] Back to Document Selection clicked');
    console.log('[ProtocolPageLayout] Protocol:', protocol);

    try {
      if (protocol) {
        const protocolId = getProtocolId(protocol);
        console.log('[ProtocolPageLayout] Protocol ID:', protocolId);

        const params = new URLSearchParams({
          protocolId: protocolId,
          studyAcronym: protocol.study_acronym
        });

        const targetUrl = `/document-selection?${params.toString()}`;
        console.log('[ProtocolPageLayout] Navigating to:', targetUrl);

        router.push(targetUrl);
      } else {
        console.log('[ProtocolPageLayout] No protocol, navigating to /document-selection');
        router.push('/document-selection');
      }
    } catch (error) {
      console.error('[ProtocolPageLayout] Navigation error:', error);
      // Fallback: navigate without params
      router.push('/document-selection');
    }
  };

  if (isLoading || !protocol) {
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

  return <>{children({ protocol, handleReturnToDocumentSelection })}</>;
}
