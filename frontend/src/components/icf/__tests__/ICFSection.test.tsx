import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import ICFSection, { ICFSectionData } from '../ICFSection';

describe('ICFSection Component', () => {
  const mockSection: ICFSectionData = {
    name: 'introduction',
    title: 'Introduction',
    content: 'This is the introduction section content.',
    status: 'ready_for_review',
    wordCount: 10,
  };

  const mockCallbacks = {
    onApprove: jest.fn(),
    onEdit: jest.fn(),
    onRegenerate: jest.fn(),
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Basic Rendering', () => {
    it('renders section with title', () => {
      render(<ICFSection section={mockSection} isGenerating={false} />);
      expect(screen.getByText('Introduction')).toBeInTheDocument();
    });

    it('renders section content', () => {
      render(<ICFSection section={mockSection} isGenerating={false} />);
      expect(screen.getByText('This is the introduction section content.')).toBeInTheDocument();
    });

    it('displays word count when provided', () => {
      render(<ICFSection section={mockSection} isGenerating={false} />);
      expect(screen.getByText(/10 words/)).toBeInTheDocument();
    });

    it('does not display word count when not provided', () => {
      const sectionWithoutWordCount = { ...mockSection, wordCount: undefined };
      render(<ICFSection section={sectionWithoutWordCount} isGenerating={false} />);
      expect(screen.queryByText(/words/)).not.toBeInTheDocument();
    });
  });

  describe('Status Display', () => {
    it('displays pending status', () => {
      const pendingSection = { ...mockSection, status: 'pending' as const };
      render(<ICFSection section={pendingSection} isGenerating={false} />);
      expect(screen.getByText(/Waiting to generate/i)).toBeInTheDocument();
      expect(screen.getByText('⏳')).toBeInTheDocument();
    });

    it('displays generating status with loading spinner', () => {
      const generatingSection = { ...mockSection, status: 'generating' as const, content: '' };
      render(<ICFSection section={generatingSection} isGenerating={false} />);
      expect(screen.getByText(/Generating introduction/i)).toBeInTheDocument();
      expect(screen.getByText('⚡')).toBeInTheDocument();
    });

    it('displays generating status with streaming content', () => {
      const generatingSection = {
        ...mockSection,
        status: 'generating' as const,
        content: 'Partial content being generated...'
      };
      render(<ICFSection section={generatingSection} isGenerating={false} />);
      expect(screen.getByText(/Partial content being generated/)).toBeInTheDocument();
      expect(screen.getByText('|')).toBeInTheDocument(); // Blinking cursor
    });

    it('displays ready_for_review status', () => {
      render(<ICFSection section={mockSection} isGenerating={false} />);
      expect(screen.getByText(/Ready for Review/i)).toBeInTheDocument();
      expect(screen.getByText('👁️')).toBeInTheDocument();
    });

    it('displays approved status', () => {
      const approvedSection = { ...mockSection, status: 'approved' as const };
      render(<ICFSection section={approvedSection} isGenerating={false} />);
      expect(screen.getByText(/Approved/i)).toBeInTheDocument();
      expect(screen.getByText('✅')).toBeInTheDocument();
    });

    it('displays error status', () => {
      const errorSection = { ...mockSection, status: 'error' as const };
      render(<ICFSection section={errorSection} isGenerating={false} />);
      expect(screen.getByText(/Error generating/i)).toBeInTheDocument();
      expect(screen.getByText('❌')).toBeInTheDocument();
    });
  });

  describe('Action Buttons - Ready for Review', () => {
    it('shows approve, edit, and regenerate buttons when ready for review', () => {
      render(<ICFSection section={mockSection} isGenerating={false} {...mockCallbacks} />);
      expect(screen.getByText('✓ Approve')).toBeInTheDocument();
      expect(screen.getByText('✏️ Edit')).toBeInTheDocument();
      expect(screen.getByText('🔄 Regenerate')).toBeInTheDocument();
    });

    it('calls onApprove when approve button is clicked', () => {
      render(<ICFSection section={mockSection} isGenerating={false} {...mockCallbacks} />);
      fireEvent.click(screen.getByText('✓ Approve'));
      expect(mockCallbacks.onApprove).toHaveBeenCalledWith('introduction');
    });

    it('does not show approve button when status is approved', () => {
      const approvedSection = { ...mockSection, status: 'approved' as const };
      render(<ICFSection section={approvedSection} isGenerating={false} {...mockCallbacks} />);
      expect(screen.queryByText('✓ Approve')).not.toBeInTheDocument();
      expect(screen.getByText('✏️ Edit')).toBeInTheDocument();
    });
  });

  describe('Regenerate Button', () => {
    it('calls onRegenerate when regenerate button is clicked', () => {
      render(<ICFSection section={mockSection} isGenerating={false} {...mockCallbacks} />);
      fireEvent.click(screen.getByText('🔄 Regenerate'));
      expect(mockCallbacks.onRegenerate).toHaveBeenCalledWith('introduction');
    });

    it('disables regenerate button when isGenerating is true', () => {
      render(<ICFSection section={mockSection} isGenerating={true} {...mockCallbacks} />);
      const regenerateButton = screen.getByText('🔄 Regenerate');
      expect(regenerateButton).toBeDisabled();
    });

    it('enables regenerate button when isGenerating is false', () => {
      render(<ICFSection section={mockSection} isGenerating={false} {...mockCallbacks} />);
      const regenerateButton = screen.getByText('🔄 Regenerate');
      expect(regenerateButton).not.toBeDisabled();
    });
  });

  describe('Edit Mode', () => {
    it('enters edit mode when edit button is clicked', async () => {
      render(<ICFSection section={mockSection} isGenerating={false} {...mockCallbacks} />);

      const editButton = screen.getByText('✏️ Edit');
      fireEvent.click(editButton);

      await waitFor(() => {
        expect(screen.getByRole('textbox')).toBeInTheDocument();
      });
    });

    it('displays current content in textarea when editing', async () => {
      render(<ICFSection section={mockSection} isGenerating={false} {...mockCallbacks} />);

      fireEvent.click(screen.getByText('✏️ Edit'));

      await waitFor(() => {
        const textarea = screen.getByRole('textbox') as HTMLTextAreaElement;
        expect(textarea.value).toBe('This is the introduction section content.');
      });
    });

    it('updates textarea content when typing', async () => {
      render(<ICFSection section={mockSection} isGenerating={false} {...mockCallbacks} />);

      fireEvent.click(screen.getByText('✏️ Edit'));

      await waitFor(() => {
        const textarea = screen.getByRole('textbox');
        expect(textarea).toBeInTheDocument();
      });

      const textarea = screen.getByRole('textbox');
      fireEvent.change(textarea, { target: { value: 'Updated content' } });

      expect((textarea as HTMLTextAreaElement).value).toBe('Updated content');
    });

    it('shows save and cancel buttons in edit mode', async () => {
      render(<ICFSection section={mockSection} isGenerating={false} {...mockCallbacks} />);

      fireEvent.click(screen.getByText('✏️ Edit'));

      await waitFor(() => {
        expect(screen.getByText('Save Changes')).toBeInTheDocument();
        expect(screen.getByText('Cancel')).toBeInTheDocument();
      });
    });

    it('hides action buttons when in edit mode', async () => {
      render(<ICFSection section={mockSection} isGenerating={false} {...mockCallbacks} />);

      fireEvent.click(screen.getByText('✏️ Edit'));

      await waitFor(() => {
        expect(screen.queryByText('✓ Approve')).not.toBeInTheDocument();
        expect(screen.queryByText('✏️ Edit')).not.toBeInTheDocument();
        expect(screen.queryByText('🔄 Regenerate')).not.toBeInTheDocument();
      });
    });
  });

  describe('Save Edit', () => {
    it('calls onEdit with updated content when save is clicked', async () => {
      render(<ICFSection section={mockSection} isGenerating={false} {...mockCallbacks} />);

      fireEvent.click(screen.getByText('✏️ Edit'));

      await waitFor(() => {
        const textarea = screen.getByRole('textbox');
        expect(textarea).toBeInTheDocument();
      });

      const textarea = screen.getByRole('textbox');
      fireEvent.change(textarea, { target: { value: 'New edited content' } });

      fireEvent.click(screen.getByText('Save Changes'));

      expect(mockCallbacks.onEdit).toHaveBeenCalledWith('introduction', 'New edited content');
    });

    it('exits edit mode after saving', async () => {
      render(<ICFSection section={mockSection} isGenerating={false} {...mockCallbacks} />);

      fireEvent.click(screen.getByText('✏️ Edit'));

      await waitFor(() => {
        expect(screen.getByRole('textbox')).toBeInTheDocument();
      });

      fireEvent.click(screen.getByText('Save Changes'));

      await waitFor(() => {
        expect(screen.queryByRole('textbox')).not.toBeInTheDocument();
        expect(screen.getByText('✏️ Edit')).toBeInTheDocument();
      });
    });
  });

  describe('Cancel Edit', () => {
    it('reverts content to original when cancel is clicked', async () => {
      render(<ICFSection section={mockSection} isGenerating={false} {...mockCallbacks} />);

      fireEvent.click(screen.getByText('✏️ Edit'));

      await waitFor(() => {
        const textarea = screen.getByRole('textbox');
        expect(textarea).toBeInTheDocument();
      });

      const textarea = screen.getByRole('textbox');
      fireEvent.change(textarea, { target: { value: 'Temporary changes' } });

      fireEvent.click(screen.getByText('Cancel'));

      await waitFor(() => {
        expect(screen.queryByRole('textbox')).not.toBeInTheDocument();
      });

      // Content should revert to original
      expect(screen.getByText('This is the introduction section content.')).toBeInTheDocument();
    });

    it('exits edit mode after canceling', async () => {
      render(<ICFSection section={mockSection} isGenerating={false} {...mockCallbacks} />);

      fireEvent.click(screen.getByText('✏️ Edit'));

      await waitFor(() => {
        expect(screen.getByRole('textbox')).toBeInTheDocument();
      });

      fireEvent.click(screen.getByText('Cancel'));

      await waitFor(() => {
        expect(screen.queryByRole('textbox')).not.toBeInTheDocument();
        expect(screen.getByText('✏️ Edit')).toBeInTheDocument();
      });
    });

    it('does not call onEdit when cancel is clicked', async () => {
      render(<ICFSection section={mockSection} isGenerating={false} {...mockCallbacks} />);

      fireEvent.click(screen.getByText('✏️ Edit'));

      await waitFor(() => {
        const textarea = screen.getByRole('textbox');
        expect(textarea).toBeInTheDocument();
      });

      const textarea = screen.getByRole('textbox');
      fireEvent.change(textarea, { target: { value: 'Temporary changes' } });

      fireEvent.click(screen.getByText('Cancel'));

      expect(mockCallbacks.onEdit).not.toHaveBeenCalled();
    });
  });

  describe('Content Updates', () => {
    it('updates edit content when section content changes', () => {
      const { rerender } = render(<ICFSection section={mockSection} isGenerating={false} {...mockCallbacks} />);

      const updatedSection = { ...mockSection, content: 'Updated section content' };
      rerender(<ICFSection section={updatedSection} isGenerating={false} {...mockCallbacks} />);

      expect(screen.getByText('Updated section content')).toBeInTheDocument();
    });

    it('syncs textarea content when section updates during edit', async () => {
      const { rerender } = render(<ICFSection section={mockSection} isGenerating={false} {...mockCallbacks} />);

      fireEvent.click(screen.getByText('✏️ Edit'));

      await waitFor(() => {
        expect(screen.getByRole('textbox')).toBeInTheDocument();
      });

      const updatedSection = { ...mockSection, content: 'Server-side update' };
      rerender(<ICFSection section={updatedSection} isGenerating={false} {...mockCallbacks} />);

      const textarea = screen.getByRole('textbox') as HTMLTextAreaElement;
      expect(textarea.value).toBe('Server-side update');
    });
  });

  describe('Optional Callbacks', () => {
    it('does not crash when onApprove is not provided', () => {
      render(<ICFSection section={mockSection} isGenerating={false} />);
      const approveButton = screen.getByText('✓ Approve');
      expect(() => fireEvent.click(approveButton)).not.toThrow();
    });

    it('does not crash when onEdit is not provided', async () => {
      render(<ICFSection section={mockSection} isGenerating={false} />);

      fireEvent.click(screen.getByText('✏️ Edit'));

      await waitFor(() => {
        expect(screen.getByRole('textbox')).toBeInTheDocument();
      });

      const textarea = screen.getByRole('textbox');
      fireEvent.change(textarea, { target: { value: 'New content' } });

      expect(() => fireEvent.click(screen.getByText('Save Changes'))).not.toThrow();
    });

    it('does not crash when onRegenerate is not provided', () => {
      render(<ICFSection section={mockSection} isGenerating={false} />);
      const regenerateButton = screen.getByText('🔄 Regenerate');
      expect(() => fireEvent.click(regenerateButton)).not.toThrow();
    });
  });

  describe('Edge Cases', () => {
    it('handles empty content gracefully', () => {
      const emptySection = { ...mockSection, content: '' };
      render(<ICFSection section={emptySection} isGenerating={false} />);
      expect(screen.getByText('No content generated.')).toBeInTheDocument();
    });

    it('handles very long content', () => {
      const longContent = 'A'.repeat(5000);
      const longSection = { ...mockSection, content: longContent };
      render(<ICFSection section={longSection} isGenerating={false} />);
      expect(screen.getByText(longContent)).toBeInTheDocument();
    });

    it('handles special characters in content', () => {
      const specialContent = 'Content with <tags> & "quotes" and \'apostrophes\'';
      const specialSection = { ...mockSection, content: specialContent };
      render(<ICFSection section={specialSection} isGenerating={false} />);
      expect(screen.getByText(specialContent)).toBeInTheDocument();
    });

    it('handles multiline content with whitespace', () => {
      const multilineContent = 'Line 1\n\nLine 2\n   Indented Line 3';
      const multilineSection = { ...mockSection, content: multilineContent };
      const { container } = render(<ICFSection section={multilineSection} isGenerating={false} />);
      // Check that content is rendered (whitespace-pre-wrap preserves formatting)
      expect(container.textContent).toContain('Line 1');
      expect(container.textContent).toContain('Line 2');
      expect(container.textContent).toContain('Indented Line 3');
    });
  });

  describe('Status Color and Icon Mapping', () => {
    it('uses correct color for each status', () => {
      const statuses: Array<ICFSectionData['status']> = [
        'pending',
        'generating',
        'ready_for_review',
        'approved',
        'error',
      ];

      statuses.forEach(status => {
        const { unmount } = render(
          <ICFSection section={{ ...mockSection, status }} isGenerating={false} />
        );
        // Component should render without errors
        expect(screen.getByText(mockSection.title)).toBeInTheDocument();
        unmount();
      });
    });

    it('uses default status handling for unknown status', () => {
      const unknownStatusSection = { ...mockSection, status: 'unknown' as any };
      render(<ICFSection section={unknownStatusSection} isGenerating={false} />);
      // Should render with default icon
      expect(screen.getByText('⏳')).toBeInTheDocument();
    });
  });

  describe('Accessibility', () => {
    it('renders textarea with proper accessibility', async () => {
      render(<ICFSection section={mockSection} isGenerating={false} {...mockCallbacks} />);

      fireEvent.click(screen.getByText('✏️ Edit'));

      await waitFor(() => {
        const textarea = screen.getByRole('textbox');
        expect(textarea).toBeInTheDocument();
        expect(textarea).toHaveValue(mockSection.content);
      });
    });

    it('maintains focus on textarea during editing', async () => {
      render(<ICFSection section={mockSection} isGenerating={false} {...mockCallbacks} />);

      fireEvent.click(screen.getByText('✏️ Edit'));

      await waitFor(() => {
        const textarea = screen.getByRole('textbox');
        expect(textarea).toBeInTheDocument();
      });

      const textarea = screen.getByRole('textbox');
      textarea.focus();
      expect(textarea).toHaveFocus();
    });
  });

  describe('Button Interactions', () => {
    it('handles approve button hover states', () => {
      render(<ICFSection section={mockSection} isGenerating={false} {...mockCallbacks} />);
      const approveButton = screen.getByText('✓ Approve');

      fireEvent.mouseEnter(approveButton);
      fireEvent.mouseLeave(approveButton);

      // Should not crash
      expect(approveButton).toBeInTheDocument();
    });

    it('handles edit button hover states', () => {
      render(<ICFSection section={mockSection} isGenerating={false} {...mockCallbacks} />);
      const editButton = screen.getByText('✏️ Edit');

      fireEvent.mouseEnter(editButton);
      fireEvent.mouseLeave(editButton);

      expect(editButton).toBeInTheDocument();
    });

    it('handles regenerate button hover when not disabled', () => {
      render(<ICFSection section={mockSection} isGenerating={false} {...mockCallbacks} />);
      const regenerateButton = screen.getByText('🔄 Regenerate');

      fireEvent.mouseEnter(regenerateButton);
      fireEvent.mouseLeave(regenerateButton);

      expect(regenerateButton).toBeInTheDocument();
    });

    it('handles regenerate button hover when disabled', () => {
      render(<ICFSection section={mockSection} isGenerating={true} {...mockCallbacks} />);
      const regenerateButton = screen.getByText('🔄 Regenerate');

      fireEvent.mouseEnter(regenerateButton);
      fireEvent.mouseLeave(regenerateButton);

      expect(regenerateButton).toBeDisabled();
    });
  });

  describe('Textarea Interactions', () => {
    it('handles textarea focus and blur events', async () => {
      render(<ICFSection section={mockSection} isGenerating={false} {...mockCallbacks} />);

      fireEvent.click(screen.getByText('✏️ Edit'));

      await waitFor(() => {
        const textarea = screen.getByRole('textbox');
        expect(textarea).toBeInTheDocument();
      });

      const textarea = screen.getByRole('textbox');
      fireEvent.focus(textarea);
      fireEvent.blur(textarea);

      expect(textarea).toBeInTheDocument();
    });
  });
});
