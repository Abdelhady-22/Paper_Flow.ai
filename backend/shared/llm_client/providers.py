"""
Shared — LLM Provider Configuration

Maps friendly provider names to LiteLLM model identifiers.
Supports multiple API key aliases (e.g. groq_2, groq_3) so each
service can use a separate API key to distribute rate limits.
"""

import os

PROVIDER_MODELS = {
    # Cloud providers
    "openai": "openai/gpt-4o-mini",
    "gemini": "gemini/gemini-1.5-flash",
    "claude": "anthropic/claude-3-haiku-20240307",
    "groq": "groq/llama3-8b-8192",
    "cohere": "cohere/command-r",
    # Groq multi-key aliases (same model, different API keys)
    "groq_2": "groq/llama3-8b-8192",
    "groq_3": "groq/llama3-8b-8192",
    "groq_4": "groq/llama3-8b-8192",
    "groq_5": "groq/llama3-8b-8192",
    # Gemini multi-key aliases
    "gemini_2": "gemini/gemini-1.5-flash",
    # Local via Ollama
    "ollama_llama3": "ollama/llama3",
    "ollama_mistral": "ollama/mistral",
    "ollama_phi3": "ollama/phi3",
    "ollama_gemma2": "ollama/gemma2",
    "ollama_qwen2": "ollama/qwen2",
    # Self-hosted Ollama cloud endpoint
    "ollama_cloud": "openai/llama3",
}

# Maps multi-key aliases to their environment variable names.
# If a provider key is not here, LiteLLM uses its default env var lookup.
PROVIDER_API_KEY_ENV = {
    "groq": "GROQ_API_KEY",
    "groq_2": "GROQ_API_KEY_2",
    "groq_3": "GROQ_API_KEY_3",
    "groq_4": "GROQ_API_KEY_4",
    "groq_5": "GROQ_API_KEY_5",
    "gemini_2": "GEMINI_API_KEY_2",
}


def get_provider_model(provider_key: str) -> str:
    """
    Get the LiteLLM model identifier for a provider key.

    Args:
        provider_key: Friendly name like 'groq', 'groq_2', 'openai'

    Returns:
        LiteLLM model string like 'groq/llama3-8b-8192'

    Raises:
        ValueError: If provider_key is not recognized
    """
    model = PROVIDER_MODELS.get(provider_key)
    if not model:
        raise ValueError(
            f"Unknown LLM provider: {provider_key}. "
            f"Available: {', '.join(PROVIDER_MODELS.keys())}"
        )
    return model


def get_provider_api_key(provider_key: str):
    """
    Get the API key for a provider alias from environment variables.

    Returns None if no custom key mapping exists (LiteLLM will use
    its default env var lookup, e.g. GROQ_API_KEY for 'groq/...' models).
    """
    env_var = PROVIDER_API_KEY_ENV.get(provider_key)
    if env_var:
        return os.getenv(env_var)
    return None
