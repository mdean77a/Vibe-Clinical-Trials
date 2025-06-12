# MVP User Stories - Clinical Trial Accelerator

**Project**: Clinical Trial Accelerator  
**Version**: MVP v1.0  
**Generated**: December 2024  
**Total Stories**: 15  

---

## 📋 **MVP Scope Overview**

### **MVP Goals:**
- Demonstrate AI-powered clinical trial document generation
- Show platform extensibility across document types
- Provide realistic protocol management workflow
- Validate core value proposition with Clinical Research Coordinators

### **MVP Constraints:**
- Single user (no authentication)
- Two document types only (ICF + Site Initiation Checklist)
- Local deployment (SQLite + Qdrant Docker)
- Basic features only (no advanced editing/regeneration)

### **Epic Structure:**
- **Epic 1**: Protocol Management System (6 stories)
- **Epic 2**: AI Document Generation Pipeline (4 stories)
- **Epic 4**: Basic Review Interface (5 stories)

---

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

### **Story 1.5: Protocol Database Record Creation**

**As a** system administrator  
**I want** uploaded protocols to be stored in the database with proper metadata  
**So that** they can be retrieved and managed effectively

#### **Acceptance Criteria:**
- **Given** a protocol has been uploaded and metadata extracted/confirmed
- **When** the user confirms the protocol information
- **Then** a new record is created in the SQLite database
- **And** the record includes study_acronym, protocol_title, collection_name, upload_date
- **And** a unique collection_name is generated for Qdrant
- **And** the protocol status is set to 'processing'
- **And** the file_path is stored for future reference

#### **Technical Notes:**
- Generate unique collection_name (e.g., study_acronym + timestamp)
- SQLite INSERT operation with proper error handling
- Ensure collection_name uniqueness

#### **Definition of Done:**
- [ ] SQLite database record created successfully
- [ ] Unique collection_name generated
- [ ] All required fields populated
- [ ] Database constraints respected
- [ ] Error handling for duplicate entries

---

### **Story 1.6: Qdrant Vector Database Processing**

**As a** system  
**I want to** process uploaded protocols into vector embeddings  
**So that** RAG retrieval can work effectively for document generation

#### **Acceptance Criteria:**
- **Given** a protocol PDF has been uploaded and database record created
- **When** the vector processing begins
- **Then** the PDF text is extracted using PyMuPDF
- **And** the text is chunked into appropriate segments (500-1000 tokens)
- **And** each chunk is embedded using OpenAI embeddings
- **And** embeddings are stored in Qdrant with the protocol's collection_name
- **And** the protocol status is updated to 'processed' upon completion
- **And** processing errors are logged and reported

#### **Technical Notes:**
- PyMuPDF for text extraction
- Text chunking strategy for optimal retrieval
- OpenAI text-embedding-ada-002 model
- Qdrant collection creation and document insertion
- Error handling and status updates

#### **Definition of Done:**
- [ ] PDF text extraction working
- [ ] Text chunking implemented (500-1000 tokens)
- [ ] OpenAI embeddings generated
- [ ] Qdrant collection created and populated
- [ ] Protocol status updated to 'processed'
- [ ] Error handling and logging implemented

---

## 🤖 **EPIC 2: AI Document Generation Pipeline**

### **Story 2.1: Document Type Selection Interface**

**As a** Clinical Research Coordinator  
**I want to** choose between generating an ICF or Site Initiation Checklist  
**So that** I can create the specific document type I need

#### **Acceptance Criteria:**
- **Given** I have selected an active protocol
- **When** I reach the document type selection page
- **Then** I see the active protocol information displayed (study acronym, title)
- **And** I see two clear options: "Generate Informed Consent Form" and "Generate Site Initiation Checklist"
- **And** each option shows a brief description of what will be generated
- **And** I can click on either option to proceed
- **And** I can return to protocol selection if needed

#### **Technical Notes:**
- Display active protocol context from session
- Clear navigation between document types
- Return to protocol selection capability

#### **Definition of Done:**
- [ ] Active protocol information displayed
- [ ] Two document type options clearly presented
- [ ] Navigation to generation workflows functional
- [ ] Return to protocol selection works
- [ ] UI is intuitive and professional

