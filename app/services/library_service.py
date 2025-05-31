from typing import List, Optional
from uuid import UUID
import logging

from app.data_models.library import Library
from app.repository.mongo_repository import MongoRepository

logger = logging.getLogger(__name__)

class LibraryService:
    def __init__(self, repository: MongoRepository):
        print(repository.library_repo)
        self.repository = repository.library_repo

    def create_library(self, library: Library) -> Library:
        return self.repository.create_library(library)

    def get_library(self, library_id: UUID) -> Library|None:
        return self.repository.get_library(library_id)

    def list_libraries(self) -> List[Library]:
        return self.repository.list_libraries()

    def save_library(self, library: Library) -> Library:
        """Save library and create vectors for all chunks."""
        try:
            saved_library = self.repository.save_library(library)
            # Then create vectors for all chunks in all documents
            for doc_id in library.get_all_doc_ids():
                document=self.repository.get_document(doc_id)
                self.repository.save_document(document)
                chunk_ids = document.get_all_chunks()
                for chunk_id in chunk_ids:
                    chunk=self.repository.get_chunk(chunk_id)
                    self.vector_db.save_chunk_vectors(chunk)

            return saved_library
        except Exception as e:
            logger.error(f"Error saving library: {str(e)}")
            raise

    def delete_library(self, library_id: UUID) -> bool:
        return self.repository.delete_library(library_id)
