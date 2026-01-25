"""
ML service wrapper for resume-job fit evaluation.

Provides a clean interface to the ML pipeline with proper error handling
and input validation. This service acts as the bridge between FastAPI
and the core ML module.
"""

from typing import Dict

from ml import analyze_resume_job_fit

from ..exceptions import EmptyJobDescriptionError


class MLService:
    """
    Wrapper service for ML pipeline operations.
    
    Encapsulates the ML pipeline and provides validation and error handling
    at the service boundary. The pipeline is initialized once and reused
    across all requests for efficiency.
    
    Attributes:
        _pipeline_initialized: Flag indicating if ML model is loaded.
    """
    
    def __init__(self):
        """
        Initialize the ML service.
        
        Note:
            The actual ML pipeline initialization happens lazily on first
            evaluate() call to avoid slowing down application startup.
        """
        self._pipeline_initialized = False
    
    def evaluate_fit(
        self,
        resume_text: str,
        job_description: str
    ) -> Dict:
        """
        Evaluate resume-job fit using the ML pipeline.
        
        Validates inputs and delegates to the core ML pipeline for scoring.
        
        Args:
            resume_text: Extracted text from candidate's resume PDF.
            job_description: Plain text job description provided by user.
        
        Returns:
            Dictionary containing:
                - fit_score: Overall match score [0, 100]
                - semantic_similarity_score: Semantic match [0, 1]
                - matched_skills: List of matching skills
                - missing_skills: List of required but absent skills
                - experience_match_score: Experience alignment [0, 1]
                - explanation: Human-readable summary
        
        Raises:
            EmptyJobDescriptionError: If job description is empty or whitespace.
        
        Example:
            >>> service = MLService()
            >>> result = service.evaluate_fit(
            ...     resume_text="Python developer with 3 years experience",
            ...     job_description="Looking for Python expert"
            ... )
            >>> result['fit_score']
            75.2
        """
        # Validate job description is not empty
        if not job_description or not job_description.strip():
            raise EmptyJobDescriptionError()
        
        # Call the ML pipeline (handles resume text validation internally)
        result = analyze_resume_job_fit(
            resume_text=resume_text,
            job_description_text=job_description
        )
        
        # Mark pipeline as initialized after first successful call
        self._pipeline_initialized = True
        
        return result
    
    def is_ready(self) -> bool:
        """
        Check if ML service is ready to handle requests.
        
        Returns:
            True if ML pipeline has been initialized, False otherwise.
        """
        return self._pipeline_initialized