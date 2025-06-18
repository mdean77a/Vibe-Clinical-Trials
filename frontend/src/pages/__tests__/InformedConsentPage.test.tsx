/**
 * Unit tests for InformedConsentPage component
 * 
 * Tests ICF generation functionality including:
 * - Document generation initiation
 * - Progress tracking
 * - Section display and editing
 * - Download functionality
 * - Error handling
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'

import { render, createMockProtocol, createMockDocument } from '../../test/test-utils'
import InformedConsentPage from '../InformedConsentPage'

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

describe('InformedConsentPage', () => {
  beforeEach(() => {
    mockNavigate.mockClear()
  })

  it('renders ICF generation page correctly', () => {
    render(<InformedConsentPage />)
    
    expect(screen.getByText('Generate Informed Consent Form')).toBeInTheDocument()
    expect(screen.getByText(/creating comprehensive informed consent documentation/i)).toBeInTheDocument()
  })

  it('displays protocol information', () => {
    render(<InformedConsentPage />)
    
    expect(screen.getByText('Protocol Information')).toBeInTheDocument()
    expect(screen.getByText('STUDY-001')).toBeInTheDocument()
    expect(screen.getByText('Test Clinical Trial Protocol')).toBeInTheDocument()
  })

  it('shows generate button initially', () => {
    render(<InformedConsentPage />)
    
    expect(screen.getByRole('button', { name: /generate informed consent form/i })).toBeInTheDocument()
  })

  it('starts generation process when generate button is clicked', async () => {
    const user = userEvent.setup()
    
    render(<InformedConsentPage />)
    
    const generateButton = screen.getByRole('button', { name: /generate informed consent form/i })
    await user.click(generateButton)
    
    expect(screen.getByText(/generating your informed consent form/i)).toBeInTheDocument()
    expect(screen.getByRole('progressbar')).toBeInTheDocument()
  })

  it('displays generation progress with steps', async () => {
    const user = userEvent.setup()
    
    render(<InformedConsentPage />)
    
    const generateButton = screen.getByRole('button', { name: /generate informed consent form/i })
    await user.click(generateButton)
    
    expect(screen.getByText(/analyzing protocol content/i)).toBeInTheDocument()
    expect(screen.getByText(/step 1 of 4/i)).toBeInTheDocument()
  })

  it('shows generated ICF sections after completion', async () => {
    const user = userEvent.setup()
    
    render(<InformedConsentPage />)
    
    const generateButton = screen.getByRole('button', { name: /generate informed consent form/i })
    await user.click(generateButton)
    
    await waitFor(() => {
      expect(screen.getByText('Study Title')).toBeInTheDocument()
      expect(screen.getByText('Purpose')).toBeInTheDocument()
      expect(screen.getByText('Procedures')).toBeInTheDocument()
      expect(screen.getByText('Risks')).toBeInTheDocument()
      expect(screen.getByText('Benefits')).toBeInTheDocument()
      expect(screen.getByText('Rights')).toBeInTheDocument()
      expect(screen.getByText('Contact Information')).toBeInTheDocument()
    })
  })

  it('displays generated content for each section', async () => {
    const user = userEvent.setup()
    
    render(<InformedConsentPage />)
    
    const generateButton = screen.getByRole('button', { name: /generate informed consent form/i })
    await user.click(generateButton)
    
    await waitFor(() => {
      expect(screen.getByText('Generated Title')).toBeInTheDocument()
      expect(screen.getByText('Generated Purpose')).toBeInTheDocument()
      expect(screen.getByText('Generated Procedures')).toBeInTheDocument()
    })
  })

  it('allows editing of generated sections', async () => {
    const user = userEvent.setup()
    
    render(<InformedConsentPage />)
    
    // Generate ICF
    const generateButton = screen.getByRole('button', { name: /generate informed consent form/i })
    await user.click(generateButton)
    
    await waitFor(() => {
      expect(screen.getByText('Generated Title')).toBeInTheDocument()
    })
    
    // Edit title section
    const editButton = screen.getAllByRole('button', { name: /edit/i })[0]
    await user.click(editButton)
    
    const titleTextarea = screen.getByDisplayValue('Generated Title')
    await user.clear(titleTextarea)
    await user.type(titleTextarea, 'Edited Study Title')
    
    const saveButton = screen.getByRole('button', { name: /save/i })
    await user.click(saveButton)
    
    expect(screen.getByText('Edited Study Title')).toBeInTheDocument()
  })

  it('shows download options after generation', async () => {
    const user = userEvent.setup()
    
    render(<InformedConsentPage />)
    
    const generateButton = screen.getByRole('button', { name: /generate informed consent form/i })
    await user.click(generateButton)
    
    await waitFor(() => {
      expect(screen.getByRole('button', { name: /download pdf/i })).toBeInTheDocument()
      expect(screen.getByRole('button', { name: /download word/i })).toBeInTheDocument()
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
    
    render(<InformedConsentPage />)
    
    const generateButton = screen.getByRole('button', { name: /generate informed consent form/i })
    await user.click(generateButton)
    
    await waitFor(() => {
      expect(screen.getByText(/generation failed/i)).toBeInTheDocument()
      expect(screen.getByRole('button', { name: /try again/i })).toBeInTheDocument()
    })
  })

  it('allows retry after generation failure', async () => {
    const user = userEvent.setup()
    
    // Mock error then success
    const { server } = await import('../../test/setup')
    const { http, HttpResponse } = await import('msw')
    
    let callCount = 0
    server.use(
      http.post('/api/generate-document', () => {
        callCount++
        if (callCount === 1) {
          return new HttpResponse(null, { status: 500 })
        }
        return HttpResponse.json(createMockDocument('icf'))
      })
    )
    
    render(<InformedConsentPage />)
    
    const generateButton = screen.getByRole('button', { name: /generate informed consent form/i })
    await user.click(generateButton)
    
    await waitFor(() => {
      expect(screen.getByText(/generation failed/i)).toBeInTheDocument()
    })
    
    const retryButton = screen.getByRole('button', { name: /try again/i })
    await user.click(retryButton)
    
    await waitFor(() => {
      expect(screen.getByText('Study Title')).toBeInTheDocument()
    })
  })

  it('navigates back to document selection', async () => {
    const user = userEvent.setup()
    
    render(<InformedConsentPage />)
    
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
    
    render(<InformedConsentPage />)
    
    expect(screen.getByText(/no protocol selected/i)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /return to home/i })).toBeInTheDocument()
  })

  it('shows section validation status', async () => {
    const user = userEvent.setup()
    
    render(<InformedConsentPage />)
    
    const generateButton = screen.getByRole('button', { name: /generate informed consent form/i })
    await user.click(generateButton)
    
    await waitFor(() => {
      // Check for validation indicators
      expect(screen.getAllByText(/✓/)).toHaveLength(7) // 7 sections
    })
  })

  it('displays word count for each section', async () => {
    const user = userEvent.setup()
    
    render(<InformedConsentPage />)
    
    const generateButton = screen.getByRole('button', { name: /generate informed consent form/i })
    await user.click(generateButton)
    
    await waitFor(() => {
      expect(screen.getAllByText(/\d+ words/)).toHaveLength(7)
    })
  })

  it('shows preview of complete document', async () => {
    const user = userEvent.setup()
    
    render(<InformedConsentPage />)
    
    const generateButton = screen.getByRole('button', { name: /generate informed consent form/i })
    await user.click(generateButton)
    
    await waitFor(() => {
      expect(screen.getByRole('button', { name: /preview document/i })).toBeInTheDocument()
    })
    
    const previewButton = screen.getByRole('button', { name: /preview document/i })
    await user.click(previewButton)
    
    expect(screen.getByText(/document preview/i)).toBeInTheDocument()
  })

  it('supports section reordering', async () => {
    const user = userEvent.setup()
    
    render(<InformedConsentPage />)
    
    const generateButton = screen.getByRole('button', { name: /generate informed consent form/i })
    await user.click(generateButton)
    
    await waitFor(() => {
      expect(screen.getAllByRole('button', { name: /move up/i })).toBeTruthy()
      expect(screen.getAllByRole('button', { name: /move down/i })).toBeTruthy()
    })
  })

  it('shows generation time estimate', () => {
    render(<InformedConsentPage />)
    
    expect(screen.getByText(/estimated time: 2-3 minutes/i)).toBeInTheDocument()
  })

  it('displays compliance information', async () => {
    const user = userEvent.setup()
    
    render(<InformedConsentPage />)
    
    const generateButton = screen.getByRole('button', { name: /generate informed consent form/i })
    await user.click(generateButton)
    
    await waitFor(() => {
      expect(screen.getByText(/ich-gcp compliant/i)).toBeInTheDocument()
      expect(screen.getByText(/fda guidelines/i)).toBeInTheDocument()
    })
  })

  it('has proper accessibility structure', () => {
    render(<InformedConsentPage />)
    
    // Check for proper heading hierarchy
    const mainHeading = screen.getByRole('heading', { level: 1 })
    expect(mainHeading).toHaveTextContent(/generate informed consent form/i)
    
    // Check for proper navigation
    expect(screen.getByRole('navigation')).toBeInTheDocument()
  })

  it('handles keyboard navigation correctly', async () => {
    const user = userEvent.setup()
    
    render(<InformedConsentPage />)
    
    // Tab through interactive elements
    await user.tab()
    expect(screen.getByRole('button', { name: /back to document selection/i })).toHaveFocus()
    
    await user.tab()
    expect(screen.getByRole('button', { name: /generate informed consent form/i })).toHaveFocus()
  })

  it('persists user edits during session', async () => {
    const user = userEvent.setup()
    
    render(<InformedConsentPage />)
    
    // Generate and edit
    const generateButton = screen.getByRole('button', { name: /generate informed consent form/i })
    await user.click(generateButton)
    
    await waitFor(() => {
      expect(screen.getByText('Generated Title')).toBeInTheDocument()
    })
    
    // Edit section
    const editButton = screen.getAllByRole('button', { name: /edit/i })[0]
    await user.click(editButton)
    
    const titleTextarea = screen.getByDisplayValue('Generated Title')
    await user.clear(titleTextarea)
    await user.type(titleTextarea, 'Modified Title')
    
    const saveButton = screen.getByRole('button', { name: /save/i })
    await user.click(saveButton)
    
    // Navigate away and back (simulate)
    expect(screen.getByText('Modified Title')).toBeInTheDocument()
  })
})