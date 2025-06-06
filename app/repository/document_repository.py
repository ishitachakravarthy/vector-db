from uuid import UUID
from pymongo.collection import Collection
import logging
from app.data_models.document import Document, DocumentUpdate
from pymongo.database import Database

logger = logging.getLogger(__name__)


class DocumentRepository:
    """Collection for documents."""

    def __init__(self, db: Database):
        self.db = db
        self.documents: Collection = self.db.documents

    def get_document(self, document_id: UUID) -> Document | None:
        try:
            data = self.documents.find_one({"_id": document_id})
            if data:
                return Document(**data)
            raise ValueError(f"Document with ID {document_id} not found")
        except Exception:
            raise ValueError("Database error: Failed to retrieve document")

    def list_documents(self) -> list[Document]:
        try:
            return [Document(**doc) for doc in self.documents.find()]
        except Exception:
            raise ValueError("Database error: Failed to list documents")

    def save_document(self, document: Document) -> Document:
        try:
            document_dict = document.model_dump()
            result = self.documents.update_one(
                {"_id": document.get_document_id()},
                {"$set": document_dict},
                upsert=True,
            )
            if not (result.matched_count == 1 or result.upserted_id is not None):
                raise ValueError(f"Failed to save document with ID {document.get_document_id()}")
            return document
        except Exception:
            raise ValueError("Database error: Failed to save document")

    def update_document(self, document_id: UUID, document_update: DocumentUpdate) -> Document:
        try:
            update_document = self.get_document(document_id)
            if document_update.get_title() is not None:
                update_document.update_title(document_update.get_title())
            if document_update.get_metadata() is not None:
                update_document.update_metadata(document_update.get_metadata())
            return self.save_document(update_document)
        except Exception:
            raise ValueError("Database error: Failed to update document")

    def delete_document(self, document_id: UUID) -> bool:
        try:
            result = self.documents.delete_one({"_id": document_id})
            if result.deleted_count == 0:
                raise ValueError(f"Document with ID {document_id} not found")
            return True
        except Exception:
            raise ValueError("Database error: Failed to delete document")
