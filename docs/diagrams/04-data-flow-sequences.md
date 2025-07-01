# Data Flow Sequences

Complete sequence diagrams showing the data flow for each major workflow in the Clinical Trial Accelerator.

---

## 🚀 Application Startup Flow

```mermaid
sequenceDiagram
    participant User as User
    participant FE as Frontend
    participant API as FastAPI Backend
    participant Q as Qdrant DB

    Note over User,Q: Application Initialization

    User->>FE: Opens application
    FE->>API: GET /api/health
    API-->>FE: {"status": "healthy"}
    
    FE->>API: GET /api/protocols/
    API->>Q: Query all protocol collections
    Q-->>API: Protocol metadata list
    API-->>FE: ProtocolResponse[]
    
    FE->>FE: Display protocol list
    FE-->>User: Show available protocols
```

**Key Steps:**
1. User opens the application
2. Frontend checks backend health
3. Frontend loads all available protocols
4. UI displays protocol selection interface

**Error Handling:**
- If health check fails → Show "API unavailable" message
- If protocol loading fails → Show empty state with upload option

---

## 📤 Protocol Upload Flow

```mermaid
sequenceDiagram
    participant User as User
    participant FE as Frontend
    participant API as FastAPI Backend
    participant Q as Qdrant DB

    Note over User,Q: Protocol Upload & Processing

    User->>FE: Selects PDF file
    FE->>FE: Validate file (PDF, size)
    User->>FE: Enters study acronym
    FE->>FE: Validate acronym format
    
    User->>FE: Clicks upload
    FE->>API: POST /api/protocols/upload<br/>(multipart/form-data)
    
    Note over API: PDF Processing
    API->>API: Extract text with PyMuPDF
    API->>API: Chunk text (RecursiveCharacterTextSplitter)
    API->>API: Generate embeddings
    
    API->>Q: Create collection
    API->>Q: Store text chunks + embeddings
    Q-->>API: Collection created successfully
    
    API-->>FE: ProtocolResponse with collection_name
    FE->>FE: Update protocol list
    FE-->>User: Navigate to document selection
```

**Key Steps:**
1. File validation (PDF format, size limits)
2. Acronym validation (2-20 chars, alphanumeric)
3. PDF text extraction using PyMuPDF
4. Text chunking for optimal embedding
5. Vector storage in Qdrant
6. Protocol metadata creation

**Progress Tracking:**
- Frontend shows upload progress (0-100%)
- Real-time feedback during processing
- Error messages for validation failures

---

## 🧾 ICF Generation Flow (Streaming)

```mermaid
sequenceDiagram
    participant User as User
    participant FE as Frontend
    participant API as FastAPI Backend
    participant ICF as ICF Service
    participant Q as Qdrant DB
    participant LLM as Claude/GPT-4

    Note over User,LLM: Real-time ICF Generation

    User->>FE: Selects protocol
    FE->>API: GET /api/icf/sections/requirements
    API-->>FE: Required sections config
    FE->>FE: Initialize section states
    
    User->>FE: Clicks "Generate ICF"
    FE->>API: POST /api/icf/generate-stream (SSE)
    
    API->>Q: Retrieve protocol context
    Q-->>API: Relevant text chunks
    
    API->>ICF: Start LangGraph workflow
    ICF->>ICF: Initialize 7 parallel section generators
    
    loop For each section (parallel)
        ICF->>LLM: Generate section with context
        
        loop Token streaming
            LLM-->>ICF: Generated tokens
            ICF-->>API: Section progress
            API-->>FE: SSE: {"event": "token", "data": {...}}
            FE->>FE: Update section content in real-time
        end
        
        LLM-->>ICF: Section complete
        ICF-->>API: Section finished
        API-->>FE: SSE: {"event": "section_complete", "data": {...}}
        FE->>FE: Mark section as ready for review
    end
    
    ICF-->>API: All sections complete
    API-->>FE: SSE: {"event": "complete", "data": {...}}
    FE-->>User: Show completed ICF for review
```

**Key Features:**
- **Parallel Processing**: All 7 sections generate simultaneously
- **Real-time Updates**: Token-by-token content streaming
- **Progress Tracking**: Visual feedback for each section
- **Error Recovery**: Section-level error handling

