/**
 * @jest-environment jsdom
 */

import { describe, it, expect, beforeEach } from 'vitest'
import type { Protocol } from '../mockData'
import {
  mockProtocols,
  initializeMockData
} from '../mockData'

describe('Mock Data Utils', () => {
  beforeEach(() => {
    // Clear localStorage before each test
    localStorage.clear()
  })

  describe('Protocol interface', () => {
    it('mock protocols match the Protocol interface', () => {
      mockProtocols.forEach(protocol => {
        expect(protocol).toHaveProperty('id')
        expect(protocol).toHaveProperty('study_acronym')
        expect(protocol).toHaveProperty('protocol_title')
        expect(protocol).toHaveProperty('upload_date')
        expect(protocol).toHaveProperty('status')
        
        expect(typeof protocol.id).toBe('string')
        expect(typeof protocol.study_acronym).toBe('string')
        expect(typeof protocol.protocol_title).toBe('string')
        expect(typeof protocol.upload_date).toBe('string')
        expect(typeof protocol.status).toBe('string')
      })
    })

    it('has valid study acronyms', () => {
      mockProtocols.forEach(protocol => {
        expect(protocol.study_acronym).toMatch(/^STUDY-\d{3}$/)
      })
    })

    it('has valid upload dates', () => {
      mockProtocols.forEach(protocol => {
        expect(protocol.upload_date).toMatch(/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$/)
        expect(new Date(protocol.upload_date)).toBeInstanceOf(Date)
        expect(new Date(protocol.upload_date).getTime()).not.toBeNaN()
      })
    })

    it('has valid statuses', () => {
      const validStatuses = ['processing', 'completed', 'failed', 'processed']
      mockProtocols.forEach(protocol => {
        expect(validStatuses).toContain(protocol.status)
      })
    })
  })

  describe('mockProtocols', () => {
    it('exports array of mock protocols', () => {
      expect(Array.isArray(mockProtocols)).toBe(true)
      expect(mockProtocols.length).toBeGreaterThan(0)
    })

    it('has unique IDs', () => {
      const ids = mockProtocols.map(p => p.id)
      const uniqueIds = new Set(ids)
      expect(uniqueIds.size).toBe(ids.length)
    })

    it('has unique study acronyms', () => {
      const acronyms = mockProtocols.map(p => p.study_acronym)
      const uniqueAcronyms = new Set(acronyms)
      expect(uniqueAcronyms.size).toBe(acronyms.length)
    })

    it('has meaningful protocol titles', () => {
      mockProtocols.forEach(protocol => {
        expect(protocol.protocol_title.length).toBeGreaterThan(10)
        expect(protocol.protocol_title).toMatch(/phase|trial|study|randomized/i)
      })
    })
  })

  describe('initializeMockData', () => {
    it('initializes localStorage with mock protocols when empty', () => {
      expect(localStorage.getItem('protocols')).toBeNull()
      
      initializeMockData()
      
      const storedProtocols = localStorage.getItem('protocols')
      expect(storedProtocols).not.toBeNull()
      
      const parsedProtocols = JSON.parse(storedProtocols!)
      expect(parsedProtocols).toEqual(mockProtocols)
    })

    it('does not overwrite existing localStorage data', () => {
      const existingData = [{ 
        id: 'existing_1', 
        study_acronym: 'EXISTING-001',
        protocol_title: 'Existing Protocol',
        upload_date: '2024-01-01T00:00:00Z',
        status: 'processed'
      }]
      
      localStorage.setItem('protocols', JSON.stringify(existingData))
      
      initializeMockData()
      
      const storedProtocols = localStorage.getItem('protocols')
      const parsedProtocols = JSON.parse(storedProtocols!)
      expect(parsedProtocols).toEqual(existingData)
      expect(parsedProtocols).not.toEqual(mockProtocols)
    })

    it('can be called multiple times safely', () => {
      initializeMockData()
      const firstCall = localStorage.getItem('protocols')
      
      initializeMockData()
      const secondCall = localStorage.getItem('protocols')
      
      expect(firstCall).toBe(secondCall)
    })
  })

  describe('data quality', () => {
    it('protocols are ordered by upload date (newest first)', () => {
      const uploadDates = mockProtocols.map(p => new Date(p.upload_date).getTime())
      const sortedDates = [...uploadDates].sort((a, b) => b - a)
      expect(uploadDates).toEqual(sortedDates)
    })

    it('contains realistic clinical trial data', () => {
      const hasPhaseInfo = mockProtocols.some(p => 
        p.protocol_title.toLowerCase().includes('phase')
      )
      const hasRandomizedStudy = mockProtocols.some(p => 
        p.protocol_title.toLowerCase().includes('randomized')
      )
      const hasClinicalTrial = mockProtocols.some(p => 
        p.protocol_title.toLowerCase().includes('trial')
      )
      
      expect(hasPhaseInfo).toBe(true)
      expect(hasRandomizedStudy).toBe(true)
      expect(hasClinicalTrial).toBe(true)
    })

    it('covers diverse medical areas', () => {
      const allTitles = mockProtocols.map(p => p.protocol_title.toLowerCase()).join(' ')
      
      // Check for different medical specialties
      const hasCardiology = allTitles.includes('cardiac') || allTitles.includes('heart')
      const hasOncology = allTitles.includes('cancer') || allTitles.includes('immunotherapy')
      const hasNeurology = allTitles.includes('stroke') || allTitles.includes('neuroprotective')
      
      expect(hasCardiology).toBe(true)
      expect(hasOncology).toBe(true)
      expect(hasNeurology).toBe(true)
    })
  })
})