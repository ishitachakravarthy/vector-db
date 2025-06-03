from typing import List, Optional
from uuid import UUID
import logging

from app.data_models.library import Library
from app.repository.mongo_repository import MongoRepository

logger = logging.getLogger(__name__)


class LibraryService:
    def __init__(self, repository: MongoRepository):
        self.repository = repository.library_repo

    def get_library(self, library_id: UUID) -> Library | None:
        return self.repository.get_library(library_id)

    def list_libraries(self) -> List[Library]:
        return self.repository.list_libraries()

    def save_library(self, library: Library) -> Library:
        saved_library = self.repository.save_library(library)
        return saved_library

    def delete_library(self, library_id: UUID) -> bool:
        library = self.repository.get_library(library_id)
        try:
            for document_id in library.get_all_doc_ids():
                document = self.document_repository.get_document(document_id)
                for chunk_id in document.chunk_ids:
                    self.chunk_repository.delete_chunk(chunk_id)
                self.document_repository.delete_document(document_id)
        except Exception as e:
            raise ValueError(f"Could not delete documents and chunks from library")

        return self.repository.delete_library(library_id)
