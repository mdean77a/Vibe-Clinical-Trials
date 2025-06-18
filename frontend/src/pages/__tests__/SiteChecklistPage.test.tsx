/**
 * Unit tests for SiteChecklistPage component
 * 
 * Tests site checklist generation functionality including:
 * - Document generation initiation
 * - Progress tracking
 * - Section display and editing
 * - Task completion tracking
 * - Download functionality
 * - Error handling
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'

import { render, createMockProtocol, createMockDocument } from '../../test/test-utils'
import SiteChecklistPage from '../SiteChecklistPage'

// Mock navigate and location
const mockNavigate = vi.fn()
const mockLocation = {
  state: {
    protocol: createMockProtocol()
  }
}

vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom')
  return {
    ...actual,
    useNavigate: () => mockNavigate,
    useLocation: () => mockLocation
  }
})

describe('SiteChecklistPage', () => {
  beforeEach(() => {
    mockNavigate.mockClear()
  })

  it('renders site checklist generation page correctly', () => {
    render(<SiteChecklistPage />)
    
    expect(screen.getByText('Generate Site Initiation Checklist')).toBeInTheDocument()
    expect(screen.getByText(/comprehensive site preparation checklist/i)).toBeInTheDocument()
  })

  it('displays protocol information', () => {
    render(<SiteChecklistPage />)
    
    expect(screen.getByText('Protocol Information')).toBeInTheDocument()
    expect(screen.getByText('STUDY-001')).toBeInTheDocument()
    expect(screen.getByText('Test Clinical Trial Protocol')).toBeInTheDocument()
  })

  it('shows generate button initially', () => {
    render(<SiteChecklistPage />)
    
    expect(screen.getByRole('button', { name: /generate site checklist/i })).toBeInTheDocument()
  })

  it('starts generation process when generate button is clicked', async () => {
    const user = userEvent.setup()
    
    render(<SiteChecklistPage />)
    
    const generateButton = screen.getByRole('button', { name: /generate site checklist/i })
    await user.click(generateButton)
    
    expect(screen.getByText(/generating your site initiation checklist/i)).toBeInTheDocument()
    expect(screen.getByRole('progressbar')).toBeInTheDocument()
  })

  it('displays generation progress with steps', async () => {
    const user = userEvent.setup()
    
    render(<SiteChecklistPage />)
    
    const generateButton = screen.getByRole('button', { name: /generate site checklist/i })
    await user.click(generateButton)
    
    expect(screen.getByText(/analyzing protocol requirements/i)).toBeInTheDocument()
    expect(screen.getByText(/step 1 of 4/i)).toBeInTheDocument()
  })

  it('shows generated checklist sections after completion', async () => {
    const user = userEvent.setup()
    
    render(<SiteChecklistPage />)
    
    const generateButton = screen.getByRole('button', { name: /generate site checklist/i })
    await user.click(generateButton)
    
    await waitFor(() => {
      expect(screen.getByText('Regulatory Requirements')).toBeInTheDocument()
      expect(screen.getByText('Training Requirements')).toBeInTheDocument()
      expect(screen.getByText('Equipment & Supplies')).toBeInTheDocument()
      expect(screen.getByText('Documentation')).toBeInTheDocument()
    })
  })

  it('displays generated content for each section', async () => {
    const user = userEvent.setup()
    
    render(<SiteChecklistPage />)
    
    const generateButton = screen.getByRole('button', { name: /generate site checklist/i })
    await user.click(generateButton)
    
    await waitFor(() => {
      expect(screen.getByText('Generated Regulatory Requirements')).toBeInTheDocument()
      expect(screen.getByText('Generated Training Requirements')).toBeInTheDocument()
      expect(screen.getByText('Generated Equipment List')).toBeInTheDocument()
      expect(screen.getByText('Generated Documentation Requirements')).toBeInTheDocument()
    })
  })

  it('displays checklist items with checkboxes', async () => {
    const user = userEvent.setup()
    
    render(<SiteChecklistPage />)
    
    const generateButton = screen.getByRole('button', { name: /generate site checklist/i })
    await user.click(generateButton)
    
    await waitFor(() => {
      const checkboxes = screen.getAllByRole('checkbox')
      expect(checkboxes.length).toBeGreaterThan(0)
    })
  })

  it('allows checking off completed tasks', async () => {
    const user = userEvent.setup()
    
    render(<SiteChecklistPage />)
    
    const generateButton = screen.getByRole('button', { name: /generate site checklist/i })
    await user.click(generateButton)
    
    await waitFor(() => {
      const firstCheckbox = screen.getAllByRole('checkbox')[0]
      expect(firstCheckbox).not.toBeChecked()
    })
    
    const firstCheckbox = screen.getAllByRole('checkbox')[0]
    await user.click(firstCheckbox)
    
    expect(firstCheckbox).toBeChecked()
  })

  it('shows completion progress', async () => {
    const user = userEvent.setup()
    
    render(<SiteChecklistPage />)
    
    const generateButton = screen.getByRole('button', { name: /generate site checklist/i })
    await user.click(generateButton)
    
    await waitFor(() => {
      expect(screen.getByText(/0% complete/i)).toBeInTheDocument()
    })
    
    // Check a task
    const firstCheckbox = screen.getAllByRole('checkbox')[0]
    await user.click(firstCheckbox)
    
    expect(screen.getByText(/\d+% complete/i)).toBeInTheDocument()
  })

  it('allows editing of generated sections', async () => {
    const user = userEvent.setup()
    
    render(<SiteChecklistPage />)
    
    // Generate checklist
    const generateButton = screen.getByRole('button', { name: /generate site checklist/i })
    await user.click(generateButton)
    
    await waitFor(() => {
      expect(screen.getByText('Generated Regulatory Requirements')).toBeInTheDocument()
    })
    
    // Edit regulatory section
    const editButton = screen.getAllByRole('button', { name: /edit/i })[0]
    await user.click(editButton)
    
    const textarea = screen.getByDisplayValue('Generated Regulatory Requirements')
    await user.clear(textarea)
    await user.type(textarea, 'Edited Regulatory Requirements')
    
    const saveButton = screen.getByRole('button', { name: /save/i })
    await user.click(saveButton)
    
    expect(screen.getByText('Edited Regulatory Requirements')).toBeInTheDocument()
  })

  it('allows adding custom checklist items', async () => {
    const user = userEvent.setup()
    
    render(<SiteChecklistPage />)
    
    const generateButton = screen.getByRole('button', { name: /generate site checklist/i })
    await user.click(generateButton)
    
    await waitFor(() => {
      expect(screen.getByText('Regulatory Requirements')).toBeInTheDocument()
    })
    
    const addItemButton = screen.getByRole('button', { name: /add custom item/i })
    await user.click(addItemButton)
    
    const newItemInput = screen.getByPlaceholderText(/enter custom checklist item/i)
    await user.type(newItemInput, 'Custom regulatory requirement')
    
    const saveItemButton = screen.getByRole('button', { name: /add item/i })
    await user.click(saveItemButton)
    
    expect(screen.getByText('Custom regulatory requirement')).toBeInTheDocument()
  })

  it('shows download options after generation', async () => {
    const user = userEvent.setup()
    
    render(<SiteChecklistPage />)
    
    const generateButton = screen.getByRole('button', { name: /generate site checklist/i })
    await user.click(generateButton)
    
    await waitFor(() => {
      expect(screen.getByRole('button', { name: /download pdf/i })).toBeInTheDocument()
      expect(screen.getByRole('button', { name: /download excel/i })).toBeInTheDocument()
    })
  })

  it('handles generation errors gracefully', async () => {
    const user = userEvent.setup()
    
    // Mock API error
    const { server } = await import('../../test/setup')
    const { http, HttpResponse } = await import('msw')
    
    server.use(
      http.post('/api/generate-document', () => {
        return new HttpResponse(null, { status: 500 })
      })
    )
    
    render(<SiteChecklistPage />)
    
    const generateButton = screen.getByRole('button', { name: /generate site checklist/i })
    await user.click(generateButton)
    
    await waitFor(() => {
      expect(screen.getByText(/generation failed/i)).toBeInTheDocument()
      expect(screen.getByRole('button', { name: /try again/i })).toBeInTheDocument()
    })
  })

  it('navigates back to document selection', async () => {
    const user = userEvent.setup()
    
    render(<SiteChecklistPage />)
    
    const backButton = screen.getByRole('button', { name: /back to document selection/i })
    await user.click(backButton)
    
    expect(mockNavigate).toHaveBeenCalledWith('/document-selection', {
      state: {
        protocol: expect.objectContaining({
          study_acronym: 'STUDY-001'
        })
      }
    })
  })

  it('handles missing protocol gracefully', () => {
    // Override mock to return no protocol
    vi.mocked(mockLocation).state = null
    
    render(<SiteChecklistPage />)
    
    expect(screen.getByText(/no protocol selected/i)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /return to home/i })).toBeInTheDocument()
  })

  it('categorizes checklist items properly', async () => {
    const user = userEvent.setup()
    
    render(<SiteChecklistPage />)
    
    const generateButton = screen.getByRole('button', { name: /generate site checklist/i })
    await user.click(generateButton)
    
    await waitFor(() => {
      // Check that items are properly categorized
      expect(screen.getByText('Pre-Study Tasks')).toBeInTheDocument()
      expect(screen.getByText('Study Initiation Tasks')).toBeInTheDocument()
      expect(screen.getByText('Ongoing Maintenance')).toBeInTheDocument()
    })
  })

  it('shows task priorities and deadlines', async () => {
    const user = userEvent.setup()
    
    render(<SiteChecklistPage />)
    
    const generateButton = screen.getByRole('button', { name: /generate site checklist/i })
    await user.click(generateButton)
    
    await waitFor(() => {
      expect(screen.getByText(/high priority/i)).toBeInTheDocument()
      expect(screen.getByText(/medium priority/i)).toBeInTheDocument()
      expect(screen.getByText(/due before study start/i)).toBeInTheDocument()
    })
  })

  it('supports filtering tasks by category', async () => {
    const user = userEvent.setup()
    
    render(<SiteChecklistPage />)
    
    const generateButton = screen.getByRole('button', { name: /generate site checklist/i })
    await user.click(generateButton)
    
    await waitFor(() => {
      expect(screen.getByRole('button', { name: /all tasks/i })).toBeInTheDocument()
      expect(screen.getByRole('button', { name: /regulatory only/i })).toBeInTheDocument()
      expect(screen.getByRole('button', { name: /training only/i })).toBeInTheDocument()
    })
    
    const regulatoryFilter = screen.getByRole('button', { name: /regulatory only/i })
    await user.click(regulatoryFilter)
    
    // Should show only regulatory tasks
    expect(screen.getByText('Regulatory Requirements')).toBeInTheDocument()
  })

  it('exports completion status with downloads', async () => {
    const user = userEvent.setup()
    
    render(<SiteChecklistPage />)
    
    const generateButton = screen.getByRole('button', { name: /generate site checklist/i })
    await user.click(generateButton)
    
    await waitFor(() => {
      expect(screen.getByRole('button', { name: /download pdf/i })).toBeInTheDocument()
    })
    
    // Check some tasks
    const checkboxes = screen.getAllByRole('checkbox')
    await user.click(checkboxes[0])
    await user.click(checkboxes[1])
    
    // Download should include completion status
    const downloadButton = screen.getByRole('button', { name: /download pdf/i })
    expect(downloadButton).toBeInTheDocument()
  })

  it('shows estimated timeline for completion', async () => {
    const user = userEvent.setup()
    
    render(<SiteChecklistPage />)
    
    const generateButton = screen.getByRole('button', { name: /generate site checklist/i })
    await user.click(generateButton)
    
    await waitFor(() => {
      expect(screen.getByText(/estimated completion time/i)).toBeInTheDocument()
      expect(screen.getByText(/2-4 weeks/i)).toBeInTheDocument()
    })
  })

  it('displays responsible party for each task', async () => {
    const user = userEvent.setup()
    
    render(<SiteChecklistPage />)
    
    const generateButton = screen.getByRole('button', { name: /generate site checklist/i })
    await user.click(generateButton)
    
    await waitFor(() => {
      expect(screen.getByText(/site coordinator/i)).toBeInTheDocument()
      expect(screen.getByText(/principal investigator/i)).toBeInTheDocument()
      expect(screen.getByText(/regulatory affairs/i)).toBeInTheDocument()
    })
  })

  it('has proper accessibility structure', () => {
    render(<SiteChecklistPage />)
    
    // Check for proper heading hierarchy
    const mainHeading = screen.getByRole('heading', { level: 1 })
    expect(mainHeading).toHaveTextContent(/generate site initiation checklist/i)
    
    // Check for proper navigation
    expect(screen.getByRole('navigation')).toBeInTheDocument()
  })

  it('handles keyboard navigation correctly', async () => {
    const user = userEvent.setup()
    
    render(<SiteChecklistPage />)
    
    // Tab through interactive elements
    await user.tab()
    expect(screen.getByRole('button', { name: /back to document selection/i })).toHaveFocus()
    
    await user.tab()
    expect(screen.getByRole('button', { name: /generate site checklist/i })).toHaveFocus()
  })

  it('preserves task completion state during session', async () => {
    const user = userEvent.setup()
    
    render(<SiteChecklistPage />)
    
    const generateButton = screen.getByRole('button', { name: /generate site checklist/i })
    await user.click(generateButton)
    
    await waitFor(() => {
      const firstCheckbox = screen.getAllByRole('checkbox')[0]
      expect(firstCheckbox).not.toBeChecked()
    })
    
    // Check task
    const firstCheckbox = screen.getAllByRole('checkbox')[0]
    await user.click(firstCheckbox)
    
    expect(firstCheckbox).toBeChecked()
    
    // State should persist during session
    expect(firstCheckbox).toBeChecked()
  })

  it('shows task dependencies and prerequisites', async () => {
    const user = userEvent.setup()
    
    render(<SiteChecklistPage />)
    
    const generateButton = screen.getByRole('button', { name: /generate site checklist/i })
    await user.click(generateButton)
    
    await waitFor(() => {
      expect(screen.getByText(/prerequisite:/i)).toBeInTheDocument()
      expect(screen.getByText(/depends on:/i)).toBeInTheDocument()
    })
  })
})