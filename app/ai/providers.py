import json
from typing import Any
import httpx
from app.ai.base import ProviderError
from app.core.config import settings

def _json_from_text(text: str) -> dict:
    text = text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1].rsplit("```", 1)[0].strip()
    try:
        value = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ProviderError("AI provider returned invalid JSON") from exc
    if not isinstance(value, dict):
        raise ProviderError("AI provider returned a non-object JSON value")
    return value

class GeminiProvider:
    name = "gemini"
    def __init__(self, api_key: str, model: str): self.api_key, self.model = api_key, model
    def generate_json(self, system_prompt: str, user_prompt: str) -> dict:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent"
        payload = {"systemInstruction": {"parts": [{"text": system_prompt}]}, "contents": [{"role": "user", "parts": [{"text": user_prompt}]}], "generationConfig": {"responseMimeType": "application/json", "temperature": 0.2}}
        try:
            response = httpx.post(url, params={"key": self.api_key}, json=payload, timeout=settings.ai_timeout_seconds)
            response.raise_for_status()
            candidates = response.json().get("candidates", [])
            text = candidates[0]["content"]["parts"][0]["text"]
            return _json_from_text(text)
        except (httpx.HTTPError, KeyError, IndexError, TypeError, ValueError) as exc:
            raise ProviderError(f"Gemini request failed: {exc}") from exc

class OpenRouterProvider:
    name = "openrouter"
    def __init__(self, api_key: str, model: str): self.api_key, self.model = api_key, model
    def generate_json(self, system_prompt: str, user_prompt: str) -> dict:
        payload = {"model": self.model, "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}], "response_format": {"type": "json_object"}, "temperature": 0.2}
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json", "HTTP-Referer": "https://skillbridge.ai", "X-Title": "SkillBridge AI"}
        try:
            response = httpx.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload, timeout=settings.ai_timeout_seconds)
            response.raise_for_status()
            text = response.json()["choices"][0]["message"]["content"]
            return _json_from_text(text)
        except (httpx.HTTPError, KeyError, IndexError, TypeError, ValueError) as exc:
            raise ProviderError(f"OpenRouter request failed: {exc}") from exc

def configured_providers() -> list[Any]:
    providers = []
    gemini_key = settings.optional_secret(settings.gemini_api_key)
    router_key = settings.optional_secret(settings.openrouter_api_key)
    if settings.ai_provider.lower() == "gemini" and gemini_key: providers.append(GeminiProvider(gemini_key, settings.gemini_model))
    if router_key: providers.append(OpenRouterProvider(router_key, settings.openrouter_model))
    if settings.ai_provider.lower() == "openrouter" and router_key:
        providers = [OpenRouterProvider(router_key, settings.openrouter_model)] + ([GeminiProvider(gemini_key, settings.gemini_model)] if gemini_key else [])
    return providers