---

### **Story 2.2: ICF Generation Workflow**

**As a** Clinical Research Coordinator  
**I want to** generate an Informed Consent Form from the active protocol  
**So that** I can create a draft ICF for regulatory submission

#### **Acceptance Criteria:**
- **Given** I have selected "Generate Informed Consent Form"
- **When** the generation process starts
- **Then** I see a progress indicator showing generation status
- **And** the system retrieves relevant context from the protocol's Qdrant collection
- **And** the LangGraph ICF workflow generates all required sections:
  - Study title and purpose
  - Procedures description
  - Risks and benefits
  - Participant rights
  - Contact information
  - Withdrawal procedures
- **And** the complete ICF is displayed within 5 minutes
- **And** each section is clearly labeled and editable

#### **Technical Notes:**
- RAG retrieval from active protocol's Qdrant collection
- LangGraph workflow with ICF-specific nodes
- Section-based generation and assembly
- Progress tracking and status updates

#### **Definition of Done:**
- [ ] RAG retrieval from correct Qdrant collection
- [ ] LangGraph ICF workflow implemented
- [ ] All required ICF sections generated
- [ ] Generation completes within 5 minutes
- [ ] Generated content displayed in editable format
- [ ] Progress indicator functional

---

### **Story 2.3: Site Initiation Checklist Generation Workflow**

**As a** Clinical Research Coordinator  
**I want to** generate a Site Initiation Checklist from the active protocol  
**So that** I can prepare for study startup activities

#### **Acceptance Criteria:**
- **Given** I have selected "Generate Site Initiation Checklist"
- **When** the generation process starts
- **Then** I see a progress indicator showing generation status
- **And** the system retrieves relevant context from the protocol's Qdrant collection
- **And** the LangGraph Site Initiation workflow generates all required sections:
  - Regulatory requirements and approvals
  - Staff training requirements
  - Equipment and supplies needed
  - Documentation requirements
  - Site preparation tasks
  - Timeline and milestones
- **And** the complete checklist is displayed within 5 minutes
- **And** each section is clearly labeled and editable

#### **Technical Notes:**
- RAG retrieval from active protocol's Qdrant collection
- LangGraph workflow with Site Initiation-specific nodes
- Checklist format with actionable items
- Progress tracking and status updates

#### **Definition of Done:**
- [ ] RAG retrieval from correct Qdrant collection
- [ ] LangGraph Site Initiation workflow implemented
- [ ] All required checklist sections generated
- [ ] Generation completes within 5 minutes
- [ ] Generated content displayed in editable format
- [ ] Checklist format is actionable and clear

---

### **Story 2.4: RAG Context Retrieval System**

**As a** system  
**I want to** retrieve relevant protocol context for document generation  
**So that** generated documents are accurate and protocol-specific

#### **Acceptance Criteria:**
- **Given** a document generation request for the active protocol
- **When** the RAG system queries the protocol's Qdrant collection
- **Then** it retrieves the most relevant text chunks for the document type
- **And** relevance scoring ensures >90% context accuracy
- **And** retrieved context is passed to the LangGraph workflow
- **And** the system handles cases where insufficient context is found
- **And** retrieval completes within 3 seconds

#### **Technical Notes:**
- Semantic search in Qdrant using document type-specific queries
- Relevance scoring and filtering
- Context assembly for LangGraph input
- Error handling for insufficient context

#### **Definition of Done:**
- [ ] Qdrant semantic search implemented
- [ ] Relevance scoring >90% accuracy
- [ ] Context retrieval within 3 seconds
- [ ] Proper error handling for edge cases
- [ ] Context properly formatted for LangGraph

---

## 📝 **EPIC 4: Basic Review Interface**

### **Story 4.1: Document Section Display**

**As a** Clinical Research Coordinator  
**I want to** view the generated document in a clear, section-based format  
**So that** I can review and edit each section individually

