from app.ai.base import ProviderError
from app.ai.providers import configured_providers
from app.core.config import settings

class AIOrchestrator:
    def generate_json(self, system_prompt: str, user_prompt: str) -> tuple[str, str, dict]:
        errors = []
        for provider in configured_providers():
            for _ in range(max(1, settings.ai_max_retries + 1)):
                try: return provider.name, provider.model, provider.generate_json(system_prompt, user_prompt)
                except ProviderError as exc: errors.append(f"{provider.name}: {exc}")
        raise ProviderError("; ".join(errors) if errors else "No AI provider is configured")
