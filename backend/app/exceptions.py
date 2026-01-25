"""
Custom exceptions for the FastAPI application.

Defines domain-specific errors with appropriate HTTP status codes.
"""

from fastapi import HTTPException, status


class PDFExtractionError(HTTPException):
    """Raised when PDF text extraction fails."""
    
    def __init__(self, detail: str = "Failed to extract text from PDF"):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail
        )


class EmptyPDFError(HTTPException):
    """Raised when PDF contains no extractable text."""
    
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="PDF file contains no extractable text"
        )


class InvalidFileError(HTTPException):
    """Raised when uploaded file is not a valid PDF."""
    
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is not a valid PDF"
        )


class EmptyJobDescriptionError(HTTPException):
    """Raised when job description is empty or whitespace-only."""
    
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Job description cannot be empty"
        )