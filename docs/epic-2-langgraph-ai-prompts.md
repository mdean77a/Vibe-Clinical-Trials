# Epic 2 LangGraph AI Frontend Development Prompts (Draft)

## Overview

These are draft prompts for AI agents to implement Epic 2 LangGraph-powered frontend components. Each prompt includes LangGraph integration specifications, human interrupt handling, and AgentState synchronization.

**LangGraph Architecture Context:**
- Backend uses LangGraph with parallel agent nodes for each ICF section
- Each section node is a subgraph: Agent → Human Interrupt → Resume/Regenerate
- Frontend serves as **LangGraph dashboard and human interaction interface**
- AgentState is the single source of truth for all content

**Usage Notes:**
- These are initial drafts for experimentation
- Prompts will be refined based on actual AI responses and LangGraph API contracts
- Each prompt is designed for focused, single-component implementation
- Assumes AI agent has access to existing codebase context

---

## Prompt 1: LangGraphStateDisplay Component

**Task:** Implement the LangGraphStateDisplay component to visualize current AgentState from LangGraph execution.

**Context:** You are implementing a React TypeScript component for the Vibe Clinical Trials application. This component displays the current state of LangGraph ICF generation, showing all 7 sections and their content as a dashboard.

**LangGraph Integration:**
- **AgentState Structure:** Based on provided TypeScript interface with section content fields
- **Real-time Updates:** Component receives new AgentState via props when parent polls LangGraph API
- **No Local State Management:** Component is pure display layer for LangGraph state

**Requirements:**
- **Component Location:** `src/components/epic2/LangGraphStateDisplay.tsx`
- **Framework:** React 18 with TypeScript, using Tailwind CSS for styling
- **Purpose:** Dashboard view of all ICF sections from LangGraph AgentState

**Component Specification:**
```typescript
interface LangGraphStateDisplayProps {
  agentState: AgentState | null;
  executionId: string | null;
  onSectionSelect: (sectionId: string) => void;
  selectedSectionId: string | null;
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
  // Optional status fields from LangGraph
  summary_status?: 'pending' | 'running' | 'waiting_human' | 'approved';
  background_status?: 'pending' | 'running' | 'waiting_human' | 'approved';
  // ... other status fields
}
```

**Implementation Requirements:**
1. **Section Mapping:** Map AgentState fields to ICF sections with display titles
2. **Visual States:** Show different visual states based on status fields (if available)
3. **Content Display:** Show current content from AgentState or placeholder text
4. **Selection Handling:** Allow section selection for interrupt handling

**Section Configuration:**
```typescript
const ICF_SECTIONS = [
  { id: 'summary', title: 'Summary', agentStateKey: 'summary', statusKey: 'summary_status' },
  { id: 'background', title: 'Background', agentStateKey: 'background', statusKey: 'background_status' },
  { id: 'participants', title: 'Number of Participants', agentStateKey: 'number_of_participants', statusKey: 'number_of_participants_status' },
  { id: 'procedures', title: 'Study Procedures', agentStateKey: 'study_procedures', statusKey: 'study_procedures_status' },
  { id: 'alternatives', title: 'Alternative Procedures', agentStateKey: 'alt_procedures', statusKey: 'alt_procedures_status' },
  { id: 'risks', title: 'Risks', agentStateKey: 'risks', statusKey: 'risks_status' },
  { id: 'benefits', title: 'Benefits', agentStateKey: 'benefits', statusKey: 'benefits_status' }
];
```

**Styling Guidelines:**
- Grid layout: `grid grid-cols-1 gap-4` for section cards
- Section cards: `border-2 rounded-lg p-4 transition-all cursor-pointer`
- Selection state: `border-blue-500 bg-blue-50`
- Default state: `border-gray-200 hover:border-gray-300`
- Status indicators with color coding

**Accessibility:**
- `aria-label` for each section card
- Keyboard navigation support
- Clear visual hierarchy
- Screen reader support for status changes

**Expected Output:** Complete React component that displays AgentState as interactive section dashboard.

---

## Prompt 2: SectionInterruptHandler Component

**Task:** Implement the SectionInterruptHandler component for responding to LangGraph human interrupts.

**Context:** You are implementing a React TypeScript component that handles human interrupts from LangGraph. When LangGraph pauses for human review, this component provides approve/reject interface and sends responses back to LangGraph.

