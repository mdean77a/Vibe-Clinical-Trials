/**
 * PDF Generation utility for ICF documents using @react-pdf/renderer
 * 
 * This module provides functionality to generate PDF documents from ICF sections
 * with markdown content, professional styling, and metadata.
 */

import React from 'react';
import ReactMarkdown from 'react-markdown';
import type { ICFSectionData } from '../components/icf/ICFSection';
import type { Protocol } from '../types/protocol';

// Dynamic import for @react-pdf/renderer to avoid SSR issues
let PDFModule: any = null;

const loadPDFModule = async () => {
  if (PDFModule) return PDFModule;
  
  // Dynamic import with proper typing
  const pdfModule = await import('@react-pdf/renderer');
  PDFModule = pdfModule;
  return pdfModule;
};

/**
 * Parse markdown content into structured elements for PDF rendering
 */
interface ParsedContent {
  type: 'paragraph' | 'heading' | 'list' | 'listItem';
  content: string;
  level?: number; // for headings
  children?: ParsedContent[];
}

const parseMarkdownToStructure = (content: string): ParsedContent[] => {
  const lines = content.split('\n');
  const parsed: ParsedContent[] = [];
  
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i].trim();
    
    if (!line) continue;
    
    // Handle headings
    if (line.startsWith('#')) {
      const level = (line.match(/^#+/) || [''])[0].length;
      const headingText = line.replace(/^#+\s*/, '');
      parsed.push({
        type: 'heading',
        content: headingText,
        level: level
      });
    }
    // Handle list items
    else if (line.startsWith('- ') || line.startsWith('* ') || /^\d+\.\s/.test(line)) {
      const listContent = line.replace(/^[-*]\s|^\d+\.\s/, '');
      parsed.push({
        type: 'listItem',
        content: listContent
      });
    }
    // Handle paragraphs
    else {
      parsed.push({
        type: 'paragraph',
        content: line
      });
    }
  }
  
  return parsed;
};

/**
 * Create PDF document component
 */
const createPDFDocument = async (sections: ICFSectionData[], protocol: Protocol) => {
  const { Document, Page, Text, View, StyleSheet, pdf } = await loadPDFModule();
  
  // Define styles for the PDF
  const styles = StyleSheet.create({
    page: {
      flexDirection: 'column',
      backgroundColor: '#FFFFFF',
      padding: 40,
      fontSize: 11,
      lineHeight: 1.5,
      fontFamily: 'Helvetica',
    },
    coverPage: {
      display: 'flex',
      flexDirection: 'column',
      justifyContent: 'center',
      alignItems: 'center',
      textAlign: 'center',
      minHeight: '100%',
    },
    coverTitle: {
      fontSize: 24,
      fontWeight: 'bold',
      marginBottom: 20,
      color: '#1f2937',
    },
    coverSubtitle: {
      fontSize: 16,
      marginBottom: 10,
      color: '#4b5563',
    },
    coverProtocol: {
      fontSize: 14,
      marginBottom: 40,
      color: '#6b7280',
    },
    coverDate: {
      fontSize: 12,
      color: '#9ca3af',
    },
    header: {
      fontSize: 18,
      fontWeight: 'bold',
      marginBottom: 20,
      color: '#1f2937',
      borderBottom: '2pt solid #e5e7eb',
      paddingBottom: 10,
    },
    sectionTitle: {
      fontSize: 14,
      fontWeight: 'bold',
      marginBottom: 12,
      marginTop: 20,
      color: '#374151',
    },
    paragraph: {
      marginBottom: 8,
      textAlign: 'justify',
      color: '#1f2937',
    },
    heading1: {
      fontSize: 14,
      fontWeight: 'bold',
      marginBottom: 8,
      marginTop: 16,
      color: '#1f2937',
    },
    heading2: {
      fontSize: 13,
      fontWeight: 'bold',
      marginBottom: 6,
      marginTop: 12,
      color: '#374151',
    },
    heading3: {
      fontSize: 12,
      fontWeight: 'bold',
      marginBottom: 4,
      marginTop: 8,
      color: '#4b5563',
    },
    listItem: {
      marginLeft: 15,
      marginBottom: 4,
      color: '#1f2937',
    },
    footer: {
      position: 'absolute',
      bottom: 30,
      left: 40,
      right: 40,
      textAlign: 'center',
      fontSize: 9,
      color: '#9ca3af',
      borderTop: '1pt solid #e5e7eb',
      paddingTop: 10,
    },
    pageNumber: {
      position: 'absolute',
      bottom: 30,
      right: 40,
      fontSize: 9,
      color: '#9ca3af',
    },
  });

  // Function to render parsed markdown content
  const renderParsedContent = (parsedContent: ParsedContent[], Text: any) => {
    return parsedContent.map((item, index) => {
      switch (item.type) {
        case 'heading':
          const headingStyle = item.level === 1 ? styles.heading1 : 
                              item.level === 2 ? styles.heading2 : styles.heading3;
          return React.createElement(Text, { key: index, style: headingStyle }, item.content);
        case 'listItem':
          return React.createElement(Text, { key: index, style: styles.listItem }, `• ${item.content}`);
        case 'paragraph':
        default:
          return React.createElement(Text, { key: index, style: styles.paragraph }, item.content);
      }
    });
  };

  // Filter sections to include only those that are ready for review or approved
  const completedSections = sections.filter(
    section => section.status === 'ready_for_review' || section.status === 'approved'
  );

  const PDFDocument = () => {
    return React.createElement(Document, null, [
      // Cover Page
      React.createElement(Page, { key: 'cover', size: 'A4', style: styles.page }, [
        React.createElement(View, { key: 'cover-content', style: styles.coverPage }, [
          React.createElement(Text, { key: 'title', style: styles.coverTitle }, 'Informed Consent Form'),
          React.createElement(Text, { key: 'subtitle', style: styles.coverSubtitle }, protocol.protocol_title),
          React.createElement(Text, { key: 'protocol', style: styles.coverProtocol }, `Study: ${protocol.study_acronym}`),
          React.createElement(Text, { key: 'date', style: styles.coverDate }, 
            `Generated on ${new Date().toLocaleDateString('en-US', {
              year: 'numeric',
              month: 'long', 
              day: 'numeric'
            })}`
          )
        ]),
        React.createElement(Text, { key: 'footer', style: styles.footer }, 'Clinical Trial Accelerator - AI-Generated Document')
      ]),
      
      // Table of Contents
      React.createElement(Page, { key: 'toc', size: 'A4', style: styles.page }, [
        React.createElement(Text, { key: 'toc-header', style: styles.header }, 'Table of Contents'),
        ...completedSections.map((section, index) =>
          React.createElement(View, { 
            key: section.name, 
            style: { marginBottom: 8, flexDirection: 'row' } 
          }, [
            React.createElement(Text, { 
              key: 'title', 
              style: { flex: 1, color: '#374151' } 
            }, `${index + 1}. ${section.title}`),
            React.createElement(Text, { 
              key: 'page', 
              style: { color: '#6b7280' } 
            }, `${index + 3}`)
          ])
        ),
        React.createElement(Text, { key: 'toc-footer', style: styles.footer }, 'Clinical Trial Accelerator - AI-Generated Document'),
        React.createElement(Text, { key: 'page-number', style: styles.pageNumber }, 'Page 2')
      ]),
      
      // ICF Sections
      ...completedSections.map((section, index) => {
        const parsedContent = parseMarkdownToStructure(section.content);
        
        return React.createElement(Page, { key: section.name, size: 'A4', style: styles.page }, [
          React.createElement(Text, { key: 'section-header', style: styles.header }, 
            `${index + 1}. ${section.title}`
          ),
          React.createElement(View, { key: 'content' }, 
            renderParsedContent(parsedContent, Text)
          ),
          React.createElement(View, { 
            key: 'status', 
            style: { marginTop: 20, padding: 10, backgroundColor: '#f9fafb', borderRadius: 4 } 
          }, [
            React.createElement(Text, { 
              key: 'status-text', 
              style: { fontSize: 9, color: '#6b7280' } 
            }, 
              `Status: ${section.status === 'approved' ? 'Approved' : 'Ready for Review'} | ` +
              `Word Count: ${section.wordCount || 0} | ` +
              `Section: ${section.name}`
            )
          ]),
          React.createElement(Text, { key: 'section-footer', style: styles.footer }, 'Clinical Trial Accelerator - AI-Generated Document'),
          React.createElement(Text, { key: 'section-page', style: styles.pageNumber }, `Page ${index + 3}`)
        ]);
      })
    ]);
  };

  return PDFDocument;
};

/**
 * Check if File System Access API is supported
 */
const isFileSystemAccessSupported = (): boolean => {
  return typeof window !== 'undefined' && 'showSaveFilePicker' in window;
};

/**
 * Get file handle using File System Access API (must be called during user gesture)
 */
const getFileHandleForSaving = async (defaultFilename: string) => {
  try {
    // @ts-ignore - File System Access API types may not be available
    const fileHandle = await window.showSaveFilePicker({
      suggestedName: defaultFilename,
      types: [
        {
          description: 'PDF files',
          accept: {
            'application/pdf': ['.pdf'],
          },
        },
      ],
    });
    return fileHandle;
  } catch (error) {
    if ((error as Error).name === 'AbortError') {
      throw new Error('File save cancelled by user');
    }
    throw error;
  }
};

/**
 * Save PDF to file handle
 */
const savePdfToFileHandle = async (pdfBlob: Blob, fileHandle: any): Promise<void> => {
  try {
    const writable = await fileHandle.createWritable();
    await writable.write(pdfBlob);
    await writable.close();
    
    console.log(`PDF saved successfully to user-selected location`);
  } catch (error) {
    console.error('Error writing to file:', error);
    throw new Error('Failed to write PDF to selected location');
  }
};

/**
 * Save PDF using traditional download (fallback method)
 */
const savePdfWithDownload = (pdfBlob: Blob, filename: string): void => {
  const url = URL.createObjectURL(pdfBlob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  
  // Trigger download
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  
  // Clean up
  URL.revokeObjectURL(url);
  
  console.log(`PDF downloaded to default location: ${filename}`);
};

/**
 * Generate and save ICF PDF with user-selectable location
 */
export const generateICFPdf = async (
  sections: ICFSectionData[], 
  protocol: Protocol,
  options: {
    includeAllSections?: boolean;
    filename?: string;
    useFilePicker?: boolean; // New option to control save method
  } = {}
): Promise<void> => {
  try {
    // Filter sections based on options
    const sectionsToInclude = options.includeAllSections 
      ? sections 
      : sections.filter(s => s.status === 'ready_for_review' || s.status === 'approved');

    if (sectionsToInclude.length === 0) {
      throw new Error('No sections available for PDF generation. Please generate or approve sections first.');
    }

    // Generate filename
    const timestamp = new Date().toISOString().split('T')[0];
    const defaultFilename = options.filename || `${protocol.study_acronym}_ICF_${timestamp}.pdf`;
    
    // Determine save method and get file handle first if using file picker
    const useFilePicker = options.useFilePicker !== false && isFileSystemAccessSupported();
    let fileHandle: any = null;
    
    if (useFilePicker) {
      // Get file handle first (during user gesture) before generating PDF
      fileHandle = await getFileHandleForSaving(defaultFilename);
    }

    // Load PDF module and create document
    const { pdf } = await loadPDFModule();
    const PDFDocument = await createPDFDocument(sectionsToInclude, protocol);
    
    // Generate PDF blob
    const pdfBlob = await pdf(React.createElement(PDFDocument)).toBlob();
    
    if (fileHandle) {
      // Save to user-selected location
      await savePdfToFileHandle(pdfBlob, fileHandle);
    } else {
      // Fallback to traditional download
      savePdfWithDownload(pdfBlob, defaultFilename);
    }
    
  } catch (error) {
    console.error('Error generating PDF:', error);
    throw error;
  }
};

/**
 * Check if the browser supports the File System Access API for save dialogs
 */
export const getFileSystemCapabilities = () => {
  const hasFileSystemAccess = isFileSystemAccessSupported();
  
  return {
    hasFileSystemAccess,
    saveMethod: hasFileSystemAccess ? 'file-picker' : 'download',
    description: hasFileSystemAccess 
      ? 'Browser supports choosing save location'
      : 'Browser will download to default Downloads folder'
  };
};

/**
 * Get PDF generation statistics
 */
export const getPdfStats = (sections: ICFSectionData[]) => {
  const completedSections = sections.filter(
    s => s.status === 'ready_for_review' || s.status === 'approved'
  );
  
  const approvedSections = sections.filter(s => s.status === 'approved');
  
  const totalWords = completedSections.reduce((sum, section) => sum + (section.wordCount || 0), 0);
  
  return {
    totalSections: sections.length,
    completedSections: completedSections.length,
    approvedSections: approvedSections.length,
    totalWords,
    canGeneratePdf: completedSections.length > 0,
  };
};

/**
 * Validate sections for PDF generation
 */
export const validateSectionsForPdf = (sections: ICFSectionData[]): {
  isValid: boolean;
  message: string;
  warnings: string[];
} => {
  const completedSections = sections.filter(
    s => s.status === 'ready_for_review' || s.status === 'approved'
  );
  
  if (completedSections.length === 0) {
    return {
      isValid: false,
      message: 'No sections are ready for PDF generation. Please generate or approve sections first.',
      warnings: []
    };
  }
  
  const warnings: string[] = [];
  
  // Check for empty content
  const emptySections = completedSections.filter(s => !s.content.trim());
  if (emptySections.length > 0) {
    warnings.push(`${emptySections.length} sections have empty content`);
  }
  
  // Check for very short sections
  const shortSections = completedSections.filter(s => (s.wordCount || 0) < 10);
  if (shortSections.length > 0) {
    warnings.push(`${shortSections.length} sections have very short content (< 10 words)`);
  }
  
  // Check if not all sections are approved
  const unapprovedSections = completedSections.filter(s => s.status !== 'approved');
  if (unapprovedSections.length > 0) {
    warnings.push(`${unapprovedSections.length} sections are not yet approved`);
  }
  
  return {
    isValid: true,
    message: `Ready to generate PDF with ${completedSections.length} sections`,
    warnings
  };
};