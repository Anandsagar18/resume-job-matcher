"""
Pydantic models for request validation and response serialization.

These models define the API contract between client and server.
"""

from typing import List
from pydantic import BaseModel, Field


class EvaluationResponse(BaseModel):
    """
    Response model for resume-job fit evaluation.
    
    Contains comprehensive scoring breakdown and skill analysis.
    """
    
    fit_score: float = Field(
        ...,
        ge=0.0,
        le=100.0,
        description="Overall fit score in range [0, 100]"
    )
    
    semantic_similarity_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Semantic match score in range [0, 1]"
    )
    
    matched_skills: List[str] = Field(
        ...,
        description="Skills present in both resume and job description"
    )
    
    missing_skills: List[str] = Field(
        ...,
        description="Skills required by job but absent from resume"
    )
    
    experience_match_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Experience alignment score in range [0, 1]"
    )
    
    explanation: str = Field(
        ...,
        description="Human-readable summary of the evaluation"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "fit_score": 78.5,
                "semantic_similarity_score": 0.82,
                "matched_skills": ["python", "docker", "machine learning"],
                "missing_skills": ["kubernetes"],
                "experience_match_score": 0.75,
                "explanation": "Semantic match score is 0.82. Matched 3 required skills. Experience alignment score is 0.75. Missing skills include: kubernetes."
            }
        }


class HealthResponse(BaseModel):
    """Health check response model."""
    
    status: str = Field(..., description="Service health status")
    ml_model_loaded: bool = Field(..., description="Whether ML model is initialized")