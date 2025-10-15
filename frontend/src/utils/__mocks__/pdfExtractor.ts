/**
 * Mock implementation of pdfExtractor for testing
 * The actual pdfExtractor uses import.meta which isn't supported in Jest
 */

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

// Re-export the actual implementations for isPDFFile and getTextPreview
// since they don't use import.meta
export function isPDFFile(file: File): boolean {
  return file.type === 'application/pdf' || file.name.toLowerCase().endsWith('.pdf');
}

export function getTextPreview(text: string, maxLength: number = 500): string {
  if (text.length <= maxLength) {
    return text;
  }

  return text.substring(0, maxLength) + '...';
}

// Mock extractTextFromPDF - this is what uses import.meta
export async function extractTextFromPDF(
  file: File,
  onProgress?: (progress: PDFExtractionProgress) => void
): Promise<PDFExtractionResult> {
  throw new Error('extractTextFromPDF should be mocked in tests');
}
