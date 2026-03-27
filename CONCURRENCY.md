# Concurrency & Parallel Processing in Paper Flow AI

## Architecture Overview

Paper Flow uses **Python's `asyncio`** for all concurrency — there are no threads. The entire backend runs on a single-threaded async event loop (uvicorn + FastAPI), which handles thousands of concurrent I/O operations without thread overhead.

```
┌─────────────────────────────────────────────────────────┐
│                    FastAPI (uvicorn)                     │
│              Single-threaded async event loop            │
├─────────────┬──────────────┬────────────────────────────┤
│  Request 1  │  Request 2   │  Request 3 ...             │
│  (async)    │  (async)     │  (async)                   │
└──────┬──────┴──────┬───────┴────────────┬───────────────┘
       │             │                    │
       ▼             ▼                    ▼
  ┌─────────┐  ┌──────────┐  ┌─────────────────────┐
  │ LLM API │  │ Redis    │  │ Qdrant / PostgreSQL  │
  │ (Groq)  │  │ Pub/Sub  │  │ (async drivers)      │
  └─────────┘  └──────────┘  └─────────────────────┘
```

> **Why no threads?** All heavy operations (LLM calls, DB queries, HTTP downloads) are I/O-bound, not CPU-bound. `asyncio` handles I/O-bound concurrency far more efficiently than threads — zero context-switch overhead, no GIL issues.

---

## 1. Simultaneous Tool Execution

