# Clinical Trial Accelerator - Navigation and API Connections

## Overview
This document summarizes all navigation connections within the frontend and all API connections between the frontend and backend of the Clinical Trial Accelerator application.

## Frontend Navigation Structure

### Application Routes
The application uses Next.js 15 App Router with a file-based routing system:

1. **Home Page (`/`)**
   - **File**: `frontend/app/page.tsx`
   - **Purpose**: Protocol selection and upload entry point
   - **Navigation**: Routes to `/document-selection` after protocol selection/upload

2. **Document Selection (`/document-selection`)**
   - **File**: `frontend/app/document-selection/page.tsx`
   - **Purpose**: Choose document type to generate (ICF or Site Checklist)
   - **Navigation**: Routes to `/informed-consent` or `/site-checklist`

3. **Informed Consent (`/informed-consent`)**
   - **File**: `frontend/app/informed-consent/page.tsx`
   - **Purpose**: ICF generation and review interface
   - **Navigation**: Can return to `/document-selection`

4. **Site Checklist (`/site-checklist`)**
   - **File**: `frontend/app/site-checklist/page.tsx`
   - **Purpose**: Site initiation checklist generation (placeholder - "Coming Soon")
   - **Navigation**: Can return to `/document-selection`

### Navigation Flow
The application follows a linear, wizard-like navigation pattern:

```
Home (/) 
  ↓ [Protocol Selection/Upload]
Document Selection (/document-selection)
  ↓ [Document Type Choice]
ICF Generation (/informed-consent) OR Site Checklist (/site-checklist)
  ↓ [Back Navigation Available]
Document Selection (/document-selection)
  ↓ [Back Navigation Available]  
Home (/)
```

### Navigation Implementation
- **Method**: Next.js `useRouter` hook with `router.push()`
- **State Management**: localStorage for protocol persistence across routes
- **URL Parameters**: Consistent `protocolId` and `studyAcronym` query parameters
- **Navigation Guards**: All pages validate protocol existence before rendering

### Key Navigation Components
- **ProtocolSelector**: Handles protocol selection and triggers navigation
- **ICFGenerationDashboard**: Main ICF interface with return navigation callback

## Frontend-Backend API Connections

### API Configuration
- **Base URL**: `http://localhost:8000/api` (development)
- **API Client**: `frontend/src/utils/api.ts`
- **CORS**: Configured for `localhost:3000` and `localhost:5173`

### Complete API Endpoint Mapping

#### Health Check Endpoints
| HTTP Method | Endpoint | Frontend Usage | Purpose |
|------------|----------|----------------|---------|
| `GET` | `/` | `healthApi.root()` | API root information |
| `GET` | `/api/health` | `healthApi.check()` | Main health check |
| `GET` | `/api/icf/health` | `icfApi.health()` | ICF service health check |

#### Protocol Management Endpoints
| HTTP Method | Endpoint | Frontend Usage | Purpose |
|------------|----------|----------------|---------|
| `POST` | `/api/protocols` | `protocolsApi.create()` | Create new protocol |
| `POST` | `/api/protocols/upload` | `protocolsApi.upload()` | Upload & process PDF |
| `GET` | `/api/protocols` | `protocolsApi.list()` | List all protocols |
| `GET` | `/api/protocols/{protocol_id}` | `protocolsApi.getById()` | Get protocol by ID |
| `GET` | `/api/protocols/collection/{collection_name}` | `protocolsApi.getByCollection()` | Get protocol by collection |
| `PATCH` | `/api/protocols/{protocol_id}/status` | `protocolsApi.updateStatus()` | Update protocol status |
| `DELETE` | `/api/protocols/{protocol_id}` | `protocolsApi.delete()` | Delete protocol |

#### ICF Generation Endpoints
| HTTP Method | Endpoint | Frontend Usage | Purpose |
|------------|----------|----------------|---------|
| `POST` | `/api/icf/generate` | `icfApi.generate()` | Generate complete ICF |
| `POST` | `/api/icf/generate-stream` | `icfApi.generateStreaming()` | **Streaming ICF generation** |
| `POST` | `/api/icf/regenerate-section` | `icfApi.regenerateSection()` | Regenerate specific section |
| `GET` | `/api/icf/protocol/{collection_name}/summary` | `icfApi.getProtocolSummary()` | Get protocol summary |
| `GET` | `/api/icf/sections/requirements` | `icfApi.getSectionRequirements()` | Get ICF section requirements |
| `GET` | `/api/icf/status/{task_id}` | `icfApi.getStatus()` | Get generation status |

### Component-Level API Usage

#### HomePage (`frontend/app/page.tsx`)
- `healthApi.check()` - Check API health on load
- `protocolsApi.list()` - Load existing protocols
- `protocolsApi.upload()` - Via ProtocolUpload component

#### ProtocolUpload (`frontend/src/components/ProtocolUpload.tsx`)
- `protocolsApi.upload(file, metadata)` - Upload PDF with form data
- **Data Flow**: File + study_acronym + protocol_title → Backend processing → Protocol creation

#### ICFGenerationDashboard (`frontend/src/components/icf/ICFGenerationDashboard.tsx`)
- `icfApi.getSectionRequirements()` - Initialize section structure
- `icfApi.generateStreaming()` - **Real-time streaming generation**
- `icfApi.regenerateSection()` - Regenerate individual sections
- **Data Flow**: Collection name → Streaming tokens → Real-time section updates

### Real-Time Streaming Connection

#### Server-Sent Events (SSE) Implementation
- **Endpoint**: `POST /api/icf/generate-stream`
- **Frontend**: Generator function with event stream parsing
- **Event Types**:
  - `section_start` - Section begins generating
  - `token` - Real-time token streaming
  - `section_complete` - Section finished
  - `section_error` - Section generation error
  - `complete` - All sections finished
  - `error` - Global error

This enables real-time token-by-token ICF generation display in the frontend.

### Data Models and Types

Frontend and backend use consistent data models:
- **Protocol**: Study information, upload metadata, status tracking
- **ICF Sections**: Structured content with requirements and generated text
- **Stream Events**: Real-time generation updates and status changes

### Backend Architecture Integration
- **Storage**: Qdrant vector database (unified metadata + embeddings)
- **Processing**: PyMuPDF for PDF text extraction
- **AI Pipeline**: LangGraph workflows with RAG retrieval
- **Embeddings**: OpenAI embeddings for semantic search

### Current Implementation Status

#### ✅ Fully Implemented
- Protocol upload and management system
- ICF generation with real-time streaming
- Complete frontend-backend integration
- Section regeneration capabilities

#### 🚧 In Progress
- Site checklist generation (UI complete, API endpoints pending)

#### 📋 Future Planned
- Statistical Analysis Plans
- Data Management Plans
- CRF templates

## Security and Configuration

### CORS Configuration
- Development origins: `localhost:3000`, `localhost:5173`
- All methods and headers allowed
- Credentials enabled

### Authentication
- **Current State**: No authentication/authorization implemented
- **Session Management**: localStorage for protocol persistence
- **Security**: CORS-only protection for development environment

## Error Handling

### Frontend
- API errors caught and displayed to users
- Network failures handled gracefully
- Form validation before API calls

### Backend
- Custom exception types (`QdrantError`, `DocumentGenerationError`)
- Standard HTTP status codes (400, 404, 500)
- Comprehensive logging for debugging

This document provides a complete mapping of the application's navigation structure and API integration patterns, showing how the frontend and backend work together to provide the clinical trial document generation workflow.