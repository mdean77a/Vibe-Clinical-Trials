import React, { useState, useEffect } from 'react';
import ICFSection, { type ICFSectionData } from './ICFSection';
import { icfApi } from '../../utils/api';
import type { Protocol } from '../../types/protocol';
import { getProtocolId } from '../../types/protocol';

interface ICFGenerationDashboardProps {
  protocol: Protocol;
  onReturnToSelection: () => void;
}

interface GenerationProgress {
  isGenerating: boolean;
  currentSection: string | null;
  completedSections: Set<string>;
  errors: string[];
}

const ICFGenerationDashboard: React.FC<ICFGenerationDashboardProps> = ({
  protocol,
  onReturnToSelection,
}) => {
  const [sections, setSections] = useState<ICFSectionData[]>([]);
  const [progress, setProgress] = useState<GenerationProgress>({
    isGenerating: false,
    currentSection: null,
    completedSections: new Set(),
    errors: [],
  });
  const [hasStartedGeneration, setHasStartedGeneration] = useState(false);

  // Initialize sections from API requirements
  useEffect(() => {
    const loadSectionRequirements = async () => {
      try {
        const requirements = await icfApi.getSectionRequirements() as {
          required_sections: Array<{
            name: string;
            title: string;
            description: string;
            estimated_length: string;
          }>;
        };
        
        // Initialize sections based on requirements
        const initialSections: ICFSectionData[] = requirements.required_sections.map((req) => ({
          name: req.name,
          title: req.title,
          content: '',
          status: 'pending' as const,
          wordCount: 0,
        }));
        
        setSections(initialSections);
      } catch (error) {
        console.error('Failed to load section requirements:', error);
        setProgress(prev => ({
          ...prev,
          errors: [...prev.errors, 'Failed to load section requirements'],
        }));
      }
    };

    loadSectionRequirements();
  }, []);

  const generateICF = async () => {
    if (progress.isGenerating) return;

    setHasStartedGeneration(true);
    setProgress({
      isGenerating: true,
      currentSection: null,
      completedSections: new Set(),
      errors: [],
    });

    // Reset all sections to generating state
    setSections(prev => prev.map(section => ({
      ...section,
      status: 'generating' as const,
      content: '',
      wordCount: 0,
    })));

    try {
      // Use the collection name stored with the protocol (from Epic 1)
      // Fall back to using the protocol ID if collection_name is not available
      const collectionName = protocol.collection_name || 
        protocol.document_id || 
        `${getProtocolId(protocol).toUpperCase().replace(/-/g, '')}-${Math.random().toString(36).substr(2, 8)}`;
      
      // Use the streaming API for real-time token updates
      const streamingGenerator = icfApi.generateStreaming(collectionName, {
        protocol_title: protocol.protocol_title,
        study_acronym: protocol.study_acronym,
        sponsor: protocol.sponsor || 'Unknown',
        indication: protocol.indication || 'General',
      });

      for await (const event of streamingGenerator) {
        if (event.event === 'section_start') {
          // Update UI to show this section is actively generating
          setProgress(prev => ({
            ...prev,
            currentSection: event.data.section_name
          }));
        } 
        else if (event.event === 'token') {
          // Update section content in real-time as tokens arrive
          setSections(prevSections => 
            prevSections.map(section => {
              if (section.name === event.data.section_name) {
                return {
                  ...section,
                  content: event.data.accumulated_content,
                  wordCount: event.data.accumulated_content.split(/\s+/).length,
                  status: 'generating' as const
                };
              }
              return section;
            })
          );
        }
        else if (event.event === 'section_complete') {
          // Mark section as ready for review when complete
          setSections(prevSections => 
            prevSections.map(section => {
              if (section.name === event.data.section_name) {
                return {
                  ...section,
                  content: event.data.content,
                  status: 'ready_for_review' as const,
                  wordCount: event.data.word_count || event.data.content.split(/\s+/).length,
                };
              }
              return section;
            })
          );

          setProgress(prev => ({
            ...prev,
            completedSections: new Set(Array.from(prev.completedSections).concat(event.data.section_name))
          }));
        }
        else if (event.event === 'section_error') {
          // Handle section-specific errors
          setSections(prevSections => 
            prevSections.map(section => {
              if (section.name === event.data.section_name) {
                return {
                  ...section,
                  status: 'error' as const
                };
              }
              return section;
            })
          );

          setProgress(prev => ({
            ...prev,
            errors: [...prev.errors, `${event.data.section_name}: ${event.data.error}`]
          }));
        }
        else if (event.event === 'complete') {
          // All sections completed
          setProgress(prev => ({
            ...prev,
            isGenerating: false,
            currentSection: null,
            errors: [...prev.errors, ...event.data.errors]
          }));
        }
        else if (event.event === 'error') {
          // Global error
          setProgress(prev => ({
            ...prev,
            isGenerating: false,
            errors: [...prev.errors, event.data.error]
          }));
        }
      }

    } catch (error) {
      console.error('ICF generation failed:', error);
      
      // Set all sections to error state
      setSections(prev => prev.map(section => ({
        ...section,
        status: 'error' as const,
      })));

      setProgress({
        isGenerating: false,
        currentSection: null,
        completedSections: new Set(),
        errors: [error instanceof Error ? error.message : 'Unknown error occurred'],
      });
    }
  };

  const handleSectionApprove = (sectionName: string) => {
    console.log(`Approved section: ${sectionName}`);
    
    // Update section status to approved
    setSections(prev => prev.map(section =>
      section.name === sectionName
        ? { ...section, status: 'approved' as const }
        : section
    ));
  };

  const handleSectionEdit = (sectionName: string, newContent: string) => {
    setSections(prev => prev.map(section => 
      section.name === sectionName 
        ? { 
            ...section, 
            content: newContent,
            wordCount: newContent.split(/\s+/).length,
            status: 'ready_for_review' as const, // Reset to ready_for_review after editing
          }
        : section
    ));
  };

  const handleSectionRegenerate = async (sectionName: string) => {
    if (progress.isGenerating) return;

    // Set specific section to generating
    setSections(prev => prev.map(section =>
      section.name === sectionName
        ? { ...section, status: 'generating' as const, content: '', wordCount: 0 }
        : section
    ));

    try {
      // Use the collection name stored with the protocol
      const collectionName = protocol.collection_name || 
        protocol.document_id || 
        `${getProtocolId(protocol).toUpperCase().replace(/-/g, '')}-${Math.random().toString(36).substr(2, 8)}`;
      
      const response = await icfApi.regenerateSection(collectionName, sectionName, {
        protocol_title: protocol.protocol_title,
        study_acronym: protocol.study_acronym,
        sponsor: protocol.sponsor || 'Unknown',
        indication: protocol.indication || 'General',
      }) as {
        section_name: string;
        content: string;
        word_count: number;
        status: string;
      };

      if (response.status === 'completed') {
        // Update only the regenerated section - set to ready_for_review, not completed
        setSections(prev => prev.map(section =>
          section.name === sectionName
            ? {
                ...section,
                status: 'ready_for_review' as const,
                content: response.content || '',
                wordCount: response.word_count || 0,
              }
            : section
        ));
      } else {
        throw new Error(`Section regeneration failed with status: ${response.status}`);
      }
    } catch (error) {
      console.error(`Section regeneration failed for ${sectionName}:`, error);
      
      // Set specific section to error state
      setSections(prev => prev.map(section =>
        section.name === sectionName
          ? { ...section, status: 'error' as const }
          : section
      ));
    }
  };

  const handleApproveAll = () => {
    console.log('Approved all sections');
    
    // Approve all sections that are ready for review
    setSections(prev => prev.map(section =>
      section.status === 'ready_for_review'
        ? { ...section, status: 'approved' as const }
        : section
    ));
  };


  const hasGeneratedSections = sections.some(s => s.status === 'ready_for_review' || s.status === 'approved');

  return (
    <div style={{ 
      padding: '24px', 
      maxWidth: '1200px', 
      margin: '0 auto',
      minHeight: '100vh'
    }}>
      {/* Header */}
      <div style={{ textAlign: 'center', marginBottom: '32px' }}>
        <h1 style={{
          fontSize: '2.5rem',
          fontWeight: 'bold',
          background: 'linear-gradient(to right, #2563eb, #9333ea)',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent',
          backgroundClip: 'text',
          marginBottom: '8px'
        }}>
          ICF Generation Dashboard
        </h1>
        <p style={{ color: '#6b7280', fontSize: '1.125rem' }}>
          Generate and review informed consent form sections
        </p>
      </div>

      {/* Protocol Info */}
      <div style={{
        background: 'linear-gradient(to right, #faf5ff, #f3e8ff)',
        border: '1px solid #d8b4fe',
        borderRadius: '12px',
        padding: '20px',
        marginBottom: '24px',
        display: 'flex',
        alignItems: 'center',
      }}>
        <div style={{
          width: '48px',
          height: '48px',
          background: '#e9d5ff',
          borderRadius: '50%',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          marginRight: '16px'
        }}>
          <span style={{ color: '#8b5cf6', fontWeight: '600', fontSize: '1.125rem' }}>
            {protocol.study_acronym.substring(0, 2).toUpperCase()}
          </span>
        </div>
        <div style={{ flex: 1 }}>
          <h3 style={{ color: '#7c3aed', fontWeight: '600', fontSize: '1.25rem', margin: 0 }}>
            {protocol.study_acronym}
          </h3>
          <p style={{ color: '#6d28d9', fontSize: '0.875rem', margin: 0 }}>
            {protocol.protocol_title}
          </p>
        </div>
      </div>

      {/* Generation Controls */}
      {!hasStartedGeneration && (
        <div style={{
          backgroundColor: '#ffffff',
          border: '1px solid #e5e7eb',
          borderRadius: '12px',
          padding: '32px',
          marginBottom: '24px',
          textAlign: 'center',
        }}>
          <div style={{
            width: '64px',
            height: '64px',
            background: '#e9d5ff',
            borderRadius: '50%',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            margin: '0 auto 16px',
          }}>
            <span style={{ fontSize: '2rem' }}>🚀</span>
          </div>
          <h3 style={{ fontSize: '1.5rem', fontWeight: '600', color: '#1f2937', marginBottom: '8px' }}>
            Ready to Generate ICF
          </h3>
          <p style={{ color: '#6b7280', marginBottom: '24px' }}>
            Generate all 7 ICF sections using AI with protocol-specific context
          </p>
          <button
            onClick={generateICF}
            disabled={progress.isGenerating}
            style={{
              background: 'linear-gradient(to right, #8b5cf6, #7c3aed)',
              color: 'white',
              fontWeight: '600',
              padding: '16px 32px',
              borderRadius: '8px',
              border: 'none',
              cursor: progress.isGenerating ? 'not-allowed' : 'pointer',
              fontSize: '1rem',
              opacity: progress.isGenerating ? 0.6 : 1,
              transition: 'all 0.2s',
            }}
            onMouseEnter={(e) => {
              if (!progress.isGenerating) {
                e.currentTarget.style.background = 'linear-gradient(to right, #7c3aed, #6d28d9)';
              }
            }}
            onMouseLeave={(e) => {
              if (!progress.isGenerating) {
                e.currentTarget.style.background = 'linear-gradient(to right, #8b5cf6, #7c3aed)';
              }
            }}
          >
            {progress.isGenerating ? '🔄 Generating ICF...' : '🚀 Generate ICF'}
          </button>
        </div>
      )}


      {/* Error Messages */}
      {progress.errors.length > 0 && (
        <div style={{
          backgroundColor: '#fef2f2',
          border: '1px solid #fecaca',
          borderRadius: '8px',
          padding: '16px',
          marginBottom: '24px',
        }}>
          <h4 style={{ color: '#dc2626', fontSize: '1rem', fontWeight: '600', margin: '0 0 8px 0' }}>
            ⚠️ Errors Occurred
          </h4>
          {progress.errors.map((error, index) => (
            <p key={index} style={{ color: '#991b1b', fontSize: '0.875rem', margin: '4px 0' }}>
              • {error}
            </p>
          ))}
        </div>
      )}

      {/* ICF Sections */}
      {hasStartedGeneration && (
        <div>
          <div style={{ 
            display: 'flex', 
            justifyContent: 'space-between', 
            alignItems: 'center', 
            marginBottom: '24px' 
          }}>
            <h2 style={{ fontSize: '1.5rem', fontWeight: '600', color: '#1f2937', margin: 0 }}>
              ICF Sections
            </h2>
            {hasGeneratedSections && (
              <div style={{ display: 'flex', gap: '12px' }}>
                <button
                  onClick={generateICF}
                  disabled={progress.isGenerating}
                  style={{
                    padding: '12px 24px',
                    fontSize: '0.875rem',
                    border: '1px solid #d1d5db',
                    borderRadius: '8px',
                    backgroundColor: '#ffffff',
                    color: '#374151',
                    cursor: progress.isGenerating ? 'not-allowed' : 'pointer',
                    transition: 'all 0.2s',
                    opacity: progress.isGenerating ? 0.6 : 1,
                  }}
                  onMouseEnter={(e) => {
                    if (!progress.isGenerating) {
                      e.currentTarget.style.backgroundColor = '#f9fafb';
                    }
                  }}
                  onMouseLeave={(e) => {
                    if (!progress.isGenerating) {
                      e.currentTarget.style.backgroundColor = '#ffffff';
                    }
                  }}
                >
                  🔄 Regenerate All
                </button>
                {sections.some(s => s.status === 'ready_for_review') && (
                  <button
                    onClick={handleApproveAll}
                    style={{
                      padding: '12px 24px',
                      fontSize: '0.875rem',
                      border: '1px solid #10b981',
                      borderRadius: '8px',
                      backgroundColor: '#10b981',
                      color: '#ffffff',
                      cursor: 'pointer',
                      transition: 'all 0.2s',
                    }}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.backgroundColor = '#059669';
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.backgroundColor = '#10b981';
                    }}
                  >
                    ✓ Approve All Sections
                  </button>
                )}
              </div>
            )}
          </div>

          {sections.map((section) => (
            <ICFSection
              key={section.name}
              section={section}
              isGenerating={progress.isGenerating}
              onApprove={handleSectionApprove}
              onEdit={handleSectionEdit}
              onRegenerate={handleSectionRegenerate}
            />
          ))}
        </div>
      )}

      {/* Return Button */}
      <div style={{ textAlign: 'center', marginTop: '32px' }}>
        <button
          onClick={onReturnToSelection}
          style={{
            background: 'linear-gradient(to right, #6b7280, #4b5563)',
            color: 'white',
            fontWeight: '600',
            padding: '12px 24px',
            borderRadius: '8px',
            border: 'none',
            cursor: 'pointer',
            fontSize: '0.875rem',
            transition: 'all 0.2s',
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.background = 'linear-gradient(to right, #4b5563, #374151)';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.background = 'linear-gradient(to right, #6b7280, #4b5563)';
          }}
        >
          ← Return to Document Selection
        </button>
      </div>
    </div>
  );
};

export default ICFGenerationDashboard;