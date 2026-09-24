"""
Vector Embedding Clients with Batch Processing and Explicit Offline Mode
Skill: agency-rag-pipeline-engineer, agency-software-architect
"""

import hashlib
import asyncio
from abc import ABC, abstractmethod
from typing import List, Optional
import numpy as np
import httpx
from openai import AsyncOpenAI
from app.core.config import settings


class BaseEmbeddingGenerator(ABC):
    """Abstract interface for dense vector embeddings."""

    @property
    def embedding_space(self) -> str:
        return f"{type(self).__name__}:{getattr(self, 'model', getattr(self, 'dimension', 'unknown'))}"

    @abstractmethod
    async def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embedding vectors for a list of text chunks in batches."""
        pass

    @abstractmethod
    async def generate_query_embedding(self, query: str) -> List[float]:
        """Generate embedding vector for a single search query."""
        pass


class OpenAIEmbeddingGenerator(BaseEmbeddingGenerator):
    """Production embedding generator using OpenAI text-embedding-3-small with bounded requests."""

    def __init__(self, api_key: str, model: str = "text-embedding-3-small", batch_size: int = 64):
        base_url = "https://openrouter.ai/api/v1" if api_key.startswith("sk-or-v1") else None
        self.client = AsyncOpenAI(api_key=api_key, base_url=base_url, timeout=settings.ai_timeout_seconds, max_retries=0)
        self.model = model
        self.batch_size = batch_size

    async def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []

        all_embeddings: List[List[float]] = []
        for i in range(0, len(texts), self.batch_size):
            batch = texts[i : i + self.batch_size]
            clean_batch = [t if t.strip() else " " for t in batch]
            try:
                response = await self.client.embeddings.create(
                    input=clean_batch,
                    model=self.model,
                )
                ordered = sorted(response.data, key=lambda item: item.index)
                if [item.index for item in ordered] != list(range(len(batch))):
                    raise ValueError("Embedding response did not match the input batch.")
                batch_vectors = [item.embedding for item in ordered]
                all_embeddings.extend(batch_vectors)
            except Exception:
                raise RuntimeError("Embedding service unavailable. Check provider configuration and retry.") from None

        return all_embeddings

    async def generate_query_embedding(self, query: str) -> List[float]:
        clean_query = query.strip() or " "
        try:
            response = await self.client.embeddings.create(
                input=[clean_query],
                model=self.model,
            )
            return response.data[0].embedding
        except Exception:
            raise RuntimeError("Embedding service unavailable. Check provider configuration and retry.") from None



class DeterministicFallbackEmbeddingGenerator(BaseEmbeddingGenerator):
    """
    Offline deterministic embedding generator for local environments without an active OpenAI key.
    Produces unit-normalized dense vectors (dimension 256) based on sub-word token hashing.
    Enables zero-dependency local testing while preserving cosine similarity ranking.
    """

    def __init__(self, dimension: int = 256):
        self.dimension = dimension

    def _hash_text_to_vector(self, text: str) -> List[float]:
        vec = np.zeros(self.dimension, dtype=np.float32)
        words = text.lower().split()
        if not words:
            vec[0] = 1.0
            return vec.tolist()

        for word in words:
            # Generate deterministic index and sign from word hash
            h = int(hashlib.sha256(word.encode("utf-8")).hexdigest()[:8], 16)
            idx = h % self.dimension
            sign = 1.0 if (h // self.dimension) % 2 == 0 else -1.0
            vec[idx] += sign

        # L2-normalize vector to unit sphere
        norm = np.linalg.norm(vec)
        if norm > 1e-9:
            vec = vec / norm
        else:
            vec[0] = 1.0

        return vec.tolist()

    async def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        return [self._hash_text_to_vector(t) for t in texts]

    async def generate_query_embedding(self, query: str) -> List[float]:
        return self._hash_text_to_vector(query)


class GeminiEmbeddingGenerator(BaseEmbeddingGenerator):
    """
    Production embedding generator using Google Gemini models/gemini-embedding-001.
    Outputs dense vectors; provider failures never switch embedding spaces.
    """

    def __init__(
        self,
        api_key: str,
        model: str = "models/gemini-embedding-001",
        timeout_seconds: float = 30.0,
    ):
        self.api_key = api_key
        self.model = model if model.startswith("models/") else f"models/{model}"
        self.timeout_seconds = timeout_seconds

    async def _embed_single(self, text: str, client: httpx.AsyncClient) -> List[float]:
        clean_text = text.strip() or " "
        url = f"https://generativelanguage.googleapis.com/v1beta/{self.model}:embedContent"
        payload = {
            "model": self.model,
            "content": {"parts": [{"text": clean_text}]},
        }
        res = await client.post(url, headers={"x-goog-api-key": self.api_key}, json=payload)
        res.raise_for_status()
        data = res.json()
        return data["embedding"]["values"]

    async def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []
        try:
            async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
                embeddings = []
                for start in range(0, len(texts), 8):
                    embeddings.extend(await asyncio.gather(*(self._embed_single(t, client) for t in texts[start:start + 8])))
                return embeddings
        except Exception:
            raise RuntimeError("Embedding service unavailable. Check provider configuration and retry.") from None

    async def generate_query_embedding(self, query: str) -> List[float]:
        try:
            async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
                return await self._embed_single(query, client)
        except Exception:
            raise RuntimeError("Embedding service unavailable. Check provider configuration and retry.") from None


def get_embedding_generator() -> BaseEmbeddingGenerator:
    """Factory helper: returns OpenAI if configured, else Gemini if configured, else deterministic fallback."""
    openai_key = settings.optional_secret(settings.openai_api_key)
    if openai_key and not openai_key.startswith("sk-or-v1"):
        return OpenAIEmbeddingGenerator(api_key=openai_key, model=settings.embedding_model)

    gemini_key = settings.optional_secret(settings.gemini_api_key)
    if gemini_key:
        return GeminiEmbeddingGenerator(api_key=gemini_key)

    return DeterministicFallbackEmbeddingGenerator()
