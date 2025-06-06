from uuid import UUID, uuid4
from pydantic import BaseModel, Field
from app.data_models.metadata import DocumentMetadata

from typing import Optional, Dict, Any
from datetime import datetime


class DocumentBase(BaseModel):
    title: str = Field(..., description="Title of the document")
    library_id: UUID = Field(..., description="ID of the library this document belongs to")


class DocumentCreate(DocumentBase):
    metadata: DocumentMetadata|None = Field(default=None, description="Document metadata")


class DocumentUpdate(BaseModel):
    title: str|None = Field(default=None, description="New title for the document")
    metadata: DocumentMetadata|None = Field(default=None, description="Updated document metadata")

    def get_title(self) -> str|None:
        return self.title

    def get_metadata(self) -> DocumentMetadata|None:
        return self.metadata


class DocumentResponse(DocumentBase):
    id: UUID = Field(..., description="Unique identifier for the document")
    chunks: list[UUID] = Field(default_factory=list, description="List of chunk IDs in the document")
    metadata: DocumentMetadata = Field(default_factory=DocumentMetadata, description="Document metadata")
    
    class Config:
        from_attributes = True


class Document(BaseModel):
    """A document containing multiple chunks of text."""

    id: UUID = Field(default_factory=uuid4, description="Unique identifier for the document")
    library_id: UUID = Field(..., description="ID of the library this document belongs to")
    title: str = Field(..., description="Title of the document")
    chunks: list[UUID] = Field(default_factory=list, description="List of chunk IDs in the document")
    metadata: DocumentMetadata = Field(default_factory=DocumentMetadata, description="Document metadata")

    def __init__(self, **data):
        super().__init__(**data)
        if not self.chunks:
            self.chunks = []
        if not self.metadata:
            self.metadata = DocumentMetadata()

    def get_document_id(self) -> UUID:
        return self.id

    def get_library_id(self) -> UUID:
        return self.library_id

    def get_all_chunks(self) -> list[UUID]:
        return self.chunks

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

    def delete_chunk(self, chunk_id: UUID) -> bool:
        if chunk_id in self.chunks:
            self.chunks.remove(chunk_id)
            self.metadata.update_timestamp()
            return True
        return False
