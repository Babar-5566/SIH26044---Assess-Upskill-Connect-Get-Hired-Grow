"""
Recursive Semantic Text Chunker
Skill: agency-rag-pipeline-engineer
"""

from typing import List, Optional
from app.rag.schemas import ParsedDocument, DocumentChunk


class RecursiveTextChunker:
    """
    Splits text along semantic boundaries (paragraphs, sentences, clauses, words)
    while preserving token/character context and configurable overlap.
    """

    def __init__(
        self,
        chunk_size: int = 700,
        chunk_overlap: int = 100,
        separators: Optional[List[str]] = None,
    ):
        if chunk_size <= 0 or chunk_overlap < 0 or chunk_overlap >= chunk_size:
            raise ValueError("chunk_overlap must be strictly smaller than chunk_size")
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.separators = separators or ["\n\n", "\n", ". ", "! ", "? ", "; ", " ", ""]

    def split_text(self, text: str) -> List[str]:
        """Split at natural boundaries, with a hard size ceiling and exact overlap."""
        chunks = []
        start = 0
        while start < len(text):
            end = min(start + self.chunk_size, len(text))
            if end < len(text):
                # Prefer paragraphs/sentences, but always advance past the overlap.
                minimum = start + max(self.chunk_overlap + 1, self.chunk_size // 2)
                for separator in self.separators:
                    if not separator:
                        continue
                    boundary = text.rfind(separator, minimum, end)
                    if boundary >= 0:
                        end = boundary + len(separator)
                        break
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            if end == len(text):
                break
            start = end - self.chunk_overlap
        return chunks

    def chunk_document(
        self,
        document: ParsedDocument,
    ) -> List[DocumentChunk]:
        """
        Chunks all pages of a parsed document while preserving page numbers and metadata.
        """
        chunks: List[DocumentChunk] = []
        global_chunk_idx = 0

        for page in document.pages:
            page_text = page.text.strip()
            if not page_text:
                continue

            page_chunks = self.split_text(page_text)
            for chunk_text in page_chunks:
                clean_chunk = chunk_text.strip()
                if not clean_chunk:
                    continue

                chunk_obj = DocumentChunk(
                    chunk_id=f"{document.document_id}_c{global_chunk_idx}",
                    document_id=document.document_id,
                    chunk_index=global_chunk_idx,
                    filename=document.original_filename,
                    page_number=page.page_number,
                    content=clean_chunk,
                    metadata={
                        "filename": document.original_filename,
                        "file_type": document.file_type,
                        "page_number": page.page_number,
                        "document_id": document.document_id,
                        "chunk_index": global_chunk_idx,
                        "char_count": len(clean_chunk),
                    },
                )
                chunks.append(chunk_obj)
                global_chunk_idx += 1

        return chunks
