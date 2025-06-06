from typing import List, Optional
from uuid import UUID

from app.data_models.document import Document, DocumentCreate, DocumentUpdate
from app.repository.mongo_repository import MongoRepository
from app.services.queue_manager import QueueManager


class DocumentService:
    def __init__(self, repository: MongoRepository):
        self.document_repository = repository.document_repo
        self.library_repository = repository.library_repo
        self.chunk_repository = repository.chunk_repo
        self.queue_manager = QueueManager()

    async def get_document(self, document_id: UUID) -> Document:
        try:
            return await self.queue_manager.enqueue_operation(
                "document",
                document_id,
                self.document_repository.get_document,
                document_id
            )
        except Exception as e:
            raise ValueError("Service error: Failed to queue document retrieval") from e

    async def list_documents(self, library_id: UUID | None = None) -> List[Document]:
        try:
            if library_id is not None:
                # Verify library exists
                library = await self.library_repository.get_library(library_id)
                if not library:
                    raise ValueError(f"Library with ID {library_id} not found")

                return await self.queue_manager.enqueue_operation(
                    "document",
                    library_id,
                    self.document_repository.list_documents,
                    library_id
                )
            else:
                # List all documents
                return await self.queue_manager.enqueue_operation(
                    "document",
                    None,
                    self.document_repository.list_documents
                )
        except Exception as e:
            raise ValueError(f"Service error: Failed to queue document listing: {str(e)}") from e

    async def create_document(self, document_create: DocumentCreate) -> Document:
        try:
            # Verify library exists
            library = await self.library_repository.get_library(document_create.library_id)
            if not library:
                raise ValueError(f"Library with ID {document_create.library_id} not found")

            document = Document(
                library_id=document_create.library_id,
                title=document_create.title,
                content=document_create.content,
                metadata=document_create.metadata
            )
            return await self.save_document(document)
        except Exception as e:
            raise ValueError(f"Service error: Failed to create document: {str(e)}") from e

    async def update_document(self, document_id: UUID, document_update: DocumentUpdate) -> Document:
        try:
            # First get the document to verify it exists
            document = await self.get_document(document_id)
            if not document:
                raise ValueError(f"Document with ID {document_id} not found")

            # Convert update to dict and remove None values
            update_dict = document_update.model_dump(exclude_unset=True)
            
            return await self.queue_manager.enqueue_operation(
                "document",
                document_id,
                self.document_repository.update_document,
                document_id,
                update_dict
            )
        except Exception as e:
            raise ValueError(f"Service error: Failed to queue document update: {str(e)}") from e

    async def save_document(self, document: Document) -> Document:
        try:
            # Verify library exists
            library = await self.library_repository.get_library(document.library_id)
            if not library:
                raise ValueError(f"Library with ID {document.library_id} not found")

            return await self.queue_manager.enqueue_operation(
                "document",
                document.id,
                self.document_repository.save_document,
                document
            )
        except Exception as e:
            raise ValueError(f"Service error: Failed to save document: {str(e)}") from e

    async def delete_document(self, document_id: UUID) -> bool:
        try:
            return await self.queue_manager.enqueue_operation(
                "document",
                document_id,
                self.document_repository.delete_document,
                document_id
            )
        except Exception as e:
            raise ValueError("Service error: Failed to queue document deletion") from e
