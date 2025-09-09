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
  type: 'paragraph' | 'heading' | 'listItem' | 'horizontalRule' | 'table';
  content: string | TextSegment[] | TableData;
  level?: number; // for headings and list indentation
}

interface TextSegment {
  text: string;
  bold?: boolean;
  italic?: boolean;
  code?: boolean;
}

interface TableData {
  headers: string[];
  rows: string[][];
}

/**
 * Parse inline markdown (bold, italic, code) into text segments
 */
const parseInlineMarkdown = (text: string): TextSegment[] => {
  const segments: TextSegment[] = [];
  let remaining = text;
  
  while (remaining.length > 0) {
    // Check for bold (**text** or __text__)
    const boldMatch = remaining.match(/^\*\*([^*]+)\*\*|^__([^_]+)__/);
    if (boldMatch) {
      const boldText = boldMatch[1] || boldMatch[2];
      segments.push({ text: boldText, bold: true });
      remaining = remaining.substring(boldMatch[0].length);
      continue;
    }
    
    // Check for italic (*text* or _text_)
    const italicMatch = remaining.match(/^\*([^*]+)\*|^_([^_]+)_/);
    if (italicMatch) {
      const italicText = italicMatch[1] || italicMatch[2];
      segments.push({ text: italicText, italic: true });
      remaining = remaining.substring(italicMatch[0].length);
      continue;
    }
    
    // Check for inline code (`code`)
    const codeMatch = remaining.match(/^`([^`]+)`/);
    if (codeMatch) {
      segments.push({ text: codeMatch[1], code: true });
      remaining = remaining.substring(codeMatch[0].length);
      continue;
    }
    
    // Find next markdown character
    const nextMarkdown = remaining.search(/[*_`]/);
    if (nextMarkdown === -1) {
      // No more markdown, add the rest as plain text
      segments.push({ text: remaining });
      break;
    } else if (nextMarkdown === 0) {
      // Markdown character at start but didn't match pattern, skip it
      segments.push({ text: remaining[0] });
      remaining = remaining.substring(1);
    } else {
      // Add plain text up to next markdown character
      segments.push({ text: remaining.substring(0, nextMarkdown) });
      remaining = remaining.substring(nextMarkdown);
    }
  }
  
  return segments;
};

/**
 * Parse a table from markdown lines
 */
const parseTable = (lines: string[], startIndex: number): { table: TableData | null, endIndex: number } => {
  let i = startIndex;
  const tableLines: string[] = [];
  
  // Collect all consecutive lines that contain '|'
  while (i < lines.length && lines[i].includes('|')) {
    tableLines.push(lines[i]);
    i++;
  }
  
  if (tableLines.length < 2) {
    return { table: null, endIndex: startIndex };
  }
  
  // Check if second line is a separator (contains only |, -, :, spaces)
  const separatorLine = tableLines[1];
  if (!/^[\|\-\:\s]+$/.test(separatorLine)) {
    return { table: null, endIndex: startIndex };
  }
  
  // Parse header row
  const headerCells = tableLines[0].split('|').map(cell => cell.trim()).filter(cell => cell);
  
  // Parse data rows (skip separator line)
  const rows: string[][] = [];
  for (let j = 2; j < tableLines.length; j++) {
    const rowCells = tableLines[j].split('|').map(cell => cell.trim()).filter(cell => cell);
    if (rowCells.length > 0) {
      rows.push(rowCells);
    }
  }
  
  return {
    table: {
      headers: headerCells,
      rows: rows
    },
    endIndex: i - 1
  };
};

