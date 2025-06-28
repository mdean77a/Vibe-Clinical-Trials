'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import ProtocolSelector from '@/components/ProtocolSelector';
import ProtocolUpload from '@/components/ProtocolUpload';
import type { Protocol } from '@/types/protocol';
import { getProtocolId } from '@/types/protocol';
import { protocolsApi, healthApi, logApiConfig } from '@/utils/api';

export default function HomePage() {
  const [protocols, setProtocols] = useState<Protocol[]>([]);
  const [showUpload, setShowUpload] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [apiHealthy, setApiHealthy] = useState<boolean | null>(null);
  const router = useRouter();

  // Load protocols from API or fallback to localStorage
  useEffect(() => {
    const loadProtocols = async () => {
      try {
        setLoading(true);
        setError(null);
        
        // Log API configuration for debugging
        logApiConfig();
        
        // Check API health first
        try {
          const healthResponse = await healthApi.check() as any;
          console.log('Health check response:', healthResponse);
          
          // Check if backend is actually available
          if (healthResponse.backend_available === false) {
            throw new Error(`Backend unavailable: ${healthResponse.backend_error}`);
          }
          
          setApiHealthy(true);
          console.log('✅ API is healthy - using backend');
          
          // Load protocols from API
          const apiResponse = await protocolsApi.list() as any;
          const apiProtocols = apiResponse.protocols || apiResponse || [];
          setProtocols(Array.isArray(apiProtocols) ? apiProtocols : []);
        } catch (apiError) {
          console.warn('⚠️ API unavailable:', apiError);
          setApiHealthy(false);
          setError('Backend API is not running. Please start the backend server to use this application.');
          setProtocols([]);
        }
      } catch (error) {
        console.error('Error loading protocols:', error);
        setError('Failed to load protocols');
      } finally {
        setLoading(false);
      }
    };

    loadProtocols();
  }, []);




  const handleProtocolSelect = (protocol: Protocol) => {
    try {
      console.log('🔄 Protocol selected:', protocol);
      
      // Store selected protocol for session persistence
      localStorage.setItem('selectedProtocol', JSON.stringify(protocol));
      
      // Navigate to document type selection page with query params
      const protocolId = getProtocolId(protocol);
      console.log('📋 Using protocol ID:', protocolId);
      
      const params = new URLSearchParams({
        protocolId: protocolId,
        studyAcronym: protocol.study_acronym
      });
      
      console.log('🚀 Navigating to:', `/document-selection?${params.toString()}`);
      router.push(`/document-selection?${params.toString()}`);
    } catch (error) {
      console.error('❌ Error in handleProtocolSelect:', error);
    }
  };

  const handleUploadNew = () => {
    setShowUpload(true);
  };

  const handleUploadComplete = async (fileName: string, acronym: string, uploadedProtocol?: any) => {
    try {
      if (apiHealthy && uploadedProtocol) {
        // Use the protocol that was already created by the upload endpoint
        console.log('✅ Using protocol created by upload:', uploadedProtocol);
        
        const newProtocol = uploadedProtocol as Protocol;
        
        // Update local state
        const updatedProtocols = [newProtocol, ...(Array.isArray(protocols) ? protocols : [])];
        setProtocols(updatedProtocols);
        
        // Store the new protocol as selected
        localStorage.setItem('selectedProtocol', JSON.stringify(newProtocol));
        
        // Navigate to document type selection page
        const params = new URLSearchParams({
          protocolId: (newProtocol as any).protocol_id || newProtocol.id,
          studyAcronym: newProtocol.study_acronym
        });
        router.push(`/document-selection?${params.toString()}`);
      } else {
        // API is not available
        console.error('❌ Cannot upload protocol - API is not available');
        alert('Cannot upload protocol. Backend API is not running.');
      }
    } catch (error) {
      console.error('❌ Error handling upload completion:', error);
      alert('Failed to complete protocol setup. Please try again.');
    }
  };

  const handleUploadCancel = () => {
    setShowUpload(false);
  };


  return (
    <div style={{ 
      padding: '24px', 
      maxWidth: '1024px', 
      margin: '0 auto',
      minHeight: '100vh'
    }}>
      <main role="main">
        <div style={{ textAlign: 'center', marginBottom: '48px' }}>
          <h1 style={{
            fontSize: '2.5rem',
            fontWeight: 'bold',
            background: 'linear-gradient(to right, #2563eb, #9333ea)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            backgroundClip: 'text',
            marginBottom: '16px'
          }}>
            Clinical Trial Accelerator
          </h1>
          <p style={{ color: '#6b7280', fontSize: '1.125rem' }}>
            Streamline your clinical trial documentation with AI-powered document generation. Generate informed consent forms and site initiation checklists.
          </p>
          
          {/* API Status Indicator */}
          {!loading && apiHealthy === true && (
            <div style={{ 
              marginTop: '12px', 
              padding: '8px 16px', 
              borderRadius: '20px', 
              display: 'inline-block',
              fontSize: '0.875rem',
              backgroundColor: '#dcfce7',
              color: '#166534',
              border: '1px solid #bbf7d0'
            }}>
              🟢 Connected to API
            </div>
          )}
        </div>

      {loading ? (
        <div style={{ textAlign: 'center', padding: '48px' }}>
          <div style={{ fontSize: '1.125rem', color: '#6b7280' }}>
            Loading protocols... {/* Debug: loading=true */}
          </div>
        </div>
      ) : error ? (
        <div style={{ 
          textAlign: 'center', 
          padding: '48px',
          backgroundColor: '#fef2f2',
          border: '1px solid #fecaca',
          borderRadius: '8px',
          color: '#dc2626'
        }}>
          <div style={{ fontSize: '1.125rem', marginBottom: '8px' }}>
            ⚠️ Error Loading Protocols
          </div>
          <div style={{ fontSize: '0.875rem' }}>
            {error}
          </div>
        </div>
      ) : showUpload ? (
        <ProtocolUpload 
          onUploadComplete={handleUploadComplete}
          onCancel={handleUploadCancel}
        />
      ) : (
        <>
          {console.log('🎯 Rendering ProtocolSelector with protocols:', protocols)}
          <ProtocolSelector 
            protocols={protocols}
            onProtocolSelect={handleProtocolSelect}
            onUploadNew={handleUploadNew}
          />
        </>
      )}
      </main>
    </div>
  );
}