from typing import List, Optional, Dict, Any
from uuid import UUID
from pymongo.collection import Collection
from bson import Binary
import uuid
import logging
from app.data_models.chunk import Chunk
from app.repository.base_repository import BaseRepository

logger = logging.getLogger(__name__)


class ChunkRepository(BaseRepository):
    """Repository for managing libraries in MongoDB."""

    def __init__(self):
        super().__init__()
        self.documents: Collection = self.db.documents

    def _serialize_chunk(self, chunk: Chunk) -> dict:
        # doc_dict = document.model_dump()
        # doc_dict["_id"] = doc_dict["id"]
        # return doc_dict
        pass

    def get_chunk(self, chunk_id: UUID) -> Optional[Chunk]:
        try:
            data = self.chunks.find_one({"_id": chunk_id})
            if data:
                return Chunk(**data)
            return None
        except Exception as e:
            logger.error(f"Error getting library: {str(e)}")
            raise

    def save_chunk(self, chunk: Chunk) -> Chunk:
        # try:
        #     document_dict = self._serialize_document(document)
        #     # Use upsert to create if not exists, update if exists
        #     result = self.documents.update_one(
        #         {"_id": document_dict["_id"]}, {"$set": document_dict}, upsert=True
        #     )

        #     logger.info(f"Saved Document with ID: {document.get_document_id()}")
        #     return document
        # except Exception as e:
        #     logger.error(f"Error saving Document: {str(e)}")
        #     raise
        pass

    # def save_vector(self, chunk_id: UUID, embedding: List[float]) -> None:
    #     """Save a vector embedding for a chunk."""
    #     vector_dict = {
    #         "_id": str(chunk_id),
    #         "embedding": embedding,
    #         "created_at": datetime.now(timezone.utc),
    #         "updated_at": datetime.now(timezone.utc),
    #     }
    #     self.vectors.update_one(
    #         {"_id": str(chunk_id)}, {"$set": vector_dict}, upsert=True
    #     )

    # def get_vector(self, chunk_id: UUID) -> Optional[List[float]]:
    #     """Get a vector embedding for a chunk."""
    #     vector_dict = self.vectors.find_one({"_id": str(chunk_id)})
    #     if vector_dict:
    #         return vector_dict["embedding"]
    #     return None

    # def delete_vector(self, chunk_id: UUID) -> bool:
    #     """Delete a vector embedding for a chunk."""
    #     result = self.vectors.delete_one({"_id": str(chunk_id)})
    #     return result.deleted_count > 0
