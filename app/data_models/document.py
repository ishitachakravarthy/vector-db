from uuid import UUID, uuid4
from pydantic import BaseModel, Field

class Document(BaseModel):
    """A document containing multiple chunks of text."""
    id: UUID = Field(default_factory=uuid4)
    library_id: UUID
    title: str
    chunks: list[UUID] = Field(default_factory=list)

    def __init__(self, **data):
        super().__init__(**data)
        if not self.chunks:
            self.chunks = []

    def get_document_id(self) -> UUID:
        return self.id

    def get_doc_title(self) -> str:
        return self.title
    def get_library_id(self)-> UUID:
        return self.library_id
    def get_all_chunks(self) -> list[UUID]:
        return self.chunks

    def update_doc_title(self, new_doc_title: str) -> None:
        self.title = new_doc_title

    def add_chunk(self, chunk_id: UUID) -> None:
        if chunk_id not in self.chunks:
            self.chunks.append(chunk_id)

    def has_chunk(self, chunk_id: UUID) -> bool:
        return chunk_id in self.chunks

    def delete_chunk(self, chunk_id: UUID) -> bool:
        if chunk_id in self.chunks:
            self.chunks.remove(chunk_id)
            return True
        return False

    def delete_all_chunks(self) -> None:
        self.chunks = []
