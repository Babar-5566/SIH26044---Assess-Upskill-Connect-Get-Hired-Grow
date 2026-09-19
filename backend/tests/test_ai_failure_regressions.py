"""Offline checks for provider failures and secret-safe responses."""
import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest
from pydantic import ValidationError

from app.ai.openai_adapter import OpenAIAdapter
from app.ai.claude_adapter import ClaudeAdapter
from app.ai.multi_llm_orchestrator import MultiLLMOrchestrator
from app.ai.multi_llm_base import LLMResponse
from app.core.config import Settings
from app.rag.embeddings import OpenAIEmbeddingGenerator


@pytest.mark.asyncio
@pytest.mark.parametrize("adapter_type", [OpenAIAdapter, ClaudeAdapter])
@pytest.mark.parametrize("failure", [RuntimeError("private provider details"), asyncio.TimeoutError()])
async def test_sdk_failures_are_safe(adapter_type, failure):
    adapter = adapter_type(api_key="test-key")
    create = AsyncMock(side_effect=failure)
    adapter.client = SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=create)), messages=SimpleNamespace(create=create))
    response = await adapter.generate_response("hello")
    assert response.status == "ERROR"
    assert response.error_message
    assert "private provider details" not in response.error_message


@pytest.mark.asyncio
async def test_comparison_is_parallel_and_contains_failure():
    orchestrator = MultiLLMOrchestrator()
    started = []
    all_started = asyncio.Event()

    async def generate(provider):
        started.append(provider)
        if len(started) == 3:
            all_started.set()
        await all_started.wait()
        if provider == "claude":
            raise RuntimeError("private provider details")
        return LLMResponse(provider=provider, model="test", content="answer", status="SUCCESS")

    for provider, adapter in orchestrator.adapters.items():
        async def respond(provider=provider, **kwargs):
            return await generate(provider)
        adapter.generate_response = respond
    responses = await asyncio.wait_for(orchestrator.compare_all("hello"), timeout=2)
    assert sum(response.status == "SUCCESS" for response in responses) == 2
    assert "private provider details" not in str(responses)
    single = await orchestrator.chat_single("claude", "hello")
    assert single.status == "ERROR"


@pytest.mark.asyncio
async def test_embedding_response_is_ordered_by_input_index():
    generator = OpenAIEmbeddingGenerator("test-key")
    response = SimpleNamespace(data=[SimpleNamespace(index=1, embedding=[0, 1]), SimpleNamespace(index=0, embedding=[1, 0])])
    generator.client = SimpleNamespace(embeddings=SimpleNamespace(create=AsyncMock(return_value=response)))
    assert await generator.generate_embeddings(["first", "second"]) == [[1, 0], [0, 1]]


def test_documented_cors_and_secret_aliases():
    config = Settings(_env_file=None, cors_origins="http://localhost:5173, http://localhost:3000", jwt_secret="local-test-secret")
    assert config.cors_origins == ["http://localhost:5173", "http://localhost:3000"]
    assert config.secret_value == "local-test-secret"


def test_production_disallows_debug_and_placeholder_secrets():
    with pytest.raises(ValidationError):
        Settings(_env_file=None, environment="production", secret_key="change-this-secret-key")
    with pytest.raises(ValidationError):
        Settings(_env_file=None, environment="production", secret_key="a" * 32, debug=True)
