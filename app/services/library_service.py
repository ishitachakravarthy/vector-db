from typing import List, Optional
from uuid import UUID
import logging

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

    def update_library(self, library_id: UUID, library_update: LibraryUpdate) -> Library | None:
        try:
            return self.queue_manager.enqueue_operation(
                "library",
                library_id,
                self.library_repository.update_library,
                library_id,
                library_update
            )
        except Exception as e:
            logger.error(f"Error updating library: {str(e)}")
            return None

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