const parseMarkdownToElements = (content: string): ParsedElement[] => {
  const lines = content.split('\n');
  const elements: ParsedElement[] = [];
  
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    const trimmedLine = line.trim();
    
    if (!trimmedLine) continue;
    
    // Handle horizontal rules (---, ***, ___)
    if (/^(-{3,}|\*{3,}|_{3,})$/.test(trimmedLine)) {
      elements.push({
        type: 'horizontalRule',
        content: ''
      });
      continue;
    }
    
    // Handle tables
    if (trimmedLine.includes('|')) {
      const tableData = parseTable(lines, i);
      if (tableData.table) {
        elements.push({
          type: 'table',
          content: tableData.table
        });
        i = tableData.endIndex; // Skip the processed table lines
        continue;
      }
    }
    
    // Handle headings
    if (trimmedLine.startsWith('#')) {
      const level = (trimmedLine.match(/^#+/) || [''])[0].length;
      const headingText = trimmedLine.replace(/^#+\s*/, '');
      elements.push({
        type: 'heading',
        content: parseInlineMarkdown(headingText),
        level: Math.min(level, 6) // Word supports up to 6 heading levels
      });
    }
    // Handle list items with indentation detection
    else if (/^(\s*)[-*]\s/.test(line) || /^(\s*)\d+\.\s/.test(line)) {
      const indentMatch = line.match(/^(\s*)/);
      const indentLevel = indentMatch ? Math.floor(indentMatch[1].length / 2) : 0; // 2 spaces = 1 level
      const listContent = line.replace(/^\s*[-*]\s|\s*\d+\.\s/, '');
      elements.push({
        type: 'listItem',
        content: parseInlineMarkdown(listContent),
        level: indentLevel
      });
    }
    // Handle paragraphs
    else {
      elements.push({
        type: 'paragraph',
        content: parseInlineMarkdown(trimmedLine)
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
 * Create TextRun elements from text segments with formatting
 */
const createTextRuns = (content: string | TextSegment[] | TableData, docxModule: any): any[] => {
  const { TextRun } = docxModule;
  
  if (typeof content === 'string') {
    return [new TextRun({ text: content, size: 24 })];
  }
  
  if (Array.isArray(content)) {
    return content.map(segment => {
      const runOptions: any = {
        text: segment.text,
        size: 24, // 12pt font
      };
      
      if (segment.bold) runOptions.bold = true;
      if (segment.italic) runOptions.italics = true;
      if (segment.code) {
        runOptions.font = 'Courier New';
        runOptions.color = '2563eb'; // Blue color for code
      }
      
      return new TextRun(runOptions);
    });
  }
  
  return [];
};

/**
 * Convert parsed markdown elements to docx elements
 */
const convertElementsToDocx = (elements: ParsedElement[], docxModule: any) => {
  const { Paragraph, TextRun, HeadingLevel, Table, TableRow, TableCell, WidthType, BorderStyle } = docxModule;
  const docxElements: any[] = [];
  
  elements.forEach(element => {
    switch (element.type) {
      case 'heading':
        const headingLevel = element.level === 1 ? HeadingLevel.HEADING_1 :
                           element.level === 2 ? HeadingLevel.HEADING_2 :
                           element.level === 3 ? HeadingLevel.HEADING_3 :
                           element.level === 4 ? HeadingLevel.HEADING_4 :
                           element.level === 5 ? HeadingLevel.HEADING_5 :
                           HeadingLevel.HEADING_6;
        
        docxElements.push(new Paragraph({
          children: createTextRuns(element.content, docxModule),
          heading: headingLevel,
          spacing: {
            before: 240,
            after: 120,
            line: 240, // Single spacing
          },
        }));
        break;
        
      case 'listItem':
        // Different indentation levels for nested lists
        const indent = (element.level || 0) * 720; // 0.5 inch per level
        
        docxElements.push(new Paragraph({
          children: createTextRuns(element.content, docxModule),
          bullet: {
            level: element.level || 0,
          },
          indent: {
            left: indent,
          },
          spacing: {
            before: 0,
            after: 0,
            line: 240, // Single spacing
          },
        }));
        break;
        
      case 'horizontalRule':
        // Create a horizontal line using a paragraph with a bottom border
        docxElements.push(new Paragraph({
          children: [new TextRun({ text: '', size: 1 })],
          border: {
            bottom: {
              color: 'CCCCCC',
              space: 1,
              style: BorderStyle.SINGLE,
              size: 6,
            },
          },
          spacing: {
            before: 240,
            after: 240,
          },
        }));
        break;
        
      case 'table':
        if (typeof element.content !== 'string' && 'headers' in element.content) {
          const tableData = element.content as TableData;
          
          // Create header row
          const headerRow = new TableRow({
            children: tableData.headers.map(header => 
              new TableCell({
                children: [new Paragraph({
                  children: [new TextRun({ text: header, bold: true, size: 24 })],
                })],
                shading: {
                  fill: 'F3F4F6', // Light gray background for headers
                },
              })
            ),
          });
          
          // Create data rows
          const dataRows = tableData.rows.map(row => 
            new TableRow({
              children: row.map(cell => 
                new TableCell({
                  children: [new Paragraph({
                    children: [new TextRun({ text: cell, size: 24 })],
                  })],
                })
              ),
            })
          );
          
          // Create table
          docxElements.push(new Table({
            rows: [headerRow, ...dataRows],
            width: {
              size: 100,
              type: WidthType.PERCENTAGE,
            },
            margins: {
              top: 120,
              bottom: 120,
            },
          }));
        }
        break;
        
      case 'paragraph':
      default:
        docxElements.push(new Paragraph({
          children: createTextRuns(element.content, docxModule),
          spacing: {
            before: 0,
            after: 120,
            line: 240, // Single spacing
          },
        }));
        break;
    }
  });
  
  return docxElements;
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
    PageBreak
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
        spacing: { before: 60, after: 60, line: 240 },
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
        spacing: { before: 240, after: 120, line: 240 },
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
        spacing: { before: 240, after: 120, line: 240 },
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