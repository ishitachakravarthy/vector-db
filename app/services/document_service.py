from uuid import UUID
import logging

from app.data_models.document import Document
from app.repository.mongo_repository import MongoRepository

logger = logging.getLogger(__name__)


class DocumentService:
    def __init__(self, repository: MongoRepository):
        self.document_repository = repository.document_repo
        self.library_repository = repository.library_repo
        self.chunk_repository = repository.chunk_repo

    def get_document(self, document_id: UUID) -> Document:
        return self.document_repository.get_document(document_id)

    def list_documents(self) -> list[Document]:
        return self.document_repository.list_documents()

    def save_document(self, document: Document) -> Document:
        saved_document = self.document_repository.save_document(document)
        try:
            library = self.library_repository.get_library(
                saved_document.get_library_id()
            )
            library.add_document(saved_document.get_document_id())
            self.library_repository.save_library(library)
        except Exception as e:
            logger.error(f"Error saving document: {str(e)}")
            raise
        return saved_document

    def delete_document(self, document_id: UUID) -> bool:
        document = self.document_repository.get_document(document_id)
        library = self.library_repository.get_library(document.get_library_id())

        try:
            for chunk_id in document.get_all_chunks():
                self.chunk_repository.delete_chunk(chunk_id)
        except Exception as e:
            raise ValueError(f"Could not delete chunks to delete document")

        try:
            library.delete_document(document_id)
            self.library_repository.save_library(library)
        except Exception as e:
            raise ValueError(
                f"Could not update Library with ID {document.get_library_id()} to remove document"
            )
        return self.document_repository.delete_document(document_id)
