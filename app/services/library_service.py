from typing import List, Optional
from uuid import UUID
from datetime import datetime, timezone
import logging

from app.data_models.library import Library
from app.data_models.document import Document
from app.repository.mongo_repository import MongoRepository

logger = logging.getLogger(__name__)

class LibraryService:
    def __init__(self, repository: MongoRepository):
        self.repository = repository

    def create_library(self, library: Library) -> Library:
        return self.repository.create_library(library)

    def get_library(self, library_id: UUID) -> Optional[Library]:
        return self.repository.get_library(library_id)

    def list_libraries(self) -> List[Library]:
        return self.repository.list_libraries()

    def save_library(self, library: Library) -> Library:
        return self.repository.save_library(library)

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
