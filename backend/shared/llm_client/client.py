"""
Shared — LiteLLM Unified LLM Client

Single interface to call any LLM provider. The application never calls
OpenAI, Gemini, or Claude SDKs directly — everything goes through LiteLLM.
Switching providers requires only a config change.

Includes: rate limiting, timeout, retry, and error handling.
"""

import litellm
from litellm import acompletion
from typing import Optional, List
from shared.logger.logger import get_logger
from shared.rate_limiter.limiter import llm_rate_limiter
from shared.error_handler.exceptions import (
    LLMRateLimitException,
    LLMTimeoutException,
    LLMAuthException,
    LLMServiceException,
)

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
        max_tokens: int = 1000,
    ) -> str:
        """
        Send a completion request to the configured LLM provider.

        Args:
            prompt: The user prompt to send
            system: Optional system message
            temperature: Sampling temperature (0.0 - 1.0)
            max_tokens: Maximum response tokens

        Returns:
            The LLM response content as a string
        """
        messages: List[dict] = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        await llm_rate_limiter.acquire()

        try:
            logger.info(
                "llm_request",
                provider=self.provider,
                prompt_len=len(prompt),
            )

            response = await acompletion(
                model=self.provider,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                timeout=self.timeout,
                num_retries=self.max_retries,
            )

            content = response.choices[0].message.content
            logger.info(
                "llm_response",
                provider=self.provider,
                tokens=response.usage.total_tokens if response.usage else 0,
            )
            return content

        except litellm.exceptions.RateLimitError as e:
            logger.warning(
                "llm_rate_limit",
                provider=self.provider,
                error=str(e),
            )
            raise LLMRateLimitException(
                "LLM rate limit reached. Please try again shortly."
            )

        except litellm.exceptions.Timeout as e:
            logger.error(
                "llm_timeout",
                provider=self.provider,
                timeout=self.timeout,
            )
            raise LLMTimeoutException(
                "The AI request timed out. Please try again."
            )

        except litellm.exceptions.AuthenticationError as e:
            logger.error("llm_auth_error", provider=self.provider)
            raise LLMAuthException(
                "LLM provider authentication failed."
            )

        except Exception as e:
            logger.error(
                "llm_unexpected_error",
                provider=self.provider,
                error=str(e),
            )
            raise LLMServiceException(
                "The AI service is temporarily unavailable."
            )
        finally:
            llm_rate_limiter.release()

    async def complete_chat(
        self,
        messages: List[dict],
        temperature: float = 0.3,
        max_tokens: int = 1000,
    ) -> str:
        """
        Send a multi-turn chat completion request.
        Used by RAG pipeline where messages include system + context + history.
        """
        await llm_rate_limiter.acquire()

        try:
            logger.info(
                "llm_chat_request",
                provider=self.provider,
                message_count=len(messages),
            )

            response = await acompletion(
                model=self.provider,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                timeout=self.timeout,
                num_retries=self.max_retries,
            )

            content = response.choices[0].message.content
            logger.info(
                "llm_chat_response",
                provider=self.provider,
                tokens=response.usage.total_tokens if response.usage else 0,
            )
            return content

        except litellm.exceptions.RateLimitError:
            raise LLMRateLimitException(
                "LLM rate limit reached. Please try again shortly."
            )
        except litellm.exceptions.Timeout:
            raise LLMTimeoutException(
                "The AI request timed out. Please try again."
            )
        except litellm.exceptions.AuthenticationError:
            raise LLMAuthException(
                "LLM provider authentication failed."
            )
        except Exception as e:
            logger.error("llm_chat_error", provider=self.provider, error=str(e))
            raise LLMServiceException(
                "The AI service is temporarily unavailable."
            )
        finally:
            llm_rate_limiter.release()
