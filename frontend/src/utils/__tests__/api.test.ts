/**
 * @jest-environment jsdom
 */

import { describe, it, expect, beforeEach } from 'vitest'
import { server } from '../../test/setup'
import { http, HttpResponse } from 'msw'

import {
  protocolsApi,
  healthApi,
  getApiUrl,
  apiRequest
} from '../api'

// Mock data
const createMockProtocol = () => ({
  protocol_id: 'proto_123',
  study_acronym: 'TEST-001',
  protocol_title: 'Test Protocol',
  collection_name: 'test_collection',
  upload_date: '2024-01-01T00:00:00Z',
  status: 'processed',
  file_path: 'test.pdf',
  created_at: '2024-01-01T00:00:00Z'
})

const createMockProtocols = (count: number) => 
  Array.from({ length: count }, (_, i) => ({
    ...createMockProtocol(),
    protocol_id: `proto_${i + 1}`,
    study_acronym: `TEST-${String(i + 1).padStart(3, '0')}`
  }))

describe('API Utils', () => {
  beforeEach(() => {
    server.resetHandlers()
  })

  describe('getApiUrl', () => {
    it('constructs API URLs correctly', () => {
      const url = getApiUrl('protocols')
      expect(url).toMatch(/\/protocols$/)
    })

    it('handles leading slashes', () => {
      const url = getApiUrl('/protocols')
      expect(url).toMatch(/\/protocols$/)
    })
  })

  describe('protocolsApi.list', () => {
    it('fetches protocols successfully', async () => {
      const mockProtocols = createMockProtocols(3)
      
      server.use(
        http.get('*/protocols', () => {
          return HttpResponse.json(mockProtocols)
        })
      )

      const result = await protocolsApi.list()
      expect(result).toEqual(mockProtocols)
    })

    it('handles empty protocol list', async () => {
      server.use(
        http.get('*/protocols', () => {
          return HttpResponse.json([])
        })
      )

      const result = await protocolsApi.list()
      expect(result).toEqual([])
    })

    it('handles API errors', async () => {
      server.use(
        http.get('*/protocols', () => {
          return new HttpResponse(null, { status: 500 })
        })
      )

      await expect(protocolsApi.list()).rejects.toThrow()
    })

    it('supports status filtering', async () => {
      const completedProtocols = createMockProtocols(2).map(p => ({ ...p, status: 'completed' }))
      
      server.use(
        http.get('*/protocols', ({ request }) => {
          const url = new URL(request.url)
          const status = url.searchParams.get('status_filter')
          
          if (status === 'completed') {
            return HttpResponse.json(completedProtocols)
          }
          
          return HttpResponse.json(createMockProtocols(5))
        })
      )

      const completedResult = await protocolsApi.list('completed')
      expect(completedResult).toEqual(completedProtocols)
      expect(completedResult).toHaveLength(2)

      const allResult = await protocolsApi.list()
      expect(allResult).toHaveLength(5)
    })
  })

  describe('protocolsApi.create', () => {
    it('creates protocol successfully', async () => {
      const newProtocol = createMockProtocol()
      const protocolData = {
        study_acronym: 'TEST-001',
        protocol_title: 'Test Protocol'
      }
      
      server.use(
        http.post('*/protocols', async ({ request }) => {
          const body = await request.json()
          expect(body).toEqual(protocolData)
          return HttpResponse.json(newProtocol, { status: 201 })
        })
      )

      const result = await protocolsApi.create(protocolData)
      expect(result).toEqual(newProtocol)
    })

    it('handles creation errors', async () => {
      server.use(
        http.post('*/protocols', () => {
          return HttpResponse.json(
            { detail: 'Protocol already exists' },
            { status: 400 }
          )
        })
      )

      const protocolData = {
        study_acronym: 'TEST-001',
        protocol_title: 'Test Protocol'
      }

      await expect(protocolsApi.create(protocolData)).rejects.toThrow()
    })
  })

  describe('protocolsApi.upload', () => {
    it('uploads protocol file successfully', async () => {
      const mockProtocol = createMockProtocol()
      const file = new File(['test content'], 'test.pdf', { type: 'application/pdf' })
      const protocolData = {
        study_acronym: 'TEST-001',
        protocol_title: 'Test Protocol'
      }
      
      server.use(
        http.post('*/upload-protocol', async ({ request }) => {
          // Verify it's a FormData request
          expect(request.headers.get('content-type')).toContain('multipart/form-data')
          return HttpResponse.json({ success: true, protocol: mockProtocol })
        })
      )

      const result = await protocolsApi.upload(file, protocolData)
      expect(result.success).toBe(true)
      expect(result.protocol).toEqual(mockProtocol)
    })

    it('handles upload errors', async () => {
      const file = new File(['test content'], 'test.pdf', { type: 'application/pdf' })
      const protocolData = {
        study_acronym: 'TEST-001',
        protocol_title: 'Test Protocol'
      }
      
      server.use(
        http.post('*/upload-protocol', () => {
          return HttpResponse.json(
            { success: false, error: 'File too large' },
            { status: 400 }
          )
        })
      )

      await expect(protocolsApi.upload(file, protocolData)).rejects.toThrow()
    })
  })

  describe('protocolsApi.getById', () => {
    it('fetches protocol by ID successfully', async () => {
      const mockProtocol = createMockProtocol()
      
      server.use(
        http.get('*/protocols/123', () => {
          return HttpResponse.json(mockProtocol)
        })
      )

      const result = await protocolsApi.getById(123)
      expect(result).toEqual(mockProtocol)
    })

    it('handles not found errors', async () => {
      server.use(
        http.get('*/protocols/999', () => {
          return HttpResponse.json(
            { detail: 'Protocol not found' },
            { status: 404 }
          )
        })
      )

      await expect(protocolsApi.getById(999)).rejects.toThrow()
    })
  })

  describe('protocolsApi.updateStatus', () => {
    it('updates protocol status successfully', async () => {
      const updatedProtocol = { ...createMockProtocol(), status: 'completed' }
      
      server.use(
        http.patch('*/protocols/123/status', async ({ request }) => {
          const body = await request.json()
          expect(body).toEqual({ status: 'completed' })
          return HttpResponse.json(updatedProtocol)
        })
      )

      const result = await protocolsApi.updateStatus(123, 'completed')
      expect(result).toEqual(updatedProtocol)
    })
  })

  describe('protocolsApi.delete', () => {
    it('deletes protocol successfully', async () => {
      server.use(
        http.delete('*/protocols/123', () => {
          return new HttpResponse(null, { status: 204 })
        })
      )

      const result = await protocolsApi.delete(123)
      expect(result).toEqual({})
    })
  })

  describe('healthApi', () => {
    it('checks health successfully', async () => {
      const healthResponse = { status: 'healthy', database: 'connected' }
      
      server.use(
        http.get('*/health', () => {
          return HttpResponse.json(healthResponse)
        })
      )

      const result = await healthApi.check()
      expect(result).toEqual(healthResponse)
    })

    it('gets root information', async () => {
      const rootResponse = { message: 'Clinical Trial Accelerator API' }
      
      server.use(
        http.get('*/', () => {
          return HttpResponse.json(rootResponse)
        })
      )

      const result = await healthApi.root()
      expect(result).toEqual(rootResponse)
    })
  })

  describe('apiRequest', () => {
    it('handles successful requests', async () => {
      const mockData = { message: 'success' }
      
      server.use(
        http.get('*/test', () => {
          return HttpResponse.json(mockData)
        })
      )

      const result = await apiRequest('test')
      expect(result).toEqual(mockData)
    })

    it('handles 204 No Content responses', async () => {
      server.use(
        http.delete('*/test', () => {
          return new HttpResponse(null, { status: 204 })
        })
      )

      const result = await apiRequest('test', { method: 'DELETE' })
      expect(result).toEqual({})
    })

    it('handles error responses', async () => {
      server.use(
        http.get('*/test', () => {
          return HttpResponse.json(
            { detail: 'Something went wrong' },
            { status: 500 }
          )
        })
      )

      await expect(apiRequest('test')).rejects.toThrow('Something went wrong')
    })
  })
})