from uuid import UUID, uuid4
from pydantic import BaseModel, Field
from typing import Optional

from app.data_models.chunk import Chunk

class Document(BaseModel):
    """A document containing multiple chunks of text."""
    id: UUID = Field(default_factory=uuid4)
    title: str
    chunks: dict[UUID, Chunk] = Field(default_factory=dict)

    def __init__(self, **data):
        super().__init__(**data)
        if not self.chunks:
            self.chunks = {}

    def get_doc_id(self) -> UUID:
        return self.id

    def get_doc_title(self) -> str:
        return self.title

    def get_all_chunks(self) -> list[Chunk]:
        return list(self.chunks.values())

    def search_chunk(self, chunk_id: UUID) -> Chunk | None:
        return self.chunks.get(chunk_id)

    def update_doc_title(self, new_doc_title: str) -> None:
        self.title = new_doc_title

    def add_chunk(self, chunk: Chunk) -> None:
        self.chunks[chunk.get_chunk_id()] = chunk

    def delete_chunk(self, chunk_id: UUID) -> bool:
        return self.chunks.pop(chunk_id, None) is not None

    def delete_all_chunks(self) -> None:
        self.chunks = {}
