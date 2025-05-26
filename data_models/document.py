from pydantic import BaseModel, Field
from typing import List

from uuid import UUID, uuid4

from data_models.chunk import Chunk
from data_models.metadata import DocumentMetadata

class Document(BaseModel):
    """A document containing multiple chunks."""
    id: UUID = Field(default_factory=uuid4)
    title: str
    chunks: List[Chunk] = Field(default_factory=list)
    metadata: DocumentMetadata
