from uuid import UUID, uuid4
from pydantic import BaseModel, Field
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
import cohere
import numpy as np
from app.config import COHERE_API_KEY
import logging

from app.data_models.metadata import ChunkMetadata

logger = logging.getLogger(__name__)

class Chunk(BaseModel):
    """A chunk of text from a document with its vector embedding."""

    id: UUID = Field(default_factory=uuid4)
    document_id: UUID
    text: str
    embedding: Optional[List[float]] = None
    metadata: ChunkMetadata

    def __init__(self, **data):
        super().__init__(**data)
        if not self.metadata:
            self.metadata = ChunkMetadata()
        if not self.embedding:
            self.generate_embedding()

    def _update_timestamp(self) -> None:
        self.metadata.updated_at = datetime.now(timezone.utc)

    # Getters for Chunk
    def get_chunk_id(self) -> UUID:
        return self.id

    def get_chunk_text(self) -> str:
        return self.text

    def get_embedding(self) -> Optional[List[float]]:
        return self.embedding

    # Setters for Chunk
    def update_chunk_text(self, new_text: str) -> None:
        self.text = new_text
        self._update_timestamp()
        # Generate new embedding for updated text
        self.generate_embedding()

    def update_metadata(self, new_metadata: ChunkMetadata) -> None:
        self.metadata = new_metadata
        self._update_timestamp()

    def update_embedding(self, embedding: List[float]) -> None:
        """Update the chunk's vector embedding."""
        self.embedding = embedding
        self._update_timestamp()
        
    def generate_embedding(self) -> Optional[List[float]]:
        """Generate embedding for the chunk's text using Cohere."""
        try:
            co = cohere.Client(COHERE_API_KEY)
            response = co.embed(
                texts=[self.text],
                model="embed-english-v3.0",
                input_type="search_document",
            )

            if response and response.embeddings:
                embedding = response.embeddings[0]
                self.update_embedding(embedding)
                return embedding
            return None

        except Exception as e:
            logger.error(f"Error generating embedding: {str(e)}")
            return None