**LangGraph Integration:**
- **Human Interrupts:** LangGraph sends interrupt notifications when sections need human review
- **Response Mechanism:** Component sends approve/reject responses via LangGraph API
- **State Synchronization:** After response, LangGraph resumes execution and updates AgentState

**Requirements:**
- **Component Location:** `src/components/epic2/SectionInterruptHandler.tsx`
- **Framework:** React 18 with TypeScript, Tailwind CSS
- **Purpose:** Handle human interrupts with approve/reject actions

**Component Specification:**
```typescript
interface SectionInterruptHandlerProps {
  interrupt: HumanInterrupt;
  onApprove: (interruptId: string) => Promise<void>;
  onReject: (interruptId: string, feedback: string) => Promise<void>;
  isLoading?: boolean;
}

interface HumanInterrupt {
  id: string;
  sectionId: string;
  nodeId: string;
  content: string;
  timestamp: string;
  status: 'pending' | 'responded';
}
```

**Implementation Requirements:**
1. **Interrupt Display:** Show generated content awaiting human review
2. **Action Interface:** Provide approve and reject (with feedback) options
3. **Feedback Collection:** Expandable textarea for rejection feedback
4. **Loading States:** Show processing state while LangGraph responds

**User Flow:**
1. **Interrupt Received:** Component displays generated content for review
2. **User Decision:** User clicks Approve or Provide Feedback
3. **Feedback Entry:** If feedback chosen, show textarea for instructions
4. **Response Submission:** Call appropriate handler (approve/reject)
5. **LangGraph Resume:** Backend resumes execution with human response

**Visual Design:**
- Yellow highlight border to indicate interrupt state
- Clear "Review Required" messaging
- Content display in scrollable container
- Action buttons with clear approve/reject distinction

**Styling Guidelines:**
- Container: `bg-yellow-50 border-l-4 border-yellow-400 p-4 rounded`
- Approve button: `bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded`
- Feedback button: `bg-orange-600 hover:bg-orange-700 text-white px-4 py-2 rounded`
- Feedback panel: `mt-4 p-3 bg-white border rounded`

**Expected Output:** Complete interrupt handling component with full LangGraph integration.

---

## Prompt 3: useLangGraphExecution Hook

**Task:** Implement the useLangGraphExecution custom hook for managing LangGraph execution lifecycle and state synchronization.

**Context:** You are implementing a React TypeScript custom hook that manages LangGraph execution, AgentState polling, and human interrupt handling for the Vibe Clinical Trials application.

**LangGraph Integration:**
- **Execution Control:** Start, stop, and monitor LangGraph executions
- **State Polling:** Regular polling of AgentState for real-time updates
- **Interrupt Management:** Handle human interrupt notifications and responses

**Requirements:**
- **Hook Location:** `src/hooks/epic2/useLangGraphExecution.ts`
- **Framework:** React 18 with TypeScript
- **Purpose:** Complete LangGraph integration layer for frontend

**Hook Interface:**
```typescript
interface LangGraphExecutionHook {
  // Execution control
  startExecution: (protocolId: string) => Promise<void>;
  cancelExecution: () => Promise<void>;
  
  // State management
  agentState: AgentState | null;
  executionId: string | null;
  executionStatus: 'idle' | 'running' | 'waiting_human' | 'completed' | 'error';
  
  // Interrupt handling
  interrupts: HumanInterrupt[];
  respondToInterrupt: (interruptId: string, response: HumanResponse) => Promise<void>;
  
  // Error handling
  error: string | null;
  isLoading: boolean;
}

interface HumanResponse {
  action: 'approve' | 'reject';
  feedback?: string;
  sectionId: string;
}
```

**Implementation Requirements:**
1. **Execution Management:**
   - Start LangGraph ICF generation execution
   - Track execution ID for subsequent API calls
   - Handle execution completion and errors

2. **State Polling:**
   - Poll LangGraph API for AgentState updates (every 2-3 seconds)
   - Implement efficient polling with backoff when no changes
   - Cleanup polling on component unmount

3. **Interrupt Handling:**
   - Detect new human interrupts from polling
   - Provide methods to respond to interrupts
   - Update interrupt status after responses

4. **Error Management:**
   - Handle API errors with user-friendly messages
   - Implement retry logic for transient failures
   - Graceful degradation for network issues

