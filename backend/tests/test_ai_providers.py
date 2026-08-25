import pytest
from app.ai.base import ProviderError
from app.ai.orchestrator import AIOrchestrator
import app.ai.orchestrator as orchestrator_module

class FailingProvider:
    name = "gemini"
    model = "test-gemini"
    def generate_json(self, system_prompt, user_prompt): raise ProviderError("failed")

class WorkingProvider:
    name = "openrouter"
    model = "test-openrouter"
    def generate_json(self, system_prompt, user_prompt): return {"recommendations": []}

def test_orchestrator_falls_back_to_second_provider(monkeypatch):
    monkeypatch.setattr(orchestrator_module, "configured_providers", lambda: [FailingProvider(), WorkingProvider()])
    provider, model, result = AIOrchestrator().generate_json("system", "user")
    assert provider == "openrouter"
    assert model == "test-openrouter"
    assert result == {"recommendations": []}

def test_orchestrator_fails_when_no_provider(monkeypatch):
    monkeypatch.setattr(orchestrator_module, "configured_providers", lambda: [])
    with pytest.raises(ProviderError): AIOrchestrator().generate_json("system", "user")
