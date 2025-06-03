from uuid import UUID
from pymongo.collection import Collection
import logging
from app.data_models.chunk import Chunk
from pymongo.database import Database

logger = logging.getLogger(__name__)


class ChunkRepository:
    """Collection for chunks"""

    def __init__(self, db: Database):
        self.db = db
        self.chunks: Collection = self.db.chunks

    def get_chunk(self, chunk_id: UUID) -> Chunk:
        try:
            data = self.chunks.find_one({"_id": chunk_id})
            if data:
                return Chunk(**data)
            raise ValueError(f"Chunk with ID {chunk_id} not found in database")
        except Exception as e:
            raise ValueError("Database connection failed")

    def list_chunks(self) -> list[Chunk]:
        try:
            return [Chunk(**chunk) for chunk in self.chunks.find()]
        except Exception as e:
            raise ValueError("Database connection failed")

    def save_chunk(self, chunk: Chunk) -> Chunk:
        try:
            chunk_dict = chunk.model_dump()
            result = self.chunks.update_one(
                {"_id": chunk.get_chunk_id()}, {"$set": chunk_dict}, upsert=True
            )
            if not (result.matched_count == 1 or result.upserted_id is not None):
                raise ValueError(
                    f"Failed to save chunk with ID {chunk.get_chunk_id()} to database"
                )
            return chunk
        except Exception as e:
            raise ValueError("Database connection failed") from e

    def delete_chunk(self, chunk_id: UUID) -> bool:
        try:
            result = self.chunks.delete_one({"_id": chunk_id})
            if result.deleted_count == 0:
                raise ValueError(f"Chunk with ID {chunk_id} not found in database")
            return True
        except Exception as e:
            raise ValueError("Database connection failed") from e
