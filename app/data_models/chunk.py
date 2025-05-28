from uuid import UUID, uuid4
from pydantic import BaseModel, Field
from datetime import datetime, timezone
from typing import Optional

from app.data_models.metadata import ChunkMetadata


class Chunk(BaseModel):
    """A chunk of text from a document."""

    id: UUID = Field(default_factory=uuid4)
    text: str
    metadata: ChunkMetadata

    def __init__(self, **data):
        super().__init__(**data)
        if not self.metadata:
            self.metadata = ChunkMetadata()

    def _update_timestamp(self) -> None:
        self.metadata.updated_at = datetime.now(timezone.utc)

    # Getters for Chunk
    def get_chunk_id(self) -> UUID:
        return self.id

    def get_chunk_text(self) -> str:
        return self.text


    # Setters for Chunk

    def update_chunk_text(self, new_text: str) -> None:
        self.text = new_text
        self._update_timestamp()

    def update_metadata(self, new_metadata: ChunkMetadata) -> None:
        self.metadata = new_metadata
        self._update_timestamp()
