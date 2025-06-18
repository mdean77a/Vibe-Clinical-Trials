/**
 * Unit tests for Button component
 * 
 * Tests button functionality including:
 * - Basic rendering
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

  it('renders disabled state correctly', () => {
    render(<Button disabled>Disabled Button</Button>)
    
    const button = screen.getByRole('button', { name: /disabled button/i })
    expect(button).toBeDisabled()
  })

  it('does not trigger click when disabled', async () => {
    const user = userEvent.setup()
    const handleClick = vi.fn()
    
    render(<Button disabled onClick={handleClick}>Disabled Button</Button>)
    
    const button = screen.getByRole('button', { name: /disabled button/i })
    await user.click(button)
    
    expect(handleClick).not.toHaveBeenCalled()
  })

  it('renders with custom className', () => {
    render(<Button className="custom-class">Custom Button</Button>)
    
    const button = screen.getByRole('button', { name: /custom button/i })
    expect(button).toHaveClass('custom-class')
  })

  it('applies custom styles', () => {
    const customStyle = { backgroundColor: 'blue', color: 'white' }
    render(<Button style={customStyle}>Styled Button</Button>)
    
    const button = screen.getByRole('button', { name: /styled button/i })
    expect(button).toHaveStyle('background-color: blue')
    expect(button).toHaveStyle('color: white')
  })

  it('handles mouse events', async () => {
    const user = userEvent.setup()
    const handleMouseEnter = vi.fn()
    const handleMouseLeave = vi.fn()
    
    render(
      <Button onMouseEnter={handleMouseEnter} onMouseLeave={handleMouseLeave}>
        Hover Button
      </Button>
    )
    
    const button = screen.getByRole('button', { name: /hover button/i })
    
    await user.hover(button)
    expect(handleMouseEnter).toHaveBeenCalledTimes(1)
    
    await user.unhover(button)
    expect(handleMouseLeave).toHaveBeenCalledTimes(1)
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

  it('renders complex children', () => {
    render(
      <Button>
        <span data-testid="icon">Icon</span>
        <span data-testid="text">Text</span>
      </Button>
    )
    
    expect(screen.getByTestId('icon')).toBeInTheDocument()
    expect(screen.getByTestId('text')).toBeInTheDocument()
  })

  it('can be rendered without onClick handler', () => {
    render(<Button>Static Button</Button>)
    const button = screen.getByRole('button', { name: /static button/i })
    expect(button).toBeInTheDocument()
  })

  it('maintains button element semantics', () => {
    render(<Button>Submit</Button>)
    const button = screen.getByRole('button', { name: /submit/i })
    expect(button.tagName).toBe('BUTTON')
  })
})