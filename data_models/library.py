from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from uuid import UUID, uuid4

from data_models.document import Document
from data_models.chunk import Chunk
from data_models.metadata import LibraryMetadata

class Library(BaseModel):
    """A library containing multiple documents and their chunks."""
    id: UUID = Field(default_factory=uuid4)
    name: str
    description: Optional[str] = None
    documents: List[Document] = Field(default_factory=list)
    metadata: LibraryMetadata
