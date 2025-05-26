from pydantic import BaseModel, Field
from typing import List, Optional

from uuid import UUID, uuid4

from data_models.chunk import Chunk
from data_models.metadata import DocumentMetadata

class Document(BaseModel):
    """A document containing multiple chunks of text."""
    id: UUID = Field(default_factory=uuid4)
    title: str
    chunks: List[Chunk] = Field(default_factory=list)
    metadata: DocumentMetadata

    def __init__(self, **data):
        super().__init__(**data)
        if not self.chunks:
            self.chunks = []

    def add_chunk(self, chunk: Chunk) -> None:
        """Add a new chunk to the document."""
        self.chunks.append(chunk)
    
    def get_chunk(self, chunk_id: UUID) -> Optional[Chunk]:
        """Retrieve a chunk by its ID."""
        for chunk in self.chunks:
            if chunk.id == chunk_id:
                return chunk
        return None
    
    def get_all_chunks(self) -> List[Chunk]:
        """Get all chunks in the document."""
        return self.chunks

    def update_chunk(self, chunk_id: UUID, new_text: str) -> bool:
        """Update a chunk's text and regenerate its embedding."""
        chunk = self.get_chunk(chunk_id)
        if chunk is not None:
            chunk.update_chunk(new_text)
            return True
        return False
    
    def delete_chunk(self, chunk_id: UUID) -> bool:
        """Delete a chunk from the document."""
        for i, chunk in enumerate(self.chunks):
            if chunk.id == chunk_id:
                self.chunks.pop(i)
                return True
        return False