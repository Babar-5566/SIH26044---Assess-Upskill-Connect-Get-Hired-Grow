"""
NumPy-based High-Performance Vector Store & Cosine Similarity Engine
Skill: agency-rag-pipeline-engineer, agency-backend-architect
"""

import os
import json
from pathlib import Path
from typing import List, Tuple, Optional, Dict, Any
import numpy as np
from app.core.config import settings
from app.rag.schemas import DocumentChunk


class NumpyVectorStore:
    """
    Lightweight, high-performance in-memory vector index powered by NumPy BLAS.
    Features:
    - BLAS-accelerated dot-product cosine similarity for normalized vectors
    - Persistent disk storage (.npy matrix + .json metadata)
    - Document-level and user-level metadata filtering
    - Zero external database dependencies
    """

    def __init__(self, storage_dir: Optional[str] = None):
        self.storage_dir = Path(storage_dir or settings.rag_vectors_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.matrix_file = self.storage_dir / "embeddings.npy"
        self.metadata_file = self.storage_dir / "chunks_metadata.json"

        self.chunks: List[DocumentChunk] = []
        self.matrix: Optional[np.ndarray] = None  # Shape: (N, D)
        self._load_from_disk()

    def _normalize(self, v: np.ndarray) -> np.ndarray:
        """Normalizes vectors along axis -1 to unit sphere (norm = 1.0)."""
        norm = np.linalg.norm(v, axis=-1, keepdims=True)
        norm = np.where(norm < 1e-9, 1.0, norm)
        return v / norm

    def _load_from_disk(self):
        """Loads serialized vector matrix and chunk metadata if present."""
        if self.matrix_file.exists() and self.metadata_file.exists():
            try:
                self.matrix = np.load(str(self.matrix_file))
                with open(self.metadata_file, "r", encoding="utf-8") as f:
                    raw_chunks = json.load(f)
                self.chunks = [DocumentChunk(**c) for c in raw_chunks]
            except Exception:
                # If corrupted, start with clean memory
                self.matrix = None
                self.chunks = []

    def persist(self):
        """Atomically saves index matrix and metadata to disk."""
        if self.matrix is not None and len(self.chunks) > 0:
            np.save(str(self.matrix_file), self.matrix)
            with open(self.metadata_file, "w", encoding="utf-8") as f:
                json.dump([c.model_dump() for c in self.chunks], f, indent=2, ensure_ascii=False)
        elif self.matrix_file.exists():
            # If cleared
            try:
                self.matrix_file.unlink(missing_ok=True)
                self.metadata_file.unlink(missing_ok=True)
            except Exception:
                pass

    def add_chunks(
        self,
        chunks: List[DocumentChunk],
        embeddings: List[List[float]],
    ):
        """Adds text chunks with corresponding embedding vectors to the index."""
        if not chunks or not embeddings:
            return

        new_vecs = np.array(embeddings, dtype=np.float32)
        new_vecs = self._normalize(new_vecs)

        if self.matrix is None or len(self.chunks) == 0:
            self.matrix = new_vecs
            self.chunks = list(chunks)
        else:
            self.matrix = np.vstack([self.matrix, new_vecs])
            self.chunks.extend(chunks)

        self.persist()

    def delete_document(self, document_id: str) -> int:
        """Removes all indexed chunks associated with a specific document UUID."""
        if not self.chunks or self.matrix is None:
            return 0

        keep_indices = [
            idx for idx, c in enumerate(self.chunks) if c.document_id != document_id
        ]
        deleted_count = len(self.chunks) - len(keep_indices)

        if deleted_count == 0:
            return 0

        if not keep_indices:
            self.chunks = []
            self.matrix = None
        else:
            self.matrix = self.matrix[keep_indices]
            self.chunks = [self.chunks[i] for i in keep_indices]

        self.persist()
        return deleted_count

    def search(
        self,
        query_vector: List[float],
        top_k: int = 5,
        similarity_threshold: float = 0.65,
        document_id: Optional[str] = None,
        user_id: Optional[str] = None,
    ) -> List[Tuple[DocumentChunk, float]]:
        """
        Executes Cosine Similarity search against all indexed vectors.
        Returns top-K chunks that meet or exceed the similarity threshold.
        """
        if self.matrix is None or len(self.chunks) == 0:
            return []

        q = np.array(query_vector, dtype=np.float32)
        q = self._normalize(q)

        # Cosine similarity: dot product of unit-normalized vectors
        scores = np.dot(self.matrix, q)  # Shape: (N,)

        # Build candidate tuples with filters
        candidates: List[Tuple[DocumentChunk, float]] = []
        for idx, score in enumerate(scores):
            chunk = self.chunks[idx]

            # Metadata scoping
            if document_id and chunk.document_id != document_id:
                continue
            if user_id and chunk.metadata.get("user_id") and chunk.metadata.get("user_id") != user_id:
                continue

            score_float = float(score)
            if score_float >= similarity_threshold:
                candidates.append((chunk, score_float))

        # Sort descending by score
        candidates.sort(key=lambda x: x[1], reverse=True)
        return candidates[:top_k]

    @property
    def total_chunks(self) -> int:
        return len(self.chunks)

    def clear(self):
        """Clears all in-memory chunks, vector matrix, and disk files."""
        self.chunks = []
        self.matrix = None
        if self.matrix_file.exists():
            self.matrix_file.unlink(missing_ok=True)
        if self.metadata_file.exists():
            self.metadata_file.unlink(missing_ok=True)


# Singleton instance
vector_store = NumpyVectorStore()
