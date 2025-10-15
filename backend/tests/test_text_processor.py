"""
Tests for text processing utilities.

Covers chunking logic, token counting, and edge cases.
"""

import pytest

from app.config import MIN_CHUNK_LENGTH, TEXT_CHUNK_OVERLAP, TEXT_CHUNK_SIZE
from app.services.text_processor import chunk_protocol_text, tiktoken_len


class TestTiktokenLen:
    """Test token length calculation."""

    @pytest.mark.unit
    def test_tiktoken_len_simple_text(self):
        """Test token counting for simple text."""
        text = "Hello, world!"
        token_count = tiktoken_len(text)
        assert isinstance(token_count, int)
        assert token_count > 0
        assert token_count < 10  # Simple text should have few tokens

    @pytest.mark.unit
    def test_tiktoken_len_empty_string(self):
        """Test token counting for empty string."""
        token_count = tiktoken_len("")
        assert token_count == 0

    @pytest.mark.unit
    def test_tiktoken_len_long_text(self):
        """Test token counting for long text."""
        # Create text with known approximate token count
        text = " ".join(["word"] * 100)  # ~100 tokens
        token_count = tiktoken_len(text)
        assert token_count > 90  # Should be close to 100
        assert token_count < 110

    @pytest.mark.unit
    def test_tiktoken_len_special_characters(self):
        """Test token counting with special characters."""
        text = "Hello! @#$% 123 \n\t"
        token_count = tiktoken_len(text)
        assert isinstance(token_count, int)
        assert token_count > 0

    @pytest.mark.unit
    def test_tiktoken_len_unicode(self):
        """Test token counting with unicode characters."""
        text = "Hello 世界 🌍"
        token_count = tiktoken_len(text)
        assert isinstance(token_count, int)
        assert token_count > 0


