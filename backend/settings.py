"""
Research Paper Assistant — Application Settings

Centralized configuration loaded from environment variables via Pydantic Settings.
All services import settings from this module.
"""

from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from .env file."""

    # ── PostgreSQL ────────────────────────────────────────────
    POSTGRES_USER: str = "admin"
    POSTGRES_PASSWORD: str = "securepassword"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "research_assistant"
    DATABASE_URL: str = "postgresql+asyncpg://admin:securepassword@localhost:5432/research_assistant"

    # ── Qdrant ────────────────────────────────────────────────
    QDRANT_HOST: str = "localhost"
    QDRANT_PORT: int = 6333

    # ── Redis ─────────────────────────────────────────────────
    REDIS_URL: str = "redis://localhost:6379"

    # ── LLM Providers ─────────────────────────────────────────
    LLM_PROVIDER: str = "groq"

    # Per-service LLM overrides (fall back to LLM_PROVIDER if not set)
    CHAT_LLM_PROVIDER: Optional[str] = None
    SUMMARIZATION_LLM_PROVIDER: Optional[str] = None
    TRANSLATION_LLM_PROVIDER: Optional[str] = None
    QA_LLM_PROVIDER: Optional[str] = None
    AGENT_LLM_PROVIDER: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    GROQ_API_KEY: Optional[str] = None
    COHERE_API_KEY: Optional[str] = None
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_CLOUD_BASE_URL: Optional[str] = None
    OLLAMA_CLOUD_API_KEY: Optional[str] = None

    # ── LLM Settings ──────────────────────────────────────────
    LLM_TIMEOUT: int = 30
    LLM_MAX_RETRIES: int = 3
    LLM_MAX_CONCURRENT: int = 5
    LLM_TEMPERATURE: float = 0.3
    LLM_MAX_TOKENS: int = 1000

    # ── NLP Modes ─────────────────────────────────────────────
    SUMMARIZATION_MODE: str = "model"
    QA_MODE: str = "model"
    TRANSLATION_EN_AR_MODE: str = "model"
    TRANSLATION_AR_EN_MODE: str = "model"

    # ── OCR ───────────────────────────────────────────────────
    OCR_ENGINE: str = "paddle"
    MISTRAL_API_KEY: Optional[str] = None
    LIGHTON_API_KEY: Optional[str] = None
    OCR_API_TIMEOUT: int = 60

    # ── STT / TTS ─────────────────────────────────────────────
    STT_PROVIDER: str = "whisper"
    TTS_PROVIDER: str = "edge_tts"
    ELEVENLABS_API_KEY: Optional[str] = None
    ELEVENLABS_STT_VOICE_AR: Optional[str] = None
    ELEVENLABS_TTS_VOICE_EN: Optional[str] = None

    # ── Rate Limits ───────────────────────────────────────────
    RATE_LIMIT_CHAT: str = "30/minute"
    RATE_LIMIT_SUMMARIZE: str = "10/minute"
    RATE_LIMIT_TRANSLATE: str = "10/minute"
    RATE_LIMIT_OCR: str = "5/minute"
    RATE_LIMIT_STT: str = "20/minute"
    RATE_LIMIT_TTS: str = "20/minute"

    # ── Storage ───────────────────────────────────────────────
    UPLOAD_DIR: str = "./storage/uploads"
    AGENT_DOWNLOAD_DIR: str = "./storage/agent_downloads"

    # ── App ───────────────────────────────────────────────────
    DEBUG: bool = False
    SECRET_KEY: str = "change-me-in-production"
    SEMANTIC_SCHOLAR_API_KEY: Optional[str] = None

    # ── CORS ──────────────────────────────────────────────────
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5173"

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
        "extra": "ignore",
    }


# Global singleton
settings = Settings()
