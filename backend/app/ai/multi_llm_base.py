"""
Multi-LLM Base Abstraction & Response Contracts
Skill: agency-software-architect, agency-backend-architect
"""

from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class LLMResponse(BaseModel):
    """Normalized response contract across all LLM providers."""
    provider: str = Field(..., description="Provider identifier (openai, claude, gemini)")
    model: str = Field(..., description="Model name/identifier used")
    content: str = Field(default="", description="Generated response content text")
    latency_ms: int = Field(default=0, description="Response time in milliseconds")
    status: str = Field(default="SUCCESS", description="Execution status: SUCCESS | ERROR")
    error_message: Optional[str] = Field(default=None, description="Detailed user-friendly error message if failed")


class BaseAsyncLLMClient(ABC):
    """Abstract interface for asynchronous LLM provider clients."""

    def __init__(self, api_key: Optional[str], model: str):
        self.api_key = api_key
        self.model = model

    @abstractmethod
    async def generate_response(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None,
    ) -> LLMResponse:
        """
        Generate text response asynchronously with isolated error containment.
        Never raises uncaught provider exceptions; encapsulates failures in LLMResponse.
        """
        pass
