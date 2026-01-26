# ---- Base image ----
FROM python:3.10-slim

# ---- Environment settings ----
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# ---- System dependencies ----
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# ---- Working directory ----
WORKDIR /app

# ---- Install Python deps first (better caching) ----
COPY requirements.txt .

RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# ---- Copy application code ----
COPY . .

# ---- Expose port (Railway uses 8080 internally) ----
EXPOSE 8080

# ---- Start FastAPI ----
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
