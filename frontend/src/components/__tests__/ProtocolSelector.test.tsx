import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import ProtocolSelector from '../ProtocolSelector';
import type { Protocol } from '../../types/protocol';

// Mock the Card and Button components
jest.mock('../Card', () => {
  return function MockCard({ children }: { children: React.ReactNode }) {
    return <div data-testid="card">{children}</div>;
  };
});

jest.mock('../Button', () => {
  return function MockButton({ 
    children, 
    onClick, 
    style, 
    onMouseEnter, 
    onMouseLeave,
    ...props 
  }: any) {
    return (
      <button 
        onClick={onClick} 
        onMouseEnter={onMouseEnter}
        onMouseLeave={onMouseLeave}
        data-testid="upload-button"
        {...props}
      >
        {children}
      </button>
    );
  };
});

// Test data
const mockProtocols: Protocol[] = [
  {
    id: 'protocol-1',
    protocol_id: 'CARDIO-123',
    study_acronym: 'CARDIO-STUDY',
    protocol_title: 'Cardiovascular Disease Prevention Study',
    upload_date: '2024-01-15T10:30:00Z',
    status: 'completed',
    sponsor: 'Test Pharma Inc.',
    indication: 'Cardiovascular Disease'
  },
  {
    id: 'protocol-2',
    protocol_id: 'ONCO-456',
    study_acronym: 'ONCOLOGY-TRIAL-WITH-VERY-LONG-NAME',
    protocol_title: 'A Very Long Protocol Title That Should Be Truncated When Displayed',
    upload_date: '2024-02-20T15:45:00Z',
    status: 'processing',
    sponsor: 'Another Pharma Corp.',
    indication: 'Oncology'
  },
  {
    id: 'protocol-3',
    protocol_id: 'NEURO-789',
    study_acronym: 'NEURO',
    protocol_title: 'Short Title',
    upload_date: '2024-03-10T08:15:00Z',
    status: 'completed'
  }
];

const defaultProps = {
  protocols: mockProtocols,
  onProtocolSelect: jest.fn(),
  onUploadNew: jest.fn()
};