**File:** [`shared/concurrent/batch_executor.py`](file:///d:/Paper_Flow.ai/backend/shared/concurrent/batch_executor.py) → `run_tools_simultaneously()`

Runs multiple NLP services in parallel on the same paper. Instead of doing summarize → translate → QA sequentially (3× latency), they run concurrently (1× latency):

```python
# Sequential: ~9 seconds (3s + 3s + 3s)
summary = await summarize(paper_id)
translation = await translate(paper_id)
qa = await generate_qa(paper_id)

# Concurrent: ~3 seconds (all at once)
summary, translation, qa = await run_tools_simultaneously(
    summarize(paper_id),
    translate(paper_id),
    generate_qa(paper_id),
)
```

**How it works:** `asyncio.gather()` submits all coroutines to the event loop. While one is waiting for an LLM API response, the others are making their own requests. All three network round-trips overlap.

---

## 2. Batch Processing with Chunked Concurrency

**File:** [`shared/concurrent/batch_executor.py`](file:///d:/Paper_Flow.ai/backend/shared/concurrent/batch_executor.py) → `process_batch()`

Processes large item lists in controlled concurrent chunks to avoid overwhelming APIs:

```
Items: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
Chunk size: 4

Round 1: [1,2,3,4]   → asyncio.gather → results → progress: 33%
Round 2: [5,6,7,8]   → asyncio.gather → results → progress: 66%
Round 3: [9,10,11,12] → asyncio.gather → results → progress: 100%
```

Each chunk runs concurrently internally. Chunks run sequentially to control memory/API pressure. Progress is published to Redis Pub/Sub → WebSocket → frontend UI after each chunk.

---

## 3. Page-Level Parallel OCR

**File:** [`services/ocr_service/utils/parallel_ocr.py`](file:///d:/Paper_Flow.ai/backend/services/ocr_service/utils/parallel_ocr.py) → `ocr_large_pdf()`

Splits large PDFs into page chunks and OCRs them concurrently:

```
100-page PDF
    │
    ├── Pages 1-10   → OCR engine ──┐
    ├── Pages 11-20  → OCR engine ──┤
    ├── Pages 21-30  → OCR engine ──┤  asyncio.gather
    ├── ...          → OCR engine ──┤  (all chunks at once)
    └── Pages 91-100 → OCR engine ──┘
                                    │
                              Merge results (ordered)
                                    │
                              Full text output
```

- **Small PDFs** (≤10 pages): processed directly, no splitting
- **Large PDFs** (>10 pages): split with `pypdf`, processed concurrently
- **Fallback**: if parallel OCR fails, falls back to sequential processing

---

## 4. Concurrent Paper Downloads

**File:** [`services/agent_service/utils/pdf_downloader.py`](file:///d:/Paper_Flow.ai/backend/services/agent_service/utils/pdf_downloader.py) → `batch_download_papers()`

When the discovery agent finds 5 papers on Semantic Scholar, it downloads all 5 PDFs simultaneously using `httpx.AsyncClient`:

```python
tasks = [download_paper_pdf(url, title, user_id) for paper in papers]
results = await asyncio.gather(*tasks, return_exceptions=True)
```

Each download runs its own retry loop (3 attempts), validates the PDF header (`%PDF`), and stores to disk — all concurrently.

---

## 5. Concurrent Paper Import Pipeline

**File:** [`services/agent_service/utils/import_pipeline.py`](file:///d:/Paper_Flow.ai/backend/services/agent_service/utils/import_pipeline.py) → `batch_import_papers()`

After downloading, multiple papers are imported into the knowledge base concurrently. Each import runs the full pipeline:

```
Paper A ─→ Extract text → Chunk → Embed → Qdrant + PostgreSQL ─┐
Paper B ─→ Extract text → Chunk → Embed → Qdrant + PostgreSQL ─┤  concurrent
Paper C ─→ Extract text → Chunk → Embed → Qdrant + PostgreSQL ─┘
```

---

## 6. LLM Rate Limiter (Semaphore)

**File:** [`shared/rate_limiter/limiter.py`](file:///d:/Paper_Flow.ai/backend/shared/rate_limiter/limiter.py) → `LLMRateLimiter`

All concurrent LLM calls are guarded by an `asyncio.Semaphore` that limits max concurrent requests (default: 5). This prevents hitting Groq/OpenAI rate limits when batch processing:

```python
class LLMRateLimiter:
    def __init__(self, max_concurrent=5):
        self._semaphore = Semaphore(max_concurrent)

# Usage: only 5 LLM calls can run simultaneously
async with llm_rate_limiter:
    response = await llm.complete(prompt)
```

---

## 7. Real-Time Progress via Redis Pub/Sub

**File:** [`shared/progress/tracker.py`](file:///d:/Paper_Flow.ai/backend/shared/progress/tracker.py)

All concurrent operations report progress in real-time:

```
Service (batch_executor)
    │ publish progress event
    ▼
Redis Pub/Sub (channel: "task_progress")
    │ subscribe + forward
    ▼
WebSocket handler (FastAPI)
    │ send_text
    ▼
Frontend UI (React) → progress bar updates
```

---

## 8. Batch Embeddings (CPU-Bound)

**File:** [`shared/embedding/embedder.py`](file:///d:/Paper_Flow.ai/backend/shared/embedding/embedder.py) → `embed_texts()`

The only CPU-bound operation. Uses `sentence-transformers` batch encoding with `batch_size=32` for efficient GPU/CPU utilization:

```python
embeddings = model.encode(texts, normalize_embeddings=True, batch_size=32)
```

The model is loaded lazily on first use and cached as a singleton — no model reload overhead per request.

---

## Summary Table

| Component | Concurrency Type | Mechanism | Controls |
|-----------|-----------------|-----------|----------|
| Multi-tool execution | I/O parallel | `asyncio.gather` | — |
| Batch processing | Chunked parallel | `asyncio.gather` + chunks | `chunk_size=10` |
| PDF page OCR | I/O parallel | `asyncio.gather` | `chunk_size=10 pages` |
| Paper downloads | I/O parallel | `asyncio.gather` + `httpx` | `max_retries=3` |
| Paper imports | I/O parallel | `asyncio.gather` | — |
| LLM API calls | Rate-limited | `asyncio.Semaphore` | `max_concurrent=5` |
| Progress tracking | Pub/Sub | Redis → WebSocket | — |
| Embeddings | CPU batch | `sentence-transformers` | `batch_size=32` |
| HTTP API | Async event loop | `uvicorn` + `FastAPI` | Worker count |
