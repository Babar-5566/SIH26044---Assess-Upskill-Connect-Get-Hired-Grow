"""
Anthropic Claude Async Adapter
Skill: agency-software-architect, agency-application-security-engineer
"""

import time
import asyncio
from typing import Optional, List, Dict
import anthropic
from anthropic import AsyncAnthropic
from app.ai.multi_llm_base import BaseAsyncLLMClient, LLMResponse


class ClaudeAdapter(BaseAsyncLLMClient):
    """Production asynchronous adapter for Anthropic Claude models."""

    provider = "claude"

    def __init__(
        self,
        api_key: Optional[str],
        model: str = "claude-3-5-sonnet-20241022",
        timeout_seconds: float = 30.0,
    ):
        super().__init__(api_key, model)
        self.timeout_seconds = timeout_seconds
        self.client = AsyncAnthropic(api_key=api_key) if api_key else None

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
                error_message="Anthropic API key is not configured in environment (.env).",
            )

        # Normalize messages for Anthropic (alternating user/assistant)
        messages: List[Dict[str, str]] = []
        if conversation_history:
            for msg in conversation_history:
                role = msg.get("role", "user")
                if role in ("user", "assistant"):
                    # Avoid back-to-back same role messages
                    if messages and messages[-1]["role"] == role:
                        messages[-1]["content"] += f"\n\n{msg.get('content', '')}"
                    else:
                        messages.append({"role": role, "content": msg.get("content", "")})

        if messages and messages[-1]["role"] == "user":
            messages[-1]["content"] += f"\n\n{prompt}"
        else:
            messages.append({"role": "user", "content": prompt})

        # Anthropic requires first message to be user
        if messages and messages[0]["role"] != "user":
            messages.insert(0, {"role": "user", "content": "Hello."})

        request_kwargs: Dict = {
            "model": self.model,
            "max_tokens": 2048,
            "messages": messages,
            "temperature": 0.7,
        }
        if system_prompt:
            request_kwargs["system"] = system_prompt

        try:
            response = await asyncio.wait_for(
                self.client.messages.create(**request_kwargs),
                timeout=self.timeout_seconds,
            )
            elapsed_ms = int((time.perf_counter() - start_time) * 1000)
            text_blocks = [
                b.text for b in response.content if getattr(b, "type", "") == "text"
            ]
            content = "".join(text_blocks)
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
        except anthropic.AuthenticationError:
            elapsed_ms = int((time.perf_counter() - start_time) * 1000)
            return LLMResponse(
                provider=self.provider,
                model=self.model,
                content="",
                latency_ms=elapsed_ms,
                status="ERROR",
                error_message="Authentication failed: Invalid Anthropic API key.",
            )
        except anthropic.RateLimitError:
            elapsed_ms = int((time.perf_counter() - start_time) * 1000)
            return LLMResponse(
                provider=self.provider,
                model=self.model,
                content="",
                latency_ms=elapsed_ms,
                status="ERROR",
                error_message="Rate limit reached or quota exceeded for Anthropic Claude API.",
            )
        except anthropic.APIError as exc:
            elapsed_ms = int((time.perf_counter() - start_time) * 1000)
            return LLMResponse(
                provider=self.provider,
                model=self.model,
                content="",
                latency_ms=elapsed_ms,
                status="ERROR",
                error_message="Anthropic service unavailable. Please retry later.",
            )
        except Exception as exc:
            elapsed_ms = int((time.perf_counter() - start_time) * 1000)
            return LLMResponse(
                provider=self.provider,
                model=self.model,
                content="",
                latency_ms=elapsed_ms,
                status="ERROR",
                error_message="Claude request failed. Please retry later.",
            )
