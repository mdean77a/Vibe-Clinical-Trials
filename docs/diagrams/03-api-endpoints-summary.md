# API Endpoints Summary

Complete reference of all backend API endpoints with methods, purposes, and response types.

## 📊 Endpoints Overview

| Category | Endpoints | Description |
|----------|-----------|-------------|
| **Health** | 2 | Application health and status |
| **Protocols** | 7 | Protocol management and CRUD |
| **ICF Generation** | 7 | AI-powered document generation |
| **Total** | **16** | Complete API surface |

---

## 🏠 Health Check Endpoints

| Method | Endpoint | Purpose | Response Type |
|--------|----------|---------|---------------|
| `GET` | `/` | Root health check | `{"message": "...", "version": "...", "status": "healthy"}` |
| `GET` | `/api/health` | Dedicated health endpoint | `{"status": "healthy"}` |

**Frontend Usage:**
- `HomePage` - Application startup health verification
- Error handling and API availability detection

---

## 📄 Protocol Management Endpoints

| Method | Endpoint | Purpose | Response Type |
|--------|----------|---------|---------------|
| `POST` | `/api/protocols/` | Create new protocol | `ProtocolResponse` |
| `POST` | `/api/protocols/upload` | Upload & process PDF | `ProtocolResponse` |
| `GET` | `/api/protocols/` | List all protocols | `ProtocolResponse[]` |
| `GET` | `/api/protocols/{protocol_id}` | Get protocol by ID | `ProtocolResponse` |
| `GET` | `/api/protocols/collection/{collection_name}` | Get by collection | `ProtocolResponse` |
| `PATCH` | `/api/protocols/collection/{collection_name}/status` | Update status | `ProtocolResponse` |
| `DELETE` | `/api/protocols/collection/{collection_name}` | Delete protocol | `204 No Content` |

**Frontend Usage:**
- `HomePage` - Protocol listing and selection
- `ProtocolUpload` - PDF upload and processing
- `APIUtils` - CRUD operations

**ProtocolResponse Structure:**
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

---

## 🧾 ICF Generation Endpoints

| Method | Endpoint | Purpose | Response Type |
|--------|----------|---------|---------------|
| `POST` | `/api/icf/generate` | Generate complete ICF | `ICFGenerationResponse` |
| `POST` | `/api/icf/generate-stream` | Streaming ICF generation | `Server-Sent Events` |
| `POST` | `/api/icf/regenerate-section` | Regenerate specific section | `SectionResponse` |
| `GET` | `/api/icf/protocol/{collection_name}/summary` | Get protocol summary | `ProtocolSummaryResponse` |
| `GET` | `/api/icf/status/{task_id}` | Check generation status | `GenerationStatusResponse` |
| `GET` | `/api/icf/sections/requirements` | Get section requirements | `RequirementsResponse` |
| `GET` | `/api/icf/health` | ICF service health | `{"status": "healthy"}` |

**Frontend Usage:**
- `ICFDashboard` - Primary ICF generation interface
- Real-time streaming and section management
- Error handling and status monitoring

---

## 📝 Response Type Details

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

### Server-Sent Events (Streaming)
```json
// Event: section_start
{"event": "section_start", "data": {"section_name": "summary"}}

// Event: token (real-time updates)
{"event": "token", "data": {"section_name": "summary", "accumulated_content": "...", "token_count": 45}}

// Event: section_complete
{"event": "section_complete", "data": {"section_name": "summary", "content": "...", "word_count": 250}}

// Event: complete
{"event": "complete", "data": {"status": "completed", "errors": []}}

// Event: error
{"event": "error", "data": {"error": "Error message"}}
```

### RequirementsResponse
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
    }
    // ... 5 more sections
  ]
}
```

---

## 🔄 Request Patterns

### Standard JSON Request
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

### Multipart Form Data (File Upload)
```
Content-Type: multipart/form-data

file: [PDF binary data]
study_acronym: "STUDY-123"
protocol_title: "Protocol Title"
```

---

## 🚨 Error Handling

### Standard Error Response
```json
{
  "detail": "Specific error message"
}
```

### Common HTTP Status Codes
- `200` - Success
- `201` - Created (protocol upload)
- `204` - No Content (delete)
- `400` - Bad Request (validation error)
- `404` - Not Found (protocol/collection)
- `500` - Internal Server Error

---

## 🔗 Frontend Integration Points

### Critical API Calls by Component

**HomePage (`app/page.tsx`)**
- Line 30: `healthApi.check()` - Health verification
- Line 42: `protocolsApi.list()` - Protocol loading

**ProtocolUpload (`components/ProtocolUpload.tsx`)**
- Line 94: `protocolsApi.upload()` - PDF upload with progress

**ICFDashboard (`components/icf/ICFGenerationDashboard.tsx`)**
- Line 35: `icfApi.getSectionRequirements()` - Section config
- Line 93: `icfApi.generateStreaming()` - Real-time generation
- Line 241: `icfApi.regenerateSection()` - Section regeneration

---

## 📋 Print Guidelines

- **Format**: Table-based for easy scanning
- **Page Size**: Standard 8.5x11" paper
- **Orientation**: Portrait recommended
- **Sections**: Organized by endpoint category
- **Cross-Reference**: Links to frontend usage locations 