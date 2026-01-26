
---

# 🧠 AI Resume–Job Matcher (v1.0)

An end-to-end **ML-powered resume–job fit analyzer** that evaluates how well a candidate’s resume matches a job description using **semantic similarity, skill overlap, and experience alignment** — without using LLMs.

> **Status:** v1.0 (Prototype)
> **Next planned:** v2.0 with improved skill taxonomy & scoring logic

---

## 🚀 Features

* 📄 Upload **resume (PDF)**
* 📝 Paste **job description text**
* 🧠 ML-based semantic matching using **Sentence Transformers**
* 🛠️ Explicit **skill matching** with explainability
* 📊 Weighted final **fit score (0–100)**
* 🌐 Full-stack app (FastAPI + React)

---

## 🏗️ Architecture Overview

```
resume-job-matcher/
├── backend/
│   ├── app/              # FastAPI backend
│   │   ├── main.py
│   │   └── services/
│   ├── ml/               # ML pipeline (core logic)
│   │   ├── embeddings.py
│   │   ├── similarity.py
│   │   ├── skill_extractor.py
│   │   ├── scorer.py
│   │   └── pipeline.py
│   └── requirements.txt
│
├── frontend/
│   ├── src/              # React + Vite frontend
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
│
└── README.md
```

---

## 🧠 ML Approach (No LLMs)

The system combines **three orthogonal signals**:

### 1️⃣ Semantic Similarity (60%)

* Sentence-level embeddings using:

  ```
  all-MiniLM-L6-v2
  ```
* Average-max cosine similarity:

  * “Does the resume cover each JD requirement?”

### 2️⃣ Skill Matching (30%)

* Deterministic keyword-based extraction
* Transparent:

  * matched skills
  * missing skills
* Easy to audit & debug

### 3️⃣ Experience Alignment (10%)

* Regex-based extraction of years
* Ratio-based scoring (capped at 1.0)

> This hybrid approach balances **accuracy + explainability**, similar to real production ATS systems.

---

## 📤 API Output Example

```json
{
  "fit_score": 67.93,
  "semantic_similarity_score": 0.716,
  "matched_skills": ["python", "nlp"],
  "missing_skills": ["deep learning", "fastapi"],
  "experience_match_score": 1.0,
  "explanation": "Semantic match score is 0.72. Matched 2 required skills. Experience alignment score is 1.00. Missing skills include: deep learning, fastapi."
}
```

---

## 🖥️ Tech Stack

### Backend

* **FastAPI**
* **Sentence-Transformers**
* **PyTorch**
* **NumPy**
* **Uvicorn**

### Frontend

* **React**
* **Vite**
* **Tailwind CSS**

---

## ▶️ Running Locally

### Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Backend runs at:

```
http://127.0.0.1:8000
```

Swagger docs:

```
http://127.0.0.1:8000/docs
```

---

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at:

```
http://localhost:3000
```

---

## 🎯 Design Goals

* ❌ No black-box LLMs
* ✅ Explainable scoring
* ✅ Interview-ready architecture
* ✅ Production-oriented ML pipeline
* ✅ Easy to extend in future versions

---

## 🔮 Planned Improvements (v2.0)

* Expanded skill taxonomy with synonyms
* Skill importance weighting (must-have vs good-to-have)
* Better experience extraction
* Caching for embeddings
* Confidence calibration on scores

---

## 👤 Author

**Anandsagar Gaikwad**
B.Tech CSE | ML & Backend Engineering
🔗 GitHub: [https://github.com/Anandsagar18](https://github.com/Anandsagar18)

---

## 📝 License

MIT License

---

