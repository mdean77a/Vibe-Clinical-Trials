# Vibe Clinical Trials - Epic 2 Frontend Architecture Document

## Table of Contents

- [Introduction](#introduction)
- [Overall Frontend Philosophy & Patterns](#overall-frontend-philosophy--patterns)
- [Detailed Frontend Directory Structure](#detailed-frontend-directory-structure)
- [Component Breakdown & Implementation Details](#component-breakdown--implementation-details)
- [State Management In-Depth](#state-management-in-depth)
- [API Interaction Layer](#api-interaction-layer)
- [Routing Strategy](#routing-strategy)
- [Build, Bundling, and Deployment](#build-bundling-and-deployment)
- [Frontend Testing Strategy](#frontend-testing-strategy)
- [Accessibility (AX) Implementation Details](#accessibility-ax-implementation-details)
- [Performance Considerations](#performance-considerations)
- [Frontend Security Considerations](#frontend-security-considerations)
- [Browser Support and Progressive Enhancement](#browser-support-and-progressive-enhancement)
- [Change Log](#change-log)

## Introduction

This document details the technical architecture for the Epic 2 AI Document Generation frontend extensions to the Vibe Clinical Trials application. It builds upon the existing React/TypeScript/Vite foundation established in Epic 1 while adding **LangGraph-powered AI generation with human-in-the-loop interrupt workflows**.

**CRITICAL PRESERVATION PRINCIPLE:** All existing pages (HomePage, DocumentTypeSelection, InformedConsentPage, SiteChecklistPage) remain unchanged in their current working state. Epic 2 adds new components and functionality without modifying existing successful implementations.

**LangGraph Architecture:** The backend uses LangGraph with parallel agent nodes for each ICF section. Each section node is a subgraph that generates content, presents it to humans via interrupts, and waits for approval/feedback before continuing. The frontend serves as a **LangGraph dashboard and human interaction interface**.

- **Link to Main Architecture Document:** `docs/architecture.md`
- **Link to UI/UX Specification:** `docs/epic-2-frontend-spec.md`
- **Link to Epic 2 PRD:** `docs/epic-2-prd.md`

## Overall Frontend Philosophy & Patterns

### Framework & Core Libraries
- **React 18.x** with **TypeScript** and **Vite** (existing foundation)
- **Tailwind CSS** for styling (existing implementation)
- **React Router** for client-side routing (existing implementation)

### Component Architecture
- **Atomic Design Principles** with existing successful component hierarchy preserved
- **New Epic 2 Components:** Specialized for streaming AI content and human-in-the-loop workflows
- **Existing Components:** HomePage, ProtocolUpload, DocumentTypeSelection remain untouched

### State Management Strategy
- **React Context + useState** for new Epic 2 features (matching existing pattern)
- **localStorage** for session persistence (existing pattern)
- **No global state management library** (maintaining current simplicity)

### Data Flow
- **LangGraph State Synchronization** - Frontend displays current AgentState from LangGraph execution
- **Human Interrupt Handling** - Frontend responds to LangGraph interrupts and provides resume mechanisms
- **RESTful API calls** for LangGraph execution control (start, resume, provide feedback)

### Styling Approach
- **Tailwind CSS** utility-first approach (existing)
- **Component-scoped styles** for complex Epic 2 interactions
- **Consistent design system** extending existing clinical aesthetic

### Key Design Patterns
- **Provider Pattern** for Epic 2 generation context
- **Custom Hooks** for streaming content management
- **Compound Components** for section-based review interface
- **Progressive Enhancement** for accessibility

## Detailed Frontend Directory Structure

```plaintext
frontend/src/
├── components/                    # Existing reusable components (PRESERVED)
│   ├── Button.tsx                # Existing button component
│   ├── Card.tsx                  # Existing card component
│   ├── ProtocolUpload.tsx        # Existing upload component (PRESERVED)
│   └── epic2/                    # NEW: Epic 2 LangGraph interface components
│       ├── LangGraphStateDisplay.tsx # Shows current AgentState content
│       ├── SectionInterruptHandler.tsx # Handles human interrupts per section
│       ├── HumanActionPanel.tsx  # Approve/reject/feedback actions for interrupts
│       ├── ExecutionProgress.tsx # Tracks LangGraph execution progress
│       ├── DocumentPreview.tsx   # Full document preview from final state
│       └── LangGraphController.tsx # Start/stop/resume LangGraph execution
├── pages/                        # Existing page components (PRESERVED)
│   ├── HomePage.tsx              # Existing homepage (PRESERVED)
│   ├── DocumentTypeSelection.tsx # Existing selection page (PRESERVED)
│   ├── InformedConsentPage.tsx   # MODIFIED: Replace alert with generation interface
│   └── SiteChecklistPage.tsx     # MODIFIED: Replace alert with generation interface
├── hooks/                        # Custom React hooks
│   ├── epic2/                    # NEW: Epic 2 LangGraph hooks
│   │   ├── useLangGraphExecution.ts # Manage LangGraph execution lifecycle
│   │   ├── useLangGraphState.ts  # Subscribe to AgentState updates
│   │   ├── useHumanInterrupts.ts # Handle interrupt notifications and responses
│   │   └── useSectionStatus.ts   # Track individual section states
├── services/                     # API service layer (EXTENDED)
│   ├── api.ts                    # Existing API utilities (PRESERVED)
│   └── epic2/                    # NEW: Epic 2 LangGraph API services
│       ├── langGraphService.ts   # LangGraph execution control (start/stop/resume)
│       ├── stateService.ts       # AgentState polling and updates
│       ├── interruptService.ts   # Human interrupt handling
│       └── pdfService.ts         # LaTeX PDF generation from final state
├── utils/                        # Utility functions (EXTENDED)
│   ├── api.ts                    # Existing API utilities (PRESERVED)
│   └── epic2/                    # NEW: Epic 2 LangGraph utilities
│       ├── agentStateHelpers.ts  # AgentState parsing and validation
│       ├── interruptHelpers.ts   # Human interrupt response formatting
│       └── documentFormatting.ts # Document assembly from AgentState
├── types/                        # TypeScript definitions (EXTENDED)
│   ├── index.ts                  # Existing types (PRESERVED)
│   └── epic2.ts                  # NEW: Epic 2 LangGraph types (AgentState, interrupts, etc.)
└── __tests__/                    # Test files (EXTENDED)
    ├── components/               # Existing component tests (PRESERVED)
    └── epic2/                    # NEW: Epic 2 component tests
```

### Notes on Frontend Structure

**Preservation Strategy:** All existing directories and files in `components/`, `pages/`, `utils/`, and `types/` remain unchanged. Epic 2 functionality is added through:
- New `epic2/` subdirectories for LangGraph interface functionality
- Minimal modifications to existing pages (only replacing alert calls with LangGraph controllers)
- Extension of existing services with new LangGraph API integration modules

**AI Agent Implementation Rules:**
- MUST NOT modify existing components unless explicitly noted
- MUST place all new Epic 2 code in designated `epic2/` directories
- MUST follow existing naming conventions and patterns
- MUST use existing Tailwind classes and design system
- MUST design components as **LangGraph state viewers and interrupt handlers**, not independent state managers

## Component Breakdown & Implementation Details

### Component Naming & Organization
- **Component Naming Convention:** PascalCase for files and components (existing pattern)
- **Organization:** Epic 2 LangGraph components in `src/components/epic2/` namespace
- **Integration:** Epic 2 components imported into existing pages without modifying page structure

### Template for Component Specification

#### Component: `LangGraphStateDisplay`

- **Purpose:** Displays current AgentState from LangGraph execution as a dashboard of all ICF sections
- **Source File(s):** `src/components/epic2/LangGraphStateDisplay.tsx`
- **Visual Reference:** Epic 2 UI/UX Specification - Section Container Design
- **Props (Properties):**
  | Prop Name | Type | Required? | Default Value | Description |
  |:----------|:-----|:----------|:--------------|:------------|
  | `agentState` | `AgentState` | Yes | N/A | Current LangGraph AgentState with all section content |
  | `executionId` | `string` | Yes | N/A | LangGraph execution ID for tracking |
  | `onSectionSelect` | `(sectionId: string) => void` | Yes | N/A | Callback when user selects a section |
  | `selectedSectionId` | `string \| null` | No | `null` | Currently selected section for review |

- **AgentState Interface:**
  ```typescript
  interface AgentState {
    messages: Array<any>;
    summary: string;
    background: string;
    number_of_participants: string;
    study_procedures: string;
    alt_procedures: string;
    risks: string;
    benefits: string;
    // Potential status fields
    summary_status?: 'pending' | 'generating' | 'waiting_human' | 'approved';
    background_status?: 'pending' | 'generating' | 'waiting_human' | 'approved';
    // ... other status fields
  }
  ```

- **Key UI Elements / Structure:**
  ```html
  <div className="langgraph-state-display grid grid-cols-1 gap-4">
    {sections.map(section => (
      <div key={section.id} 
           className={`section-card border-2 rounded-lg p-4 transition-all cursor-pointer
                      ${selectedSectionId === section.id ? 'border-blue-500 bg-blue-50' : 'border-gray-200'}`}
           onClick={() => onSectionSelect(section.id)}>
        <div className="section-header flex items-center justify-between mb-3">
          <h3 className="text-lg font-semibold">{section.title}</h3>
          <SectionStatusBadge status={section.status} />
        </div>
        <div className="content-preview">
          <p className="text-gray-700 text-sm">
            {agentState[section.key] || 'Waiting to start...'}
          </p>
        </div>
      </div>
    ))}
  </div>
  ```

- **Events Handled / Emitted:**
  - **Handles:** Section card clicks for selection
  - **Emits:** `onSectionSelect(sectionId)`

- **Actions Triggered:**
  - **State Management:** None - displays LangGraph state only
  - **API Calls:** None - pure display component

- **Styling Notes:**
  - Grid layout for section cards
  - Visual selection states with border/background changes
  - Status badges with color coding for LangGraph node states
  - Content preview with text truncation for long content

---

#### Component: `SectionInterruptHandler`

- **Purpose:** Handles human interrupts for individual ICF sections when LangGraph pauses for human review
- **Source File(s):** `src/components/epic2/SectionInterruptHandler.tsx`
- **Visual Reference:** Epic 2 UI/UX Specification - Section Review Interface
- **Props (Properties):**
  | Prop Name | Type | Required? | Default Value | Description |
  |:----------|:-----|:----------|:--------------|:------------|
  | `sectionId` | `string` | Yes | N/A | ID of the section awaiting human review |
  | `sectionTitle` | `string` | Yes | N/A | Display title of the section |
  | `content` | `string` | Yes | N/A | Generated content awaiting approval |
  | `onApprove` | `() => void` | Yes | N/A | Approve content and resume LangGraph |
  | `onReject` | `(feedback: string) => void` | Yes | N/A | Reject with feedback and regenerate |
  | `isLoading` | `boolean` | No | `false` | Whether LangGraph is processing response |

- **Internal State:**
  | State Variable | Type | Initial Value | Description |
  |:---------------|:-----|:--------------|:------------|
  | `feedback` | `string` | `''` | User feedback for regeneration |
  | `showFeedbackPanel` | `boolean` | `false` | Whether feedback input is visible |

- **Key UI Elements / Structure:**
  ```html
  <div className="interrupt-handler bg-yellow-50 border-l-4 border-yellow-400 p-4 rounded">
    <div className="interrupt-header mb-4">
      <h4 className="text-lg font-semibold text-yellow-800">
        Review Required: {sectionTitle}
      </h4>
      <p className="text-sm text-yellow-700">LangGraph is waiting for your approval</p>
    </div>
    
    <div className="content-review mb-4">
      <div className="content-box bg-white border rounded p-3 max-h-40 overflow-y-auto">
        {content}
      </div>
    </div>
    
    <div className="action-buttons flex gap-3">
      <button 
        onClick={onApprove}
        disabled={isLoading}
        className="approve-btn bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded">
        ✓ Approve & Continue
      </button>
      <button 
        onClick={() => setShowFeedbackPanel(!showFeedbackPanel)}
        disabled={isLoading}
        className="feedback-btn bg-orange-600 hover:bg-orange-700 text-white px-4 py-2 rounded">
        ✏️ Provide Feedback
      </button>
    </div>
    
    {showFeedbackPanel && (
      <div className="feedback-panel mt-4 p-3 bg-white border rounded">
        <textarea 
          value={feedback}
          onChange={(e) => setFeedback(e.target.value)}
          placeholder="Provide specific feedback for regeneration..."
          className="w-full h-24 p-2 border rounded resize-none"
        />
        <button 
          onClick={() => onReject(feedback)}
          disabled={!feedback.trim() || isLoading}
          className="submit-feedback bg-red-600 hover:bg-red-700 text-white px-3 py-1 rounded mt-2">
          Submit Feedback & Regenerate
        </button>
      </div>
    )}
  </div>
  ```

- **Events Handled / Emitted:**
  - **Handles:** Approve/reject actions, feedback input
  - **Emits:** `onApprove()`, `onReject(feedback)`

- **Actions Triggered:**
  - **LangGraph Resume:** Calls LangGraph API to resume execution with human response
  - **State Updates:** Updates interrupt state to show processing

---

#### Component: `ExecutionProgress`

- **Purpose:** Tracks overall LangGraph execution progress across all agent nodes
- **Source File(s):** `src/components/epic2/ExecutionProgress.tsx`
- **Visual Reference:** Epic 2 UI/UX Specification - Progress Tracker
- **Props (Properties):**
  | Prop Name | Type | Required? | Default Value | Description |
  |:----------|:-----|:----------|:--------------|:------------|
  | `executionId` | `string` | Yes | N/A | LangGraph execution ID |
  | `nodeStatuses` | `Record<string, NodeStatus>` | Yes | N/A | Status of each LangGraph node |
  | `overallStatus` | `'running' \| 'waiting' \| 'completed' \| 'error'` | Yes | N/A | Overall execution status |

- **NodeStatus Interface:**
  ```typescript
  interface NodeStatus {
    id: string;
    name: string;
    status: 'pending' | 'running' | 'waiting_human' | 'completed' | 'error';
    startTime?: string;
    endTime?: string;
  }
  ```

- **Key UI Elements / Structure:**
  ```html
  <div className="execution-progress bg-gray-50 border rounded-lg p-4">
    <div className="progress-header mb-4">
      <h3 className="text-lg font-semibold">LangGraph Execution Progress</h3>
      <div className="execution-id text-xs text-gray-500">ID: {executionId}</div>
    </div>
    
    <div className="nodes-status grid grid-cols-2 md:grid-cols-4 gap-3">
      {Object.values(nodeStatuses).map(node => (
        <div key={node.id} className="node-status-card bg-white border rounded p-3">
          <div className="node-name text-sm font-medium">{node.name}</div>
          <div className={`status-indicator flex items-center mt-1 text-xs
                         ${getStatusColor(node.status)}`}>
            <StatusIcon status={node.status} />
            {getStatusText(node.status)}
          </div>
        </div>
      ))}
    </div>
    
    <div className="overall-status mt-4 p-3 bg-white border rounded">
      <div className="flex items-center justify-between">
        <span className="font-medium">Overall Status:</span>
        <span className={`px-2 py-1 rounded text-sm ${getOverallStatusColor(overallStatus)}`}>
          {overallStatus.toUpperCase()}
        </span>
      </div>
    </div>
  </div>
  ```

## State Management In-Depth

### Chosen Solution
**LangGraph State Synchronization** - Frontend displays and responds to LangGraph AgentState rather than managing independent state

### Decision Guide for State Location
- **LangGraph AgentState:** Primary source of truth for all ICF content and generation status
- **React Context:** Lightweight coordination of UI state (selected sections, interrupt handling)
- **Local Component State:** UI interactions only (form inputs, panel visibility)
- **No Persistent Storage:** LangGraph maintains execution state; frontend is stateless view layer

### Epic 2 LangGraph Integration

#### LangGraphContext

```typescript
interface LangGraphContextState {
  executionId: string | null;
  agentState: AgentState | null;
  executionStatus: 'idle' | 'running' | 'waiting_human' | 'completed' | 'error';
  interrupts: HumanInterrupt[];
  selectedSectionId: string | null;
  error: string | null;
}

interface AgentState {
  messages: Array<any>;
  summary: string;
  background: string;
  number_of_participants: string;
  study_procedures: string;
  alt_procedures: string;
  risks: string;
  benefits: string;
  // Status tracking (if implemented in LangGraph)
  summary_status?: SectionStatus;
  background_status?: SectionStatus;
  number_of_participants_status?: SectionStatus;
  study_procedures_status?: SectionStatus;
  alt_procedures_status?: SectionStatus;
  risks_status?: SectionStatus;
  benefits_status?: SectionStatus;
}

interface HumanInterrupt {
  id: string;
  sectionId: string;
  nodeId: string;
  content: string;
  timestamp: string;
  status: 'pending' | 'responded';
}

type SectionStatus = 'pending' | 'running' | 'waiting_human' | 'approved' | 'error';
```

**Location:** `src/hooks/epic2/useLangGraphExecution.ts`

**Key Actions:**
- `startExecution(protocolId: string)` - Initialize LangGraph ICF generation
- `resumeExecution(interruptId: string, response: HumanResponse)` - Respond to human interrupts
- `pollAgentState()` - Fetch current LangGraph state
- `selectSection(sectionId: string)` - UI-only section selection
- `cancelExecution()` - Stop LangGraph execution

**Human Response Types:**
```typescript
interface HumanResponse {
  action: 'approve' | 'reject';
  feedback?: string; // Required for reject actions
  sectionId: string;
}
```

## API Interaction Layer

### Client/Service Structure

**HTTP Client Setup:** Extending existing `src/utils/api.ts` with LangGraph integration

#### LangGraph Service: `langGraphService.ts`

```typescript
// src/services/epic2/langGraphService.ts
export interface StartExecutionRequest {
  protocolId: string;
  documentType: 'icf' | 'site_checklist';
}

export interface ExecutionResponse {
  executionId: string;
  status: 'started' | 'error';
  message?: string;
}

export interface AgentStateResponse {
  executionId: string;
  agentState: AgentState;
  executionStatus: 'running' | 'waiting_human' | 'completed' | 'error';
  interrupts: HumanInterrupt[];
}

export class LangGraphService {
  // Start LangGraph execution for ICF generation
  async startExecution(request: StartExecutionRequest): Promise<ExecutionResponse>;
  
  // Get current AgentState and execution status
  async getExecutionState(executionId: string): Promise<AgentStateResponse>;
  
  // Respond to human interrupt and resume execution
  async resumeExecution(
    executionId: string, 
    interruptId: string, 
    response: HumanResponse
  ): Promise<{ status: 'resumed' | 'error'; message?: string }>;
  
  // Cancel running execution
  async cancelExecution(executionId: string): Promise<{ status: 'cancelled' | 'error' }>;
  
  // Get execution history/logs (optional)
  async getExecutionLogs(executionId: string): Promise<ExecutionLog[]>;
}
```

#### State Polling Service: `stateService.ts`

```typescript
// src/services/epic2/stateService.ts
export class StateService {
  // Poll AgentState with configurable interval
  startPolling(
    executionId: string, 
    onUpdate: (state: AgentStateResponse) => void,
    intervalMs: number = 2000
  ): () => void; // Returns cleanup function
  
  // Single state fetch
  async fetchState(executionId: string): Promise<AgentStateResponse>;
  
  // Check for new interrupts
  async checkInterrupts(executionId: string): Promise<HumanInterrupt[]>;
}
```

#### Interrupt Handling Service: `interruptService.ts`

```typescript
// src/services/epic2/interruptService.ts
export interface InterruptResponse {
  interruptId: string;
  action: 'approve' | 'reject';
  feedback?: string;
  timestamp: string;
}

export class InterruptService {
  // Respond to human interrupt
  async respondToInterrupt(
    executionId: string,
    interruptId: string,
    response: InterruptResponse
  ): Promise<{ status: 'success' | 'error'; message?: string }>;
  
  // Get pending interrupts for execution
  async getPendingInterrupts(executionId: string): Promise<HumanInterrupt[]>;
  
  // Mark interrupt as seen (UI feedback)
  async acknowledgeInterrupt(interruptId: string): Promise<void>;
}
```

### Error Handling & Retries
- **LangGraph Execution Errors:** Detailed error messages with restart options
- **State Polling Failures:** Exponential backoff with connection retry
- **Interrupt Response Errors:** User notification with retry mechanism
- **Network Timeouts:** Graceful degradation with offline state indication

## Routing Strategy

### Routing Library
**React Router** (existing implementation preserved)

### Route Definitions

| Path Pattern | Component/Page | Protection | Notes |
|:-------------|:---------------|:-----------|:------|
| `/` | `HomePage.tsx` | Public | PRESERVED - no changes |
| `/document-selection` | `DocumentTypeSelection.tsx` | Public | PRESERVED - no changes |
| `/informed-consent` | `InformedConsentPage.tsx` | Public | MODIFIED - replace alert with generation interface |
| `/site-checklist` | `SiteChecklistPage.tsx` | Public | MODIFIED - replace alert with generation interface |

**No new routes required** - Epic 2 functionality integrates into existing page structure

## Build, Bundling, and Deployment

### Build Process & Scripts
**Preserved from existing:** Vite build system with TypeScript and Tailwind CSS

**New Build Considerations:**
- **Server-Sent Events:** Ensure Vite dev server supports SSE proxy
- **PDF Generation:** Bundle size optimization for PDF.js dependencies
- **Streaming Components:** Code splitting for Epic 2 components

### Environment Configuration
**Extended existing:** Environment variables for Epic 2 endpoints

```env
# Existing (preserved)
VITE_API_URL=http://localhost:8000

# New for Epic 2
VITE_STREAMING_ENDPOINT=http://localhost:8000/api/stream
VITE_PDF_GENERATION_ENDPOINT=http://localhost:8000/api/generate-pdf
```

## Frontend Testing Strategy

### Component Testing
**Extended existing Jest + React Testing Library setup**

**Epic 2 Component Tests:**
- `StreamingTextBox.test.tsx` - Content streaming simulation
- `ActionPanel.test.tsx` - User interactions and state management
- `ProgressTracker.test.tsx` - Progress calculations and navigation

### Feature/Flow Testing
**New Epic 2 Integration Tests:**
- Complete ICF generation workflow
- Section approval and regeneration flows
- PDF generation and download

### End-to-End UI Testing
**Extended existing E2E to include:**
- Protocol upload → ICF generation → PDF download workflow
- Bulk approval operations
- Error handling and recovery scenarios

## Accessibility (AX) Implementation Details

### Semantic HTML
- All Epic 2 components use semantic HTML5 elements
- `<section>` for ICF sections, `<button>` for actions, `<progress>` for tracking

### ARIA Implementation
- **StreamingTextBox:** `aria-live="polite"` for content updates
- **ActionPanel:** `aria-expanded` for instruction panels
- **ProgressTracker:** `role="progressbar"` with `aria-valuenow`

### Keyboard Navigation
- Tab order: Section selection → Action buttons → Progress tracker
- Enter/Space activation for all interactive elements
- Escape to cancel instruction panels

### Focus Management
- Focus returns to selected section after actions
- Clear focus indicators for all Epic 2 components
- Screen reader announcements for status changes

## Performance Considerations

### LangGraph State Optimization
- **Polling Efficiency:** Configurable polling intervals with backoff when no changes detected
- **Component Memoization:** `React.memo` for components displaying static AgentState content
- **State Diffing:** Only re-render components when relevant AgentState fields change

### Memory Management
- **Polling Cleanup:** Proper cleanup of polling intervals on component unmount
- **State Caching:** Minimal client-side caching of AgentState for UI responsiveness
- **PDF Generation:** Stream large PDFs directly from LangGraph execution results

### Code Splitting
- **Epic 2 Components:** Lazy load LangGraph interface components
- **PDF Library:** Dynamic import for PDF.js when needed
- **Polling Service:** Separate bundle for state management utilities

## Frontend Security Considerations

### Content Security Policy
- **LangGraph API Endpoints:** Whitelist LangGraph backend URLs in CSP
- **PDF Generation:** Secure PDF blob handling and download

### Input Validation
- **Human Feedback:** Client-side sanitization for feedback text (server validation primary)
- **AgentState Display:** XSS prevention for LangGraph-generated content
- **File Downloads:** Validate PDF blob integrity from LangGraph results

### LangGraph Security
- **API Authentication:** Include auth tokens in LangGraph API requests
- **Execution Isolation:** Validate execution IDs to prevent cross-user access
- **State Validation:** Verify AgentState structure and content before display

## Browser Support and Progressive Enhancement

### Target Browsers
**Extended existing:** Latest 2 versions of Chrome, Firefox, Safari, Edge

### SSE Support
- **EventSource Polyfill:** For older browsers lacking SSE support
- **Fallback Strategy:** Polling for browsers without SSE capability

### Progressive Enhancement
- **Core Functionality:** Document generation works without advanced features
- **Enhanced Experience:** Streaming provides real-time feedback but not required
- **Graceful Degradation:** Fall back to request/response for generation if SSE fails

## Change Log

| Change | Date | Version | Description | Author |
| ------ | ---- | ------- | ----------- | ------ |
| Initial | 2025-06-19 | 1.0 | Epic 2 frontend architecture extending existing React/Vite application | Jane (Design Architect) |