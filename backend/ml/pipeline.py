"""
End-to-end orchestration pipeline for resume-job fit evaluation.

This module serves as the single entry point for the ML scoring system.
It coordinates all components (embeddings, similarity, skills, scoring)
and ensures data flows correctly between them.

Pipeline architecture:
    Input: (resume_text, job_description_text)
      ↓
    1. Sentence tokenization (split into sentences)
      ↓
    2. Embedding generation (convert to vectors)
      ↓
    3. Semantic similarity computation (compare vectors)
      ↓
    4. Skill extraction and matching (keyword-based)
      ↓
    5. Experience extraction and scoring (regex-based)
      ↓
    6. Weighted final score computation
      ↓
    Output: Dictionary with scores, matches, and explanation

Design principles:
- Single Responsibility: This file only orchestrates, doesn't implement
- Stateful Model: EmbeddingModel is loaded once and reused
- Clean Interfaces: Each component has clear inputs/outputs
- Error Isolation: Components can be tested independently
"""

from typing import Dict, List

from .embeddings import EmbeddingModel
from .similarity import average_max_cosine_similarity
from .skill_extractor import match_skills
from .scorer import compute_experience_score, compute_final_score
from .constants import SKILL_PHRASES




class ResumeJobFitPipeline:
    """
    Orchestrates the complete resume-job matching workflow.
    
    This pipeline combines semantic analysis, skill matching, and experience
    evaluation to produce a comprehensive fit score with detailed breakdowns.
    
    The pipeline is stateful (holds an embedding model) but thread-safe for
    read operations. Multiple evaluate() calls can run in parallel.
    
    Typical usage:
        >>> pipeline = ResumeJobFitPipeline()  # Load model once
        >>> result = pipeline.evaluate(resume_text, jd_text)
        >>> print(f"Fit score: {result['fit_score']}")
        >>> print(f"Missing skills: {result['missing_skills']}")
    
    Attributes:
        embedding_model: Pretrained sentence transformer for semantic encoding.
    """

    def __init__(self) -> None:
        """
        Initialize the pipeline with required models and resources.
        
        Note:
            First initialization will download the embedding model (~80MB)
            from HuggingFace if not already cached. Subsequent initializations
            load from local cache and are fast.
        """

        # Load embedding model once during initialization
        # This is the only stateful component in the pipeline
        self.embedding_model = EmbeddingModel()
        self.skill_embeddings = {
            skill: self.embedding_model.encode([skill])[0]
            for skill in SKILL_PHRASES
        }

    def evaluate(
        self,
        resume_text: str,
        job_description_text: str,
    ) -> Dict:
        """
        Evaluate how well a resume fits a job description.
        
        Runs the complete scoring pipeline and returns a comprehensive
        breakdown of the match quality across multiple dimensions.
        
        Args:
            resume_text: Full text content of the candidate's resume.
                        Should include work experience, skills, education, etc.
            job_description_text: Full text of the job posting.
                                 Should include requirements, responsibilities, etc.
        
        Returns:
            Dictionary containing:
            
            - fit_score (float): Overall match score in [0, 100].
              Higher is better. 75+ indicates strong fit.
              
            - semantic_similarity_score (float): Semantic match score in [0, 1].
              Measures conceptual alignment between resume and JD.
              
            - matched_skills (List[str]): Skills present in both resume and JD.
              Sorted alphabetically. Shows candidate's relevant qualifications.
              
            - missing_skills (List[str]): Skills required by JD but missing from resume.
              Sorted alphabetically. Highlights gaps in candidate's profile.
              
            - experience_match_score (float): Experience alignment in [0, 1].
              Measures if candidate meets years-of-experience requirement.
              
            - explanation (str): Human-readable summary of the evaluation.
              Useful for displaying to users or logging.
        
        Example:
            >>> pipeline = ResumeJobFitPipeline()
            >>> result = pipeline.evaluate(
            ...     resume_text="Python developer with 3 years experience...",
            ...     job_description_text="Looking for Python expert with ML skills..."
            ... )
            >>> result['fit_score']
            72.5
            >>> result['matched_skills']
            ['python']
            >>> result['missing_skills']
            ['machine learning']
        
        Note:
            This method is thread-safe for concurrent calls as long as
            the underlying embedding model supports it (which it does).
        """
        # =====================================================================
        # Step 1: Tokenize text into sentences
        # =====================================================================
        # Break documents into sentences for granular semantic matching
        # Sentence-level embeddings work better than document-level for our use case
        resume_sentences = _tokenize_into_sentences(resume_text)
        jd_sentences = _tokenize_into_sentences(job_description_text)

        # =====================================================================
        # Step 2: Generate embeddings for semantic analysis
        # =====================================================================
        # Convert text into dense vector representations
        # Each sentence becomes a 384-dimensional vector (for default model)
        resume_embeddings = self.embedding_model.encode(resume_sentences)
        jd_embeddings = self.embedding_model.encode(jd_sentences)

        # =====================================================================
        # Step 3: Compute semantic similarity
        # =====================================================================
        # Measure how well resume content covers job requirements conceptually
        # Returns float in [0, 1] where higher means better coverage
        semantic_similarity = average_max_cosine_similarity(
            source_embeddings=jd_embeddings,   # What's required
            target_embeddings=resume_embeddings  # What candidate has
        )

        # =====================================================================
        # Step 4: Extract and match technical skills
        # =====================================================================
        # Keyword-based extraction finds explicit skill mentions
        # Returns matched skills, missing skills, and overlap ratio
        matched_skills, missing_skills, skill_overlap_ratio = match_skills(
            resume_text=resume_text,
            job_description_text=job_description_text
        )

        # =====================================================================
        # Step 5: Evaluate experience alignment
        # =====================================================================
        # Extract years of experience and compute if candidate meets requirement
        # Returns float in [0, 1] where 1.0 means meets or exceeds requirement
        experience_score = compute_experience_score(
            resume_text=resume_text,
            job_description_text=job_description_text
        )

        # =====================================================================
        # Step 6: Compute weighted final score
        # =====================================================================
        # Combine all signals using configured weights from constants.py
        # Returns final score in [0, 100] range
        final_fit_score = compute_final_score(
            semantic_similarity=semantic_similarity,
            skill_overlap=skill_overlap_ratio,
            experience_score=experience_score
        )

        # =====================================================================
        # Step 7: Generate human-readable explanation
        # =====================================================================
        explanation = _generate_explanation(
            semantic_similarity=semantic_similarity,
            matched_skills=matched_skills,
            missing_skills=missing_skills,
            experience_score=experience_score
        )

        # =====================================================================
        # Return comprehensive results
        # =====================================================================
        return {
            "fit_score": final_fit_score,
            "semantic_similarity_score": round(semantic_similarity, 3),
            "matched_skills": matched_skills,
            "missing_skills": missing_skills,
            "experience_match_score": round(experience_score, 3),
            "explanation": explanation,
        }


