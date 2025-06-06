from uuid import UUID, uuid4
from pydantic import BaseModel, Field
from app.data_models.metadata import ChunkMetadata

from datetime import datetime, timezone
import cohere
from app.config import COHERE_API_KEY
import logging

logger = logging.getLogger(__name__)

class ChunkBase(BaseModel):
    document_id: UUID = Field(..., description="ID of the document this chunk belongs to")
    text: str = Field(..., description="Text content of the chunk")

class ChunkCreate(ChunkBase):
    metadata: ChunkMetadata|None = None

class ChunkUpdate(BaseModel):
    text: str|None = None
    metadata: ChunkMetadata|None = None
    def get_text(self) -> str | None:
        return self.text
    def get_metadata(self) -> ChunkMetadata | None:
        return self.metadata

class ChunkResponse(ChunkBase):
    id: UUID = Field(..., description="Unique identifier for the chunk")
    embedding: list[float] | None = Field(None, description="Vector embedding of the chunk text")
    metadata: ChunkMetadata = Field(default_factory=ChunkMetadata, description="Chunk metadata")
    
    class Config:
        from_attributes = True

class Chunk(BaseModel):
    """A chunk of text from a document with its vector embedding."""

    id: UUID = Field(default_factory=uuid4)
    document_id: UUID
    text: str
    embedding: list[float]|None = None
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

    def get_document_id(self) -> UUID:
        return self.document_id

    def get_chunk_text(self) -> str:
        return self.text

    def get_embedding(self) -> list[float]|None:
        return self.embedding

    # Setters for Chunk
    def update_chunk_text(self, new_text: str) -> None:
        self.text = new_text
        self._update_timestamp()
        self.generate_embedding()

    def update_metadata(self, new_metadata: ChunkMetadata) -> None:
        self.metadata = new_metadata
        self._update_timestamp()

    def update_embedding(self, embedding: list[float]) -> None:
        self.embedding = embedding
        self._update_timestamp()

    def generate_embedding(self) -> list[float] | None:
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
