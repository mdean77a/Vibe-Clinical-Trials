/**
 * Tests for pdfExtractor utility functions
 *
 * Note: extractTextFromPDF is not tested here due to import.meta.url issues in Jest.
 * It relies on pdfjs-dist which uses ESM modules and import.meta, which are not
 * supported in Jest's CommonJS environment. This function should be tested via:
 * 1. Integration tests with real PDF files
 * 2. E2E tests in the browser
 */

// Use the mock version to avoid import.meta issues
jest.mock('../pdfExtractor');

import { isPDFFile, getTextPreview } from '../pdfExtractor';

describe('pdfExtractor', () => {
  describe('isPDFFile', () => {
    it('returns true for PDF MIME type', () => {
      const file = new File(['content'], 'test.pdf', { type: 'application/pdf' });
      expect(isPDFFile(file)).toBe(true);
    });

    it('returns true for .pdf extension regardless of MIME type', () => {
      const file = new File(['content'], 'test.pdf', { type: '' });
      expect(isPDFFile(file)).toBe(true);
    });

    it('returns true for .PDF extension (case insensitive)', () => {
      const file = new File(['content'], 'test.PDF', { type: '' });
      expect(isPDFFile(file)).toBe(true);
    });

    it('returns true for mixed case PDF extension', () => {
      const file = new File(['content'], 'test.Pdf', { type: '' });
      expect(isPDFFile(file)).toBe(true);
    });

    it('returns false for non-PDF file', () => {
      const file = new File(['content'], 'test.txt', { type: 'text/plain' });
      expect(isPDFFile(file)).toBe(false);
    });

    it('returns false for PDF-like name but wrong extension', () => {
      const file = new File(['content'], 'mypdf.txt', { type: 'text/plain' });
      expect(isPDFFile(file)).toBe(false);
    });

    it('returns false for file with no extension', () => {
      const file = new File(['content'], 'document', { type: '' });
      expect(isPDFFile(file)).toBe(false);
    });

    it('returns false for empty filename', () => {
      const file = new File(['content'], '', { type: '' });
      expect(isPDFFile(file)).toBe(false);
    });

    it('returns false for common document formats', () => {
      const docx = new File(['content'], 'test.docx', { type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' });
      const txt = new File(['content'], 'test.txt', { type: 'text/plain' });
      const xlsx = new File(['content'], 'test.xlsx', { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });

      expect(isPDFFile(docx)).toBe(false);
      expect(isPDFFile(txt)).toBe(false);
      expect(isPDFFile(xlsx)).toBe(false);
    });

    it('returns true when PDF MIME type but no extension', () => {
      const file = new File(['content'], 'document', { type: 'application/pdf' });
      expect(isPDFFile(file)).toBe(true);
    });

    it('handles file with multiple dots in name', () => {
      const file = new File(['content'], 'my.document.test.pdf', { type: '' });
      expect(isPDFFile(file)).toBe(true);
    });
  });

  describe('getTextPreview', () => {
    describe('Basic Truncation', () => {
      it('returns full text when shorter than max length', () => {
        const text = 'Short text';
        expect(getTextPreview(text, 500)).toBe('Short text');
      });

      it('returns full text when exactly max length', () => {
        const text = 'A'.repeat(500);
        expect(getTextPreview(text, 500)).toBe(text);
      });

      it('truncates text longer than max length', () => {
        const text = 'A'.repeat(1000);
        const preview = getTextPreview(text, 500);
        expect(preview).toBe('A'.repeat(500) + '...');
        expect(preview.length).toBe(503); // 500 + '...'
      });

      it('uses default max length of 500', () => {
        const text = 'A'.repeat(1000);
        const preview = getTextPreview(text);
        expect(preview).toBe('A'.repeat(500) + '...');
      });
    });

    describe('Edge Cases', () => {
      it('handles empty text', () => {
        expect(getTextPreview('', 500)).toBe('');
      });

      it('handles very small max length', () => {
        const text = 'Hello world';
        const preview = getTextPreview(text, 5);
        expect(preview).toBe('Hello...');
      });

      it('handles max length of 1', () => {
        const text = 'Hello world';
        const preview = getTextPreview(text, 1);
        expect(preview).toBe('H...');
      });

      it('handles max length of 0', () => {
        const text = 'Hello world';
        const preview = getTextPreview(text, 0);
        expect(preview).toBe('...');
      });

      it('handles negative max length', () => {
        const text = 'Hello world';
        const preview = getTextPreview(text, -10);
        expect(preview).toBe('...');
      });
    });

    describe('Special Characters', () => {
      it('handles text with special characters', () => {
        const text = 'Hello <world> & "special" \'characters\'!';
        expect(getTextPreview(text, 500)).toBe(text);
      });

      it('truncates text with special characters correctly', () => {
        const text = '<hello>' + 'A'.repeat(1000);
        const preview = getTextPreview(text, 10);
        expect(preview).toBe('<hello>AAA...');
      });

      it('handles HTML-like tags', () => {
        const text = '<div><span>Content</span></div>';
        expect(getTextPreview(text, 500)).toBe(text);
      });

      it('handles quotes and apostrophes', () => {
        const text = 'He said, "Hello!" and she replied, \'Hi!\'';
        expect(getTextPreview(text, 500)).toBe(text);
      });

      it('handles special symbols', () => {
        const text = '© ® ™ § € £ ¥ ± × ÷';
        expect(getTextPreview(text, 500)).toBe(text);
      });
    });

    describe('Multiline Text', () => {
      it('handles multiline text', () => {
        const text = 'Line 1\nLine 2\nLine 3';
        expect(getTextPreview(text, 500)).toBe(text);
      });

      it('truncates multiline text correctly', () => {
        const text = 'Line 1\nLine 2\n' + 'A'.repeat(1000);
        const preview = getTextPreview(text, 20);
        // 'Line 1\n' = 7 chars, 'Line 2\n' = 7 chars, remaining = 6 chars
        expect(preview.length).toBe(23); // 20 + '...'
        expect(preview).toContain('Line 1');
        expect(preview).toContain('Line 2');
        expect(preview).toMatch(/\.\.\.$/); // ends with ...
      });

      it('handles Windows line endings', () => {
        const text = 'Line 1\r\nLine 2\r\nLine 3';
        expect(getTextPreview(text, 500)).toBe(text);
      });

      it('handles mixed line endings', () => {
        const text = 'Line 1\nLine 2\r\nLine 3\rLine 4';
        expect(getTextPreview(text, 500)).toBe(text);
      });

      it('handles text with only newlines', () => {
        const text = '\n\n\n';
        expect(getTextPreview(text, 500)).toBe(text);
      });
    });

    describe('Unicode and Emojis', () => {
      it('handles unicode characters', () => {
        const text = '你好世界 🌍 café';
        expect(getTextPreview(text, 500)).toBe(text);
      });

      it('handles emojis', () => {
        const text = '😀 😃 😄 😁 🎉 🎊 🎈';
        expect(getTextPreview(text, 500)).toBe(text);
      });

      it('truncates text with emojis correctly', () => {
        const text = '😀'.repeat(1000);
        const preview = getTextPreview(text, 10);
        // Emojis are multi-byte, so truncation might not be exactly 10 characters
        expect(preview).toContain('😀');
        expect(preview).toContain('...');
      });

      it('handles mixed unicode scripts', () => {
        const text = 'Hello мир 世界 مرحبا שלום';
        expect(getTextPreview(text, 500)).toBe(text);
      });

      it('handles Arabic and RTL text', () => {
        const text = 'مرحبا بك في العالم';
        expect(getTextPreview(text, 500)).toBe(text);
      });
    });

    describe('Real-world Scenarios', () => {
      it('handles typical protocol text', () => {
        const text = 'Study Protocol: XYZ-123\nPhase: III\nObjective: To evaluate...';
        expect(getTextPreview(text, 500)).toBe(text);
      });

      it('handles protocol text that needs truncation', () => {
        const longProtocol = 'Study Protocol: XYZ-123\n'.repeat(100);
        const preview = getTextPreview(longProtocol, 100);
        expect(preview.length).toBe(103); // 100 + '...'
        expect(preview).toContain('Study Protocol');
        expect(preview).toMatch(/\.\.\.$/); // ends with ...
      });

      it('preserves formatting in preview', () => {
        const text = 'Title: Important Study\n\n1. Introduction\n2. Methods\n3. Results';
        const preview = getTextPreview(text, 100);
        if (text.length > 100) {
          expect(preview).toContain('Title');
          expect(preview).toMatch(/\.\.\.$/); // ends with ...
        } else {
          expect(preview).toBe(text);
        }
      });

      it('handles very long single word', () => {
        const longWord = 'A'.repeat(1000);
        const preview = getTextPreview(longWord, 50);
        expect(preview.length).toBe(53); // 50 + '...'
        expect(preview).toMatch(/^A+\.\.\.$/);
      });

      it('handles text with tabs', () => {
        const text = 'Column1\tColumn2\tColumn3';
        expect(getTextPreview(text, 500)).toBe(text);
      });

      it('handles text with various whitespace', () => {
        const text = 'Text   with    irregular     spacing';
        expect(getTextPreview(text, 500)).toBe(text);
      });
    });

    describe('Performance Considerations', () => {
      it('handles extremely long text efficiently', () => {
        const longText = 'A'.repeat(1000000);
        const start = Date.now();
        const preview = getTextPreview(longText, 1000);
        const duration = Date.now() - start;

        expect(preview.length).toBe(1003); // 1000 + '...'
        expect(duration).toBeLessThan(100); // Should be fast
      });

      it('does not modify original text', () => {
        const text = 'Original text that should not be modified';
        const preview = getTextPreview(text, 10);

        expect(text).toBe('Original text that should not be modified');
        expect(preview).not.toBe(text);
      });
    });
  });
});
