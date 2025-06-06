from uuid import UUID
from pymongo.collection import Collection
from pymongo.database import Database
from typing import List, Optional

from app.data_models.document import Document
from app.data_models.metadata import DocumentMetadata


class DocumentRepository:
    """Collection for documents."""

    def __init__(self, db: Database):
        self.db = db
        self.documents: Collection = self.db.documents

    async def get_document(self, document_id: UUID) -> Document | None:
        try:
            data = self.documents.find_one({"_id": document_id})
            if not data:
                return None
            return Document(**data)
        except Exception as e:
            raise ValueError(f"Database error: Failed to retrieve document: {str(e)}")

    async def list_documents(self, library_id: UUID | None = None) -> List[Document]:
        try:
            if library_id is not None:
                return [Document(**doc) for doc in self.documents.find({"library_id": library_id})]
            else:
                return [Document(**doc) for doc in self.documents.find()]
        except Exception as e:
            raise ValueError(f"Database error: Failed to list documents: {str(e)}")

    async def save_document(self, document: Document) -> Document:
        try:
            document_dict = document.model_dump()
            result = self.documents.find_one_and_update(
                {"_id": document.id},
                {"$set": document_dict},
                upsert=True,
                return_document=True
            )
            if not result:
                raise ValueError(f"Failed to save document with ID {document.id}")
            return Document(**result)
        except Exception as e:
            raise ValueError(f"Database error: Failed to save document: {str(e)}")

    async def update_document(self, document_id: UUID, document_update: dict) -> Document:
        try:
            update_document = await self.get_document(document_id)
            if not update_document:
                raise ValueError(f"Document with ID {document_id} not found")
            
            if document_update.get("title") is not None:
                update_document.title = document_update["title"]
            if document_update.get("content") is not None:
                update_document.content = document_update["content"]
            if document_update.get("metadata") is not None:
                if isinstance(document_update["metadata"], dict):
                    current_metadata = update_document.metadata.model_dump()
                    current_metadata.update(document_update["metadata"])
                    update_document.metadata = DocumentMetadata(**current_metadata)
                else:
                    update_document.metadata = document_update["metadata"]
            return await self.save_document(update_document)
        except Exception as e:
            raise ValueError(f"Database error: Failed to update document: {str(e)}")

    async def delete_document(self, document_id: UUID) -> bool:
        try:
            result = self.documents.delete_one({"_id": document_id})
            if result.deleted_count == 0:
                raise ValueError(f"Document with ID {document_id} not found")
            return True
        except Exception as e:
            raise ValueError(f"Database error: Failed to delete document: {str(e)}")

    async def get_documents_by_library(self, library_id: UUID) -> List[Document]:
        try:
            return [Document(**doc) for doc in self.documents.find({"library_id": library_id})]
        except Exception as e:
            raise ValueError(f"Database error: Failed to get documents by library: {str(e)}")
