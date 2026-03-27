# Paper_Flow.ai — Setup Guide

## Prerequisites

| Tool | Download |
|------|----------|
| Docker Desktop | [docker.com/products/docker-desktop](https://docker.com/products/docker-desktop) |
| Python 3.11 | [python.org](https://python.org) |
| Node.js 20+ | [nodejs.org](https://nodejs.org) |
| Git | [git-scm.com](https://git-scm.com) |

---

## Step-by-Step Installation

### 1. Clone the Repository

```bash
git clone https://github.com/Abdelhady-22/Paper_Flow.ai.git
cd Paper_Flow.ai
```

### 2. Start Infrastructure

Spin up Postgres, Redis, and Qdrant using Docker:

```bash
docker compose up -d
```

### 3. Backend Setup

```bash
cd backend
python -m venv venv
venv\Scripts\activate          # Windows
pip install -r requirements.txt
```

### 4. Configure Environment Variables

```bash
cp .env.example .env
```

> Open `.env` and set your API key:
> ```
> GROQ_API_KEY=your_key_here
> ```

### 5. Start the Backend

```bash
uvicorn gateway.main:app --reload --host 0.0.0.0 --port 8000
```

### 6. Start the Frontend

Open a **new terminal**, then run:

```bash
cd frontend
npm install
npm run dev
```

---

## Access

| Service | URL |
|---------|-----|
| Frontend | http://localhost:5173 |
| Backend API | http://localhost:8000 |
| API Docs | http://localhost:8000/docs |
| Health Check | http://localhost:8000/health |
