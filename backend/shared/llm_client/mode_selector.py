"""
Shared — NLP Mode Selector

Selects between 'model' mode (local ML model) and 'llm' mode (cloud LLM via LiteLLM).
Each NLP service (summarization, Q&A, translation) can be configured independently.
"""

import os
from typing import Optional
from shared.error_handler.exceptions import InvalidModeException


class ModeSelector:
    """Selects the processing mode ('model' or 'llm') for NLP services."""

    VALID_MODES = ("model", "llm")

    def get_strategy(
        self, service: str, override_mode: Optional[str] = None
    ) -> str:
        """
        Get the processing mode for a service.

        Args:
            service: Service name (e.g. 'summarization', 'qa', 'translation_en_ar')
            override_mode: Optional override passed from the API request

        Returns:
            'model' or 'llm'

        Raises:
            InvalidModeException: If mode is not 'model' or 'llm'
        """
        mode = override_mode or os.getenv(f"{service.upper()}_MODE", "model")
        if mode not in self.VALID_MODES:
            raise InvalidModeException(
                user_message=f"Invalid processing mode: '{mode}'. Use 'model' or 'llm'.",
                internal_detail=f"Service={service}, requested_mode={mode}",
            )
        return mode
