/**
 * Integration tests for App component
 * 
 * Tests application-level functionality including:
 * - Routing and navigation
 * - Full user workflows
 * - Error boundaries
 * - Performance considerations
 */

import { describe, it, expect, vi } from 'vitest'
import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'

import { render } from '../test/test-utils'
import App from '../App'

// Note: These tests are currently disabled as they were written for React Router
// In a Next.js app, routing is handled differently through the file system
// TODO: Rewrite these tests to work with Next.js routing

const renderApp = () => {
  return render(<App />)
}

describe('App Integration Tests', () => {
  it('renders home page by default', () => {
    renderApp()
    
    expect(screen.getByText('Clinical Trial Accelerator')).toBeInTheDocument()
    expect(screen.getByText(/ai-powered document generation/i)).toBeInTheDocument()
  })

  it.skip('navigates through complete ICF generation workflow', async () => {
    const user = userEvent.setup()
    
    renderApp()
    
    // Start at home page
    expect(screen.getByText('Clinical Trial Accelerator')).toBeInTheDocument()
    
    // Wait for protocols to load and select one
    await waitFor(() => {
      expect(screen.getByRole('button', { name: /select a protocol/i })).toBeInTheDocument()
    })
    
    const dropdown = screen.getByRole('button', { name: /select a protocol/i })
    await user.click(dropdown)
    
    const firstProtocol = screen.getByText('STUDY-001')
    await user.click(firstProtocol)
    
    // Continue to document selection
    const continueButton = screen.getByRole('button', { name: /continue to document selection/i })
    await user.click(continueButton)
    
    // Should be on document selection page
    await waitFor(() => {
      expect(screen.getByText('Select Document Type')).toBeInTheDocument()
    })
    
    // Select ICF generation
    const icfButton = screen.getByText('Generate ICF').closest('button')
    await user.click(icfButton!)
    
    // Should be on ICF generation page
    await waitFor(() => {
      expect(screen.getByText('Generate Informed Consent Form')).toBeInTheDocument()
    })
    
    // Start generation
    const generateButton = screen.getByRole('button', { name: /generate informed consent form/i })
    await user.click(generateButton)
    
    // Should see generation progress
    expect(screen.getByText(/generating your informed consent form/i)).toBeInTheDocument()
    
    // Wait for completion
    await waitFor(() => {
      expect(screen.getByText('Study Title')).toBeInTheDocument()
      expect(screen.getByText('Purpose')).toBeInTheDocument()
    }, { timeout: 5000 })
  })

  it.skip('navigates through complete site checklist workflow', async () => {
    const user = userEvent.setup()
    
    renderApp()
    
    // Navigate to protocol selection and continue to document selection
    await waitFor(() => {
      expect(screen.getByRole('button', { name: /select a protocol/i })).toBeInTheDocument()
    })
    
    const dropdown = screen.getByRole('button', { name: /select a protocol/i })
    await user.click(dropdown)
    
    const firstProtocol = screen.getByText('STUDY-001')
    await user.click(firstProtocol)
    
    const continueButton = screen.getByRole('button', { name: /continue to document selection/i })
    await user.click(continueButton)
    
    await waitFor(() => {
      expect(screen.getByText('Select Document Type')).toBeInTheDocument()
    })
    
    // Select site checklist generation
    const checklistButton = screen.getByText('Generate Checklist').closest('button')
    await user.click(checklistButton!)
    
    // Should be on site checklist page
    await waitFor(() => {
      expect(screen.getByText('Generate Site Initiation Checklist')).toBeInTheDocument()
    })
    
    // Start generation
    const generateButton = screen.getByRole('button', { name: /generate site checklist/i })
    await user.click(generateButton)
    
    // Should see generation progress
    expect(screen.getByText(/generating your site initiation checklist/i)).toBeInTheDocument()
    
    // Wait for completion
    await waitFor(() => {
      expect(screen.getByText('Regulatory Requirements')).toBeInTheDocument()
      expect(screen.getByText('Training Requirements')).toBeInTheDocument()
    }, { timeout: 5000 })
  })

  it.skip('handles protocol upload workflow', async () => {
    const user = userEvent.setup()
    
    renderApp()
    
    // Click upload new protocol
    await waitFor(() => {
      expect(screen.getByRole('button', { name: /upload new protocol/i })).toBeInTheDocument()
    })
    
    const uploadButton = screen.getByRole('button', { name: /upload new protocol/i })
    await user.click(uploadButton)
    
    // Should show upload form
    expect(screen.getByText('Upload Protocol')).toBeInTheDocument()
    expect(screen.getByLabelText(/study acronym/i)).toBeInTheDocument()
    
    // Fill upload form
    await user.type(screen.getByLabelText(/study acronym/i), 'NEW-001')
    await user.type(screen.getByLabelText(/protocol title/i), 'New Test Protocol')
    
    // Upload file
    const file = new File([''], 'protocol.pdf', { type: 'application/pdf' })
    const fileInput = screen.getByLabelText(/choose file/i)
    await user.upload(fileInput, file)
    
    // Submit upload
    const submitButton = screen.getByRole('button', { name: /upload protocol/i })
    await user.click(submitButton)
    
    // Should show success message
    await waitFor(() => {
      expect(screen.getByText(/protocol uploaded successfully/i)).toBeInTheDocument()
    })
  })

  it.skip('handles navigation back and forth correctly', async () => {
    const user = userEvent.setup()
    
    renderApp()
    
    // Navigate forward through the flow
    await waitFor(() => {
      expect(screen.getByRole('button', { name: /select a protocol/i })).toBeInTheDocument()
    })
    
    const dropdown = screen.getByRole('button', { name: /select a protocol/i })
    await user.click(dropdown)
    
    const firstProtocol = screen.getByText('STUDY-001')
    await user.click(firstProtocol)
    
    const continueButton = screen.getByRole('button', { name: /continue to document selection/i })
    await user.click(continueButton)
    
    await waitFor(() => {
      expect(screen.getByText('Select Document Type')).toBeInTheDocument()
    })
    
    // Navigate back to home
    const backButton = screen.getByRole('button', { name: /back to protocol selection/i })
    await user.click(backButton)
    
    // Should be back at home page
    await waitFor(() => {
      expect(screen.getByText('Clinical Trial Accelerator')).toBeInTheDocument()
    })
  })

  it.skip('handles direct URL navigation', async () => {
    // Test direct navigation to document selection page
    window.history.pushState({}, '', '/document-selection')
    
    renderApp()
    
    // Should handle missing protocol state gracefully
    expect(screen.getByText(/no protocol selected/i)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /return to home/i })).toBeInTheDocument()
  })

  it('handles API errors gracefully throughout the app', async () => {
    const user = userEvent.setup()
    
    // Mock API errors
    const { server } = await import('../test/setup')
    const { http, HttpResponse } = await import('msw')
    
    server.use(
      http.get('/api/protocols/', () => {
        return new HttpResponse(null, { status: 500 })
      })
    )
    
    renderApp()
    
    // Should show error state
    await waitFor(() => {
      expect(screen.getByText(/failed to load protocols/i)).toBeInTheDocument()
    })
    
    // Should allow retry
    expect(screen.getByRole('button', { name: /retry/i })).toBeInTheDocument()
  })

  it.skip('maintains application state during navigation', async () => {
    const user = userEvent.setup()
    
    renderApp()
    
    // Select protocol
    await waitFor(() => {
      expect(screen.getByRole('button', { name: /select a protocol/i })).toBeInTheDocument()
    })
    
    const dropdown = screen.getByRole('button', { name: /select a protocol/i })
    await user.click(dropdown)
    
    const firstProtocol = screen.getByText('STUDY-001')
    await user.click(firstProtocol)
    
    // Navigate to document selection
    const continueButton = screen.getByRole('button', { name: /continue to document selection/i })
    await user.click(continueButton)
    
    // Should maintain protocol information
    await waitFor(() => {
      expect(screen.getByText('STUDY-001')).toBeInTheDocument()
      expect(screen.getByText('Test Clinical Trial Protocol')).toBeInTheDocument()
    })
  })

  it.skip('handles browser back/forward buttons correctly', async () => {
    const user = userEvent.setup()
    
    renderApp()
    
    // Navigate forward
    await waitFor(() => {
      expect(screen.getByRole('button', { name: /select a protocol/i })).toBeInTheDocument()
    })
    
    const dropdown = screen.getByRole('button', { name: /select a protocol/i })
    await user.click(dropdown)
    
    const firstProtocol = screen.getByText('STUDY-001')
    await user.click(firstProtocol)
    
    const continueButton = screen.getByRole('button', { name: /continue to document selection/i })
    await user.click(continueButton)
    
    await waitFor(() => {
      expect(screen.getByText('Select Document Type')).toBeInTheDocument()
    })
    
    // Simulate browser back button
    window.history.back()
    
    // Should return to home page
    await waitFor(() => {
      expect(screen.getByText('Clinical Trial Accelerator')).toBeInTheDocument()
    })
  })

  it('displays loading states appropriately', async () => {
    renderApp()
    
    // Should show loading state for protocols
    expect(screen.getByText(/loading protocols/i)).toBeInTheDocument()
    
    // Should eventually show loaded content
    await waitFor(() => {
      expect(screen.queryByText(/loading protocols/i)).not.toBeInTheDocument()
      expect(screen.getByRole('button', { name: /select a protocol/i })).toBeInTheDocument()
    })
  })

  it('handles keyboard navigation throughout the app', async () => {
    const user = userEvent.setup()
    
    renderApp()
    
    await waitFor(() => {
      expect(screen.getByRole('button', { name: /select a protocol/i })).toBeInTheDocument()
    })
    
    // Tab through elements
    await user.tab()
    expect(screen.getByRole('button', { name: /select a protocol/i })).toHaveFocus()
    
    await user.tab()
    expect(screen.getByRole('button', { name: /upload new protocol/i })).toHaveFocus()
    
    // Use keyboard to navigate
    await user.keyboard('{Enter}')
    
    // Should navigate to upload form
    expect(screen.getByText('Upload Protocol')).toBeInTheDocument()
  })

  it('handles mobile-responsive layout', () => {
    // Mock mobile viewport
    Object.defineProperty(window, 'innerWidth', {
      writable: true,
      configurable: true,
      value: 375,
    })
    
    renderApp()
    
    // Should render without layout issues
    expect(screen.getByText('Clinical Trial Accelerator')).toBeInTheDocument()
    
    // Mobile-specific elements should be present
    const mainContent = screen.getByRole('main')
    expect(mainContent).toBeInTheDocument()
  })

  it('provides proper accessibility structure', () => {
    renderApp()
    
    // Should have proper landmark elements
    expect(screen.getByRole('main')).toBeInTheDocument()
    
    // Should have proper heading hierarchy
    const mainHeading = screen.getByRole('heading', { level: 1 })
    expect(mainHeading).toBeInTheDocument()
    
    // Should be keyboard navigable
    const interactiveElements = screen.getAllByRole('button')
    expect(interactiveElements.length).toBeGreaterThan(0)
  })

  it('handles concurrent user actions gracefully', async () => {
    const user = userEvent.setup()
    
    renderApp()
    
    await waitFor(() => {
      expect(screen.getByRole('button', { name: /select a protocol/i })).toBeInTheDocument()
    })
    
    // Simulate rapid clicks
    const dropdown = screen.getByRole('button', { name: /select a protocol/i })
    const uploadButton = screen.getByRole('button', { name: /upload new protocol/i })
    
    // Rapid alternating clicks should not break the app
    await user.click(dropdown)
    await user.click(uploadButton)
    await user.click(dropdown)
    
    // App should still be functional
    expect(screen.getByText('Upload Protocol')).toBeInTheDocument()
  })
})