"""
FastAPI application for resume-job fit scoring API.

This module defines the REST API endpoints and coordinates between
PDF parsing, ML evaluation, and response serialization.

The API exposes a single evaluation endpoint that accepts resume PDFs
and job descriptions, returning comprehensive fit scores.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI, File, Form, UploadFile, status
from fastapi.responses import JSONResponse

from .models import EvaluationResponse, HealthResponse
from .services.pdf_parser import extract_text_from_pdf
from .services.ml_service import MLService
from .exceptions import (
    PDFExtractionError,
    EmptyPDFError,
    InvalidFileError,
    EmptyJobDescriptionError
)

from fastapi.middleware.cors import CORSMiddleware





# Global ML service instance (initialized at startup)
ml_service = MLService()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for application startup and shutdown.
    
    Handles resource initialization and cleanup. Currently used to
    pre-warm the ML service on startup for faster first request.
    """
    # Startup: Initialize ML service
    # Note: Model loading happens lazily on first request to avoid
    # blocking startup, but we initialize the service wrapper here
    print("Starting Resume-Job Fit API...")
    print("ML service initialized (model will load on first request)")
    
    yield
    
    # Shutdown: Cleanup (nothing to clean up currently)
    print("Shutting down Resume-Job Fit API...")


# Initialize FastAPI application
app = FastAPI(
    title="Resume-Job Fit Scoring API",
    description="ML-powered API for evaluating how well a resume matches a job description",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get(
    "/health",
    response_model=HealthResponse,
    summary="Health check endpoint",
    description="Check if the API and ML service are operational"
)
async def health_check():
    """
    Health check endpoint.
    
    Returns service status and whether the ML model is loaded.
    Useful for monitoring and load balancer health checks.
    """
    return HealthResponse(
        status="healthy",
        ml_model_loaded=ml_service.is_ready()
    )


@app.post(
    "/evaluate",
    response_model=EvaluationResponse,
    status_code=status.HTTP_200_OK,
    summary="Evaluate resume-job fit",
    description="Upload a resume PDF and job description to get a comprehensive fit score"
)
async def evaluate_resume_job_fit(
    resume: UploadFile = File(
        ...,
        description="Resume PDF file to evaluate"
    ),
    job_description: str = Form(
        ...,
        description="Job description text to match against"
    )
):
    """
    Evaluate how well a resume fits a job description.
    
    This endpoint orchestrates the complete evaluation pipeline:
    1. Validates the uploaded file is a PDF
    2. Extracts text from the PDF
    3. Runs ML scoring pipeline
    4. Returns comprehensive fit analysis
    
    Args:
        resume: Uploaded PDF file containing candidate's resume.
        job_description: Plain text job description to evaluate against.
    
    Returns:
        EvaluationResponse containing:
            - Overall fit score (0-100)
            - Semantic similarity score
            - Matched and missing skills
            - Experience alignment score
            - Human-readable explanation
    
    Raises:
        400 Bad Request: Empty job description, invalid PDF, or empty PDF
        422 Unprocessable Entity: PDF extraction failed
        500 Internal Server Error: Unexpected server error
    """
    # Validate file type
    if not resume.filename.lower().endswith('.pdf'):
        raise InvalidFileError()
    
    # Read file content
    file_content = await resume.read()
    
    # Extract text from PDF
    resume_text = extract_text_from_pdf(file_content)
    
    # Evaluate using ML pipeline
    result = ml_service.evaluate_fit(
        resume_text=resume_text,
        job_description=job_description
    )
    
    # Return response (Pydantic handles serialization)
    return result


@app.exception_handler(PDFExtractionError)
async def pdf_extraction_error_handler(request, exc: PDFExtractionError):
    """Handle PDF extraction errors with proper error response."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )


@app.exception_handler(EmptyPDFError)
async def empty_pdf_error_handler(request, exc: EmptyPDFError):
    """Handle empty PDF errors with proper error response."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )


@app.exception_handler(InvalidFileError)
async def invalid_file_error_handler(request, exc: InvalidFileError):
    """Handle invalid file errors with proper error response."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )


@app.exception_handler(EmptyJobDescriptionError)
async def empty_job_description_error_handler(request, exc: EmptyJobDescriptionError):
    """Handle empty job description errors with proper error response."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc: Exception):
    """Catch-all handler for unexpected errors."""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error occurred"}
    )




## Request Flow

### Successful Request
'''
1. Client sends POST /evaluate
   ├─ resume: resume.pdf (multipart/form-data)
   └─ job_description: "Looking for Python developer..." (form field)

2. app/main.py::evaluate_resume_job_fit()
   ├─ Validates PDF file extension
   ├─ Reads file content into memory
   └─ Calls pdf_parser.extract_text_from_pdf()

3. app/services/pdf_parser.py::extract_text_from_pdf()
   ├─ Parses PDF using PyPDF2
   ├─ Extracts text from all pages
   ├─ Validates non-empty content
   └─ Returns: "Software Engineer with 5 years Python..."

4. app/main.py continues
   └─ Calls ml_service.evaluate_fit()

5. app/services/ml_service.py::evaluate_fit()
   ├─ Validates job_description is non-empty
   └─ Calls ml.analyze_resume_job_fit()

6. ml/pipeline.py::analyze_resume_job_fit()
   ├─ Initializes ResumeJobFitPipeline
   ├─ Tokenizes texts into sentences
   ├─ Generates embeddings
   ├─ Computes semantic similarity
   ├─ Matches skills
   ├─ Scores experience
   ├─ Computes weighted final score
   └─ Returns: {fit_score: 78.5, ...}

7. app/main.py formats response
   └─ Returns: EvaluationResponse JSON

8. Client receives:
{
  "fit_score": 78.5,
  "semantic_similarity_score": 0.82,
  "matched_skills": ["python", "docker"],
  "missing_skills": ["kubernetes"],
  "experience_match_score": 0.75,
  "explanation": "Semantic match score is 0.82..."
}
'''

### Error Handling Examples
'''
**Invalid PDF:**

Client → Invalid file → InvalidFileError (400)
Response: {"detail": "Uploaded file is not a valid PDF"}


**Empty PDF:**

Client → PDF with no text → EmptyPDFError (400)
Response: {"detail": "PDF file contains no extractable text"}


**Empty Job Description:**

Client → "" or "   " → EmptyJobDescriptionError (400)
Response: {"detail": "Job description cannot be empty"}
'''