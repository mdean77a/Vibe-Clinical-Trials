import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import type { Protocol } from '@/types/protocol';

/**
 * Custom hook to load and manage protocol from localStorage
 * Handles error cases and redirects if protocol is missing/invalid
 */
export function useProtocolLoader() {
  const router = useRouter();
  const [selectedProtocol, setSelectedProtocol] = useState<Protocol | null>(null);
  const [isLoading, setIsLoading] = useState(true);

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
    setIsLoading(false);
  }, [router]);

  return { protocol: selectedProtocol, isLoading };
}
