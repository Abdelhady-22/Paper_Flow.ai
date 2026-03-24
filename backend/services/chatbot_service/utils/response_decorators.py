"""
Chatbot Service — Response Decorators (Section 28, Pattern 4)

Implements the Decorator Pattern for the chat response pipeline.
Each decorator wraps the previous, stacking enhancements:

  citations → language → formatting

This makes the pipeline composable and extensible.
"""

from typing import List, Optional, Dict, Any
from shared.logger.logger import get_logger

logger = get_logger(__name__)


class ResponseDecorator:
    """Base decorator for response processing."""

    def __init__(self, wrapped=None):
        self._wrapped = wrapped

    async def process(self, response: str, context: Dict[str, Any]) -> str:
        if self._wrapped:
            response = await self._wrapped.process(response, context)
        return response


class CitationDecorator(ResponseDecorator):
    """
    Adds citation references to the response.
    Maps LLM output back to source chunks with paper references.
    """

    async def process(self, response: str, context: Dict[str, Any]) -> str:
        response = await super().process(response, context)

        citations = context.get("citations", [])
        if not citations:
            return response

        # Append citation references
        citation_lines = ["\n\n---\n**Sources:**"]
        for i, cite in enumerate(citations, 1):
            paper_title = cite.get("paper_title", "Unknown Paper")
            page = cite.get("page_number")
            section = cite.get("section", "")
            ref = f"[{i}] {paper_title}"
            if page:
                ref += f", Page {page}"
            if section:
                ref += f", {section}"
            citation_lines.append(ref)

        return response + "\n".join(citation_lines)


class LanguageDecorator(ResponseDecorator):
    """
    Adjusts response formatting based on language.
    Adds RTL markers for Arabic, adjusts quote style, etc.
    """

    async def process(self, response: str, context: Dict[str, Any]) -> str:
        response = await super().process(response, context)

        language = context.get("language", "en")
        if language == "ar":
            # Add RTL Unicode marker for proper rendering
            response = "\u200F" + response
            logger.debug("response_rtl_marker_added")

        return response


class FormattingDecorator(ResponseDecorator):
    """
    Cleans and formats the response.
    Removes excessive whitespace, normalizes line breaks, etc.
    """

    async def process(self, response: str, context: Dict[str, Any]) -> str:
        response = await super().process(response, context)

        # Remove excessive blank lines
        import re
        response = re.sub(r"\n{3,}", "\n\n", response)

        # Strip leading/trailing whitespace
        response = response.strip()

        return response


def build_response_pipeline() -> ResponseDecorator:
    """
    Build the full response decorator chain.

    Order: Formatting → Language → Citations
    (innermost runs first, outermost runs last)
    """
    pipeline = FormattingDecorator(
        LanguageDecorator(
            CitationDecorator()
        )
    )
    return pipeline
