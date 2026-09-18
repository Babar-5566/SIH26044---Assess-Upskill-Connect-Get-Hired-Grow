"""
Google Gemini Async Adapter
Skill: agency-software-architect, agency-backend-architect
"""

import time
import asyncio
from typing import Optional, List, Dict
import httpx
from app.ai.multi_llm_base import BaseAsyncLLMClient, LLMResponse


class GeminiAdapter(BaseAsyncLLMClient):
    """Production asynchronous adapter for Google Gemini models via async REST."""

    provider = "gemini"

    def __init__(
        self,
        api_key: Optional[str],
        model: str = "gemini-3-flash-preview",
        timeout_seconds: float = 30.0,
    ):
        super().__init__(api_key, model)
        self.timeout_seconds = timeout_seconds

    async def generate_response(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None,
    ) -> LLMResponse:
        start_time = time.perf_counter()

        if not self.api_key:
            return LLMResponse(
                provider=self.provider,
                model=self.model,
                content="",
                latency_ms=0,
                status="ERROR",
                error_message="Google Gemini API key is not configured in environment (.env).",
            )

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent"

        contents = []
        if conversation_history:
            for msg in conversation_history:
                role = "user" if msg.get("role") == "user" else "model"
                contents.append({"role": role, "parts": [{"text": msg.get("content", "")}]})

        contents.append({"role": "user", "parts": [{"text": prompt}]})

        payload: Dict = {
            "contents": contents,
            "generationConfig": {
                "temperature": 0.7,
                "maxOutputTokens": 2048,
            },
        }
        if system_prompt:
            payload["systemInstruction"] = {
                "parts": [{"text": system_prompt}]
            }

        try:
            async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
                response = await client.post(
                    url,
                    params={"key": self.api_key},
                    json=payload,
                )

                elapsed_ms = int((time.perf_counter() - start_time) * 1000)

                if response.status_code == 400:
                    return LLMResponse(
                        provider=self.provider,
                        model=self.model,
                        content="",
                        latency_ms=elapsed_ms,
                        status="ERROR",
                        error_message="Bad request: Check Gemini API key validity or model compatibility.",
                    )
                if response.status_code == 429:
                    if self.model != "gemini-3.1-flash-lite":
                        fallback_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.1-flash-lite:generateContent"
                        fallback_res = await client.post(
                            fallback_url,
                            params={"key": self.api_key},
                            json=payload,
                        )
                        if fallback_res.status_code == 200:
                            fb_data = fallback_res.json()
                            fb_candidates = fb_data.get("candidates", [])
                            if fb_candidates:
                                fb_parts = fb_candidates[0].get("content", {}).get("parts", [])
                                fb_content = "".join([p.get("text", "") for p in fb_parts if "text" in p])
                                return LLMResponse(
                                    provider=self.provider,
                                    model="gemini-3.1-flash-lite",
                                    content=fb_content,
                                    latency_ms=int((time.perf_counter() - start_time) * 1000),
                                    status="SUCCESS",
                                )
                    return LLMResponse(
                        provider=self.provider,
                        model=self.model,
                        content="",
                        latency_ms=elapsed_ms,
                        status="ERROR",
                        error_message="Quota or rate limit exceeded for Google Gemini API. Please retry in a few seconds.",
                    )

                response.raise_for_status()
                data = response.json()

                candidates = data.get("candidates", [])
                if not candidates:
                    return LLMResponse(
                        provider=self.provider,
                        model=self.model,
                        content="",
                        latency_ms=elapsed_ms,
                        status="ERROR",
                        error_message="Gemini returned no candidates (possible safety filter block).",
                    )

                parts = candidates[0].get("content", {}).get("parts", [])
                content = parts[0].get("text", "") if parts else ""

                return LLMResponse(
                    provider=self.provider,
                    model=self.model,
                    content=content,
                    latency_ms=elapsed_ms,
                    status="SUCCESS",
                )

        except httpx.TimeoutException:
            elapsed_ms = int((time.perf_counter() - start_time) * 1000)
            return LLMResponse(
                provider=self.provider,
                model=self.model,
                content="",
                latency_ms=elapsed_ms,
                status="ERROR",
                error_message=f"Request timed out after {self.timeout_seconds} seconds.",
            )
        except httpx.HTTPStatusError as exc:
            elapsed_ms = int((time.perf_counter() - start_time) * 1000)
            return LLMResponse(
                provider=self.provider,
                model=self.model,
                content="",
                latency_ms=elapsed_ms,
                status="ERROR",
                error_message=f"Gemini HTTP {exc.response.status_code}: {exc.response.text[:150]}",
            )
        except Exception as exc:
            elapsed_ms = int((time.perf_counter() - start_time) * 1000)
            return LLMResponse(
                provider=self.provider,
                model=self.model,
                content="",
                latency_ms=elapsed_ms,
                status="ERROR",
                error_message=f"Unexpected Gemini error: {str(exc)}",
            )