class TestChunkProtocolText:
    """Test protocol text chunking."""

    @pytest.mark.unit
    def test_chunk_small_text(self):
        """Test chunking text smaller than chunk size."""
        text = "This is a small protocol document for testing."
        chunks = chunk_protocol_text(text)

        assert isinstance(chunks, list)
        assert len(chunks) == 1
        assert chunks[0] == text

    @pytest.mark.unit
    def test_chunk_large_text(self):
        """Test chunking large text that requires splitting."""
        # Create text larger than TEXT_CHUNK_SIZE (2000 tokens)
        # Need ~3000+ tokens to ensure splitting
        text = " ".join(
            ["Protocol section with detailed content"] * 2000
        )  # ~8000 tokens
        chunks = chunk_protocol_text(text)

        assert isinstance(chunks, list)
        assert len(chunks) > 1  # Should be split into multiple chunks
        # Verify each chunk is not empty
        for chunk in chunks:
            assert len(chunk.strip()) > 0

    @pytest.mark.unit
    def test_chunk_text_with_overlap(self):
        """Test that chunks have proper overlap."""
        # Create large enough text to ensure multiple chunks (need >2000 tokens)
        text = " ".join(
            [
                f"Section {idx} with detailed content for protocol testing"
                for idx in range(2000)
            ]
        )
        chunks = chunk_protocol_text(text)

        if len(chunks) > 1:
            # Check that consecutive chunks share some content (overlap)
            for idx in range(len(chunks) - 1):
                # Last words of chunk i should appear in chunk i+1
                chunk_i_words = chunks[idx].split()[-10:]  # Last 10 words
                chunk_next = chunks[idx + 1]
                # At least some overlap should exist
                overlap_found = any(word in chunk_next for word in chunk_i_words)
                assert overlap_found, f"Chunks {idx} and {idx+1} should have overlap"
        else:
            # If only one chunk, that's okay - just verify it's reasonable
            assert len(chunks) == 1

    @pytest.mark.unit
    def test_chunk_empty_string(self):
        """Test chunking empty string."""
        chunks = chunk_protocol_text("")

        assert isinstance(chunks, list)
        assert len(chunks) == 1
        assert chunks[0] == ""

    @pytest.mark.unit
    def test_chunk_whitespace_only(self):
        """Test chunking whitespace-only text."""
        text = "   \n\t  \n   "
        chunks = chunk_protocol_text(text)

        assert isinstance(chunks, list)
        assert len(chunks) == 1
        assert chunks[0] == ""

    @pytest.mark.unit
    def test_chunk_filters_short_chunks(self):
        """Test that very short chunks are filtered out."""
        # Create text that might produce short chunks
        text = "A. " * 100  # Many short segments
        chunks = chunk_protocol_text(text)

        # All chunks should be longer than MIN_CHUNK_LENGTH
        for chunk in chunks:
            assert (
                len(chunk.strip()) >= MIN_CHUNK_LENGTH or chunk.strip() == text.strip()
            )

    @pytest.mark.unit
    def test_chunk_preserves_content(self):
        """Test that no content is lost during chunking."""
        text = "Important protocol information that must be preserved."
        chunks = chunk_protocol_text(text)

        # Verify key words are preserved
        combined = " ".join(chunks)
        assert "Important" in combined
        assert "protocol" in combined
        assert "preserved" in combined

    @pytest.mark.unit
    def test_chunk_with_newlines(self):
        """Test chunking text with newlines."""
        text = "Section 1\n\nThis is section 1 content.\n\nSection 2\n\nThis is section 2 content."
        chunks = chunk_protocol_text(text)

        assert isinstance(chunks, list)
        assert len(chunks) >= 1
        # Content should be preserved
        combined = " ".join(chunks)
        assert "Section 1" in combined
        assert "Section 2" in combined

    @pytest.mark.unit
    def test_chunk_with_special_characters(self):
        """Test chunking text with special characters."""
        text = "Protocol: Study #123 (Phase II/III) - Safety & Efficacy @ 2024"
        chunks = chunk_protocol_text(text)

        assert isinstance(chunks, list)
        assert len(chunks) >= 1
        assert chunks[0].strip() == text.strip()

    @pytest.mark.unit
    def test_chunk_realistic_protocol(self):
        """Test chunking realistic protocol-like text."""
        text = """
        CLINICAL TRIAL PROTOCOL

        Study Title: A Phase III, Randomized, Double-Blind Study
        Protocol Number: ABC-2024-001

        1. BACKGROUND
        This study investigates the efficacy and safety of the experimental treatment.

        2. OBJECTIVES
        Primary: To demonstrate superiority of treatment vs placebo
        Secondary: To evaluate safety and tolerability

        3. STUDY DESIGN
        This is a multicenter, randomized, double-blind, placebo-controlled study.

        4. PATIENT POPULATION
        Inclusion Criteria:
        - Age 18-65 years
        - Diagnosis confirmed
        - Written informed consent

        Exclusion Criteria:
        - Pregnant or nursing
        - Prior treatment within 30 days
        """
        chunks = chunk_protocol_text(text)

        assert isinstance(chunks, list)
        assert len(chunks) >= 1
        # Verify key sections are preserved
        combined = " ".join(chunks)
        assert "CLINICAL TRIAL PROTOCOL" in combined
        assert "OBJECTIVES" in combined
        assert "STUDY DESIGN" in combined

    @pytest.mark.unit
    def test_chunk_returns_stripped_chunks(self):
        """Test that chunks are properly stripped of whitespace."""
        text = "   Content with    extra   spaces   "
        chunks = chunk_protocol_text(text)

        for chunk in chunks:
            # No leading/trailing whitespace
            assert chunk == chunk.strip()

    @pytest.mark.unit
    def test_chunk_configuration_constants(self):
        """Test that chunking respects configuration constants."""
        # Verify config constants are being used
        assert TEXT_CHUNK_SIZE > 0
        assert TEXT_CHUNK_OVERLAP >= 0
        assert MIN_CHUNK_LENGTH > 0
        assert TEXT_CHUNK_OVERLAP < TEXT_CHUNK_SIZE  # Overlap should be less than size


class TestChunkProtocolTextEdgeCases:
    """Test edge cases and error conditions."""

    @pytest.mark.unit
    def test_chunk_very_long_single_line(self):
        """Test chunking extremely long single line."""
        text = "word " * 5000  # Very long single line
        chunks = chunk_protocol_text(text)

        assert isinstance(chunks, list)
        assert len(chunks) > 1  # Should be split

    @pytest.mark.unit
    def test_chunk_unicode_text(self):
        """Test chunking unicode text."""
        text = "临床试验方案 Clinical Trial Protocol 世界 World 🌍"
        chunks = chunk_protocol_text(text)

        assert isinstance(chunks, list)
        assert len(chunks) >= 1
        # Unicode should be preserved
        combined = " ".join(chunks)
        assert "临床试验" in combined or "世界" in combined

    @pytest.mark.unit
    def test_chunk_mixed_content(self):
        """Test chunking mixed content types."""
        text = """
        Text content

        Table:
        | Column1 | Column2 |
        | Value1  | Value2  |

        List:
        - Item 1
        - Item 2
        - Item 3

        More text content.
        """
        chunks = chunk_protocol_text(text)

        assert isinstance(chunks, list)
        assert len(chunks) >= 1
        combined = " ".join(chunks)
        assert "Table:" in combined
        assert "List:" in combined
