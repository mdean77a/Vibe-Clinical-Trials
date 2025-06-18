/**
 * Unit tests for ProtocolUpload component
 * 
 * Tests protocol upload functionality including:
 * - File selection and upload
 * - Form validation
 * - Progress indication
 * - Error handling
 * - Success states
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'

import { render } from '../../test/test-utils'
import ProtocolUpload from '../ProtocolUpload'

// Mock file for testing
const createMockFile = (name: string, size: number, type: string) => {
  const file = new File([''], name, { type })
  Object.defineProperty(file, 'size', { value: size })
  return file
}

describe('ProtocolUpload', () => {
  const mockOnUploadSuccess = vi.fn()
  const mockOnUploadError = vi.fn()

  beforeEach(() => {
    mockOnUploadSuccess.mockClear()
    mockOnUploadError.mockClear()
  })

  it('renders upload form correctly', () => {
    render(
      <ProtocolUpload 
        onUploadSuccess={mockOnUploadSuccess}
        onUploadError={mockOnUploadError}
      />
    )
    
    expect(screen.getByText('Upload Protocol')).toBeInTheDocument()
    expect(screen.getByLabelText(/study acronym/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/protocol title/i)).toBeInTheDocument()
    expect(screen.getByText(/drag and drop your pdf file here/i)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /upload protocol/i })).toBeInTheDocument()
  })

  it('handles form input changes', async () => {
    const user = userEvent.setup()
    
    render(
      <ProtocolUpload 
        onUploadSuccess={mockOnUploadSuccess}
        onUploadError={mockOnUploadError}
      />
    )
    
    const acronymInput = screen.getByLabelText(/study acronym/i)
    const titleInput = screen.getByLabelText(/protocol title/i)
    
    await user.type(acronymInput, 'STUDY-123')
    await user.type(titleInput, 'Test Clinical Trial Protocol')
    
    expect(acronymInput).toHaveValue('STUDY-123')
    expect(titleInput).toHaveValue('Test Clinical Trial Protocol')
  })

  it('handles file selection via file input', async () => {
    const user = userEvent.setup()
    const mockFile = createMockFile('protocol.pdf', 1024 * 1024, 'application/pdf')
    
    render(
      <ProtocolUpload 
        onUploadSuccess={mockOnUploadSuccess}
        onUploadError={mockOnUploadError}
      />
    )
    
    const fileInput = screen.getByLabelText(/choose file/i)
    await user.upload(fileInput, mockFile)
    
    expect(screen.getByText('protocol.pdf')).toBeInTheDocument()
    expect(screen.getByText(/1\.0 mb/i)).toBeInTheDocument()
  })

  it('handles file selection via drag and drop', async () => {
    const mockFile = createMockFile('protocol.pdf', 2048 * 1024, 'application/pdf')
    
    render(
      <ProtocolUpload 
        onUploadSuccess={mockOnUploadSuccess}
        onUploadError={mockOnUploadError}
      />
    )
    
    const dropZone = screen.getByText(/drag and drop your pdf file here/i).closest('div')
    
    // Simulate drag and drop
    const dragEvent = new Event('drop', { bubbles: true })
    Object.defineProperty(dragEvent, 'dataTransfer', {
      value: {
        files: [mockFile]
      }
    })
    
    dropZone?.dispatchEvent(dragEvent)
    
    await waitFor(() => {
      expect(screen.getByText('protocol.pdf')).toBeInTheDocument()
      expect(screen.getByText(/2\.0 mb/i)).toBeInTheDocument()
    })
  })

  it('validates required fields before upload', async () => {
    const user = userEvent.setup()
    
    render(
      <ProtocolUpload 
        onUploadSuccess={mockOnUploadSuccess}
        onUploadError={mockOnUploadError}
      />
    )
    
    const uploadButton = screen.getByRole('button', { name: /upload protocol/i })
    await user.click(uploadButton)
    
    expect(screen.getByText(/study acronym is required/i)).toBeInTheDocument()
    expect(screen.getByText(/protocol title is required/i)).toBeInTheDocument()
    expect(screen.getByText(/pdf file is required/i)).toBeInTheDocument()
  })

  it('validates file type (PDF only)', async () => {
    const user = userEvent.setup()
    const invalidFile = createMockFile('document.txt', 1024, 'text/plain')
    
    render(
      <ProtocolUpload 
        onUploadSuccess={mockOnUploadSuccess}
        onUploadError={mockOnUploadError}
      />
    )
    
    const fileInput = screen.getByLabelText(/choose file/i)
    await user.upload(fileInput, invalidFile)
    
    expect(screen.getByText(/only pdf files are allowed/i)).toBeInTheDocument()
  })

  it('validates file size limits', async () => {
    const user = userEvent.setup()
    const largeFile = createMockFile('large-protocol.pdf', 50 * 1024 * 1024, 'application/pdf') // 50MB
    
    render(
      <ProtocolUpload 
        onUploadSuccess={mockOnUploadSuccess}
        onUploadError={mockOnUploadError}
      />
    )
    
    const fileInput = screen.getByLabelText(/choose file/i)
    await user.upload(fileInput, largeFile)
    
    expect(screen.getByText(/file size must be less than 10mb/i)).toBeInTheDocument()
  })

  it('shows upload progress during submission', async () => {
    const user = userEvent.setup()
    const mockFile = createMockFile('protocol.pdf', 1024 * 1024, 'application/pdf')
    
    render(
      <ProtocolUpload 
        onUploadSuccess={mockOnUploadSuccess}
        onUploadError={mockOnUploadError}
      />
    )
    
    // Fill form
    await user.type(screen.getByLabelText(/study acronym/i), 'STUDY-123')
    await user.type(screen.getByLabelText(/protocol title/i), 'Test Protocol')
    await user.upload(screen.getByLabelText(/choose file/i), mockFile)
    
    // Submit form
    const uploadButton = screen.getByRole('button', { name: /upload protocol/i })
    await user.click(uploadButton)
    
    expect(screen.getByText(/uploading/i)).toBeInTheDocument()
    expect(screen.getByRole('progressbar')).toBeInTheDocument()
  })

  it('handles successful upload', async () => {
    const user = userEvent.setup()
    const mockFile = createMockFile('protocol.pdf', 1024 * 1024, 'application/pdf')
    
    render(
      <ProtocolUpload 
        onUploadSuccess={mockOnUploadSuccess}
        onUploadError={mockOnUploadError}
      />
    )
    
    // Fill form
    await user.type(screen.getByLabelText(/study acronym/i), 'STUDY-123')
    await user.type(screen.getByLabelText(/protocol title/i), 'Test Protocol')
    await user.upload(screen.getByLabelText(/choose file/i), mockFile)
    
    // Submit form
    const uploadButton = screen.getByRole('button', { name: /upload protocol/i })
    await user.click(uploadButton)
    
    await waitFor(() => {
      expect(mockOnUploadSuccess).toHaveBeenCalledWith({
        id: 1,
        study_acronym: 'STUDY-123',
        protocol_title: 'Test Protocol',
        status: 'processing',
        upload_date: expect.any(String),
        document_id: 'test-document-id'
      })
    })
  })

  it('handles upload errors', async () => {
    const user = userEvent.setup()
    const mockFile = createMockFile('protocol.pdf', 1024 * 1024, 'application/pdf')
    
    // Mock API error
    const { server } = await import('../../test/setup')
    const { http, HttpResponse } = await import('msw')
    
    server.use(
      http.post('/api/protocols/', () => {
        return new HttpResponse(null, { status: 500 })
      })
    )
    
    render(
      <ProtocolUpload 
        onUploadSuccess={mockOnUploadSuccess}
        onUploadError={mockOnUploadError}
      />
    )
    
    // Fill form
    await user.type(screen.getByLabelText(/study acronym/i), 'STUDY-123')
    await user.type(screen.getByLabelText(/protocol title/i), 'Test Protocol')
    await user.upload(screen.getByLabelText(/choose file/i), mockFile)
    
    // Submit form
    const uploadButton = screen.getByRole('button', { name: /upload protocol/i })
    await user.click(uploadButton)
    
    await waitFor(() => {
      expect(screen.getByText(/upload failed/i)).toBeInTheDocument()
      expect(mockOnUploadError).toHaveBeenCalled()
    })
  })

  it('allows file removal after selection', async () => {
    const user = userEvent.setup()
    const mockFile = createMockFile('protocol.pdf', 1024 * 1024, 'application/pdf')
    
    render(
      <ProtocolUpload 
        onUploadSuccess={mockOnUploadSuccess}
        onUploadError={mockOnUploadError}
      />
    )
    
    // Upload file
    const fileInput = screen.getByLabelText(/choose file/i)
    await user.upload(fileInput, mockFile)
    
    expect(screen.getByText('protocol.pdf')).toBeInTheDocument()
    
    // Remove file
    const removeButton = screen.getByRole('button', { name: /remove file/i })
    await user.click(removeButton)
    
    expect(screen.queryByText('protocol.pdf')).not.toBeInTheDocument()
    expect(screen.getByText(/drag and drop your pdf file here/i)).toBeInTheDocument()
  })

  it('resets form after successful upload', async () => {
    const user = userEvent.setup()
    const mockFile = createMockFile('protocol.pdf', 1024 * 1024, 'application/pdf')
    
    render(
      <ProtocolUpload 
        onUploadSuccess={mockOnUploadSuccess}
        onUploadError={mockOnUploadError}
      />
    )
    
    // Fill and submit form
    await user.type(screen.getByLabelText(/study acronym/i), 'STUDY-123')
    await user.type(screen.getByLabelText(/protocol title/i), 'Test Protocol')
    await user.upload(screen.getByLabelText(/choose file/i), mockFile)
    
    const uploadButton = screen.getByRole('button', { name: /upload protocol/i })
    await user.click(uploadButton)
    
    await waitFor(() => {
      expect(screen.getByLabelText(/study acronym/i)).toHaveValue('')
      expect(screen.getByLabelText(/protocol title/i)).toHaveValue('')
      expect(screen.queryByText('protocol.pdf')).not.toBeInTheDocument()
    })
  })

  it('shows upload requirements and guidelines', () => {
    render(
      <ProtocolUpload 
        onUploadSuccess={mockOnUploadSuccess}
        onUploadError={mockOnUploadError}
      />
    )
    
    expect(screen.getByText(/upload requirements/i)).toBeInTheDocument()
    expect(screen.getByText(/pdf format only/i)).toBeInTheDocument()
    expect(screen.getByText(/maximum file size: 10mb/i)).toBeInTheDocument()
    expect(screen.getByText(/file should contain complete protocol/i)).toBeInTheDocument()
  })

  it('handles drag over and drag leave events', async () => {
    render(
      <ProtocolUpload 
        onUploadSuccess={mockOnUploadSuccess}
        onUploadError={mockOnUploadError}
      />
    )
    
    const dropZone = screen.getByText(/drag and drop your pdf file here/i).closest('div')
    
    // Simulate drag over
    const dragOverEvent = new Event('dragover', { bubbles: true })
    dropZone?.dispatchEvent(dragOverEvent)
    
    expect(dropZone).toHaveClass('border-blue-500', 'bg-blue-50')
    
    // Simulate drag leave
    const dragLeaveEvent = new Event('dragleave', { bubbles: true })
    dropZone?.dispatchEvent(dragLeaveEvent)
    
    expect(dropZone).not.toHaveClass('border-blue-500', 'bg-blue-50')
  })

  it('displays file preview information', async () => {
    const user = userEvent.setup()
    const mockFile = createMockFile('clinical-trial-protocol.pdf', 2.5 * 1024 * 1024, 'application/pdf')
    
    render(
      <ProtocolUpload 
        onUploadSuccess={mockOnUploadSuccess}
        onUploadError={mockOnUploadError}
      />
    )
    
    const fileInput = screen.getByLabelText(/choose file/i)
    await user.upload(fileInput, mockFile)
    
    expect(screen.getByText('clinical-trial-protocol.pdf')).toBeInTheDocument()
    expect(screen.getByText(/2\.5 mb/i)).toBeInTheDocument()
    expect(screen.getByText(/pdf/i)).toBeInTheDocument()
  })
})