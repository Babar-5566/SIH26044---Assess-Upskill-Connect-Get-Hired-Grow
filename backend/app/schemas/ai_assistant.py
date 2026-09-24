"""
Pydantic Schemas for AI Assistant & RAG API
Skill: agency-software-architect, agency-backend-architect
"""

import uuid
from typing import Optional, List, Literal, Annotated
from pydantic import BaseModel, Field, ConfigDict, StringConstraints

Provider = Literal["openai", "claude", "gemini"]
MessageText = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=10000)]


class ConversationMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: MessageText


class CompareRequest(BaseModel):
    """Request schema for parallel Multi-LLM query comparison."""
    model_config = ConfigDict(str_strip_whitespace=True)
    prompt: MessageText
    system_prompt: Optional[str] = Field(default=None, max_length=5000, description="Optional system instructions")


class ChatRequest(BaseModel):
    """Request schema for single-model conversational continuation."""
    prompt: MessageText
    provider: Provider = "gemini"
    system_prompt: Optional[str] = Field(default=None, max_length=5000, description="Optional system prompt")
    conversation_history: List[ConversationMessage] = Field(
        default_factory=list,
        max_length=100,
        description="Prior message turns: [{'role': 'user'|'assistant', 'content': '...'}]"
    )


class RAGQueryRequest(BaseModel):
    """Request schema for document-grounded question answering."""
    model_config = ConfigDict(str_strip_whitespace=True)
    question: str = Field(..., min_length=1, max_length=2000, description="The question about uploaded documents")
    provider: Provider = "gemini"
    document_id: Optional[uuid.UUID] = None
    top_k: Optional[int] = Field(default=None, ge=1, le=20, description="Maximum chunks to retrieve")
    similarity_threshold: Optional[float] = Field(default=None, ge=0.0, le=1.0, description="Minimum cosine similarity")


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
