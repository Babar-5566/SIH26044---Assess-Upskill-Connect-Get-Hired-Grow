"""
RAG Ingestion and Document Schemas
Skill: agency-software-architect, agency-rag-pipeline-engineer
"""

from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field


class ParsedPage(BaseModel):
    """Represents text extracted from a specific page or section."""
    page_number: Optional[int] = Field(default=None, description="1-indexed page number if applicable")
    text: str = Field(..., description="Extracted and normalized text content")


class ParsedDocument(BaseModel):
    """Normalized document extraction container."""
    document_id: str = Field(..., description="Unique UUID for the ingested document")
    original_filename: str = Field(..., description="Original user file name")
    file_type: str = Field(..., description="Extension: pdf, docx, txt")
    total_pages: int = Field(default=1, description="Total pages or structural units extracted")
    pages: List[ParsedPage] = Field(default_factory=list, description="List of parsed pages/sections")


class DocumentChunk(BaseModel):
    """A semantically coherent text chunk ready for vectorization."""
    chunk_id: str = Field(..., description="Globally unique chunk identifier")
    document_id: str = Field(..., description="Parent document UUID")
    chunk_index: int = Field(..., description="0-indexed position within parent document")
    filename: str = Field(..., description="Source document filename")
    page_number: Optional[int] = Field(default=None, description="Page number for citations")
    content: str = Field(..., description="Actual text chunk content")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata for search filtering")
