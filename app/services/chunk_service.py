from typing import List, Optional
from uuid import UUID
import logging

from app.data_models.chunk import Chunk
from app.repository.mongo_repository import MongoRepository

logger = logging.getLogger(__name__)


class ChunkService:
    def __init__(self, repository: MongoRepository):
        self.repository = repository.chunk_repo

    def create_chunk(self, chunk: Chunk) -> Chunk:
        pass

    def get_chunk(self, chunk_id: UUID) -> Optional[Chunk]:
        pass

    def list_chunks(self) -> list[Chunk]:
        pass

    def delete_chunk(self, chunk_id: UUID) -> bool:
        pass

    def save_chunk(self, chunk: Chunk) -> Chunk:
        """Save chunk and create vectors for all chunks."""
        try:
            saved_chunk = self.repository.save_chunk(chunk)
            return saved_chunk
        except Exception as e:
            logger.error(f"Error saving library: {str(e)}")
            raise
