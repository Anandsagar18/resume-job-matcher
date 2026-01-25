# test_ml_pipeline.py
from ml.pipeline import analyze_resume_job_fit

resume_text = """
Machine Learning Engineer with experience in Python, PyTorch,
NLP, REST APIs, and data analysis. Built ML models for forecasting.
"""

job_description = """
Looking for an ML Engineer with strong Python skills, experience in NLP,
deep learning, FastAPI, and model deployment.
"""

result = analyze_resume_job_fit(resume_text, job_description)

for k, v in result.items():
    print(f"{k}: {v}")
