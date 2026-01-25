"""
ML module for resume-job fit scoring.

Public API:
    analyze_resume_job_fit(resume_text, job_description_text) -> Dict
"""

from .pipeline import analyze_resume_job_fit

__all__ = ["analyze_resume_job_fit"]