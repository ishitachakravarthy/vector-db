from pydantic import BaseModel, Field
from uuid import UUID, uuid4

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
        self.generate_embedding()

    def get_chunk_id(self):
        return self.id
    
    def update_chunk(self, new_text: str) -> None:
        """Update the chunk's text and vector."""
        self.text = new_text
        self.generate_embedding()

    def generate_embedding(self) -> None:
        """Generate embedding using Cohere's API."""
        try:
            response = co.embed(
                texts=[self.text],
                model='embed-english-v3.0',
                input_type='search_document'
            )
            self.vector = response.embeddings[0]
        except Exception as e:
            print(f"Error generating embedding: {e}")
            self.vector = None   