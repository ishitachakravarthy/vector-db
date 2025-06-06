from typing import List, Optional
from uuid import UUID

from app.data_models.library import Library, LibraryCreate, LibraryUpdate
from app.data_models.metadata import LibraryMetadata
from app.repository.mongo_repository import MongoRepository
from app.services.queue_manager import QueueManager


class LibraryService:
    def __init__(self, repository: MongoRepository):
        self.document_repository = repository.document_repo
        self.library_repository = repository.library_repo
        self.chunk_repository = repository.chunk_repo
        self.queue_manager = QueueManager()

    async def get_library(self, library_id: UUID) -> Library:
        try:
            return await self.queue_manager.enqueue_operation(
                "library",
                library_id,
                self.library_repository.get_library,
                library_id
            )
        except Exception as e:
            raise ValueError("Service error: Failed to queue library retrieval") from e

    async def list_libraries(self) -> List[Library]:
        try:
            return await self.queue_manager.enqueue_operation(
                "library",
                UUID(int=0),  # Use a dummy UUID for list operations
                self.library_repository.list_libraries
            )
        except Exception as e:
            raise ValueError("Service error: Failed to queue library listing") from e

    async def create_library(self, library_create: LibraryCreate) -> Library:
        try:
            # Create metadata if not provided
            metadata = library_create.metadata or LibraryMetadata(
                is_public=False,
                language="en"
            )
            
            library = Library(
                title=library_create.title,
                description=library_create.description,
                index_type=library_create.index_type,
                metadata=metadata
            )
            return await self.save_library(library)
        except Exception as e:
            raise ValueError(f"Service error: Failed to create library: {str(e)}") from e

    async def update_library(self, library_id: UUID, library_update: LibraryUpdate) -> Library:
        try:
            return await self.queue_manager.enqueue_operation(
                "library",
                library_id,
                self.library_repository.update_library,
                library_id,
                library_update
            )
        except Exception as e:
            raise ValueError("Service error: Failed to queue library update") from e

    async def save_library(self, library: Library) -> Library:
        try:
            return await self.queue_manager.enqueue_operation(
                "library",
                library.id,
                self.library_repository.save_library,
                library
            )
        except Exception as e:
            raise ValueError(f"Service error: Failed to save library: {str(e)}") from e

    async def delete_library(self, library_id: UUID) -> bool:
        try:
            library = await self.get_library(library_id)
            if not library:
                raise ValueError(f"Library with ID {library_id} not found")

            async def delete_operation():
                with self.library_repository.libraries.database.client.start_session() as session:
                    with session.start_transaction():
                        for document_id in library.get_all_doc_ids():
                            document = await self.document_repository.get_document(document_id)
                            if document:
                                for chunk_id in document.get_all_chunks():
                                    await self.chunk_repository.delete_chunk(chunk_id)
                            await self.document_repository.delete_document(document_id)
                        return await self.library_repository.delete_library(library_id)

            return await self.queue_manager.enqueue_operation(
                "library",
                library_id,
                delete_operation
            )
        except Exception as e:
            raise ValueError("Service error: Failed to delete library and its contents") from e
