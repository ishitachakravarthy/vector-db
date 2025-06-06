from uuid import UUID
from typing import Optional

from app.data_models.document import Document, DocumentCreate, DocumentUpdate
from app.repository.mongo_repository import MongoRepository
from app.services.queue_manager import QueueManager


class DocumentService:
    def __init__(self, repository: MongoRepository):
        self.document_repository = repository.document_repo
        self.library_repository = repository.library_repo
        self.chunk_repository = repository.chunk_repo
        self.queue_manager = QueueManager()

    def get_document(self, document_id: UUID) -> Document:
        try:
            return self.queue_manager.enqueue_operation(
                "document",
                document_id,
                self.document_repository.get_document,
                document_id,
            )
        except Exception as e:
            raise ValueError("Service error: Failed to queue document retrieval") from e

    def list_documents(self) -> list[Document]:
        return self.document_repository.list_documents()

    def create_document(self, document_create: DocumentCreate) -> Document:
        try:
            document = Document(
                title=document_create.title,
                library_id=document_create.library_id,
                metadata=document_create.metadata,
            )
            return self.save_document(document)
        except Exception as e:
            raise ValueError("Service error: Failed to create document") from e

    def update_document(
        self, document_id: UUID, document_update: DocumentUpdate
    ) -> Optional[Document]:
        try:
            return self.queue_manager.enqueue_operation(
                "document",
                document_id,
                self.document_repository.update_document,
                document_id,
                document_update,
            )
        except Exception as e:
            raise ValueError("Service error: Failed to update document") from e

    def save_document(self, document: Document) -> Document:
        try:
            saved_document: Document = self.queue_manager.enqueue_operation(
                "document",
                document.get_document_id(),
                self.document_repository.save_document,
                document,
            )
            library = self.library_repository.get_library(
                saved_document.get_library_id()
            )
            if not library:
                raise ValueError(
                    f"Library with ID {saved_document.get_library_id()} not found"
                )
            library.add_document(saved_document.get_document_id())
            self.library_repository.save_library(library)
            return saved_document
        except Exception as e:
            raise ValueError(
                "Service error: Failed to save document and update library"
            ) from e

    def delete_document(self, document_id: UUID) -> bool:
        try:
            document = self.get_document(document_id)
            library = self.library_repository.get_library(document.get_library_id())
            if not library:
                raise ValueError(
                    f"Library with ID {document.get_library_id()} not found"
                )
            def delete_operation():
                for chunk_id in document.get_all_chunks():
                    self.chunk_repository.delete_chunk(chunk_id)
                library.delete_document(document_id)
                self.library_repository.save_library(library)
                return self.document_repository.delete_document(document_id)

            return self.queue_manager.enqueue_operation(
                "document", document_id, delete_operation
            )
        except Exception as e:
            raise ValueError(
                "Service error: Failed to delete document and its chunks"
            ) from e
