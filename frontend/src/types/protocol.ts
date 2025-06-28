export interface Protocol {
  id?: string; // For backward compatibility
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

// API Response Types
export interface HealthResponse {
  status: string;
}

export interface ProtocolsListResponse {
  protocols?: Protocol[];
}

// Utility function to safely get protocol ID (handles both Qdrant and mock formats)
export const getProtocolId = (protocol: Protocol): string => {
  return protocol.protocol_id || protocol.id || '';
};