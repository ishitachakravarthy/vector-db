from abc import ABC, abstractmethod
from pydantic import BaseModel, Field
from datetime import datetime, timezone

class BaseMetadata(ABC, BaseModel):
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
    )

    def update_timestamp(self) -> None:
        self.updated_at = datetime.now(timezone.utc)

    @abstractmethod
    def get_type(self) -> str:
        pass

class ChunkMetadata(BaseMetadata):
    section: str | None = Field(default="Body", description="Header, Body, Footer")
    order: int | None = Field(default=0, description="Order of the chunk in the document")
    def get_type(self) -> str:
        return "Chunk"

class DocumentMetadata(BaseMetadata):
    author: str | None = Field(default=None, description="Author of the document")
    status: str|None = Field(default="draft", description="Draft, published, archived)")
    def get_type(self) -> str:
        return "Document"

class LibraryMetadata(BaseMetadata):
    is_public: bool = Field(default=False, description="Whether the library is publicly accessible")
    language: str = Field(default="en", description="Primary language")
    def get_type(self) -> str:
        return "Library"
