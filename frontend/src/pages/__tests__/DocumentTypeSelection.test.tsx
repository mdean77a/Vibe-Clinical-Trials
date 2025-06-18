/**
 * Unit tests for DocumentTypeSelection component
 * 
 * Tests document type selection functionality including:
 * - Document type options display
 * - Type selection handling
 * - Navigation to specific generators
 * - Protocol context handling
 * - Error states
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'

import { render, createMockProtocol } from '../../test/test-utils'
import DocumentTypeSelection from '../DocumentTypeSelection'

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

describe('DocumentTypeSelection', () => {
  beforeEach(() => {
    mockNavigate.mockClear()
  })

  it('renders document type selection page correctly', () => {
    render(<DocumentTypeSelection />)
    
    expect(screen.getByText('Select Document Type')).toBeInTheDocument()
    expect(screen.getByText(/choose the type of document you want to generate/i)).toBeInTheDocument()
  })

  it('displays protocol information', () => {
    render(<DocumentTypeSelection />)
    
    expect(screen.getByText('Selected Protocol')).toBeInTheDocument()
    expect(screen.getByText('STUDY-001')).toBeInTheDocument()
    expect(screen.getByText('Test Clinical Trial Protocol')).toBeInTheDocument()
  })

  it('displays ICF document type option', () => {
    render(<DocumentTypeSelection />)
    
    expect(screen.getByText('Informed Consent Form (ICF)')).toBeInTheDocument()
    expect(screen.getByText(/generate comprehensive informed consent documentation/i)).toBeInTheDocument()
    expect(screen.getByText(/patient rights and study information/i)).toBeInTheDocument()
  })

  it('displays Site Checklist document type option', () => {
    render(<DocumentTypeSelection />)
    
    expect(screen.getByText('Site Initiation Checklist')).toBeInTheDocument()
    expect(screen.getByText(/generate detailed site preparation checklists/i)).toBeInTheDocument()
    expect(screen.getByText(/regulatory requirements and training/i)).toBeInTheDocument()
  })

  it('navigates to ICF generator when selected', async () => {
    const user = userEvent.setup()
    
    render(<DocumentTypeSelection />)
    
    const icfCard = screen.getByText('Informed Consent Form (ICF)').closest('div')
    const icfButton = icfCard?.querySelector('button')
    
    expect(icfButton).toBeInTheDocument()
    await user.click(icfButton!)
    
    expect(mockNavigate).toHaveBeenCalledWith('/informed-consent', {
      state: {
        protocol: expect.objectContaining({
          study_acronym: 'STUDY-001'
        })
      }
    })
  })

  it('navigates to Site Checklist generator when selected', async () => {
    const user = userEvent.setup()
    
    render(<DocumentTypeSelection />)
    
    const checklistCard = screen.getByText('Site Initiation Checklist').closest('div')
    const checklistButton = checklistCard?.querySelector('button')
    
    expect(checklistButton).toBeInTheDocument()
    await user.click(checklistButton!)
    
    expect(mockNavigate).toHaveBeenCalledWith('/site-checklist', {
      state: {
        protocol: expect.objectContaining({
          study_acronym: 'STUDY-001'
        })
      }
    })
  })

  it('shows back to protocol selection button', () => {
    render(<DocumentTypeSelection />)
    
    expect(screen.getByRole('button', { name: /back to protocol selection/i })).toBeInTheDocument()
  })

  it('navigates back to home when back button is clicked', async () => {
    const user = userEvent.setup()
    
    render(<DocumentTypeSelection />)
    
    const backButton = screen.getByRole('button', { name: /back to protocol selection/i })
    await user.click(backButton)
    
    expect(mockNavigate).toHaveBeenCalledWith('/')
  })

  it('handles missing protocol gracefully', () => {
    // Override mock to return no protocol
    vi.mocked(mockLocation).state = null
    
    render(<DocumentTypeSelection />)
    
    expect(screen.getByText(/no protocol selected/i)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /return to home/i })).toBeInTheDocument()
  })

  it('redirects to home when no protocol is provided', async () => {
    const user = userEvent.setup()
    
    // Override mock to return no protocol
    vi.mocked(mockLocation).state = null
    
    render(<DocumentTypeSelection />)
    
    const returnButton = screen.getByRole('button', { name: /return to home/i })
    await user.click(returnButton)
    
    expect(mockNavigate).toHaveBeenCalledWith('/')
  })

  it('displays document type features correctly', () => {
    render(<DocumentTypeSelection />)
    
    // ICF features
    expect(screen.getByText(/study objectives and procedures/i)).toBeInTheDocument()
    expect(screen.getByText(/risks and benefits/i)).toBeInTheDocument()
    expect(screen.getByText(/participant rights/i)).toBeInTheDocument()
    expect(screen.getByText(/contact information/i)).toBeInTheDocument()
    
    // Site Checklist features
    expect(screen.getByText(/regulatory compliance/i)).toBeInTheDocument()
    expect(screen.getByText(/staff training requirements/i)).toBeInTheDocument()
    expect(screen.getByText(/equipment and supplies/i)).toBeInTheDocument()
    expect(screen.getByText(/documentation checklist/i)).toBeInTheDocument()
  })

  it('shows estimated generation time for each document type', () => {
    render(<DocumentTypeSelection />)
    
    expect(screen.getByText(/estimated time: 2-3 minutes/i)).toBeInTheDocument()
    expect(screen.getByText(/estimated time: 1-2 minutes/i)).toBeInTheDocument()
  })

  it('displays document type icons or images', () => {
    render(<DocumentTypeSelection />)
    
    // Check for document type visual indicators
    const icfSection = screen.getByText('Informed Consent Form (ICF)').closest('div')
    const checklistSection = screen.getByText('Site Initiation Checklist').closest('div')
    
    expect(icfSection).toHaveClass('bg-white', 'border', 'rounded-lg')
    expect(checklistSection).toHaveClass('bg-white', 'border', 'rounded-lg')
  })

  it('handles keyboard navigation correctly', async () => {
    const user = userEvent.setup()
    
    render(<DocumentTypeSelection />)
    
    // Tab through interactive elements
    await user.tab()
    expect(screen.getByRole('button', { name: /back to protocol selection/i })).toHaveFocus()
    
    await user.tab()
    const icfButton = screen.getByText('Generate ICF').closest('button')
    expect(icfButton).toHaveFocus()
    
    await user.tab()
    const checklistButton = screen.getByText('Generate Checklist').closest('button')
    expect(checklistButton).toHaveFocus()
  })

  it('shows protocol status and upload date', () => {
    render(<DocumentTypeSelection />)
    
    expect(screen.getByText(/status: completed/i)).toBeInTheDocument()
    expect(screen.getByText(/uploaded:/i)).toBeInTheDocument()
  })

  it('has proper accessibility structure', () => {
    render(<DocumentTypeSelection />)
    
    // Check for proper heading hierarchy
    const mainHeading = screen.getByRole('heading', { level: 1 })
    expect(mainHeading).toHaveTextContent(/select document type/i)
    
    // Check for proper section headings
    expect(screen.getByRole('heading', { level: 2, name: /selected protocol/i })).toBeInTheDocument()
    expect(screen.getByRole('heading', { level: 3, name: /informed consent form/i })).toBeInTheDocument()
    expect(screen.getByRole('heading', { level: 3, name: /site initiation checklist/i })).toBeInTheDocument()
  })

  it('displays helpful tooltips or additional information', () => {
    render(<DocumentTypeSelection />)
    
    expect(screen.getByText(/ai-powered content generation/i)).toBeInTheDocument()
    expect(screen.getByText(/based on your protocol requirements/i)).toBeInTheDocument()
  })

  it('shows document type comparison', () => {
    render(<DocumentTypeSelection />)
    
    // Should show clear distinctions between document types
    expect(screen.getByText(/for participants/i)).toBeInTheDocument()
    expect(screen.getByText(/for research sites/i)).toBeInTheDocument()
  })

  it('handles protocol with different statuses', () => {
    // Test with processing protocol
    const processingProtocol = createMockProtocol({ status: 'processing' })
    vi.mocked(mockLocation).state = { protocol: processingProtocol }
    
    render(<DocumentTypeSelection />)
    
    expect(screen.getByText(/status: processing/i)).toBeInTheDocument()
    
    // Document generation should still be available
    expect(screen.getByText('Generate ICF')).toBeInTheDocument()
    expect(screen.getByText('Generate Checklist')).toBeInTheDocument()
  })
})