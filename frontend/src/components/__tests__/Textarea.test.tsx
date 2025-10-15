import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import Textarea from '../Textarea';

describe('Textarea Component', () => {
  describe('Basic Rendering', () => {
    it('renders as a textarea element', () => {
      render(<Textarea />);
      const textarea = screen.getByRole('textbox');
      expect(textarea.tagName).toBe('TEXTAREA');
    });

    it('renders with default classes', () => {
      render(<Textarea />);
      const textarea = screen.getByRole('textbox');
      expect(textarea).toHaveClass('px-3', 'py-2', 'border', 'rounded');
    });
  });

  describe('Placeholder', () => {
    it('renders with placeholder text', () => {
      render(<Textarea placeholder="Enter your text here" />);
      const textarea = screen.getByPlaceholderText('Enter your text here');
      expect(textarea).toBeInTheDocument();
    });

    it('renders without placeholder when not provided', () => {
      render(<Textarea />);
      const textarea = screen.getByRole('textbox');
      expect(textarea).not.toHaveAttribute('placeholder');
    });

    it('renders with empty placeholder', () => {
      render(<Textarea placeholder="" />);
      const textarea = screen.getByRole('textbox');
      expect(textarea).toHaveAttribute('placeholder', '');
    });
  });

  describe('Value and Controlled Input', () => {
    it('renders with initial value', () => {
      render(<Textarea value="Initial text" onChange={() => {}} />);
      const textarea = screen.getByRole('textbox') as HTMLTextAreaElement;
      expect(textarea.value).toBe('Initial text');
    });

    it('renders with empty value', () => {
      render(<Textarea value="" onChange={() => {}} />);
      const textarea = screen.getByRole('textbox') as HTMLTextAreaElement;
      expect(textarea.value).toBe('');
    });

    it('calls onChange when value changes', async () => {
      const handleChange = jest.fn();
      render(<Textarea value="" onChange={handleChange} />);
      const textarea = screen.getByRole('textbox');

      await userEvent.type(textarea, 'Hello');

      expect(handleChange).toHaveBeenCalled();
      expect(handleChange).toHaveBeenCalledTimes(5); // Once per character
    });

    it('passes correct event to onChange', async () => {
      const handleChange = jest.fn();
      render(<Textarea value="" onChange={handleChange} />);
      const textarea = screen.getByRole('textbox');

      await userEvent.type(textarea, 'A');

      expect(handleChange).toHaveBeenCalled();
      const lastCall = handleChange.mock.calls[handleChange.mock.calls.length - 1][0];
      expect(lastCall.target).toBe(textarea);
    });

    it('works as controlled component', async () => {
      const ControlledTextarea = () => {
        const [value, setValue] = React.useState('');
        return (
          <Textarea
            value={value}
            onChange={(e) => setValue(e.target.value)}
            placeholder="Type here"
          />
        );
      };

      render(<ControlledTextarea />);
      const textarea = screen.getByRole('textbox') as HTMLTextAreaElement;

      await userEvent.type(textarea, 'Test text');

      expect(textarea.value).toBe('Test text');
    });
  });

  describe('Custom Styling', () => {
    it('applies custom className', () => {
      render(<Textarea className="custom-class" />);
      const textarea = screen.getByRole('textbox');
      expect(textarea).toHaveClass('custom-class');
    });

    it('applies multiple custom classes', () => {
      render(<Textarea className="class1 class2 class3" />);
      const textarea = screen.getByRole('textbox');
      expect(textarea).toHaveClass('class1', 'class2', 'class3');
    });

    it('preserves default classes when adding custom className', () => {
      render(<Textarea className="custom" />);
      const textarea = screen.getByRole('textbox');
      expect(textarea).toHaveClass('px-3', 'py-2', 'border', 'rounded', 'custom');
    });

    it('handles empty className prop', () => {
      render(<Textarea className="" />);
      const textarea = screen.getByRole('textbox');
      expect(textarea).toHaveClass('px-3', 'py-2', 'border', 'rounded');
    });

    it('handles undefined className prop', () => {
      render(<Textarea />);
      const textarea = screen.getByRole('textbox');
      expect(textarea).toHaveClass('px-3', 'py-2', 'border', 'rounded');
    });
  });

  describe('User Interactions', () => {
    it('handles typing', async () => {
      const ControlledTextarea = () => {
        const [value, setValue] = React.useState('');
        return <Textarea value={value} onChange={(e) => setValue(e.target.value)} />;
      };

      render(<ControlledTextarea />);
      const textarea = screen.getByRole('textbox') as HTMLTextAreaElement;

      await userEvent.type(textarea, 'Hello World');

      expect(textarea.value).toBe('Hello World');
    });

    it('handles multiline text', async () => {
      const ControlledTextarea = () => {
        const [value, setValue] = React.useState('');
        return <Textarea value={value} onChange={(e) => setValue(e.target.value)} />;
      };

      render(<ControlledTextarea />);
      const textarea = screen.getByRole('textbox') as HTMLTextAreaElement;

      await userEvent.type(textarea, 'Line 1{Enter}Line 2{Enter}Line 3');

      expect(textarea.value).toBe('Line 1\nLine 2\nLine 3');
    });

    it('handles backspace', async () => {
      const ControlledTextarea = () => {
        const [value, setValue] = React.useState('Hello');
        return <Textarea value={value} onChange={(e) => setValue(e.target.value)} />;
      };

      render(<ControlledTextarea />);
      const textarea = screen.getByRole('textbox') as HTMLTextAreaElement;

      await userEvent.type(textarea, '{Backspace}');

      expect(textarea.value).toBe('Hell');
    });

    it('handles clear all text', async () => {
      const ControlledTextarea = () => {
        const [value, setValue] = React.useState('Some text to clear');
        return <Textarea value={value} onChange={(e) => setValue(e.target.value)} />;
      };

      render(<ControlledTextarea />);
      const textarea = screen.getByRole('textbox') as HTMLTextAreaElement;

      await userEvent.clear(textarea);

      expect(textarea.value).toBe('');
    });

    it('handles focus and blur events', () => {
      render(<Textarea />);
      const textarea = screen.getByRole('textbox');

      textarea.focus();
      expect(textarea).toHaveFocus();

      textarea.blur();
      expect(textarea).not.toHaveFocus();
    });
  });

  describe('Edge Cases', () => {
    it('handles undefined value', () => {
      render(<Textarea value={undefined} />);
      const textarea = screen.getByRole('textbox') as HTMLTextAreaElement;
      expect(textarea.value).toBe('');
    });

    it('handles missing onChange prop', () => {
      render(<Textarea value="Test" />);
      const textarea = screen.getByRole('textbox');
      expect(textarea).toBeInTheDocument();
    });

    it('handles very long text input', async () => {
      const longText = 'A'.repeat(5000);
      const ControlledTextarea = () => {
        const [value, setValue] = React.useState('');
        return <Textarea value={value} onChange={(e) => setValue(e.target.value)} />;
      };

      render(<ControlledTextarea />);
      const textarea = screen.getByRole('textbox') as HTMLTextAreaElement;

      fireEvent.change(textarea, { target: { value: longText } });

      expect(textarea.value).toBe(longText);
    });

    it('handles special characters', async () => {
      const specialChars = '!@#$%^&*()_+-=[]{}|;:\'",.<>?/~`';
      const ControlledTextarea = () => {
        const [value, setValue] = React.useState('');
        return <Textarea value={value} onChange={(e) => setValue(e.target.value)} />;
      };

      render(<ControlledTextarea />);
      const textarea = screen.getByRole('textbox') as HTMLTextAreaElement;

      fireEvent.change(textarea, { target: { value: specialChars } });

      expect(textarea.value).toBe(specialChars);
    });

    it('handles unicode characters', async () => {
      const unicode = 'Hello 世界 🌍 café';
      const ControlledTextarea = () => {
        const [value, setValue] = React.useState('');
        return <Textarea value={value} onChange={(e) => setValue(e.target.value)} />;
      };

      render(<ControlledTextarea />);
      const textarea = screen.getByRole('textbox') as HTMLTextAreaElement;

      fireEvent.change(textarea, { target: { value: unicode } });

      expect(textarea.value).toBe(unicode);
    });
  });

  describe('Accessibility', () => {
    it('has proper textarea role', () => {
      render(<Textarea />);
      const textarea = screen.getByRole('textbox');
      expect(textarea).toBeInTheDocument();
    });

    it('can be focused', () => {
      render(<Textarea />);
      const textarea = screen.getByRole('textbox');
      textarea.focus();
      expect(textarea).toHaveFocus();
    });

    it('supports keyboard interaction', async () => {
      const ControlledTextarea = () => {
        const [value, setValue] = React.useState('');
        return <Textarea value={value} onChange={(e) => setValue(e.target.value)} />;
      };

      render(<ControlledTextarea />);
      const textarea = screen.getByRole('textbox');

      textarea.focus();
      await userEvent.keyboard('Hello');

      expect((textarea as HTMLTextAreaElement).value).toBe('Hello');
    });
  });

  describe('Performance and Rendering', () => {
    it('renders without errors', () => {
      expect(() => render(<Textarea />)).not.toThrow();
    });

    it('handles rapid re-renders', () => {
      const { rerender } = render(<Textarea value="Initial" />);

      for (let i = 0; i < 100; i++) {
        rerender(<Textarea value={`Value ${i}`} />);
      }

      const textarea = screen.getByRole('textbox') as HTMLTextAreaElement;
      expect(textarea.value).toBe('Value 99');
    });

    it('handles rapid value changes', async () => {
      const ControlledTextarea = () => {
        const [value, setValue] = React.useState('');
        return <Textarea value={value} onChange={(e) => setValue(e.target.value)} />;
      };

      render(<ControlledTextarea />);
      const textarea = screen.getByRole('textbox');

      await userEvent.type(textarea, 'abcdefghijklmnopqrstuvwxyz');

      expect((textarea as HTMLTextAreaElement).value).toBe('abcdefghijklmnopqrstuvwxyz');
    });
  });
});
