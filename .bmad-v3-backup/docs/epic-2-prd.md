# Epic 2: AI Document Generation - Product Requirements Document (PRD)

## Goals and Background Context

### Goals

- Enable clinical trial teams to generate high-quality, regulation-ready Informed Consent Forms from uploaded protocol PDFs
- Implement human-in-the-loop review workflow ensuring 100% human approval for regulatory compliance
- Provide section-by-section AI generation with streaming feedback and comprehensive revision capabilities
- Deliver professional PDF output using LaTeX formatting for immediate clinical use
- Establish foundation for future clinical document generation (Site Initiation Checklists, additional document types)

### Background Context

The Vibe Clinical Trials project has successfully completed Epic 1, establishing a robust PDF processing pipeline that extracts, chunks, and stores clinical trial protocols in a Qdrant vector database. This foundation enables sophisticated document generation capabilities using the stored protocol data as context.

Clinical trial document generation operates in a highly regulated environment where human oversight is mandatory. The system must generate near-complete drafts (approaching 100% completeness) while ensuring every section receives human review and approval before final output. This approach maximizes AI efficiency while maintaining regulatory compliance and quality standards.

## Requirements

### Functional

- FR1: The system shall generate Informed Consent Forms with seven standardized sections: Summary, Background, Number of Participants, Study Procedures, Alternative Procedures, Risks, and Benefits
- FR2: Each section shall be generated using specialized AI prompts tailored to the specific content requirements of that section
- FR3: Generated content shall stream into individual text boxes in real-time, providing immediate visual feedback to users
- FR4: Users shall be able to select any section for review with three action options: approve as-is, direct text editing, or LLM regeneration with custom instructions
- FR5: The system shall provide an "Approve All" bulk action for rapid workflow completion during prompt experimentation
- FR6: Approved sections shall be locked but automatically unlock when users attempt to edit, enabling flexible revision workflows
- FR7: After all sections are approved, users shall preview the complete document before final PDF generation
- FR8: The system shall generate professional PDF documents using LaTeX formatting
- FR9: Site Initiation Checklist generation shall be implemented as a secondary MVP feature following the same workflow pattern
- FR10: The system shall integrate seamlessly with existing protocol selection and document type selection workflows

### Non Functional

- NFR1: Document generation shall complete within 60 seconds for all seven ICF sections
- NFR2: The system shall maintain session state throughout the review process without requiring save functionality
- NFR3: Generated content shall approach 100% completeness to minimize human writing requirements
- NFR4: The user interface shall provide clear visual indicators for section status (generating, ready for review, approved, locked)
- NFR5: All generated content shall be stored temporarily and discarded after session completion to ensure data privacy
- NFR6: The system shall handle concurrent section generation without performance degradation
- NFR7: PDF generation shall produce consistently formatted, professional documents suitable for regulatory submission

## User Interface Design Goals

### Overall UX Vision

The interface prioritizes efficiency and clarity for clinical professionals who need to rapidly review and approve AI-generated content. The design emphasizes immediate visual feedback, intuitive section management, and seamless transitions between review, editing, and approval actions.

### Key Interaction Paradigms

- **Streaming Generation**: Real-time content population provides immediate engagement and progress visibility
- **Section-Based Review**: Independent section management allows flexible, non-linear review workflows
- **Context Switching**: Smooth transitions between approve/edit/regenerate modes without page reloads
- **Bulk Operations**: "Approve All" functionality supports rapid experimentation and workflow acceleration
- **Progressive Disclosure**: Document preview and final review stages reveal complexity only when needed

### Core Screens and Views

- **ICF Generation Screen**: Primary workspace displaying all seven sections with streaming content generation
- **Section Review Interface**: Focused editing environment for individual section refinement
- **Document Preview Screen**: Full document review before final PDF generation
- **Download Confirmation**: Final step confirming successful PDF creation and providing download access

### Accessibility

Standard web accessibility practices (WCAG 2.1 AA compliance) with particular attention to:
- Clear visual indicators for section status and actions
- Keyboard navigation support for all interactive elements
- Screen reader compatibility for generated content

### Branding

Consistent with existing Vibe Clinical Trials branding:
- Professional healthcare aesthetic with clean, modern design
- Clear visual hierarchy emphasizing content over decoration
- Trustworthy color scheme appropriate for regulated environments

### Target Device and Platforms

Web responsive design optimized for:
- Desktop workstations (primary use case)
- Tablet devices for mobile review scenarios
- Modern browsers with full JavaScript support

## Technical Assumptions

### Repository Structure

Monorepo structure maintained, integrating with existing frontend/backend architecture established in Epic 1.

### Service Architecture

Extension of existing FastAPI backend with new document generation endpoints, maintaining the current local deployment model.

### Testing Requirements

- Unit tests for individual section generation functions
- Integration tests for complete ICF generation workflow
- End-to-end tests for human-in-the-loop review process
- PDF generation validation tests
- API endpoint testing for all new generation endpoints

### Additional Technical Assumptions and Requests

