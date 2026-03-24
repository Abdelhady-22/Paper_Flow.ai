"""
Shared — Concurrent Processing Utilities (Sections 21-23)

Provides:
1. Simultaneous tool execution (Section 21.3)
2. Batch processing with concurrent chunks (Section 22-23)
3. Combined concurrency + batch processing

All utilities publish progress via Redis Pub/Sub.
"""

import asyncio
from typing import Any, Callable, Coroutine, List, Optional
from shared.logger.logger import get_logger
from shared.progress.tracker import progress_tracker

logger = get_logger(__name__)


# ══════════════════════════════════════════════════════════════
# Section 21.3: Simultaneous Tool Execution
# ══════════════════════════════════════════════════════════════

async def run_tools_simultaneously(
    *coroutines: Coroutine,
    return_exceptions: bool = True,
) -> list:
    """
    Execute multiple NLP tools concurrently.

    Example:
        summary, translation, qa = await run_tools_simultaneously(
            summarization_service.summarize(paper_id, mode="model"),
            translation_service.translate(paper_id, "en-ar", mode="model"),
            qa_service.generate(paper_id, mode="llm"),
        )
    """
    results = await asyncio.gather(*coroutines, return_exceptions=return_exceptions)
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            logger.error("simultaneous_tool_failed", tool_index=i, error=str(result))
    return results


# ══════════════════════════════════════════════════════════════
# Sections 22-23: Batch Processing with Concurrent Chunks
# ══════════════════════════════════════════════════════════════

async def process_batch(
    items: List[Any],
    processor: Callable,
    chunk_size: int = 10,
    task_id: Optional[str] = None,
    task_label: str = "batch",
) -> List[Any]:
    """
    Process a batch of items in concurrent chunks.

    Flow (Section 23):
      1. Read chunk of items (sequential)
      2. Process chunk (asyncio.gather — concurrent)
      3. Write results (sequential)
      4. Publish progress (Redis Pub/Sub → WebSocket → UI)
      5. Repeat for next chunk

    Args:
        items: List of items to process
        processor: Async callable that processes a single item
        chunk_size: Number of items per concurrent chunk
        task_id: Optional task ID for progress tracking
        task_label: Label for progress messages

    Returns:
        List of results (same order as input items)
    """
    total = len(items)
    all_results = []

    for chunk_start in range(0, total, chunk_size):
        chunk_end = min(chunk_start + chunk_size, total)
        chunk = items[chunk_start:chunk_end]

        # Publish progress
        if task_id:
            progress = chunk_start / total
            await progress_tracker.publish(
                task_id,
                "processing",
                progress,
                f"{task_label}: processing {chunk_start + 1}-{chunk_end} of {total}",
            )

        # Process chunk concurrently
        tasks = [processor(item) for item in chunk]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Collect results
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(
                    "batch_item_failed",
                    item_index=chunk_start + i,
                    error=str(result),
                )
                all_results.append(None)
            else:
                all_results.append(result)

    # Final progress
    if task_id:
        await progress_tracker.publish(task_id, "complete", 1.0, f"{task_label}: complete")

    logger.info(
        "batch_complete",
        label=task_label,
        total=total,
        successful=sum(1 for r in all_results if r is not None),
        failed=sum(1 for r in all_results if r is None),
    )

    return all_results


async def process_multiple_papers(
    files: list,
    processor: Callable,
    task_id: Optional[str] = None,
) -> list:
    """
    Parallel paper processing utility (Section 21.1).

    Args:
        files: List of file objects/bytes to process
        processor: Async callable that processes a single file

    Returns:
        List of results
    """
    return await process_batch(
        items=files,
        processor=processor,
        chunk_size=10,
        task_id=task_id,
        task_label="paper_processing",
    )
