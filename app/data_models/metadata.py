from abc import ABC, abstractmethod
from pydantic import BaseModel, Field
from datetime import datetime, timezone

class BaseMetadata(ABC, BaseModel):
    """Abstract base class for all metadata types."""
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="When the item was created",
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="When the item was last updated",
    )

    def update_timestamp(self) -> None:
        """Update the updated_at timestamp."""
        self.updated_at = datetime.now(timezone.utc)

    @abstractmethod
    def get_type(self) -> str:
        """Return the type of metadata."""
        pass

class ChunkMetadata(BaseMetadata):
    """Metadata specific to chunks."""
    section: str = Field(..., description="Section of the document this chunk belongs to")
    order: int = Field(..., description="Order of the chunk in the document")

    def get_type(self) -> str:
        return "Chunk"

class DocumentMetadata(BaseMetadata):
    """Metadata specific to documents."""
    author: str = Field(..., description="Author of the document")
    status: str = Field(default="draft", description="Status of the document (draft, published, archived)")

    def get_type(self) -> str:
        return "Document"

class LibraryMetadata(BaseMetadata):
    """Metadata specific to libraries."""
    is_public: bool = Field(default=False, description="Whether the library is publicly accessible")
    language: str = Field(default="en", description="Primary language of the library content")

    def get_type(self) -> str:
        return "Library"
