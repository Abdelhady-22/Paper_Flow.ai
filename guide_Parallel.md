# Research Paper Assistant — Complete Project Guide

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Core Features](#2-core-features)
3. [Who It's For](#3-whos-it-for)
4. [Tech Stack](#4-tech-stack)
5. [System Architecture](#5-system-architecture)
6. [Layered Architecture](#6-layered-architecture)
7. [Microservices — Application Services](#7-microservices--application-services)
8. [AI Agent Orchestration — CrewAI](#8-ai-agent-orchestration--crewai)
9. [ML Models & LLM Providers](#9-ml-models--llm-providers)
10. [LiteLLM — Unified LLM Interface](#10-litellm--unified-llm-interface)
11. [OCR — Engines & Providers](#11-ocr--engines--providers)
12. [Voice Interaction — STT & TTS](#12-voice-interaction--stt--tts)
13. [Chat UX — Message Actions](#13-chat-ux--message-actions)
14. [Chat & File Storage](#14-chat--file-storage)
15. [Database Migrations — Alembic](#15-database-migrations--alembic)
16. [NLP Services — Model vs LLM Mode](#16-nlp-services--model-vs-llm-mode)
17. [Export System](#17-export-system)
18. [Error Handling & Exception Management](#18-error-handling--exception-management)
19. [Logging & Monitoring](#19-logging--monitoring)
20. [Rate Limiting & Timeouts](#20-rate-limiting--timeouts)
21. [Technical Architecture: Async & Concurrent Processing](#21-technical-architecture-async--concurrent-processing)
22. [Technical Architecture: Batch Processing](#22-technical-architecture-batch-processing)
23. [Combining Concurrency with Batch Processing](#23-combining-concurrency-with-batch-processing)
24. [Smart Caching Layer — Redis](#24-smart-caching-layer--redis)
25. [AI Enhancement: RAG Pipeline](#25-ai-enhancement-rag-pipeline)
26. [AI Enhancement: Vector Database — Qdrant](#26-ai-enhancement-vector-database--qdrant)
27. [Real-Time Progress Tracking — WebSockets](#27-real-time-progress-tracking--websockets)
28. [Recommended Design Patterns](#28-recommended-design-patterns)
29. [Deployment — Docker](#29-deployment--docker)
30. [Feature-to-Technology Mapping](#30-feature-to-technology-mapping)
31. [Information Flow](#31-information-flow)
32. [Implementation Checklist](#32-implementation-checklist)

---

## 1. Project Overview

The **Research Paper Assistant** is an intelligent web application designed to help anyone engage deeply with academic and scientific literature — whether you're a student, researcher, professional, or simply a curious reader. It removes the barriers of complex academic language, making any paper from any field accessible, understandable, and actionable.

### Core Philosophy

- **Accessible**: Complex research made understandable for everyone
- **Efficient**: AI-powered tools that save hours of reading and analysis
- **Scalable**: Built to handle anything from a single paper to an entire research library
- **Multilingual**: Full Arabic–English support including voice interaction
- **Flexible**: Every NLP operation configurable between local ML models or cloud LLMs
- **Reliable**: Comprehensive error handling, logging, rate limiting, and graceful degradation

---

## 2. Core Features

### 2.1 Getting Papers Into the System

**Option A — Direct Upload**
Upload PDFs or Word documents, including scanned or image-based papers. The system handles unreadable scans through multiple OCR engines (PaddleOCR, Mistral OCR API, LightOnOCR).

**Option B — AI-Powered Discovery**
Describe your topic of interest and provide keywords. The CrewAI agent pipeline searches Semantic Scholar, retrieves relevant papers, downloads them, and imports them automatically.

---

### 2.2 Conversational Chat Workspace

- Ask questions about paper content via text or voice
- Responses grounded in actual paper content via RAG
- Every response cited with exact paper section references
- Voice input (STT) and voice output (TTS) with multiple provider options
- Message actions: like, dislike, copy (assistant messages); copy (user messages)
- Multiple chat sessions organized by topic
- All conversations saved to PostgreSQL per user
- Uploaded and collected files stored and linked to each session

---

### 2.3 Specialized NLP Tools

Each tool supports two modes: **Model Mode** (local ML model) or **LLM Mode** (cloud/local LLM via LiteLLM) — configurable per service.

| Tool | Model Mode | LLM Mode | Export |
|---|---|---|---|
| Summarization | DistilBART | Any LiteLLM provider | TXT, DOCX, PDF |
| Q&A Generation | T5-small | Any LiteLLM provider | TXT, DOCX, PDF |
| Translation EN→AR | opus-mt-en-ar | Any LiteLLM provider | TXT, DOCX, PDF |
| Translation AR→EN | opus-mt-ar-en | Any LiteLLM provider | TXT, DOCX, PDF |
| OCR | PaddleOCR / Mistral / LightOn | — | TXT, DOCX, PDF |

---

### 2.4 Voice Interaction

- **STT**: User records voice → transcribed → sent to chatbot
- **TTS**: Chatbot response → spoken audio → played to user
- Multiple providers: Faster Whisper (local), ElevenLabs API, Gemini STT/TTS
- Bilingual: Arabic and English

---

### 2.5 Export System

All tool outputs downloadable as TXT, DOCX, or PDF.

---

## 3. Who It's For

| User Type | Primary Use Case |
|---|---|
| **Students** | Study efficiently, generate Q&A sets, understand complex papers |
| **Academic Researchers** | Analyze literature, compare studies, discover papers |
| **Healthcare Professionals** | Quick reference, evidence review, stay current |
| **Journalists** | Understand and accurately report on complex research topics |
| **Professionals** | Stay informed in their field without spending hours reading |
| **Curious Individuals** | Genuinely understand what a paper says — not just its abstract |

---

## 4. Tech Stack

### 4.1 Frontend

| Category | Technology | Purpose |
|---|---|---|
| **Framework** | React | Component-based UI |
| **Language** | TypeScript | Type-safe application logic |
| **Styling** | Tailwind CSS | Utility-first styling |
| **State Management** | Redux Toolkit | Global state management |
| **HTTP Client** | Axios | REST API communication |
| **WebSocket** | Native WebSocket API | Real-time progress updates |
| **PDF Viewer** | react-pdf | In-browser paper viewing |
| **Audio Recording** | MediaRecorder API | STT voice capture |
| **Audio Playback** | HTML5 Audio API | TTS playback |
| **i18n** | react-i18next | Arabic / English support |
| **Notifications** | react-hot-toast | User-friendly messages |
| **File Download** | file-saver | Client-side file downloads |
| **Icons** | lucide-react | UI icons |

---

### 4.2 Backend

| Category | Technology | Purpose |
|---|---|---|
| **Framework** | FastAPI 0.109 | REST API server |
| **Server** | Uvicorn 0.27 | ASGI server |
| **LLM Orchestration** | LangChain 0.1 | LLM chain management |
| **AI Agents** | CrewAI 0.114 | Multi-agent paper discovery |
| **LLM Management** | LiteLLM | Unified multi-provider LLM interface |
| **Vector Store** | Qdrant | Similarity search for RAG |
| **Embeddings** | sentence-transformers 2.2.2 | 384-dim text embeddings |
| **ASR (STT)** | Faster Whisper, ElevenLabs, Gemini | Speech-to-text |
| **TTS** | Edge-TTS, ElevenLabs, Gemini | Text-to-speech |
| **Transformers** | Transformers 4.36.2 | Summarization, Q&A, NLP |
| **OCR** | PaddleOCR 2.7, Mistral API, LightOnOCR | Document text extraction |
| **Translation** | MarianNMT / NLLB-200 | Arabic–English translation models |
| **PDF Processing** | PyPDF2 3.0, pdfplumber 0.10 | PDF text extraction |
| **DOCX Processing** | python-docx 1.1 | Word document read/write |
| **PDF Export** | fpdf2 / reportlab | PDF generation |
| **Text Processing** | NLTK 3.8, tiktoken 0.5 | Tokenization & chunking |
| **Deep Learning** | PyTorch 2.1.2 | Model backend |
| **Tokenization** | sentencepiece 0.1.99 | Subword tokenization |
| **Validation** | Pydantic 2.5.3 | Request/response models |
| **HTTP Client** | httpx 0.26 | Async HTTP requests |
| **DB ORM** | SQLAlchemy 2.0 (async) | ORM + query builder |
| **DB Migrations** | Alembic | Schema versioning & migrations |
| **Logging** | structlog + loguru | Structured application logging |
| **Rate Limiting** | slowapi + LiteLLM built-in | Request rate control |
| **Config** | python-dotenv 1.0 | Environment management |

---

### 4.3 Databases & Infrastructure

| Category | Technology | Purpose |
|---|---|---|
| **Relational DB** | PostgreSQL 16 | Users, metadata, chat, sessions, files |
| **Vector DB** | Qdrant | Paper chunk embeddings for RAG |
| **Cache + Event Bus** | Redis 7 | Response caching + Pub/Sub events |

---

## 5. System Architecture

```
┌──────────────────────────────────────────────────────────┐
│                    React Frontend                         │
│   Text Chat │ Voice (STT/TTS) │ Upload │ Export │ Actions │
└──────────────────────┬───────────────────────────────────┘
                       │ HTTPS + WebSocket
┌──────────────────────▼───────────────────────────────────┐
│                    API Gateway                            │
│       FastAPI Router — Auth + Routing + Rate Limit        │
└──┬──────┬──────┬──────┬──────┬──────┬──────┬────────────┘
   │      │      │      │      │      │      │
   ▼      ▼      ▼      ▼      ▼      ▼      ▼
Chatbot Summary Trans  OCR   Q&A  Voice  Agent  Export
Service Service Service Serv. Serv. Serv. Service Service
   │      │      │      │      │      │      │      │
   └──────┴──────┴──────┴──────┴──────┴──────┴──────┘
                          │
            ┌─────────────┼──────────────┐
            ▼             ▼              ▼
       PostgreSQL        Qdrant         Redis
    (Users, Chats,    (Vectors &     (Cache &
     Files, Results)   Embeddings)    Pub/Sub)
```

---

## 6. Layered Architecture

Every service follows a consistent **Layered Architecture** — keeping concerns separated, code clean, and logic testable.

### 6.1 Folder Structure Per Service

```
service_name/
│
├── routes/              ← HTTP endpoints (FastAPI APIRouter)
│   └── routes.py
│
├── services/            ← Business logic layer
│   └── service.py
│
├── repository/          ← Database access layer (no raw SQL in services)
│   ├── postgres_repo.py
│   └── qdrant_repo.py
│
├── models/              ← Pydantic schemas, SQLAlchemy ORM models, DTOs
│   ├── domain.py        ← SQLAlchemy ORM models
│   └── schemas.py       ← Pydantic request/response schemas
│
├── utils/               ← Stateless helper functions
│   ├── text_chunker.py
│   ├── embedding_utils.py
│   ├── file_parser.py
│   └── export_utils.py
│
├── exceptions/          ← Service-specific custom exceptions
│   └── exceptions.py
│
├── tests/               ← Unit + integration tests
│   ├── test_routes.py
│   ├── test_services.py
│   └── test_repository.py
│
└── main.py              ← FastAPI app initialization for this service
```

---

### 6.2 Layer Responsibilities

#### Routes Layer
Handles incoming HTTP. Validates with Pydantic. Calls service. Returns response. Zero business logic.

```python
# routes/routes.py
from fastapi import APIRouter, Depends, UploadFile
from services.service import SummarizationService
from models.schemas import SummarizeRequest, SummaryResponse

router = APIRouter(prefix="/summarize", tags=["summarization"])

@router.post("/", response_model=SummaryResponse)
async def summarize_paper(
    request: SummarizeRequest,
    service: SummarizationService = Depends()
) -> SummaryResponse:
    return await service.summarize(request.paper_id, request.mode)
```

#### Services Layer
Business logic only. Decides mode, coordinates repositories, calls AI. No direct DB queries.

```python
# services/service.py
class SummarizationService:
    def __init__(
        self,
        paper_repo: PaperRepository = Depends(),
        cache_repo: CacheRepository = Depends(),
        mode_selector: ModeSelector = Depends()
    ):
        self.paper_repo = paper_repo
        self.cache_repo = cache_repo
        self.mode_selector = mode_selector

    async def summarize(self, paper_id: UUID, mode: str) -> SummaryResult:
        cached = await self.cache_repo.get(f"summary:{paper_id}:{mode}")
        if cached:
            return cached

        text = await self.paper_repo.get_text(paper_id)
        strategy = self.mode_selector.get_strategy("summarization", mode)
        summary = await strategy.run(text)

        await self.cache_repo.set(f"summary:{paper_id}:{mode}", summary, ttl=86400)
        await self.paper_repo.save_result(paper_id, "summary", summary, mode)
        return summary
```

#### Repository Layer
All data access behind abstract interfaces.

```python
# repository/postgres_repo.py
class PostgresPaperRepository(PaperRepository):
    def __init__(self, session: AsyncSession = Depends(get_db)):
        self.session = session

    async def get_text(self, paper_id: UUID) -> str:
        result = await self.session.execute(
            select(Paper).where(Paper.id == paper_id)
        )
        paper = result.scalar_one_or_none()
        if not paper:
            raise PaperNotFoundException(paper_id)
        return paper.extracted_text

    async def save_result(
        self, paper_id: UUID, tool: str, content: str, mode: str
    ) -> ToolResult:
        result = ToolResult(
            paper_id=paper_id, tool_type=tool,
            content=content, mode_used=mode
        )
        self.session.add(result)
        await self.session.commit()
        return result
```

#### Models Layer

```python
# models/domain.py  (SQLAlchemy ORM)
class Paper(Base):
    __tablename__ = "papers"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    filename: Mapped[str]
    file_path: Mapped[str]
    extracted_text: Mapped[Optional[str]]
    source: Mapped[str] = mapped_column(default="upload")
    status: Mapped[str] = mapped_column(default="pending")
    created_at: Mapped[datetime] = mapped_column(default=func.now())

# models/schemas.py  (Pydantic)
class SummarizeRequest(BaseModel):
    paper_id: UUID
    mode: Literal["model", "llm"] = "model"
    language: Literal["en", "ar"] = "en"

class SummaryResponse(BaseModel):
    content: str
    paper_id: UUID
    mode_used: str
    created_at: datetime
```

#### Utils Layer

```python
# utils/text_chunker.py
def chunk_text(
    text: str,
    chunk_size: int = 500,
    overlap: int = 50
) -> List[str]:
    """Split text into overlapping chunks using tiktoken + NLTK."""
    sentences = nltk.sent_tokenize(text)
    chunks, current, current_tokens = [], [], 0
    enc = tiktoken.get_encoding("cl100k_base")
    for sentence in sentences:
        tokens = len(enc.encode(sentence))
        if current_tokens + tokens > chunk_size and current:
            chunks.append(" ".join(current))
            current = current[-overlap:]
            current_tokens = sum(len(enc.encode(s)) for s in current)
        current.append(sentence)
        current_tokens += tokens
    if current:
        chunks.append(" ".join(current))
    return chunks
```

---

## 7. Microservices — Application Services

### 7.1 Project Structure

```
research_paper_assistant/
│
├── gateway/                     ← API Gateway
│
├── services/
│   ├── chatbot_service/         ← RAG chat + message actions
│   ├── summarization_service/   ← Summarization (model or LLM)
│   ├── translation_service/     ← AR↔EN translation (model or LLM)
│   ├── ocr_service/             ← OCR (PaddleOCR / Mistral / LightOn)
│   ├── qa_service/              ← Q&A generation (model or LLM)
│   ├── voice_service/           ← STT + TTS (multi-provider)
│   ├── agent_service/           ← CrewAI paper discovery
│   └── export_service/          ← TXT / DOCX / PDF export
│
├── shared/
│   ├── embedding/               ← sentence-transformers wrapper
│   ├── chunking/                ← text chunker (tiktoken + NLTK)
│   ├── llm_client/              ← LiteLLM unified client
│   ├── rate_limiter/            ← Rate limit + timeout middleware
│   ├── error_handler/           ← Global exception handlers
│   └── logger/                  ← Structured logging setup
│
├── infrastructure/
│   ├── postgres/
│   │   ├── database.py          ← Async SQLAlchemy engine + session
│   │   └── migrations/          ← Alembic migrations folder
│   ├── qdrant/
│   │   └── client.py
│   └── redis/
│       └── client.py
│
└── alembic.ini                  ← Alembic configuration
```

---

### 7.2 Chatbot Service

Receives user questions (text or voice transcript). Runs RAG pipeline. Returns cited grounded responses. Saves every message turn to PostgreSQL. Handles message actions (like, dislike, copy).

```
chatbot_service/
├── routes/      chat_routes.py, action_routes.py
├── services/    chat_service.py, rag_service.py, action_service.py
├── repository/  qdrant_repo.py, chat_repo.py
├── models/      chat_models.py, schemas.py
├── utils/       prompt_builder.py, citation_mapper.py
├── exceptions/  exceptions.py
└── tests/       test_chat_service.py
```

### 7.3 Summarization Service

```
summarization_service/
├── routes/      summary_routes.py
├── services/    summary_service.py, mode_selector.py
├── repository/  paper_repo.py, cache_repo.py
├── models/      summary_models.py, schemas.py
├── utils/       text_chunker.py
├── exceptions/  exceptions.py
└── tests/       test_summary_service.py
```

### 7.4 Translation Service

```
translation_service/
├── routes/      translation_routes.py
├── services/    translation_service.py, lang_detector.py, mode_selector.py
├── repository/  translation_repo.py, cache_repo.py
├── models/      translation_models.py, schemas.py
├── utils/       term_preserving_utils.py
├── exceptions/  exceptions.py
└── tests/       test_translation_service.py
```

### 7.5 OCR Service

```
ocr_service/
├── routes/      ocr_routes.py
├── services/    ocr_service.py, engine_selector.py
├── repository/  ocr_result_repo.py
├── models/      ocr_models.py, schemas.py
├── utils/       image_preprocessor.py, paddle_wrapper.py,
│                mistral_wrapper.py, lighton_wrapper.py
├── exceptions/  exceptions.py
└── tests/       test_ocr_service.py
```

### 7.6 Q&A Service

```
qa_service/
├── routes/      qa_routes.py
├── services/    qa_service.py, mode_selector.py
├── repository/  qa_result_repo.py
├── models/      qa_models.py, schemas.py
├── utils/       section_splitter.py
├── exceptions/  exceptions.py
└── tests/       test_qa_service.py
```

### 7.7 Voice Service

```
voice_service/
├── routes/      stt_routes.py, tts_routes.py
├── services/    asr_service.py, tts_service.py, provider_selector.py
├── repository/  voice_session_repo.py
├── models/      voice_models.py, schemas.py
├── utils/       audio_preprocessor.py
├── exceptions/  exceptions.py
└── tests/       test_voice_service.py
```

### 7.8 Export Service

```
export_service/
├── routes/      export_routes.py
├── services/    export_service.py
├── repository/  result_repo.py
├── models/      export_models.py, schemas.py
├── utils/
│   ├── txt_exporter.py
│   ├── docx_exporter.py
│   └── pdf_exporter.py
├── exceptions/  exceptions.py
└── tests/       test_export_service.py
```

---

## 8. AI Agent Orchestration — CrewAI

### Agent Pipeline

```
User describes research topic
        ↓
CrewAI Orchestrator (sequential execution)
        ↓
keyword_agent → search_agent → download_agent → import_agent → report_agent
```

### 8.1 Keyword Agent (`keyword_agent`)
Extracts precise search keywords from the user's natural language query using an LLM.

### 8.2 Search Agent (`search_agent`)
Queries Semantic Scholar API with extracted keywords. Returns paper metadata with PDF links.

### 8.3 Download Agent (`download_agent`)
Downloads discovered PDFs using async httpx. Handles retries and file validation.

### 8.4 Import Agent (`import_agent`)
Runs the full ingestion pipeline on downloaded PDFs:
```
PDF → OCR (if needed) → chunk → embed → Qdrant + PostgreSQL
```

### 8.5 Report Agent (`report_agent`)
Generates a structured discovery report: papers found, imported, failed, and ranked by relevance.

### 8.6 Orchestrator

```python
# agent_service/services/orchestrator.py
from crewai import Crew, Process

crew = Crew(
    agents=[keyword_agent, search_agent, download_agent,
            import_agent, report_agent],
    tasks=[keyword_task, search_task, download_task,
           import_task, report_task],
    process=Process.sequential,
    verbose=False
)

async def run_discovery(query: str) -> DiscoveryReport:
    result = await crew.kickoff_async(inputs={"query": query})
    return DiscoveryReport.parse(result)
```

---

## 9. ML Models & LLM Providers

### 9.1 Local ML Models

| Component | Model | Source | Notes |
|---|---|---|---|
| **Embeddings** | all-MiniLM-L6-v2 | sentence-transformers | 384-dim vectors |
| **Summarization** | distilbart-cnn-12-6 | sshleifer | Model mode |
| **Q&A Generation** | t5-small | Google | Model mode |
| **Translation EN→AR** | opus-mt-en-ar | Helsinki-NLP | Model mode |
| **Translation AR→EN** | opus-mt-ar-en | Helsinki-NLP | Model mode |
| **Translation (Alt)** | nllb-200-distilled-600M | Facebook | Multilingual |
| **ASR / STT** | Whisper small | OpenAI | via Faster Whisper |
| **TTS (offline)** | speecht5_tts | Microsoft | Offline fallback |
| **OCR** | PaddleOCR | Baidu | Local OCR engine |

---

### 9.2 LLM Providers

All LLM providers are accessed through **LiteLLM**. See Section 10 for full configuration details.

| Provider | Models | Type |
|---|---|---|
| **OpenAI** | gpt-4o, gpt-4o-mini, gpt-3.5-turbo | Cloud |
| **Google Gemini** | gemini-1.5-pro, gemini-1.5-flash | Cloud |
| **Anthropic Claude** | claude-3-5-sonnet, claude-3-haiku | Cloud |
| **Groq** | llama3-8b-8192, llama3-70b-8192 | Cloud (fast) |
| **Cohere** | command-r, command-r-plus | Cloud |
| **Ollama (local)** | llama3, mistral, phi3, gemma2, qwen2 | Local |
| **Ollama (cloud)** | Any hosted Ollama endpoint | Self-hosted cloud |

*Additional LLM providers can be added via LiteLLM without code changes.*

---

## 10. LiteLLM — Unified LLM Interface

### 10.1 Overview

LiteLLM provides a single, unified interface to call any LLM provider. The application never calls OpenAI, Gemini, or Claude SDKs directly — everything goes through LiteLLM. This means switching providers requires only a config change.

---

### 10.2 LiteLLM Client (Shared Module)

```python
# shared/llm_client/client.py

import litellm
from litellm import acompletion
from typing import Optional, List
from shared.logger.logger import get_logger
from shared.rate_limiter.limiter import llm_rate_limiter

logger = get_logger(__name__)

class LLMClient:
    """
    Unified LLM client via LiteLLM.
    Supports OpenAI, Gemini, Claude, Groq, Cohere, Ollama, and more.
    All calls include rate limiting, timeout, retry, and error handling.
    """

    def __init__(self, provider: str, timeout: int = 30, max_retries: int = 3):
        self.provider = provider
        self.timeout = timeout
        self.max_retries = max_retries

        # LiteLLM global settings
        litellm.set_verbose = False
        litellm.request_timeout = timeout
        litellm.num_retries = max_retries
        litellm.drop_params = True  # silently drop unsupported params per provider

    async def complete(
        self,
        prompt: str,
        system: Optional[str] = None,
        temperature: float = 0.3,
        max_tokens: int = 1000
    ) -> str:
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        await llm_rate_limiter.acquire()

        try:
            logger.info("llm_request", provider=self.provider, prompt_len=len(prompt))

            response = await acompletion(
                model=self.provider,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                timeout=self.timeout,
                num_retries=self.max_retries
            )

            content = response.choices[0].message.content
            logger.info("llm_response", provider=self.provider, tokens=response.usage.total_tokens)
            return content

        except litellm.exceptions.RateLimitError as e:
            logger.warning("llm_rate_limit", provider=self.provider, error=str(e))
            raise LLMRateLimitException("LLM rate limit reached. Please try again shortly.")

        except litellm.exceptions.Timeout as e:
            logger.error("llm_timeout", provider=self.provider, timeout=self.timeout)
            raise LLMTimeoutException("The AI request timed out. Please try again.")

        except litellm.exceptions.AuthenticationError as e:
            logger.error("llm_auth_error", provider=self.provider)
            raise LLMAuthException("LLM provider authentication failed.")

        except Exception as e:
            logger.error("llm_unexpected_error", provider=self.provider, error=str(e))
            raise LLMServiceException("The AI service is temporarily unavailable.")
```

---

### 10.3 Provider Configuration

```python
# shared/llm_client/providers.py

PROVIDER_MODELS = {
    # Cloud providers
    "openai":    "openai/gpt-4o-mini",
    "gemini":    "gemini/gemini-1.5-flash",
    "claude":    "anthropic/claude-3-haiku-20240307",
    "groq":      "groq/llama3-8b-8192",
    "cohere":    "cohere/command-r",

    # Local via Ollama
    "ollama_llama3":  "ollama/llama3",
    "ollama_mistral": "ollama/mistral",
    "ollama_phi3":    "ollama/phi3",
    "ollama_gemma2":  "ollama/gemma2",
    "ollama_qwen2":   "ollama/qwen2",

    # Self-hosted Ollama cloud endpoint
    "ollama_cloud": "openai/llama3",  # with OPENAI_API_BASE set to cloud endpoint
}

def get_provider_model(provider_key: str) -> str:
    model = PROVIDER_MODELS.get(provider_key)
    if not model:
        raise ValueError(f"Unknown LLM provider: {provider_key}")
    return model
```

---

### 10.4 Provider .env Configuration

```env
# Active LLM provider (pick one or configure per service)
LLM_PROVIDER=groq

# API Keys
OPENAI_API_KEY=sk-...
GEMINI_API_KEY=AI...
ANTHROPIC_API_KEY=sk-ant-...
GROQ_API_KEY=gsk_...
COHERE_API_KEY=...

# Ollama local
OLLAMA_BASE_URL=http://localhost:11434

# Ollama cloud (self-hosted)
OLLAMA_CLOUD_BASE_URL=https://your-ollama-server.com
OLLAMA_CLOUD_API_KEY=your_key_if_required

# LLM settings
LLM_TIMEOUT=30
LLM_MAX_RETRIES=3
LLM_TEMPERATURE=0.3
LLM_MAX_TOKENS=1000
```

---

## 11. OCR — Engines & Providers

### 11.1 Overview

The OCR Service supports three engines, selectable via configuration. Each engine has its own wrapper class following the same interface.

```python
# ocr_service/services/engine_selector.py

class OCREngine(ABC):
    @abstractmethod
    async def extract(self, file: bytes, filename: str) -> OCRResult: ...

class OCREngineSelector:
    def get_engine(self, engine: str) -> OCREngine:
        engines = {
            "paddle":  PaddleOCREngine(),
            "mistral": MistralOCREngine(),
            "lighton": LightOnOCREngine()
        }
        engine_obj = engines.get(engine)
        if not engine_obj:
            raise OCREngineNotFoundException(f"Unknown OCR engine: {engine}")
        return engine_obj
```

---

### 11.2 Engine 1 — PaddleOCR (Local)

**Type:** Local model — no API key required, runs fully offline.

**Supported formats:** PNG, JPG, JPEG, TIFF, BMP, scanned PDF

```python
# ocr_service/utils/paddle_wrapper.py

from paddleocr import PaddleOCR
from shared.logger.logger import get_logger

logger = get_logger(__name__)

class PaddleOCREngine(OCREngine):
    def __init__(self):
        self.ocr = PaddleOCR(use_angle_cls=True, lang="en", show_log=False)

    async def extract(self, file: bytes, filename: str) -> OCRResult:
        try:
            logger.info("paddle_ocr_start", filename=filename)
            result = self.ocr.ocr(file, cls=True)
            text = "\n".join([line[1][0] for block in result for line in block])
            logger.info("paddle_ocr_complete", filename=filename, chars=len(text))
            return OCRResult(text=text, engine="paddle", page_count=len(result))
        except Exception as e:
            logger.error("paddle_ocr_error", filename=filename, error=str(e))
            raise OCRExtractionException("Text extraction failed. Please try a different file or OCR engine.")
```

---

### 11.3 Engine 2 — Mistral OCR API

**Type:** Cloud API — requires `MISTRAL_API_KEY`. High accuracy for complex documents.

```python
# ocr_service/utils/mistral_wrapper.py

import httpx
from shared.logger.logger import get_logger

logger = get_logger(__name__)

class MistralOCREngine(OCREngine):
    BASE_URL = "https://api.mistral.ai/v1/ocr"

    def __init__(self):
        self.api_key = settings.MISTRAL_API_KEY
        if not self.api_key:
            raise MissingAPIKeyException("MISTRAL_API_KEY is not configured.")

    async def extract(self, file: bytes, filename: str) -> OCRResult:
        try:
            logger.info("mistral_ocr_start", filename=filename)
            async with httpx.AsyncClient(timeout=60) as client:
                response = await client.post(
                    self.BASE_URL,
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    files={"file": (filename, file, "application/octet-stream")},
                    data={"model": "mistral-ocr-latest"}
                )
                response.raise_for_status()
                data = response.json()
                text = data.get("text", "")
                logger.info("mistral_ocr_complete", filename=filename, chars=len(text))
                return OCRResult(text=text, engine="mistral")
        except httpx.TimeoutException:
            logger.error("mistral_ocr_timeout", filename=filename)
            raise OCRTimeoutException("Mistral OCR timed out. Try a smaller file or use local OCR.")
        except httpx.HTTPStatusError as e:
            logger.error("mistral_ocr_http_error", status=e.response.status_code)
            raise OCRProviderException("Mistral OCR API returned an error. Please try again.")
        except Exception as e:
            logger.error("mistral_ocr_error", error=str(e))
            raise OCRExtractionException("Text extraction via Mistral failed.")
```

---

### 11.4 Engine 3 — LightOnOCR

**Type:** Cloud API — requires `LIGHTON_API_KEY`. Specialized for scientific and academic documents.

```python
# ocr_service/utils/lighton_wrapper.py

import httpx
from shared.logger.logger import get_logger

logger = get_logger(__name__)

class LightOnOCREngine(OCREngine):
    BASE_URL = "https://api.lighton.ai/v1/ocr"

    def __init__(self):
        self.api_key = settings.LIGHTON_API_KEY
        if not self.api_key:
            raise MissingAPIKeyException("LIGHTON_API_KEY is not configured.")

    async def extract(self, file: bytes, filename: str) -> OCRResult:
        try:
            logger.info("lighton_ocr_start", filename=filename)
            async with httpx.AsyncClient(timeout=60) as client:
                response = await client.post(
                    self.BASE_URL,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/octet-stream"
                    },
                    content=file
                )
                response.raise_for_status()
                data = response.json()
                text = data.get("result", {}).get("text", "")
                logger.info("lighton_ocr_complete", filename=filename, chars=len(text))
                return OCRResult(text=text, engine="lighton")
        except httpx.TimeoutException:
            logger.error("lighton_ocr_timeout", filename=filename)
            raise OCRTimeoutException("LightOn OCR timed out.")
        except Exception as e:
            logger.error("lighton_ocr_error", error=str(e))
            raise OCRExtractionException("Text extraction via LightOn failed.")
```

---

### 11.5 OCR Engine Comparison

| Feature | PaddleOCR | Mistral OCR | LightOnOCR |
|---|---|---|---|
| **Type** | Local model | Cloud API | Cloud API |
| **API Key** | Not required | Required | Required |
| **Offline** | ✅ Yes | ❌ No | ❌ No |
| **Cost** | Free | Paid | Paid |
| **Best for** | General docs | Complex layouts | Academic papers |
| **Speed** | Medium | Fast | Fast |
| **Config key** | `paddle` | `mistral` | `lighton` |

---

## 12. Voice Interaction — STT & TTS

### 12.1 Overview

Voice interaction is handled through the **Voice Service** which supports multiple providers for both STT and TTS. All providers implement the same abstract interface — switching providers requires only a config change.

---

### 12.2 STT — Speech to Text

**Supported Providers:**

| Provider | Type | Config Key | Notes |
|---|---|---|---|
| **Faster Whisper** | Local model | `whisper` | Free, offline, default |
| **ElevenLabs** | Cloud API | `elevenlabs` | High accuracy |
| **Google Gemini** | Cloud API | `gemini` | Multilingual |

**STT Flow:**
```
User presses Record → MediaRecorder captures audio (WAV/WebM)
        ↓
Audio blob → POST /voice/stt
        ↓
Voice Service → Provider selected by STT_PROVIDER config
        ↓
Transcript returned to frontend
        ↓
Frontend sends transcript → POST /chat/message
```

**STT Provider Interface:**

```python
# voice_service/services/asr_service.py

class STTProvider(ABC):
    @abstractmethod
    async def transcribe(self, audio: bytes, language: str) -> str: ...

class WhisperSTTProvider(STTProvider):
    def __init__(self):
        self.model = WhisperModel("small", device="cpu", compute_type="int8")

    async def transcribe(self, audio: bytes, language: str) -> str:
        try:
            with tempfile.NamedTemporaryFile(suffix=".wav") as tmp:
                tmp.write(audio)
                tmp.flush()
                segments, _ = self.model.transcribe(tmp.name, language=language)
                return " ".join([seg.text for seg in segments]).strip()
        except Exception as e:
            logger.error("whisper_stt_error", error=str(e))
            raise STTException("Voice transcription failed. Please try again.")

class ElevenLabsSTTProvider(STTProvider):
    BASE_URL = "https://api.elevenlabs.io/v1/speech-to-text"

    async def transcribe(self, audio: bytes, language: str) -> str:
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.post(
                    self.BASE_URL,
                    headers={"xi-api-key": settings.ELEVENLABS_API_KEY},
                    files={"audio": ("audio.wav", audio, "audio/wav")},
                    data={"model_id": "scribe_v1", "language_code": language}
                )
                response.raise_for_status()
                return response.json().get("text", "")
        except httpx.TimeoutException:
            raise STTTimeoutException("Voice transcription timed out.")
        except Exception as e:
            logger.error("elevenlabs_stt_error", error=str(e))
            raise STTException("ElevenLabs transcription failed.")

class GeminiSTTProvider(STTProvider):
    async def transcribe(self, audio: bytes, language: str) -> str:
        try:
            import google.generativeai as genai
            genai.configure(api_key=settings.GEMINI_API_KEY)
            model = genai.GenerativeModel("gemini-1.5-flash")
            audio_part = {"mime_type": "audio/wav", "data": audio}
            response = model.generate_content([
                f"Transcribe this audio in {language}. Return only the transcript text.",
                audio_part
            ])
            return response.text.strip()
        except Exception as e:
            logger.error("gemini_stt_error", error=str(e))
            raise STTException("Gemini transcription failed.")
```

---

### 12.3 TTS — Text to Speech

**Supported Providers:**

| Provider | Type | Config Key | Languages |
|---|---|---|---|
| **Edge-TTS** | Cloud (free) | `edge_tts` | Arabic, English, + many more |
| **ElevenLabs** | Cloud API | `elevenlabs` | Arabic, English, + many more |
| **Google Gemini** | Cloud API | `gemini` | Multilingual |
| **SpeechT5** | Local model | `speecht5` | English (offline fallback) |

**TTS Voice Configuration:**

```python
# voice_service/utils/voice_config.py

EDGE_TTS_VOICES = {
    "ar": "ar-SA-HamedNeural",
    "en": "en-US-ChristopherNeural"
}

ELEVENLABS_VOICES = {
    "ar": "your_arabic_voice_id",
    "en": "your_english_voice_id"
}
```

**TTS Provider Interface:**

```python
# voice_service/services/tts_service.py

class TTSProvider(ABC):
    @abstractmethod
    async def synthesize(self, text: str, language: str) -> bytes: ...

class EdgeTTSProvider(TTSProvider):
    async def synthesize(self, text: str, language: str) -> bytes:
        try:
            voice = EDGE_TTS_VOICES.get(language, "en-US-ChristopherNeural")
            communicate = edge_tts.Communicate(text, voice)
            audio_bytes = b""
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    audio_bytes += chunk["data"]
            return audio_bytes
        except Exception as e:
            logger.error("edge_tts_error", language=language, error=str(e))
            raise TTSException("Voice generation failed. Please try again.")

class ElevenLabsTTSProvider(TTSProvider):
    BASE_URL = "https://api.elevenlabs.io/v1/text-to-speech"

    async def synthesize(self, text: str, language: str) -> bytes:
        try:
            voice_id = ELEVENLABS_VOICES.get(language, ELEVENLABS_VOICES["en"])
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.post(
                    f"{self.BASE_URL}/{voice_id}",
                    headers={
                        "xi-api-key": settings.ELEVENLABS_API_KEY,
                        "Content-Type": "application/json"
                    },
                    json={
                        "text": text,
                        "model_id": "eleven_multilingual_v2",
                        "voice_settings": {"stability": 0.5, "similarity_boost": 0.75}
                    }
                )
                response.raise_for_status()
                return response.content
        except httpx.TimeoutException:
            raise TTSTimeoutException("Voice generation timed out.")
        except Exception as e:
            logger.error("elevenlabs_tts_error", error=str(e))
            raise TTSException("ElevenLabs TTS failed.")

class GeminiTTSProvider(TTSProvider):
    async def synthesize(self, text: str, language: str) -> bytes:
        try:
            import google.generativeai as genai
            genai.configure(api_key=settings.GEMINI_API_KEY)
            model = genai.GenerativeModel("gemini-2.0-flash-exp")
            response = model.generate_content(
                f"Generate speech audio for: {text}",
                generation_config={"response_modalities": ["AUDIO"]}
            )
            return response.candidates[0].content.parts[0].inline_data.data
        except Exception as e:
            logger.error("gemini_tts_error", error=str(e))
            raise TTSException("Gemini TTS failed.")
```

---

### 12.4 Provider Selector

```python
# voice_service/services/provider_selector.py

class VoiceProviderSelector:
    def get_stt_provider(self) -> STTProvider:
        provider = settings.STT_PROVIDER
        providers = {
            "whisper":     WhisperSTTProvider,
            "elevenlabs":  ElevenLabsSTTProvider,
            "gemini":      GeminiSTTProvider
        }
        cls = providers.get(provider)
        if not cls:
            raise InvalidProviderException(f"Unknown STT provider: {provider}")
        return cls()

    def get_tts_provider(self) -> TTSProvider:
        provider = settings.TTS_PROVIDER
        providers = {
            "edge_tts":    EdgeTTSProvider,
            "elevenlabs":  ElevenLabsTTSProvider,
            "gemini":      GeminiTTSProvider,
            "speecht5":    SpeechT5Provider
        }
        cls = providers.get(provider)
        if not cls:
            raise InvalidProviderException(f"Unknown TTS provider: {provider}")
        return cls()
```

---

## 13. Chat UX — Message Actions

### 13.1 Overview

Users can interact with both their own messages and the assistant's messages through a set of UX actions that improve usability and allow feedback collection.

---

### 13.2 Available Actions

| Action | Target | Stored? | Purpose |
|---|---|---|---|
| **Copy** | User message | No | Copy user's own text |
| **Copy** | Assistant message | No | Copy assistant response |
| **Like** | Assistant message | Yes → DB | Positive feedback |
| **Dislike** | Assistant message | Yes → DB | Negative feedback |

---

### 13.3 Database Schema

```sql
-- Message feedback stored in chat_messages table
ALTER TABLE chat_messages ADD COLUMN feedback VARCHAR(10) DEFAULT NULL;
-- feedback values: NULL (no action), 'like', 'dislike'
```

---

### 13.4 Backend Action Routes

```python
# chatbot_service/routes/action_routes.py

router = APIRouter(prefix="/chat/messages", tags=["message-actions"])

@router.patch("/{message_id}/like")
async def like_message(
    message_id: UUID,
    service: ActionService = Depends()
) -> MessageFeedbackResponse:
    return await service.set_feedback(message_id, "like")

@router.patch("/{message_id}/dislike")
async def dislike_message(
    message_id: UUID,
    service: ActionService = Depends()
) -> MessageFeedbackResponse:
    return await service.set_feedback(message_id, "dislike")

@router.patch("/{message_id}/remove-feedback")
async def remove_feedback(
    message_id: UUID,
    service: ActionService = Depends()
) -> MessageFeedbackResponse:
    return await service.set_feedback(message_id, None)
```

---

### 13.5 Action Service

```python
# chatbot_service/services/action_service.py

class ActionService:
    def __init__(self, chat_repo: ChatRepository = Depends()):
        self.chat_repo = chat_repo

    async def set_feedback(
        self, message_id: UUID, feedback: Optional[str]
    ) -> MessageFeedbackResponse:
        message = await self.chat_repo.get_message(message_id)
        if not message:
            raise MessageNotFoundException(message_id)
        if message.role != "assistant":
            raise InvalidFeedbackTargetException("Feedback can only be given on assistant messages.")

        updated = await self.chat_repo.update_feedback(message_id, feedback)
        logger.info("message_feedback", message_id=str(message_id), feedback=feedback)
        return MessageFeedbackResponse(message_id=message_id, feedback=feedback)
```

---

### 13.6 Frontend Copy Behavior

Copy is handled entirely on the frontend — no API call needed:

```typescript
// components/chat/MessageActions.tsx

const copyToClipboard = async (text: string) => {
  try {
    await navigator.clipboard.writeText(text);
    toast.success("Copied to clipboard");
  } catch {
    toast.error("Failed to copy");
  }
};

// For user messages
<button onClick={() => copyToClipboard(message.content)}>
  <CopyIcon size={14} />
</button>

// For assistant messages
<button onClick={() => copyToClipboard(message.content)}>
  <CopyIcon size={14} />
</button>
<button onClick={() => handleLike(message.id)}>
  <ThumbsUpIcon size={14} className={liked ? "text-green-500" : ""} />
</button>
<button onClick={() => handleDislike(message.id)}>
  <ThumbsDownIcon size={14} className={disliked ? "text-red-500" : ""} />
</button>
```

---

## 14. Chat & File Storage

### 14.1 PostgreSQL Schema

```sql
-- Users
CREATE TABLE users (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email       VARCHAR(255) UNIQUE NOT NULL,
    hashed_pwd  VARCHAR(255) NOT NULL,
    created_at  TIMESTAMP DEFAULT NOW()
);

-- Chat Sessions
CREATE TABLE chat_sessions (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     UUID REFERENCES users(id) ON DELETE CASCADE,
    title       VARCHAR(500),
    created_at  TIMESTAMP DEFAULT NOW(),
    updated_at  TIMESTAMP DEFAULT NOW()
);

-- Chat Messages
CREATE TABLE chat_messages (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id  UUID REFERENCES chat_sessions(id) ON DELETE CASCADE,
    role        VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant')),
    content     TEXT NOT NULL,
    citations   JSONB DEFAULT '[]',
    input_type  VARCHAR(20) DEFAULT 'text' CHECK (input_type IN ('text', 'voice')),
    feedback    VARCHAR(10) CHECK (feedback IN ('like', 'dislike')),
    created_at  TIMESTAMP DEFAULT NOW()
);

-- Papers (uploaded + agent-collected)
CREATE TABLE papers (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     UUID REFERENCES users(id) ON DELETE CASCADE,
    filename    VARCHAR(500) NOT NULL,
    file_path   TEXT NOT NULL,
    source      VARCHAR(20) DEFAULT 'upload' CHECK (source IN ('upload', 'agent')),
    external_id VARCHAR(255),
    page_count  INT,
    language    VARCHAR(10) DEFAULT 'en',
    status      VARCHAR(30) DEFAULT 'pending',
    created_at  TIMESTAMP DEFAULT NOW()
);

-- Tool Results
CREATE TABLE tool_results (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    paper_id    UUID REFERENCES papers(id) ON DELETE CASCADE,
    user_id     UUID REFERENCES users(id) ON DELETE CASCADE,
    tool_type   VARCHAR(50) NOT NULL,
    mode_used   VARCHAR(20),
    content     TEXT NOT NULL,
    metadata    JSONB DEFAULT '{}',
    created_at  TIMESTAMP DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_chat_messages_session ON chat_messages(session_id);
CREATE INDEX idx_papers_user ON papers(user_id);
CREATE INDEX idx_tool_results_paper ON tool_results(paper_id);
```

---

### 14.2 File Storage Structure

```
storage/
├── uploads/
│   └── {user_id}/
│       └── {paper_id}/
│           └── original.pdf
│
└── agent_downloads/
    └── {user_id}/
        └── {paper_id}/
            └── paper.pdf
```

---

## 15. Database Migrations — Alembic

### 15.1 Why Alembic

Alembic is the standard database migration tool for SQLAlchemy projects. It tracks schema changes as versioned migration scripts, allowing safe and reproducible schema evolution across environments (development, staging, production).

---

### 15.2 Setup

```bash
# Install
pip install alembic

# Initialize Alembic in project root
alembic init infrastructure/postgres/migrations
```

---

### 15.3 alembic.ini

```ini
[alembic]
script_location = infrastructure/postgres/migrations
sqlalchemy.url = postgresql+asyncpg://%(POSTGRES_USER)s:%(POSTGRES_PASSWORD)s@%(POSTGRES_HOST)s/%(POSTGRES_DB)s

[loggers]
keys = root, sqlalchemy, alembic

[logger_alembic]
level = WARN
handlers =
qualname = alembic.runtime.migration
```

---

### 15.4 env.py Configuration

```python
# infrastructure/postgres/migrations/env.py

from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config
from alembic import context
from infrastructure.postgres.database import Base

# Import ALL models so Alembic can detect them
from services.chatbot_service.models.domain import ChatSession, ChatMessage
from services.ocr_service.models.domain import Paper
from services.summarization_service.models.domain import ToolResult

target_metadata = Base.metadata

def run_migrations_online():
    connectable = async_engine_from_config(
        context.config.get_section(context.config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()
```

---

### 15.5 Migration Workflow

```bash
# Generate a new migration after changing SQLAlchemy models
alembic revision --autogenerate -m "add feedback column to chat_messages"

# Apply all pending migrations (upgrade to latest)
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# View current migration version
alembic current

# View full migration history
alembic history --verbose

# Run in Docker after containers start
docker-compose exec gateway alembic upgrade head
```

---

### 15.6 Example Migration File

```python
# infrastructure/postgres/migrations/versions/001_initial_schema.py

"""Initial schema

Revision ID: 001
Create Date: 2024-01-01
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB

def upgrade():
    op.create_table("users",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("email", sa.String(255), unique=True, nullable=False),
        sa.Column("hashed_pwd", sa.String(255), nullable=False),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )
    op.create_table("chat_sessions",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id")),
        sa.Column("title", sa.String(500)),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now()),
    )
    # ... remaining tables

def downgrade():
    op.drop_table("chat_sessions")
    op.drop_table("users")
```

---

## 16. NLP Services — Model vs LLM Mode

### 16.1 Mode Configuration

```env
# .env
SUMMARIZATION_MODE=model      # "model" or "llm"
QA_MODE=model
TRANSLATION_EN_AR_MODE=model
TRANSLATION_AR_EN_MODE=model

LLM_PROVIDER=groq
```

```python
# shared/llm_client/mode_selector.py

class ModeSelector:
    def get_strategy(self, service: str, override_mode: Optional[str] = None):
        mode = override_mode or os.getenv(f"{service.upper()}_MODE", "model")
        if mode not in ("model", "llm"):
            raise InvalidModeException(f"Mode must be 'model' or 'llm', got: {mode}")
        return mode
```

---

### 16.2 Summarization

```python
# Model Mode
async def summarize_model(text: str) -> str:
    chunks = chunk_text(text, chunk_size=1024)
    summaries = [summarizer(chunk)[0]["summary_text"] for chunk in chunks]
    return " ".join(summaries)

# LLM Mode
async def summarize_llm(text: str) -> str:
    return await llm_client.complete(
        system="You are an expert at summarizing academic research papers.",
        prompt=f"""Summarize the following paper covering:
        - Objectives, Methodology, Key Findings, Conclusions, Limitations

        Text:
        {text}"""
    )
```

---

### 16.3 Q&A Generation

```python
# Model Mode
async def generate_qa_model(text: str) -> List[QAPair]:
    output = qa_pipeline(f"generate questions: {text}", max_length=512)
    return parse_qa_pairs(output[0]["generated_text"])

# LLM Mode
async def generate_qa_llm(text: str) -> List[QAPair]:
    response = await llm_client.complete(
        system="You are an expert at generating educational Q&A from academic content.",
        prompt=f"""Generate 10 comprehensive Q&A pairs from this research paper.
        Format strictly as:
        Q: [question]
        A: [answer]

        Content:
        {text}"""
    )
    return parse_qa_pairs(response)
```

---

### 16.4 Translation

```python
# Model Mode
async def translate_model(text: str, direction: str) -> str:
    model_map = {
        "en-ar": "Helsinki-NLP/opus-mt-en-ar",
        "ar-en": "Helsinki-NLP/opus-mt-ar-en"
    }
    tokenizer = MarianTokenizer.from_pretrained(model_map[direction])
    model = MarianMTModel.from_pretrained(model_map[direction])
    tokens = tokenizer([text], return_tensors="pt", padding=True, truncation=True)
    translated = model.generate(**tokens)
    return tokenizer.decode(translated[0], skip_special_tokens=True)

# LLM Mode
async def translate_llm(text: str, direction: str) -> str:
    target = {"en-ar": "Arabic", "ar-en": "English"}[direction]
    return await llm_client.complete(
        system=f"You are an expert scientific translator. Translate accurately to {target}.",
        prompt=f"Translate this research paper text to {target}. Preserve all technical terms.\n\n{text}"
    )
```

---

### 16.5 Mode Comparison

| Aspect | Model Mode | LLM Mode |
|---|---|---|
| Speed | Fast (local) | Depends on provider |
| Cost | Free | API costs |
| Privacy | Full (no external calls) | Data sent to provider |
| Quality | Good | Better for complex content |
| Offline | ✅ | ❌ |
| Context window | Limited | Large |

---

## 17. Export System

### 17.1 Supported Exports

| Tool | TXT | DOCX | PDF |
|---|---|---|---|
| Summarization | ✅ | ✅ | ✅ |
| Q&A Generation | ✅ | ✅ | ✅ |
| Translation EN→AR | ✅ (RTL) | ✅ (RTL) | ✅ (RTL) |
| Translation AR→EN | ✅ | ✅ | ✅ |
| OCR Result | ✅ | ✅ | ✅ |

---

### 17.2 Export API

```
POST /export/{tool_type}/{result_id}?format=txt
POST /export/{tool_type}/{result_id}?format=docx
POST /export/{tool_type}/{result_id}?format=pdf

tool_type: summary | qa | translation | ocr
```

---

### 17.3 TXT Exporter

```python
# export_service/utils/txt_exporter.py

async def export_as_txt(content: str, title: str) -> bytes:
    output = f"{title}\n{'=' * len(title)}\n\n{content}"
    return output.encode("utf-8")
```

---

### 17.4 DOCX Exporter

```python
# export_service/utils/docx_exporter.py

from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from io import BytesIO

async def export_as_docx(content: str, title: str, rtl: bool = False) -> bytes:
    doc = Document()
    alignment = WD_ALIGN_PARAGRAPH.RIGHT if rtl else WD_ALIGN_PARAGRAPH.LEFT

    heading = doc.add_heading(title, level=1)
    heading.alignment = alignment

    for paragraph in content.split("\n\n"):
        if paragraph.strip():
            p = doc.add_paragraph(paragraph.strip())
            p.paragraph_format.alignment = alignment

    buffer = BytesIO()
    doc.save(buffer)
    return buffer.getvalue()
```

---

### 17.5 PDF Exporter

```python
# export_service/utils/pdf_exporter.py

from fpdf import FPDF
from io import BytesIO

async def export_as_pdf(content: str, title: str, language: str = "en") -> bytes:
    pdf = FPDF()
    pdf.add_page()

    if language == "ar":
        pdf.add_font("Arabic", fname="fonts/NotoSansArabic.ttf", uni=True)
        pdf.set_font("Arabic", size=14)
    else:
        pdf.set_font("Helvetica", size=14)

    pdf.cell(0, 12, title, ln=True, align="C")
    pdf.ln(6)
    pdf.set_font_size(11)
    pdf.multi_cell(0, 8, content)

    return bytes(pdf.output())
```

---

## 18. Error Handling & Exception Management

### 18.1 Philosophy

The application follows a strict **two-layer error strategy**:

1. **Internal layer**: All exceptions are logged with full technical detail (stack traces, context, IDs)
2. **External layer**: Users only ever see clean, friendly messages — never system errors, stack traces, or internal codes

---

### 18.2 Custom Exception Hierarchy

```python
# shared/error_handler/exceptions.py

class AppBaseException(Exception):
    """Base class for all application exceptions."""
    def __init__(self, user_message: str, internal_detail: str = ""):
        self.user_message = user_message        # shown to user
        self.internal_detail = internal_detail  # logged only, never shown
        super().__init__(internal_detail or user_message)

# ── LLM Exceptions ────────────────────────────────────────────────────
class LLMServiceException(AppBaseException): pass
class LLMRateLimitException(AppBaseException): pass
class LLMTimeoutException(AppBaseException): pass
class LLMAuthException(AppBaseException): pass

# ── OCR Exceptions ────────────────────────────────────────────────────
class OCRExtractionException(AppBaseException): pass
class OCRTimeoutException(AppBaseException): pass
class OCRProviderException(AppBaseException): pass
class OCREngineNotFoundException(AppBaseException): pass

# ── Voice Exceptions ──────────────────────────────────────────────────
class STTException(AppBaseException): pass
class STTTimeoutException(AppBaseException): pass
class TTSException(AppBaseException): pass
class TTSTimeoutException(AppBaseException): pass
class InvalidProviderException(AppBaseException): pass

# ── Data Exceptions ───────────────────────────────────────────────────
class PaperNotFoundException(AppBaseException):
    def __init__(self, paper_id):
        super().__init__(
            user_message="Paper not found.",
            internal_detail=f"Paper with ID {paper_id} does not exist."
        )

class MessageNotFoundException(AppBaseException):
    def __init__(self, message_id):
        super().__init__(
            user_message="Message not found.",
            internal_detail=f"Message {message_id} not found."
        )

class InvalidFeedbackTargetException(AppBaseException): pass
class InvalidModeException(AppBaseException): pass
class MissingAPIKeyException(AppBaseException): pass

# ── Export Exceptions ─────────────────────────────────────────────────
class ExportException(AppBaseException): pass
class UnsupportedFormatException(AppBaseException): pass
```

---

### 18.3 Global Exception Handler

```python
# shared/error_handler/handler.py

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from shared.logger.logger import get_logger

logger = get_logger(__name__)

def register_exception_handlers(app: FastAPI) -> None:

    @app.exception_handler(AppBaseException)
    async def app_exception_handler(
        request: Request, exc: AppBaseException
    ) -> JSONResponse:
        logger.error(
            "app_exception",
            path=request.url.path,
            user_message=exc.user_message,
            internal_detail=exc.internal_detail,
            exc_type=type(exc).__name__
        )
        return JSONResponse(
            status_code=400,
            content={"error": exc.user_message, "success": False}
        )

    @app.exception_handler(LLMRateLimitException)
    async def rate_limit_handler(
        request: Request, exc: LLMRateLimitException
    ) -> JSONResponse:
        logger.warning("llm_rate_limit_hit", path=request.url.path)
        return JSONResponse(
            status_code=429,
            content={"error": exc.user_message, "success": False}
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        # Log full detail internally
        logger.error(
            "unexpected_error",
            path=request.url.path,
            error=str(exc),
            exc_type=type(exc).__name__,
            exc_info=True  # includes full stack trace in logs
        )
        # Return generic message to user — never expose system internals
        return JSONResponse(
            status_code=500,
            content={
                "error": "Something went wrong. Please try again.",
                "success": False
            }
        )
```

---

### 18.4 Standard API Response Format

All API responses follow a consistent format:

```python
# shared/error_handler/responses.py

class APIResponse(BaseModel):
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None

# Success response
{"success": true, "data": {"content": "...", "paper_id": "..."}}

# Error response (what user sees)
{"success": false, "error": "Paper not found."}

# Never in response:
# - Stack traces
# - Database error messages
# - Internal IDs or system paths
# - API keys or credentials
```

---

## 19. Logging & Monitoring

### 19.1 Philosophy

All logs use **structured logging** (JSON format) so they can be easily searched, filtered, and monitored by log management tools (e.g., Grafana Loki, ELK Stack, Datadog).

Every log entry contains: timestamp, level, service name, event name, and relevant context.

---

### 19.2 Logger Setup

```python
# shared/logger/logger.py

import structlog
import logging
import sys
from settings import settings

def setup_logging():
    log_level = logging.DEBUG if settings.DEBUG else logging.INFO

    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()   # structured JSON output
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=log_level
    )

def get_logger(name: str):
    return structlog.get_logger(name)
```

---

### 19.3 What Gets Logged

| Event | Level | Logged Fields |
|---|---|---|
| API request received | INFO | path, method, user_id |
| LLM call start | INFO | provider, prompt_len |
| LLM call complete | INFO | provider, tokens_used |
| LLM rate limit hit | WARNING | provider, retry_after |
| LLM timeout | ERROR | provider, timeout_sec |
| OCR started | INFO | engine, filename |
| OCR complete | INFO | engine, filename, char_count |
| OCR failed | ERROR | engine, filename, error |
| Paper upload started | INFO | filename, user_id |
| Paper processing done | INFO | paper_id, duration_ms |
| STT transcription | INFO | provider, language, duration |
| TTS generation | INFO | provider, language, text_len |
| Message feedback | INFO | message_id, feedback |
| Cache hit | DEBUG | key |
| Cache miss | DEBUG | key |
| DB query | DEBUG | table, operation, duration_ms |
| Unexpected error | ERROR | path, error, stack trace |
| App startup | INFO | service, version, environment |

---

### 19.4 Sample Log Entries (JSON)

```json
{"timestamp": "2024-01-15T10:23:45Z", "level": "info", "service": "chatbot_service",
 "event": "llm_request", "provider": "groq/llama3-8b-8192", "prompt_len": 1247}

{"timestamp": "2024-01-15T10:23:46Z", "level": "info", "service": "chatbot_service",
 "event": "llm_response", "provider": "groq/llama3-8b-8192", "tokens": 342}

{"timestamp": "2024-01-15T10:24:01Z", "level": "error", "service": "ocr_service",
 "event": "mistral_ocr_timeout", "filename": "paper.pdf", "timeout": 60}

{"timestamp": "2024-01-15T10:24:02Z", "level": "warning", "service": "gateway",
 "event": "rate_limit_exceeded", "user_id": "abc123", "endpoint": "/summarize"}
```

---

### 19.5 Request Logging Middleware

```python
# shared/logger/middleware.py

import time
from fastapi import Request
from shared.logger.logger import get_logger

logger = get_logger(__name__)

async def log_requests(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    duration_ms = round((time.time() - start) * 1000, 2)

    logger.info(
        "http_request",
        method=request.method,
        path=request.url.path,
        status=response.status_code,
        duration_ms=duration_ms,
        user_agent=request.headers.get("user-agent", "")
    )
    return response
```

---

## 20. Rate Limiting & Timeouts

### 20.1 API Rate Limiting (slowapi)

Rate limiting prevents abuse and protects the system from being overwhelmed. Applied at the API Gateway level.

```python
# gateway/middleware/rate_limit.py

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import FastAPI

limiter = Limiter(key_func=get_remote_address)

def register_rate_limiting(app: FastAPI):
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)

async def rate_limit_exceeded_handler(request, exc):
    return JSONResponse(
        status_code=429,
        content={"error": "Too many requests. Please wait a moment and try again.", "success": False}
    )
```

```python
# Applying limits to routes
@router.post("/summarize")
@limiter.limit("10/minute")   # 10 summarization requests per minute per IP
async def summarize(request: Request, ...): ...

@router.post("/chat/message")
@limiter.limit("30/minute")   # 30 chat messages per minute
async def chat(request: Request, ...): ...

@router.post("/voice/stt")
@limiter.limit("20/minute")   # 20 voice transcriptions per minute
async def stt(request: Request, ...): ...
```

---

### 20.2 LLM Rate Limiting (LiteLLM + AsyncLimiter)

```python
# shared/rate_limiter/limiter.py

from asyncio import Semaphore

class LLMRateLimiter:
    """
    Controls concurrent LLM requests to avoid hitting provider rate limits.
    Max concurrent LLM calls configurable via LLM_MAX_CONCURRENT env var.
    """
    def __init__(self, max_concurrent: int = 5):
        self._semaphore = Semaphore(max_concurrent)

    async def acquire(self):
        await self._semaphore.acquire()

    def release(self):
        self._semaphore.release()

    async def __aenter__(self):
        await self.acquire()
        return self

    async def __aexit__(self, *args):
        self.release()

# Global singleton used across all services
llm_rate_limiter = LLMRateLimiter(
    max_concurrent=int(os.getenv("LLM_MAX_CONCURRENT", "5"))
)
```

---

### 20.3 Timeouts

Timeouts are configured at multiple levels to prevent hanging requests:

```python
# shared/llm_client/client.py
litellm.request_timeout = settings.LLM_TIMEOUT   # default: 30 seconds

# OCR API calls
async with httpx.AsyncClient(timeout=60) as client: ...   # OCR timeout: 60s

# Paper download (agent)
async with httpx.AsyncClient(timeout=120) as client: ...  # Download timeout: 120s

# Redis operations
redis = aioredis.from_url(url, socket_timeout=5)          # Redis timeout: 5s

# Database queries (SQLAlchemy)
engine = create_async_engine(url, pool_timeout=30)        # DB pool timeout: 30s
```

---

### 20.4 Rate Limit Configuration (.env)

```env
# API rate limits
RATE_LIMIT_CHAT=30/minute
RATE_LIMIT_SUMMARIZE=10/minute
RATE_LIMIT_TRANSLATE=10/minute
RATE_LIMIT_OCR=5/minute
RATE_LIMIT_STT=20/minute
RATE_LIMIT_TTS=20/minute

# LLM concurrency
LLM_MAX_CONCURRENT=5
LLM_TIMEOUT=30
LLM_MAX_RETRIES=3

# External API timeouts (seconds)
OCR_API_TIMEOUT=60
DOWNLOAD_TIMEOUT=120
REDIS_TIMEOUT=5
```

---

## 21. Technical Architecture: Async & Concurrent Processing

### 21.1 Parallel Paper Processing

```python
async def process_multiple_papers(files: List[UploadFile]) -> List[PaperResult]:
    tasks = [process_single_paper(file) for file in files]
    return await asyncio.gather(*tasks, return_exceptions=True)
```

### 21.2 OCR Page-Level Parallelism

```python
async def ocr_large_pdf(pdf_path: str) -> str:
    page_chunks = split_pdf_into_chunks(pdf_path, chunk_size=10)
    results = await asyncio.gather(*[ocr_chunk(chunk) for chunk in page_chunks])
    return merge_ordered(results)
```

### 21.3 Simultaneous Tool Execution

```python
summary, translation, qa = await asyncio.gather(
    summarization_service.summarize(paper_id, mode="model"),
    translation_service.translate(paper_id, "en-ar", mode="model"),
    qa_service.generate(paper_id, mode="llm")
)
```

---

## 22. Technical Architecture: Batch Processing

### 22.1 Bulk Ingestion

```
200 PDFs queued
  ↓
Background task (FastAPI BackgroundTasks or Celery)
  ↓
Process in concurrent chunks of 10
  ↓
Per chunk: OCR → chunk text → embed → Qdrant → PostgreSQL
  ↓
After each paper: Redis.publish progress event
  ↓
Repeat until done
```

### 22.2 Scheduled Operations

| Operation | Schedule | Benefit |
|---|---|---|
| Bulk summarization | Nightly 2:00 AM | Frees daytime resources |
| Translation batch | Queue threshold | Groups small jobs |
| Embedding refresh | Weekly | Updates when models change |

### 22.3 ETL Pipeline

```
Extract  → Raw PDFs + metadata from storage
Transform → OCR → Clean → Chunk → Embed → Tag
Load     → PostgreSQL (metadata) + Qdrant (vectors)
```

---

## 23. Combining Concurrency with Batch Processing

```
Batch job starts
  ↓
Step 1: Read chunk of papers    (sequential)
  ↓
Step 2: Process chunk           (asyncio.gather — concurrent)
    Coroutine 1 → Paper 1 OCR + Embed
    Coroutine 2 → Paper 2 OCR + Embed
    Coroutine 3 → Paper 3 OCR + Embed
  ↓
Step 3: Write results           (bulk insert — sequential)
  ↓
Step 4: Publish progress        (Redis Pub/Sub → WebSocket → UI)
  ↓
Repeat for next chunk
```

---

## 24. Smart Caching Layer — Redis

### 24.1 Cache Keys & TTLs

| Data | Cache Key | TTL |
|---|---|---|
| Summaries | `summary:{paper_id}:{mode}` | 24h |
| Q&A sets | `qa:{paper_id}:{mode}` | 24h |
| Translation EN→AR | `trans:en-ar:{paper_id}:{mode}` | 48h |
| Translation AR→EN | `trans:ar-en:{paper_id}:{mode}` | 48h |
| OCR results | `ocr:{paper_id}:{engine}` | 72h |
| Vector search | `search:{query_hash}` | 1h |
| Paper metadata | `paper:meta:{paper_id}` | 12h |
| LLM responses | `llm:{prompt_hash}` | 6h |
| Export files | `export:{result_id}:{format}` | 2h |
| Audio (TTS) | `tts:{text_hash}:{lang}:{provider}` | 4h |

---

### 24.2 Cache Flow

```python
cache_key = f"summary:{paper_id}:{mode}"
cached = await redis.get(cache_key)
if cached:
    return SummaryResult.parse_raw(cached)   # instant

result = await run_summarization(paper_id, mode)
await redis.setex(cache_key, 86400, result.json())
return result
```

---

### 24.3 Redis Pub/Sub (Cross-Service Events)

```
Batch/OCR/Agent Service → redis.publish("paper:processed:{id}", data)
        ↓ subscribers receive event independently
Cache Service   → pre-populate result cache
Chatbot Service → mark paper as available for chat
Notif. Service  → push WebSocket progress to user
```

---

## 25. AI Enhancement: RAG Pipeline

### 25.1 Full Pipeline

```
User question
  ↓
── RETRIEVE ──────────────────────────────────────────────
sentence-transformers → 384-dim query vector
Qdrant ANN search → top 5 relevant paper chunks
  ↓
── AUGMENT ───────────────────────────────────────────────
LangChain: [system] + [retrieved chunks] + [question]
  ↓
── GENERATE ──────────────────────────────────────────────
LiteLLM → provider (OpenAI / Gemini / Claude / Groq / Ollama)
  ↓
── CITE ──────────────────────────────────────────────────
Map response → source chunks → citations
[Paper Title, Page 7, Section 3.2]
  ↓
Cited response returned + saved to PostgreSQL
```

---

### 25.2 Chunking Strategy

| Parameter | Value | Reason |
|---|---|---|
| Chunk size | 500 tokens | Fits context, preserves meaning |
| Overlap | 50 tokens | Prevents concept fragmentation |
| Tokenizer | tiktoken | Accurate LLM token counting |
| Boundary | NLTK sentences | Natural text breaks |

---

## 26. AI Enhancement: Vector Database — Qdrant

### 26.1 Document Structure

```json
{
  "id": "uuid",
  "vector": [0.023, -0.412, "... 384 dims"],
  "payload": {
    "paper_id": "paper_abc123",
    "user_id": "user_xyz789",
    "page_number": 7,
    "section": "Methodology",
    "chunk_index": 14,
    "text": "The study employed a randomized controlled trial...",
    "language": "en",
    "token_count": 487
  }
}
```

### 26.2 Multi-Paper Search

```python
results = await qdrant_client.search(
    collection_name="papers",
    query_vector=query_embedding,
    query_filter=Filter(
        must=[FieldCondition(key="user_id", match=MatchValue(value=user_id))]
    ),
    limit=5
)
```

---

## 27. Real-Time Progress Tracking — WebSockets

### 27.1 Flow

```
User triggers bulk action
  ↓
WebSocket: ws://api/ws/progress/{job_id}
  ↓
Background job processes, publishes after each item:
  Redis.publish("progress:{job_id}", {processed, total, percent, status})
  ↓
Notification Service receives → WebSocket pushes to React
  ↓
React: progress bar + status label update in real time
  ↓
Final: {percent: 100} → toast "Done!"
```

### 27.2 FastAPI WebSocket

```python
@app.websocket("/ws/progress/{job_id}")
async def progress_ws(websocket: WebSocket, job_id: str):
    await websocket.accept()
    pubsub = redis.pubsub()
    await pubsub.subscribe(f"progress:{job_id}")
    try:
        async for message in pubsub.listen():
            if message["type"] == "message":
                await websocket.send_text(message["data"])
    except WebSocketDisconnect:
        await pubsub.unsubscribe(f"progress:{job_id}")
        logger.info("websocket_disconnected", job_id=job_id)
```

---

## 28. Recommended Design Patterns

### Pattern 1: Strategy Pattern
**Problem:** Swappable LLM providers, OCR engines, STT/TTS providers, model vs LLM mode.
**Solution:** Abstract interface + concrete implementations. Selector chooses at runtime.
**Used in:** Summarization, Translation, Q&A, OCR, Voice services.

### Pattern 2: Observer Pattern
**Problem:** Multiple services react to the same event (paper processed, job done).
**Solution:** Redis Pub/Sub as event bus — publishers don't know subscribers.
**Used in:** All services via Redis Pub/Sub.

### Pattern 3: Factory Pattern
**Problem:** Different file types and OCR engines need different processor instantiation.
**Solution:** Factory takes type string, returns correct implementation.
**Used in:** OCR Service (engine), Paper Ingestion (file type).

### Pattern 4: Decorator Pattern
**Problem:** LLM responses need layered enhancement (citations, language, formatting).
**Solution:** Each enhancement wraps the previous — stackable and composable.
**Used in:** Chatbot Service response pipeline.

### Pattern 5: Repository Pattern
**Problem:** Business logic must not contain raw database queries.
**Solution:** Abstract repository interfaces — services call repo methods, not SQL.
**Used in:** Every service.

| Pattern | Type | Applied In | Problem Solved |
|---|---|---|---|
| **Strategy** | Behavioral | All NLP + Voice services | Swappable providers & modes |
| **Observer** | Behavioral | All services (Redis) | Decoupled event reactions |
| **Factory** | Creational | OCR + Ingestion | Provider/type routing |
| **Decorator** | Structural | Chatbot pipeline | Layered response building |
| **Repository** | Architectural | All services | Clean data access |

---

## 29. Deployment — Docker

### 29.1 Container Map

```
docker-compose.yml
├── frontend              ← React (Nginx)
├── gateway               ← FastAPI API Gateway
├── chatbot_service
├── summarization_service
├── translation_service
├── ocr_service
├── qa_service
├── voice_service
├── agent_service
├── export_service
├── postgres              ← PostgreSQL 16
├── qdrant                ← Qdrant vector DB
└── redis                 ← Redis 7
```

---

### 29.2 Docker Compose

```yaml
version: "3.9"

services:

  frontend:
    build: ./frontend
    ports: ["3000:80"]
    depends_on: [gateway]
    networks: [app_network]

  gateway:
    build: ./gateway
    ports: ["8000:8000"]
    env_file: .env
    depends_on: [postgres, redis, qdrant]
    networks: [app_network]

  chatbot_service:
    build: ./services/chatbot_service
    env_file: .env
    depends_on: [postgres, qdrant, redis]
    networks: [app_network]

  summarization_service:
    build: ./services/summarization_service
    env_file: .env
    depends_on: [postgres, redis]
    networks: [app_network]

  translation_service:
    build: ./services/translation_service
    env_file: .env
    depends_on: [postgres, redis]
    networks: [app_network]

  ocr_service:
    build: ./services/ocr_service
    env_file: .env
    depends_on: [postgres]
    networks: [app_network]

  qa_service:
    build: ./services/qa_service
    env_file: .env
    depends_on: [postgres, redis]
    networks: [app_network]

  voice_service:
    build: ./services/voice_service
    env_file: .env
    networks: [app_network]

  agent_service:
    build: ./services/agent_service
    env_file: .env
    depends_on: [postgres, qdrant, redis]
    networks: [app_network]

  export_service:
    build: ./services/export_service
    env_file: .env
    depends_on: [postgres]
    networks: [app_network]

  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: research_assistant
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports: ["5432:5432"]
    networks: [app_network]

  qdrant:
    image: qdrant/qdrant:latest
    ports: ["6333:6333", "6334:6334"]
    volumes:
      - qdrant_data:/qdrant/storage
    networks: [app_network]

  redis:
    image: redis:7-alpine
    ports: ["6379:6379"]
    volumes: [redis_data:/data]
    command: redis-server --appendonly yes
    networks: [app_network]

volumes:
  postgres_data:
  qdrant_data:
  redis_data:

networks:
  app_network:
    driver: bridge
```

---

### 29.3 Service Dockerfile (Standard Template)

```dockerfile
FROM python:3.11-slim
WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc g++ libpq-dev curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

HEALTHCHECK --interval=30s --timeout=10s --start-period=10s \
  CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", \
     "--log-level", "warning"]
```

---

### 29.4 Frontend Dockerfile

```dockerfile
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

---

### 29.5 Environment Variables (.env)

```env
# PostgreSQL
POSTGRES_USER=admin
POSTGRES_PASSWORD=securepassword
POSTGRES_HOST=postgres
POSTGRES_DB=research_assistant
DATABASE_URL=postgresql+asyncpg://admin:securepassword@postgres:5432/research_assistant

# Qdrant
QDRANT_HOST=qdrant
QDRANT_PORT=6333

# Redis
REDIS_URL=redis://redis:6379

# ── LLM Providers ─────────────────────────────────────────
LLM_PROVIDER=groq
OPENAI_API_KEY=sk-...
GEMINI_API_KEY=AI...
ANTHROPIC_API_KEY=sk-ant-...
GROQ_API_KEY=gsk_...
COHERE_API_KEY=...
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_CLOUD_BASE_URL=https://your-ollama-server.com

# LLM settings
LLM_TIMEOUT=30
LLM_MAX_RETRIES=3
LLM_MAX_CONCURRENT=5
LLM_TEMPERATURE=0.3
LLM_MAX_TOKENS=1000

# ── NLP Modes ─────────────────────────────────────────────
SUMMARIZATION_MODE=model
QA_MODE=model
TRANSLATION_EN_AR_MODE=model
TRANSLATION_AR_EN_MODE=model

# ── OCR ───────────────────────────────────────────────────
OCR_ENGINE=paddle
MISTRAL_API_KEY=...
LIGHTON_API_KEY=...
OCR_API_TIMEOUT=60

# ── STT / TTS ─────────────────────────────────────────────
STT_PROVIDER=whisper
TTS_PROVIDER=edge_tts
ELEVENLABS_API_KEY=...
ELEVENLABS_STT_VOICE_AR=your_arabic_voice_id
ELEVENLABS_TTS_VOICE_EN=your_english_voice_id

# ── Rate Limits ───────────────────────────────────────────
RATE_LIMIT_CHAT=30/minute
RATE_LIMIT_SUMMARIZE=10/minute
RATE_LIMIT_TRANSLATE=10/minute
RATE_LIMIT_OCR=5/minute
RATE_LIMIT_STT=20/minute
RATE_LIMIT_TTS=20/minute

# ── Storage ───────────────────────────────────────────────
UPLOAD_DIR=/app/storage/uploads
AGENT_DOWNLOAD_DIR=/app/storage/agent_downloads

# ── App ───────────────────────────────────────────────────
DEBUG=false
SECRET_KEY=your_secret_key_for_jwt
SEMANTIC_SCHOLAR_API_KEY=...
```

---

### 29.6 Commands

```bash
# Build and start all services
docker-compose up --build

# Start in background (detached)
docker-compose up -d

# Run Alembic migrations after startup
docker-compose exec gateway alembic upgrade head

# View logs for a specific service
docker-compose logs -f chatbot_service

# Rebuild a single service after code change
docker-compose up --build summarization_service

# Stop all services
docker-compose down

# Stop and remove all data volumes (full reset)
docker-compose down -v
```

---

### 29.7 GitHub Actions — CI/CD Workflow

The CI/CD pipeline automates testing, building, and pushing Docker images to Docker Hub (or any container registry) on every push or pull request. It runs in two stages: **CI** (test + lint) and **CD** (build + push images).

---

#### Workflow Overview

```
Push to main / Pull Request
        ↓
┌─────────────────────────────────┐
│         CI Stage                │
│  lint → unit tests → security   │
└──────────────┬──────────────────┘
               │ (only on push to main)
┌──────────────▼──────────────────┐
│         CD Stage                │
│  build images → push to registry│
│  → deploy (optional)            │
└─────────────────────────────────┘
```

---

#### Workflow File

```yaml
# .github/workflows/ci-cd.yml

name: CI/CD — Build and Push Docker Images

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

env:
  REGISTRY: docker.io
  IMAGE_PREFIX: ${{ secrets.DOCKERHUB_USERNAME }}/research-paper-assistant

jobs:

  # ────────────────────────────────────────────────────────────
  # JOB 1: Lint & Test (runs on every push and PR)
  # ────────────────────────────────────────────────────────────
  ci:
    name: Lint and Test
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:16-alpine
        env:
          POSTGRES_DB: test_db
          POSTGRES_USER: test_user
          POSTGRES_PASSWORD: test_password
        ports: ["5432:5432"]
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

      redis:
        image: redis:7-alpine
        ports: ["6379:6379"]
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Python 3.11
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"
          cache: "pip"

      - name: Install dependencies
        run: |
          pip install --upgrade pip
          pip install -r requirements-dev.txt

      - name: Run Ruff linter
        run: ruff check . --output-format=github

      - name: Run Black formatter check
        run: black --check .

      - name: Run type checking (mypy)
        run: mypy services/ shared/ --ignore-missing-imports

      - name: Run unit tests
        env:
          DATABASE_URL: postgresql+asyncpg://test_user:test_password@localhost:5432/test_db
          REDIS_URL: redis://localhost:6379
          LLM_PROVIDER: groq
          GROQ_API_KEY: ${{ secrets.GROQ_API_KEY }}
          SUMMARIZATION_MODE: model
          QA_MODE: model
          TRANSLATION_EN_AR_MODE: model
          TRANSLATION_AR_EN_MODE: model
          OCR_ENGINE: paddle
          STT_PROVIDER: whisper
          TTS_PROVIDER: edge_tts
        run: |
          pytest services/ shared/ \
            --cov=services \
            --cov=shared \
            --cov-report=xml \
            --cov-report=term-missing \
            -v

      - name: Upload coverage report
        uses: codecov/codecov-action@v4
        with:
          file: ./coverage.xml
          fail_ci_if_error: false

      - name: Run security scan (bandit)
        run: bandit -r services/ shared/ -ll --exit-zero

      - name: Check for dependency vulnerabilities (safety)
        run: safety check --full-report || true

  # ────────────────────────────────────────────────────────────
  # JOB 2: Build and Push Docker Images (only on push to main)
  # ────────────────────────────────────────────────────────────
  build-and-push:
    name: Build and Push — ${{ matrix.service }}
    runs-on: ubuntu-latest
    needs: ci
    if: github.ref == 'refs/heads/main' && github.event_name == 'push'

    strategy:
      matrix:
        service:
          - gateway
          - chatbot_service
          - summarization_service
          - translation_service
          - ocr_service
          - qa_service
          - voice_service
          - agent_service
          - export_service
          - frontend
      fail-fast: false   # continue building other images even if one fails

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Log in to Docker Hub
        uses: docker/login-action@v3
        with:
          username: ${{ secrets.DOCKERHUB_USERNAME }}
          password: ${{ secrets.DOCKERHUB_TOKEN }}

      - name: Extract metadata (tags and labels)
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ${{ env.IMAGE_PREFIX }}-${{ matrix.service }}
          tags: |
            type=sha,prefix=sha-,format=short
            type=ref,event=branch
            type=raw,value=latest,enable=${{ github.ref == 'refs/heads/main' }}

      - name: Build and push ${{ matrix.service }}
        uses: docker/build-push-action@v5
        with:
          context: ./${{ matrix.service == 'frontend' && 'frontend' || format('services/{0}', matrix.service) }}
          file: ./${{ matrix.service == 'frontend' && 'frontend' || format('services/{0}', matrix.service) }}/Dockerfile
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
          platforms: linux/amd64,linux/arm64

  # ────────────────────────────────────────────────────────────
  # JOB 3: Notify on completion
  # ────────────────────────────────────────────────────────────
  notify:
    name: Notify Result
    runs-on: ubuntu-latest
    needs: [ci, build-and-push]
    if: always()

    steps:
      - name: Report success
        if: needs.build-and-push.result == 'success'
        run: |
          echo "✅ All images built and pushed successfully."
          echo "Images pushed with tags: latest + sha-$(git rev-parse --short HEAD)"

      - name: Report failure
        if: needs.build-and-push.result == 'failure' || needs.ci.result == 'failure'
        run: |
          echo "❌ CI/CD pipeline failed. Check logs above."
          exit 1
```

---

#### Required GitHub Secrets

Set these in your GitHub repository under **Settings → Secrets and variables → Actions**:

| Secret | Description |
|---|---|
| `DOCKERHUB_USERNAME` | Your Docker Hub username |
| `DOCKERHUB_TOKEN` | Docker Hub access token (not password) |
| `GROQ_API_KEY` | Groq API key for running LLM tests in CI |

---

#### Workflow Triggers

| Event | CI Runs | Images Built & Pushed |
|---|---|---|
| Pull Request → `main` | ✅ Yes | ❌ No |
| Push → `develop` | ✅ Yes | ❌ No |
| Push → `main` | ✅ Yes | ✅ Yes |

---

#### Image Tags Produced

For every push to `main`, each service image is tagged with:

```
your-username/research-paper-assistant-chatbot_service:latest
your-username/research-paper-assistant-chatbot_service:main
your-username/research-paper-assistant-chatbot_service:sha-a3f9c12
```

The `sha-` tag allows pinning to an exact commit for rollback.

---

#### requirements-dev.txt (CI dependencies)

```txt
# All production dependencies
-r requirements.txt

# Testing
pytest==7.4.0
pytest-asyncio==0.23.0
pytest-cov==4.1.0
httpx==0.26.0          # for TestClient async

# Code quality
ruff==0.1.9
black==24.1.1
mypy==1.8.0

# Security scanning
bandit==1.7.7
safety==3.0.1
```

---

### 29.8 File Validation & Security

Every file upload goes through a strict multi-layer validation pipeline before any processing begins. Validation happens at the **gateway level** and again inside the **OCR/ingestion service** — defense in depth.

---

#### 29.8.1 Validation Layers

```
File arrives at POST /upload
        ↓
Layer 1: Extension whitelist check       ← reject unknown extensions instantly
        ↓
Layer 2: File size limit check           ← reject oversized files
        ↓
Layer 3: MIME type verification          ← check actual content, not just name
        ↓
Layer 4: Magic bytes (file signature)    ← read first bytes to confirm real type
        ↓
Layer 5: File content integrity check    ← can the file actually be opened/parsed?
        ↓
Layer 6: Malware scan (optional)         ← ClamAV integration if configured
        ↓
File accepted → processing begins
```

---

#### 29.8.2 Allowed File Types

| Extension | MIME Type | Magic Bytes | Max Size |
|---|---|---|---|
| `.pdf` | `application/pdf` | `%PDF` (25 50 44 46) | 50 MB |
| `.docx` | `application/vnd.openxmlformats-officedocument.wordprocessingml.document` | `PK` (50 4B) | 30 MB |
| `.png` | `image/png` | `\x89PNG` | 20 MB |
| `.jpg` / `.jpeg` | `image/jpeg` | `\xFF\xD8\xFF` | 20 MB |
| `.tiff` | `image/tiff` | `II` or `MM` | 30 MB |
| `.bmp` | `image/bmp` | `BM` | 20 MB |
| `.wav` | `audio/wav` | `RIFF` | 25 MB |
| `.webm` | `audio/webm` | `\x1A\x45\xDF\xA3` | 25 MB |

---

#### 29.8.3 File Validator Implementation

```python
# shared/security/file_validator.py

import magic
from pathlib import Path
from fastapi import UploadFile, HTTPException
from shared.logger.logger import get_logger
from shared.error_handler.exceptions import (
    FileTooLargeException,
    UnsupportedFileTypeException,
    CorruptedFileException,
    SuspiciousFileException
)

logger = get_logger(__name__)

# ── Allowed types configuration ────────────────────────────────────────
ALLOWED_EXTENSIONS = {".pdf", ".docx", ".png", ".jpg", ".jpeg", ".tiff", ".bmp"}
AUDIO_EXTENSIONS   = {".wav", ".webm", ".mp3", ".ogg"}

ALLOWED_MIME_TYPES = {
    ".pdf":  "application/pdf",
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ".png":  "image/png",
    ".jpg":  "image/jpeg",
    ".jpeg": "image/jpeg",
    ".tiff": "image/tiff",
    ".bmp":  "image/bmp",
    ".wav":  "audio/wav",
    ".webm": "audio/webm"
}

MAGIC_BYTES = {
    ".pdf":  b"%PDF",
    ".png":  b"\x89PNG",
    ".jpg":  b"\xff\xd8\xff",
    ".jpeg": b"\xff\xd8\xff",
    ".bmp":  b"BM",
    ".wav":  b"RIFF",
}

MAX_FILE_SIZES: dict[str, int] = {
    ".pdf":  50 * 1024 * 1024,   # 50 MB
    ".docx": 30 * 1024 * 1024,   # 30 MB
    ".png":  20 * 1024 * 1024,   # 20 MB
    ".jpg":  20 * 1024 * 1024,
    ".jpeg": 20 * 1024 * 1024,
    ".tiff": 30 * 1024 * 1024,
    ".bmp":  20 * 1024 * 1024,
    ".wav":  25 * 1024 * 1024,   # 25 MB
    ".webm": 25 * 1024 * 1024,
}


class FileValidator:
    """
    Multi-layer file validator.
    Validates extension, size, MIME type, magic bytes, and content integrity.
    Never exposes internal error details to the user.
    """

    async def validate(self, file: UploadFile, context: str = "document") -> bytes:
        """
        Validate file and return its bytes if all checks pass.
        context: "document" | "audio"
        """
        allowed = AUDIO_EXTENSIONS if context == "audio" else ALLOWED_EXTENSIONS

        # ── Layer 1: Extension whitelist ───────────────────────────────
        ext = Path(file.filename or "").suffix.lower()
        if ext not in allowed:
            logger.warning(
                "file_rejected_extension",
                filename=file.filename,
                extension=ext,
                context=context
            )
            raise UnsupportedFileTypeException(
                f"File type '{ext}' is not supported. "
                f"Allowed types: {', '.join(sorted(allowed))}"
            )

        # ── Layer 2: Read file content ─────────────────────────────────
        content = await file.read()
        await file.seek(0)  # reset for downstream processing

        # ── Layer 3: File size limit ───────────────────────────────────
        max_size = MAX_FILE_SIZES.get(ext, 20 * 1024 * 1024)
        size_mb = round(len(content) / 1024 / 1024, 2)
        max_mb  = round(max_size / 1024 / 1024)

        if len(content) > max_size:
            logger.warning(
                "file_rejected_size",
                filename=file.filename,
                size_mb=size_mb,
                max_mb=max_mb
            )
            raise FileTooLargeException(
                f"File is too large ({size_mb} MB). "
                f"Maximum allowed size for {ext} files is {max_mb} MB."
            )

        if len(content) == 0:
            raise CorruptedFileException("The uploaded file is empty.")

        # ── Layer 4: Magic bytes verification ─────────────────────────
        expected_magic = MAGIC_BYTES.get(ext)
        if expected_magic and not content.startswith(expected_magic):
            logger.warning(
                "file_rejected_magic_bytes",
                filename=file.filename,
                extension=ext
            )
            raise SuspiciousFileException(
                "The file content does not match its extension. "
                "Please upload a valid file."
            )

        # ── Layer 5: MIME type check (python-magic) ────────────────────
        detected_mime = magic.from_buffer(content, mime=True)
        expected_mime = ALLOWED_MIME_TYPES.get(ext, "")

        # DOCX files are ZIP-based — python-magic detects them as zip
        docx_mimes = {
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "application/zip"
        }
        mime_valid = (
            detected_mime == expected_mime
            or (ext == ".docx" and detected_mime in docx_mimes)
        )

        if not mime_valid:
            logger.warning(
                "file_rejected_mime",
                filename=file.filename,
                detected_mime=detected_mime,
                expected_mime=expected_mime
            )
            raise SuspiciousFileException(
                "The file appears to be invalid or corrupted. "
                "Please upload a valid file."
            )

        # ── Layer 6: Content integrity ─────────────────────────────────
        await self._verify_content_integrity(content, ext, file.filename)

        logger.info(
            "file_accepted",
            filename=file.filename,
            extension=ext,
            size_mb=size_mb
        )
        return content

    async def _verify_content_integrity(
        self, content: bytes, ext: str, filename: str
    ) -> None:
        """Try to open the file with the appropriate library to confirm it's valid."""
        try:
            if ext == ".pdf":
                import pypdf
                from io import BytesIO
                pypdf.PdfReader(BytesIO(content))

            elif ext == ".docx":
                import docx
                from io import BytesIO
                docx.Document(BytesIO(content))

            elif ext in {".png", ".jpg", ".jpeg", ".tiff", ".bmp"}:
                from PIL import Image
                from io import BytesIO
                img = Image.open(BytesIO(content))
                img.verify()

        except Exception as e:
            logger.warning(
                "file_integrity_failed",
                filename=filename,
                extension=ext,
                error=str(e)
            )
            raise CorruptedFileException(
                "The file appears to be corrupted or unreadable. "
                "Please try uploading the file again."
            )
```

---

#### 29.8.4 New Security Exceptions

```python
# shared/error_handler/exceptions.py  (additions)

class FileTooLargeException(AppBaseException): pass
class UnsupportedFileTypeException(AppBaseException): pass
class CorruptedFileException(AppBaseException): pass
class SuspiciousFileException(AppBaseException): pass
class MissingAPIKeyException(AppBaseException): pass
```

---

#### 29.8.5 Using the Validator in Routes

```python
# ocr_service/routes/ocr_routes.py

from shared.security.file_validator import FileValidator

router = APIRouter(prefix="/ocr", tags=["ocr"])
validator = FileValidator()

@router.post("/extract")
async def extract_text(
    file: UploadFile,
    engine: str = "paddle",
    service: OCRService = Depends()
):
    # Validate before any processing — fail fast
    file_bytes = await validator.validate(file, context="document")

    result = await service.extract(file_bytes, file.filename, engine)
    return result


# voice_service/routes/stt_routes.py
@router.post("/voice/stt")
async def speech_to_text(
    audio: UploadFile,
    language: str = "en",
    service: ASRService = Depends()
):
    audio_bytes = await validator.validate(audio, context="audio")
    transcript = await service.transcribe(audio_bytes, language)
    return {"text": transcript}
```

---

#### 29.8.6 Frontend File Validation (First Defense Layer)

Validation also happens on the frontend before the file is even sent — giving the user instant feedback without a round trip to the server.

```typescript
// frontend/src/utils/fileValidator.ts

const ALLOWED_DOC_TYPES = [
  "application/pdf",
  "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
  "image/png", "image/jpeg", "image/tiff", "image/bmp"
];

const ALLOWED_AUDIO_TYPES = ["audio/wav", "audio/webm", "audio/ogg"];

const MAX_SIZES_MB: Record<string, number> = {
  "application/pdf": 50,
  "application/vnd.openxmlformats-officedocument.wordprocessingml.document": 30,
  "image/png": 20,
  "image/jpeg": 20,
  "image/tiff": 30,
  "image/bmp": 20,
  "audio/wav": 25,
  "audio/webm": 25
};

export interface ValidationResult {
  valid: boolean;
  error?: string;
}

export function validateFile(
  file: File,
  context: "document" | "audio" = "document"
): ValidationResult {
  const allowed = context === "audio" ? ALLOWED_AUDIO_TYPES : ALLOWED_DOC_TYPES;

  // Check MIME type
  if (!allowed.includes(file.type)) {
    return {
      valid: false,
      error: `File type not supported. Allowed: ${allowed.join(", ")}`
    };
  }

  // Check file size
  const maxMB = MAX_SIZES_MB[file.type] ?? 20;
  const fileMB = file.size / 1024 / 1024;
  if (fileMB > maxMB) {
    return {
      valid: false,
      error: `File too large (${fileMB.toFixed(1)} MB). Maximum is ${maxMB} MB.`
    };
  }

  // Check for empty file
  if (file.size === 0) {
    return { valid: false, error: "The file is empty." };
  }

  return { valid: true };
}
```

```typescript
// Usage in upload component
const handleFileSelect = (file: File) => {
  const result = validateFile(file, "document");
  if (!result.valid) {
    toast.error(result.error!);
    return;
  }
  uploadFile(file);
};
```

---

#### 29.8.7 Filename Sanitization

Uploaded filenames are sanitized before storing to prevent path traversal attacks and injection:

```python
# shared/security/filename_sanitizer.py

import re
from pathlib import Path

def sanitize_filename(filename: str) -> str:
    """
    Remove dangerous characters from filenames.
    Prevents path traversal (../../etc/passwd) and injection attacks.
    """
    # Get only the base name — strip any directory components
    name = Path(filename).name

    # Keep only safe characters: letters, digits, dots, hyphens, underscores
    name = re.sub(r"[^\w.\-]", "_", name)

    # Remove leading dots (hidden files on Unix)
    name = name.lstrip(".")

    # Limit filename length
    if len(name) > 255:
        stem = Path(name).stem[:200]
        suffix = Path(name).suffix
        name = stem + suffix

    # Fallback if name becomes empty after sanitization
    if not name or name == Path(name).suffix:
        name = f"uploaded_file{Path(filename).suffix}"

    return name
```

---

#### 29.8.8 Secure File Storage Paths

Files are stored with UUID-based paths — never using the original filename in the storage path:

```python
# shared/storage/file_storage.py

import uuid
from pathlib import Path
from shared.security.filename_sanitizer import sanitize_filename

async def store_file(
    content: bytes,
    original_filename: str,
    user_id: str,
    base_dir: str
) -> dict:
    """
    Store file safely using UUID path.
    Returns storage metadata — original name stored in DB only, not in path.
    """
    paper_id = str(uuid.uuid4())
    safe_name = sanitize_filename(original_filename)
    ext = Path(safe_name).suffix

    # Path uses UUIDs — original name never appears in filesystem path
    storage_path = Path(base_dir) / user_id / paper_id / f"file{ext}"
    storage_path.parent.mkdir(parents=True, exist_ok=True)

    storage_path.write_bytes(content)

    return {
        "paper_id": paper_id,
        "storage_path": str(storage_path),
        "original_filename": safe_name,  # sanitized name stored in DB
        "size_bytes": len(content)
    }
```

---

#### 29.8.9 Validation Summary

| Check | Where | What it catches |
|---|---|---|
| Extension whitelist | Frontend + Backend | Wrong file types |
| File size limit | Frontend + Backend | Oversized uploads |
| Empty file check | Backend | Zero-byte files |
| Magic bytes check | Backend | Extension spoofing (e.g. `.exe` renamed to `.pdf`) |
| MIME type check | Backend | Mismatched content types |
| Content integrity | Backend | Corrupted/unreadable files |
| Filename sanitization | Backend | Path traversal, injection |
| UUID-based storage | Backend | Directory traversal in paths |

---

## 30. Feature-to-Technology Mapping

| Feature | Async | Batch | Redis | Qdrant+RAG | WebSocket | Export |
|---|---|---|---|---|---|---|
| Upload papers | ✅ | ✅ Bulk | ✅ Meta cache | ✅ Embeddings | ✅ Progress | — |
| OCR (Paddle/Mistral/LightOn) | ✅ Page parallel | ✅ Batch | ✅ Result cache | — | ✅ Status | ✅ TXT/DOCX/PDF |
| Summarization | ✅ Per-paper | ✅ Nightly | ✅ Result cache | ✅ RAG input | ✅ Notify | ✅ TXT/DOCX/PDF |
| Translation EN→AR | ✅ Section | ✅ Bulk | ✅ Result cache | — | ✅ Progress | ✅ TXT/DOCX/PDF |
| Translation AR→EN | ✅ Section | ✅ Bulk | ✅ Result cache | — | ✅ Progress | ✅ TXT/DOCX/PDF |
| Q&A Generation | ✅ Parallel | ✅ Bulk | ✅ Result cache | ✅ RAG input | ✅ Notify | ✅ TXT/DOCX/PDF |
| Chat (RAG) | ✅ Async LLM | — | ✅ LLM cache | ✅ Core pipeline | — | — |
| Message Like/Dislike/Copy | — | — | — | — | — | — |
| STT (Whisper/ElevenLabs/Gemini) | ✅ Async | — | — | — | — | — |
| TTS (Edge/ElevenLabs/Gemini) | ✅ Async | — | ✅ Audio cache | — | — | — |
| Paper discovery (CrewAI) | ✅ Async agents | — | ✅ Search cache | ✅ Semantic | ✅ Agent progress | — |
| ETL pipeline | — | ✅ Core | — | ✅ Embeddings | ✅ Job progress | — |
| Cross-service events | — | — | ✅ Pub/Sub | — | ✅ Push client | — |

---

## 31. Information Flow

### 31.1 Chat Flow (Text + Voice)

```
── TEXT INPUT ──────────────────────────────────────────────
User types → Frontend → POST /chat/message {content, session_id}

── VOICE INPUT ─────────────────────────────────────────────
User records audio → POST /voice/stt
  → STT Provider (Whisper / ElevenLabs / Gemini)
  → Transcript returned → POST /chat/message {content, input_type: "voice"}

── RAG PIPELINE ────────────────────────────────────────────
Check Redis: "llm:{prompt_hash}"
  HIT → return cached response instantly
  MISS →
    Query → sentence-transformers → 384-dim vector
    Qdrant search (filtered by user_id)
    Top 5 chunks retrieved
    LangChain: [system] + [chunks] + [question] → prompt
    LiteLLM → configured provider (OpenAI/Gemini/Claude/Groq/Ollama/...)
    Response generated
    Decorator: citations → language → formatting
    Saved to PostgreSQL (chat_messages)
    Saved to Redis (llm cache)

── TEXT OUTPUT ─────────────────────────────────────────────
Response + citations → Frontend → displayed

── VOICE OUTPUT ────────────────────────────────────────────
Response text → POST /voice/tts
  → TTS Provider (Edge-TTS / ElevenLabs / Gemini)
  → Audio bytes → Frontend → HTML5 Audio plays

── MESSAGE ACTIONS ─────────────────────────────────────────
Copy (user msg)      → navigator.clipboard (frontend only)
Copy (assistant msg) → navigator.clipboard (frontend only)
Like                 → PATCH /chat/messages/{id}/like → PostgreSQL
Dislike              → PATCH /chat/messages/{id}/dislike → PostgreSQL
```

---

### 31.2 NLP Tool Request Flow

```
POST /summarize {paper_id, mode: "model"|"llm"}
  ↓
Rate limit check (slowapi) → 429 if exceeded → friendly message
  ↓
Summarization Service:
  1. Check Redis cache "summary:{paper_id}:{mode}"
     HIT → return instantly
  2. Fetch text from PostgreSQL (paper_repo)
     NOT FOUND → PaperNotFoundException → "Paper not found."
  3. ModeSelector → "model" or "llm"
     model → DistilBART local inference
     llm   → LLMClient → LiteLLM → provider
             (rate limiter, timeout, retry handled in LLMClient)
             LLM errors → caught → user-friendly message returned
  4. Save to PostgreSQL (tool_results)
  5. Cache in Redis (24h TTL)
  6. Return SummaryResponse
  ↓
User clicks "Download PDF":
  POST /export/summary/{result_id}?format=pdf
  Export Service fetches content from tool_results
  fpdf2 generates PDF (Arabic font if RTL)
  Response: file bytes with Content-Disposition: attachment
  Browser downloads file
```

---

### 31.3 Agent Discovery Flow

```
POST /agent/discover {query}
  ↓
WebSocket: ws://api/ws/progress/{job_id}
  ↓
CrewAI sequential pipeline:
  keyword_agent  → LLM extracts keywords
    ↓ WS: "Extracting keywords..."
  search_agent   → Semantic Scholar API
    ↓ WS: "Found 23 papers..."
  download_agent → async httpx PDF downloads
    ↓ WS: "Downloading paper 5/23..."
  import_agent   → per paper: OCR → chunk → embed → Qdrant + PostgreSQL
    ↓ WS: "Importing paper 12/23..."
  report_agent   → structured discovery report
    ↓ WS: "Discovery complete!"
  ↓
Papers ready for chat, summarization, Q&A, translation
Report displayed in UI
```

---

## 32. Implementation Checklist

This checklist covers everything needed to go from zero to a fully running system.

### Infrastructure

- [ ] PostgreSQL running and accessible
- [ ] Qdrant running and accessible
- [ ] Redis running and accessible
- [ ] Docker and Docker Compose installed
- [ ] `.env` file created with all required keys
- [ ] Alembic migrations written and tested
- [ ] `alembic upgrade head` executed successfully
- [ ] Qdrant collection created (`papers` collection with 384-dim vectors)

### Shared Modules

- [ ] `shared/logger/` — structlog setup + middleware
- [ ] `shared/llm_client/` — LiteLLM client + provider config
- [ ] `shared/rate_limiter/` — LLM semaphore limiter
- [ ] `shared/error_handler/` — exception hierarchy + global handlers
- [ ] `shared/embedding/` — sentence-transformers wrapper
- [ ] `shared/chunking/` — tiktoken + NLTK chunker

### Services

- [ ] Gateway — routing, auth middleware, rate limiting (slowapi), request logging
- [ ] Chatbot Service — RAG pipeline, chat history, like/dislike/copy actions
- [ ] Summarization Service — model mode (DistilBART) + LLM mode (LiteLLM)
- [ ] Translation Service — EN→AR + AR→EN, model + LLM modes
- [ ] OCR Service — PaddleOCR + Mistral API + LightOnOCR with engine selector
- [ ] Q&A Service — model mode (T5) + LLM mode (LiteLLM)
- [ ] Voice Service — STT (Whisper + ElevenLabs + Gemini) + TTS (Edge-TTS + ElevenLabs + Gemini)
- [ ] Agent Service — CrewAI orchestrator + all 5 agents
- [ ] Export Service — TXT + DOCX + PDF exporters for all tools

### AI & ML

- [ ] sentence-transformers model downloaded and cached
- [ ] DistilBART model downloaded and cached (summarization model mode)
- [ ] T5-small model downloaded and cached (Q&A model mode)
- [ ] MarianNMT EN→AR model downloaded and cached
- [ ] MarianNMT AR→EN model downloaded and cached
- [ ] PaddleOCR model files downloaded
- [ ] Faster Whisper model downloaded (STT)
- [ ] LiteLLM tested with each configured provider
- [ ] Qdrant collection indexed and tested with sample embedding

### Frontend

- [ ] React project initialized with TypeScript
- [ ] Tailwind CSS configured
- [ ] Redux Toolkit store set up
- [ ] Axios client configured with base URL + auth headers
- [ ] Chat UI with message actions (like, dislike, copy)
- [ ] Voice recording (MediaRecorder) + playback (Audio API)
- [ ] WebSocket connection for real-time progress
- [ ] File upload component
- [ ] Export buttons (TXT, DOCX, PDF) on all tool results
- [ ] Arabic RTL layout support (react-i18next)
- [ ] Error toast notifications (react-hot-toast)

### Testing

- [ ] Unit tests for each service layer
- [ ] Repository tests against test database
- [ ] Integration tests for API routes
- [ ] LLM mock for offline testing
- [ ] OCR engine mock for offline testing
- [ ] Load test for rate limiting validation

### CI/CD & GitHub Actions

- [ ] `.github/workflows/ci-cd.yml` created in repository
- [ ] `DOCKERHUB_USERNAME` secret added to GitHub repository
- [ ] `DOCKERHUB_TOKEN` secret added to GitHub repository
- [ ] `GROQ_API_KEY` secret added for CI test runs
- [ ] `requirements-dev.txt` created with ruff, black, mypy, pytest, bandit, safety
- [ ] CI pipeline runs on pull requests (lint + tests only)
- [ ] CD pipeline runs on push to `main` (build + push all images)
- [ ] All 10 service images build successfully in Actions
- [ ] Image tags verified on Docker Hub (latest + sha- tag)
- [ ] Matrix build confirmed: no single service failure blocks others

### File Validation & Security

- [ ] `shared/security/file_validator.py` implemented with all 6 layers
- [ ] `shared/security/filename_sanitizer.py` implemented
- [ ] `shared/storage/file_storage.py` using UUID-based paths
- [ ] New security exceptions added to exception hierarchy
- [ ] `python-magic` and `Pillow` added to requirements.txt
- [ ] File validator used in all upload routes (OCR, papers, voice)
- [ ] Frontend `fileValidator.ts` implemented with type + size checks
- [ ] Extension whitelist tested with disallowed file types (expect rejection)
- [ ] Magic bytes check tested (rename .exe to .pdf — expect rejection)
- [ ] File size limit tested (oversized file — expect friendly error message)
- [ ] Empty file upload tested (expect rejection)
- [ ] Filename sanitization tested with path traversal attempt (`../../etc/passwd`)
- [ ] Storage paths confirmed to use UUIDs (no original filenames in paths)

### Production Readiness

- [ ] All Docker containers build without errors
- [ ] `docker-compose up` starts all services successfully
- [ ] `alembic upgrade head` runs inside gateway container
- [ ] WebSocket connections tested end-to-end
- [ ] File upload and export tested end-to-end
- [ ] Error handling verified (no system errors shown to users)
- [ ] Log output validated (structured JSON format)
- [ ] Rate limits tested (429 responses return friendly messages)
- [ ] GitHub Actions CI passes on a test PR
- [ ] GitHub Actions CD pushes images successfully on merge to main

---

*Research Paper Assistant — Complete Project Guide*
