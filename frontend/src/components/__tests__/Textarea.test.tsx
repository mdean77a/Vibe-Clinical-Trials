/**
 * Unit tests for Textarea component
 * 
 * Tests textarea functionality including:
 * - Basic rendering and input handling
 * - Multi-line text support
 * - Resize behavior
 * - Validation states
 * - Accessibility features
 */

import { describe, it, expect, vi } from 'vitest'
import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'

import { render } from '../../test/test-utils'
import Textarea from '../Textarea'

describe('Textarea', () => {
  it('renders textarea with label', () => {
    render(<Textarea label="Test Textarea" />)
    
    expect(screen.getByLabelText(/test textarea/i)).toBeInTheDocument()
    expect(screen.getByText('Test Textarea')).toBeInTheDocument()
  })

  it('handles value changes', async () => {
    const user = userEvent.setup()
    const handleChange = vi.fn()
    
    render(<Textarea label="Test Textarea" onChange={handleChange} />)
    
    const textarea = screen.getByLabelText(/test textarea/i)
    await user.type(textarea, 'multi\nline\ntext')
    
    expect(handleChange).toHaveBeenCalled()
    expect(textarea).toHaveValue('multi\nline\ntext')
  })

  it('renders with placeholder', () => {
    render(<Textarea label="Test Textarea" placeholder="Enter multi-line text here" />)
    
    const textarea = screen.getByLabelText(/test textarea/i)
    expect(textarea).toHaveAttribute('placeholder', 'Enter multi-line text here')
  })

  it('supports multi-line text input', async () => {
    const user = userEvent.setup()
    
    render(<Textarea label="Multi-line Textarea" />)
    
    const textarea = screen.getByLabelText(/multi-line textarea/i)
    await user.type(textarea, 'Line 1{enter}Line 2{enter}Line 3')
    
    expect(textarea).toHaveValue('Line 1\nLine 2\nLine 3')
  })

  it('renders disabled state correctly', () => {
    render(<Textarea label="Disabled Textarea" disabled />)
    
    const textarea = screen.getByLabelText(/disabled textarea/i)
    expect(textarea).toBeDisabled()
    expect(textarea).toHaveClass('opacity-50', 'cursor-not-allowed')
  })

  it('renders required state correctly', () => {
    render(<Textarea label="Required Textarea" required />)
    
    const textarea = screen.getByLabelText(/required textarea/i)
    expect(textarea).toBeRequired()
    expect(screen.getByText('*')).toBeInTheDocument()
  })

  it('renders error state correctly', () => {
    render(<Textarea label="Error Textarea" error="This field is required" />)
    
    const textarea = screen.getByLabelText(/error textarea/i)
    expect(textarea).toHaveClass('border-red-500')
    expect(screen.getByText('This field is required')).toBeInTheDocument()
  })

  it('renders success state correctly', () => {
    render(<Textarea label="Success Textarea" success />)
    
    const textarea = screen.getByLabelText(/success textarea/i)
    expect(textarea).toHaveClass('border-green-500')
  })

  it('renders help text when provided', () => {
    render(<Textarea label="Textarea with Help" helpText="This is helpful information" />)
    
    expect(screen.getByText('This is helpful information')).toBeInTheDocument()
  })

  it('renders with custom rows', () => {
    render(<Textarea label="Custom Rows" rows={10} />)
    
    const textarea = screen.getByLabelText(/custom rows/i)
    expect(textarea).toHaveAttribute('rows', '10')
  })

  it('renders with custom cols', () => {
    render(<Textarea label="Custom Cols" cols={50} />)
    
    const textarea = screen.getByLabelText(/custom cols/i)
    expect(textarea).toHaveAttribute('cols', '50')
  })

  it('supports resize behavior', () => {
    const { rerender } = render(<Textarea label="Resizable" resize="both" />)
    
    let textarea = screen.getByLabelText(/resizable/i)
    expect(textarea).toHaveClass('resize')
    
    rerender(<Textarea label="Resizable" resize="vertical" />)
    textarea = screen.getByLabelText(/resizable/i)
    expect(textarea).toHaveClass('resize-y')
    
    rerender(<Textarea label="Resizable" resize="horizontal" />)
    textarea = screen.getByLabelText(/resizable/i)
    expect(textarea).toHaveClass('resize-x')
    
    rerender(<Textarea label="Resizable" resize="none" />)
    textarea = screen.getByLabelText(/resizable/i)
    expect(textarea).toHaveClass('resize-none')
  })

  it('renders with custom className', () => {
    render(<Textarea label="Custom Textarea" className="custom-textarea-class" />)
    
    const textarea = screen.getByLabelText(/custom textarea/i)
    expect(textarea).toHaveClass('custom-textarea-class')
  })

  it('supports controlled value', () => {
    const { rerender } = render(<Textarea label="Controlled Textarea" value="initial text" onChange={() => {}} />)
    
    const textarea = screen.getByLabelText(/controlled textarea/i)
    expect(textarea).toHaveValue('initial text')
    
    rerender(<Textarea label="Controlled Textarea" value="updated text" onChange={() => {}} />)
    expect(textarea).toHaveValue('updated text')
  })

  it('supports uncontrolled textarea with defaultValue', () => {
    render(<Textarea label="Uncontrolled Textarea" defaultValue="default text" />)
    
    const textarea = screen.getByLabelText(/uncontrolled textarea/i)
    expect(textarea).toHaveValue('default text')
  })

  it('handles focus and blur events', async () => {
    const user = userEvent.setup()
    const handleFocus = vi.fn()
    const handleBlur = vi.fn()
    
    render(<Textarea label="Focus Textarea" onFocus={handleFocus} onBlur={handleBlur} />)
    
    const textarea = screen.getByLabelText(/focus textarea/i)
    
    await user.click(textarea)
    expect(handleFocus).toHaveBeenCalledTimes(1)
    
    await user.tab()
    expect(handleBlur).toHaveBeenCalledTimes(1)
  })

  it('supports maxLength attribute', () => {
    render(<Textarea label="Max Length" maxLength={100} />)
    
    const textarea = screen.getByLabelText(/max length/i)
    expect(textarea).toHaveAttribute('maxlength', '100')
  })

  it('supports minLength attribute', () => {
    render(<Textarea label="Min Length" minLength={10} />)
    
    const textarea = screen.getByLabelText(/min length/i)
    expect(textarea).toHaveAttribute('minlength', '10')
  })

  it('has proper accessibility attributes', () => {
    render(<Textarea label="Accessible Textarea" aria-describedby="help-text" />)
    
    const textarea = screen.getByLabelText(/accessible textarea/i)
    expect(textarea).toHaveAttribute('aria-describedby', 'help-text')
  })

  it('links label to textarea correctly', () => {
    render(<Textarea label="Linked Textarea" />)
    
    const label = screen.getByText('Linked Textarea')
    const textarea = screen.getByLabelText(/linked textarea/i)
    
    expect(label).toHaveAttribute('for', textarea.id)
  })

  it('supports autoFocus', () => {
    render(<Textarea label="Auto Focus" autoFocus />)
    
    const textarea = screen.getByLabelText(/auto focus/i)
    expect(textarea).toHaveFocus()
  })

  it('supports readonly state', () => {
    render(<Textarea label="Readonly Textarea" readOnly value="readonly text" />)
    
    const textarea = screen.getByLabelText(/readonly textarea/i)
    expect(textarea).toHaveAttribute('readonly')
    expect(textarea).toHaveValue('readonly text')
  })

  it('handles keyboard navigation correctly', async () => {
    const user = userEvent.setup()
    
    render(
      <div>
        <Textarea label="First Textarea" />
        <Textarea label="Second Textarea" />
      </div>
    )
    
    const firstTextarea = screen.getByLabelText(/first textarea/i)
    const secondTextarea = screen.getByLabelText(/second textarea/i)
    
    // Tab through textareas
    await user.tab()
    expect(firstTextarea).toHaveFocus()
    
    await user.tab()
    expect(secondTextarea).toHaveFocus()
  })

  it('supports character counter display', () => {
    render(<Textarea label="Character Counter" maxLength={100} showCharacterCount />)
    
    expect(screen.getByText('0 / 100')).toBeInTheDocument()
  })

  it('updates character counter on input', async () => {
    const user = userEvent.setup()
    
    render(<Textarea label="Character Counter" maxLength={100} showCharacterCount />)
    
    const textarea = screen.getByLabelText(/character counter/i)
    await user.type(textarea, 'Hello')
    
    expect(screen.getByText('5 / 100')).toBeInTheDocument()
  })

  it('supports auto-resize functionality', async () => {
    const user = userEvent.setup()
    
    render(<Textarea label="Auto Resize" autoResize />)
    
    const textarea = screen.getByLabelText(/auto resize/i)
    
    // Type multiple lines to trigger resize
    await user.type(textarea, 'Line 1{enter}Line 2{enter}Line 3{enter}Line 4{enter}Line 5')
    
    // The textarea should have appropriate styling for auto-resize
    expect(textarea).toHaveClass('resize-none')
  })
})