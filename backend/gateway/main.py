"""
API Gateway — Main Application

Central entry point for all API requests. Handles:
- Route mounting for all microservices
- CORS configuration
- Rate limiting (slowapi)
- Request logging middleware
- Global exception handlers
- Health check endpoint
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded
from fastapi.responses import JSONResponse

from settings import settings
from shared.logger.logger import setup_logging, get_logger
from shared.logger.middleware import RequestLoggingMiddleware
from shared.error_handler.handler import register_exception_handlers
from shared.rate_limiter.api_limiter import limiter
from infrastructure.postgres.database import close_db
from infrastructure.qdrant.client import init_qdrant, close_qdrant
from infrastructure.redis.client import init_redis, close_redis

# Setup structured logging on import
setup_logging()
logger = get_logger(__name__)

# ── Rate Limiter ──────────────────────────────────────────────
# limiter is imported from shared.rate_limiter.api_limiter

# ── App Initialization ────────────────────────────────────────
app = FastAPI(
    title="Research Paper Assistant",
    description="AI-powered research paper analysis and interaction platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.state.limiter = limiter

# ── Middleware ─────────────────────────────────────────────────
# Cross-Origin Resource Sharing
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request logging
app.add_middleware(RequestLoggingMiddleware)

# ── Exception Handlers ────────────────────────────────────────
register_exception_handlers(app)


# Rate limit exceeded handler
@app.exception_handler(RateLimitExceeded)
async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={
            "error": "Too many requests. Please wait a moment and try again.",
            "success": False,
        },
    )


# ── Lifecycle Events ──────────────────────────────────────────
@app.on_event("startup")
async def startup():
    logger.info("gateway_starting", version="1.0.0", debug=settings.DEBUG)

    # Initialize infrastructure connections
    app.state.qdrant = await init_qdrant()
    app.state.redis = await init_redis()

    logger.info("gateway_started", message="All infrastructure connections ready")


@app.on_event("shutdown")
async def shutdown():
    logger.info("gateway_shutting_down")

    # Close infrastructure connections
    if hasattr(app.state, "qdrant"):
        await close_qdrant(app.state.qdrant)
    if hasattr(app.state, "redis"):
        await close_redis(app.state.redis)
    await close_db()

    logger.info("gateway_stopped")


# ── Health Check ──────────────────────────────────────────────
@app.get("/health", tags=["system"])
async def health_check():
    """Health check endpoint for Docker and monitoring."""
    return {
        "status": "healthy",
        "service": "gateway",
        "version": "1.0.0",
    }


@app.get("/", tags=["system"])
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Research Paper Assistant API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
    }


# ── WebSocket ─────────────────────────────────────────────────
from fastapi import WebSocket
from shared.progress.tracker import websocket_progress_handler


@app.websocket("/ws/progress")
async def progress_ws(websocket: WebSocket):
    """WebSocket endpoint for real-time task progress updates."""
    await websocket_progress_handler(websocket)


# ── Route Mounting ────────────────────────────────────────────
from services.ocr_service.routes.ocr_routes import router as ocr_router
from services.summarization_service.routes.summary_routes import router as summary_router
from services.translation_service.routes.translation_routes import router as translation_router
from services.qa_service.routes.qa_routes import router as qa_router
from services.chatbot_service.routes.chat_routes import router as chat_router
from services.chatbot_service.routes.action_routes import router as action_router
from services.voice_service.routes.voice_routes import router as voice_router
from services.export_service.routes.export_routes import router as export_router
from services.agent_service.routes.agent_routes import router as agent_router

app.include_router(ocr_router, prefix="/api/v1")
app.include_router(summary_router, prefix="/api/v1")
app.include_router(translation_router, prefix="/api/v1")
app.include_router(qa_router, prefix="/api/v1")
app.include_router(chat_router, prefix="/api/v1")
app.include_router(action_router, prefix="/api/v1")
app.include_router(voice_router, prefix="/api/v1")
app.include_router(export_router, prefix="/api/v1")
app.include_router(agent_router, prefix="/api/v1")

