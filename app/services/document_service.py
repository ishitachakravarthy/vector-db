from typing import List, Optional
from uuid import UUID
import logging

from app.data_models.document import Document
from app.repository.mongo_repository import MongoRepository

logger = logging.getLogger(__name__)


class DocumentService:
    def __init__(self, repository: MongoRepository):
        self.repository = repository.document_repo
        self.library_repo = repository.library_repo

    def create_document(self, document: Document) -> Document:
        """Create a new document and add it to its library."""
        # Verify library exists
        library = self.library_repo.get_library(document.library_id)
        if not library:
            raise ValueError(f"Library with ID {document.library_id} does not exist")
        
        try:
            # Save the document to the database
            saved_document = self.repository.save_document(document)
            
            # Add document to library
            library.add_document(saved_document.id)
            self.library_repo.save_library(library)
            
            return saved_document
        except Exception as e:
            logger.error(f"Error creating document: {str(e)}")
            raise

    def get_document(self, document_id: UUID) -> Optional[Document]:
        """Get a document by its ID."""
        return self.repository.get_document(document_id)

    def list_documents(self) -> list[Document]:
        """List all documents."""
        return self.repository.list_documents()

    def delete_document(self, document_id: UUID) -> bool:
        """Delete a document and remove it from its library."""
        document = self.get_document(document_id)
        if not document:
            return False
            
        library = self.library_repo.get_library(document.library_id)
        if library:
            library.remove_document(document_id)
            self.library_repo.save_library(library)
            
        return self.repository.delete_document(document_id)

    def save_document(self, document: Document) -> Document:
        """Save document and create vectors for all chunks."""
        try:
            saved_document = self.repository.save_document(document)
            return saved_document
        except Exception as e:
            logger.error(f"Error saving library: {str(e)}")
            raise
