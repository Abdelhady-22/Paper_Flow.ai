"""
Agent Service — Pydantic Schemas
"""

from typing import Optional, List
from pydantic import BaseModel
from uuid import UUID


class PaperSearchRequest(BaseModel):
    query: str
    max_results: int = 5
    fields: Optional[List[str]] = None


class DiscoverRequest(BaseModel):
    """Full discovery pipeline request."""
    query: str
    max_papers: int = 5
    auto_import: bool = True


class DiscoveredPaper(BaseModel):
    title: str
    authors: List[str]
    abstract: Optional[str] = None
    year: Optional[int] = None
    url: Optional[str] = None
    paper_id: Optional[str] = None
    citations: Optional[int] = None


class DiscoveryResponse(BaseModel):
    """Simple search-only response."""
    papers: List[DiscoveredPaper]
    query: str
    total_found: int


class DiscoveryReport(BaseModel):
    """Full pipeline report including download and import results."""
    task_id: str
    query: str
    keywords: str
    papers_found: int
    papers_downloaded: int = 0
    papers_imported: int = 0
    papers: List[DiscoveredPaper] = []
    downloaded: List[dict] = []
    imported: List[dict] = []
    report: str = ""
