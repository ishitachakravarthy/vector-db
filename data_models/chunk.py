from main import co

from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import datetime, UTC
from uuid import UUID, uuid4
import numpy as np

from data_models.metadata import ChunkMetadata

class Chunk(BaseModel):
    """A chunk of text with its vector representation."""
    id: UUID = Field(default_factory=uuid4)
    text: str
    vector: Optional[List[float]] = None
    metadata: ChunkMetadata
