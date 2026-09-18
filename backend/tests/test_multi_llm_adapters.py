"""
Unit test for Multi-LLM provider adapters and async parallel orchestrator.
Skill: agency-software-architect, agency-backend-architect
"""

import pytest
from app.ai.multi_llm_base import LLMResponse
from app.ai.openai_adapter import OpenAIAdapter
from app.ai.claude_adapter import ClaudeAdapter
from app.ai.gemini_adapter import GeminiAdapter
from app.ai.multi_llm_orchestrator import MultiLLMOrchestrator


def test_provider_status():
    """Verify that provider statuses are correctly discovered."""
    orchestrator = MultiLLMOrchestrator()
    statuses = orchestrator.get_providers_status()
    providers = {s["provider"] for s in statuses}
    assert "openai" in providers
    assert "claude" in providers
    assert "gemini" in providers


@pytest.mark.asyncio
async def test_missing_api_key_graceful_handling():
    """Ensure that missing API keys gracefully return ERROR status without crashing."""
    openai_adapter = OpenAIAdapter(api_key=None, model="gpt-4o")
    claude_adapter = ClaudeAdapter(api_key=None, model="claude-3-5-sonnet-20241022")
    gemini_adapter = GeminiAdapter(api_key=None, model="gemini-2.5-flash")

    res_openai = await openai_adapter.generate_response("Hello")
    assert res_openai.status == "ERROR"
    assert "OpenAI API key is not configured" in (res_openai.error_message or "")

    res_claude = await claude_adapter.generate_response("Hello")
    assert res_claude.status == "ERROR"
    assert "Anthropic API key is not configured" in (res_claude.error_message or "")

    res_gemini = await gemini_adapter.generate_response("Hello")
    assert res_gemini.status == "ERROR"
    assert "Google Gemini API key is not configured" in (res_gemini.error_message or "")


@pytest.mark.asyncio
async def test_parallel_compare_all_containment():
    """Ensure parallel compare_all returns exactly 3 results with isolated errors."""
    orchestrator = MultiLLMOrchestrator()
    results = await orchestrator.compare_all("Testing parallel query")
    assert len(results) == 3
    for r in results:
        assert isinstance(r, LLMResponse)
        assert r.provider in ("openai", "claude", "gemini")
        assert r.status in ("SUCCESS", "ERROR")


@pytest.mark.asyncio
async def test_chat_single_invalid_provider():
    """Ensure invalid provider name returns polite error."""
    orchestrator = MultiLLMOrchestrator()
    res = await orchestrator.chat_single("unsupported_provider", "Hello")
    assert res.status == "ERROR"
    assert "not recognized" in (res.error_message or "")
