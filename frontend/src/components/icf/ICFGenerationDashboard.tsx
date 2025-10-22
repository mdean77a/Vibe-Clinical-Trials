import React, { useState, useEffect } from 'react';
import ICFSection, { type ICFSectionData } from './ICFSection';
import { icfApi } from '../../utils/api';
import type { Protocol } from '../../types/protocol';
import { getProtocolId } from '../../types/protocol';
import { generateICFPdf, getPdfStats, validateSectionsForPdf, getFileSystemCapabilities } from '../../utils/pdfGenerator';
import { generateICFDocx, validateSectionsForDocx, getDocxFileSystemCapabilities } from '../../utils/docxGenerator';
import { generateICFMarkdown, validateSectionsForMarkdown, getMarkdownFileSystemCapabilities } from '../../utils/markdownGenerator';
import DashboardContainer from '@/components/shared/DashboardContainer';
import ProtocolInfoCard from '@/components/shared/ProtocolInfoCard';
import BackToSelectionButton from '@/components/shared/BackToSelectionButton';

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
  const [editingSections, setEditingSections] = useState<Set<string>>(new Set());

  // Initialize sections with static data
  useEffect(() => {
    // Section requirements are static and defined by the backend prompts
    const sectionRequirements = [
      { name: 'summary', title: 'Study Summary' },
      { name: 'background', title: 'Background and Purpose' },
      { name: 'participants', title: 'Number of Participants' },
      { name: 'procedures', title: 'Study Procedures' },
      { name: 'alternatives', title: 'Alternative Procedures' },
      { name: 'risks', title: 'Risks and Discomforts' },
      { name: 'benefits', title: 'Benefits' }
    ];

    const initialSections: ICFSectionData[] = sectionRequirements.map((req) => ({
      name: req.name,
      title: req.title,
      content: '',
      status: 'pending' as const,
      wordCount: 0,
    }));

    setSections(initialSections);
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
    } finally {
      // Ensure any sections still marked as generating are marked as complete
      // This handles cases where section_complete event is not received
      setSections(prev => prev.map(section => {
        if (section.status === 'generating' && section.content) {
          console.log(`Stream ended - finalizing section ${section.name} that was still marked as generating`);
          return {
            ...section,
            status: 'ready_for_review' as const,
            wordCount: section.content.split(/\s+/).length,
          };
        }
        return section;
      }));
      
      // Always ensure isGenerating is set to false when stream ends
      setProgress(prev => ({
        ...prev,
        isGenerating: false,
        currentSection: null,
      }));
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
    
    // Check if any section is currently generating
    if (anySectionGenerating) return;

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
      
      // Stream the section regeneration
      const streamIterator = icfApi.regenerateSection(collectionName, sectionName, {
        protocol_title: protocol.protocol_title,
        study_acronym: protocol.study_acronym,
        sponsor: protocol.sponsor || 'Unknown',
        indication: protocol.indication || 'General',
      });

      for await (const event of streamIterator) {
        if (event.event === 'section_start') {
          console.log(`Starting regeneration of ${event.data.section_name}`);
        } else if (event.event === 'token') {
          // Update section content in real-time as tokens stream in
          setSections(prev => prev.map(section =>
            section.name === event.data.section_name
              ? { 
                  ...section, 
                  content: event.data.accumulated_content || event.data.content,
                  status: 'generating' as const
                }
              : section
          ));
        } else if (event.event === 'section_complete') {
          // Mark section as completed
          setSections(prev => prev.map(section =>
            section.name === event.data.section_name
              ? { 
                  ...section, 
                  status: 'ready_for_review' as const, 
                  content: event.data.content,
                  wordCount: event.data.word_count 
                }
              : section
          ));
        } else if (event.event === 'section_error') {
          console.error(`Error in ${event.data.section_name}:`, event.data.error);
          setSections(prev => prev.map(section =>
            section.name === event.data.section_name
              ? { ...section, status: 'error' as const }
              : section
          ));
        } else if (event.event === 'complete') {
          console.log('Section regeneration completed');
        } else if (event.event === 'error') {
          throw new Error(event.data.error);
        }
      }
    } catch (error) {
      console.error(`Section regeneration failed for ${sectionName}:`, error);
      
      // Set specific section to error state
      setSections(prev => prev.map(section =>
        section.name === sectionName
          ? { ...section, status: 'error' as const }
          : section
      ));
    } finally {
      // Ensure the section is marked as complete if it has content but is still generating
      setSections(prev => prev.map(section => {
        if (section.name === sectionName && section.status === 'generating' && section.content) {
          console.log(`Stream ended - finalizing section ${section.name} that was still marked as generating`);
          return {
            ...section,
            status: 'ready_for_review' as const,
            wordCount: section.content.split(/\s+/).length,
          };
        }
        return section;
      }));
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

  const handleExportPdf = async () => {
    // Early return if export is not allowed
    if (!canExport) {
      return;
    }
    
    try {
      // Validate sections before generating
      const validation = validateSectionsForPdf(sections);
      
      if (!validation.isValid) {
        alert(validation.message);
        return;
      }
      
      // Show warnings if any (but don't break user gesture with confirm dialog if file picker is supported)
      const capabilities = getFileSystemCapabilities();
      
      if (validation.warnings.length > 0 && !capabilities.hasFileSystemAccess) {
        // Only show confirmation dialog for fallback download method
        const proceed = confirm(
          `PDF generation warnings:\n${validation.warnings.join('\n')}\n\nDo you want to continue with download to default folder?`
        );
        if (!proceed) return;
      }
      
      // Generate and save PDF - file picker (if supported) will be shown immediately
      await generateICFPdf(sections, protocol, {
        includeAllSections: false, // Only include ready_for_review and approved sections
        useFilePicker: true, // Enable file picker if supported
      });
      
      console.log('PDF export completed successfully');
    } catch (error) {
      if (error instanceof Error && error.message === 'File save cancelled by user') {
        console.log('PDF export cancelled by user');
        return; // Don't show error alert for user cancellation
      }
      
      console.error('PDF export failed:', error);
      alert(`Failed to export PDF: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  };

  const handleExportDocx = async () => {
    // Early return if export is not allowed
    if (!canExport) {
      return;
    }
    
    try {
      // Validate sections before generating
      const validation = validateSectionsForDocx(sections);
      
      if (!validation.isValid) {
        alert(validation.message);
        return;
      }
      
      // Show warnings if any (but don't break user gesture with confirm dialog if file picker is supported)
      const capabilities = getDocxFileSystemCapabilities();
      
      if (validation.warnings.length > 0 && !capabilities.hasFileSystemAccess) {
        // Only show confirmation dialog for fallback download method
        const proceed = confirm(
          `Word document generation warnings:\n${validation.warnings.join('\n')}\n\nDo you want to continue with download to default folder?`
        );
        if (!proceed) return;
      }
      
      // Generate and save Word document - file picker (if supported) will be shown immediately
      await generateICFDocx(sections, protocol, {
        includeAllSections: false, // Only include ready_for_review and approved sections
        useFilePicker: true, // Enable file picker if supported
      });
      
      console.log('Word document export completed successfully');
    } catch (error) {
      if (error instanceof Error && error.message === 'File save cancelled by user') {
        console.log('Word document export cancelled by user');
        return; // Don't show error alert for user cancellation
      }
      
      console.error('Word document export failed:', error);
      alert(`Failed to export Word document: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  };

  const handleExportMarkdown = async () => {
    // Early return if export is not allowed
    if (!canExport) {
      return;
    }
    
    try {
      // Validate sections before generating
      const validation = validateSectionsForMarkdown(sections);
      
      if (!validation.isValid) {
        alert(validation.message);
        return;
      }
      
      // Show warnings if any (but don't break user gesture with confirm dialog if file picker is supported)
      const capabilities = getMarkdownFileSystemCapabilities();
      
      if (validation.warnings.length > 0 && !capabilities.hasFileSystemAccess) {
        // Only show confirmation dialog for fallback download method
        const proceed = confirm(
          `Markdown generation warnings:\n${validation.warnings.join('\n')}\n\nDo you want to continue with download to default folder?`
        );
        if (!proceed) return;
      }
      
      // Generate and save Markdown - file picker (if supported) will be shown immediately
      await generateICFMarkdown(sections, protocol, {
        includeAllSections: false, // Only include ready_for_review and approved sections
        useFilePicker: true, // Enable file picker if supported
      });
      
      console.log('Markdown export completed successfully');
    } catch (error) {
      if (error instanceof Error && error.message === 'File save cancelled by user') {
        console.log('Markdown export cancelled by user');
        return; // Don't show error alert for user cancellation
      }
      
      console.error('Markdown export failed:', error);
      alert(`Failed to export Markdown: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  };


  const hasGeneratedSections = sections.some(s => s.status === 'ready_for_review' || s.status === 'approved');
  
  // Check if ALL sections are approved (required for export)
  const allSectionsApproved = sections.length > 0 && sections.every(s => s.status === 'approved');
  
  // Check if any section is currently generating
  const anySectionGenerating = sections.some(s => s.status === 'generating');
  
  // Export buttons should be enabled only when all sections are approved and nothing is generating
  const canExport = allSectionsApproved && !progress.isGenerating && !anySectionGenerating;

  return (
    <DashboardContainer maxWidth="1200px">
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
      <ProtocolInfoCard protocol={protocol} />

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
                    disabled={anySectionGenerating}
                    style={{
                      padding: '12px 24px',
                      fontSize: '0.875rem',
                      border: '1px solid #10b981',
                      borderRadius: '8px',
                      backgroundColor: '#10b981',
                      color: '#ffffff',
                      cursor: anySectionGenerating ? 'not-allowed' : 'pointer',
                      transition: 'all 0.2s',
                      opacity: anySectionGenerating ? 0.6 : 1,
                    }}
                    onMouseEnter={(e) => {
                      if (!anySectionGenerating) {
                        e.currentTarget.style.backgroundColor = '#059669';
                      }
                    }}
                    onMouseLeave={(e) => {
                      if (!anySectionGenerating) {
                        e.currentTarget.style.backgroundColor = '#10b981';
                      }
                    }}
                    title={anySectionGenerating ? 'Wait for all sections to finish generating' : 'Approve all sections that are ready for review'}
                  >
                    ✓ Approve All Sections
                  </button>
                )}
                <button
                  onClick={handleExportPdf}
                  disabled={!canExport}
                  style={{
                    padding: '10px 20px',
                    fontSize: '0.875rem',
                    border: '1px solid #ef4444',
                    borderRadius: '8px',
                    backgroundColor: '#ef4444',
                    color: '#ffffff',
                    cursor: !canExport ? 'not-allowed' : 'pointer',
                    transition: 'all 0.2s',
                    opacity: !canExport ? 0.6 : 1,
                  }}
                  onMouseEnter={(e) => {
                    if (canExport) {
                      e.currentTarget.style.backgroundColor = '#dc2626';
                    }
                  }}
                  onMouseLeave={(e) => {
                    if (canExport) {
                      e.currentTarget.style.backgroundColor = '#ef4444';
                    }
                  }}
                  title={!canExport ? 'All sections must be approved before exporting' : 
                    `Export ICF as PDF - ${getFileSystemCapabilities().description}`}
                >
                  📄 PDF
                </button>
                <button
                  onClick={handleExportDocx}
                  disabled={!canExport}
                  style={{
                    padding: '10px 20px',
                    fontSize: '0.875rem',
                    border: '1px solid #2563eb',
                    borderRadius: '8px',
                    backgroundColor: '#2563eb',
                    color: '#ffffff',
                    cursor: !canExport ? 'not-allowed' : 'pointer',
                    transition: 'all 0.2s',
                    opacity: !canExport ? 0.6 : 1,
                  }}
                  onMouseEnter={(e) => {
                    if (canExport) {
                      e.currentTarget.style.backgroundColor = '#1d4ed8';
                    }
                  }}
                  onMouseLeave={(e) => {
                    if (canExport) {
                      e.currentTarget.style.backgroundColor = '#2563eb';
                    }
                  }}
                  title={!canExport ? 'All sections must be approved before exporting' : 
                    `Export ICF as Word document - ${getDocxFileSystemCapabilities().description}`}
                >
                  📝 Word
                </button>
                <button
                  onClick={handleExportMarkdown}
                  disabled={!canExport}
                  style={{
                    padding: '10px 20px',
                    fontSize: '0.875rem',
                    border: '1px solid #059669',
                    borderRadius: '8px',
                    backgroundColor: '#059669',
                    color: '#ffffff',
                    cursor: !canExport ? 'not-allowed' : 'pointer',
                    transition: 'all 0.2s',
                    opacity: !canExport ? 0.6 : 1,
                  }}
                  onMouseEnter={(e) => {
                    if (canExport) {
                      e.currentTarget.style.backgroundColor = '#047857';
                    }
                  }}
                  onMouseLeave={(e) => {
                    if (canExport) {
                      e.currentTarget.style.backgroundColor = '#059669';
                    }
                  }}
                  title={!canExport ? 'All sections must be approved before exporting' : 
                    `Export ICF as Markdown - ${getMarkdownFileSystemCapabilities().description}`}
                >
                  📝 Markdown
                </button>
              </div>
            )}
          </div>

          {sections.map((section) => (
            <ICFSection
              key={section.name}
              section={section}
              isGenerating={progress.isGenerating || anySectionGenerating}
              onApprove={handleSectionApprove}
              onEdit={handleSectionEdit}
              onRegenerate={handleSectionRegenerate}
            />
          ))}
        </div>
      )}

      {/* Return Button */}
      <div style={{ textAlign: 'center', marginTop: '32px' }}>
        <BackToSelectionButton onClick={onReturnToSelection} />
      </div>
    </DashboardContainer>
  );
};

export default ICFGenerationDashboard;