#### **Acceptance Criteria:**
- **Given** a document has been generated (ICF or Site Initiation Checklist)
- **When** I view the document
- **Then** I see a three-panel layout: sidebar navigation, main editor, protocol viewer
- **And** the sidebar shows all document sections with status indicators
- **And** the main editor displays the currently selected section
- **And** the protocol viewer shows relevant protocol text for reference
- **And** I can navigate between sections using the sidebar
- **And** the active protocol information is displayed in the header

#### **Technical Notes:**
- Three-panel responsive layout
- Section-based navigation
- Status indicators for each section
- Protocol reference panel

#### **Definition of Done:**
- [ ] Three-panel layout implemented
- [ ] Section navigation functional
- [ ] Status indicators working
- [ ] Protocol reference panel displays relevant text
- [ ] Responsive design works on desktop
- [ ] Active protocol context displayed

---

### **Story 4.2: Basic Text Editing Capability**

**As a** Clinical Research Coordinator  
**I want to** edit the generated document sections  
**So that** I can refine the content to meet specific requirements

#### **Acceptance Criteria:**
- **Given** I am viewing a document section
- **When** I click in the editor area
- **Then** I can edit the text content directly
- **And** changes are saved automatically as I type
- **And** I can use basic formatting (bold, italic, bullet points)
- **And** I can undo/redo changes
- **And** the section status updates to "Modified" when edited
- **And** I see a visual indicator that changes have been saved

#### **Technical Notes:**
- Rich text editor (basic formatting only)
- Auto-save functionality
- Undo/redo capability
- Section status tracking

#### **Definition of Done:**
- [ ] Text editing functional in all sections
- [ ] Auto-save working
- [ ] Basic formatting options available
- [ ] Undo/redo implemented
- [ ] Section status tracking accurate
- [ ] Save indicators clear to user

---

### **Story 4.3: Section Approval Workflow**

**As a** Clinical Research Coordinator  
**I want to** approve individual sections after review  
**So that** I can track my progress and ensure quality control

#### **Acceptance Criteria:**
- **Given** I have reviewed and edited a document section
- **When** I click the "Approve Section" button
- **Then** the section status changes to "Approved"
- **And** the section is visually marked as approved (green indicator)
- **And** I can still view the section but editing is disabled
- **And** I can "Unapprove" the section if I need to make changes
- **And** the overall document status shows progress (e.g., "3 of 6 sections approved")

#### **Technical Notes:**
- Section-level approval status tracking
- Visual status indicators
- Approval/unapproval toggle functionality
- Overall progress tracking

#### **Definition of Done:**
- [ ] Section approval functionality working
- [ ] Visual status indicators clear
- [ ] Approved sections become read-only
- [ ] Unapproval capability functional
- [ ] Overall progress tracking accurate

---

### **Story 4.4: Document Export Functionality**

**As a** Clinical Research Coordinator  
**I want to** export the completed document  
**So that** I can use it for regulatory submission or further review

#### **Acceptance Criteria:**
- **Given** I have completed reviewing the document
- **When** I click "Export Document"
- **Then** the system generates a formatted document file
- **And** the filename includes the protocol acronym and document type (e.g., "STUDY123_ICF_v1.pdf")
- **And** the exported document maintains proper formatting
- **And** the export includes all approved and modified sections
- **And** I can download the file to my local system
- **And** the export process completes within 30 seconds

#### **Technical Notes:**
- Document formatting and PDF generation
- Protocol-specific naming conventions
- File download capability
- Export processing within time limits

#### **Definition of Done:**
- [ ] Document export generates properly formatted file
- [ ] Filename follows protocol-specific naming convention
- [ ] All sections included in export
- [ ] Download functionality working
- [ ] Export completes within 30 seconds
- [ ] Multiple export formats supported (PDF minimum)

---

### **Story 4.5: Return to Document Type Selection**

**As a** Clinical Research Coordinator  
**I want to** return to document type selection after completing a document  
**So that** I can generate additional document types for the same protocol

#### **Acceptance Criteria:**
- **Given** I have completed working on a document (ICF or Site Initiation Checklist)
- **When** I click "Generate Another Document" or similar navigation
- **Then** I return to the document type selection page
- **And** the same protocol remains active
- **And** I can select the other document type
- **And** my previous work is saved and accessible
- **And** I can switch between protocols if needed

