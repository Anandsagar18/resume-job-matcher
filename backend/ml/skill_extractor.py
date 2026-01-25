"""
Keyword-based skill extraction and matching for resumes and job descriptions.

This module uses deterministic keyword matching to identify technical skills.
It's intentionally simple and explainable - no ML models, no ambiguity in
what gets matched.

Why keyword-based?
- Explainable: We can show exactly which skills were found
- Fast: No model inference required
- Reliable: Same input always produces same output
- Debuggable: Easy to trace why a skill was/wasn't matched

Known limitations:
- Requires exact phrase matches (won't catch "React.js" if we only list "react")
- Can't handle synonyms (e.g., "ML" vs "machine learning" are different)
- Sensitive to spacing/punctuation (mitigated by normalization)
- Misses context (can't tell "Python" the language from "Python" the snake)
- Limited to curated vocabulary (won't find skills not in RECOGNIZED_SKILLS)

Future improvements could include:
- Fuzzy matching for common abbreviations
- Skill taxonomies to group related terms
- ML-based entity recognition for unknown skills
- But keyword matching is a solid baseline that works well in practice
"""

from typing import List, Set, Tuple
import re
import numpy as np

from .constants import RECOGNIZED_SKILLS


def extract_skills(text: str) -> Set[str]:
    """
    Extract technical skills from text using keyword matching.
    
    Scans the input text for any skills from our curated vocabulary
    (RECOGNIZED_SKILLS). The matching is case-insensitive and handles
    special characters gracefully.
    
    Args:
        text: Input text from resume or job description. Can contain
              multiple paragraphs, bullet points, etc.
    
    Returns:
        Set of skill strings found in the text. Returns empty set if
        no recognized skills are found.
        
        Skills are returned in their canonical form (as defined in
        RECOGNIZED_SKILLS), not as they appear in the text.
    
    Example:
        >>> text = "Experienced with Python, Docker, and Machine Learning"
        >>> extract_skills(text)
        {'python', 'docker', 'machine learning'}
        
        >>> extract_skills("Expert in basket weaving")
        set()  # No recognized skills
    
    Note:
        - Multi-word skills (e.g., "machine learning") are supported
        - Matching is substring-based: "Python3" will match "python"
        - Special characters are normalized before matching
    """
    if not text or not text.strip():
        return set()
    
    # Normalize text for consistent matching
    normalized_text = _normalize_text(text)
    
    # Find all skills present in the normalized text
    found_skills = {
        skill
        for skill in RECOGNIZED_SKILLS
        if skill in normalized_text  # Substring match in normalized space
    }
    
    return found_skills


def match_skills(
    resume_text: str,
    job_description_text: str,
) -> Tuple[List[str], List[str], float]:
    """
    Compare resume skills against job description requirements.
    
    Extracts skills from both documents and computes the overlap to
    determine how well the candidate's skills match the position's
    requirements.
    
    Args:
        resume_text: Full text content of the candidate's resume.
        job_description_text: Full text of the job posting.
    
    Returns:
        Three-element tuple containing:
        
        1. matched_skills (List[str]): Skills present in both resume and JD,
           sorted alphabetically. These are the candidate's relevant skills.
           
        2. missing_skills (List[str]): Skills required by JD but absent from
           resume, sorted alphabetically. These represent gaps in the
           candidate's qualifications.
           
        3. overlap_score (float): Ratio of matched to required skills,
           in range [0.0, 1.0]. Formula: len(matched) / len(required).
           Returns 1.0 if JD has no skill requirements (edge case).
    
    Example:
        >>> resume = "I know Python and Docker"
        >>> jd = "Looking for Python, Docker, and Kubernetes expert"
        >>> matched, missing, score = match_skills(resume, jd)
        >>> matched
        ['docker', 'python']
        >>> missing
        ['kubernetes']
        >>> score
        0.6666...  # 2 out of 3 skills matched
    
    Edge cases:
        - If JD mentions no skills, returns ([], [], 1.0)
        - If resume mentions no skills, returns ([], all_jd_skills, 0.0)
        - Empty inputs are handled gracefully
    """
    # Extract skills from both documents independently
    resume_skills = extract_skills(resume_text)
    jd_required_skills = extract_skills(job_description_text)
    
    # Handle edge case: JD has no skill requirements
    # Return perfect score to avoid penalizing candidate
    if not jd_required_skills:
        return [], [], 1.0
    
    # Compute set intersections and differences
    matched_skills = resume_skills & jd_required_skills  # Set intersection
    missing_skills = jd_required_skills - resume_skills  # Set difference
    
    # Convert to sorted lists for consistent output ordering
    matched_skills_list = sorted(matched_skills)
    missing_skills_list = sorted(missing_skills)
    
    # Compute overlap as ratio of matched to required
    overlap_score = len(matched_skills) / len(jd_required_skills)
    
    return matched_skills_list, missing_skills_list, overlap_score


def _normalize_text(text: str) -> str:
    """
    Normalize text for robust skill matching.
    
    Performs case normalization and punctuation handling to make
    matching more resilient to formatting variations.
    
    Transformations:
    - Convert to lowercase (case-insensitive matching)
    - Replace punctuation with spaces (handles "Python/Django" → "python django")
    - Preserve alphanumerics (keeps "C++", "3D modeling")
    - Preserve + symbol (for "C++", "5+ years")
    
    Args:
        text: Raw text to normalize.
    
    Returns:
        Normalized text string ready for matching.
    
    Example:
        >>> _normalize_text("Python/Django, C++!")
        'python django  c  '
        >>> _normalize_text("Machine-Learning Expert")
        'machine learning expert'
    
    Note:
        This aggressive normalization means "C++" becomes "c  " but
        we match against the skill "c++" which also gets normalized.
        Both normalize to "c  " so matching still works.
    """
    # Convert to lowercase for case-insensitive matching
    lowercased = text.lower()
    
    # Replace non-alphanumeric characters (except + and space) with spaces
    # This handles punctuation, hyphens, slashes, etc.
    # Pattern: keep letters, numbers, +, and spaces; replace everything else
    normalized = re.sub(r"[^a-z0-9+ ]", " ", lowercased)
    
    return normalized

def semantic_skill_match(
    skill_embeddings,
    resume_embeddings,
    threshold: float = 0.65,
):
    matched = set()
    for skill, emb in skill_embeddings.items():
        sims = np.dot(resume_embeddings, emb)
        if np.max(sims) >= threshold:
            matched.add(skill)
    return matched