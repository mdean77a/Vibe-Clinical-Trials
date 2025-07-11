/**
 * PDF text extraction utility using PDF.js
 * Extracts text from PDF files on the client-side
 */

// Dynamic import to avoid SSR issues
let pdfjsLib: any = null;

export interface PDFExtractionResult {
  text: string;
  pageCount: number;
  extractedAt: string;
}

export interface PDFExtractionProgress {
  currentPage: number;
  totalPages: number;
  percentage: number;
}

/**
 * Initialize PDF.js library (client-side only)
 */
async function initializePDFJS() {
  if (pdfjsLib) return pdfjsLib;
  
  if (typeof window === 'undefined') {
    throw new Error('PDF extraction is only available in the browser');
  }
  
  // Dynamic import to avoid SSR issues
  pdfjsLib = await import('pdfjs-dist');
  
  // Configure PDF.js worker - use local worker file
  pdfjsLib.GlobalWorkerOptions.workerSrc = new URL(
    'pdfjs-dist/build/pdf.worker.mjs',
    import.meta.url
  ).toString();
  
  return pdfjsLib;
}

/**
 * Extract text from a PDF file
 * @param file The PDF file to extract text from
 * @param onProgress Optional callback for progress updates
 * @returns Promise with extraction result
 */
export async function extractTextFromPDF(
  file: File,
  onProgress?: (progress: PDFExtractionProgress) => void
): Promise<PDFExtractionResult> {
  try {
    // Initialize PDF.js library
    const pdfjs = await initializePDFJS();
    
    // Convert file to ArrayBuffer
    const arrayBuffer = await file.arrayBuffer();
    
    // Load the PDF document
    const pdf = await pdfjs.getDocument({ data: arrayBuffer }).promise;
    const pageCount = pdf.numPages;
    
    let fullText = '';
    
    // Extract text from each page
    for (let pageNum = 1; pageNum <= pageCount; pageNum++) {
      const page = await pdf.getPage(pageNum);
      const textContent = await page.getTextContent();
      
      // Combine text items from the page
      const pageText = textContent.items
        .map((item: any) => item.str)
        .join(' ');
      
      // Add page marker and text
      fullText += `\n\n--- Page ${pageNum} ---\n\n`;
      fullText += pageText;
      
      // Report progress
      if (onProgress) {
        onProgress({
          currentPage: pageNum,
          totalPages: pageCount,
          percentage: Math.round((pageNum / pageCount) * 100)
        });
      }
    }
    
    return {
      text: fullText.trim(),
      pageCount,
      extractedAt: new Date().toISOString()
    };
  } catch (error) {
    console.error('PDF extraction error:', error);
    throw new Error(`Failed to extract text from PDF: ${error instanceof Error ? error.message : 'Unknown error'}`);
  }
}

/**
 * Validate if a file is a PDF
 * @param file The file to validate
 * @returns True if the file is a PDF
 */
export function isPDFFile(file: File): boolean {
  return file.type === 'application/pdf' || file.name.toLowerCase().endsWith('.pdf');
}

/**
 * Get a preview of the extracted text
 * @param text The full extracted text
 * @param maxLength Maximum length of the preview
 * @returns Truncated preview of the text
 */
export function getTextPreview(text: string, maxLength: number = 500): string {
  if (text.length <= maxLength) {
    return text;
  }
  
  return text.substring(0, maxLength) + '...';
}