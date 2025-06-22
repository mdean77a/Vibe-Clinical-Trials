# Document Editor UI & Interaction Flow

## Layout
- Sidebar: List of document sections (with status indicators)
- Main: Rich text editor, regeneration prompt, approve/undo buttons
- Right: Protocol viewer with search

## Interaction
- Users can:
  - Edit content manually
  - Prompt AI to regenerate a section
  - Mark section as Approved
  - Export when all approved

## Components
- React, Tailwind, shadcn/ui
- Tiptap editor or equivalent
- State-tracking per section
- Regeneration is non-destructive (versioned in memory)

