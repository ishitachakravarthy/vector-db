from typing import List, Optional
from uuid import UUID
import logging
from datetime import datetime

from app.data_models.library import Library, LibraryCreate, LibraryUpdate
from app.repository.mongo_repository import MongoRepository
from app.services.queue_manager import QueueManager

logger = logging.getLogger(__name__)


class LibraryService:
    def __init__(self, repository: MongoRepository):
        self.document_repository = repository.document_repo
        self.library_repository = repository.library_repo
        self.chunk_repository = repository.chunk_repo
        self.queue_manager = QueueManager()

    def get_library(self, library_id: UUID) -> Library | None:
        return self.queue_manager.enqueue_operation(
            "library",
            library_id,
            self.library_repository.get_library,
            library_id
        )

    def list_libraries(self) -> List[Library]:
        return self.library_repository.list_libraries()

    def create_library(self, library_create: LibraryCreate) -> Library:
        library = Library(
            title=library_create.title,
            description=library_create.description,
            index_type=library_create.index_type,
            metadata=library_create.metadata
        )
        return self.save_library(library)

    # TODO: Redo in repository
    def update_library(self, library_id: UUID, library_update: LibraryUpdate) -> Library | None:
        library = self.get_library(library_id)
        if not library:
            return None

        if library_update.title is not None:
            library.update_library_title(library_update.title)
        if library_update.description is not None:
            library.update_library_description(library_update.description)
        if library_update.index_type is not None:
            library.update_index_type(library_update.index_type)
        if library_update.metadata is not None:
            library.update_metadata(library_update.metadata)

        return self.save_library(library)

    def save_library(self, library: Library) -> Library:
        try:
            return self.queue_manager.enqueue_operation(
                "library",
                library.get_library_id(),
                self.library_repository.save_library,
                library
            )
        except ValueError as e:
            logger.error(f"Error saving library {library.get_library_id()}: {str(e)}")
            raise

    def delete_library(self, library_id: UUID) -> bool:
        # First check if library exists
        library = self.get_library(library_id)
        if not library:
            return False

        # Use a transaction for atomic deletion
        def delete_operation():
            with self.library_repository.libraries.database.client.start_session() as session:
                with session.start_transaction():
                    for document_id in library.get_all_doc_ids():
                        document = self.document_repository.get_document(document_id)
                        if document:
                            for chunk_id in document.get_all_chunks():
                                self.chunk_repository.delete_chunk(chunk_id)
                        self.document_repository.delete_document(document_id)

                    # Finally delete the library
                    return self.library_repository.delete_library(library_id)

        return self.queue_manager.enqueue_operation(
            "library",
            library_id,
            delete_operation
        )

    def get_queue_size(self, library_id: UUID) -> int:
        return self.queue_manager.get_queue_size("library", library_id)

    def get_last_processed_time(self, library_id: UUID) -> datetime:
        return self.queue_manager.get_last_processed_time("library", library_id)
