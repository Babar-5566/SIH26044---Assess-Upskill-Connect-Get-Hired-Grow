"""
Multi-LLM Async Parallel Orchestrator
Skill: agency-software-architect, agency-backend-architect
"""

import asyncio
from typing import Optional, List, Dict, Any
from app.core.config import settings
from app.ai.multi_llm_base import LLMResponse, BaseAsyncLLMClient
from app.ai.openai_adapter import OpenAIAdapter
from app.ai.claude_adapter import ClaudeAdapter
from app.ai.gemini_adapter import GeminiAdapter


class MultiLLMOrchestrator:
    """
    Coordinates concurrent queries across OpenAI, Anthropic Claude, and Google Gemini.
    Provides isolated execution: a failure in one model does not crash or delay other models.
    """

    def __init__(self):
        openai_key = settings.optional_secret(settings.openai_api_key)
        claude_key = settings.optional_secret(settings.anthropic_api_key)
        gemini_key = settings.optional_secret(settings.gemini_api_key)

        self.adapters: Dict[str, BaseAsyncLLMClient] = {
            "openai": OpenAIAdapter(
                api_key=openai_key,
                model=settings.openai_model,
                timeout_seconds=settings.ai_timeout_seconds,
            ),
            "claude": ClaudeAdapter(
                api_key=claude_key,
                model=settings.claude_model,
                timeout_seconds=settings.ai_timeout_seconds,
            ),
            "gemini": GeminiAdapter(
                api_key=gemini_key,
                model=settings.gemini_model,
                timeout_seconds=settings.ai_timeout_seconds,
            ),
        }

    async def compare_all(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
    ) -> List[LLMResponse]:
        """
        Dispatches the user prompt to all three models in PARALLEL using asyncio.gather.
        Collects all outputs and latencies side-by-side with complete error containment.
        """
        tasks = [
            adapter.generate_response(prompt=prompt, system_prompt=system_prompt)
            for adapter in self.adapters.values()
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        normalized_responses: List[LLMResponse] = []
        for (provider_name, adapter), result in zip(self.adapters.items(), results):
            if isinstance(result, Exception):
                normalized_responses.append(
                    LLMResponse(
                        provider=provider_name,
                        model=adapter.model,
                        content="",
                        latency_ms=0,
                        status="ERROR",
                        error_message="Provider request failed. Please retry later.",
                    )
                )
            elif isinstance(result, LLMResponse):
                normalized_responses.append(result)
            else:
                normalized_responses.append(
                    LLMResponse(
                        provider=provider_name,
                        model=adapter.model,
                        content=str(result),
                        latency_ms=0,
                        status="SUCCESS",
                    )
                )

        return normalized_responses

    async def chat_single(
        self,
        provider: str,
        prompt: str,
        system_prompt: Optional[str] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None,
    ) -> LLMResponse:
        """
        Continues a conversation with a single designated model, passing conversation history.
        """
        provider_clean = provider.lower().strip()
        adapter = self.adapters.get(provider_clean)

        if not adapter:
            return LLMResponse(
                provider=provider_clean,
                model="unknown",
                content="",
                latency_ms=0,
                status="ERROR",
                error_message=f"Provider '{provider}' is not recognized. Choose from: openai, claude, gemini.",
            )

        try:
            return await adapter.generate_response(
                prompt=prompt, system_prompt=system_prompt, conversation_history=conversation_history,
            )
        except Exception:
            return LLMResponse(provider=provider_clean, model=adapter.model, content="", latency_ms=0,
                               status="ERROR", error_message="Provider request failed. Please retry later.")

    def get_providers_status(self) -> List[Dict[str, Any]]:
        """Returns the readiness status and configured model for each provider."""
        return [
            {
                "provider": name,
                "model": adapter.model,
                "is_configured": bool(adapter.api_key),
            }
            for name, adapter in self.adapters.items()
        ]


# Singleton instance for dependency injection
multi_llm_orchestrator = MultiLLMOrchestrator()
