from typing import List, Optional
from uuid import UUID
from datetime import datetime, timezone
import logging

from app.data_models.document import Document
from app.repository.mongo_repository import MongoRepository
from app.services.vector_db_service import VectorDBService

logger = logging.getLogger(__name__)


class DocumentService:
    def __init__(self, repository: MongoRepository):
        self.repository = repository
        self.vector_db = VectorDBService(repository)

    def create_document(self, document: Document) -> Document:
        pass
        # return self.repository.create_library(document)

    def get_document(self, document_id: UUID) -> Optional[Document]:
        pass
        # return self.repository.get_library(library_id)

    def list_documents(self) -> List[Document]:
        pass
        # return self.repository.list_libraries()


    def delete_document(self, document_id: UUID) -> bool:
        pass
        # return self.repository.delete_library(library_id)


    def save_document(self, document: Document) -> Document:
        """Save document and create vectors for all chunks."""
        try:
            saved_document = self.repository.save_document(document)
            return saved_document
        except Exception as e:
            logger.error(f"Error saving library: {str(e)}")
            raise
