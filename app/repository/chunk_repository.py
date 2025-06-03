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
        data = self.chunks.find_one({"_id": chunk_id})
        if data:
            return Chunk(**data)
        raise ValueError(f"Chunk with ID {chunk_id} not found")

    def list_chunks(self) -> list[Chunk]:
        return [Chunk(**chunk) for chunk in self.chunks.find()]

    def save_chunk(self, chunk: Chunk) -> Chunk:
        chunk_dict = chunk.model_dump()
        self.chunks.update_one(
            {"_id": chunk.get_chunk_id()}, {"$set": chunk_dict}, upsert=True
        )
        return chunk

    def delete_chunk(self, chunk_id: UUID) -> bool:
        result = self.chunks.delete_one({"_id": chunk_id})
        return result.deleted_count > 0