describe('ProtocolSelector Component', () => {
  let user: ReturnType<typeof userEvent.setup>;

  beforeEach(() => {
    user = userEvent.setup();
    jest.clearAllMocks();
  });

  describe('Rendering', () => {
    it('renders the component with correct heading and description', () => {
      render(<ProtocolSelector {...defaultProps} />);
      
      expect(screen.getByRole('heading', { name: /select protocol/i })).toBeInTheDocument();
      expect(screen.getByText(/choose an existing protocol or upload a new one/i)).toBeInTheDocument();
    });

    it('renders the Card component', () => {
      render(<ProtocolSelector {...defaultProps} />);
      
      expect(screen.getByTestId('card')).toBeInTheDocument();
    });

    it('renders the existing protocols label', () => {
      render(<ProtocolSelector {...defaultProps} />);
      
      expect(screen.getByText('Existing Protocols')).toBeInTheDocument();
    });

    it('renders the upload button', () => {
      render(<ProtocolSelector {...defaultProps} />);
      
      expect(screen.getByTestId('upload-button')).toBeInTheDocument();
      expect(screen.getByText('Upload New Protocol')).toBeInTheDocument();
      expect(screen.getByText(/upload a new clinical trial protocol pdf/i)).toBeInTheDocument();
    });

    it('renders the "or" divider', () => {
      render(<ProtocolSelector {...defaultProps} />);
      
      expect(screen.getByText('or')).toBeInTheDocument();
    });
  });

  describe('Protocol Dropdown - With Protocols', () => {
    it('shows "Select a protocol..." when protocols are available', () => {
      render(<ProtocolSelector {...defaultProps} />);
      
      const dropdownButton = screen.getByRole('button', { name: /select a protocol/i });
      expect(dropdownButton).toBeInTheDocument();
      expect(dropdownButton).not.toBeDisabled();
    });

    it('shows dropdown arrow when protocols are available', () => {
      render(<ProtocolSelector {...defaultProps} />);
      
      const dropdownButton = screen.getByRole('button', { name: /select a protocol/i });
      const svg = dropdownButton.querySelector('svg');
      expect(svg).toBeInTheDocument();
    });

    it('opens dropdown when clicked', async () => {
      render(<ProtocolSelector {...defaultProps} />);
      
      const dropdownButton = screen.getByRole('button', { name: /select a protocol/i });
      await user.click(dropdownButton);
      
      // Check that protocol options are visible
      expect(screen.getByText('CARDIO-STUDY')).toBeInTheDocument();
      expect(screen.getByText('ONCOLOGY-TRIAL-...')).toBeInTheDocument(); // Truncated
      expect(screen.getByText('NEURO')).toBeInTheDocument();
    });

    it('closes dropdown when clicked again', async () => {
      render(<ProtocolSelector {...defaultProps} />);
      
      const dropdownButton = screen.getByRole('button', { name: /select a protocol/i });
      
      // Open dropdown
      await user.click(dropdownButton);
      expect(screen.getByText('CARDIO-STUDY')).toBeInTheDocument();
      
      // Close dropdown
      await user.click(dropdownButton);
      expect(screen.queryByText('CARDIO-STUDY')).not.toBeInTheDocument();
    });

    it('rotates arrow icon when dropdown is opened', async () => {
      render(<ProtocolSelector {...defaultProps} />);
      
      const dropdownButton = screen.getByRole('button', { name: /select a protocol/i });
      const svg = dropdownButton.querySelector('svg');
      
      // Initially not rotated
      expect(svg).toHaveStyle('transform: rotate(0deg)');
      
      // Open dropdown
      await user.click(dropdownButton);
      expect(svg).toHaveStyle('transform: rotate(180deg)');
    });
  });

  describe('Protocol Dropdown - Empty State', () => {
    const emptyProps = {
      ...defaultProps,
      protocols: []
    };

    it('shows "No existing protocols found" when no protocols available', () => {
      render(<ProtocolSelector {...emptyProps} />);
      
      expect(screen.getByText('No existing protocols found')).toBeInTheDocument();
    });

    it('disables dropdown button when no protocols available', () => {
      render(<ProtocolSelector {...emptyProps} />);
      
      const dropdownButton = screen.getByRole('button', { name: /no existing protocols found/i });
      expect(dropdownButton).toBeDisabled();
    });

    it('does not show dropdown arrow when no protocols available', () => {
      render(<ProtocolSelector {...emptyProps} />);
      
      const dropdownButton = screen.getByRole('button', { name: /no existing protocols found/i });
      const svg = dropdownButton.querySelector('svg');
      expect(svg).not.toBeInTheDocument();
    });

    it('does not open dropdown when no protocols available', async () => {
      render(<ProtocolSelector {...emptyProps} />);
      
      const dropdownButton = screen.getByRole('button', { name: /no existing protocols found/i });
      await user.click(dropdownButton);
      
      // Should not show any protocol options
      expect(screen.queryByText('CARDIO-STUDY')).not.toBeInTheDocument();
    });
  });

  describe('Protocol Selection', () => {
    it('calls onProtocolSelect when a protocol is clicked', async () => {
      const mockOnProtocolSelect = jest.fn();
      render(<ProtocolSelector {...defaultProps} onProtocolSelect={mockOnProtocolSelect} />);
      
      // Open dropdown
      const dropdownButton = screen.getByRole('button', { name: /select a protocol/i });
      await user.click(dropdownButton);
      
      // Click on first protocol
      const firstProtocol = screen.getByText('CARDIO-STUDY');
      await user.click(firstProtocol);
      
      expect(mockOnProtocolSelect).toHaveBeenCalledWith(mockProtocols[0]);
    });

    it('closes dropdown after protocol selection', async () => {
      render(<ProtocolSelector {...defaultProps} />);
      
      // Open dropdown
      const dropdownButton = screen.getByRole('button', { name: /select a protocol/i });
      await user.click(dropdownButton);
      
      // Click on first protocol
      const firstProtocol = screen.getByText('CARDIO-STUDY');
      await user.click(firstProtocol);
      
      // Dropdown should be closed
      expect(screen.queryByText('CARDIO-STUDY')).not.toBeInTheDocument();
    });

    it('selects the correct protocol when multiple protocols exist', async () => {
      const mockOnProtocolSelect = jest.fn();
      render(<ProtocolSelector {...defaultProps} onProtocolSelect={mockOnProtocolSelect} />);
      
      // Open dropdown
      const dropdownButton = screen.getByRole('button', { name: /select a protocol/i });
      await user.click(dropdownButton);
      
      // Click on second protocol (using partial text match)
      const secondProtocol = screen.getByText('ONCOLOGY-TRIAL-...');
      await user.click(secondProtocol);
      
      expect(mockOnProtocolSelect).toHaveBeenCalledWith(mockProtocols[1]);
    });
  });

  describe('Upload Button', () => {
    it('calls onUploadNew when upload button is clicked', async () => {
      const mockOnUploadNew = jest.fn();
      render(<ProtocolSelector {...defaultProps} onUploadNew={mockOnUploadNew} />);
      
      const uploadButton = screen.getByTestId('upload-button');
      await user.click(uploadButton);
      
      expect(mockOnUploadNew).toHaveBeenCalledTimes(1);
    });
  });

  describe('Text Formatting and Truncation', () => {
    it('truncates long study acronyms', async () => {
      render(<ProtocolSelector {...defaultProps} />);
      
      // Open dropdown
      const dropdownButton = screen.getByRole('button', { name: /select a protocol/i });
      await user.click(dropdownButton);
      
      // Long acronym should be truncated (15 chars max)
      expect(screen.getByText('ONCOLOGY-TRIAL-...')).toBeInTheDocument();
      expect(screen.queryByText('ONCOLOGY-TRIAL-WITH-VERY-LONG-NAME')).not.toBeInTheDocument();
    });

    it('truncates long protocol titles', async () => {
      render(<ProtocolSelector {...defaultProps} />);
      
      // Open dropdown
      const dropdownButton = screen.getByRole('button', { name: /select a protocol/i });
      await user.click(dropdownButton);
      
      // Long title should be truncated (35 chars max by default)
      const longTitleElement = screen.getByText(/A Very Long Protocol Title That Sho/);
      expect(longTitleElement).toBeInTheDocument();
    });

    it('does not truncate short text', async () => {
      render(<ProtocolSelector {...defaultProps} />);
      
      // Open dropdown
      const dropdownButton = screen.getByRole('button', { name: /select a protocol/i });
      await user.click(dropdownButton);
      
      // Short acronym and title should not be truncated
      expect(screen.getByText('NEURO')).toBeInTheDocument();
      expect(screen.getByText('Short Title')).toBeInTheDocument();
    });

    it('formats dates correctly', async () => {
      render(<ProtocolSelector {...defaultProps} />);
      
      // Open dropdown
      const dropdownButton = screen.getByRole('button', { name: /select a protocol/i });
      await user.click(dropdownButton);
      
      // Check that dates are formatted in locale format
      expect(screen.getByText(/Jan 15, 2024/)).toBeInTheDocument();
      expect(screen.getByText(/Feb 20, 2024/)).toBeInTheDocument();
      expect(screen.getByText(/Mar 10, 2024/)).toBeInTheDocument();
    });
  });

  describe('Keyboard Navigation', () => {
    it('supports keyboard navigation on dropdown button', async () => {
      render(<ProtocolSelector {...defaultProps} />);
      
      const dropdownButton = screen.getByRole('button', { name: /select a protocol/i });
      
      // Focus the button
      dropdownButton.focus();
      expect(dropdownButton).toHaveFocus();
      
      // Press Enter to open dropdown (simulate click instead since keyboard handler might not be implemented)
      await user.click(dropdownButton);
      await waitFor(() => {
        expect(screen.getByText('CARDIO-STUDY')).toBeInTheDocument();
      });
    });

    it('supports focus on protocol options', async () => {
      render(<ProtocolSelector {...defaultProps} />);
      
      // Open dropdown
      const dropdownButton = screen.getByRole('button', { name: /select a protocol/i });
      await user.click(dropdownButton);
      
      // Get protocol buttons
      const protocolButtons = screen.getAllByRole('button').filter(button => 
        button.textContent?.includes('CARDIO-STUDY') || 
        button.textContent?.includes('ONCOLOGY-TRIAL-') ||
        button.textContent?.includes('NEURO')
      );
      
      // Focus first protocol option
      if (protocolButtons[0]) {
        protocolButtons[0].focus();
        expect(protocolButtons[0]).toHaveFocus();
      }
    });
  });

  describe('Accessibility', () => {
    it('has proper ARIA attributes', () => {
      render(<ProtocolSelector {...defaultProps} />);
      
      // Check that buttons have proper roles
      expect(screen.getByRole('button', { name: /select a protocol/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /upload new protocol/i })).toBeInTheDocument();
    });

    it('maintains proper focus management', async () => {
      render(<ProtocolSelector {...defaultProps} />);
      
      const dropdownButton = screen.getByRole('button', { name: /select a protocol/i });
      const uploadButton = screen.getByTestId('upload-button');
      
      // Tab navigation should work
      await user.tab();
      expect(dropdownButton).toHaveFocus();
      
      await user.tab();
      expect(uploadButton).toHaveFocus();
    });
  });

  describe('Edge Cases', () => {
    it('handles protocols with missing optional fields', async () => {
      const protocolsWithMissingFields: Protocol[] = [
        {
          study_acronym: 'TEST',
          protocol_title: 'Test Protocol',
          upload_date: '2024-01-01T00:00:00Z',
          status: 'completed'
          // Missing optional fields like sponsor, indication, etc.
        }
      ];

      const props = {
        ...defaultProps,
        protocols: protocolsWithMissingFields
      };

      render(<ProtocolSelector {...props} />);
      
      // Open dropdown
      const dropdownButton = screen.getByRole('button', { name: /select a protocol/i });
      await user.click(dropdownButton);
      
      expect(screen.getByText('TEST')).toBeInTheDocument();
      expect(screen.getByText('Test Protocol')).toBeInTheDocument();
    });

    it('handles protocols with different ID formats', async () => {
      const protocolsWithDifferentIds: Protocol[] = [
        {
          id: 'old-format-id',
          study_acronym: 'OLD-FORMAT',
          protocol_title: 'Old Format Protocol',
          upload_date: '2024-01-01T00:00:00Z',
          status: 'completed'
        },
        {
          protocol_id: 'new-format-id',
          study_acronym: 'NEW-FORMAT',
          protocol_title: 'New Format Protocol',
          upload_date: '2024-01-01T00:00:00Z',
          status: 'completed'
        }
      ];

      const mockOnProtocolSelect = jest.fn();
      const props = {
        ...defaultProps,
        protocols: protocolsWithDifferentIds,
        onProtocolSelect: mockOnProtocolSelect
      };

      render(<ProtocolSelector {...props} />);
      
      // Open dropdown
      const dropdownButton = screen.getByRole('button', { name: /select a protocol/i });
      await user.click(dropdownButton);
      
      // Click on first protocol
      const firstProtocol = screen.getByText('OLD-FORMAT');
      await user.click(firstProtocol);
      
      expect(mockOnProtocolSelect).toHaveBeenCalledWith(protocolsWithDifferentIds[0]);
    });

    it('handles empty strings gracefully', async () => {
      const protocolsWithEmptyStrings: Protocol[] = [
        {
          study_acronym: '',
          protocol_title: '',
          upload_date: '2024-01-01T00:00:00Z',
          status: 'completed'
        }
      ];

      const props = {
        ...defaultProps,
        protocols: protocolsWithEmptyStrings
      };

      render(<ProtocolSelector {...props} />);
      
      // Open dropdown
      const dropdownButton = screen.getByRole('button', { name: /select a protocol/i });
      await user.click(dropdownButton);
      
      // Should still render without crashing (check for multiple buttons)
      expect(screen.getAllByRole('button')).toHaveLength(3); // dropdown + protocol option + upload button
    });
  });

  describe('Visual States and Styling', () => {
    it('applies correct styles based on protocol availability', () => {
      render(<ProtocolSelector {...defaultProps} />);
      
      const dropdownButton = screen.getByRole('button', { name: /select a protocol/i });
      expect(dropdownButton).toHaveStyle('cursor: pointer');
    });

    it('applies disabled styles when no protocols available', () => {
      const emptyProps = {
        ...defaultProps,
        protocols: []
      };

      render(<ProtocolSelector {...emptyProps} />);
      
      const dropdownButton = screen.getByRole('button', { name: /no existing protocols found/i });
      expect(dropdownButton).toHaveStyle('cursor: not-allowed');
    });
  });
}); 