from pydantic import BaseModel, Field
from uuid import UUID, uuid4
from datetime import datetime,UTC

from data_models.metadata import ChunkMetadata
from main import co

class Chunk(BaseModel):
    """A chunk of text with its vector representation."""

    id: UUID = Field(default_factory=uuid4)
    text: str
    vector: list[float] | None = None
    metadata: ChunkMetadata

    def __init__(self, **data):
        super().__init__(**data)
        self.set_vector_emb()

    def _update_timestamp(self) -> None:
        self.metadata.updated_at = datetime.now(UTC)

    # Getters for Chunk
    def get_chunk_id(self)->UUID:
        return self.id

    def get_chunk_text(self):
        return self.text

    def get_chunk_vector(self):
        return self.vector

    # Setters for Chunk
    def set_chunk_text(self, new_text: str) -> None:
        self.text = new_text
        self.set_vector_emb()
        self._update_timestamp()

    def set_vector_emb(self) -> None:
        try:
            response = co.embed(
                texts=[self.text],
                model="embed-english-v3.0",
                input_type="search_document",
            )
            self.vector = response.embeddings[0]

        except Exception as e:
            print(f"Error generating embedding: {e}")
            self.vector = None
        self._update_timestamp()

    def update_metadata(self, new_metadata: ChunkMetadata):
        self.metadata = new_metadata
        self._update_timestamp()