**Section Types Generated:**
1. Summary - Study overview
2. Background - Medical rationale
3. Participants - Eligibility criteria
4. Procedures - Study timeline
5. Alternatives - Treatment options
6. Risks - Potential side effects
7. Benefits - Expected outcomes

---

## 🔄 Section Regeneration Flow

```mermaid
sequenceDiagram
    participant User as User
    participant FE as Frontend
    participant API as FastAPI Backend
    participant ICF as ICF Service
    participant Q as Qdrant DB
    participant LLM as Claude/GPT-4

    Note over User,LLM: Individual Section Regeneration

    User->>FE: Clicks "Regenerate" on section
    FE->>FE: Set section to "generating" state
    
    FE->>API: POST /api/icf/regenerate-section
    Note over API: Request includes section_name
    
    API->>Q: Retrieve protocol context
    Q-->>API: Relevant text chunks for section
    
    API->>ICF: Regenerate specific section
    ICF->>LLM: Generate section with fresh context
    LLM-->>ICF: New section content
    
    ICF-->>API: Section regeneration complete
    API-->>FE: SectionResponse
    
    FE->>FE: Update specific section content
    FE->>FE: Set section to "ready_for_review"
    FE-->>User: Show regenerated content
```

**Use Cases:**
- User unsatisfied with generated content
- Need different tone or focus
- Error recovery for failed sections
- Iterative content refinement

**Benefits:**
- No need to regenerate entire ICF
- Preserves approved sections
- Fast turnaround for improvements
- Maintains workflow continuity

---

## 🚨 Error Handling Flows

```mermaid
sequenceDiagram
    participant User as User
    participant FE as Frontend
    participant API as FastAPI Backend
    participant Service as Backend Service

    Note over User,Service: Error Scenarios

    alt API Unavailable
        User->>FE: Any action requiring API
        FE->>API: Any API request
        API--X FE: Connection timeout/error
        FE->>FE: Set apiHealthy = false
        FE-->>User: Show "API unavailable" message
        
    else Generation Error
        FE->>API: POST /api/icf/generate-stream
        API->>Service: Start generation
        Service--X API: Service error
        API-->>FE: SSE: {"event": "error", "data": {...}}
        FE->>FE: Show error state
        FE-->>User: Display error with retry option
        
    else Section Error
        API->>Service: Generate specific section
        Service--X API: Section generation fails
        API-->>FE: SSE: {"event": "section_error", "data": {...}}
        FE->>FE: Mark section as error state
        FE-->>User: Show section error with regenerate option
        
    else Upload Error
        FE->>API: POST /api/protocols/upload
        API--X FE: Upload processing fails
        FE->>FE: Reset upload state
        FE-->>User: Show upload error message
    end
```

**Error Recovery Strategies:**
- **Graceful Degradation**: Continue with available functionality
- **User Feedback**: Clear error messages with actionable steps
- **Retry Mechanisms**: Allow users to retry failed operations
- **Partial Success**: Handle section-level failures independently

---

## 📊 Performance Characteristics

### Typical Response Times
- **Health Check**: < 100ms
- **Protocol List**: < 500ms
- **File Upload**: 2-10 seconds (depends on file size)
- **ICF Generation**: 30-120 seconds (streaming)
- **Section Regeneration**: 10-30 seconds

### Concurrent Operations
- **Multiple Sections**: Generated in parallel
- **Real-time Streaming**: Token-by-token updates
- **Background Processing**: PDF text extraction
- **Error Isolation**: Section failures don't affect others

---

## 🔗 Integration Points

### Frontend State Management
- **Real-time Updates**: SSE event handling
- **Progress Tracking**: Visual feedback systems
- **Error States**: Component-level error boundaries
- **Session Persistence**: localStorage for protocol selection

### Backend Orchestration
- **LangGraph Workflows**: AI pipeline management
- **Vector Search**: Context retrieval optimization
- **Streaming Responses**: Server-Sent Events implementation
- **Error Recovery**: Service-level exception handling

---

## 📋 Print Guidelines

- **Page Size**: Each sequence fits on standard 8.5x11" paper
- **Orientation**: Portrait recommended
- **Sections**: Organized by workflow type
- **Detail Level**: Sufficient for debugging and development
- **Cross-Reference**: Links to related API endpoints 