- LaTeX PDF generation requires server-side processing capabilities
- Streaming content delivery necessitates WebSocket or Server-Sent Events implementation
- Document generation services must integrate with existing Qdrant vector database connections
- Session management required for multi-section review workflow state
- Error handling and retry mechanisms for AI generation failures
- Content validation to ensure generated text meets basic quality standards

## Epics

### Epic List

- Epic 2.1 Informed Consent Form Generation: Implement complete ICF generation workflow with human-in-the-loop review
- Epic 2.2 Site Initiation Checklist Generation: Extend generation capabilities to site checklists using established workflow patterns
- Epic 2.3 Document Export and Management: Enhance PDF generation and add document management capabilities

## Epic 2.1 Informed Consent Form Generation

This epic delivers the core AI document generation functionality, enabling clinical teams to create regulation-ready Informed Consent Forms through an intelligent human-in-the-loop workflow. The implementation establishes the foundation for all future clinical document generation capabilities.

### Story 2.1.1 Backend ICF Generation Service

As a clinical trial administrator,
I want the system to generate ICF sections using protocol data stored in Qdrant,
so that I can create comprehensive informed consent documents based on our specific trial protocols.

#### Acceptance Criteria

- AC1: Create API endpoint `/api/generate-icf` that accepts protocol ID and returns generated ICF sections
- AC2: Implement seven specialized generation functions for each ICF section (Summary, Background, Number of Participants, Study Procedures, Alternative Procedures, Risks, Benefits)
- AC3: Each section generation uses tailored prompts optimized for that specific content type
- AC4: Generated content integrates relevant protocol data retrieved from Qdrant collections
- AC5: API returns structured JSON with section identifiers, content, and generation metadata
- AC6: Implement error handling for generation failures with appropriate HTTP status codes
- AC7: Add logging for generation requests and performance metrics

### Story 2.1.2 Frontend ICF Generation Interface

As a clinical trial administrator,
I want to see all ICF sections generated simultaneously with real-time streaming,
so that I can immediately begin reviewing content as it becomes available.

#### Acceptance Criteria

- AC1: Replace "not yet implemented" alert in InformedConsentPage with actual generation interface
- AC2: Display seven section containers in fixed order with clear section titles
- AC3: Implement streaming content display that populates text boxes as content is generated
- AC4: Show loading indicators during content generation for each section
- AC5: Provide visual status indicators (generating, ready for review, approved, locked)
- AC6: Maintain responsive design that works on desktop and tablet devices
- AC7: Handle generation errors gracefully with retry options
- AC8: Implement "Approve All" button for bulk section approval

### Story 2.1.3 Section Review and Revision Workflow

As a clinical trial administrator,
I want to review, edit, and approve each ICF section individually,
so that I can ensure regulatory compliance while maintaining efficient workflow.

#### Acceptance Criteria

- AC1: Enable section selection for focused review with clear visual indication of active section
- AC2: Implement three action modes per section: approve as-is, direct edit, LLM regeneration
- AC3: Provide text prompt field for LLM revision instructions with clear submission process
- AC4: Enable direct text editing with inline editing capabilities
- AC5: Implement section approval with locking mechanism that prevents accidental changes
- AC6: Auto-unlock sections when users attempt to edit approved content
- AC7: Track approval status across all sections with visual progress indicators
- AC8: Validate that all sections are approved before enabling document finalization
- AC9: Implement undo/redo functionality for editing actions

### Story 2.1.4 Document Preview and PDF Generation

As a clinical trial administrator,
I want to preview the complete ICF document and generate a professional PDF,
so that I can review the final document before use in clinical trials.

#### Acceptance Criteria

- AC1: Create document preview screen showing complete ICF with all approved sections
- AC2: Implement "Continue Revisions" option that returns to section review interface
- AC3: Add "Download PDF" functionality that triggers LaTeX-based PDF generation
- AC4: Generate professionally formatted PDF documents with consistent styling
- AC5: Include proper document structure with headers, sections, and page formatting
- AC6: Provide download confirmation and clear success/failure feedback
- AC7: Implement PDF generation error handling with retry capabilities
- AC8: Add metadata to generated PDFs (generation date, protocol information)

## Epic 2.2 Site Initiation Checklist Generation

This epic extends the document generation capabilities to Site Initiation Checklists, leveraging the established workflow patterns and infrastructure from ICF generation while addressing the unique requirements of checklist-format documents.

### Story 2.2.1 Backend Site Checklist Generation Service

As a clinical trial administrator,
I want the system to generate Site Initiation Checklists from protocol data,
so that I can create comprehensive site preparation documents for clinical trial sites.

#### Acceptance Criteria

- AC1: Create API endpoint `/api/generate-site-checklist` accepting protocol ID
- AC2: Implement checklist section generation for: regulatory, training, equipment, documentation, preparation, timeline
- AC3: Generate checklist-format content with actionable items and clear completion criteria
- AC4: Integrate protocol-specific requirements into checklist items
- AC5: Return structured JSON with checklist sections and individual checklist items
- AC6: Implement error handling consistent with ICF generation endpoints
- AC7: Add performance logging and monitoring for checklist generation

