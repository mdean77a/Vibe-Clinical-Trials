# Vibe Clinical Trials Coding Standards

## Core Standards

- **Languages & Runtimes:** 
  - TypeScript 5.3.3 (both frontend and backend)
  - Node.js 20.11.0 LTS
  - Python 3.11+ (for AI/ML components)
  
- **Style & Linting:**
  - ESLint with TypeScript plugin
  - Prettier for code formatting
  - Pre-commit hooks for automated checks
  
- **Test Organization:**
  - Test files in `__tests__` folders: `*.test.tsx` or `*.test.ts`
  - Test utilities in `src/test/`
  - Integration tests in `tests/integration/`
  - E2E tests in `tests/e2e/`

## Naming Conventions

| Element | Convention | Example |
| :------ | :--------- | :------ |
| Variables | camelCase | `protocols`, `showUpload`, `apiHealthy` |
| Functions | camelCase | `loadProtocols()`, `generateICF()` |
| Event Handlers | handle prefix | `handleClick()`, `handleProtocolSelect()` |
| Boolean Variables | is/has prefix | `isGenerating`, `hasStartedGeneration` |
| Constants | UPPER_SNAKE_CASE | `API_BASE_URL` |
| Classes | PascalCase | `Protocol`, `ICFSection` |
| Component Files | PascalCase | `Button.tsx`, `ICFGenerationDashboard.tsx` |
| Utility Files | camelCase | `api.ts`, `vectorUtils.ts` |
| React Components | PascalCase | `HomePage`, `ProtocolList` |
| Props Interfaces | ComponentNameProps | `ButtonProps`, `HomePageProps` |
| API Routes | kebab-case | `/api/protocols`, `/api/icf-generation` |
| Route Paths | kebab-case | `/document-selection`, `/icf-generation` |
| Qdrant Collections | snake_case | `clinical_trials`, `protocol_embeddings` |

## Critical Rules

- **Type Safety:** Avoid `any` type - use proper type definitions or type assertions when needed
- **API Organization:** All API calls must go through the centralized `utils/api.ts` module
- **API Namespaces:** Group related API calls in namespaces (e.g., `protocolsApi`, `icfApi`)
- **Error Handling:** Use try-catch blocks with fallback strategies (e.g., localStorage fallback)
- **Component Structure:** Use functional components with React.FC and Props interfaces
- **State Management:** Use React hooks for local state - no direct state mutation
- **Async Operations:** Always use async/await with proper error handling
- **Console Logging:** Use descriptive console logs for debugging and errors
- **Local Storage:** Use for persistence between sessions when API is unavailable
- **Testing:** Tests in `__tests__` folders using Vitest and React Testing Library

## Language-Specific Guidelines

### TypeScript Specifics

- **Strict Mode:** Always enable strict mode in tsconfig.json
- **Type Imports:** Use type-only imports when importing just types: `import type { Protocol } from './types'`
- **Type Assertions:** Use `as` for API responses when type is known
- **Interface Naming:** Props interfaces end with `Props`, regular interfaces use descriptive names
- **Generics:** Use in utility functions for type safety (e.g., `apiRequest<T>`)

### React Specifics

- **Components:** Functional components only with `React.FC<Props>`
- **Component Files:** One component per file, exported as default
- **Props Interfaces:** Define above component with descriptive `ComponentNameProps` pattern
- **Hooks:** Custom hooks must start with 'use' prefix
- **Event Handlers:** Inline arrow functions for simple handlers, named functions for complex logic
- **Conditional Rendering:** Use ternary operators or logical AND (&&)

## Import Order

1. React imports
2. External dependencies
3. Internal paths with @ alias
4. Relative imports
5. Type imports
6. Style imports (if any)

```typescript
// React
import React from 'react';
import { useState, useEffect } from 'react';

// External dependencies
import { useNavigate } from 'react-router-dom';

// Internal with @ alias
import { protocolsApi } from '@/utils/api';
import Button from '@/components/Button';

// Relative imports
import ProtocolCard from './ProtocolCard';

// Type imports
import type { Protocol } from '@/types';

// Styles (inline styles preferred with Tailwind)
```

## API Patterns

### API Module Structure

All API calls must be organized in `src/utils/api.ts`:

```typescript
// Base configuration
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Generic request handler
async function apiRequest<T>(endpoint: string, options?: RequestInit): Promise<T> {
  // Implementation with error handling
}

// Feature namespaces
export const protocolsApi = {
  list: () => apiRequest<Protocol[]>('/api/protocols'),
  get: (id: string) => apiRequest<Protocol>(`/api/protocols/${id}`),
  upload: (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    return apiRequest('/api/protocols/upload', {
      method: 'POST',
      body: formData
    });
  }
};

export const icfApi = {
  generate: (data: ICFGenerationRequest) => 
    apiRequest<ICFGenerationResponse>('/api/icf/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    })
};
```

### Error Handling with Fallbacks

```typescript
try {
  const apiResponse = await protocolsApi.list() as any;
  const apiProtocols = apiResponse.protocols || apiResponse || [];
  setProtocols(apiProtocols);
} catch (error) {
  console.error('Failed to load from API, using localStorage:', error);
  // Fallback to localStorage
  const stored = localStorage.getItem('uploadedProtocols');
  if (stored) {
    setProtocols(JSON.parse(stored));
  }
}
```

## Styling Approach

### Tailwind CSS

- **Primary Styling Method:** Use Tailwind utility classes
- **Class Composition:** Combine utilities for complex styles
- **Dynamic Classes:** Use template literals for conditional classes

```typescript
// Static classes
<Button className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600">

// Dynamic classes
<div className={`px-4 py-2 ${isActive ? 'bg-blue-500' : 'bg-gray-500'} rounded`}>

// Combining with props
<Button className={`px-4 py-2 bg-blue-500 text-white rounded ${className}`}>
```

### Inline Styles

Use for dynamic values that can't be expressed with Tailwind:

```typescript
<div style={{ 
  padding: '24px', 
  maxWidth: '1024px',
  backgroundColor: dynamicColor 
}}>
```

## Component Patterns

### Standard Component Structure

```typescript
import React from 'react';

interface ComponentNameProps {
  title: string;
  onClick?: () => void;
  className?: string;
}

const ComponentName: React.FC<ComponentNameProps> = ({ 
  title, 
  onClick, 
  className = '' 
}) => {
  // Hooks
  const [state, setState] = useState(false);
  
  // Effects
  useEffect(() => {
    // Effect logic
  }, []);
  
  // Handlers
  const handleClick = () => {
    onClick?.();
  };
  
  // Render
  return (
    <div className={`component-base ${className}`}>
      {/* Component content */}
    </div>
  );
};

export default ComponentName;
```

## Git Commit Conventions

- Use conventional commits: `feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`
- Keep commits atomic and focused
- Write clear, imperative mood messages: "Add protocol upload feature" not "Added protocol upload feature"