# Research Paper Assistant

An intelligent web application designed to help anyone engage deeply with academic and scientific literature — whether you're a student, researcher, professional, or simply a curious reader.

## 🌟 Core Features

- **Paper Ingestion**: Upload PDFs/DOCX or discover papers via AI-powered search
- **Conversational Chat**: RAG-powered Q&A with citations from actual paper content
- **NLP Tools**: Summarization, Q&A Generation, Translation (EN↔AR), OCR
- **Voice Interaction**: Speech-to-Text and Text-to-Speech (multilingual)
- **Export System**: Download results as TXT, DOCX, or PDF
- **AI Agent Discovery**: CrewAI-powered automatic paper discovery via Semantic Scholar

## 🏗️ Architecture

Microservices architecture with 8 backend services + API Gateway:

| Service | Purpose |
|---|---|
| **Gateway** | API routing, rate limiting, CORS, WebSocket |
| **Chatbot** | RAG-powered conversational Q&A |
| **Summarization** | Paper summarization (Model/LLM modes) |
| **Translation** | Arabic ↔ English translation |
| **OCR** | Text extraction from scanned documents |
| **Q&A** | Question-Answer generation |
| **Voice** | STT/TTS with multiple providers |
| **Agent** | AI-powered paper discovery |
| **Export** | TXT/DOCX/PDF generation |

## 🛠️ Tech Stack

- **Backend**: FastAPI, SQLAlchemy (async), LangChain, CrewAI, LiteLLM
- **Frontend**: React, TypeScript, Tailwind CSS, Redux Toolkit
- **Databases**: PostgreSQL 16, Qdrant (vectors), Redis 7 (cache)
- **ML Models**: sentence-transformers, DistilBART, T5, MarianNMT, Whisper
- **Deployment**: Docker, Docker Compose, GitHub Actions CI/CD

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.11+
- Node.js 20+

### Setup

```bash
# 1. Clone the repository
git clone <repo-url>
cd Paper_Flow.ai

# 2. Copy environment config
cp .env.example .env
# Edit .env with your API keys

# 3. Start infrastructure
docker-compose up -d

# 4. Install backend dependencies
cd backend
pip install -r requirements.txt

# 5. Run database migrations
alembic upgrade head

# 6. Start the gateway
cd gateway && uvicorn main:app --reload --port 8000
```

### Docker (Full Stack)
```bash
docker-compose up --build
```

## 📁 Project Structure

```
Paper_Flow.ai/
├── backend/
│   ├── gateway/                     ← API Gateway
│   ├── services/
│   │   ├── chatbot_service/         ← RAG chat
│   │   ├── summarization_service/   ← Summarization
│   │   ├── translation_service/     ← Translation
│   │   ├── ocr_service/             ← OCR
│   │   ├── qa_service/              ← Q&A generation
│   │   ├── voice_service/           ← STT/TTS
│   │   ├── agent_service/           ← CrewAI agents
│   │   └── export_service/          ← File export
│   ├── shared/
│   │   ├── embedding/               ← Text embeddings
│   │   ├── chunking/                ← Text chunking
│   │   ├── llm_client/              ← LiteLLM client
│   │   ├── rate_limiter/            ← Rate limiting
│   │   ├── error_handler/           ← Exception handling
│   │   ├── logger/                  ← Structured logging
│   │   ├── security/                ← File validation
│   │   ├── storage/                 ← Secure file storage
│   │   ├── progress/                ← WebSocket progress
│   │   └── models/                  ← ORM models
│   ├── infrastructure/
│   │   ├── postgres/                ← DB + Alembic
│   │   ├── qdrant/                  ← Vector DB client
│   │   └── redis/                   ← Cache client
│   ├── requirements.txt
│   ├── requirements-dev.txt
│   ├── settings.py
│   └── alembic.ini
├── frontend/                        ← React app (coming soon)
├── docker-compose.yml
├── .env.example
└── .gitignore
```

## 📡 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/v1/ocr/upload` | Upload & process paper |
| `POST` | `/api/v1/ocr/extract` | OCR text extraction |
| `GET` | `/api/v1/ocr/papers` | List user's papers |
| `POST` | `/api/v1/chat/sessions` | Create chat session |
| `POST` | `/api/v1/chat/message` | Send message (RAG) |
| `POST` | `/api/v1/summarize/` | Summarize paper |
| `POST` | `/api/v1/translate/` | Translate paper |
| `POST` | `/api/v1/qa/generate` | Generate Q&A pairs |
| `POST` | `/api/v1/voice/stt` | Speech-to-Text |
| `POST` | `/api/v1/voice/tts` | Text-to-Speech |
| `POST` | `/api/v1/export/` | Export to TXT/DOCX/PDF |
| `POST` | `/api/v1/agent/discover` | AI paper discovery |
| `PATCH` | `/api/v1/chat/messages/{id}/like` | Like message |
| `PATCH` | `/api/v1/chat/messages/{id}/dislike` | Dislike message |
| `WS` | `/ws/progress` | Real-time progress |

## 📄 License

MIT
