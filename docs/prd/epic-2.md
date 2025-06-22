# Epic 2: AI Document Generation Pipeline

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

### **Story 2.5: ICF Final Document Download**

**As a** Clinical Research Coordinator  
**I want to** download the completed ICF as a professional PDF document  
**So that** I can use it for regulatory submission and clinical trial operations

#### **Acceptance Criteria:**
- **Given** I have approved all ICF sections
- **When** I complete the review process
- **Then** I see a "Download Final ICF" button prominently displayed
- **And** clicking the button triggers PDF generation on the backend
- **And** the system generates a professionally formatted PDF with:
  - Protocol-specific filename (e.g., "STUDY123_ICF_v1_2025-01-20.pdf")
  - All approved section content in proper order
  - Professional medical document formatting
  - Document metadata (generation date, protocol info, version)
  - Proper headers, footers, and page numbering
- **And** the PDF downloads automatically to my local computer
- **And** I receive confirmation that the download was successful
- **And** the download process completes within 30 seconds

#### **Technical Notes:**
- Backend PDF generation API endpoint (`/api/icf/download-pdf`)
- Professional PDF formatting using reportlab or similar
- Protocol-specific naming convention
- Browser download trigger with proper MIME types
- Error handling for PDF generation failures

#### **Definition of Done:**
- [ ] Backend API endpoint for PDF generation implemented
- [ ] Frontend download button appears when all sections approved
- [ ] PDF generation includes all approved content
- [ ] Professional formatting with proper document structure
- [ ] Protocol-specific filename generation
- [ ] Automatic browser download functionality
- [ ] Error handling and user feedback
- [ ] Download completes within 30 seconds
- [ ] Generated PDF is suitable for regulatory submission