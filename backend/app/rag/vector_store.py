"""
NumPy-based High-Performance Vector Store & Cosine Similarity Engine
Skill: agency-rag-pipeline-engineer, agency-backend-architect
"""

import os
import json
import tempfile
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
        self.snapshot_file = self.storage_dir / "index.npz"

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
        if self.snapshot_file.exists():
            with np.load(self.snapshot_file, allow_pickle=False) as snapshot:
                matrix = snapshot["matrix"]
                chunks = [DocumentChunk(**chunk) for chunk in json.loads(str(snapshot["metadata"].item()))]
            if chunks:
                self._validate_vectors(matrix, len(chunks))
                self.matrix = matrix
                self.chunks = chunks
            return
        if self.matrix_file.exists() and self.metadata_file.exists():
            try:
                self.matrix = np.load(str(self.matrix_file), allow_pickle=False)
                with open(self.metadata_file, "r", encoding="utf-8") as f:
                    raw_chunks = json.load(f)
                self.chunks = [DocumentChunk(**c) for c in raw_chunks]
                self._validate_vectors(self.matrix, len(self.chunks))
            except Exception:
                raise ValueError("Vector index could not be loaded. Restore the index from backup.") from None

    def persist(self):
        """Publish vectors and metadata together in one atomic snapshot."""
        temporary = None
        try:
            with tempfile.NamedTemporaryFile(dir=self.storage_dir, suffix=".npz", delete=False) as output:
                temporary = Path(output.name)
                np.savez(output, matrix=self.matrix if self.matrix is not None else np.empty((0, 0)),
                         metadata=json.dumps([chunk.model_dump() for chunk in self.chunks], ensure_ascii=False))
                output.flush()
                os.fsync(output.fileno())
            os.replace(temporary, self.snapshot_file)
        finally:
            if temporary is not None:
                temporary.unlink(missing_ok=True)

    @staticmethod
    def _validate_vectors(vectors: np.ndarray, count: int):
        if vectors.ndim != 2 or vectors.shape[0] != count or vectors.shape[1] == 0:
            raise ValueError("Embedding count or dimensions do not match the document chunks.")
        if not np.isfinite(vectors).all() or np.any(np.linalg.norm(vectors, axis=1) < 1e-9):
            raise ValueError("Embeddings must contain finite, nonzero vectors.")

    def _replace(self, chunks, matrix):
        previous = self.chunks, self.matrix
        self.chunks, self.matrix = chunks, matrix
        try:
            self.persist()
        except Exception:
            self.chunks, self.matrix = previous
            raise

    def add_chunks(
        self,
        chunks: List[DocumentChunk],
        embeddings: List[List[float]],
    ):
        """Adds text chunks with corresponding embedding vectors to the index."""
        if not chunks and not embeddings:
            return

        new_vecs = np.array(embeddings, dtype=np.float32)
        self._validate_vectors(new_vecs, len(chunks))
        new_vecs = self._normalize(new_vecs)

        spaces = {chunk.metadata.get("embedding_space") for chunk in [*self.chunks, *chunks]}
        if len(spaces) > 1 or (self.matrix is not None and self.matrix.shape[1] != new_vecs.shape[1]):
            raise ValueError("Embedding configuration differs from the saved index. Restore the original configuration or re-upload documents into a new index.")
        ids = [chunk.chunk_id for chunk in [*self.chunks, *chunks]]
        if len(ids) != len(set(ids)):
            raise ValueError("Duplicate document chunks cannot be indexed.")

        if self.matrix is None or len(self.chunks) == 0:
            self._replace(list(chunks), new_vecs)
        else:
            self._replace([*self.chunks, *chunks], np.vstack([self.matrix, new_vecs]))

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
            self._replace([], None)
        else:
            self._replace([self.chunks[i] for i in keep_indices], self.matrix[keep_indices])
        return deleted_count

    def search(
        self,
        query_vector: List[float],
        top_k: int = 5,
        similarity_threshold: float = 0.65,
        document_id: Optional[str] = None,
        user_id: Optional[str] = None,
        embedding_space: Optional[str] = None,
    ) -> List[Tuple[DocumentChunk, float]]:
        """
        Executes Cosine Similarity search against all indexed vectors.
        Returns top-K chunks that meet or exceed the similarity threshold.
        """
        if self.matrix is None or len(self.chunks) == 0:
            return []

        q = np.array(query_vector, dtype=np.float32)
        if q.ndim != 1 or q.shape[0] != self.matrix.shape[1] or not np.isfinite(q).all() or np.linalg.norm(q) < 1e-9:
            raise ValueError("Query embedding does not match the saved index. Restore the original embedding configuration or re-index documents.")
        if embedding_space is not None and any(chunk.metadata.get("embedding_space") != embedding_space for chunk in self.chunks):
            raise ValueError("Embedding configuration differs from the saved index. Re-index documents before searching.")
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
            if user_id is not None and chunk.metadata.get("user_id") != user_id:
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
        self._replace([], None)
        if self.matrix_file.exists():
            self.matrix_file.unlink(missing_ok=True)
        if self.metadata_file.exists():
            self.metadata_file.unlink(missing_ok=True)


# Singleton instance
vector_store = NumpyVectorStore()
