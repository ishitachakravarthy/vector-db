from uuid import UUID, uuid4
from pydantic import BaseModel, Field
from app.data_models.metadata import DocumentMetadata

from typing import Optional, Dict, Any
from datetime import datetime


class DocumentBase(BaseModel):
    """Base model for document data."""
    title: str = Field(..., description="Title of the document")
    library_id: UUID = Field(..., description="Unique identifier for the library")


class DocumentCreate(DocumentBase):
    """Model for creating a new document."""
    metadata: Optional[DocumentMetadata] = Field(default_factory=DocumentMetadata)


class DocumentUpdate(BaseModel):
    """Model for updating an existing document."""
    title: Optional[str] = None
    metadata: Optional[DocumentMetadata] = None


class DocumentResponse(DocumentBase):
    """Model for document responses."""
    id: UUID = Field(..., description="Unique identifier for the document")
    chunks: list[UUID] = Field(
        default_factory=list, description="List of chunk IDs in the document"
    )
    metadata: DocumentMetadata | None = Field(None, description="Document metadata")
    
    class Config:
        from_attributes = True


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
            self.metadata = {}

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
