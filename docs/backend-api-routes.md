# Clinical Trial Accelerator - Backend API Routes

This document provides a comprehensive overview of all available API endpoints in the Clinical Trial Accelerator backend.

## Base URL
- **Development**: `http://localhost:8000`
- **Production**: TBD

## Authentication
Currently, no authentication is required for API endpoints.

---

## 🏠 Root Application Routes

### Health Check Endpoints

#### `GET /`
**Description**: Root endpoint for basic health check  
**Response**: 
```json
{
  "message": "Clinical Trial Accelerator API",
  "version": "0.1.0",
  "status": "healthy"
}
```

#### `GET /api/health`
**Description**: Dedicated health check endpoint  
**Response**: 
```json
{
  "status": "healthy"
}
```

---

## 📄 Protocol Management Routes (`/api/protocols`)

### Create Protocol

#### `POST /api/protocols/`
**Description**: Create a new protocol entry  
**Request Body**:
```json
{
  "study_acronym": "STUDY-123",
  "protocol_title": "Safety and Efficacy Study of Drug X"
}
```
**Response**: `ProtocolResponse` (201 Created)

#### `POST /api/protocols/upload`
**Description**: Upload and process a protocol PDF with full text extraction  
**Content-Type**: `multipart/form-data`  
**Form Data**:
- `file`: PDF file (required)
- `study_acronym`: Study acronym (required)
- `protocol_title`: Protocol title (required)

**Response**: `ProtocolResponse` (201 Created)

### Retrieve Protocols

#### `GET /api/protocols/`
**Description**: List all protocols with optional status filtering  
**Query Parameters**:
- `status_filter` (optional): Filter protocols by status

**Response**: `List[ProtocolResponse]`

#### `GET /api/protocols/{protocol_id}`
**Description**: Get a specific protocol by ID  
**Path Parameters**:
- `protocol_id`: Protocol identifier

**Response**: `ProtocolResponse`

#### `GET /api/protocols/collection/{collection_name}`
**Description**: Get a protocol by Qdrant collection name  
**Path Parameters**:
- `collection_name`: Qdrant collection identifier

**Response**: `ProtocolResponse`

### Update Protocol

#### `PATCH /api/protocols/collection/{collection_name}/status`
**Description**: Update protocol status  
**Path Parameters**:
- `collection_name`: Qdrant collection identifier

**Request Body**: `ProtocolUpdate`
**Response**: `ProtocolResponse`

---

## 🧾 ICF Generation Routes (`/api/icf`)

### Generate ICF

#### `POST /api/icf/generate`
**Description**: Generate a complete Informed Consent Form for a protocol  
**Request Body**:
```json
{
  "protocol_collection_name": "ABCD1234-efgh-5678-ijkl-9012mnopqrst-a1b2c3d4",
  "protocol_metadata": {
    "protocol_title": "Safety and Efficacy Study",
    "sponsor": "Example Pharma",
    "indication": "Oncology"
  }
}
```

**Response**: `ICFGenerationResponse`

**Generated Sections**:
- Summary: Overview of the study
- Background: Medical/scientific background
- Participants: Number and eligibility criteria
- Procedures: Study procedures and timeline
- Alternatives: Alternative treatment options
- Risks: Potential risks and side effects
- Benefits: Potential benefits to participants

#### `POST /api/icf/generate-stream`
**Description**: Generate ICF with streaming section results using Server-Sent Events (SSE)  
**Request Body**: Same as `/generate`  
**Response**: `StreamingResponse` (text/event-stream)

**Event Types**:
- `section_complete`: When a section finishes generating
- `error`: When a section fails to generate
- `complete`: When all sections are finished

#### `POST /api/icf/regenerate-section`
**Description**: Regenerate a specific ICF section  
**Request Body**:
```json
{
  "protocol_collection_name": "collection-name",
  "section_name": "summary",
  "protocol_metadata": {}
}
```

**Response**: Section regeneration result

### ICF Information & Status

#### `GET /api/icf/protocol/{collection_name}/summary`
**Description**: Get protocol summary information  
**Path Parameters**:
- `collection_name`: Protocol collection identifier

**Response**: `ProtocolSummaryResponse`

#### `GET /api/icf/status/{task_id}`
**Description**: Check the status of an ICF generation task  
**Path Parameters**:
- `task_id`: Generation task identifier

**Response**: `GenerationStatusResponse`

#### `GET /api/icf/sections/requirements`
**Description**: Get ICF section requirements and specifications  
**Response**: ICF section configuration and requirements

#### `GET /api/icf/health`
**Description**: Health check for ICF generation service  
**Response**: 
```json
{
  "status": "healthy"
}
```

---

## 📊 Data Models

### ProtocolResponse
```json
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
```

### ICFGenerationResponse
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

---

## 🔧 Technical Architecture

### Core Technologies
- **FastAPI**: Web framework
- **Qdrant**: Vector database for document storage and retrieval
- **LangGraph**: AI workflow orchestration
- **PyMuPDF**: PDF text extraction
- **Claude Sonnet 4**: Primary LLM with GPT-4o fallback

### Key Features
- **Streaming Responses**: Real-time ICF generation progress
- **RAG (Retrieval Augmented Generation)**: Context-aware document generation
- **Parallel Processing**: Concurrent section generation
- **Vector Similarity Search**: Intelligent context retrieval
- **PDF Processing**: Automated protocol text extraction and chunking

---

## 🚀 Usage Examples

### Upload a Protocol
```bash
curl -X POST "http://localhost:8000/api/protocols/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@protocol.pdf" \
  -F "study_acronym=STUDY-123" \
  -F "protocol_title=Safety Study of Drug X"
```

### Generate ICF
```bash
curl -X POST "http://localhost:8000/api/icf/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "protocol_collection_name": "your-collection-name",
    "protocol_metadata": {
      "protocol_title": "Your Study Title"
    }
  }'
```

### Stream ICF Generation
```bash
curl -X POST "http://localhost:8000/api/icf/generate-stream" \
  -H "Content-Type: application/json" \
  -H "Accept: text/event-stream" \
  -d '{
    "protocol_collection_name": "your-collection-name"
  }'
```

---

## 📝 Notes

- This API supports the **First MVP** focusing on ICF (Informed Consent Form) generation only
- Site Checklist functionality is planned for Phase 2
- All endpoints use JSON for request/response bodies unless specified otherwise
- The system is production-ready for ICF generation workflows
- CORS is configured for `localhost:3000` and `localhost:5173` (React dev servers)

---

## 🔗 Related Documentation

- [Project PRD](./prd.md)
- [Technical Architecture](./architecture.md)
- [Deployment Checklist](./deployment-checklist.md)
- [Epic Documentation](./prd/) 