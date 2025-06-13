import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import ProtocolSelector from '../components/ProtocolSelector';
import ProtocolUpload from '../components/ProtocolUpload';
import { initializeMockData } from '../utils/mockData';
import type { Protocol } from '../utils/mockData';

const HomePage: React.FC = () => {
  const [protocols, setProtocols] = useState<Protocol[]>([]);
  const [showUpload, setShowUpload] = useState(false);
  const navigate = useNavigate();

  // Load protocols from localStorage (simulating database)
  useEffect(() => {
    // Initialize mock data if no protocols exist
    initializeMockData();
    
    const savedProtocols = localStorage.getItem('protocols');
    if (savedProtocols) {
      try {
        setProtocols(JSON.parse(savedProtocols));
      } catch (error) {
        console.error('Error parsing saved protocols:', error);
        setProtocols([]);
      }
    }
  }, []);

  // Save protocols to localStorage (simulating database)
  const saveProtocols = (updatedProtocols: Protocol[]) => {
    localStorage.setItem('protocols', JSON.stringify(updatedProtocols));
    setProtocols(updatedProtocols);
  };

  const handleProtocolSelect = (protocol: Protocol) => {
    // Store selected protocol for session persistence
    localStorage.setItem('selectedProtocol', JSON.stringify(protocol));
    
    // Navigate to document type selection page
    navigate('/document-selection', { 
      state: { 
        protocol: protocol,
        protocolId: protocol.id,
        studyAcronym: protocol.study_acronym 
      } 
    });
  };

  const handleUploadNew = () => {
    setShowUpload(true);
  };

  const handleUploadComplete = (fileName: string, acronym: string) => {
    // Create a new protocol entry (simulating backend processing)
    const newProtocol: Protocol = {
      id: `protocol_${Date.now()}`,
      study_acronym: acronym,
      protocol_title: extractProtocolTitle(fileName),
      upload_date: new Date().toISOString(),
      status: 'processed'
    };

    const updatedProtocols = [newProtocol, ...protocols];
    saveProtocols(updatedProtocols);
    
    // Store the new protocol as selected
    localStorage.setItem('selectedProtocol', JSON.stringify(newProtocol));
    
    // Navigate to document type selection page
    navigate('/document-selection', { 
      state: { 
        protocol: newProtocol,
        protocolId: newProtocol.id,
        studyAcronym: newProtocol.study_acronym 
      } 
    });
  };

  const handleUploadCancel = () => {
    setShowUpload(false);
  };

  // Helper functions to simulate metadata extraction
  const extractProtocolTitle = (fileName: string): string => {
    // Simple extraction logic - in real app this would be done by backend
    const nameWithoutExt = fileName.replace('.pdf', '');
    return nameWithoutExt.replace(/[-_]/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
  };

  return (
    <div style={{ 
      padding: '24px', 
      maxWidth: '1024px', 
      margin: '0 auto',
      minHeight: '100vh'
    }}>
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
          Streamline your clinical trial document generation
        </p>
      </div>

      {showUpload ? (
        <ProtocolUpload 
          onUploadComplete={handleUploadComplete}
          onCancel={handleUploadCancel}
        />
      ) : (
        <ProtocolSelector 
          protocols={protocols}
          onProtocolSelect={handleProtocolSelect}
          onUploadNew={handleUploadNew}
        />
      )}
    </div>
  );
};

export default HomePage; 