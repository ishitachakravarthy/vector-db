from uuid import UUID
from pymongo.collection import Collection
from app.data_models.chunk import Chunk, ChunkUpdate
from pymongo.database import Database

class ChunkRepository:
    """Collection for chunks"""

    def __init__(self, db: Database):
        self.db = db
        self.chunks: Collection = self.db.chunks

    def get_chunk(self, chunk_id: UUID) -> Chunk:
        try:
            data = self.chunks.find_one({"_id": chunk_id})
            if not data:
                raise ValueError(f"Chunk with ID {chunk_id} not found")
            return Chunk(**data)
        except Exception:
            raise ValueError("Database error: Failed to retrieve chunk")

    def list_chunks(self) -> list[UUID]:
        try:
            return [Chunk(**chunk).get_chunk_id() for chunk in self.chunks.find()]
        except Exception:
            raise ValueError("Database error: Failed to list chunks")

    def save_chunk(self, chunk: Chunk) -> Chunk:
        try:
            chunk_dict = chunk.model_dump()
            result = self.chunks.update_one(
                {"_id": chunk.get_chunk_id()}, {"$set": chunk_dict}, upsert=True
            )
            if not (result.matched_count == 1 or result.upserted_id is not None):
                raise ValueError(f"Failed to save chunk with ID {chunk.get_chunk_id()}")
            return chunk
        except Exception:
            raise ValueError("Database error: Failed to save chunk")

    def update_chunk(self, chunk_id: UUID, chunk_update: ChunkUpdate) -> Chunk:
        try:
            update_chunk = self.get_chunk(chunk_id)
            if chunk_update.get_text() is not None:
                update_chunk.update_chunk_text(chunk_update.get_text())
            if chunk_update.get_metadata() is not None:
                update_chunk.update_metadata(chunk_update.get_metadata())
            return self.save_chunk(update_chunk)
        except Exception:
            raise ValueError("Database error: Failed to update chunk")

    def delete_chunk(self, chunk_id: UUID) -> bool:
        try:
            result = self.chunks.delete_one({"_id": chunk_id})
            if result.deleted_count == 0:
                raise ValueError(f"Chunk with ID {chunk_id} not found")
            return True
        except Exception:
            raise ValueError("Database error: Failed to delete chunk")
