# Paper Flow AI — Clean PC Setup Guide

> **Only needs: Docker Desktop + Git + OpenAI API Key**
> No Python, Node.js, PostgreSQL, or any other software needed.

---

## What You Need

| Requirement | Why |
|---|---|
| **Docker Desktop** | Runs everything in containers |
| **Git** | Clone the repo |
| **OpenAI API Key** | Powers chat, summarization, translation, Q&A, agent |
| **~10 GB free disk** | Docker images + volumes |

---

## Setup (5 minutes)

### 1. Install Docker Desktop (if not installed)
Download from [docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop/) → Install → **Start it** → Wait for "Engine running" in the bottom-left corner.

### 2. Clone the Repository
```powershell
git clone https://github.com/Abdelhady-22/Paper_Flow.ai.git
cd Paper_Flow.ai
```

### 3. Create Your `.env` File
```powershell
copy .env.local-openai .env
```

### 4. Paste Your OpenAI Key
Open `.env` in any editor and replace the placeholder on line 28:
```
OPENAI_API_KEY=sk-paste-your-real-key-here
```
Save and close.

### 5. Build & Run
```powershell
docker compose up --build -d
```

> [!NOTE]
> First build takes **10–15 minutes** (downloads Python packages, ML models, Node modules).
> After that, starting/stopping takes seconds.

### 6. Open the App
Wait ~2 minutes for all containers to become healthy, then:

| URL | What |
|---|---|
| **http://localhost:3000** | 🎨 Main App (upload PDFs, chat, summarize, etc.) |
| **http://localhost:8000/docs** | 📚 API Documentation (Swagger) |

---

## What's Running (5 Containers)

```
┌─────────────┐     ┌──────────────┐
│   Browser    │────▶│   Frontend   │ :3000  (Nginx + React)
└─────────────┘     └──────┬───────┘
                           │ /api/*
                           ▼
                    ┌──────────────┐
                    │   Gateway    │ :8000  (FastAPI, 8 services)
                    └──┬───┬───┬──┘
              ┌────────┘   │   └────────┐
              ▼            ▼            ▼
        ┌──────────┐ ┌──────────┐ ┌──────────┐
        │PostgreSQL│ │  Qdrant  │ │  Redis   │
        │  :5432   │ │  :6333   │ │  :6379   │
        └──────────┘ └──────────┘ └──────────┘
```

| Container | Purpose | Needs Internet? |
|---|---|---|
| **gateway** | FastAPI backend (all 8 AI services) | Yes (OpenAI API calls) |
| **frontend** | React UI served by Nginx | No |
| **postgres** | User data, papers, results | No |
| **qdrant** | Vector embeddings for RAG chatbot | No |
| **redis** | Caching + real-time progress | No |

---

## Test All 8 Services

| # | Feature | How to Test | What Happens |
|---|---|---|---|
| 1 | **Upload PDF** | Click Upload → pick a PDF | Stored in PostgreSQL |
| 2 | **OCR** | Automatic after upload | PaddleOCR extracts text (local, free) |
| 3 | **Chat** | Open Chat → ask a question | OpenAI GPT-4o-mini answers via RAG |
| 4 | **Summarize** | Click Summarize | OpenAI generates structured summary |
| 5 | **Translate** | Click Translate (EN↔AR) | OpenAI translates the paper |
| 6 | **Q&A** | Click Generate Q&A | OpenAI creates question-answer pairs |
| 7 | **Listen (TTS)** | Click 🔊 on any text | Edge TTS reads aloud (free, no key) |
| 8 | **Discover Papers** | Search a topic | Agent searches Semantic Scholar via OpenAI |

---

## What It Costs

| Service | Model Used | Cost per Request |
|---|---|---|
| Chat | `gpt-4o-mini` | ~$0.001–0.003 |
| Summarize | `gpt-4o-mini` | ~$0.002–0.005 |
| Translate | `gpt-4o-mini` | ~$0.002–0.005 |
| Q&A | `gpt-4o-mini` | ~$0.002–0.005 |
| Agent | `gpt-4o-mini` | ~$0.001 |
| OCR | PaddleOCR (local) | **Free** |
| TTS | Edge TTS (cloud) | **Free** |
| STT | Whisper (local) | **Free** |

> A full test session (upload → chat → summarize → translate → Q&A) ≈ **$0.02–0.05**

---

## Useful Commands

```powershell
# Check if all containers are running
docker compose ps

# Watch live logs
docker compose logs -f

# Logs for just the backend
docker compose logs gateway -f

# Restart backend after changes
docker compose restart gateway

# Stop everything (keeps data)
docker compose down

# Full reset (deletes all data)
docker compose down -v

# Rebuild after code changes
docker compose up --build -d

# Free disk space
docker system prune -a
```

---

## Troubleshooting

| Problem | Fix |
|---|---|
| "Cannot connect to Docker daemon" | Start Docker Desktop, wait for "Engine running" |
| Gateway keeps restarting | Run `docker compose logs gateway --tail 50` to see the error |
| "OPENAI_API_KEY not set" | Check `.env` has your real key (no quotes around the value) |
| Port 3000/8000 in use | `netstat -ano \| findstr :3000` → `taskkill /PID <PID> /F` |
| Build fails (disk full) | `docker system prune -a` then retry |
| Slow first start | Normal — ML models download on first run (~2-3 min) |
| Frontend shows blank page | Wait 1-2 min for gateway to finish starting |

---

## Files in the Repo

| File | Purpose |
|---|---|
| `.env.local-openai` | Template for local dev with OpenAI (copy to `.env`) |
| `.env.codespaces` | Template for GitHub Codespaces (5 Groq keys) |
| `.env.example` | Template with all providers documented |
| `.env.docker` | Template for generic Docker deployment |
| `docker-compose.yml` | Defines all 5 containers |
| `Dockerfile` | Backend container (Python 3.11) |
| `Dockerfile.frontend` | Frontend container (Node → Nginx) |
