"""
Semantic similarity computation using cosine distance between embeddings.

This module implements the core semantic matching logic that compares
job description requirements against resume content using vector similarity.

Mathematical foundation:
- Cosine similarity measures the angle between two vectors
- Range: [-1, 1], but normalized embeddings yield [0, 1]
- Formula: cos(θ) = (A · B) / (||A|| × ||B||)
- With L2-normalized vectors: cos(θ) = A · B (simple dot product)

Why average-max similarity?
- A job description has multiple requirements (sentences)
- For each requirement, we find the best-matching resume sentence
- Average across requirements gives overall coverage score
- This approach rewards comprehensive matches over single strong matches
"""

from typing import Tuple

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity


def average_max_cosine_similarity(
    source_embeddings: np.ndarray,
    target_embeddings: np.ndarray,
) -> float:
    """
    Compute semantic coverage from source to target using max-pooled similarity.
    
    For each sentence in the source (typically job description), find the
    most similar sentence in the target (typically resume), then average
    these maximum similarities to get an overall coverage score.
    
    This metric answers: "How well does the resume cover each requirement
    mentioned in the job description?"
    
    Algorithm:
    1. Compute pairwise cosine similarity matrix (source_size × target_size)
    2. For each source sentence, take max similarity across all target sentences
    3. Average these max similarities to get final score
    
    Args:
        source_embeddings: Sentence embeddings from job description.
                          Shape: (num_source_sentences, embedding_dim)
        target_embeddings: Sentence embeddings from resume.
                          Shape: (num_target_sentences, embedding_dim)
    
    Returns:
        Float similarity score in range [0.0, 1.0] where:
        - 1.0 = perfect semantic coverage (every JD sentence has exact match)
        - 0.0 = no semantic overlap (orthogonal vectors)
        - 0.7+ = strong match (typical for good candidates)
        - 0.5-0.7 = moderate match
        - <0.5 = weak match
    
    Raises:
        ValueError: If input arrays have incompatible shapes or are empty.
    
    Example:
        >>> jd_emb = np.array([[0.1, 0.2], [0.3, 0.4]])  # 2 JD sentences
        >>> resume_emb = np.array([[0.15, 0.25], [0.8, 0.1]])  # 2 resume sentences
        >>> score = average_max_cosine_similarity(jd_emb, resume_emb)
        >>> 0.0 <= score <= 1.0
        True
    
    Note:
        Assumes embeddings are L2-normalized (from embeddings.py).
        If not normalized, cosine_similarity handles it but is slower.
    """
    # Defensive checks for input validity
    _validate_embeddings(source_embeddings, target_embeddings)
    
    # Compute pairwise cosine similarities
    # Shape: (num_source_sentences, num_target_sentences)
    similarity_matrix = cosine_similarity(source_embeddings, target_embeddings)
    
    # For each source sentence, find the best match in target
    # Shape: (num_source_sentences,)
    max_similarities = similarity_matrix.max(axis=1)
    
    # Average across all source sentences to get overall coverage
    average_similarity = float(max_similarities.mean())
    
    # Ensure output is in valid range (handles numerical edge cases)
    return np.clip(average_similarity, 0.0, 1.0)


def _validate_embeddings(
    source_embeddings: np.ndarray,
    target_embeddings: np.ndarray,
) -> None:
    """
    Validate shape and dimensionality of embedding arrays.
    
    Args:
        source_embeddings: Source sentence embeddings.
        target_embeddings: Target sentence embeddings.
    
    Raises:
        ValueError: If arrays are empty, not 2D, or have mismatched dimensions.
    """
    # Check that arrays are not empty
    if source_embeddings.size == 0:
        raise ValueError(
            "source_embeddings is empty. Need at least one source sentence."
        )
    if target_embeddings.size == 0:
        raise ValueError(
            "target_embeddings is empty. Need at least one target sentence."
        )
    
    # Check that arrays are 2D
    if source_embeddings.ndim != 2:
        raise ValueError(
            f"source_embeddings must be 2D array, got shape {source_embeddings.shape}"
        )
    if target_embeddings.ndim != 2:
        raise ValueError(
            f"target_embeddings must be 2D array, got shape {target_embeddings.shape}"
        )
    
    # Check that embedding dimensions match
    source_dim = source_embeddings.shape[1]
    target_dim = target_embeddings.shape[1]
    
    if source_dim != target_dim:
        raise ValueError(
            f"Embedding dimension mismatch: source has {source_dim} dimensions, "
            f"target has {target_dim} dimensions. Both must use same embedding model."
        )