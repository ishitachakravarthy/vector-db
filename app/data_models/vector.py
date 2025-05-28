from uuid import UUID, uuid4
from pydantic import BaseModel, Field
import numpy as np
from datetime import datetime, timezone
from typing import Optional, List
import cohere

co = cohere.Client(
    "A1Fi5KBBNoekwBPIa833CBScs6Z2mHEtOXxr52KO"
)  # Replace with your actual API key

class Vector(BaseModel):
    """A vector embedding model that stores embeddings for chunks."""
    chunk_id: UUID  # Reference to the chunk this vector represents
    embedding: List[float]  # Store as list for JSON serialization

    def __init__(self, **data):
        if isinstance(data.get('embedding'), np.ndarray):
            data['embedding'] = data['embedding'].tolist()
        super().__init__(**data)

    def get_id(self) -> UUID:
        return self.chunk_id

    def get_embedding(self) -> np.ndarray:
        return np.array(self.embedding)

    def set_vector_emb(self) -> None:
        try:
            response = co.embed(
                texts=[self.text],
                model="embed-english-v3.0",
                input_type="search_document",
            )
            self.embedding = response.embeddings[0]

        except Exception as e:
            print(f"Error generating embedding: {e}")
            self.embedding = None
