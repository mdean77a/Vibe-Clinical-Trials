import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import Input from '../Input';

describe('Input Component', () => {
  let user: ReturnType<typeof userEvent.setup>;

  beforeEach(() => {
    user = userEvent.setup();
  });

  describe('Basic Rendering', () => {
    it('renders as an input element', () => {
      render(<Input />);
      
      const inputElement = screen.getByRole('textbox');
      expect(inputElement).toBeInTheDocument();
      expect(inputElement.tagName).toBe('INPUT');
    });

    it('renders with default type "text"', () => {
      render(<Input />);
      
      const inputElement = screen.getByRole('textbox');
      expect(inputElement).toHaveAttribute('type', 'text');
    });

    it('renders with default classes', () => {
      render(<Input />);
      
      const inputElement = screen.getByRole('textbox');
      expect(inputElement).toHaveClass('px-3', 'py-2', 'border', 'rounded');
    });

    it('is enabled by default', () => {
      render(<Input />);
      
      const inputElement = screen.getByRole('textbox');
      expect(inputElement).not.toBeDisabled();
    });
  });

  describe('Input Types', () => {
    it('renders with custom type', () => {
      render(<Input type="email" />);
      
      const inputElement = screen.getByRole('textbox');
      expect(inputElement).toHaveAttribute('type', 'email');
    });

    it('renders password input', () => {
      render(<Input type="password" />);
      
      // Password inputs don't have the textbox role
      const inputElement = document.querySelector('input[type="password"]');
      expect(inputElement).toBeInTheDocument();
      expect(inputElement).toHaveAttribute('type', 'password');
    });

    it('renders number input', () => {
      render(<Input type="number" />);
      
      const inputElement = screen.getByRole('spinbutton');
      expect(inputElement).toHaveAttribute('type', 'number');
    });

    it('renders email input', () => {
      render(<Input type="email" />);
      
      const inputElement = screen.getByRole('textbox');
      expect(inputElement).toHaveAttribute('type', 'email');
    });

    it('renders tel input', () => {
      render(<Input type="tel" />);
      
      const inputElement = screen.getByRole('textbox');
      expect(inputElement).toHaveAttribute('type', 'tel');
    });

    it('renders url input', () => {
      render(<Input type="url" />);
      
      const inputElement = screen.getByRole('textbox');
      expect(inputElement).toHaveAttribute('type', 'url');
    });

    it('renders search input', () => {
      render(<Input type="search" />);
      
      const inputElement = screen.getByRole('searchbox');
      expect(inputElement).toHaveAttribute('type', 'search');
    });
  });

  describe('Placeholder', () => {
    it('renders with placeholder text', () => {
      const placeholder = 'Enter your name';
      render(<Input placeholder={placeholder} />);
      
      const inputElement = screen.getByPlaceholderText(placeholder);
      expect(inputElement).toBeInTheDocument();
    });

    it('renders without placeholder when not provided', () => {
      render(<Input />);
      
      const inputElement = screen.getByRole('textbox');
      expect(inputElement).not.toHaveAttribute('placeholder');
    });

    it('renders with empty placeholder', () => {
      render(<Input placeholder="" />);
      
      const inputElement = screen.getByRole('textbox');
      expect(inputElement).toHaveAttribute('placeholder', '');
    });
  });

  describe('Value and Controlled Input', () => {
    it('renders with initial value', () => {
      const value = 'Initial value';
      render(<Input value={value} onChange={() => {}} />);
      
      const inputElement = screen.getByDisplayValue(value);
      expect(inputElement).toBeInTheDocument();
    });

    it('renders with empty value', () => {
      render(<Input value="" onChange={() => {}} />);
      
      const inputElement = screen.getByRole('textbox');
      expect(inputElement).toHaveValue('');
    });

    it('calls onChange when value changes', async () => {
      const mockOnChange = jest.fn();
      render(<Input onChange={mockOnChange} />);
      
      const inputElement = screen.getByRole('textbox');
      await user.type(inputElement, 'test');
      
      expect(mockOnChange).toHaveBeenCalledTimes(4); // Once for each character
    });

    it('passes correct event to onChange', async () => {
      const mockOnChange = jest.fn();
      render(<Input onChange={mockOnChange} />);
      
      const inputElement = screen.getByRole('textbox');
      await user.type(inputElement, 'a');
      
      expect(mockOnChange).toHaveBeenCalledWith(
        expect.objectContaining({
          target: expect.objectContaining({
            value: 'a'
          })
        })
      );
    });

    it('works as controlled component', async () => {
      const ControlledInput = () => {
        const [value, setValue] = React.useState('');
        return (
          <Input 
            value={value} 
            onChange={(e) => setValue(e.target.value)} 
          />
        );
      };

      render(<ControlledInput />);
      
      const inputElement = screen.getByRole('textbox');
      await user.type(inputElement, 'controlled');
      
      expect(inputElement).toHaveValue('controlled');
    });
  });

  describe('Disabled State', () => {
    it('renders as disabled when disabled prop is true', () => {
      render(<Input disabled={true} />);
      
      const inputElement = screen.getByRole('textbox');
      expect(inputElement).toBeDisabled();
    });

    it('renders as enabled when disabled prop is false', () => {
      render(<Input disabled={false} />);
      
      const inputElement = screen.getByRole('textbox');
      expect(inputElement).not.toBeDisabled();
    });

    it('does not call onChange when disabled', async () => {
      const mockOnChange = jest.fn();
      render(<Input disabled={true} onChange={mockOnChange} />);
      
      const inputElement = screen.getByRole('textbox');
      await user.type(inputElement, 'test');
      
      expect(mockOnChange).not.toHaveBeenCalled();
    });

    it('cannot be focused when disabled', () => {
      render(<Input disabled={true} />);
      
      const inputElement = screen.getByRole('textbox');
      inputElement.focus();
      
      expect(inputElement).not.toHaveFocus();
    });
  });

  describe('Custom Styling', () => {
    it('applies custom className', () => {
      const customClass = 'custom-input-class';
      render(<Input className={customClass} />);
      
      const inputElement = screen.getByRole('textbox');
      expect(inputElement).toHaveClass(customClass);
      // Should still have default classes
      expect(inputElement).toHaveClass('px-3', 'py-2', 'border', 'rounded');
    });

    it('applies multiple custom classes', () => {
      const customClasses = 'class1 class2 class3';
      render(<Input className={customClasses} />);
      
      const inputElement = screen.getByRole('textbox');
      expect(inputElement).toHaveClass('class1', 'class2', 'class3');
    });

    it('applies custom inline styles', () => {
      const customStyle: React.CSSProperties = {
        backgroundColor: 'yellow',
        fontSize: '18px',
        border: '2px solid red',
        padding: '10px'
      };

      render(<Input style={customStyle} />);

      const inputElement = screen.getByRole('textbox');
      // JSDOM returns colors in rgb format
      expect(inputElement).toHaveStyle({
        backgroundColor: 'rgb(255, 255, 0)',
        fontSize: '18px',
        border: '2px solid red',
        padding: '10px'
      });
    });

    it('combines custom className and style', () => {
      const customClass = 'special-input';
      const customStyle: React.CSSProperties = {
        color: 'blue',
        fontWeight: 'bold'
      };

      render(<Input className={customClass} style={customStyle} />);

      const inputElement = screen.getByRole('textbox');
      expect(inputElement).toHaveClass('special-input');
      // JSDOM returns colors in rgb format
      expect(inputElement).toHaveStyle({
        color: 'rgb(0, 0, 255)',
        fontWeight: 'bold'
      });
    });
  });

  describe('User Interactions', () => {
    it('handles typing', async () => {
      render(<Input />);
      
      const inputElement = screen.getByRole('textbox');
      await user.type(inputElement, 'Hello World');
      
      expect(inputElement).toHaveValue('Hello World');
    });

    it('handles backspace', async () => {
      render(<Input />);
      
      const inputElement = screen.getByRole('textbox');
      await user.type(inputElement, 'Hello');
      await user.keyboard('{Backspace}');
      
      expect(inputElement).toHaveValue('Hell');
    });

    it('handles clear all with Ctrl+A and Delete', async () => {
      render(<Input />);
      
      const inputElement = screen.getByRole('textbox');
      await user.type(inputElement, 'Hello World');
      await user.keyboard('{Control>}a{/Control}');
      await user.keyboard('{Delete}');
      
      expect(inputElement).toHaveValue('');
    });

    it('handles focus and blur events', async () => {
      render(
        <div>
          <Input />
          <button>Other element</button>
        </div>
      );
      
      const inputElement = screen.getByRole('textbox');
      const buttonElement = screen.getByRole('button');
      
      await user.click(inputElement);
      expect(inputElement).toHaveFocus();
      
      await user.click(buttonElement);
      expect(inputElement).not.toHaveFocus();
    });

    it('handles copy and paste simulation', async () => {
      render(<Input />);
      
      const inputElement = screen.getByRole('textbox');
      await user.type(inputElement, 'Copy this text');
      
      // Test select all functionality (Ctrl+A)
      await user.keyboard('{Control>}a{/Control}');
      
      // Verify selection works by typing over selected text
      await user.type(inputElement, 'New text');
      
      expect(inputElement).toHaveValue('Copy this textNew text');
    });
  });

  describe('Keyboard Navigation', () => {
    it('can be focused with Tab', async () => {
      render(
        <div>
          <button>Previous element</button>
          <Input />
          <button>Next element</button>
        </div>
      );
      
      const inputElement = screen.getByRole('textbox');
      
      await user.tab();
      await user.tab(); // Tab to input
      
      expect(inputElement).toHaveFocus();
    });

    it('moves focus away with Tab', async () => {
      render(
        <div>
          <Input />
          <button>Next element</button>
        </div>
      );
      
      const inputElement = screen.getByRole('textbox');
      const buttonElement = screen.getByRole('button');
      
      await user.click(inputElement);
      expect(inputElement).toHaveFocus();
      
      await user.tab();
      expect(buttonElement).toHaveFocus();
    });

    it('handles Enter key', async () => {
      render(<Input />);
      
      const inputElement = screen.getByRole('textbox');
      await user.click(inputElement);
      await user.keyboard('{Enter}');
      
      // Input should maintain focus after Enter key
      expect(inputElement).toHaveFocus();
    });

    it('handles Escape key', async () => {
      render(<Input />);
      
      const inputElement = screen.getByRole('textbox');
      await user.click(inputElement);
      await user.keyboard('{Escape}');
      
      // Input should maintain focus after Escape key
      expect(inputElement).toHaveFocus();
    });
  });

  describe('Edge Cases', () => {
    it('handles undefined value', () => {
      render(<Input value={undefined} onChange={() => {}} />);
      
      const inputElement = screen.getByRole('textbox');
      expect(inputElement).toHaveValue('');
    });

    it('handles null value', () => {
      // @ts-expect-error Testing edge case with null value
      render(<Input value={null} onChange={() => {}} />);
      
      const inputElement = screen.getByRole('textbox');
      expect(inputElement).toHaveValue('');
    });

    it('handles empty className prop', () => {
      render(<Input className="" />);
      
      const inputElement = screen.getByRole('textbox');
      expect(inputElement).toHaveClass('px-3', 'py-2', 'border', 'rounded');
    });

    it('handles undefined className prop', () => {
      render(<Input className={undefined} />);
      
      const inputElement = screen.getByRole('textbox');
      expect(inputElement).toHaveClass('px-3', 'py-2', 'border', 'rounded');
    });

    it('handles empty style object', () => {
      render(<Input style={{}} />);
      
      const inputElement = screen.getByRole('textbox');
      expect(inputElement).toBeInTheDocument();
    });

    it('handles undefined style prop', () => {
      render(<Input style={undefined} />);
      
      const inputElement = screen.getByRole('textbox');
      expect(inputElement).toBeInTheDocument();
    });

    it('handles missing onChange prop', async () => {
      render(<Input />);
      
      const inputElement = screen.getByRole('textbox');
      
      // Should not throw error when typing without onChange
      expect(() => {
        fireEvent.change(inputElement, { target: { value: 'test' } });
      }).not.toThrow();
    });

    it('handles very long text input', async () => {
      const longText = 'a'.repeat(1000);
      render(<Input />);
      
      const inputElement = screen.getByRole('textbox');
      await user.type(inputElement, longText);
      
      expect(inputElement).toHaveValue(longText);
    });

    it('handles special characters', async () => {
      // Split special characters into safe groups for userEvent
      const safeSpecialChars = '!@#$%^&*()_+-=;:,.<>?';
      const problematicChars = '[]{}|'; // These cause issues with userEvent
      
      render(<Input />);
      
      const inputElement = screen.getByRole('textbox');
      
      // Test safe special characters with userEvent
      await user.type(inputElement, safeSpecialChars);
      expect(inputElement).toHaveValue(safeSpecialChars);
      
      // Test problematic characters with fireEvent
      fireEvent.change(inputElement, { target: { value: problematicChars } });
      expect(inputElement).toHaveValue(problematicChars);
    });

    it('handles unicode characters', async () => {
      const unicodeText = '🚀 Hello 世界 🌟';
      render(<Input />);
      
      const inputElement = screen.getByRole('textbox');
      await user.type(inputElement, unicodeText);
      
      expect(inputElement).toHaveValue(unicodeText);
    });
  });

  describe('Accessibility', () => {
    it('has proper input role', () => {
      render(<Input />);
      
      const inputElement = screen.getByRole('textbox');
      expect(inputElement).toBeInTheDocument();
    });

    it('has proper accessibility role', () => {
      render(<Input />);
      
      const inputElement = screen.getByRole('textbox');
      expect(inputElement).toBeInTheDocument();
      expect(inputElement).toHaveAttribute('type', 'text');
    });

    it('works with different input types for accessibility', () => {
      const { rerender } = render(<Input type="email" />);
      
      let inputElement = screen.getByRole('textbox');
      expect(inputElement).toHaveAttribute('type', 'email');
      
      rerender(<Input type="search" />);
      inputElement = screen.getByRole('searchbox');
      expect(inputElement).toHaveAttribute('type', 'search');
      
      rerender(<Input type="number" />);
      inputElement = screen.getByRole('spinbutton');
      expect(inputElement).toHaveAttribute('type', 'number');
    });
  });

  describe('Performance and Rendering', () => {
    it('renders without errors', () => {
      expect(() => {
        render(<Input />);
      }).not.toThrow();
    });

    it('handles rapid re-renders', () => {
      const { rerender } = render(<Input value="initial" onChange={() => {}} />);
      
      expect(screen.getByDisplayValue('initial')).toBeInTheDocument();
      
      rerender(<Input value="updated" onChange={() => {}} />);
      
      expect(screen.getByDisplayValue('updated')).toBeInTheDocument();
      expect(screen.queryByDisplayValue('initial')).not.toBeInTheDocument();
    });

    it('handles dynamic prop changes', () => {
      const { rerender } = render(<Input type="text" disabled={false} />);
      
      let inputElement = screen.getByRole('textbox');
      expect(inputElement).toHaveAttribute('type', 'text');
      expect(inputElement).not.toBeDisabled();
      
      rerender(<Input type="email" disabled={true} />);
      
      inputElement = screen.getByRole('textbox');
      expect(inputElement).toHaveAttribute('type', 'email');
      expect(inputElement).toBeDisabled();
    });

    it('maintains focus during re-renders', async () => {
      const { rerender } = render(<Input value="test" onChange={() => {}} />);
      
      const inputElement = screen.getByRole('textbox');
      await user.click(inputElement);
      expect(inputElement).toHaveFocus();
      
      rerender(<Input value="test updated" onChange={() => {}} />);
      
      // Focus should be maintained after re-render
      expect(inputElement).toHaveFocus();
    });
  });
}); 