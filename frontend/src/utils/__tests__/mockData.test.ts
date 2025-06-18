/**
 * Unit tests for mock data utilities
 * 
 * Tests mock data generation including:
 * - Data structure validation
 * - Data consistency
 * - Edge cases and variations
 * - Performance of data generation
 */

import { describe, it, expect } from 'vitest'
import {
  generateMockProtocol,
  generateMockProtocols,
  generateMockDocument,
  generateMockUser,
  generateMockProgress,
  MOCK_PROTOCOL_TEMPLATES,
  MOCK_STUDY_PHASES,
  MOCK_THERAPEUTIC_AREAS
} from '../mockData'

describe('Mock Data Utils', () => {
  describe('generateMockProtocol', () => {
    it('generates valid protocol with default values', () => {
      const protocol = generateMockProtocol()
      
      expect(protocol).toHaveProperty('id')
      expect(protocol).toHaveProperty('study_acronym')
      expect(protocol).toHaveProperty('protocol_title')
      expect(protocol).toHaveProperty('status')
      expect(protocol).toHaveProperty('upload_date')
      expect(protocol).toHaveProperty('document_id')
      
      expect(typeof protocol.id).toBe('number')
      expect(typeof protocol.study_acronym).toBe('string')
      expect(typeof protocol.protocol_title).toBe('string')
      expect(['processing', 'completed', 'failed']).toContain(protocol.status)
      expect(protocol.upload_date).toMatch(/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z$/)
      expect(typeof protocol.document_id).toBe('string')
    })

    it('accepts custom overrides', () => {
      const customProtocol = generateMockProtocol({
        study_acronym: 'CUSTOM-001',
        protocol_title: 'Custom Protocol Title',
        status: 'completed'
      })
      
      expect(customProtocol.study_acronym).toBe('CUSTOM-001')
      expect(customProtocol.protocol_title).toBe('Custom Protocol Title')
      expect(customProtocol.status).toBe('completed')
    })

    it('generates unique IDs for different protocols', () => {
      const protocol1 = generateMockProtocol()
      const protocol2 = generateMockProtocol()
      
      expect(protocol1.id).not.toBe(protocol2.id)
      expect(protocol1.document_id).not.toBe(protocol2.document_id)
    })

    it('generates realistic study acronyms', () => {
      const protocol = generateMockProtocol()
      
      expect(protocol.study_acronym).toMatch(/^[A-Z0-9-]+$/)
      expect(protocol.study_acronym.length).toBeGreaterThan(3)
      expect(protocol.study_acronym.length).toBeLessThan(20)
    })

    it('generates realistic protocol titles', () => {
      const protocol = generateMockProtocol()
      
      expect(protocol.protocol_title.length).toBeGreaterThan(10)
      expect(protocol.protocol_title.length).toBeLessThan(200)
      expect(protocol.protocol_title).toContain('Clinical')
    })

    it('generates valid upload dates within reasonable range', () => {
      const protocol = generateMockProtocol()
      const uploadDate = new Date(protocol.upload_date)
      const now = new Date()
      const oneYearAgo = new Date(now.getFullYear() - 1, now.getMonth(), now.getDate())
      
      expect(uploadDate.getTime()).toBeGreaterThan(oneYearAgo.getTime())
      expect(uploadDate.getTime()).toBeLessThanOrEqual(now.getTime())
    })
  })

  describe('generateMockProtocols', () => {
    it('generates specified number of protocols', () => {
      const protocols = generateMockProtocols(5)
      expect(protocols).toHaveLength(5)
    })

    it('generates default number when count not specified', () => {
      const protocols = generateMockProtocols()
      expect(protocols.length).toBeGreaterThan(0)
      expect(protocols.length).toBeLessThanOrEqual(10)
    })

    it('generates protocols with unique IDs', () => {
      const protocols = generateMockProtocols(10)
      const ids = protocols.map(p => p.id)
      const uniqueIds = new Set(ids)
      
      expect(uniqueIds.size).toBe(protocols.length)
    })

    it('generates protocols with different statuses', () => {
      const protocols = generateMockProtocols(20)
      const statuses = protocols.map(p => p.status)
      const uniqueStatuses = new Set(statuses)
      
      expect(uniqueStatuses.size).toBeGreaterThan(1)
    })

    it('accepts custom generation options', () => {
      const protocols = generateMockProtocols(5, {
        status: 'completed'
      })
      
      expect(protocols.every(p => p.status === 'completed')).toBe(true)
    })

    it('handles edge case of zero count', () => {
      const protocols = generateMockProtocols(0)
      expect(protocols).toHaveLength(0)
    })

    it('handles large counts efficiently', () => {
      const startTime = Date.now()
      const protocols = generateMockProtocols(1000)
      const endTime = Date.now()
      
      expect(protocols).toHaveLength(1000)
      expect(endTime - startTime).toBeLessThan(1000) // Should complete in under 1 second
    })
  })

  describe('generateMockDocument', () => {
    it('generates valid ICF document', () => {
      const document = generateMockDocument('icf')
      
      expect(document.document_type).toBe('icf')
      expect(document).toHaveProperty('sections')
      expect(document.sections).toHaveProperty('title')
      expect(document.sections).toHaveProperty('purpose')
      expect(document.sections).toHaveProperty('procedures')
      expect(document.sections).toHaveProperty('risks')
      expect(document.sections).toHaveProperty('benefits')
      expect(document.sections).toHaveProperty('rights')
      expect(document.sections).toHaveProperty('contact')
    })

    it('generates valid site checklist document', () => {
      const document = generateMockDocument('site_checklist')
      
      expect(document.document_type).toBe('site_checklist')
      expect(document).toHaveProperty('sections')
      expect(document.sections).toHaveProperty('regulatory')
      expect(document.sections).toHaveProperty('training')
      expect(document.sections).toHaveProperty('equipment')
      expect(document.sections).toHaveProperty('documentation')
    })

    it('accepts custom section overrides', () => {
      const document = generateMockDocument('icf', {
        title: 'Custom ICF Title',
        purpose: 'Custom Purpose Section'
      })
      
      expect(document.sections.title).toBe('Custom ICF Title')
      expect(document.sections.purpose).toBe('Custom Purpose Section')
    })

    it('generates realistic section content', () => {
      const document = generateMockDocument('icf')
      
      Object.values(document.sections).forEach(section => {
        expect(typeof section).toBe('string')
        expect(section.length).toBeGreaterThan(10)
        expect(section.length).toBeLessThan(1000)
      })
    })

    it('includes metadata properties', () => {
      const document = generateMockDocument('icf')
      
      expect(document).toHaveProperty('status')
      expect(document).toHaveProperty('generated_at')
      expect(document).toHaveProperty('word_count')
      expect(['processing', 'completed', 'failed']).toContain(document.status)
    })
  })

  describe('generateMockUser', () => {
    it('generates valid user data', () => {
      const user = generateMockUser()
      
      expect(user).toHaveProperty('id')
      expect(user).toHaveProperty('name')
      expect(user).toHaveProperty('email')
      expect(user).toHaveProperty('role')
      expect(user).toHaveProperty('organization')
      
      expect(typeof user.id).toBe('string')
      expect(user.email).toMatch(/^[^\s@]+@[^\s@]+\.[^\s@]+$/)
      expect(['researcher', 'admin', 'coordinator']).toContain(user.role)
    })

    it('accepts custom user properties', () => {
      const user = generateMockUser({
        name: 'Dr. Jane Smith',
        role: 'admin'
      })
      
      expect(user.name).toBe('Dr. Jane Smith')
      expect(user.role).toBe('admin')
    })
  })

  describe('generateMockProgress', () => {
    it('generates valid progress data', () => {
      const progress = generateMockProgress()
      
      expect(progress).toHaveProperty('current_step')
      expect(progress).toHaveProperty('total_steps')
      expect(progress).toHaveProperty('percentage')
      expect(progress).toHaveProperty('status')
      expect(progress).toHaveProperty('estimated_remaining')
      
      expect(progress.percentage).toBeGreaterThanOrEqual(0)
      expect(progress.percentage).toBeLessThanOrEqual(100)
      expect(progress.current_step).toBeLessThanOrEqual(progress.total_steps)
    })

    it('accepts custom progress values', () => {
      const progress = generateMockProgress({
        current_step: 3,
        total_steps: 5,
        status: 'analyzing'
      })
      
      expect(progress.current_step).toBe(3)
      expect(progress.total_steps).toBe(5)
      expect(progress.status).toBe('analyzing')
      expect(progress.percentage).toBe(60) // 3/5 * 100
    })
  })

  describe('Mock data constants', () => {
    it('provides valid protocol templates', () => {
      expect(Array.isArray(MOCK_PROTOCOL_TEMPLATES)).toBe(true)
      expect(MOCK_PROTOCOL_TEMPLATES.length).toBeGreaterThan(0)
      
      MOCK_PROTOCOL_TEMPLATES.forEach(template => {
        expect(template).toHaveProperty('name')
        expect(template).toHaveProperty('description')
        expect(template).toHaveProperty('typical_sections')
        expect(Array.isArray(template.typical_sections)).toBe(true)
      })
    })

    it('provides valid study phases', () => {
      expect(Array.isArray(MOCK_STUDY_PHASES)).toBe(true)
      expect(MOCK_STUDY_PHASES.length).toBeGreaterThan(0)
      
      MOCK_STUDY_PHASES.forEach(phase => {
        expect(typeof phase).toBe('string')
        expect(phase.length).toBeGreaterThan(0)
      })
    })

    it('provides valid therapeutic areas', () => {
      expect(Array.isArray(MOCK_THERAPEUTIC_AREAS)).toBe(true)
      expect(MOCK_THERAPEUTIC_AREAS.length).toBeGreaterThan(0)
      
      MOCK_THERAPEUTIC_AREAS.forEach(area => {
        expect(typeof area).toBe('string')
        expect(area.length).toBeGreaterThan(0)
      })
    })
  })

  describe('Data consistency', () => {
    it('maintains consistent data relationships', () => {
      const protocols = generateMockProtocols(5)
      
      protocols.forEach(protocol => {
        // All protocols should have consistent timestamp format
        expect(protocol.upload_date).toMatch(/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z$/)
        
        // Document IDs should be UUIDs or similar format
        expect(protocol.document_id).toMatch(/^[a-f0-9-]{36}$/)
        
        // Study acronyms should follow consistent pattern
        expect(protocol.study_acronym).toMatch(/^[A-Z0-9-]+$/)
      })
    })

    it('generates diverse but realistic data', () => {
      const protocols = generateMockProtocols(20)
      
      const acronyms = protocols.map(p => p.study_acronym)
      const titles = protocols.map(p => p.protocol_title)
      
      // Should have variety in generated data
      expect(new Set(acronyms).size).toBeGreaterThan(15)
      expect(new Set(titles).size).toBeGreaterThan(15)
    })
  })

  describe('Performance', () => {
    it('generates large datasets efficiently', () => {
      const startTime = Date.now()
      
      // Generate large dataset
      const protocols = generateMockProtocols(10000)
      const documents = protocols.map(() => generateMockDocument('icf'))
      const users = Array.from({ length: 1000 }, () => generateMockUser())
      
      const endTime = Date.now()
      const duration = endTime - startTime
      
      expect(protocols).toHaveLength(10000)
      expect(documents).toHaveLength(10000)
      expect(users).toHaveLength(1000)
      expect(duration).toBeLessThan(5000) // Should complete in under 5 seconds
    })
  })
})