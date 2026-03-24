"""
Chatbot Service — Citation Mapper

Maps LLM response back to source chunks to generate citations.
Implements the Cite step from the RAG pipeline (Section 25.1).
"""

from typing import List
from services.chatbot_service.models.schemas import Citation


def map_citations(response_text: str, context_chunks: List[dict]) -> List[Citation]:
    """
    Map the LLM response back to source paper chunks to create citations.

    Simple approach: if a significant phrase from a chunk appears in the response,
    include that chunk as a citation.
    """
    citations = []
    seen_paper_ids = set()

    for chunk in context_chunks:
        text = chunk.get("text", "")
        paper_id = chunk.get("paper_id", "")

        # Check if key phrases from this chunk were used in the response
        if not text or not paper_id:
            continue

        # Split chunk into key phrases and check overlap
        words = text.split()
        if len(words) < 5:
            continue

        # Check for significant phrase matches (5-word sequences)
        chunk_used = False
        for i in range(0, len(words) - 5, 3):
            phrase = " ".join(words[i : i + 5]).lower()
            if phrase in response_text.lower():
                chunk_used = True
                break

        # Also check if the response references the source number
        source_idx = context_chunks.index(chunk) + 1
        if f"source {source_idx}" in response_text.lower():
            chunk_used = True

        if chunk_used and paper_id not in seen_paper_ids:
            citations.append(
                Citation(
                    paper_id=paper_id,
                    page_number=chunk.get("page_number"),
                    section=chunk.get("section", ""),
                    text_snippet=text[:200],
                )
            )
            seen_paper_ids.add(paper_id)

    return citations
