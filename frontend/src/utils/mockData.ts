export interface Protocol {
  id?: string; // For mock data compatibility
  protocol_id?: string; // From Qdrant API
  document_id?: string;
  collection_name?: string;
  study_acronym: string;
  protocol_title: string;
  upload_date: string;
  status: string;
  sponsor?: string;
  indication?: string;
  file_path?: string; // From Qdrant API
  created_at?: string; // From Qdrant API
}

export const mockProtocols: Protocol[] = [
  {
    id: 'protocol_1',
    study_acronym: 'STUDY-001',
    protocol_title: 'A Phase III Randomized Study of Novel Cardiac Drug in Heart Failure Patients',
    upload_date: '2024-12-15T10:30:00Z',
    status: 'processed'
  },
  {
    id: 'protocol_2', 
    study_acronym: 'STUDY-002',
    protocol_title: 'Phase II Clinical Trial of Immunotherapy in Advanced Lung Cancer',
    upload_date: '2024-12-10T14:20:00Z',
    status: 'processed'
  },
  {
    id: 'protocol_3',
    study_acronym: 'STUDY-003',
    protocol_title: 'Randomized Controlled Trial of Neuroprotective Agent in Stroke Recovery',
    upload_date: '2024-12-05T09:15:00Z',
    status: 'processed'
  }
];

export const initializeMockData = () => {
  const existingProtocols = localStorage.getItem('protocols');
  if (!existingProtocols) {
    localStorage.setItem('protocols', JSON.stringify(mockProtocols));
  }
};

// Utility function to safely get protocol ID (handles both Qdrant and mock formats)
export const getProtocolId = (protocol: Protocol): string => {
  return protocol.protocol_id || protocol.id || '';
}; 