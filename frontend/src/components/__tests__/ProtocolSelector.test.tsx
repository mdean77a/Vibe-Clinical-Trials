/**
 * Unit tests for ProtocolSelector component
 * 
 * Tests protocol selection functionality including:
 * - Protocol list display
 * - Protocol selection
 * - Empty states
 * - User interactions
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'

import { render, createMockProtocols } from '../../test/test-utils'
import ProtocolSelector from '../ProtocolSelector'

describe('ProtocolSelector', () => {
  const mockOnProtocolSelect = vi.fn()
  const mockOnUploadNew = vi.fn()
  const mockProtocols = createMockProtocols(3)

  beforeEach(() => {
    mockOnProtocolSelect.mockClear()
    mockOnUploadNew.mockClear()
  })

  it('renders protocol selector with empty protocols', () => {
    render(
      <ProtocolSelector 
        protocols={[]} 
        onProtocolSelect={mockOnProtocolSelect} 
        onUploadNew={mockOnUploadNew}
      />
    )
    
    expect(screen.getByText(/no existing protocols found/i)).toBeInTheDocument()
    expect(screen.getByText(/upload new protocol/i)).toBeInTheDocument()
  })

  it('displays list of protocols when dropdown is opened', async () => {
    const user = userEvent.setup()
    
    render(
      <ProtocolSelector 
        protocols={mockProtocols} 
        onProtocolSelect={mockOnProtocolSelect} 
        onUploadNew={mockOnUploadNew}
      />
    )

    // Click dropdown to open it
    const dropdown = screen.getByRole('button', { name: /select a protocol/i })
    await user.click(dropdown)

    expect(screen.getByText('STUDY-001')).toBeInTheDocument()
    expect(screen.getByText('STUDY-002')).toBeInTheDocument()
    expect(screen.getByText('STUDY-003')).toBeInTheDocument()
  })

  it('handles protocol selection correctly', async () => {
    const user = userEvent.setup()
    
    render(
      <ProtocolSelector 
        protocols={mockProtocols} 
        onProtocolSelect={mockOnProtocolSelect} 
        onUploadNew={mockOnUploadNew}
      />
    )

    // Open dropdown
    const dropdown = screen.getByRole('button', { name: /select a protocol/i })
    await user.click(dropdown)

    // Click on first protocol
    const firstProtocol = screen.getByText('STUDY-001')
    await user.click(firstProtocol)

    expect(mockOnProtocolSelect).toHaveBeenCalledWith(mockProtocols[0])
  })

  it('handles upload new protocol button click', async () => {
    const user = userEvent.setup()
    
    render(
      <ProtocolSelector 
        protocols={mockProtocols} 
        onProtocolSelect={mockOnProtocolSelect} 
        onUploadNew={mockOnUploadNew}
      />
    )

    const uploadButton = screen.getByRole('button', { name: /upload new protocol/i })
    await user.click(uploadButton)

    expect(mockOnUploadNew).toHaveBeenCalledTimes(1)
  })

  it('shows protocol details in dropdown', async () => {
    const user = userEvent.setup()
    
    render(
      <ProtocolSelector 
        protocols={mockProtocols} 
        onProtocolSelect={mockOnProtocolSelect} 
        onUploadNew={mockOnUploadNew}
      />
    )

    // Open dropdown
    const dropdown = screen.getByRole('button', { name: /select a protocol/i })
    await user.click(dropdown)

    // Check protocol details are displayed
    expect(screen.getByText('Test Protocol 1')).toBeInTheDocument()
    expect(screen.getByText('Test Protocol 2')).toBeInTheDocument()
    expect(screen.getByText('Test Protocol 3')).toBeInTheDocument()
  })

  it('disables dropdown when no protocols available', () => {
    render(
      <ProtocolSelector 
        protocols={[]} 
        onProtocolSelect={mockOnProtocolSelect} 
        onUploadNew={mockOnUploadNew}
      />
    )

    const dropdown = screen.getByRole('button', { name: /no existing protocols found/i })
    expect(dropdown).toBeDisabled()
  })

  it('shows correct UI structure', () => {
    render(
      <ProtocolSelector 
        protocols={mockProtocols} 
        onProtocolSelect={mockOnProtocolSelect} 
        onUploadNew={mockOnUploadNew}
      />
    )

    expect(screen.getByText('Select Protocol')).toBeInTheDocument()
    expect(screen.getByText(/choose an existing protocol or upload/i)).toBeInTheDocument()
    expect(screen.getByText('Existing Protocols')).toBeInTheDocument()
    expect(screen.getByText('or')).toBeInTheDocument()
    expect(screen.getByText(/upload a new clinical trial protocol/i)).toBeInTheDocument()
  })

  it('formats dates correctly in protocol list', async () => {
    const user = userEvent.setup()
    const protocolWithSpecificDate = [{
      ...mockProtocols[0],
      upload_date: '2024-12-15T12:00:00Z'
    }]
    
    render(
      <ProtocolSelector 
        protocols={protocolWithSpecificDate} 
        onProtocolSelect={mockOnProtocolSelect} 
        onUploadNew={mockOnUploadNew}
      />
    )

    // Open dropdown
    const dropdown = screen.getByRole('button', { name: /select a protocol/i })
    await user.click(dropdown)

    // Check that date is formatted
    expect(screen.getByText(/Dec 15, 2024/)).toBeInTheDocument()
  })

  it('handles keyboard navigation', async () => {
    const user = userEvent.setup()
    
    render(
      <ProtocolSelector 
        protocols={mockProtocols} 
        onProtocolSelect={mockOnProtocolSelect} 
        onUploadNew={mockOnUploadNew}
      />
    )

    // Tab to dropdown button
    await user.tab()
    
    // Check focus is on dropdown
    const dropdown = screen.getByRole('button', { name: /select a protocol/i })
    expect(dropdown).toHaveFocus()

    // Press Enter to open dropdown
    await user.keyboard('{Enter}')
    
    // Tab to first protocol and press Enter
    await user.tab()
    await user.keyboard('{Enter}')

    expect(mockOnProtocolSelect).toHaveBeenCalledWith(mockProtocols[0])
  })
})