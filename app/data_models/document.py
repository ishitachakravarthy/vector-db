from uuid import UUID, uuid4
from pydantic import BaseModel, Field
from app.data_models.metadata import DocumentMetadata


class Document(BaseModel):
    """A document containing multiple chunks of text."""

    id: UUID = Field(default_factory=uuid4)
    library_id: UUID
    title: str
    chunks: list[UUID] = Field(default_factory=list)
    metadata: DocumentMetadata = Field(default_factory=DocumentMetadata)

    def __init__(self, **data):
        super().__init__(**data)
        if not self.chunks:
            self.chunks = []
        if not self.metadata:
            self.metadata = DocumentMetadata()

    def get_document_id(self) -> UUID:
        return self.id

    def get_doc_title(self) -> str:
        return self.title

    def get_library_id(self) -> UUID:
        return self.library_id

    def get_all_chunks(self) -> list[UUID]:
        return self.chunks

    def get_metadata(self) -> DocumentMetadata:
        return self.metadata

    def update_title(self, new_title: str) -> None:
        self.title = new_title
        self.metadata.update_timestamp()

    def update_metadata(self, new_metadata: DocumentMetadata) -> None:
        self.metadata = new_metadata
        self.metadata.update_timestamp()

    def add_chunk(self, chunk_id: UUID) -> None:
        if chunk_id not in self.chunks:
            self.chunks.append(chunk_id)
            self.metadata.update_timestamp()

    def has_chunk(self, chunk_id: UUID) -> bool:
        return chunk_id in self.chunks

    def delete_chunk(self, chunk_id: UUID) -> bool:
        if chunk_id in self.chunks:
            self.chunks.remove(chunk_id)
            self.metadata.update_timestamp()
            return True
        return False

    def delete_all_chunks(self) -> None:
        self.chunks = []
        self.metadata.update_timestamp()
