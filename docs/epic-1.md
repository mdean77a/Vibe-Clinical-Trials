# Epic 1: Protocol Management System

## 🎯 **EPIC 1: Protocol Management System**

### **Story 1.1: Protocol Selection Landing Page**

**As a** Clinical Research Coordinator  
**I want to** see a list of previously processed protocols when I open the application  
**So that** I can quickly select an existing protocol to work with without re-uploading

#### **Acceptance Criteria:**
- **Given** I open the Clinical Trial Accelerator application
- **When** the landing page loads
- **Then** I see a list of all previously processed protocols
- **And** each protocol displays the study acronym and protocol title
- **And** I see an "Upload New Protocol" button
- **And** the list is sorted by most recently uploaded first
- **And** if no protocols exist, I see a message "No protocols found. Upload your first protocol to get started."

#### **Technical Notes:**
- Query SQLite database for all protocols with status 'processed'
- Display in table/card format with study_acronym and protocol_title
- Handle empty state gracefully

#### **Definition of Done:**
- [ ] Landing page displays protocol list from SQLite database
- [ ] Empty state handled appropriately
- [ ] Upload new protocol button functional
- [ ] Responsive design works on desktop
- [ ] Basic error handling for database connection issues

---

### **Story 1.2: Protocol Selection Workflow**

**As a** Clinical Research Coordinator  
**I want to** select an existing protocol from the list  
**So that** I can generate documents for that specific study

#### **Acceptance Criteria:**
- **Given** I am on the protocol selection landing page
- **When** I click on a protocol from the list
- **Then** that protocol becomes the active protocol for my session
- **And** I am navigated to the document type selection page
- **And** the active protocol information (study acronym, title) is displayed in the header
- **And** the system stores the collection_name for RAG retrieval

#### **Technical Notes:**
- Set active protocol in session/state management
- Store collection_name for Qdrant queries
- Update UI to show active protocol context

#### **Definition of Done:**
- [ ] Protocol selection updates session state
- [ ] Navigation to document type selection works
- [ ] Active protocol displayed in UI header
- [ ] Collection name properly stored for RAG queries
- [ ] Session persists active protocol until changed

---

### **Story 1.3: New Protocol Upload Interface**

**As a** Clinical Research Coordinator  
**I want to** upload a new clinical trial protocol PDF  
**So that** I can generate documents for a study not yet in the system

#### **Acceptance Criteria:**
- **Given** I click "Upload New Protocol" from the landing page
- **When** the upload interface opens
- **Then** I see a drag-and-drop area for PDF files
- **And** I can browse and select a PDF file
- **And** I see file validation (PDF only, max 50MB)
- **And** I see upload progress indicator
- **And** I receive clear error messages for invalid files

#### **Technical Notes:**
- File validation: PDF format, 50MB max size
- Progress indicator for upload process
- Error handling for file type, size, corruption

#### **Definition of Done:**
- [ ] Drag-and-drop upload interface functional
- [ ] File validation works (PDF only, 50MB max)
- [ ] Upload progress indicator displays
- [ ] Error messages clear and actionable
- [ ] File successfully stored in uploads directory

---

### **Story 1.4: Automatic Metadata Extraction**

**As a** Clinical Research Coordinator  
**I want** the system to automatically extract study information from uploaded protocols  
**So that** I don't have to manually enter study acronym and protocol title

#### **Acceptance Criteria:**
- **Given** I have uploaded a valid protocol PDF
- **When** the system processes the document
- **Then** it automatically extracts the study acronym
- **And** it extracts the protocol title
- **And** it displays the extracted information for my confirmation
- **And** I can edit the information if the extraction is incorrect
- **And** I can proceed with the extracted or corrected information

#### **Technical Notes:**
- Use PyMuPDF for text extraction
- Implement regex patterns for study acronym detection
- Extract title from document headers/first pages
- Provide manual override capability

#### **Definition of Done:**
- [ ] Study acronym extraction implemented
- [ ] Protocol title extraction implemented
- [ ] Extracted information displayed for confirmation
- [ ] Manual editing capability provided
- [ ] Extraction accuracy >80% for standard protocol formats

---

### **Story 1.5: Qdrant Document Creation**

**As a** system administrator  
**I want** uploaded protocols to be stored in Qdrant with proper metadata  
**So that** they can be retrieved and managed effectively

#### **Acceptance Criteria:**
- **Given** a protocol has been uploaded and metadata extracted/confirmed
- **When** the user confirms the protocol information
- **Then** protocol metadata is embedded in Qdrant document metadata
- **And** metadata includes: study_acronym, protocol_title, filename, upload_date, status
- **And** user-provided acronym is stored in metadata during upload
- **And** the protocol status is set to 'processing'
- **And** no separate file persistence is needed (user retains original PDF)

#### **Technical Notes:**
- Store metadata directly in Qdrant document metadata fields
- Use study_acronym provided by user during upload
- Generate unique document IDs for Qdrant collections
- Status field tracks processing state ('processing' → 'completed')

#### **Definition of Done:**
- [ ] Qdrant document created with embedded metadata
- [ ] All required metadata fields populated
- [ ] User-provided study acronym properly stored
- [ ] Status tracking functional
- [ ] No separate database dependencies

---

### **Story 1.6: Unified Qdrant Processing**

**As a** system  
**I want to** process uploaded protocols into vector embeddings with metadata storage  
**So that** RAG retrieval and protocol management work through a single Qdrant system

#### **Acceptance Criteria:**
- **Given** a protocol PDF has been uploaded and user has provided study acronym
- **When** the unified processing begins
- **Then** the PDF text is extracted using PyMuPDF (no file persistence needed)
- **And** the text is chunked into appropriate segments (500-1000 tokens)
- **And** each chunk is embedded using OpenAI embeddings
- **And** embeddings AND metadata are stored together in Qdrant
- **And** protocol metadata (filename, study_acronym, upload_date, status) stored in document metadata
- **And** the protocol status is updated to 'completed' upon completion
- **And** processing errors are logged and reported

#### **Technical Notes:**
- PyMuPDF for text extraction from uploaded PDF
- Text chunking strategy for optimal retrieval
- OpenAI text-embedding-ada-002 model
- Single Qdrant operation: embed chunks + store metadata
- Protocol metadata (filename, study_acronym, upload_date, status) stored in document metadata
- Memory-based Qdrant initially, external URL upgrade path
- No PDF file persistence required

#### **Definition of Done:**
- [ ] PDF text extraction working (no file storage)
- [ ] Text chunking implemented (500-1000 tokens)
- [ ] OpenAI embeddings generated
- [ ] Qdrant collection created with unified storage
- [ ] Protocol metadata embedded in Qdrant documents
- [ ] Protocol status updated to 'completed'
- [ ] Memory-based Qdrant setup functional
- [ ] Error handling and logging implemented