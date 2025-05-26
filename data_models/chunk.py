
from pydantic import BaseModel, Field
from typing import List, Optional
from uuid import UUID, uuid4

from data_models.metadata import ChunkMetadata

class Chunk(BaseModel):
    """A chunk of text with its vector representation."""
    id: UUID = Field(default_factory=uuid4)
    text: str
    vector: Optional[List[float]] = None
    metadata: ChunkMetadata
