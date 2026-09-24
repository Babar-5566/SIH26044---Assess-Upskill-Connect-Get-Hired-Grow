"""
RAG Ingestion and Processing Pipeline
"""

from app.rag.schemas import DocumentChunk, ParsedDocument, ParsedPage
from app.rag.parsers import parse_document, parse_pdf, parse_docx, parse_txt, clean_text
from app.rag.chunker import RecursiveTextChunker
from app.rag.embeddings import BaseEmbeddingGenerator, OpenAIEmbeddingGenerator, DeterministicFallbackEmbeddingGenerator, get_embedding_generator
from app.rag.vector_store import NumpyVectorStore, vector_store
from app.rag.engine import RAGEngine, rag_engine, RAGResponse, CitationSource, INSUFFICIENT_INFO_MESSAGE

__all__ = [
    "DocumentChunk",
    "ParsedDocument",
    "ParsedPage",
    "parse_document",
    "parse_pdf",
    "parse_docx",
    "parse_txt",
    "clean_text",
    "RecursiveTextChunker",
    "BaseEmbeddingGenerator",
    "OpenAIEmbeddingGenerator",
    "DeterministicFallbackEmbeddingGenerator",
    "get_embedding_generator",
    "NumpyVectorStore",
    "vector_store",
    "RAGEngine",
    "rag_engine",
    "RAGResponse",
    "CitationSource",
    "INSUFFICIENT_INFO_MESSAGE",
]


