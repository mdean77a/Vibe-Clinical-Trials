# Frontend API Usage - Clinical Trial Accelerator

This document maps every place in the frontend code where backend API endpoints are called, along with the expected JSON response structures.

## 📁 Frontend API Architecture

### Core API Module: `frontend/src/utils/api.ts`
- **Base URL**: `http://localhost:8000/api` (development)
- **Configuration**: Environment-aware with `NEXT_PUBLIC_API_URL`
- **Error Handling**: Standardized error responses with `detail` field
- **Content Type**: `application/json` for most requests

---

## 🔍 API Call Mappings

### 1. Health Check APIs

#### `healthApi.check()` - Main Health Check
**Used in**: `frontend/app/page.tsx:30`
```typescript
const healthResponse = await healthApi.check() as HealthResponse;
```

**Backend Endpoint**: `GET /api/health`
**Expected Response**:
```json
{
  "status": "healthy"
}
```

**Frontend Type**:
```typescript
interface HealthResponse {
  status: string;
}
```

#### `healthApi.root()` - Root Endpoint
**Backend Endpoint**: `GET /`
**Expected Response**:
```json
{
  "message": "Clinical Trial Accelerator API",
  "version": "0.1.0",
  "status": "healthy"
}
```

---

### 2. Protocol Management APIs

#### `protocolsApi.list()` - List All Protocols
**Used in**: `frontend/app/page.tsx:42`
```typescript
const apiResponse = await protocolsApi.list() as Protocol[] | ProtocolsListResponse;
const apiProtocols = Array.isArray(apiResponse) ? apiResponse : (apiResponse as ProtocolsListResponse).protocols || [];
```

**Backend Endpoint**: `GET /api/protocols/`
**Expected Response**:
```json
[
  {
    "protocol_id": "proto_1234567890",
    "study_acronym": "STUDY-123",
    "protocol_title": "Safety and Efficacy Study",
    "collection_name": "collection-uuid",
    "upload_date": "2024-01-01T00:00:00",
    "status": "ready",
    "file_path": "/path/to/file.pdf",
    "created_at": "2024-01-01T00:00:00"
  }
]
```

**Frontend Types**:
```typescript
interface Protocol {
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
  file_path?: string;
  created_at?: string;
}

interface ProtocolsListResponse {
  protocols?: Protocol[];
}
```

#### `protocolsApi.upload()` - Upload Protocol PDF
**Used in**: `frontend/src/components/ProtocolUpload.tsx:94`
```typescript
const uploadResponse = await protocolsApi.upload(selectedFile, {
  study_acronym: acronym.trim().toUpperCase(),
  protocol_title: `Protocol ${acronym.trim().toUpperCase()}`,
});
```

**Backend Endpoint**: `POST /api/protocols/upload`
**Request**: `multipart/form-data`
- `file`: PDF file
- `study_acronym`: string
- `protocol_title`: string

**Expected Response**: Same as `Protocol` interface above

**Usage Context**: 
- Progress tracking with `uploadProgress` state
- Error handling with user-friendly messages
- Automatic navigation to document selection after success

#### `protocolsApi.create()` - Create Protocol Entry
**Backend Endpoint**: `POST /api/protocols/`
**Request Body**:
```json
{
  "study_acronym": "STUDY-123",
  "protocol_title": "Safety and Efficacy Study of Drug X"
}
```
**Expected Response**: Same as `Protocol` interface

#### `protocolsApi.getById()` - Get Protocol by ID
**Backend Endpoint**: `GET /api/protocols/{protocol_id}`
**Expected Response**: Same as `Protocol` interface

#### `protocolsApi.getByCollection()` - Get Protocol by Collection
**Backend Endpoint**: `GET /api/protocols/collection/{collection_name}`
**Expected Response**: Same as `Protocol` interface

#### `protocolsApi.updateStatus()` - Update Protocol Status
**Backend Endpoint**: `PATCH /api/protocols/{id}/status`
**Request Body**:
```json
{
  "status": "processing"
}
```
**Expected Response**: Same as `Protocol` interface

#### `protocolsApi.delete()` - Delete Protocol
**Backend Endpoint**: `DELETE /api/protocols/{id}`
**Expected Response**: `204 No Content`

---

### 3. ICF Generation APIs

#### `icfApi.getSectionRequirements()` - Get ICF Section Requirements
**Used in**: `frontend/src/components/icf/ICFGenerationDashboard.tsx:35`
```typescript
const requirements = await icfApi.getSectionRequirements() as {
  required_sections: Array<{
    name: string;
    title: string;
    description: string;
    estimated_length: string;
  }>;
};
```

