from uuid import UUID, uuid4
from pydantic import BaseModel, Field
import numpy as np
from datetime import datetime, timezone
from typing import Optional, List
import cohere
from app.data_models.chunk import Chunk
from app.repository.mongo_repository import MongoRepository
from app.config import COHERE_API_KEY

co = cohere.Client(COHERE_API_KEY)

class Vector(BaseModel):
    """A vector embedding model that stores embeddings for chunks."""
    chunk_id: UUID  # Reference to the chunk this vector represents
    embedding: Optional[List[float]] = None  # Store as list for JSON serialization
    repository: Optional[MongoRepository] = None  # Repository to access chunks

    def __init__(self, **data):
        if isinstance(data.get('embedding'), np.ndarray):
            data['embedding'] = data['embedding'].tolist()
        super().__init__(**data)

    def get_id(self) -> UUID:
        return self.chunk_id

    def get_embedding(self) -> np.ndarray:
        return np.array(self.embedding) if self.embedding else None

    def set_vector_emb(self) -> None:
        """Generate and set the vector embedding for the chunk's text content."""
        if not self.repository:
            raise ValueError("Repository not set. Call set_repository() first.")

        try:
            # Get the chunk from the repository
            chunk = self.repository.get_chunk(self.chunk_id)
            if not chunk:
                raise ValueError(f"Chunk with ID {self.chunk_id} not found")

            # Generate embedding from chunk's text
            response = co.embed(
                texts=[chunk.text],
                model="embed-english-v3.0",
                input_type="search_document",
            )
            self.embedding = response.embeddings[0]
        except Exception as e:
            print(f"Error generating embedding: {e}")
            self.embedding = None

    def set_repository(self, repository: MongoRepository) -> None:
        """Set the repository for accessing chunks."""
        self.repository = repository
