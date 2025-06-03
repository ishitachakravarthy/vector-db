from uuid import UUID
from pymongo.collection import Collection
import logging
from app.data_models.document import Document
from pymongo.database import Database

logger = logging.getLogger(__name__)


class DocumentRepository:
    """Collection for documents."""

    def __init__(self, db: Database):
        self.db = db
        self.documents: Collection = self.db.documents

    def get_document(self, document_id: UUID) -> Document | None:
        data = self.documents.find_one({"_id": document_id})
        if data:
            return Document(**data)
        return None

    def list_documents(self) -> list[Document]:
        return [Document(**doc) for doc in self.documents.find()]

    def save_document(self, document: Document) -> Document:
        document_dict = document.model_dump()
        self.documents.update_one(
            {"_id": document.get_document_id()}, {"$set": document_dict}, upsert=True
        )
        return document

    def delete_document(self, document_id: UUID) -> bool:
        result = self.documents.delete_one({"_id": document_id})
        return result.deleted_count > 0
