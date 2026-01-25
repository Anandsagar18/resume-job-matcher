"""
Final score computation combining multiple signals into a single fit score.

This module implements the weighted scoring formula that produces the final
resume-job fit score. It combines three orthogonal signals:

1. Semantic similarity (60%): Do the concepts in the resume match the JD?
2. Skill overlap (30%): Does the candidate have the required technical skills?
3. Experience match (10%): Does the candidate have enough years of experience?

Design philosophy:
- Transparent: Each component score is computed independently
- Interpretable: Final score maps to 0-100 scale familiar to users
- Tunable: Weights are centralized in constants.py for easy experimentation
- Conservative: Missing data defaults to neutral scores, not penalties

The scoring formula is:
    raw_score = (0.6 × semantic) + (0.3 × skills) + (0.1 × experience)
    fit_score = raw_score × 100
"""

import re
from typing import Optional
from .constants import RECOGNIZED_SKILLS
from .constants import SKILL_CATEGORIES
from .constants import CATEGORY_WEIGHTS

from .constants import (
    SEMANTIC_SIMILARITY_WEIGHT,
    SKILL_MATCH_WEIGHT,
    EXPERIENCE_MATCH_WEIGHT,
    MIN_EXPERIENCE_YEARS,
    MAX_EXPERIENCE_YEARS,
)


def compute_experience_score(
    resume_text: str,
    job_description_text: str,
) -> float:
    """
    Compute normalized experience match score based on years of experience.
    
    Extracts years of experience from both documents using regex heuristics,
    then computes how well the candidate's experience meets the requirement.
    
    Scoring logic:
    - If JD requires 5 years and resume has 5+: score = 1.0
    - If JD requires 5 years and resume has 3: score = 0.6 (3/5)
    - If JD requires 0 or doesn't mention years: score = 1.0 (no penalty)
    - Score is capped at 1.0 (extra experience doesn't give bonus)
    
    Args:
        resume_text: Full text of candidate's resume.
        job_description_text: Full text of job posting.
    
    Returns:
        Float in range [0.0, 1.0] representing experience alignment.
        
        1.0 = Candidate meets or exceeds experience requirement
        0.0 = Candidate has zero experience when some is required
        0.5 = Candidate has half the required experience
    
    Example:
        >>> resume = "Software engineer with 3 years of experience"
        >>> jd = "Looking for 5+ years experience"
        >>> compute_experience_score(resume, jd)
        0.6  # 3 / 5 = 0.6
        
        >>> jd_no_req = "Looking for a software engineer"
        >>> compute_experience_score(resume, jd_no_req)
        1.0  # No requirement means no penalty
    
    Note:
        Uses regex heuristics which may not catch all phrasings.
        See _extract_years_of_experience for matching patterns.
    """
    candidate_years = _extract_years_of_experience(resume_text)
    required_years = _extract_years_of_experience(job_description_text)
    
    # If JD doesn't specify experience requirement, give perfect score
    if required_years <= 0:
        return 1.0
    
    # Compute ratio, capping at 1.0 (no bonus for extra experience)
    experience_ratio = candidate_years / required_years
    normalized_score = min(experience_ratio, 1.0)
    
    # Ensure score stays within valid bounds
    return max(0.0, normalized_score)


