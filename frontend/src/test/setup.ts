/**
 * Test setup file for Vitest
 * 
 * This file is run before each test file and sets up:
 * - Testing Library matchers
 * - MSW (Mock Service Worker) for API mocking
 * - Global test utilities
 */

import '@testing-library/jest-dom'
import { expect, afterEach, beforeAll, afterAll } from 'vitest'
import { cleanup } from '@testing-library/react'
import { setupServer } from 'msw/node'
import { http, HttpResponse } from 'msw'

// Setup MSW server for API mocking
const handlers = [
  // Mock health check endpoints
  http.get('/api/health', () => {
    return HttpResponse.json({ status: 'healthy' })
  }),
  
  http.get('http://localhost:8000/health', () => {
    return HttpResponse.json({ status: 'healthy' })
  }),
  
  // Mock protocols endpoints - both /api and localhost:8000 patterns
  http.get('/api/protocols', () => {
    return HttpResponse.json({
      protocols: [
        {
          id: 'protocol_1',
          study_acronym: 'STUDY-001',
          protocol_title: 'Test Clinical Trial Protocol',
          status: 'processed',
          upload_date: '2024-12-15T12:00:00Z'
        },
        {
          id: 'protocol_2',
          study_acronym: 'STUDY-002',
          protocol_title: 'Test Protocol 2',
          status: 'processed',
          upload_date: '2024-12-14T12:00:00Z'
        },
        {
          id: 'protocol_3',
          study_acronym: 'STUDY-003',
          protocol_title: 'Test Protocol 3',
          status: 'processed',
          upload_date: '2024-12-13T12:00:00Z'
        }
      ]
    })
  }),
  
  http.get('http://localhost:8000/protocols', () => {
    return HttpResponse.json({
      protocols: [
        {
          id: 'protocol_1',
          study_acronym: 'STUDY-001',
          protocol_title: 'Test Clinical Trial Protocol',
          status: 'processed',
          upload_date: '2024-12-15T12:00:00Z'
        },
        {
          id: 'protocol_2',
          study_acronym: 'STUDY-002',
          protocol_title: 'Test Protocol 2',
          status: 'processed',
          upload_date: '2024-12-14T12:00:00Z'
        },
        {
          id: 'protocol_3',
          study_acronym: 'STUDY-003',
          protocol_title: 'Test Protocol 3',
          status: 'processed',
          upload_date: '2024-12-13T12:00:00Z'
        }
      ]
    })
  }),
  
  http.post('/api/protocols', async ({ request }) => {
    const body = await request.json()
    return HttpResponse.json({
      id: `protocol_${Date.now()}`,
      study_acronym: body.study_acronym,
      protocol_title: body.protocol_title,
      status: 'processed',
      upload_date: new Date().toISOString()
    }, { status: 201 })
  }),
  
  http.post('http://localhost:8000/protocols', async ({ request }) => {
    const body = await request.json()
    return HttpResponse.json({
      id: `protocol_${Date.now()}`,
      study_acronym: body.study_acronym,
      protocol_title: body.protocol_title,
      status: 'processed',
      upload_date: new Date().toISOString()
    }, { status: 201 })
  }),
  
  // Mock document generation endpoints
  http.post('/api/generate-document', async ({ request }) => {
    const body = await request.json()
    return HttpResponse.json({
      document_type: body.document_type,
      sections: body.document_type === 'icf' ? {
        title: 'Generated Title',
        purpose: 'Generated Purpose',
        procedures: 'Generated Procedures',
        risks: 'Generated Risks',
        benefits: 'Generated Benefits',
        rights: 'Generated Rights',
        contact: 'Generated Contact Info'
      } : {
        regulatory: 'Generated Regulatory Requirements',
        training: 'Generated Training Requirements',
        equipment: 'Generated Equipment List',
        documentation: 'Generated Documentation Requirements'
      },
      status: 'completed',
      generated_at: new Date().toISOString(),
      word_count: 1500
    })
  }),
  
  // Catch-all for unhandled requests
  http.all('*', ({ request }) => {
    console.warn(`Unhandled ${request.method} request to ${request.url}`)
    return new HttpResponse(null, { status: 404 })
  })
]

const server = setupServer(...handlers)

// Start server before all tests
beforeAll(() => {
  server.listen({ onUnhandledRequest: 'warn' })
})

// Clean up after each test
afterEach(() => {
  cleanup()
  server.resetHandlers()
})

// Close server after all tests
afterAll(() => {
  server.close()
})

// Export server for test-specific handler overrides
export { server }