### Story 2.2.2 Frontend Site Checklist Interface

As a clinical trial administrator,
I want to generate and review Site Initiation Checklists using the same workflow as ICF documents,
so that I can efficiently create site preparation materials.

#### Acceptance Criteria

- AC1: Replace "not yet implemented" alert in SiteChecklistPage with generation interface
- AC2: Adapt section-based interface for checklist format with appropriate visual styling
- AC3: Display checklist sections in logical order with clear section identification
- AC4: Implement streaming generation for checklist content with progress indicators
- AC5: Provide same review workflow (approve, edit, regenerate) as ICF generation
- AC6: Adapt bulk approval functionality for checklist-specific requirements
- AC7: Maintain consistent UI patterns with ICF generation interface
- AC8: Generate PDF checklists with checkbox formatting and professional layout

## Epic 2.3 Document Export and Management

This epic enhances the document generation system with advanced export capabilities and basic document management features, preparing the foundation for future enterprise features.

### Story 2.3.1 Enhanced PDF Generation

As a clinical trial administrator,
I want access to advanced PDF formatting options and metadata,
so that I can generate documents that meet specific organizational requirements.

#### Acceptance Criteria

- AC1: Implement LaTeX templating system for consistent PDF formatting
- AC2: Add document metadata including protocol information, generation date, and version
- AC3: Include organizational branding and header/footer customization options
- AC4: Generate table of contents for multi-section documents
- AC5: Implement page numbering and professional document layout
- AC6: Add watermarking options for draft vs. final document status
- AC7: Optimize PDF generation performance for large documents

### Story 2.3.2 Generation History and Tracking

As a clinical trial administrator,
I want to track document generation history and access previously generated documents,
so that I can maintain audit trails and avoid duplicate work.

#### Acceptance Criteria

- AC1: Store generation history with timestamps and user identification
- AC2: Implement basic document versioning for regenerated content
- AC3: Provide access to recently generated documents through simple listing interface
- AC4: Add download links for previously generated PDFs
- AC5: Implement automatic cleanup of old generation data after defined retention period
- AC6: Track generation metrics for system performance monitoring
- AC7: Provide basic audit trail for regulatory compliance needs

## Change Log

| Change | Date | Version | Description | Author |
| ------ | ---- | ------- | ----------- | ------ |
| Initial | 2025-06-19 | 1.0 | Initial PRD creation for Epic 2 AI Document Generation | John (PM) |

----- END PRD START CHECKLIST OUTPUT ------

## Checklist Results Report

### Category Statuses

| Category | Status | Critical Issues |
|----------|--------|----------------|
| 1. Problem Definition & Context | **PASS** | None |
| 2. MVP Scope Definition | **PASS** | None |
| 3. User Experience Requirements | **PASS** | None |
| 4. Functional Requirements | **PASS** | None |
| 5. Non-Functional Requirements | **PASS** | None |
| 6. Epic & Story Structure | **PASS** | None |
| 7. Technical Guidance | **PASS** | None |
| 8. Cross-Functional Requirements | **PASS** | None |
| 9. Clarity & Communication | **PASS** | None |

### Validation Details

**Strengths Identified:**
- ✅ **Clear Problem Definition**: Regulatory compliance requirements and human-in-the-loop necessity well articulated
- ✅ **Focused MVP Scope**: ICF generation as primary feature with Site Checklists as secondary is appropriately scoped
- ✅ **Detailed User Experience**: Section-by-section workflow with streaming, review, and approval clearly defined
- ✅ **Comprehensive Functional Requirements**: All 10 functional requirements are testable and user-focused
- ✅ **Strong Non-Functional Requirements**: Performance, privacy, and regulatory considerations thoroughly addressed
- ✅ **Well-Structured Epics**: Sequential epics with clear value delivery and appropriate story sizing
- ✅ **Technical Integration**: Builds naturally on Epic 1 foundation with existing Qdrant/API infrastructure
- ✅ **Implementation Ready**: Stories include specific acceptance criteria sized for single agent execution

### Final Decision

**✅ READY FOR ARCHITECT**: The PRD and epics are comprehensive, properly structured, and ready for architectural design. The document provides clear technical guidance, implementation-ready stories, and maintains focus on regulatory compliance requirements essential for clinical trial environments.

----- END Checklist START Design Architect `UI/UX Specification Mode` Prompt ------

## Design Architect Prompt

Create detailed UI/UX specifications for the Informed Consent Form generation interface, focusing on the section-based review workflow, streaming content display, and human-in-the-loop approval process as defined in this PRD.

----- END Design Architect `UI/UX Specification Mode` Prompt START Architect Prompt ------

## Architect Prompt

Design the technical architecture for AI document generation services, including streaming content delivery, LaTeX PDF generation, and integration with existing Qdrant vector database infrastructure as specified in this PRD.

----- END Architect Prompt ------