**Backend Endpoint**: `GET /api/icf/sections/requirements`
**Expected Response**:
```json
{
  "required_sections": [
    {
      "name": "summary",
      "title": "Study Summary",
      "description": "Overview of the study",
      "estimated_length": "200-300 words"
    },
    {
      "name": "background",
      "title": "Background & Rationale",
      "description": "Medical/scientific background",
      "estimated_length": "300-500 words"
    },
    {
      "name": "participants",
      "title": "Study Participants",
      "description": "Number and eligibility criteria",
      "estimated_length": "200-400 words"
    },
    {
      "name": "procedures",
      "title": "Study Procedures",
      "description": "Study procedures and timeline",
      "estimated_length": "400-600 words"
    },
    {
      "name": "alternatives",
      "title": "Alternative Treatments",
      "description": "Alternative treatment options",
      "estimated_length": "150-250 words"
    },
    {
      "name": "risks",
      "title": "Risks & Side Effects",
      "description": "Potential risks and side effects",
      "estimated_length": "300-500 words"
    },
    {
      "name": "benefits",
      "title": "Potential Benefits",
      "description": "Potential benefits to participants",
      "estimated_length": "150-300 words"
    }
  ]
}
```

#### `icfApi.generateStreaming()` - Generate ICF with Streaming
**Used in**: `frontend/src/components/icf/ICFGenerationDashboard.tsx:93`
```typescript
const streamingGenerator = icfApi.generateStreaming(collectionName, {
  protocol_title: protocol.protocol_title,
  study_acronym: protocol.study_acronym,
  sponsor: protocol.sponsor || 'Unknown',
  indication: protocol.indication || 'General',
});

for await (const event of streamingGenerator) {
  // Handle streaming events
}
```

**Backend Endpoint**: `POST /api/icf/generate-stream`
**Request Body**:
```json
{
  "protocol_collection_name": "collection-uuid",
  "protocol_metadata": {
    "protocol_title": "Study Title",
    "study_acronym": "STUDY-123",
    "sponsor": "Sponsor Name",
    "indication": "Medical Indication"
  }
}
```

**Response**: Server-Sent Events (SSE) stream with events:

**Event: `section_start`**
```json
{
  "event": "section_start",
  "data": {
    "section_name": "summary"
  }
}
```

**Event: `token`** (Real-time content updates)
```json
{
  "event": "token",
  "data": {
    "section_name": "summary",
    "accumulated_content": "This study will evaluate...",
    "token_count": 45
  }
}
```

**Event: `section_complete`**
```json
{
  "event": "section_complete",
  "data": {
    "section_name": "summary",
    "content": "Complete section content...",
    "word_count": 250,
    "status": "completed"
  }
}
```

**Event: `section_error`**
```json
{
  "event": "section_error",
  "data": {
    "section_name": "summary",
    "error": "Failed to generate section"
  }
}
```

**Event: `complete`**
```json
{
  "event": "complete",
  "data": {
    "status": "completed",
    "errors": []
  }
}
```

**Event: `error`**
```json
{
  "event": "error",
  "data": {
    "error": "Global error message"
  }
}
```

#### `icfApi.regenerateSection()` - Regenerate Specific Section
**Used in**: `frontend/src/components/icf/ICFGenerationDashboard.tsx:241`
```typescript
const response = await icfApi.regenerateSection(collectionName, sectionName, {
  protocol_title: protocol.protocol_title,
  study_acronym: protocol.study_acronym,
  sponsor: protocol.sponsor || 'Unknown',
  indication: protocol.indication || 'General',
}) as {
  section_name: string;
  content: string;
  word_count: number;
  status: string;
};
```

**Backend Endpoint**: `POST /api/icf/regenerate-section`
**Request Body**:
```json
{
  "protocol_collection_name": "collection-uuid",
  "section_name": "summary",
  "protocol_metadata": {
    "protocol_title": "Study Title",
    "study_acronym": "STUDY-123",
    "sponsor": "Sponsor Name",
    "indication": "Medical Indication"
  }
}
```

**Expected Response**:
```json
{
  "section_name": "summary",
  "content": "Regenerated section content...",
  "word_count": 275,
  "status": "completed"
}
```

#### `icfApi.generate()` - Generate Complete ICF
**Backend Endpoint**: `POST /api/icf/generate`
**Request Body**:
```json
{
  "protocol_collection_name": "collection-uuid",
  "protocol_metadata": {
    "protocol_title": "Study Title",
    "sponsor": "Sponsor Name",
    "indication": "Medical Indication"
  }
}
```

