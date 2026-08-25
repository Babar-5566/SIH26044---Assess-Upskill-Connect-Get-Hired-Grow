from typing import Protocol

class ProviderError(RuntimeError):
    pass

class AIProvider(Protocol):
    name: str
    model: str
    def generate_json(self, system_prompt: str, user_prompt: str) -> dict: ...
