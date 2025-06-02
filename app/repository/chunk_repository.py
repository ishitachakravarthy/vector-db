from typing import List, Optional, Dict, Any
from uuid import UUID
from pymongo.collection import Collection
from bson import Binary
import uuid
import logging
from app.data_models.chunk import Chunk
from app.repository.base_repository import BaseRepository
from pymongo.database import Database

logger = logging.getLogger(__name__)


class ChunkRepository(BaseRepository):
    """Repository for managing chunks in MongoDB."""

    def __init__(self, db: Database, collection_name: str):
        super().__init__(db, collection_name)
        self.chunks: Collection = self.db.chunks

    def _serialize_chunk(self, chunk: Chunk) -> dict:
        chunk_dict = chunk.model_dump()
        chunk_dict["_id"] = chunk_dict["id"]
        return chunk_dict

    def get_chunk(self, chunk_id: UUID) -> Optional[Chunk]:
        """Get a chunk by ID."""
        try:
            data = self.chunks.find_one({"_id": chunk_id})
            if data:
                return Chunk(**data)
            return None
        except Exception as e:
            logger.error(f"Error getting chunk: {str(e)}")
            raise

    def save_chunk(self, chunk: Chunk) -> Chunk:
        try:
            chunk_dict = self._serialize_chunk(chunk)
            # Use upsert to create if not exists, update if exists
            result = self.chunks.update_one(
                {"_id": chunk_dict["_id"]}, {"$set": chunk_dict}, upsert=True
            )

            logger.info(f"Saved Chunk with ID: {chunk.get_chunk_id()}")
            return chunk
        except Exception as e:
            logger.error(f"Error saving Chunk: {str(e)}")
            raise

    def list_chunks(self) -> List[Chunk]:
        """List all chunks."""
        return [Chunk(**doc) for doc in self.chunks.find()]

    def delete_chunk(self, chunk_id: UUID) -> bool:
        """Delete a chunk by ID."""
        result = self.chunks.delete_one({"_id": chunk_id})
        return result.deleted_count > 0

