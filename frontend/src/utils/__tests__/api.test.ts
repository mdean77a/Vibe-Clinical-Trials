/**
 * Unit tests for API utility functions
 * 
 * Tests API interactions including:
 * - HTTP request handling
 * - Error handling and retries
 * - Data transformation
 * - Authentication (if applicable)
 * - Response parsing
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { server } from '../../test/setup'
import { http, HttpResponse } from 'msw'

import {
  fetchProtocols,
  createProtocol,
  getProtocolById,
  updateProtocolStatus,
  deleteProtocol,
  generateDocument,
  ApiError
} from '../api'
import { createMockProtocol, createMockProtocols, createMockDocument } from '../../test/test-utils'

describe('API Utils', () => {
  beforeEach(() => {
    server.resetHandlers()
  })

  describe('fetchProtocols', () => {
    it('fetches protocols successfully', async () => {
      const mockProtocols = createMockProtocols(3)
      
      server.use(
        http.get('/api/protocols/', () => {
          return HttpResponse.json(mockProtocols)
        })
      )

      const result = await fetchProtocols()
      expect(result).toEqual(mockProtocols)
    })

    it('handles empty protocol list', async () => {
      server.use(
        http.get('/api/protocols/', () => {
          return HttpResponse.json([])
        })
      )

      const result = await fetchProtocols()
      expect(result).toEqual([])
    })

    it('handles API errors', async () => {
      server.use(
        http.get('/api/protocols/', () => {
          return new HttpResponse(null, { status: 500 })
        })
      )

      await expect(fetchProtocols()).rejects.toThrow(ApiError)
    })

    it('supports status filtering', async () => {
      const completedProtocols = createMockProtocols(2).map(p => ({ ...p, status: 'completed' as const }))
      
      server.use(
        http.get('/api/protocols/', ({ request }) => {
          const url = new URL(request.url)
          const status = url.searchParams.get('status')
          
          if (status === 'completed') {
            return HttpResponse.json(completedProtocols)
          }
          
          return HttpResponse.json(createMockProtocols(5))
        })
      )

      const result = await fetchProtocols('completed')
      expect(result).toEqual(completedProtocols)
      expect(result.every(p => p.status === 'completed')).toBe(true)
    })

    it('handles network errors', async () => {
      server.use(
        http.get('/api/protocols/', () => {
          return HttpResponse.error()
        })
      )

      await expect(fetchProtocols()).rejects.toThrow()
    })
  })

  describe('createProtocol', () => {
    it('creates protocol successfully', async () => {
      const protocolData = {
        study_acronym: 'TEST-001',
        protocol_title: 'Test Protocol',
        file: new File([''], 'protocol.pdf', { type: 'application/pdf' })
      }

      const expectedResponse = {
        id: 1,
        study_acronym: 'TEST-001',
        protocol_title: 'Test Protocol',
        status: 'processing' as const,
        upload_date: '2024-12-15T12:00:00Z',
        document_id: 'test-doc-id'
      }

      server.use(
        http.post('/api/protocols/', async ({ request }) => {
          const formData = await request.formData()
          expect(formData.get('study_acronym')).toBe('TEST-001')
          expect(formData.get('protocol_title')).toBe('Test Protocol')
          expect(formData.get('file')).toBeInstanceOf(File)
          
          return HttpResponse.json(expectedResponse, { status: 201 })
        })
      )

      const result = await createProtocol(protocolData)
      expect(result).toEqual(expectedResponse)
    })

    it('handles validation errors', async () => {
      const protocolData = {
        study_acronym: '',
        protocol_title: 'Test Protocol',
        file: new File([''], 'protocol.pdf', { type: 'application/pdf' })
      }

      server.use(
        http.post('/api/protocols/', () => {
          return HttpResponse.json(
            { error: 'Study acronym is required' }, 
            { status: 400 }
          )
        })
      )

      await expect(createProtocol(protocolData)).rejects.toThrow(ApiError)
    })

    it('handles file size errors', async () => {
      const protocolData = {
        study_acronym: 'TEST-001',
        protocol_title: 'Test Protocol',
        file: new File(['x'.repeat(15 * 1024 * 1024)], 'large.pdf', { type: 'application/pdf' })
      }

      server.use(
        http.post('/api/protocols/', () => {
          return HttpResponse.json(
            { error: 'File size exceeds limit' }, 
            { status: 413 }
          )
        })
      )

      await expect(createProtocol(protocolData)).rejects.toThrow(ApiError)
    })

    it('handles server errors', async () => {
      const protocolData = {
        study_acronym: 'TEST-001',
        protocol_title: 'Test Protocol',
        file: new File([''], 'protocol.pdf', { type: 'application/pdf' })
      }

      server.use(
        http.post('/api/protocols/', () => {
          return new HttpResponse(null, { status: 500 })
        })
      )

      await expect(createProtocol(protocolData)).rejects.toThrow(ApiError)
    })
  })

  describe('getProtocolById', () => {
    it('fetches protocol by ID successfully', async () => {
      const mockProtocol = createMockProtocol()
      
      server.use(
        http.get('/api/protocols/:id', ({ params }) => {
          expect(params.id).toBe('1')
          return HttpResponse.json(mockProtocol)
        })
      )

      const result = await getProtocolById(1)
      expect(result).toEqual(mockProtocol)
    })

    it('handles protocol not found', async () => {
      server.use(
        http.get('/api/protocols/:id', () => {
          return new HttpResponse(null, { status: 404 })
        })
      )

      await expect(getProtocolById(999)).rejects.toThrow(ApiError)
    })

    it('handles invalid ID format', async () => {
      await expect(getProtocolById(-1)).rejects.toThrow()
    })
  })

  describe('updateProtocolStatus', () => {
    it('updates protocol status successfully', async () => {
      const updatedProtocol = { ...createMockProtocol(), status: 'completed' as const }
      
      server.use(
        http.patch('/api/protocols/:id/status', async ({ params, request }) => {
          expect(params.id).toBe('1')
          const body = await request.json()
          expect(body.status).toBe('completed')
          
          return HttpResponse.json(updatedProtocol)
        })
      )

      const result = await updateProtocolStatus(1, 'completed')
      expect(result).toEqual(updatedProtocol)
    })

    it('handles invalid status values', async () => {
      server.use(
        http.patch('/api/protocols/:id/status', () => {
          return HttpResponse.json(
            { error: 'Invalid status value' }, 
            { status: 400 }
          )
        })
      )

      await expect(updateProtocolStatus(1, 'invalid' as any)).rejects.toThrow(ApiError)
    })
  })

  describe('deleteProtocol', () => {
    it('deletes protocol successfully', async () => {
      server.use(
        http.delete('/api/protocols/:id', ({ params }) => {
          expect(params.id).toBe('1')
          return new HttpResponse(null, { status: 204 })
        })
      )

      await expect(deleteProtocol(1)).resolves.toBeUndefined()
    })

    it('handles protocol not found during deletion', async () => {
      server.use(
        http.delete('/api/protocols/:id', () => {
          return new HttpResponse(null, { status: 404 })
        })
      )

      await expect(deleteProtocol(999)).rejects.toThrow(ApiError)
    })
  })

  describe('generateDocument', () => {
    it('generates ICF document successfully', async () => {
      const mockDocument = createMockDocument('icf')
      
      server.use(
        http.post('/api/generate-document', async ({ request }) => {
          const body = await request.json()
          expect(body.document_type).toBe('icf')
          expect(body.protocol_id).toBe(1)
          
          return HttpResponse.json(mockDocument)
        })
      )

      const result = await generateDocument('icf', 1)
      expect(result).toEqual(mockDocument)
    })

    it('generates site checklist document successfully', async () => {
      const mockDocument = createMockDocument('site_checklist')
      
      server.use(
        http.post('/api/generate-document', async ({ request }) => {
          const body = await request.json()
          expect(body.document_type).toBe('site_checklist')
          expect(body.protocol_id).toBe(1)
          
          return HttpResponse.json(mockDocument)
        })
      )

      const result = await generateDocument('site_checklist', 1)
      expect(result).toEqual(mockDocument)
    })

    it('handles generation failures', async () => {
      server.use(
        http.post('/api/generate-document', () => {
          return HttpResponse.json(
            { error: 'Generation failed' }, 
            { status: 500 }
          )
        })
      )

      await expect(generateDocument('icf', 1)).rejects.toThrow(ApiError)
    })

    it('handles invalid document types', async () => {
      await expect(generateDocument('invalid' as any, 1)).rejects.toThrow()
    })

    it('supports custom generation options', async () => {
      const options = {
        template: 'comprehensive',
        language: 'en',
        compliance_level: 'ich-gcp'
      }

      server.use(
        http.post('/api/generate-document', async ({ request }) => {
          const body = await request.json()
          expect(body.options).toEqual(options)
          
          return HttpResponse.json(createMockDocument('icf'))
        })
      )

      const result = await generateDocument('icf', 1, options)
      expect(result).toBeDefined()
    })
  })

  describe('ApiError', () => {
    it('creates error with correct properties', () => {
      const error = new ApiError('Test error', 400, 'BAD_REQUEST')
      
      expect(error.message).toBe('Test error')
      expect(error.status).toBe(400)
      expect(error.code).toBe('BAD_REQUEST')
      expect(error.name).toBe('ApiError')
    })

    it('is instanceof Error', () => {
      const error = new ApiError('Test error', 500)
      expect(error).toBeInstanceOf(Error)
      expect(error).toBeInstanceOf(ApiError)
    })
  })

  describe('Request timeout handling', () => {
    it('handles request timeouts', async () => {
      server.use(
        http.get('/api/protocols/', () => {
          // Simulate slow response
          return new Promise(() => {}) // Never resolves
        })
      )

      const timeoutPromise = new Promise((_, reject) => {
        setTimeout(() => reject(new Error('Request timeout')), 100)
      })

      await expect(Promise.race([fetchProtocols(), timeoutPromise])).rejects.toThrow('Request timeout')
    })
  })

  describe('Request retries', () => {
    it('retries failed requests', async () => {
      let callCount = 0
      
      server.use(
        http.get('/api/protocols/', () => {
          callCount++
          if (callCount < 3) {
            return new HttpResponse(null, { status: 500 })
          }
          return HttpResponse.json(createMockProtocols(1))
        })
      )

      // Note: This test assumes retry logic is implemented in the API utils
      // If not implemented, this test should be updated or the retry logic should be added
      const result = await fetchProtocols()
      expect(result).toHaveLength(1)
      expect(callCount).toBe(3)
    })
  })

  describe('Content-Type handling', () => {
    it('sends correct Content-Type for JSON requests', async () => {
      server.use(
        http.post('/api/generate-document', ({ request }) => {
          expect(request.headers.get('Content-Type')).toBe('application/json')
          return HttpResponse.json(createMockDocument('icf'))
        })
      )

      await generateDocument('icf', 1)
    })

    it('sends correct Content-Type for form data requests', async () => {
      const protocolData = {
        study_acronym: 'TEST-001',
        protocol_title: 'Test Protocol',
        file: new File([''], 'protocol.pdf', { type: 'application/pdf' })
      }

      server.use(
        http.post('/api/protocols/', ({ request }) => {
          // FormData automatically sets the correct Content-Type with boundary
          expect(request.headers.get('Content-Type')).toContain('multipart/form-data')
          return HttpResponse.json(createMockProtocol(), { status: 201 })
        })
      )

      await createProtocol(protocolData)
    })
  })
})