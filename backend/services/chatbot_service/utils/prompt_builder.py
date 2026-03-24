"""
Chatbot Service — Prompt Builder

Builds the RAG prompt with system message, retrieved context, and conversation history.
Implements the Augment step from the RAG pipeline (Section 25.1).
"""

from typing import List


def build_rag_prompt(
    question: str,
    context_chunks: List[dict],
    history: list = None,
) -> List[dict]:
    """
    Build the message list for the LLM call.

    Args:
        question: The user's question
        context_chunks: Retrieved paper chunks from Qdrant
        history: Previous messages in the conversation

    Returns:
        List of message dicts for LLM completion
    """
    system_message = """You are an expert research paper assistant. Answer questions based ONLY on the provided paper content.

Rules:
1. Only use information from the provided context chunks
2. If the context doesn't contain relevant information, say so clearly
3. Always cite your sources by referencing the paper section or page
4. Be accurate and precise — do not fabricate information
5. Provide comprehensive but concise answers
6. Use academic language appropriate for research discussion"""

    # Build context from retrieved chunks
    if context_chunks:
        context_parts = []
        for i, chunk in enumerate(context_chunks, 1):
            section = chunk.get("section", "Unknown Section")
            page = chunk.get("page_number", "?")
            text = chunk.get("text", "")
            context_parts.append(
                f"[Source {i}] (Section: {section}, Page: {page})\n{text}"
            )
        context_text = "\n\n---\n\n".join(context_parts)
        system_message += f"\n\n=== RETRIEVED PAPER CONTENT ===\n\n{context_text}\n\n=== END CONTENT ==="
    else:
        system_message += "\n\nNote: No relevant paper content was found for this query. Let the user know."

    messages = [{"role": "system", "content": system_message}]

    # Add conversation history (excluding the current message)
    if history:
        for msg in history[:-1]:  # Exclude last (which is the current user msg)
            messages.append({
                "role": msg.role if hasattr(msg, 'role') else "user",
                "content": msg.content if hasattr(msg, 'content') else str(msg),
            })

    # Add current question
    messages.append({"role": "user", "content": question})

    return messages
