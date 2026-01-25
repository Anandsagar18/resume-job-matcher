"""
Centralized ML configuration for resume-job matching pipeline.

This module contains all tunable parameters for the scoring algorithm.
Keeping these centralized makes experimentation safer and changes explicit.
All modifications to scoring behavior should happen here, not scattered
across implementation files.
"""

# =============================================================================
# Scoring Weights
# =============================================================================
# These weights define how different signals contribute to the final fit score.
# Must sum to 1.0 for interpretability.
# 
# Current philosophy:
# - Semantic similarity is the primary signal (60%) - measures conceptual alignment
# - Skills are secondary (30%) - hard requirements matter but context varies
# - Experience is tertiary (10%) - provides signal but years alone don't tell full story

SEMANTIC_SIMILARITY_WEIGHT: float = 0.6  # Weight for sentence embedding similarity
SKILL_MATCH_WEIGHT: float = 0.3          # Weight for keyword skill overlap
EXPERIENCE_MATCH_WEIGHT: float = 0.1     # Weight for years of experience alignment


# =============================================================================
# Skill Vocabulary
# =============================================================================
# Curated set of technical skills for keyword-based extraction.
# 
# Design decisions:
# - Lowercase only (normalization happens in skill_extractor.py)
# - Multi-word phrases supported (e.g., "machine learning")
# - Focuses on high-signal technical terms
# - Intentionally small to avoid false positives from common words
#
# To expand: Add new skills here and they'll automatically be detected.
# To test: Ensure new terms don't overlap with common English words.

RECOGNIZED_SKILLS = {

    # =========================
    # Programming Languages
    # =========================
    "python", "java", "c++", "c", "javascript", "typescript",
    "go", "golang", "rust", "scala", "kotlin", "bash",
    "sql", "r", "matlab",

    # =========================
    # ML / AI Core
    # =========================
    "machine learning", "deep learning", "artificial intelligence",
    "supervised learning", "unsupervised learning",
    "reinforcement learning",

    "nlp", "natural language processing",
    "computer vision", "cv",
    "speech recognition", "text classification",
    "information retrieval", "recommendation systems",

    # =========================
    # ML Frameworks & Libraries
    # =========================
    "pytorch", "tensorflow", "keras", "scikit-learn",
    "xgboost", "lightgbm", "catboost",
    "huggingface", "transformers",
    "opencv", "spacy", "nltk",
    "pandas", "numpy", "scipy",

    # =========================
    # Data & Analytics
    # =========================
    "data analysis", "data science", "data engineering",
    "feature engineering", "data preprocessing",
    "data visualization",
    "power bi", "tableau",

    # =========================
    # Backend & APIs
    # =========================
    "fastapi", "django", "flask",
    "node.js", "express",
    "rest api", "graphql",
    "microservices",

    # =========================
    # Databases & Storage
    # =========================
    "mysql", "postgresql", "sqlite",
    "mongodb", "redis", "elasticsearch",
    "cassandra", "dynamodb",

    # =========================
    # DevOps / MLOps / Cloud
    # =========================
    "docker", "kubernetes", "helm",
    "ci/cd", "github actions",
    "mlops", "model deployment",
    "model monitoring",

    "aws", "gcp", "azure",
    "ec2", "s3", "lambda",
    "cloud functions",

    # =========================
    # Systems & CS Fundamentals
    # =========================
    "data structures", "algorithms",
    "operating systems", "computer networks",
    "dbms", "system design",
    "distributed systems",
    "parallel computing",

    # =========================
    # Software Engineering
    # =========================
    "object oriented programming", "oop",
    "design patterns", "clean architecture",
    "unit testing", "integration testing",
    "debugging", "performance optimization",

    # =========================
    # Tools & Platforms
    # =========================
    "git", "github", "gitlab",
    "linux", "unix",
    "jira", "confluence",
    "docker compose",

    # =========================
    # Research & Advanced Topics
    # =========================
    "transformer models", "llms",
    "attention mechanism",
    "bert", "gpt",
    "time series forecasting",
    "anomaly detection",
}

SKILL_PHRASES = {
    "machine learning",
    "ml",
    "deep learning",
    "neural networks",
    "nlp",
    "natural language processing",
    "computer vision",
    "cv",
    "python",
    "fastapi",
    "rest api",
    "docker",
    "kubernetes",
    "aws",
    "gcp",
    "azure",
}

SKILL_CATEGORIES = {
    "core_ml": {
        "machine learning", "ml", "deep learning",
        "neural networks", "nlp", "computer vision"
    },
    "backend": {
        "python", "fastapi", "django", "flask", "rest api"
    },
    "data": {
        "sql", "mongodb", "pandas", "numpy"
    },
    "devops": {
        "docker", "kubernetes", "aws", "gcp", "azure"
    },
}

CATEGORY_WEIGHTS = {
    "core_ml": 0.4,
    "backend": 0.25,
    "data": 0.2,
    "devops": 0.15,
}



# =============================================================================
# Experience Boundaries
# =============================================================================
# Used for normalizing and validating experience-related scores.
#
# MIN_EXPERIENCE_YEARS: Allows for entry-level candidates (0 years)
# MAX_EXPERIENCE_YEARS: Upper bound for normalization; prevents outliers
#                       from skewing scores (e.g., "40 years experience")

MIN_EXPERIENCE_YEARS: int = 0
MAX_EXPERIENCE_YEARS: int = 20  # Caps experience at 20 years for scoring purposes