"""
Shared — LLM Provider Configuration

Maps friendly provider names to LiteLLM model identifiers.
Additional providers can be added here without code changes elsewhere.
"""

PROVIDER_MODELS = {
    # Cloud providers
    "openai": "openai/gpt-4o-mini",
    "gemini": "gemini/gemini-1.5-flash",
    "claude": "anthropic/claude-3-haiku-20240307",
    "groq": "groq/llama3-8b-8192",
    "cohere": "cohere/command-r",
    # Local via Ollama
    "ollama_llama3": "ollama/llama3",
    "ollama_mistral": "ollama/mistral",
    "ollama_phi3": "ollama/phi3",
    "ollama_gemma2": "ollama/gemma2",
    "ollama_qwen2": "ollama/qwen2",
    # Self-hosted Ollama cloud endpoint
    "ollama_cloud": "openai/llama3",
}


def get_provider_model(provider_key: str) -> str:
    """
    Get the LiteLLM model identifier for a provider key.

    Args:
        provider_key: Friendly name like 'groq', 'openai', 'ollama_llama3'

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
