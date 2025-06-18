/**
 * Unit tests for Button component
 * 
 * Tests button functionality including:
 * - Basic rendering
 * - Different variants and sizes
 * - Click events
 * - Disabled states
 * - Accessibility
 */

import { describe, it, expect, vi } from 'vitest'
import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'

import { render } from '../../test/test-utils'
import Button from '../Button'

describe('Button', () => {
  it('renders button with text', () => {
    render(<Button>Click me</Button>)
    
    expect(screen.getByRole('button', { name: /click me/i })).toBeInTheDocument()
  })

  it('handles click events', async () => {
    const user = userEvent.setup()
    const handleClick = vi.fn()
    
    render(<Button onClick={handleClick}>Click me</Button>)
    
    const button = screen.getByRole('button', { name: /click me/i })
    await user.click(button)
    
    expect(handleClick).toHaveBeenCalledTimes(1)
  })

  it('renders primary variant correctly', () => {
    render(<Button variant="primary">Primary Button</Button>)
    
    const button = screen.getByRole('button', { name: /primary button/i })
    expect(button).toHaveClass('bg-blue-600')
  })

  it('renders secondary variant correctly', () => {
    render(<Button variant="secondary">Secondary Button</Button>)
    
    const button = screen.getByRole('button', { name: /secondary button/i })
    expect(button).toHaveClass('bg-gray-600')
  })

  it('renders outline variant correctly', () => {
    render(<Button variant="outline">Outline Button</Button>)
    
    const button = screen.getByRole('button', { name: /outline button/i })
    expect(button).toHaveClass('border-gray-300')
  })

  it('renders small size correctly', () => {
    render(<Button size="sm">Small Button</Button>)
    
    const button = screen.getByRole('button', { name: /small button/i })
    expect(button).toHaveClass('px-3', 'py-1.5', 'text-sm')
  })

  it('renders large size correctly', () => {
    render(<Button size="lg">Large Button</Button>)
    
    const button = screen.getByRole('button', { name: /large button/i })
    expect(button).toHaveClass('px-6', 'py-3', 'text-lg')
  })

  it('renders disabled state correctly', () => {
    render(<Button disabled>Disabled Button</Button>)
    
    const button = screen.getByRole('button', { name: /disabled button/i })
    expect(button).toBeDisabled()
    expect(button).toHaveClass('opacity-50', 'cursor-not-allowed')
  })

  it('does not trigger click when disabled', async () => {
    const user = userEvent.setup()
    const handleClick = vi.fn()
    
    render(<Button disabled onClick={handleClick}>Disabled Button</Button>)
    
    const button = screen.getByRole('button', { name: /disabled button/i })
    await user.click(button)
    
    expect(handleClick).not.toHaveBeenCalled()
  })

  it('renders loading state correctly', () => {
    render(<Button loading>Loading Button</Button>)
    
    const button = screen.getByRole('button', { name: /loading button/i })
    expect(button).toBeDisabled()
    expect(screen.getByText(/loading/i)).toBeInTheDocument()
  })

  it('renders with custom className', () => {
    render(<Button className="custom-class">Custom Button</Button>)
    
    const button = screen.getByRole('button', { name: /custom button/i })
    expect(button).toHaveClass('custom-class')
  })

  it('supports button type attributes', () => {
    render(<Button type="submit">Submit Button</Button>)
    
    const button = screen.getByRole('button', { name: /submit button/i })
    expect(button).toHaveAttribute('type', 'submit')
  })

  it('has proper accessibility attributes', () => {
    render(<Button aria-label="Accessible button">Button</Button>)
    
    const button = screen.getByRole('button', { name: /accessible button/i })
    expect(button).toHaveAttribute('aria-label', 'Accessible button')
  })

  it('supports keyboard navigation', async () => {
    const user = userEvent.setup()
    const handleClick = vi.fn()
    
    render(<Button onClick={handleClick}>Keyboard Button</Button>)
    
    const button = screen.getByRole('button', { name: /keyboard button/i })
    
    // Tab to button and press Enter
    await user.tab()
    expect(button).toHaveFocus()
    
    await user.keyboard('{Enter}')
    expect(handleClick).toHaveBeenCalledTimes(1)
    
    // Press Space
    await user.keyboard(' ')
    expect(handleClick).toHaveBeenCalledTimes(2)
  })

  it('renders with icon when provided', () => {
    const TestIcon = () => <span data-testid="test-icon">Icon</span>
    
    render(<Button icon={<TestIcon />}>Button with Icon</Button>)
    
    expect(screen.getByTestId('test-icon')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /button with icon/i })).toBeInTheDocument()
  })

  it('renders full width correctly', () => {
    render(<Button fullWidth>Full Width Button</Button>)
    
    const button = screen.getByRole('button', { name: /full width button/i })
    expect(button).toHaveClass('w-full')
  })
})