"""
Agent Service — 5 CrewAI Agents + Tasks

Implements the full agent pipeline from Section 8:
1. keyword_agent → Extract search keywords from user query via LLM
2. search_agent → Query Semantic Scholar with keywords
3. download_agent → Download discovered PDFs via async httpx
4. import_agent → OCR → chunk → embed → Qdrant + PostgreSQL
5. report_agent → Generate structured discovery report

Pipeline: keyword_agent → search_agent → download_agent → import_agent → report_agent
"""

from crewai import Agent, Task, Crew, Process
from shared.llm_client.client import LLMClient
from shared.llm_client.providers import get_provider_model
from shared.logger.logger import get_logger
from settings import settings

logger = get_logger(__name__)


def _get_llm_model():
    """Get the LiteLLM model string for CrewAI agents."""
    return get_provider_model(settings.LLM_PROVIDER)


# ══════════════════════════════════════════════════════════════
# Agent Definitions
# ══════════════════════════════════════════════════════════════

def create_keyword_agent() -> Agent:
    """8.1 Keyword Agent — extracts precise search keywords from natural language."""
    return Agent(
        role="Keyword Extraction Expert",
        goal="Extract precise, academic search keywords from a user's research description.",
        backstory=(
            "You are an expert at understanding research topics and converting "
            "natural language descriptions into precise academic search keywords "
            "that will yield the most relevant results on Semantic Scholar."
        ),
        verbose=False,
        allow_delegation=False,
        llm=_get_llm_model(),
    )


def create_search_agent() -> Agent:
    """8.2 Search Agent — queries Semantic Scholar with extracted keywords."""
    return Agent(
        role="Academic Paper Searcher",
        goal="Find the most relevant academic papers on Semantic Scholar.",
        backstory=(
            "You are a research librarian who specializes in finding relevant "
            "academic papers. You use the Semantic Scholar API to search for "
            "papers and return structured metadata including titles, authors, "
            "abstracts, and PDF URLs."
        ),
        verbose=False,
        allow_delegation=False,
        llm=_get_llm_model(),
    )


def create_download_agent() -> Agent:
    """8.3 Download Agent — downloads PDFs of discovered papers."""
    return Agent(
        role="Paper Download Specialist",
        goal="Download PDF files of discovered papers reliably.",
        backstory=(
            "You handle downloading PDF files from various academic sources. "
            "You manage retries, handle failures gracefully, and validate "
            "downloaded files to ensure they are valid PDFs."
        ),
        verbose=False,
        allow_delegation=False,
        llm=_get_llm_model(),
    )


def create_import_agent() -> Agent:
    """8.4 Import Agent — runs the full ingestion pipeline on downloaded PDFs."""
    return Agent(
        role="Paper Import Specialist",
        goal="Import downloaded papers into the knowledge base via the full ingestion pipeline.",
        backstory=(
            "You run the complete paper ingestion pipeline: "
            "PDF text extraction → OCR (if needed) → text chunking → "
            "embedding generation → store in Qdrant vector DB + PostgreSQL."
        ),
        verbose=False,
        allow_delegation=False,
        llm=_get_llm_model(),
    )


def create_report_agent() -> Agent:
    """8.5 Report Agent — generates a structured discovery report."""
    return Agent(
        role="Discovery Report Writer",
        goal="Generate a comprehensive discovery report summarizing all found papers.",
        backstory=(
            "You create structured reports summarizing the paper discovery process. "
            "Your reports include: total papers found, successfully imported count, "
            "failed imports, and a ranked list of papers by relevance."
        ),
        verbose=False,
        allow_delegation=False,
        llm=_get_llm_model(),
    )


# ══════════════════════════════════════════════════════════════
# Task Definitions
# ══════════════════════════════════════════════════════════════

def create_keyword_task(agent: Agent) -> Task:
    return Task(
        description=(
            "Extract 3-5 precise academic search keywords from this research query: {query}\n"
            "Return ONLY the keywords as a comma-separated list, nothing else."
        ),
        expected_output="A comma-separated list of 3-5 academic search keywords.",
        agent=agent,
    )


def create_search_task(agent: Agent) -> Task:
    return Task(
        description=(
            "Use the extracted keywords to search Semantic Scholar.\n"
            "For each paper found, collect: title, authors, abstract, year, citation count, and PDF URL.\n"
            "Return the results as a structured list."
        ),
        expected_output="A structured list of paper metadata (title, authors, abstract, year, url).",
        agent=agent,
    )


def create_download_task(agent: Agent) -> Task:
    return Task(
        description=(
            "Download the PDF files for all papers that have available PDF URLs.\n"
            "Validate that each downloaded file is a valid PDF.\n"
            "Report which papers were successfully downloaded and which failed."
        ),
        expected_output="A report of downloaded papers with file paths and any failures.",
        agent=agent,
    )


def create_import_task(agent: Agent) -> Task:
    return Task(
        description=(
            "For each successfully downloaded paper, run the import pipeline:\n"
            "1. Extract text (PDF parsing + OCR fallback)\n"
            "2. Chunk the text into 500-token overlapping segments\n"
            "3. Generate embeddings for each chunk\n"
            "4. Store chunks in Qdrant vector database\n"
            "5. Save paper record to PostgreSQL\n"
            "Report import results for each paper."
        ),
        expected_output="Import results for each paper: success/failure with details.",
        agent=agent,
    )


def create_report_task(agent: Agent) -> Task:
    return Task(
        description=(
            "Generate a comprehensive discovery report including:\n"
            "- Total papers found via Semantic Scholar\n"
            "- Papers successfully downloaded\n"
            "- Papers successfully imported into the knowledge base\n"
            "- Any failures with reasons\n"
            "- Top papers ranked by citation count and relevance"
        ),
        expected_output="A structured discovery report with statistics and ranked paper list.",
        agent=agent,
    )