**API Integration:**
```typescript
// Expected API calls
const langGraphService = new LangGraphService();

// Start execution
const executionResponse = await langGraphService.startExecution({
  protocolId: 'protocol-123',
  documentType: 'icf'
});

// Poll for state
const stateResponse = await langGraphService.getExecutionState(executionId);

// Respond to interrupt
await langGraphService.resumeExecution(executionId, interruptId, response);
```

**Polling Strategy:**
- Start polling after successful execution start
- Use `setInterval` with cleanup on unmount
- Exponential backoff if no state changes detected
- Stop polling when execution completes or errors

**State Management:**
- Use `useState` for all hook state
- Use `useEffect` for polling lifecycle
- Use `useCallback` for memoized action functions
- Use `useRef` for polling interval references

**Expected Output:** Robust custom hook providing complete LangGraph integration with error handling and cleanup.

---

## Prompt 4: LangGraph Service Layer

**Task:** Implement the LangGraphService class for API interactions with LangGraph backend endpoints.

**Context:** You are implementing a TypeScript service class that handles all API communications with the LangGraph backend for ICF generation, state polling, and interrupt handling.

**LangGraph API Contract:**
- **Execution Endpoints:** Start, stop, resume LangGraph executions
- **State Endpoints:** Get current AgentState and execution status
- **Interrupt Endpoints:** Respond to human interrupts and get pending interrupts

**Requirements:**
- **Service Location:** `src/services/epic2/langGraphService.ts`
- **Framework:** TypeScript with existing API client patterns
- **Purpose:** Centralized LangGraph API interactions

**Service Interface:**
```typescript
class LangGraphService {
  // Execution control
  async startExecution(request: StartExecutionRequest): Promise<ExecutionResponse>;
  async cancelExecution(executionId: string): Promise<CancelResponse>;
  
  // State management
  async getExecutionState(executionId: string): Promise<AgentStateResponse>;
  
  // Interrupt handling
  async resumeExecution(
    executionId: string, 
    interruptId: string, 
    response: HumanResponse
  ): Promise<ResumeResponse>;
  
  async getPendingInterrupts(executionId: string): Promise<HumanInterrupt[]>;
}
```

**API Endpoint Specifications:**
```typescript
// POST /api/langgraph/start
interface StartExecutionRequest {
  protocolId: string;
  documentType: 'icf' | 'site_checklist';
}

interface ExecutionResponse {
  executionId: string;
  status: 'started' | 'error';
  message?: string;
}

// GET /api/langgraph/state/{executionId}
interface AgentStateResponse {
  executionId: string;
  agentState: AgentState;
  executionStatus: 'running' | 'waiting_human' | 'completed' | 'error';
  interrupts: HumanInterrupt[];
  timestamp: string;
}

// POST /api/langgraph/resume/{executionId}
interface ResumeRequest {
  interruptId: string;
  response: HumanResponse;
}

interface ResumeResponse {
  status: 'resumed' | 'error';
  message?: string;
}
```

**Implementation Requirements:**
1. **HTTP Client Integration:**
   - Use existing API client from `src/utils/api.ts`
   - Include authentication headers
   - Handle environment-specific base URLs

2. **Error Handling:**
   - Network timeout handling
   - HTTP status code handling (400, 401, 500, etc.)
   - Structured error responses with user-friendly messages

3. **Request/Response Validation:**
   - TypeScript interfaces for all API contracts
   - Runtime validation of critical response fields
   - Graceful handling of unexpected response formats

4. **Configuration:**
   - Environment-specific endpoint configuration
   - Configurable timeout values
   - Rate limiting awareness

**Error Handling Strategy:**
```typescript
try {
  const response = await this.apiClient.post('/api/langgraph/start', request);
  return response.data;
} catch (error) {
  if (error.response?.status === 400) {
    throw new Error('Invalid protocol ID or request format');
  } else if (error.response?.status === 401) {
    throw new Error('Authentication required');
  } else if (error.response?.status >= 500) {
    throw new Error('LangGraph service temporarily unavailable');
  } else {
    throw new Error('Failed to start LangGraph execution');
  }
}
```

**Expected Output:** Complete service class with full LangGraph API integration, error handling, and TypeScript types.

---

## Prompt 5: InformedConsentPage LangGraph Integration

**Task:** Modify the existing InformedConsentPage to integrate LangGraph execution interface while preserving all existing functionality.