def _tokenize_into_sentences(text: str) -> List[str]:
    """
    Split text into sentences using a lightweight rule-based approach.

    This avoids runtime dependency downloads (e.g., NLTK punkt),
    which can be fragile in production environments.

    Args:
        text: Raw text to tokenize.

    Returns:
        List of sentence strings. Returns [''] if input is empty.
    """
    if not text or not text.strip():
        return [""]

    # Simple but robust sentence splitting
    sentences = [
        s.strip()
        for s in text.replace("\n", " ").split(".")
        if s.strip()
    ]

    return sentences if sentences else [text]



def _generate_explanation(
    semantic_similarity: float,
    matched_skills: List[str],
    missing_skills: List[str],
    experience_score: float,
) -> str:
    """
    Generate human-readable explanation of the evaluation results.
    
    Summarizes the key findings in natural language suitable for
    displaying to users or including in reports.
    
    Args:
        semantic_similarity: Semantic match score in [0, 1].
        matched_skills: List of skills found in both resume and JD.
        missing_skills: List of skills required but not found in resume.
        experience_score: Experience alignment score in [0, 1].
    
    Returns:
        Multi-sentence explanation string summarizing the evaluation.
    
    Example:
        >>> _generate_explanation(
        ...     semantic_similarity=0.82,
        ...     matched_skills=['python', 'docker'],
        ...     missing_skills=['kubernetes'],
        ...     experience_score=0.75
        ... )
        'Semantic match score is 0.82. Matched 2 required skills. ...'
    """
    # Count matched and missing skills for summary
    num_matched = len(matched_skills)
    
    # Format missing skills list, or indicate none are missing
    missing_skills_text = (
        ", ".join(missing_skills) if missing_skills else "None"
    )
    
    # Construct explanation with key metrics
    explanation = (
        f"Semantic match score is {semantic_similarity:.2f}. "
        f"Matched {num_matched} required skill{'s' if num_matched != 1 else ''}. "
        f"Experience alignment score is {experience_score:.2f}. "
        f"Missing skills include: {missing_skills_text}."
    )

    return explanation

def analyze_resume_job_fit(
    resume_text: str,
    job_description_text: str,
) -> Dict:
    """
    Public functional API for resume–job fit analysis.

    This wrapper exposes a simple function-based interface over the
    ResumeJobFitPipeline class, making integration with scripts,
    FastAPI endpoints, and tests straightforward.

    Args:
        resume_text: Full resume text.
        job_description_text: Full job description text.

    Returns:
        Dictionary containing fit score, skill matches, and explanation.
    """
    pipeline = ResumeJobFitPipeline()
    return pipeline.evaluate(resume_text, job_description_text)
