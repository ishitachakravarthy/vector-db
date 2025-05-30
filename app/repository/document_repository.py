from typing import List, Optional, Dict, Any
from uuid import UUID
from pymongo.collection import Collection
from bson import Binary
import uuid
import logging
from app.data_models.library import Document
from app.repository.base_repository import BaseRepository

logger = logging.getLogger(__name__)


class DocumentRepository(BaseRepository):
    """Repository for managing libraries in MongoDB."""

    def __init__(self):
        super().__init__()
        self.documents: Collection = self.db.documents

    def _serialize_document(self, document: Document) -> dict:
        doc_dict = document.model_dump()
        doc_dict["_id"] = doc_dict["id"]
        return doc_dict

    def get_document(self, document_id: UUID) -> Optional[Document]:
        try:
            data = self.documents.find_one({"_id": document_id})
            if data:
                return Document(**data)
            return None
        except Exception as e:
            logger.error(f"Error getting library: {str(e)}")
            raise

    def save_document(self, document: Document) -> Document:
        """Save or update a library in MongoDB."""
        try:
            document_dict = self._serialize_document(document)
            # Use upsert to create if not exists, update if exists
            result = self.documents.update_one(
                {"_id": document_dict["_id"]}, {"$set": document_dict}, upsert=True
            )

            logger.info(f"Saved Document with ID: {document.get_document_id()}")
            return document
        except Exception as e:
            logger.error(f"Error saving Document: {str(e)}")
            raise
