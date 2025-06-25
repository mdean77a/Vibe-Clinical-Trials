/**
 * Custom test utilities for React components
 * 
 * This module provides:
 * - Custom render function with providers
 * - Common test data factories
 * - Helper functions for testing
 */

import { ReactElement } from 'react'
import { render, RenderOptions } from '@testing-library/react'

// Custom render function that includes providers
const AllTheProviders = ({ children }: { children: React.ReactNode }) => {
  return (
    <>
      {children}
    </>
  )
}

const customRender = (
  ui: ReactElement,
  options?: Omit<RenderOptions, 'wrapper'>
) => render(ui, { wrapper: AllTheProviders, ...options })

// Re-export everything from testing-library
export * from '@testing-library/react'

// Override render method
export { customRender as render }

// Test data factories
export const createMockProtocol = (overrides = {}) => ({
  id: 1,
  study_acronym: 'STUDY-001',
  protocol_title: 'Test Clinical Trial Protocol',
  status: 'completed' as const,
  upload_date: '2024-12-15T12:00:00Z',
  document_id: 'test-document-id',
  ...overrides
})

export const createMockProtocols = (count = 3) => 
  Array.from({ length: count }, (_, i) => 
    createMockProtocol({
      id: i + 1,
      study_acronym: `STUDY-${String(i + 1).padStart(3, '0')}`,
      protocol_title: `Test Protocol ${i + 1}`
    })
  )

export const createMockDocument = (type: 'icf' | 'site_checklist', overrides = {}) => ({
  document_type: type,
  sections: {
    title: 'Generated Title',
    purpose: 'Generated Purpose',
    procedures: 'Generated Procedures',
    ...(type === 'icf' && {
      risks: 'Generated Risks',
      benefits: 'Generated Benefits',
      rights: 'Generated Rights',
      contact: 'Generated Contact'
    }),
    ...(type === 'site_checklist' && {
      regulatory: 'Generated Regulatory Requirements',
      training: 'Generated Training Requirements',
      equipment: 'Generated Equipment List',
      documentation: 'Generated Documentation Requirements'
    })
  },
  status: 'completed',
  ...overrides
})

// Helper functions for common test scenarios
export const waitForLoadingToFinish = async () => {
  const { waitForElementToBeRemoved, queryByText } = await import('@testing-library/react')
  
  try {
    await waitForElementToBeRemoved(() => queryByText(/loading/i), { timeout: 3000 })
  } catch {
    // Loading element might not exist, which is fine
  }
}

export const fillProtocolForm = async (user: any, protocolData: any) => {
  const { screen } = await import('@testing-library/react')
  
  const acronymInput = screen.getByLabelText(/study acronym/i)
  const titleInput = screen.getByLabelText(/protocol title/i)
  
  await user.clear(acronymInput)
  await user.type(acronymInput, protocolData.study_acronym)
  
  await user.clear(titleInput)
  await user.type(titleInput, protocolData.protocol_title)
}

export const expectProtocolInList = (protocols: any[], expectedProtocol: any) => {
  const protocol = protocols.find(p => p.study_acronym === expectedProtocol.study_acronym)
  expect(protocol).toBeDefined()
  expect(protocol?.protocol_title).toBe(expectedProtocol.protocol_title)
  expect(protocol?.status).toBe(expectedProtocol.status)
}