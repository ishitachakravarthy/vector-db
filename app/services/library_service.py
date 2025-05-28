from typing import List, Optional
from uuid import UUID
from datetime import datetime, timezone
import logging

from app.data_models.library import Library
from app.data_models.document import Document
from app.repository.mongo_repository import MongoRepository
from app.services.vector_db_service import VectorDBService

logger = logging.getLogger(__name__)

class LibraryService:
    def __init__(self, repository: MongoRepository):
        self.repository = repository
        self.vector_db = VectorDBService(repository)

    def create_library(self, library: Library) -> Library:
        return self.repository.create_library(library)

    def get_library(self, library_id: UUID) -> Optional[Library]:
        return self.repository.get_library(library_id)

    def list_libraries(self) -> List[Library]:
        return self.repository.list_libraries()

    def save_library(self, library: Library) -> Library:
        """Save library and create vectors for all chunks."""
        try:
            # First save the library to MongoDB
            saved_library = self.repository.save_library(library)
            
            # Then create vectors for all chunks in all documents
            for document in library.get_all_docs():
                chunks = document.get_all_chunks()
                if chunks:
                    self.vector_db.save_chunk_vectors(chunks)
            
            return saved_library
        except Exception as e:
            logger.error(f"Error saving library: {str(e)}")
            raise

    def delete_library(self, library_id: UUID) -> bool:
        return self.repository.delete_library(library_id)
    
    

    # def get_document(self, document_id: UUID) -> Optional[Document]:
    #     """Get a document by ID."""
    #     library = self.repository.find_library_by_id(document_id)
    #     if library:
    #         return library.documents.get(document_id)
    #     return None

    # def list_documents(self, library_id: UUID) -> List[Document]:
    #     """List all documents in a library."""
    #     library = self.repository.find_library_by_id(library_id)
    #     if library:
    #         return list(library.documents.values())
    #     return []
