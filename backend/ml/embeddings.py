"""
Sentence embedding generation for semantic text matching.

This module provides a thin wrapper around a pretrained sentence transformer model.
Embeddings enable semantic similarity computation beyond keyword matching - they
capture meaning and context, allowing us to match conceptually similar phrases
even when exact words differ.

Key design decisions:
- Uses pretrained embeddings only (no fine-tuning for simplicity and speed)
- Normalizes embeddings to enable cosine similarity via dot product
- Model choice (all-MiniLM-L6-v2) balances quality and inference speed
- Stateless operations: no training, no state updates, deterministic outputs

Why embeddings?
- "5 years of Python development" semantically matches "extensive Python experience"
- Captures domain knowledge without explicit keyword lists
- Generalizes to unseen phrasings in job descriptions and resumes
"""

from typing import List

import numpy as np
from sentence_transformers import SentenceTransformer


class EmbeddingModel:
    """
    Wrapper for generating sentence embeddings using a pretrained transformer.
    
    This class encapsulates the sentence transformer model and provides a
    consistent interface for encoding text into dense vector representations.
    
    The model is loaded once during initialization and reused across all
    encoding calls, making this suitable for processing multiple resume-job
    pairs efficiently.
    
    Attributes:
        model: Pretrained SentenceTransformer instance for encoding text.
        model_name: Identifier of the model being used.
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2") -> None:
        """
        Initialize the embedding model.
        
        Args:
            model_name: HuggingFace model identifier. Default is a lightweight,
                       balanced model (384 dimensions, ~80MB) suitable for
                       production deployment. Alternative options:
                       - "all-mpnet-base-v2" (higher quality, slower)
                       - "paraphrase-MiniLM-L3-v2" (faster, lower quality)
        
        Note:
            First run will download the model from HuggingFace (~80MB for default).
            Subsequent runs load from local cache.
        """
        self.model_name = model_name
        self.model = SentenceTransformer(model_name)

    def encode(self, texts: List[str]) -> np.ndarray:
        """
        Generate normalized embeddings for a batch of text inputs.
        
        Each text string is encoded into a dense vector representation that
        captures its semantic meaning. Vectors are L2-normalized so that
        cosine similarity can be computed via simple dot products.
        
        Args:
            texts: List of text strings to encode. Typically sentences from
                  resumes or job descriptions. Empty strings are supported
                  but will produce low-quality embeddings.
        
        Returns:
            NumPy array of shape (len(texts), embedding_dim) containing
            L2-normalized embedding vectors. Each row corresponds to one
            input text in the same order.
            
            For the default model, embedding_dim = 384.
        
        Example:
            >>> embedder = EmbeddingModel()
            >>> texts = ["Python developer", "Software engineer"]
            >>> embeddings = embedder.encode(texts)
            >>> embeddings.shape
            (2, 384)
        
        Note:
            - Normalization enables cosine_similarity(A, B) == dot(A, B)
            - Batch encoding is more efficient than encoding texts individually
            - Model is pretrained; no gradients are computed
        """
        return self.model.encode(
            texts,
            normalize_embeddings=True,  # L2 normalization for cosine similarity
            show_progress_bar=False,    # Suppress progress bar for cleaner logs
        )