#### **Technical Notes:**
- Navigation back to document type selection
- Session state preservation
- Document persistence
- Protocol switching capability

#### **Definition of Done:**
- [ ] Navigation back to document type selection works
- [ ] Active protocol maintained in session
- [ ] Previous work preserved and accessible
- [ ] Protocol switching capability functional
- [ ] User workflow is intuitive and efficient

---

## 📊 **Development Planning**

### **Sprint Breakdown:**

#### **Sprint 1: Protocol Management Foundation (Weeks 1-2)**
- Story 1.1: Protocol Selection Landing Page
- Story 1.2: Protocol Selection Workflow
- Story 1.3: New Protocol Upload Interface

#### **Sprint 2: Protocol Processing (Weeks 3-4)**
- Story 1.4: Automatic Metadata Extraction
- Story 1.5: Protocol Database Record Creation
- Story 1.6: Qdrant Vector Database Processing

#### **Sprint 3: Document Generation (Weeks 5-6)**
- Story 2.1: Document Type Selection Interface
- Story 2.2: ICF Generation Workflow
- Story 2.3: Site Initiation Checklist Generation Workflow
- Story 2.4: RAG Context Retrieval System

#### **Sprint 4: Review Interface (Weeks 7-8)**
- Story 4.1: Document Section Display
- Story 4.2: Basic Text Editing Capability
- Story 4.3: Section Approval Workflow
- Story 4.4: Document Export Functionality
- Story 4.5: Return to Document Type Selection

### **Key Dependencies:**
1. SQLite database setup (required for Stories 1.1, 1.2, 1.5)
2. Qdrant Docker container (required for Stories 1.6, 2.4)
3. OpenAI API integration (required for Stories 1.6, 2.2, 2.3, 2.4)
4. LangGraph implementation (required for Stories 2.2, 2.3)

### **Technical Stack:**
- **Frontend**: React + Vite + Tailwind CSS
- **Backend**: FastAPI (Python)
- **Database**: SQLite (protocol metadata)
- **Vector Database**: Qdrant (Docker container)
- **AI**: OpenAI embeddings + LangGraph workflows
- **PDF Processing**: PyMuPDF

---

## ✅ **Story Completion Tracking**

### **Epic 1: Protocol Management System**
- [ ] Story 1.1: Protocol Selection Landing Page
- [ ] Story 1.2: Protocol Selection Workflow
- [ ] Story 1.3: New Protocol Upload Interface
- [ ] Story 1.4: Automatic Metadata Extraction
- [ ] Story 1.5: Protocol Database Record Creation
- [ ] Story 1.6: Qdrant Vector Database Processing

### **Epic 2: AI Document Generation Pipeline**
- [ ] Story 2.1: Document Type Selection Interface
- [ ] Story 2.2: ICF Generation Workflow
- [ ] Story 2.3: Site Initiation Checklist Generation Workflow
- [ ] Story 2.4: RAG Context Retrieval System

### **Epic 4: Basic Review Interface**
- [ ] Story 4.1: Document Section Display
- [ ] Story 4.2: Basic Text Editing Capability
- [ ] Story 4.3: Section Approval Workflow
- [ ] Story 4.4: Document Export Functionality
- [ ] Story 4.5: Return to Document Type Selection

---

## 🎯 **MVP Success Criteria**

1. **Protocol Management**: Successfully display processed protocols and enable selection of active protocol
2. **Upload & Processing**: Successfully upload new protocol, extract metadata, create Qdrant collection, and update database
3. **Document Generation**: Successfully generate both ICF and Site Initiation Checklist from selected protocol
4. **Quality**: Generated documents contain all required regulatory sections for their respective types
5. **Extensibility**: Demonstrate platform can handle different document structures and content types
6. **Workflow**: Complete end-to-end workflow (select/upload protocol → choose document type → generate → review → export) in <30 minutes per document
7. **User Validation**: Single CRC can complete full workflow for both document types without technical support
8. **Business Value**: Show company leadership how platform scales across document types and manages multiple protocols

---

**This MVP story backlog provides a complete foundation for developing the Clinical Trial Accelerator MVP, demonstrating both core functionality and platform extensibility to company leadership.**