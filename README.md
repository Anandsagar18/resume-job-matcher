# 🧠 AI Resume–Job Fit Scorer

> **Production-ready ML application for intelligent resume evaluation**  
> Live at [ai-resume.anandsagargaikwad.in](https://ai-resume.anandsagargaikwad.in/)

An end-to-end machine learning system that evaluates how well a candidate's resume matches a job description using semantic similarity, skill extraction, and experience alignment—without relying on LLMs.

[![Live Demo](https://img.shields.io/badge/demo-live-success)](https://ai-resume.anandsagargaikwad.in/)
[![Backend](https://img.shields.io/badge/backend-FastAPI-009688)](https://api.anandsagargaikwad.in/docs)
[![Frontend](https://img.shields.io/badge/frontend-React-61DAFB)](https://ai-resume.anandsagargaikwad.in/)

---

## 🎯 What It Does

Upload a resume (PDF) and paste a job description to receive:

- **Overall fit score** (0-100) based on weighted ML signals
- **Semantic similarity analysis** using sentence embeddings
- **Matched skills** vs. missing skills breakdown
- **Experience alignment score** comparing candidate years to requirements
- **Human-readable explanation** for transparency

**Use cases:**
- Recruiters pre-screening candidates at scale
- Job seekers validating resume-job alignment before applying
- Career coaches providing data-driven feedback

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                         Frontend                            │
│                    (React + Vite)                           │
│                  Hosted on Vercel                           │
└────────────────────┬────────────────────────────────────────┘
                     │ HTTPS
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                    Backend API                              │
│                  (FastAPI + ML)                             │
│          Dockerized on DigitalOcean                         │
│        Nginx reverse proxy + Let's Encrypt                  │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                    ML Pipeline                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │ PDF Parser   │→ │  Embeddings  │→ │   Scoring    │       │
│  │  (PyPDF2)    │  │ (SentenceTr) │  │  (Weighted)  │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
│                                                             │
│  ┌──────────────┐  ┌──────────────┐                         │
│  │Skill Extract │→ │  Experience  │                         │
│  │  (Keywords)  │  │   (Regex)    │                         │
│  └──────────────┘  └──────────────┘                         │
└─────────────────────────────────────────────────────────────┘
```

**Key architectural decisions:**
- **Separation of concerns**: Frontend and backend deployed independently for flexibility
- **Stateless API**: Backend is horizontally scalable
- **Production-grade infrastructure**: Containerized deployment with HTTPS and reverse proxy

---

## 🛠️ Tech Stack

### Frontend
- **Framework**: React 18
- **Build tool**: Vite
- **Styling**: Tailwind CSS
- **HTTP client**: Axios
- **Hosting**: Vercel (auto-deploy from Git)

### Backend
- **Framework**: FastAPI (Python 3.10)
- **ML libraries**:
  - `sentence-transformers` (semantic embeddings)
  - `scikit-learn` (cosine similarity)
  - `PyTorch` (embedding model inference)
  - `PyPDF2` (resume text extraction)
- **Server**: Uvicorn (ASGI)
- **Containerization**: Docker
- **Hosting**: DigitalOcean Droplet (Ubuntu)
- **Reverse proxy**: Nginx with Let's Encrypt SSL

---

## 🧠 ML Logic (High Level)

The system combines three orthogonal signals to compute a final fit score:

### 1. Semantic Similarity (60% weight)
- Converts resume and job description into sentence embeddings using `all-MiniLM-L6-v2` transformer model
- Computes **average-max cosine similarity**: for each JD requirement, finds the best-matching resume sentence
- Captures conceptual alignment beyond keyword matching

### 2. Skill Matching (30% weight)
- Deterministic keyword extraction from a curated vocabulary (350+ technical skills)
- Returns:
  - **Matched skills**: Present in both resume and JD
  - **Missing skills**: Required by JD but absent from resume
- Transparent and auditable

### 3. Experience Alignment (10% weight)
- Regex-based extraction of "X years of experience" from both documents
- Computes ratio score (capped at 1.0)
- Handles edge cases (no requirement → perfect score)

**Final score formula:**
```python
fit_score = (0.6 × semantic_similarity) + (0.3 × skill_match) + (0.1 × experience_score)
```

**Design philosophy:**
- ✅ Explainable: Every component is interpretable
- ✅ No black-box LLMs: Deterministic and reproducible
- ✅ Production-oriented: Similar to real ATS systems

---

## 🚀 Deployment Strategy

### Backend Deployment (DigitalOcean)

1. **Dockerization**:
   - Application containerized with multi-stage build for optimized size
   - `requirements.txt` cached for faster rebuilds

2. **Server setup**:
   - Ubuntu 24 droplet running Docker
   - Nginx configured as reverse proxy
   - SSL certificate from Let's Encrypt (auto-renewal via certbot)

3. **CI/CD**:
   - Manual deployment: SSH into droplet, pull latest code, rebuild container
   - Nginx handles traffic routing and HTTPS termination

**Backend URL**: `https://api.anandsagargaikwad.in`

### Frontend Deployment (Vercel)

1. **Auto-deploy**:
   - Connected to GitHub repository
   - Automatic builds on push to `main` branch

2. **Environment config**:
   - API base URL configured to point to production backend
   - Build optimizations enabled (Vite bundler)

**Frontend URL**: `https://ai-resume.anandsagargaikwad.in`

---

## 💻 Local Development Setup

### Prerequisites
- Python 3.10+
- Node.js 18+
- Docker (optional, for backend)

### Backend (Option 1: Python)

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Backend runs at**: `http://localhost:8000`  
**Swagger docs**: `http://localhost:8000/docs`

### Backend (Option 2: Docker)

```bash
cd backend
docker build -t resume-job-matcher-backend .
docker run -p 8000:8080 resume-job-matcher-backend
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

**Frontend runs at**: `http://localhost:3000`

**Note**: Update `API_BASE_URL` in `frontend/src/services/api.js` to `http://localhost:8000` for local backend connection.

---

## 📚 API Documentation

### Interactive Docs
- **Swagger UI**: `https://api.anandsagargaikwad.in/docs`
- **ReDoc**: `https://api.anandsagargaikwad.in/redoc`

### Key Endpoints

#### `POST /evaluate`
Evaluate resume-job fit.

**Request**:
- `resume` (file): PDF file
- `job_description` (form field): Plain text

**Response** (200 OK):
```json
{
  "fit_score": 78.5,
  "semantic_similarity_score": 0.82,
  "matched_skills": ["python", "docker", "fastapi"],
  "missing_skills": ["kubernetes"],
  "experience_match_score": 0.75,
  "explanation": "Semantic match score is 0.82. Matched 3 required skills..."
}
```

**Error responses**:
- `400`: Invalid PDF, empty job description, or empty PDF
- `422`: PDF extraction failed
- `500`: Internal server error

#### `GET /health`
Health check endpoint.

**Response**:
```json
{
  "status": "healthy",
  "ml_model_loaded": true
}
```

---

## 🔮 Future Improvements

### v2.0 Roadmap
- [ ] **Expanded skill taxonomy**: Add synonyms and fuzzy matching (e.g., "React.js" ↔ "React")
- [ ] **Skill importance weighting**: Distinguish must-have vs. good-to-have skills
- [ ] **Improved experience extraction**: Handle non-standard phrasings ("half a decade")
- [ ] **Embedding caching**: Store precomputed JD embeddings for faster repeated evaluations
- [ ] **Confidence calibration**: Add uncertainty estimates to scores
- [ ] **User authentication**: Save evaluation history
- [ ] **Batch processing**: Upload multiple resumes for comparative analysis
- [ ] **Fine-tuned embeddings**: Domain-specific model for tech recruitment

### Infrastructure
- [ ] CI/CD pipeline with GitHub Actions
- [ ] Horizontal scaling with load balancer
- [ ] Rate limiting and API authentication
- [ ] Monitoring and observability (Prometheus + Grafana)

---

## 👤 Author

**Anandsagar Gaikwad**  
B.Tech Computer Science & Engineering | ML & Backend

This is a production-ready ML project demonstrating:
- End-to-end system design from ML pipeline to deployment
- Real-world infrastructure (Docker, Nginx, HTTPS, cloud hosting)
- Clean, maintainable, and interview-ready codebase

🔗 **GitHub**: [github.com/Anandsagar18](https://github.com/Anandsagar18)  
🌐 **Live Demo**: [ai-resume.anandsagargaikwad.in](https://ai-resume.anandsagargaikwad.in/)

---

## 📝 License

MIT License

---

## 🙏 Acknowledgments

- **HuggingFace** for pretrained sentence transformer models
- **FastAPI** community for excellent async framework
- **Tailwind CSS** for utility-first styling

---

**⭐ If you find this project useful, consider giving it a star!**
