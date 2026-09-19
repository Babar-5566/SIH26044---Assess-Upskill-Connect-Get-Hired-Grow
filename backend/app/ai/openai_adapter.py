"""
OpenAI Async Adapter
Skill: agency-software-architect, agency-application-security-engineer
"""

import time
import asyncio
from typing import Optional, List, Dict
import openai
from openai import AsyncOpenAI
from app.ai.multi_llm_base import BaseAsyncLLMClient, LLMResponse


class OpenAIAdapter(BaseAsyncLLMClient):
    """Production asynchronous adapter for OpenAI models."""

    provider = "openai"

    def __init__(self, api_key: Optional[str], model: str = "gpt-4o", timeout_seconds: float = 30.0):
        super().__init__(api_key, model)
        self.timeout_seconds = timeout_seconds
        self.client = AsyncOpenAI(api_key=api_key) if api_key else None

    async def generate_response(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None,
    ) -> LLMResponse:
        start_time = time.perf_counter()

        if not self.api_key or not self.client:
            return LLMResponse(
                provider=self.provider,
                model=self.model,
                content="",
                latency_ms=0,
                status="ERROR",
                error_message="OpenAI API key is not configured in environment (.env).",
            )

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        if conversation_history:
            for msg in conversation_history:
                role = msg.get("role", "user")
                if role in ("user", "assistant", "system"):
                    messages.append({"role": role, "content": msg.get("content", "")})

        messages.append({"role": "user", "content": prompt})

        try:
            response = await asyncio.wait_for(
                self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=0.7,
                ),
                timeout=self.timeout_seconds,
            )
            elapsed_ms = int((time.perf_counter() - start_time) * 1000)
            content = response.choices[0].message.content or ""
            if not content.strip():
                raise ValueError("Provider returned no text")

            return LLMResponse(
                provider=self.provider,
                model=self.model,
                content=content,
                latency_ms=elapsed_ms,
                status="SUCCESS",
            )

        except asyncio.TimeoutError:
            elapsed_ms = int((time.perf_counter() - start_time) * 1000)
            return LLMResponse(
                provider=self.provider,
                model=self.model,
                content="",
                latency_ms=elapsed_ms,
                status="ERROR",
                error_message=f"Request timed out after {self.timeout_seconds} seconds.",
            )
        except openai.AuthenticationError:
            elapsed_ms = int((time.perf_counter() - start_time) * 1000)
            return LLMResponse(
                provider=self.provider,
                model=self.model,
                content="",
                latency_ms=elapsed_ms,
                status="ERROR",
                error_message="Authentication failed: Invalid OpenAI API key.",
            )
        except openai.RateLimitError:
            elapsed_ms = int((time.perf_counter() - start_time) * 1000)
            return LLMResponse(
                provider=self.provider,
                model=self.model,
                content="",
                latency_ms=elapsed_ms,
                status="ERROR",
                error_message="Rate limit reached or quota exceeded for OpenAI API.",
            )
        except openai.APIError as exc:
            elapsed_ms = int((time.perf_counter() - start_time) * 1000)
            return LLMResponse(
                provider=self.provider,
                model=self.model,
                content="",
                latency_ms=elapsed_ms,
                status="ERROR",
                error_message="OpenAI service unavailable. Please retry later.",
            )
        except Exception as exc:
            elapsed_ms = int((time.perf_counter() - start_time) * 1000)
            return LLMResponse(
                provider=self.provider,
                model=self.model,
                content="",
                latency_ms=elapsed_ms,
                status="ERROR",
                error_message="OpenAI request failed. Please retry later.",
            )
