/**
 * Unit tests for Card component
 * 
 * Tests card functionality including:
 * - Basic rendering
 * - Content display
 * - Custom styling
 * - Layout behavior
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

  it('applies default card styles', () => {
    render(
      <Card data-testid="card">
        <p>Content</p>
      </Card>
    )
    
    const card = screen.getByTestId('card')
    expect(card).toHaveClass('p-4', 'bg-white', 'shadow', 'rounded')
  })

  it('applies custom className', () => {
    render(
      <Card className="custom-card" data-testid="card">
        <p>Content</p>
      </Card>
    )
    
    const card = screen.getByTestId('card')
    expect(card).toHaveClass('custom-card')
    // Should still have default classes
    expect(card).toHaveClass('p-4', 'bg-white', 'shadow', 'rounded')
  })

  it('applies custom styles', () => {
    const customStyle = { 
      backgroundColor: 'lightblue', 
      border: '2px solid red',
      padding: '20px'
    }
    
    render(
      <Card style={customStyle} data-testid="card">
        <p>Styled content</p>
      </Card>
    )
    
    const card = screen.getByTestId('card')
    expect(card).toHaveStyle('background-color: lightblue')
    expect(card).toHaveStyle('border: 2px solid red')
    expect(card).toHaveStyle('padding: 20px')
  })

  it('renders complex children structure', () => {
    render(
      <Card>
        <div data-testid="header">
          <h2>Card Title</h2>
          <p>Subtitle</p>
        </div>
        <div data-testid="body">
          <p>Card body content</p>
          <button>Action</button>
        </div>
      </Card>
    )
    
    expect(screen.getByTestId('header')).toBeInTheDocument()
    expect(screen.getByTestId('body')).toBeInTheDocument()
    expect(screen.getByText('Card Title')).toBeInTheDocument()
    expect(screen.getByText('Subtitle')).toBeInTheDocument()
    expect(screen.getByText('Card body content')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Action' })).toBeInTheDocument()
  })

  it('handles empty children gracefully', () => {
    render(<Card data-testid="empty-card"> </Card>)
    
    const card = screen.getByTestId('empty-card')
    expect(card).toBeInTheDocument()
  })

  it('renders as a div element', () => {
    render(
      <Card data-testid="card">
        <p>Content</p>
      </Card>
    )
    
    const card = screen.getByTestId('card')
    expect(card.tagName).toBe('DIV')
  })

  it('combines multiple custom classes', () => {
    render(
      <Card className="border-2 border-blue-500 m-4" data-testid="card">
        <p>Multi-class card</p>
      </Card>
    )
    
    const card = screen.getByTestId('card')
    expect(card).toHaveClass('border-2', 'border-blue-500', 'm-4')
    // Should still have default classes
    expect(card).toHaveClass('p-4', 'bg-white', 'shadow', 'rounded')
  })

  it('supports nested cards', () => {
    render(
      <Card data-testid="outer-card">
        <h2>Outer Card</h2>
        <Card data-testid="inner-card">
          <p>Inner Card Content</p>
        </Card>
      </Card>
    )
    
    expect(screen.getByTestId('outer-card')).toBeInTheDocument()
    expect(screen.getByTestId('inner-card')).toBeInTheDocument()
    expect(screen.getByText('Outer Card')).toBeInTheDocument()
    expect(screen.getByText('Inner Card Content')).toBeInTheDocument()
  })

  it('preserves content accessibility', () => {
    render(
      <Card>
        <button aria-label="Close">×</button>
        <input aria-label="Search" type="text" />
        <a href="#" aria-label="Learn more">Link</a>
      </Card>
    )
    
    expect(screen.getByRole('button', { name: 'Close' })).toBeInTheDocument()
    expect(screen.getByRole('textbox', { name: 'Search' })).toBeInTheDocument()
    expect(screen.getByRole('link', { name: 'Learn more' })).toBeInTheDocument()
  })

  it('maintains proper layout structure', () => {
    render(
      <Card data-testid="layout-card">
        <header>Header content</header>
        <main>Main content</main>
        <footer>Footer content</footer>
      </Card>
    )
    
    const card = screen.getByTestId('layout-card')
    expect(card.children).toHaveLength(3)
    expect(screen.getByText('Header content')).toBeInTheDocument()
    expect(screen.getByText('Main content')).toBeInTheDocument()
    expect(screen.getByText('Footer content')).toBeInTheDocument()
  })
})