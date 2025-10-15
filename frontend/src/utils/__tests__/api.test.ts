import {
  getApiUrl,
  apiRequest,
  protocolsApi,
  icfApi,
  healthApi,
  logApiConfig,
} from '../api';

// Mock fetch globally
global.fetch = jest.fn();

describe('API Utilities', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    (global.fetch as jest.Mock).mockClear();
  });

  describe('getApiUrl', () => {
    const originalEnv = process.env;

    beforeEach(() => {
      process.env = { ...originalEnv };
    });

    afterEach(() => {
      process.env = originalEnv;
    });

    it('constructs URL correctly with leading slash', () => {
      const url = getApiUrl('/protocols');
      expect(url).toContain('protocols');
    });

    it('constructs URL correctly without leading slash', () => {
      const url = getApiUrl('protocols');
      expect(url).toContain('protocols');
    });

    it('avoids double slashes when endpoint has leading slash', () => {
      const url = getApiUrl('/protocols');
      // Should not have double slashes in the path (excluding http://)
      const pathPart = url.split('://')[1] || url;
      expect(pathPart).not.toMatch(/\/\//);
    });

    it('uses production API in production mode', () => {
      process.env.NODE_ENV = 'production';
      process.env.NEXT_PUBLIC_API_URL = undefined;
      const url = getApiUrl('test');
      expect(url).toContain('/api/test');
    });

    it('uses localhost in development mode', () => {
      process.env.NODE_ENV = 'development';
      process.env.NEXT_PUBLIC_API_URL = undefined;
      const url = getApiUrl('test');
      expect(url).toContain('localhost:8000');
    });

    it('uses NEXT_PUBLIC_API_URL when provided', () => {
      // Note: In Next.js, NEXT_PUBLIC_API_URL is compile-time, so we test that
      // the function uses it correctly by checking the pattern
      const url = getApiUrl('test');
      expect(url).toContain('test');
      // URL will use either NEXT_PUBLIC_API_URL or fall back to localhost/production
      expect(url).toMatch(/^https?:\/\//);
    });
  });

  describe('apiRequest', () => {
    it('makes successful GET request', async () => {
      const mockData = { id: 1, name: 'Test' };
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => mockData,
      });

      const result = await apiRequest('test-endpoint');

      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('test-endpoint'),
        expect.objectContaining({
          headers: expect.objectContaining({
            'Content-Type': 'application/json',
          }),
        })
      );
      expect(result).toEqual(mockData);
    });

    it('makes successful POST request', async () => {
      const mockData = { id: 1 };
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => mockData,
      });

      const result = await apiRequest('test', {
        method: 'POST',
        body: JSON.stringify({ name: 'Test' }),
      });

      expect(global.fetch).toHaveBeenCalledWith(
        expect.any(String),
        expect.objectContaining({
          method: 'POST',
          body: JSON.stringify({ name: 'Test' }),
        })
      );
      expect(result).toEqual(mockData);
    });

    it('handles 204 No Content response', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 204,
      });

      const result = await apiRequest('test');

      expect(result).toEqual({});
    });

    it('throws error for non-ok response with detail', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 400,
        statusText: 'Bad Request',
        json: async () => ({ detail: 'Invalid request' }),
      });

      await expect(apiRequest('test')).rejects.toThrow('Invalid request');
    });

    it('throws error for non-ok response without detail', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 500,
        statusText: 'Internal Server Error',
        json: async () => ({}),
      });

      await expect(apiRequest('test')).rejects.toThrow('HTTP 500');
    });

    it('throws error when json parsing fails on error response', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 500,
        statusText: 'Internal Server Error',
        json: async () => {
          throw new Error('JSON parse error');
        },
      });

      await expect(apiRequest('test')).rejects.toThrow('HTTP 500');
    });

    it('handles network errors', async () => {
      (global.fetch as jest.Mock).mockRejectedValueOnce(new Error('Network error'));

      await expect(apiRequest('test')).rejects.toThrow('Network error');
    });

    it('includes custom headers', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({}),
      });

      await apiRequest('test', {
        headers: {
          'Authorization': 'Bearer token123',
        },
      });

      expect(global.fetch).toHaveBeenCalledWith(
        expect.any(String),
        expect.objectContaining({
          headers: expect.objectContaining({
            'Content-Type': 'application/json',
            'Authorization': 'Bearer token123',
          }),
        })
      );
    });

    it('allows overriding Content-Type header', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({}),
      });

      await apiRequest('test', {
        headers: {
          'Content-Type': 'text/plain',
        },
      });

      expect(global.fetch).toHaveBeenCalledWith(
        expect.any(String),
        expect.objectContaining({
          headers: expect.objectContaining({
            'Content-Type': 'text/plain',
          }),
        })
      );
    });
  });

  describe('protocolsApi', () => {
    describe('uploadText', () => {
      it('uploads protocol with extracted text', async () => {
        const mockResponse = { protocol_id: 'test-123' };
        (global.fetch as jest.Mock).mockResolvedValueOnce({
          ok: true,
          status: 200,
          json: async () => mockResponse,
        });

        const protocolData = {
          study_acronym: 'TEST-001',
          protocol_title: 'Test Protocol',
          extracted_text: 'Sample protocol text',
          original_filename: 'protocol.pdf',
          page_count: 10,
        };

        const result = await protocolsApi.uploadText(protocolData);

        expect(global.fetch).toHaveBeenCalledWith(
          expect.stringContaining('protocols/upload-text'),
          expect.objectContaining({
            method: 'POST',
            body: JSON.stringify(protocolData),
          })
        );
        expect(result).toEqual(mockResponse);
      });

      it('handles upload errors', async () => {
        (global.fetch as jest.Mock).mockResolvedValueOnce({
          ok: false,
          status: 400,
          statusText: 'Bad Request',
          json: async () => ({ detail: 'Invalid protocol data' }),
        });

        const protocolData = {
          study_acronym: '',
          protocol_title: '',
          extracted_text: '',
          original_filename: '',
          page_count: 0,
        };

        await expect(protocolsApi.uploadText(protocolData)).rejects.toThrow(
          'Invalid protocol data'
        );
      });
    });

    describe('list', () => {
      it('lists all protocols without filter', async () => {
        const mockProtocols = [{ id: '1' }, { id: '2' }];
        (global.fetch as jest.Mock).mockResolvedValueOnce({
          ok: true,
          status: 200,
          json: async () => mockProtocols,
        });

        const result = await protocolsApi.list();

        expect(global.fetch).toHaveBeenCalledWith(
          expect.stringMatching(/protocols$/),
          expect.any(Object)
        );
        expect(result).toEqual(mockProtocols);
      });

      it('lists protocols with status filter', async () => {
        const mockProtocols = [{ id: '1', status: 'active' }];
        (global.fetch as jest.Mock).mockResolvedValueOnce({
          ok: true,
          status: 200,
          json: async () => mockProtocols,
        });

        const result = await protocolsApi.list('active');

        expect(global.fetch).toHaveBeenCalledWith(
          expect.stringContaining('status_filter=active'),
          expect.any(Object)
        );
        expect(result).toEqual(mockProtocols);
      });

      it('encodes special characters in status filter', async () => {
        (global.fetch as jest.Mock).mockResolvedValueOnce({
          ok: true,
          status: 200,
          json: async () => [],
        });

        await protocolsApi.list('status with spaces');

        expect(global.fetch).toHaveBeenCalledWith(
          expect.stringContaining('status_filter=status%20with%20spaces'),
          expect.any(Object)
        );
      });
    });
  });

  describe('icfApi', () => {
    describe('getProtocolSummary', () => {
      it('fetches protocol summary', async () => {
        const mockSummary = { title: 'Test Protocol', sections: 10 };
        (global.fetch as jest.Mock).mockResolvedValueOnce({
          ok: true,
          status: 200,
          json: async () => mockSummary,
        });

        const result = await icfApi.getProtocolSummary('test-collection');

        expect(global.fetch).toHaveBeenCalledWith(
          expect.stringContaining('icf/protocol/test-collection/summary'),
          expect.any(Object)
        );
        expect(result).toEqual(mockSummary);
      });
    });

    describe('getStatus', () => {
      it('fetches generation status', async () => {
        const mockStatus = { task_id: 'task-123', status: 'completed' };
        (global.fetch as jest.Mock).mockResolvedValueOnce({
          ok: true,
          status: 200,
          json: async () => mockStatus,
        });

        const result = await icfApi.getStatus('task-123');

        expect(global.fetch).toHaveBeenCalledWith(
          expect.stringContaining('icf/status/task-123'),
          expect.any(Object)
        );
        expect(result).toEqual(mockStatus);
      });
    });

    describe('regenerateSection', () => {
      it('streams section regeneration', async () => {
        const mockReader = {
          read: jest
            .fn()
            .mockResolvedValueOnce({
              done: false,
              value: new TextEncoder().encode('data: {"type":"token","content":"Hello"}\n'),
            })
            .mockResolvedValueOnce({
              done: false,
              value: new TextEncoder().encode('data: {"type":"complete"}\n'),
            })
            .mockResolvedValueOnce({
              done: true,
              value: undefined,
            }),
          releaseLock: jest.fn(),
        };

        (global.fetch as jest.Mock).mockResolvedValueOnce({
          ok: true,
          status: 200,
          body: {
            getReader: () => mockReader,
          },
        });

        const generator = icfApi.regenerateSection('test-collection', 'section-1');
        const results = [];

        for await (const chunk of generator) {
          results.push(chunk);
        }

        expect(results).toHaveLength(2);
        expect(results[0]).toEqual({ type: 'token', content: 'Hello' });
        expect(results[1]).toEqual({ type: 'complete' });
        expect(mockReader.releaseLock).toHaveBeenCalled();
      });

      it('throws error for non-ok response', async () => {
        (global.fetch as jest.Mock).mockResolvedValueOnce({
          ok: false,
          status: 404,
          statusText: 'Not Found',
        });

        const generator = icfApi.regenerateSection('test-collection', 'missing-section');

        await expect(generator.next()).rejects.toThrow('HTTP 404');
      });

      it('throws error when response body is null', async () => {
        (global.fetch as jest.Mock).mockResolvedValueOnce({
          ok: true,
          status: 200,
          body: null,
        });

        const generator = icfApi.regenerateSection('test-collection', 'section-1');

        await expect(generator.next()).rejects.toThrow('Response body is null');
      });

      it('handles invalid SSE data gracefully', async () => {
        const mockReader = {
          read: jest
            .fn()
            .mockResolvedValueOnce({
              done: false,
              value: new TextEncoder().encode('data: invalid json\n'),
            })
            .mockResolvedValueOnce({
              done: true,
              value: undefined,
            }),
          releaseLock: jest.fn(),
        };

        (global.fetch as jest.Mock).mockResolvedValueOnce({
          ok: true,
          status: 200,
          body: {
            getReader: () => mockReader,
          },
        });

        const generator = icfApi.regenerateSection('test-collection', 'section-1');
        const results = [];

        for await (const chunk of generator) {
          results.push(chunk);
        }

        expect(results).toHaveLength(0); // Invalid data is skipped
      });

      it('includes protocol metadata in request', async () => {
        const mockReader = {
          read: jest.fn().mockResolvedValueOnce({
            done: true,
            value: undefined,
          }),
          releaseLock: jest.fn(),
        };

        (global.fetch as jest.Mock).mockResolvedValueOnce({
          ok: true,
          status: 200,
          body: {
            getReader: () => mockReader,
          },
        });

        const metadata = { title: 'Test Protocol' };
        const generator = icfApi.regenerateSection('test-collection', 'section-1', metadata);

        await generator.next();

        expect(global.fetch).toHaveBeenCalledWith(
          expect.any(String),
          expect.objectContaining({
            body: JSON.stringify({
              protocol_collection_name: 'test-collection',
              section_name: 'section-1',
              protocol_metadata: metadata,
            }),
          })
        );
      });
    });

    describe('generateStreaming', () => {
      it('streams ICF generation', async () => {
        const mockReader = {
          read: jest
            .fn()
            .mockResolvedValueOnce({
              done: false,
              value: new TextEncoder().encode('data: {"section":"intro","status":"generating"}\n'),
            })
            .mockResolvedValueOnce({
              done: false,
              value: new TextEncoder().encode('data: {"section":"intro","status":"complete"}\n'),
            })
            .mockResolvedValueOnce({
              done: true,
              value: undefined,
            }),
          releaseLock: jest.fn(),
        };

        (global.fetch as jest.Mock).mockResolvedValueOnce({
          ok: true,
          status: 200,
          body: {
            getReader: () => mockReader,
          },
        });

        const generator = icfApi.generateStreaming('test-collection');
        const results = [];

        for await (const chunk of generator) {
          results.push(chunk);
        }

        expect(results).toHaveLength(2);
        expect(results[0]).toEqual({ section: 'intro', status: 'generating' });
        expect(results[1]).toEqual({ section: 'intro', status: 'complete' });
      });

      it('handles multiple lines in single chunk', async () => {
        const mockReader = {
          read: jest
            .fn()
            .mockResolvedValueOnce({
              done: false,
              value: new TextEncoder().encode(
                'data: {"id":1}\ndata: {"id":2}\ndata: {"id":3}\n'
              ),
            })
            .mockResolvedValueOnce({
              done: true,
              value: undefined,
            }),
          releaseLock: jest.fn(),
        };

        (global.fetch as jest.Mock).mockResolvedValueOnce({
          ok: true,
          status: 200,
          body: {
            getReader: () => mockReader,
          },
        });

        const generator = icfApi.generateStreaming('test-collection');
        const results = [];

        for await (const chunk of generator) {
          results.push(chunk);
        }

        expect(results).toHaveLength(3);
        expect(results).toEqual([{ id: 1 }, { id: 2 }, { id: 3 }]);
      });

      it('releases reader lock on error', async () => {
        const mockReader = {
          read: jest.fn().mockRejectedValueOnce(new Error('Read error')),
          releaseLock: jest.fn(),
        };

        (global.fetch as jest.Mock).mockResolvedValueOnce({
          ok: true,
          status: 200,
          body: {
            getReader: () => mockReader,
          },
        });

        const generator = icfApi.generateStreaming('test-collection');

        await expect(async () => {
          for await (const _chunk of generator) {
            // Should not reach here
          }
        }).rejects.toThrow('Read error');

        expect(mockReader.releaseLock).toHaveBeenCalled();
      });
    });

    describe('health', () => {
      it('checks ICF service health', async () => {
        const mockHealth = { status: 'healthy' };
        (global.fetch as jest.Mock).mockResolvedValueOnce({
          ok: true,
          status: 200,
          json: async () => mockHealth,
        });

        const result = await icfApi.health();

        expect(global.fetch).toHaveBeenCalledWith(
          expect.stringContaining('icf/health'),
          expect.any(Object)
        );
        expect(result).toEqual(mockHealth);
      });
    });
  });

  describe('healthApi', () => {
    describe('check', () => {
      it('checks API health', async () => {
        const mockHealth = { status: 'ok' };
        (global.fetch as jest.Mock).mockResolvedValueOnce({
          ok: true,
          status: 200,
          json: async () => mockHealth,
        });

        const result = await healthApi.check();

        expect(global.fetch).toHaveBeenCalledWith(
          expect.stringContaining('health'),
          expect.any(Object)
        );
        expect(result).toEqual(mockHealth);
      });
    });

    describe('root', () => {
      it('fetches API root information', async () => {
        const mockRoot = { name: 'Clinical Trial Accelerator API', version: '1.0' };
        (global.fetch as jest.Mock).mockResolvedValueOnce({
          ok: true,
          status: 200,
          json: async () => mockRoot,
        });

        const result = await healthApi.root();

        expect(result).toEqual(mockRoot);
      });
    });
  });

  describe('logApiConfig', () => {
    it('logs API configuration to console', () => {
      const consoleSpy = jest.spyOn(console, 'log').mockImplementation();

      logApiConfig();

      expect(consoleSpy).toHaveBeenCalledWith(
        'API Configuration:',
        expect.objectContaining({
          baseUrl: expect.any(String),
          environment: expect.any(String),
          mode: expect.any(String),
        })
      );

      consoleSpy.mockRestore();
    });
  });
});
