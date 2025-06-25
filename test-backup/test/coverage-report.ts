/**
 * Coverage report utilities for test analysis
 * 
 * Provides utilities for:
 * - Coverage threshold validation
 * - Custom coverage reporting
 * - Test performance metrics
 */

export interface CoverageReport {
  statements: number
  branches: number
  functions: number
  lines: number
}

export interface CoverageThresholds {
  statements: number
  branches: number
  functions: number
  lines: number
}

export const DEFAULT_THRESHOLDS: CoverageThresholds = {
  statements: 80,
  branches: 80,
  functions: 80,
  lines: 80
}

export function validateCoverage(
  coverage: CoverageReport, 
  thresholds: CoverageThresholds = DEFAULT_THRESHOLDS
): { passed: boolean; failures: string[] } {
  const failures: string[] = []
  
  if (coverage.statements < thresholds.statements) {
    failures.push(`Statements coverage ${coverage.statements}% is below threshold ${thresholds.statements}%`)
  }
  
  if (coverage.branches < thresholds.branches) {
    failures.push(`Branches coverage ${coverage.branches}% is below threshold ${thresholds.branches}%`)
  }
  
  if (coverage.functions < thresholds.functions) {
    failures.push(`Functions coverage ${coverage.functions}% is below threshold ${thresholds.functions}%`)
  }
  
  if (coverage.lines < thresholds.lines) {
    failures.push(`Lines coverage ${coverage.lines}% is below threshold ${thresholds.lines}%`)
  }
  
  return {
    passed: failures.length === 0,
    failures
  }
}

export function generateCoverageReport(coverage: CoverageReport): string {
  return `
Coverage Report:
================
Statements: ${coverage.statements}%
Branches:   ${coverage.branches}%
Functions:  ${coverage.functions}%
Lines:      ${coverage.lines}%
`
}

export function calculateOverallCoverage(coverage: CoverageReport): number {
  return (coverage.statements + coverage.branches + coverage.functions + coverage.lines) / 4
}

export function getCoverageStatus(coverage: CoverageReport, thresholds: CoverageThresholds): 'excellent' | 'good' | 'needs-improvement' | 'poor' {
  const overall = calculateOverallCoverage(coverage)
  
  if (overall >= 90) return 'excellent'
  if (overall >= 80) return 'good'
  if (overall >= 70) return 'needs-improvement'
  return 'poor'
}