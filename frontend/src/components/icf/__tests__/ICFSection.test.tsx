import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import ICFSection, { ICFSectionData } from '../ICFSection';

const mockSection: ICFSectionData = {
  name: 'summary',
  title: 'Study Summary',
  content: 'This is a test summary content.',
  status: 'completed',
  wordCount: 6,
};

describe('ICFSection', () => {
  test('renders section with completed status', () => {
    render(
      <ICFSection
        section={mockSection}
        isGenerating={false}
      />
    );
    
    expect(screen.getByText('Study Summary')).toBeInTheDocument();
    expect(screen.getByText('This is a test summary content.')).toBeInTheDocument();
    expect(screen.getByText(/6 words/)).toBeInTheDocument();
  });

  test('renders generating state', () => {
    const generatingSection = {
      ...mockSection,
      status: 'generating' as const,
      content: '',
    };

    render(
      <ICFSection
        section={generatingSection}
        isGenerating={true}
      />
    );
    
    expect(screen.getByText(/Generating study summary/)).toBeInTheDocument();
  });

  test('renders pending state', () => {
    const pendingSection = {
      ...mockSection,
      status: 'pending' as const,
      content: '',
    };

    render(
      <ICFSection
        section={pendingSection}
        isGenerating={false}
      />
    );
    
    expect(screen.getByText(/Waiting to generate study summary/)).toBeInTheDocument();
  });

  test('renders error state', () => {
    const errorSection = {
      ...mockSection,
      status: 'error' as const,
      content: '',
    };

    render(
      <ICFSection
        section={errorSection}
        isGenerating={false}
      />
    );
    
    expect(screen.getByText(/Error generating study summary/)).toBeInTheDocument();
  });
});