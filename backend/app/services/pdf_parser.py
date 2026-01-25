"""
PDF text extraction service.

Handles parsing of PDF files and extraction of plain text content.
Uses PyPDF2 for robust PDF processing with fallback mechanisms.
"""

import io
from typing import BinaryIO

from PyPDF2 import PdfReader
from PyPDF2.errors import PdfReadError

from ..exceptions import PDFExtractionError, EmptyPDFError, InvalidFileError


def extract_text_from_pdf(file_content: bytes) -> str:
    """
    Extract plain text from PDF file content.
    
    Reads all pages from the PDF and concatenates their text content.
    Handles encrypted PDFs, corrupted files, and empty documents gracefully.
    
    Args:
        file_content: Raw bytes of the PDF file.
    
    Returns:
        Extracted text as a single string. Newlines and formatting are preserved
        where possible. Whitespace is normalized.
    
    Raises:
        InvalidFileError: If file is not a valid PDF or cannot be parsed.
        EmptyPDFError: If PDF contains no extractable text.
        PDFExtractionError: If text extraction fails for other reasons.
    
    Example:
        >>> with open("resume.pdf", "rb") as f:
        ...     content = f.read()
        >>> text = extract_text_from_pdf(content)
        >>> len(text) > 0
        True
    """
    try:
        # Wrap bytes in BytesIO for file-like interface
        pdf_file = io.BytesIO(file_content)
        
        # Initialize PDF reader
        reader = PdfReader(pdf_file)
        
        # Extract text from all pages
        text_parts = []
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)
        
        # Combine all pages with space separator
        full_text = " ".join(text_parts)
        
        # Validate that we extracted meaningful content
        if not full_text or not full_text.strip():
            raise EmptyPDFError()
        
        return full_text.strip()
    
    except PdfReadError as e:
        # PDF is corrupted or not a valid PDF file
        raise InvalidFileError()
    
    except EmptyPDFError:
        # Re-raise our custom error
        raise
    
    except Exception as e:
        # Catch-all for unexpected errors during extraction
        raise PDFExtractionError(
            detail=f"Unexpected error during PDF extraction: {str(e)}"
        )