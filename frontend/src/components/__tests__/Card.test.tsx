/**
 * Unit tests for Card component
 * 
 * Tests card functionality including:
 * - Basic rendering
 * - Different variants and layouts
 * - Content display
 * - Accessibility
 */

import { describe, it, expect } from 'vitest'
import { screen } from '@testing-library/react'

import { render } from '../../test/test-utils'
import Card from '../Card'

describe('Card', () => {
  it('renders card with children', () => {
    render(
      <Card>
        <p>Card content</p>
      </Card>
    )
    
    expect(screen.getByText('Card content')).toBeInTheDocument()
  })

  it('renders with title when provided', () => {
    render(
      <Card title="Card Title">
        <p>Card content</p>
      </Card>
    )
    
    expect(screen.getByText('Card Title')).toBeInTheDocument()
    expect(screen.getByText('Card content')).toBeInTheDocument()
  })

  it('renders with subtitle when provided', () => {
    render(
      <Card title="Card Title" subtitle="Card Subtitle">
        <p>Card content</p>
      </Card>
    )
    
    expect(screen.getByText('Card Title')).toBeInTheDocument()
    expect(screen.getByText('Card Subtitle')).toBeInTheDocument()
    expect(screen.getByText('Card content')).toBeInTheDocument()
  })

  it('renders default variant correctly', () => {
    render(
      <Card data-testid="card">
        <p>Content</p>
      </Card>
    )
    
    const card = screen.getByTestId('card')
    expect(card).toHaveClass('bg-white', 'border', 'border-gray-200')
  })

  it('renders elevated variant correctly', () => {
    render(
      <Card variant="elevated" data-testid="card">
        <p>Content</p>
      </Card>
    )
    
    const card = screen.getByTestId('card')
    expect(card).toHaveClass('bg-white', 'shadow-lg')
  })

  it('renders outlined variant correctly', () => {
    render(
      <Card variant="outlined" data-testid="card">
        <p>Content</p>
      </Card>
    )
    
    const card = screen.getByTestId('card')
    expect(card).toHaveClass('bg-white', 'border-2', 'border-gray-300')
  })

  it('renders filled variant correctly', () => {
    render(
      <Card variant="filled" data-testid="card">
        <p>Content</p>
      </Card>
    )
    
    const card = screen.getByTestId('card')
    expect(card).toHaveClass('bg-gray-50', 'border', 'border-gray-200')
  })

  it('renders compact padding correctly', () => {
    render(
      <Card padding="compact" data-testid="card">
        <p>Content</p>
      </Card>
    )
    
    const card = screen.getByTestId('card')
    expect(card).toHaveClass('p-3')
  })

  it('renders comfortable padding correctly', () => {
    render(
      <Card padding="comfortable" data-testid="card">
        <p>Content</p>
      </Card>
    )
    
    const card = screen.getByTestId('card')
    expect(card).toHaveClass('p-8')
  })

  it('renders with custom className', () => {
    render(
      <Card className="custom-card-class" data-testid="card">
        <p>Content</p>
      </Card>
    )
    
    const card = screen.getByTestId('card')
    expect(card).toHaveClass('custom-card-class')
  })

  it('renders with actions when provided', () => {
    const actions = (
      <div>
        <button>Action 1</button>
        <button>Action 2</button>
      </div>
    )
    
    render(
      <Card title="Card with Actions" actions={actions}>
        <p>Card content</p>
      </Card>
    )
    
    expect(screen.getByText('Card with Actions')).toBeInTheDocument()
    expect(screen.getByText('Card content')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /action 1/i })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /action 2/i })).toBeInTheDocument()
  })

  it('has proper semantic structure', () => {
    render(
      <Card title="Semantic Card">
        <p>Content</p>
      </Card>
    )
    
    // Should have proper heading structure
    const title = screen.getByText('Semantic Card')
    expect(title.tagName).toBe('H3')
  })

  it('renders image when provided', () => {
    render(
      <Card 
        title="Card with Image" 
        image="/test-image.jpg"
        imageAlt="Test image"
      >
        <p>Content</p>
      </Card>
    )
    
    const image = screen.getByRole('img', { name: /test image/i })
    expect(image).toBeInTheDocument()
    expect(image).toHaveAttribute('src', '/test-image.jpg')
    expect(image).toHaveAttribute('alt', 'Test image')
  })

  it('renders clickable card correctly', () => {
    render(
      <Card clickable data-testid="card">
        <p>Clickable content</p>
      </Card>
    )
    
    const card = screen.getByTestId('card')
    expect(card).toHaveClass('cursor-pointer', 'hover:shadow-md', 'transition-shadow')
  })

  it('renders loading state correctly', () => {
    render(
      <Card loading data-testid="card">
        <p>Content</p>
      </Card>
    )
    
    expect(screen.getByText(/loading/i)).toBeInTheDocument()
  })

  it('supports complex content structure', () => {
    render(
      <Card title="Complex Card">
        <div>
          <h4>Section 1</h4>
          <p>Section 1 content</p>
        </div>
        <div>
          <h4>Section 2</h4>
          <ul>
            <li>Item 1</li>
            <li>Item 2</li>
          </ul>
        </div>
      </Card>
    )
    
    expect(screen.getByText('Complex Card')).toBeInTheDocument()
    expect(screen.getByText('Section 1')).toBeInTheDocument()
    expect(screen.getByText('Section 1 content')).toBeInTheDocument()
    expect(screen.getByText('Section 2')).toBeInTheDocument()
    expect(screen.getByText('Item 1')).toBeInTheDocument()
    expect(screen.getByText('Item 2')).toBeInTheDocument()
  })
})