from uuid import UUID
import logging
from typing import Optional

from app.data_models.document import Document, DocumentCreate, DocumentUpdate
from app.repository.mongo_repository import MongoRepository
from app.services.queue_manager import QueueManager

logger = logging.getLogger(__name__)


class DocumentService:
    def __init__(self, repository: MongoRepository):
        self.document_repository = repository.document_repo
        self.library_repository = repository.library_repo
        self.chunk_repository = repository.chunk_repo
        self.queue_manager = QueueManager()

    def get_document(self, document_id: UUID) -> Document:
        return self.queue_manager.enqueue_operation(
            "document",
            document_id,
            self.document_repository.get_document,
            document_id
        )

    def list_documents(self) -> list[Document]:
        return self.document_repository.list_documents()

    def create_document(self, document_create: DocumentCreate) -> Document:
        document = Document(
            title=document_create.title,
            library_id=document_create.library_id,
            metadata=document_create.metadata
        )
        return self.save_document(document)

    def update_document(self, document_id: UUID, document_update: DocumentUpdate) -> Optional[Document]:
        document = self.get_document(document_id)
        if not document:
            return None

        if document_update.title is not None:
            document.update_title(document_update.title)
        if document_update.metadata is not None:
            document.update_metadata(document_update.metadata)

        return self.save_document(document)

    def save_document(self, document: Document) -> Document:
        try:
            saved_document = self.queue_manager.enqueue_operation(
                "document",
                document.get_document_id(),
                self.document_repository.save_document,
                document
            )
            
            # Update library in a separate operation
            library = self.library_repository.get_library(
                saved_document.get_library_id()
            )
            library.add_document(saved_document.get_document_id())
            self.library_repository.save_library(library)
            
            return saved_document
        except Exception as e:
            logger.error(f"Error saving document: {str(e)}")
            raise

    def delete_document(self, document_id: UUID) -> bool:
        document = self.get_document(document_id)
        library = self.library_repository.get_library(document.get_library_id())

        def delete_operation():
            try:
                # Delete all chunks
                for chunk_id in document.get_all_chunks():
                    self.chunk_repository.delete_chunk(chunk_id)
                
                # Update library
                library.delete_document(document_id)
                self.library_repository.save_library(library)
                
                # Delete document
                return self.document_repository.delete_document(document_id)
            except Exception as e:
                logger.error(f"Error in delete operation: {str(e)}")
                raise

        return self.queue_manager.enqueue_operation(
            "document",
            document_id,
            delete_operation
        )
