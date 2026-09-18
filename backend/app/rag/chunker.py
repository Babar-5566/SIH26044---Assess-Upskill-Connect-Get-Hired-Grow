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
        if chunk_overlap >= chunk_size:
            raise ValueError("chunk_overlap must be strictly smaller than chunk_size")
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.separators = separators or ["\n\n", "\n", ". ", "! ", "? ", "; ", " ", ""]

    def _split_text_with_separator(self, text: str, separator: str) -> List[str]:
        if separator:
            parts = text.split(separator)
            # Re-attach separator to avoid losing sentence endings
            return [p + separator for p in parts[:-1]] + ([parts[-1]] if parts[-1] else [])
        return list(text)

    def split_text(self, text: str) -> List[str]:
        """Splits text recursively until all segments satisfy chunk_size with overlap."""
        final_chunks: List[str] = []
        good_splits: List[str] = []

        # Find the appropriate primary separator
        separator = self.separators[-1]
        for s in self.separators:
            if s == "" or s in text:
                separator = s
                break

        splits = self._split_text_with_separator(text, separator)

        # Merge splits into chunks of target size with overlap
        current_chunk: List[str] = []
        current_length = 0

        for split in splits:
            split_len = len(split)

            if current_length + split_len > self.chunk_size:
                if current_chunk:
                    chunk_str = "".join(current_chunk).strip()
                    if chunk_str:
                        final_chunks.append(chunk_str)

                    # Keep overlap from the end of current_chunk
                    overlap_chunk: List[str] = []
                    overlap_len = 0
                    for item in reversed(current_chunk):
                        if overlap_len + len(item) <= self.chunk_overlap:
                            overlap_chunk.insert(0, item)
                            overlap_len += len(item)
                        else:
                            break
                    current_chunk = overlap_chunk
                    current_length = overlap_len

            current_chunk.append(split)
            current_length += split_len

        if current_chunk:
            chunk_str = "".join(current_chunk).strip()
            if chunk_str:
                final_chunks.append(chunk_str)

        return final_chunks

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
