/**
 * Word Document Generation utility for ICF documents using docx.js
 * 
 * This module provides functionality to generate professional Word documents from ICF sections
 * with markdown content, consistent formatting with PDF output, and metadata.
 */

import type { ICFSectionData } from '../components/icf/ICFSection';
import type { Protocol } from '../types/protocol';

// Dynamic import for docx to avoid SSR issues
let DocxModule: any = null;

const loadDocxModule = async () => {
  if (DocxModule) return DocxModule;
  
  // Dynamic import with proper typing
  const docxModule = await import('docx');
  DocxModule = docxModule;
  return docxModule;
};

/**
 * Parse markdown content into structured elements for Word rendering
 */
interface ParsedElement {
  type: 'paragraph' | 'heading' | 'listItem';
  content: string;
  level?: number; // for headings
}

const parseMarkdownToElements = (content: string): ParsedElement[] => {
  const lines = content.split('\n');
  const elements: ParsedElement[] = [];
  
  for (const line of lines) {
    const trimmedLine = line.trim();
    
    if (!trimmedLine) continue;
    
    // Handle headings
    if (trimmedLine.startsWith('#')) {
      const level = (trimmedLine.match(/^#+/) || [''])[0].length;
      const headingText = trimmedLine.replace(/^#+\s*/, '');
      elements.push({
        type: 'heading',
        content: headingText,
        level: Math.min(level, 6) // Word supports up to 6 heading levels
      });
    }
    // Handle list items
    else if (trimmedLine.startsWith('- ') || trimmedLine.startsWith('* ') || /^\d+\.\s/.test(trimmedLine)) {
      const listContent = trimmedLine.replace(/^[-*]\s|^\d+\.\s/, '');
      elements.push({
        type: 'listItem',
        content: listContent
      });
    }
    // Handle paragraphs
    else {
      elements.push({
        type: 'paragraph',
        content: trimmedLine
      });
    }
  }
  
  return elements;
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
          description: 'Word documents',
          accept: {
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
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
 * Save Word document to file handle
 */
const saveDocxToFileHandle = async (docxBlob: Blob, fileHandle: any): Promise<void> => {
  try {
    const writable = await fileHandle.createWritable();
    await writable.write(docxBlob);
    await writable.close();
    
    console.log(`Word document saved successfully to user-selected location`);
  } catch (error) {
    console.error('Error writing to file:', error);
    throw new Error('Failed to write Word document to selected location');
  }
};

/**
 * Save Word document using traditional download (fallback method)
 */
const saveDocxWithDownload = (docxBlob: Blob, filename: string): void => {
  const url = URL.createObjectURL(docxBlob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  
  // Trigger download
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  
  // Clean up
  URL.revokeObjectURL(url);
  
  console.log(`Word document downloaded to default location: ${filename}`);
};

/**
 * Convert parsed markdown elements to docx elements
 */
const convertElementsToDocx = (elements: ParsedElement[], docxModule: any) => {
  const { Paragraph, TextRun, HeadingLevel } = docxModule;
  
  return elements.map(element => {
    switch (element.type) {
      case 'heading':
        const headingLevel = element.level === 1 ? HeadingLevel.HEADING_1 :
                           element.level === 2 ? HeadingLevel.HEADING_2 :
                           element.level === 3 ? HeadingLevel.HEADING_3 :
                           element.level === 4 ? HeadingLevel.HEADING_4 :
                           element.level === 5 ? HeadingLevel.HEADING_5 :
                           HeadingLevel.HEADING_6;
        
        return new Paragraph({
          text: element.content,
          heading: headingLevel,
          spacing: {
            before: 240,
            after: 120,
          },
        });
        
      case 'listItem':
        return new Paragraph({
          text: element.content,
          bullet: {
            level: 0,
          },
          spacing: {
            before: 60,
            after: 60,
          },
        });
        
      case 'paragraph':
      default:
        return new Paragraph({
          children: [
            new TextRun({
              text: element.content,
              size: 24, // 12pt font
            }),
          ],
          spacing: {
            before: 120,
            after: 120,
            line: 360, // 1.5 line spacing
          },
        });
    }
  });
};

/**
 * Create Word document from ICF sections
 */
const createWordDocument = async (sections: ICFSectionData[], protocol: Protocol) => {
  const docxModule = await loadDocxModule();
  const { 
    Document, 
    Paragraph, 
    TextRun, 
    HeadingLevel, 
    AlignmentType, 
    PageBreak,
    TableOfContents,
    StyleLevel
  } = docxModule;

  // Filter sections to include only completed ones
  const completedSections = sections.filter(
    section => section.status === 'ready_for_review' || section.status === 'approved'
  );

  // Create document sections
  const documentChildren = [
    // Cover page
    new Paragraph({
      children: [
        new TextRun({
          text: 'Informed Consent Form',
          size: 48, // 24pt
          bold: true,
        }),
      ],
      alignment: AlignmentType.CENTER,
      spacing: { before: 1440, after: 480 }, // Large spacing for cover page
    }),
    new Paragraph({
      children: [
        new TextRun({
          text: protocol.protocol_title,
          size: 32, // 16pt
          bold: true,
        }),
      ],
      alignment: AlignmentType.CENTER,
      spacing: { before: 240, after: 240 },
    }),
    new Paragraph({
      children: [
        new TextRun({
          text: `Study: ${protocol.study_acronym}`,
          size: 28, // 14pt
        }),
      ],
      alignment: AlignmentType.CENTER,
      spacing: { before: 240, after: 480 },
    }),
    new Paragraph({
      children: [
        new TextRun({
          text: `Generated on ${new Date().toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'long', 
            day: 'numeric'
          })}`,
          size: 24, // 12pt
          italics: true,
        }),
      ],
      alignment: AlignmentType.CENTER,
      spacing: { before: 960, after: 240 },
    }),
    new Paragraph({
      children: [
        new TextRun({
          text: 'Clinical Trial Accelerator - AI-Generated Document',
          size: 20, // 10pt
          color: '666666',
        }),
      ],
      alignment: AlignmentType.CENTER,
      spacing: { before: 480 },
    }),
    
    // Page break before table of contents
    new Paragraph({
      children: [new PageBreak()],
    }),
    
    // Table of Contents
    new Paragraph({
      text: 'Table of Contents',
      heading: HeadingLevel.HEADING_1,
      spacing: { before: 240, after: 480 },
    }),
    
    // TOC entries
    ...completedSections.map((section, index) => 
      new Paragraph({
        children: [
          new TextRun({
            text: `${index + 1}. ${section.title}`,
            size: 24,
          }),
        ],
        spacing: { before: 120, after: 120 },
      })
    ),
  ];

  // Add ICF sections
  completedSections.forEach((section, index) => {
    // Page break before each section
    documentChildren.push(
      new Paragraph({
        children: [new PageBreak()],
      })
    );
    
    // Section title
    documentChildren.push(
      new Paragraph({
        text: `${index + 1}. ${section.title}`,
        heading: HeadingLevel.HEADING_1,
        spacing: { before: 240, after: 480 },
      })
    );
    
    // Section content
    const parsedElements = parseMarkdownToElements(section.content);
    const docxElements = convertElementsToDocx(parsedElements, docxModule);
    documentChildren.push(...docxElements);
    
    // Section metadata
    documentChildren.push(
      new Paragraph({
        children: [
          new TextRun({
            text: `Status: ${section.status === 'approved' ? 'Approved' : 'Ready for Review'} | `,
            size: 18,
            color: '666666',
            italics: true,
          }),
          new TextRun({
            text: `Word Count: ${section.wordCount || 0} | `,
            size: 18,
            color: '666666',
            italics: true,
          }),
          new TextRun({
            text: `Section: ${section.name}`,
            size: 18,
            color: '666666',
            italics: true,
          }),
        ],
        spacing: { before: 480, after: 240 },
        border: {
          top: { style: 'single', size: 1, color: 'CCCCCC' },
        },
      })
    );
  });

  // Create document
  const doc = new Document({
    sections: [
      {
        properties: {
          page: {
            margin: {
              top: 1440,    // 1 inch
              right: 1440,  // 1 inch
              bottom: 1440, // 1 inch
              left: 1440,   // 1 inch
            },
          },
        },
        children: documentChildren,
      },
    ],
    title: `${protocol.study_acronym} - Informed Consent Form`,
    description: `ICF for ${protocol.protocol_title}`,
    creator: 'Clinical Trial Accelerator',
    company: 'Clinical Trial Accelerator',
    lastModifiedBy: 'AI Document Generator',
  });

  return doc;
};

/**
 * Generate and save ICF Word document with user-selectable location
 */
export const generateICFDocx = async (
  sections: ICFSectionData[], 
  protocol: Protocol,
  options: {
    includeAllSections?: boolean;
    filename?: string;
    useFilePicker?: boolean;
  } = {}
): Promise<void> => {
  try {
    // Filter sections based on options
    const sectionsToInclude = options.includeAllSections 
      ? sections 
      : sections.filter(s => s.status === 'ready_for_review' || s.status === 'approved');

    if (sectionsToInclude.length === 0) {
      throw new Error('No sections available for Word document generation. Please generate or approve sections first.');
    }

    // Generate filename
    const timestamp = new Date().toISOString().split('T')[0];
    const defaultFilename = options.filename || `${protocol.study_acronym}_ICF_${timestamp}.docx`;
    
    // Determine save method and get file handle first if using file picker
    const useFilePicker = options.useFilePicker !== false && isFileSystemAccessSupported();
    let fileHandle: any = null;
    
    if (useFilePicker) {
      // Get file handle first (during user gesture) before generating document
      fileHandle = await getFileHandleForSaving(defaultFilename);
    }

    // Load docx module and create document
    const docxModule = await loadDocxModule();
    const { Packer } = docxModule;
    const doc = await createWordDocument(sectionsToInclude, protocol);
    
    // Generate Word document blob
    const docxBlob = await Packer.toBlob(doc);
    
    if (fileHandle) {
      // Save to user-selected location
      await saveDocxToFileHandle(docxBlob, fileHandle);
    } else {
      // Fallback to traditional download
      saveDocxWithDownload(docxBlob, defaultFilename);
    }
    
  } catch (error) {
    console.error('Error generating Word document:', error);
    throw error;
  }
};

/**
 * Validate sections for Word document generation
 */
export const validateSectionsForDocx = (sections: ICFSectionData[]): {
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
      message: 'No sections are ready for Word document generation. Please generate or approve sections first.',
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
    message: `Ready to generate Word document with ${completedSections.length} sections`,
    warnings
  };
};

/**
 * Get file system capabilities for Word documents
 */
export const getDocxFileSystemCapabilities = () => {
  const hasFileSystemAccess = isFileSystemAccessSupported();
  
  return {
    hasFileSystemAccess,
    saveMethod: hasFileSystemAccess ? 'file-picker' : 'download',
    description: hasFileSystemAccess 
      ? 'Browser supports choosing save location'
      : 'Browser will download to default Downloads folder'
  };
};