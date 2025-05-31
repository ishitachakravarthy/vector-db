from typing import List, Optional
from uuid import UUID
import logging

from app.data_models.document import Document
from app.repository.mongo_repository import MongoRepository

logger = logging.getLogger(__name__)


class DocumentService:
    def __init__(self, repository: MongoRepository):
        self.repository = repository

    def create_document(self, document: Document) -> Document:
        pass

    def get_document(self, document_id: UUID) -> Optional[Document]:
        pass

    def list_documents(self) -> List[Document]:
        pass

    def delete_document(self, document_id: UUID) -> bool:
        pass

    def save_document(self, document: Document) -> Document:
        """Save document and create vectors for all chunks."""
        try:
            saved_document = self.repository.save_document(document)
            return saved_document
        except Exception as e:
            logger.error(f"Error saving library: {str(e)}")
            raise