**Expected Response**:
```json
{
  "collection_name": "collection-uuid",
  "sections": {
    "summary": "Generated summary content...",
    "background": "Generated background content...",
    "participants": "Generated participants content...",
    "procedures": "Generated procedures content...",
    "alternatives": "Generated alternatives content...",
    "risks": "Generated risks content...",
    "benefits": "Generated benefits content..."
  },
  "metadata": {
    "generation_time": "2024-01-01T00:00:00",
    "model_used": "claude-3-sonnet",
    "total_sections": 7
  },
  "errors": [],
  "status": "completed"
}
```

#### `icfApi.getProtocolSummary()` - Get Protocol Summary
**Backend Endpoint**: `GET /api/icf/protocol/{collection_name}/summary`
**Expected Response**:
```json
{
  "collection_name": "collection-uuid",
  "status": "ready",
  "protocol_metadata": {
    "protocol_title": "Study Title",
    "study_acronym": "STUDY-123"
  },
  "message": "Protocol is ready for ICF generation"
}
```

#### `icfApi.getStatus()` - Get Generation Status
**Backend Endpoint**: `GET /api/icf/status/{task_id}`
**Expected Response**:
```json
{
  "task_id": "task-uuid",
  "status": "completed",
  "message": "ICF generation completed successfully"
}
```

#### `icfApi.health()` - ICF Service Health Check
**Backend Endpoint**: `GET /api/icf/health`
**Expected Response**:
```json
{
  "status": "healthy"
}
```

---

## 🎯 Frontend State Management

### ICF Generation Dashboard State
```typescript
interface GenerationProgress {
  isGenerating: boolean;
  currentSection: string | null;
  completedSections: Set<string>;
  errors: string[];
}

interface ICFSectionData {
  name: string;
  title: string;
  content: string;
  status: 'pending' | 'generating' | 'ready_for_review' | 'approved' | 'error';
  wordCount: number;
}
```

### Protocol Upload State
- `selectedFile`: File | null
- `acronym`: string
- `isUploading`: boolean
- `uploadProgress`: number (0-100)
- `error`: string | null

### Main Page State
- `protocols`: Protocol[]
- `loading`: boolean
- `error`: string | null
- `apiHealthy`: boolean | null
- `showUpload`: boolean

---

## 🔄 Error Handling Patterns

### Standard API Error Response
```json
{
  "detail": "Error message here"
}
```

### Frontend Error Handling
```typescript
try {
  const response = await apiCall();
} catch (error) {
  const errorData = await response.json().catch(() => ({}));
  throw new Error(errorData.detail || errorData.error || `HTTP ${response.status}: ${response.statusText}`);
}
```

### User-Facing Error Messages
- **API Unavailable**: "Backend API is not running. Please start the backend server to use this application."
- **Upload Failed**: "Failed to upload and process protocol. Please try again."
- **Generation Failed**: "ICF generation failed: [specific error]"
- **Section Error**: "[section_name]: [error message]"

---

## 🚀 Usage Patterns

### 1. Application Startup
1. Check API health (`healthApi.check()`)
2. Load protocols list (`protocolsApi.list()`)
3. Display appropriate UI based on API availability

### 2. Protocol Upload Flow
1. Validate file (PDF, size limits)
2. Validate acronym (2-20 chars, alphanumeric)
3. Upload with progress tracking (`protocolsApi.upload()`)
4. Navigate to document selection on success

### 3. ICF Generation Flow
1. Load section requirements (`icfApi.getSectionRequirements()`)
2. Initialize section state
3. Start streaming generation (`icfApi.generateStreaming()`)
4. Handle real-time updates (tokens, completion, errors)
5. Allow section-specific regeneration (`icfApi.regenerateSection()`)

### 4. Collection Name Resolution
```typescript
const collectionName = protocol.collection_name || 
  protocol.document_id || 
  `${getProtocolId(protocol).toUpperCase().replace(/-/g, '')}-${Math.random().toString(36).substr(2, 8)}`;
```

---

## 📝 Notes

- **Streaming**: ICF generation uses Server-Sent Events for real-time progress
- **Fallback**: Frontend gracefully handles API unavailability
- **Type Safety**: All responses are typed with TypeScript interfaces
- **Error Recovery**: Section-level error handling allows partial success
- **Progress Tracking**: Upload and generation provide user feedback
- **Session Persistence**: Selected protocols stored in localStorage

---

## 🔗 Related Files

### Frontend API Files
- `frontend/src/utils/api.ts` - Main API utility functions
- `frontend/src/types/protocol.ts` - Type definitions
- `frontend/src/components/icf/ICFGenerationDashboard.tsx` - ICF generation UI
- `frontend/src/components/ProtocolUpload.tsx` - Protocol upload UI
- `frontend/app/page.tsx` - Main application page

### Backend API Files
- `backend/app/api/protocols.py` - Protocol management endpoints
- `backend/app/api/icf_generation.py` - ICF generation endpoints
- `backend/app/main.py` - FastAPI application setup 