def compute_final_score(
    semantic_similarity: float,
    skill_overlap: float,
    experience_score: float,
) -> float:
    """
    Combine multiple signals into weighted final fit score.
    
    Applies the configured weights to each component score and scales
    the result to a 0-100 range for user-friendly interpretation.
    
    Formula:
        raw_score = (SEMANTIC_WEIGHT × semantic_similarity) +
                   (SKILL_WEIGHT × skill_overlap) +
                   (EXPERIENCE_WEIGHT × experience_score)
        
        fit_score = raw_score × 100
    
    Current weights (from constants.py):
        - Semantic similarity: 60% (most important - captures overall fit)
        - Skill overlap: 30% (hard requirements matter)
        - Experience: 10% (provides signal but isn't everything)
    
    Args:
        semantic_similarity: Semantic match score from embeddings, in [0, 1].
        skill_overlap: Skill match ratio from keyword extraction, in [0, 1].
        experience_score: Experience alignment score, in [0, 1].
    
    Returns:
        Float in range [0.0, 100.0] representing overall fit percentage.
        
        90-100: Excellent fit (rare, top candidates)
        75-89:  Strong fit (good match, likely to interview)
        60-74:  Moderate fit (some alignment, worth reviewing)
        40-59:  Weak fit (significant gaps)
        0-39:   Poor fit (major misalignment)
    
    Example:
        >>> compute_final_score(
        ...     semantic_similarity=0.85,
        ...     skill_overlap=0.75,
        ...     experience_score=1.0
        ... )
        83.5  # (0.6×0.85) + (0.3×0.75) + (0.1×1.0) = 0.835 → 83.5
    
    Note:
        All component scores should be in [0, 1] range.
        Result is rounded to 2 decimal places for consistency.
    """
    # Compute weighted sum of component scores
    # Each component contributes based on its configured importance
    weighted_semantic = SEMANTIC_SIMILARITY_WEIGHT * semantic_similarity
    weighted_skills = SKILL_MATCH_WEIGHT * skill_overlap
    weighted_experience = EXPERIENCE_MATCH_WEIGHT * experience_score
    
    raw_score = weighted_semantic + weighted_skills + weighted_experience
    
    # Scale to 0-100 range for user-friendly percentage
    fit_score_percentage = raw_score * 100.0
    
    # Round to 2 decimal places for clean output
    return round(fit_score_percentage, 2)


def _extract_years_of_experience(text: str) -> float:
    """
    Extract years of experience from text using regex pattern matching.
    
    Searches for common phrasings that indicate years of experience:
    - "3 years experience"
    - "5+ years of experience"
    - "7.5 years"
    - "2 year background"
    
    If multiple year mentions are found (e.g., "3 years Python, 5 years Java"),
    returns the maximum value under the assumption that the highest number
    represents total professional experience.
    
    Args:
        text: Text to search for experience mentions (resume or JD).
    
    Returns:
        Float representing years of experience. Returns 0.0 if no
        experience mention is found in the text.
    
    Example:
        >>> _extract_years_of_experience("5+ years of Python experience")
        5.0
        >>> _extract_years_of_experience("3.5 years software development")
        3.5
        >>> _extract_years_of_experience("Recent college graduate")
        0.0
    
    Limitations:
        - Won't catch "half a decade" or other non-numeric phrasings
        - Assumes Western format (won't catch "経験5年")
        - May miss context (e.g., "avoid candidates with 1 year experience")
        - Simple heuristic, not a full NLP parser
    """
    # Case-insensitive search for year patterns
    text_lower = text.lower()
    
    # Regex pattern explanation:
    # (\d+(?:\.\d+)?) - Captures integers or decimals (3, 5.5, 10)
    # \s*\+?\s* - Optional whitespace, optional plus sign, optional whitespace
    # years? - Matches "year" or "years"
    #
    # Examples matched:
    # - "3 years"
    # - "5+ years"
    # - "7.5 years"
    # - "10+years" (handles missing spaces)
    year_mentions = re.findall(
        r"(\d+(?:\.\d+)?)\s*\+?\s*years?",
        text_lower
    )
    
    # Return 0 if no matches found
    if not year_mentions:
        return 0.0
    
    # Convert all matches to floats and return the maximum
    # Rationale: If someone mentions "3 years Python, 5 years total experience",
    # we want the 5, not the 3
    years_as_floats = [float(years) for years in year_mentions]
    max_years = max(years_as_floats)
    
    return max_years

def compute_weighted_skill_score(matched_skills, required_skills):
    score = 0.0
    total_weight = 0.0

    for category, skills in SKILL_CATEGORIES.items():
        required = skills & required_skills
        if not required:
            continue

        matched = skills & matched_skills
        ratio = len(matched) / len(required)
        weight = CATEGORY_WEIGHTS[category]

        score += ratio * weight
        total_weight += weight

    return score / total_weight if total_weight > 0 else 1.0
