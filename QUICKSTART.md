# 🚀 Quick Start Guide

Run the full **Paper Flow AI** stack from zero in minutes.

---

## Prerequisites

| Tool | Version | Install |
|------|---------|---------|
| **Python** | 3.11+ | [python.org](https://python.org) |
| **Node.js** | 20+ | [nodejs.org](https://nodejs.org) |
| **Docker** | 24+ | [docker.com](https://docker.com) |
| **Git** | any | [git-scm.com](https://git-scm.com) |

---

## Option A: Docker (Recommended)

One command to run everything:

```bash
# 1. Clone
git clone https://github.com/Abdelhady-22/Paper_Flow.ai.git
cd Paper_Flow.ai

# 2. Create .env from template
cp .env.example .env
# Edit .env with your API keys (LLM, OCR, etc.)

# 3. For Docker, update hostnames
cp .env.docker .env
# Edit .env with your API keys

# 4. Start everything
docker-compose up --build -d

# 5. Run database migrations
docker-compose exec gateway alembic upgrade head
```

**Access:**
- Frontend: [http://localhost:3000](http://localhost:3000)
- Backend API: [http://localhost:8000](http://localhost:8000)
- API Docs: [http://localhost:8000/docs](http://localhost:8000/docs)
- Health Check: [http://localhost:8000/health](http://localhost:8000/health)

---

## Option B: Local Development

### Step 1 — Start Infrastructure

```bash
# Start only PostgreSQL, Qdrant, Redis
docker-compose up postgres qdrant redis -d
```

### Step 2 — Backend

```bash
# Create virtual environment
cd backend
python -m venv .venv

# Activate (Windows)
.venv\Scripts\activate
# Activate (macOS/Linux)
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env in project root
cd ..
cp .env.example .env
# Edit .env — set DATABASE_URL, REDIS_URL, QDRANT_HOST, API keys

# Run migrations
cd backend
alembic upgrade head

# Start the server
uvicorn gateway.main:app --reload --host 0.0.0.0 --port 8000
```

Backend runs at [http://localhost:8000](http://localhost:8000)

### Step 3 — Frontend

```bash
# In a new terminal
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev
```

Frontend runs at [http://localhost:5173](http://localhost:5173)

---

## Environment Variables

Create `.env` in the project root. Key variables:

```env
# ── Database ──────────────────────────────────────
DATABASE_URL=postgresql+asyncpg://admin:securepassword@localhost:5432/research_assistant
POSTGRES_USER=admin
POSTGRES_PASSWORD=securepassword
POSTGRES_DB=research_assistant

# ── Qdrant ────────────────────────────────────────
QDRANT_HOST=localhost
QDRANT_PORT=6333

# ── Redis ─────────────────────────────────────────
REDIS_URL=redis://localhost:6379

# ── LLM Provider (pick one or more) ──────────────
LLM_PROVIDER=groq
GROQ_API_KEY=gsk_...
# OPENAI_API_KEY=sk-...
# GEMINI_API_KEY=AI...
# ANTHROPIC_API_KEY=sk-ant-...

# ── NLP Processing Modes ─────────────────────────
SUMMARIZATION_MODE=model     # "model" (local) or "llm" (cloud)
QA_MODE=model
TRANSLATION_EN_AR_MODE=model
TRANSLATION_AR_EN_MODE=model

# ── OCR ───────────────────────────────────────────
OCR_ENGINE=paddle            # paddle | mistral | lighton
# MISTRAL_API_KEY=
# LIGHTON_API_KEY=

# ── Voice ─────────────────────────────────────────
STT_PROVIDER=whisper         # whisper | elevenlabs | gemini
TTS_PROVIDER=edge_tts        # edge_tts | elevenlabs | gemini | speecht5

# ── App ───────────────────────────────────────────
DEBUG=true
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

> **Note:** For Docker, change hostnames from `localhost` to service names:
> `localhost` → `postgres`, `redis`, `qdrant`

---

## Project Structure

```
Paper_Flow.ai/
├── backend/
│   ├── gateway/              # FastAPI app, routing, middleware
│   ├── services/
│   │   ├── ocr_service/      # PDF/image text extraction
│   │   ├── summarization_service/
│   │   ├── translation_service/
│   │   ├── qa_service/
│   │   ├── chatbot_service/  # RAG-powered chat
│   │   ├── voice_service/    # STT + TTS
│   │   ├── export_service/   # TXT, DOCX, PDF export
│   │   └── agent_service/    # CrewAI paper discovery
│   ├── shared/               # Logger, error handler, LLM client, etc.
│   ├── infrastructure/       # PostgreSQL, Qdrant, Redis clients
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── pages/            # Welcome, Dashboard, Chat, Research, Summarize, Translate, OCR, Q&A, Discover
│   │   ├── components/       # Navbar, Footer, PageTransition
│   │   ├── context/          # ThemeContext (dark/light toggle)
│   │   ├── store/            # Redux Toolkit slices
│   │   ├── api/              # Axios client
│   │   └── utils/            # Motion variants, file validator
│   └── package.json
├── Dockerfile                # Backend
├── Dockerfile.frontend       # Frontend (multi-stage Nginx)
├── docker-compose.yml
├── .github/workflows/ci-cd.yml
└── .env.example
```

---

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/api/v1/ocr/upload` | POST | Upload + OCR a paper |
| `/api/v1/ocr/papers` | GET | List uploaded papers |
| `/api/v1/chat/sessions` | POST/GET | Create/list chat sessions |
| `/api/v1/chat/message` | POST | Send message (RAG chat) |
| `/api/v1/summarize/` | POST | Summarize a paper |
| `/api/v1/translate/` | POST | Translate a paper |
| `/api/v1/qa/generate` | POST | Generate Q&A pairs |
| `/api/v1/voice/stt` | POST | Speech-to-text |
| `/api/v1/voice/tts` | POST | Text-to-speech |
| `/api/v1/export/` | POST | Export to TXT/DOCX/PDF |
| `/api/v1/agent/search` | POST | Search Semantic Scholar |
| `/api/v1/agent/discover` | POST | Full AI discovery pipeline |
| `/ws/progress` | WS | Real-time task progress |

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| DB connection error | Check `DATABASE_URL` and that PostgreSQL is running |
| Redis connection error | Check `REDIS_URL` and that Redis is running |
| Qdrant connection error | Check `QDRANT_HOST:QDRANT_PORT` and that Qdrant is running |
| LLM errors | Verify API key for your chosen `LLM_PROVIDER` |
| OCR slow/failing | Switch `OCR_ENGINE` to `paddle` for local processing |
| Frontend proxy error | Backend must be running on port 8000 |
| Migration error | Run `alembic upgrade head` from the `backend/` directory |
