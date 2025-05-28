from typing import List, Optional, Dict, Any
from uuid import UUID
import cohere
import logging
from app.data_models.chunk import Chunk
from app.repository.mongo_repository import MongoRepository
from app.config import COHERE_API_KEY

logger = logging.getLogger(__name__)

class VectorDBService:
    def __init__(self, repository: MongoRepository):
        self.co = cohere.Client(COHERE_API_KEY)
        self.repository = repository

    def create_embedding(self, text: str) -> List[float]:
        """Create a vector embedding for the given text."""
        try:
            response = self.co.embed(
                texts=[text],
                model="embed-english-v3.0",
                input_type="search_document",
            )
            return response.embeddings[0]
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise

    def save_chunk_vectors(self, chunks: List[Chunk]) -> None:
        """Save vectors for all chunks in a document."""
        for chunk in chunks:
            try:
                # Check if vector already exists
                existing_vector = self.repository.get_vector(chunk.id)
                if existing_vector:
                    logger.info(f"Vector already exists for chunk {chunk.id}")
                    continue

                # Create and save new vector
                embedding = self.create_embedding(chunk.text)
                self.repository.save_vector(chunk.id, embedding)
                logger.info(f"Created and saved embedding for chunk {chunk.id}")
            except Exception as e:
                logger.error(f"Error saving vector for chunk {chunk.id}: {e}")
                raise 