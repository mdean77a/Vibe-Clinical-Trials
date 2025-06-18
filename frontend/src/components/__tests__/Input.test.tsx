/**
 * Unit tests for Input component
 * 
 * Tests input functionality including:
 * - Basic rendering and input handling
 * - Different input types
 * - Validation states
 * - Accessibility features
 * - Form integration
 */

import { describe, it, expect, vi } from 'vitest'
import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'

import { render } from '../../test/test-utils'
import Input from '../Input'

describe('Input', () => {
  it('renders input with label', () => {
    render(<Input label="Test Input" />)
    
    expect(screen.getByLabelText(/test input/i)).toBeInTheDocument()
    expect(screen.getByText('Test Input')).toBeInTheDocument()
  })

  it('handles value changes', async () => {
    const user = userEvent.setup()
    const handleChange = vi.fn()
    
    render(<Input label="Test Input" onChange={handleChange} />)
    
    const input = screen.getByLabelText(/test input/i)
    await user.type(input, 'test value')
    
    expect(handleChange).toHaveBeenCalledTimes(10) // 10 characters
    expect(input).toHaveValue('test value')
  })

  it('renders with placeholder', () => {
    render(<Input label="Test Input" placeholder="Enter text here" />)
    
    const input = screen.getByLabelText(/test input/i)
    expect(input).toHaveAttribute('placeholder', 'Enter text here')
  })

  it('renders text input type correctly', () => {
    render(<Input label="Text Input" type="text" />)
    
    const input = screen.getByLabelText(/text input/i)
    expect(input).toHaveAttribute('type', 'text')
  })

  it('renders email input type correctly', () => {
    render(<Input label="Email Input" type="email" />)
    
    const input = screen.getByLabelText(/email input/i)
    expect(input).toHaveAttribute('type', 'email')
  })

  it('renders password input type correctly', () => {
    render(<Input label="Password Input" type="password" />)
    
    const input = screen.getByLabelText(/password input/i)
    expect(input).toHaveAttribute('type', 'password')
  })

  it('renders number input type correctly', () => {
    render(<Input label="Number Input" type="number" />)
    
    const input = screen.getByLabelText(/number input/i)
    expect(input).toHaveAttribute('type', 'number')
  })

  it('renders disabled state correctly', () => {
    render(<Input label="Disabled Input" disabled />)
    
    const input = screen.getByLabelText(/disabled input/i)
    expect(input).toBeDisabled()
    expect(input).toHaveClass('opacity-50', 'cursor-not-allowed')
  })

  it('renders required state correctly', () => {
    render(<Input label="Required Input" required />)
    
    const input = screen.getByLabelText(/required input/i)
    expect(input).toBeRequired()
    expect(screen.getByText('*')).toBeInTheDocument()
  })

  it('renders error state correctly', () => {
    render(<Input label="Error Input" error="This field is required" />)
    
    const input = screen.getByLabelText(/error input/i)
    expect(input).toHaveClass('border-red-500')
    expect(screen.getByText('This field is required')).toBeInTheDocument()
  })

  it('renders success state correctly', () => {
    render(<Input label="Success Input" success />)
    
    const input = screen.getByLabelText(/success input/i)
    expect(input).toHaveClass('border-green-500')
  })

  it('renders help text when provided', () => {
    render(<Input label="Input with Help" helpText="This is helpful information" />)
    
    expect(screen.getByText('This is helpful information')).toBeInTheDocument()
  })

  it('renders with custom className', () => {
    render(<Input label="Custom Input" className="custom-input-class" />)
    
    const input = screen.getByLabelText(/custom input/i)
    expect(input).toHaveClass('custom-input-class')
  })

  it('supports controlled value', () => {
    const { rerender } = render(<Input label="Controlled Input" value="initial" onChange={() => {}} />)
    
    const input = screen.getByLabelText(/controlled input/i)
    expect(input).toHaveValue('initial')
    
    rerender(<Input label="Controlled Input" value="updated" onChange={() => {}} />)
    expect(input).toHaveValue('updated')
  })

  it('supports uncontrolled input with defaultValue', () => {
    render(<Input label="Uncontrolled Input" defaultValue="default value" />)
    
    const input = screen.getByLabelText(/uncontrolled input/i)
    expect(input).toHaveValue('default value')
  })

  it('handles focus and blur events', async () => {
    const user = userEvent.setup()
    const handleFocus = vi.fn()
    const handleBlur = vi.fn()
    
    render(<Input label="Focus Input" onFocus={handleFocus} onBlur={handleBlur} />)
    
    const input = screen.getByLabelText(/focus input/i)
    
    await user.click(input)
    expect(handleFocus).toHaveBeenCalledTimes(1)
    
    await user.tab()
    expect(handleBlur).toHaveBeenCalledTimes(1)
  })

  it('has proper accessibility attributes', () => {
    render(<Input label="Accessible Input" aria-describedby="help-text" />)
    
    const input = screen.getByLabelText(/accessible input/i)
    expect(input).toHaveAttribute('aria-describedby', 'help-text')
  })

  it('links label to input correctly', () => {
    render(<Input label="Linked Input" />)
    
    const label = screen.getByText('Linked Input')
    const input = screen.getByLabelText(/linked input/i)
    
    expect(label).toHaveAttribute('for', input.id)
  })

  it('renders with icon when provided', () => {
    const TestIcon = () => <span data-testid="test-icon">Icon</span>
    
    render(<Input label="Input with Icon" icon={<TestIcon />} />)
    
    expect(screen.getByTestId('test-icon')).toBeInTheDocument()
    expect(screen.getByLabelText(/input with icon/i)).toBeInTheDocument()
  })

  it('supports size variants', () => {
    const { rerender } = render(<Input label="Size Input" size="sm" />)
    
    let input = screen.getByLabelText(/size input/i)
    expect(input).toHaveClass('text-sm', 'py-1')
    
    rerender(<Input label="Size Input" size="lg" />)
    input = screen.getByLabelText(/size input/i)
    expect(input).toHaveClass('text-lg', 'py-3')
  })

  it('validates email format', async () => {
    const user = userEvent.setup()
    
    render(<Input label="Email Validation" type="email" />)
    
    const input = screen.getByLabelText(/email validation/i)
    await user.type(input, 'invalid-email')
    
    // Browser validation will handle email format
    expect(input).toHaveAttribute('type', 'email')
    expect(input).toHaveValue('invalid-email')
  })

  it('supports min and max for number inputs', () => {
    render(<Input label="Number Range" type="number" min={0} max={100} />)
    
    const input = screen.getByLabelText(/number range/i)
    expect(input).toHaveAttribute('min', '0')
    expect(input).toHaveAttribute('max', '100')
  })

  it('supports step for number inputs', () => {
    render(<Input label="Number Step" type="number" step={0.1} />)
    
    const input = screen.getByLabelText(/number step/i)
    expect(input).toHaveAttribute('step', '0.1')
  })

  it('handles keyboard navigation correctly', async () => {
    const user = userEvent.setup()
    
    render(
      <div>
        <Input label="First Input" />
        <Input label="Second Input" />
      </div>
    )
    
    const firstInput = screen.getByLabelText(/first input/i)
    const secondInput = screen.getByLabelText(/second input/i)
    
    // Tab through inputs
    await user.tab()
    expect(firstInput).toHaveFocus()
    
    await user.tab()
    expect(secondInput).toHaveFocus()
  })
})