**Context:** You are updating the existing `src/pages/InformedConsentPage.tsx` to replace the "not yet implemented" alert with a complete LangGraph-powered ICF generation interface.

**LangGraph Integration:**
- **Replace Alert:** Remove alert call, add LangGraph execution workflow
- **State Management:** Use Epic 2 LangGraph hooks for execution management
- **Component Integration:** Add LangGraph components for state display and interrupt handling

**Requirements:**
- **File Location:** `src/pages/InformedConsentPage.tsx` (MODIFY EXISTING)
- **Preservation:** Keep all existing navigation, styling, and page structure
- **Integration:** Replace only the button action with LangGraph controller

**Current Code to Replace:**
```typescript
const handleBuildForms = () => {
  alert("The consent form builder is not yet implemented.");
};
```

**New Implementation Strategy:**
1. **Import LangGraph Components:**
   - LangGraphStateDisplay, SectionInterruptHandler, ExecutionProgress
   - useLangGraphExecution hook

2. **State Management:**
   - Replace alert with LangGraph execution initialization
   - Add execution state management using Epic 2 hooks
   - Handle workflow transitions (idle → running → interrupts → completed)

3. **UI Integration:**
   - Keep existing button, change action to start LangGraph execution
   - Add conditional rendering for execution interface
   - Show interrupt handlers when human review required

**Workflow Implementation:**
```typescript
const {
  startExecution,
  agentState,
  executionId,
  executionStatus,
  interrupts,
  respondToInterrupt,
  error,
  isLoading
} = useLangGraphExecution();

const handleBuildForms = async () => {
  if (selectedProtocol?.id) {
    await startExecution(selectedProtocol.id);
  }
};

// Render logic
{executionStatus === 'running' && (
  <div className="langgraph-execution mt-8">
    <ExecutionProgress executionId={executionId} />
    <LangGraphStateDisplay 
      agentState={agentState}
      executionId={executionId}
      onSectionSelect={setSelectedSection}
    />
  </div>
)}

{interrupts.length > 0 && (
  <div className="interrupts-section mt-6">
    {interrupts.map(interrupt => (
      <SectionInterruptHandler
        key={interrupt.id}
        interrupt={interrupt}
        onApprove={(id) => respondToInterrupt(id, { action: 'approve' })}
        onReject={(id, feedback) => respondToInterrupt(id, { action: 'reject', feedback })}
      />
    ))}
  </div>
)}
```

**Preserved Elements:**
- All existing imports and dependencies
- Page header, navigation, and styling
- Protocol context and selection logic
- Button styling and placement
- Error handling patterns

**New Elements:**
- LangGraph execution state management
- Real-time AgentState display
- Human interrupt handling interface
- Execution progress tracking
- PDF generation from completed state

**Expected Output:** Modified page component with seamless LangGraph integration and preserved existing functionality.

---

## Implementation Notes

### Development Order (LangGraph-First)
1. **LangGraphService** - API integration layer
2. **useLangGraphExecution** - State management hook
3. **LangGraphStateDisplay** - AgentState dashboard
4. **SectionInterruptHandler** - Human interrupt interface
5. **InformedConsentPage Integration** - Final page integration

### LangGraph Testing Strategy
- Mock LangGraph API responses for component testing
- Simulate AgentState updates for state management testing
- Test interrupt workflows with mock human responses
- E2E tests with LangGraph test environment

### Performance Considerations (LangGraph-Specific)
- Efficient AgentState polling with smart intervals
- Component memoization for static AgentState content
- Minimal re-renders during polling cycles
- Proper cleanup of polling and API connections

### Error Handling Patterns
- LangGraph execution failures with restart options
- Network connectivity issues with retry mechanisms
- Invalid AgentState responses with graceful degradation
- Human interrupt response failures with feedback to user

---

## Refinement Notes

**These are draft prompts requiring iteration based on:**
- Actual LangGraph API contract and response formats
- AgentState structure and status field implementation
- Human interrupt mechanism and timing
- Backend integration testing and optimization

**Next Steps:**
1. Implement LangGraph backend endpoints
2. Test prompts with AI agents using mock LangGraph responses
3. Refine component interfaces based on actual AgentState structure
4. Optimize polling strategies based on performance testing
5. Update interrupt handling based on LangGraph interrupt API