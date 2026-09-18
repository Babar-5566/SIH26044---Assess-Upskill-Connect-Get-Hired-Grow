"""
Pydantic Schemas for AI Assistant & RAG API
Skill: agency-software-architect, agency-backend-architect
"""

import uuid
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class CompareRequest(BaseModel):
    """Request schema for parallel Multi-LLM query comparison."""
    prompt: str = Field(..., min_length=1, max_length=10000, description="The user question or prompt")
    system_prompt: Optional[str] = Field(default=None, max_length=5000, description="Optional system instructions")


class ChatRequest(BaseModel):
    """Request schema for single-model conversational continuation."""
    prompt: str = Field(..., min_length=1, max_length=10000, description="Follow-up question or message")
    provider: str = Field(default="gemini", description="Selected provider: openai, claude, gemini")
    system_prompt: Optional[str] = Field(default=None, description="Optional system prompt")
    conversation_history: Optional[List[Dict[str, str]]] = Field(
        default_factory=list,
        description="Prior message turns: [{'role': 'user'|'assistant', 'content': '...'}]"
    )


class RAGQueryRequest(BaseModel):
    """Request schema for document-grounded question answering."""
    question: str = Field(..., min_length=1, max_length=2000, description="The question about uploaded documents")
    provider: str = Field(default="gemini", description="LLM to use for answer synthesis: openai, claude, gemini")
    document_id: Optional[str] = Field(default=None, description="Optional filter to scope search to a single document UUID")
    top_k: Optional[int] = Field(default=5, ge=1, le=20, description="Maximum chunks to retrieve")
    similarity_threshold: Optional[float] = Field(default=0.65, ge=0.0, le=1.0, description="Minimum cosine similarity")


class DocumentUploadResponse(BaseModel):
    """Response returned upon successful file ingestion and vectorization."""
    document_id: str
    original_filename: str
    file_type: str
    file_size_bytes: int
    chunk_count: int
    status: str
    message: str


class DocumentListItem(BaseModel):
    """Document summary item for file lists."""
    id: str
    original_filename: str
    file_type: str
    file_size_bytes: int
    chunk_count: int
    status: str
    created_at: str
