import React, { ReactElement } from 'react'
import { render, RenderOptions } from '@testing-library/react'

// Custom render function that includes providers
const AllTheProviders = ({ children }: { children: React.ReactNode }) => {
  return <>{children}</>
}

const customRender = (
  ui: ReactElement,
  options?: Omit<RenderOptions, 'wrapper'>
) => render(ui, { wrapper: AllTheProviders, ...options })

export * from '@testing-library/react'
export { customRender as render }

// Mock data factories
export const mockProtocol = {
  id: 'test-protocol-1',
  title: 'Test Clinical Trial Protocol',
  description: 'A test protocol for unit testing',
  upload_date: '2024-01-15T10:30:00Z',
  file_name: 'test-protocol.pdf',
  study_phase: 'Phase II',
  indication: 'Oncology',
  sponsor: 'Test Pharmaceutical Inc.',
}

export const mockDocument = {
  id: 'test-doc-1',
  protocol_id: 'test-protocol-1',
  document_type: 'informed_consent',
  title: 'Informed Consent Form',
  status: 'draft' as const,
  created_at: '2024-01-15T11:00:00Z',
  sections: [
    {
      id: 'section-1',
      title: 'Study Purpose',
      content: 'This study aims to test the effectiveness of...',
      order: 1,
    },
    {
      id: 'section-2', 
      title: 'Risks and Benefits',
      content: 'The potential risks include...',
      order: 2,
    },
  ],
}

// Helper functions for common test scenarios
export const waitForLoadingToFinish = () => {
  return new Promise(resolve => setTimeout(resolve, 0))
}

export const mockStreamingResponse = (content: string, delay: number = 100) => {
  return new Promise<string>((resolve) => {
    setTimeout(() => resolve(content), delay)
  })
}