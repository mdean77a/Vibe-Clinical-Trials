import React from 'react';
import { render, screen } from '@testing-library/react';
import Card from '../Card';

describe('Card Component', () => {
  describe('Basic Rendering', () => {
    it('renders children correctly', () => {
      render(
        <Card>
          <p>Test content</p>
        </Card>
      );
      
      expect(screen.getByText('Test content')).toBeInTheDocument();
    });

    it('renders with default classes', () => {
      const { container } = render(
        <Card>
          <span>Content</span>
        </Card>
      );
      
      const cardElement = container.firstChild as HTMLElement;
      expect(cardElement).toHaveClass('p-4', 'bg-white', 'shadow', 'rounded');
    });

    it('renders as a div element', () => {
      const { container } = render(
        <Card>
          <span>Content</span>
        </Card>
      );
      
      expect(container.firstChild?.nodeName).toBe('DIV');
    });
  });

  describe('Custom Styling', () => {
    it('applies custom className', () => {
      const customClass = 'custom-card-class';
      const { container } = render(
        <Card className={customClass}>
          <span>Content</span>
        </Card>
      );
      
      const cardElement = container.firstChild as HTMLElement;
      expect(cardElement).toHaveClass(customClass);
      // Should still have default classes
      expect(cardElement).toHaveClass('p-4', 'bg-white', 'shadow', 'rounded');
    });

    it('applies multiple custom classes', () => {
      const customClasses = 'class1 class2 class3';
      const { container } = render(
        <Card className={customClasses}>
          <span>Content</span>
        </Card>
      );
      
      const cardElement = container.firstChild as HTMLElement;
      expect(cardElement).toHaveClass('class1', 'class2', 'class3');
    });

    it('applies custom inline styles', () => {
      const customStyle: React.CSSProperties = {
        backgroundColor: 'red',
        border: '2px solid blue',
        margin: '10px',
        padding: '20px'
      };
      
      const { container } = render(
        <Card style={customStyle}>
          <span>Content</span>
        </Card>
      );
      
      const cardElement = container.firstChild as HTMLElement;
      expect(cardElement).toHaveStyle({
        backgroundColor: 'red',
        border: '2px solid blue',
        margin: '10px',
        padding: '20px'
      });
    });

    it('combines custom className and style', () => {
      const customClass = 'special-card';
      const customStyle: React.CSSProperties = {
        fontSize: '18px',
        color: 'purple'
      };
      
      const { container } = render(
        <Card className={customClass} style={customStyle}>
          <span>Content</span>
        </Card>
      );
      
      const cardElement = container.firstChild as HTMLElement;
      expect(cardElement).toHaveClass('special-card');
      expect(cardElement).toHaveStyle({
        fontSize: '18px',
        color: 'purple'
      });
    });
  });

  describe('Children Rendering', () => {
    it('renders text children', () => {
      render(
        <Card>
          Simple text content
        </Card>
      );
      
      expect(screen.getByText('Simple text content')).toBeInTheDocument();
    });

    it('renders single React element child', () => {
      render(
        <Card>
          <button>Click me</button>
        </Card>
      );
      
      expect(screen.getByRole('button', { name: 'Click me' })).toBeInTheDocument();
    });

    it('renders multiple children', () => {
      render(
        <Card>
          <h1>Title</h1>
          <p>Description</p>
          <button>Action</button>
        </Card>
      );
      
      expect(screen.getByRole('heading', { name: 'Title' })).toBeInTheDocument();
      expect(screen.getByText('Description')).toBeInTheDocument();
      expect(screen.getByRole('button', { name: 'Action' })).toBeInTheDocument();
    });

    it('renders nested components', () => {
      render(
        <Card>
          <div>
            <Card>
              <span>Nested card content</span>
            </Card>
          </div>
        </Card>
      );
      
      expect(screen.getByText('Nested card content')).toBeInTheDocument();
    });

    it('renders complex JSX structure', () => {
      render(
        <Card>
          <div>
            <header>
              <h2>Card Header</h2>
            </header>
            <main>
              <p>Main content area</p>
              <ul>
                <li>Item 1</li>
                <li>Item 2</li>
              </ul>
            </main>
            <footer>
              <button>Save</button>
              <button>Cancel</button>
            </footer>
          </div>
        </Card>
      );
      
      expect(screen.getByRole('heading', { name: 'Card Header' })).toBeInTheDocument();
      expect(screen.getByText('Main content area')).toBeInTheDocument();
      expect(screen.getByText('Item 1')).toBeInTheDocument();
      expect(screen.getByText('Item 2')).toBeInTheDocument();
      expect(screen.getByRole('button', { name: 'Save' })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: 'Cancel' })).toBeInTheDocument();
    });
  });

  describe('Edge Cases', () => {
    it('handles empty className prop', () => {
      const { container } = render(
        <Card className="">
          <span>Content</span>
        </Card>
      );
      
      const cardElement = container.firstChild as HTMLElement;
      expect(cardElement).toHaveClass('p-4', 'bg-white', 'shadow', 'rounded');
    });

    it('handles undefined className prop', () => {
      const { container } = render(
        <Card className={undefined}>
          <span>Content</span>
        </Card>
      );
      
      const cardElement = container.firstChild as HTMLElement;
      expect(cardElement).toHaveClass('p-4', 'bg-white', 'shadow', 'rounded');
    });

    it('handles empty style object', () => {
      const { container } = render(
        <Card style={{}}>
          <span>Content</span>
        </Card>
      );
      
      const cardElement = container.firstChild as HTMLElement;
      expect(cardElement).toBeInTheDocument();
    });

    it('handles undefined style prop', () => {
      const { container } = render(
        <Card style={undefined}>
          <span>Content</span>
        </Card>
      );
      
      const cardElement = container.firstChild as HTMLElement;
      expect(cardElement).toBeInTheDocument();
    });

    it('renders with null children', () => {
      const { container } = render(
        <Card>
          {null}
        </Card>
      );
      
      const cardElement = container.firstChild as HTMLElement;
      expect(cardElement).toBeInTheDocument();
      expect(cardElement).toBeEmptyDOMElement();
    });

    it('renders with undefined children', () => {
      const { container } = render(
        <Card>
          {undefined}
        </Card>
      );
      
      const cardElement = container.firstChild as HTMLElement;
      expect(cardElement).toBeInTheDocument();
      expect(cardElement).toBeEmptyDOMElement();
    });

    it('renders with conditional children', () => {
      const showContent = true;
      render(
        <Card>
          {showContent && <p>Conditional content</p>}
          {!showContent && <p>Alternative content</p>}
        </Card>
      );
      
      expect(screen.getByText('Conditional content')).toBeInTheDocument();
      expect(screen.queryByText('Alternative content')).not.toBeInTheDocument();
    });
  });

  describe('Accessibility', () => {
    it('maintains proper DOM structure', () => {
      const { container } = render(
        <Card>
          <h1>Accessible heading</h1>
          <p>Accessible content</p>
        </Card>
      );
      
      expect(screen.getByRole('heading', { level: 1 })).toBeInTheDocument();
      expect(container.firstChild).toHaveTextContent('Accessible heading');
      expect(container.firstChild).toHaveTextContent('Accessible content');
    });

    it('preserves child component accessibility attributes', () => {
      render(
        <Card>
          <button aria-label="Close dialog" aria-pressed="false">
            ×
          </button>
        </Card>
      );
      
      const button = screen.getByRole('button', { name: 'Close dialog' });
      expect(button).toHaveAttribute('aria-pressed', 'false');
    });

    it('applies custom className correctly', () => {
      const { container } = render(
        <Card className="custom-card">
          <p>Content with custom class</p>
        </Card>
      );
      
      const cardElement = container.firstChild as HTMLElement;
      expect(cardElement).toHaveClass('custom-card');
      expect(cardElement).toHaveClass('p-4', 'bg-white', 'shadow', 'rounded');
    });
  });

  describe('Performance and Rendering', () => {
    it('renders without errors', () => {
      expect(() => {
        render(
          <Card>
            <div>Test content</div>
          </Card>
        );
      }).not.toThrow();
    });

    it('handles rapid re-renders', () => {
      const { rerender } = render(
        <Card>
          <span>Initial content</span>
        </Card>
      );
      
      expect(screen.getByText('Initial content')).toBeInTheDocument();
      
      rerender(
        <Card>
          <span>Updated content</span>
        </Card>
      );
      
      expect(screen.getByText('Updated content')).toBeInTheDocument();
      expect(screen.queryByText('Initial content')).not.toBeInTheDocument();
    });

    it('handles dynamic className changes', () => {
      const { rerender, container } = render(
        <Card className="initial-class">
          <span>Content</span>
        </Card>
      );
      
      let cardElement = container.firstChild as HTMLElement;
      expect(cardElement).toHaveClass('initial-class');
      
      rerender(
        <Card className="updated-class">
          <span>Content</span>
        </Card>
      );
      
      cardElement = container.firstChild as HTMLElement;
      expect(cardElement).toHaveClass('updated-class');
      expect(cardElement).not.toHaveClass('initial-class');
    });

    it('handles dynamic style changes', () => {
      const { rerender, container } = render(
        <Card style={{ color: 'red' }}>
          <span>Content</span>
        </Card>
      );
      
      let cardElement = container.firstChild as HTMLElement;
      expect(cardElement).toHaveStyle({ color: 'red' });
      
      rerender(
        <Card style={{ color: 'blue', fontSize: '16px' }}>
          <span>Content</span>
        </Card>
      );
      
      cardElement = container.firstChild as HTMLElement;
      expect(cardElement).toHaveStyle({ color: 'blue', fontSize: '16px' });
    });
  });
}); 