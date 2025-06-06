from uuid import UUID
import logging
from typing import Optional

from app.data_models.chunk import Chunk, ChunkCreate, ChunkUpdate
from app.repository.mongo_repository import MongoRepository
from app.services.queue_manager import QueueManager

logger = logging.getLogger(__name__)


class ChunkService:
    def __init__(self, repository: MongoRepository):
        self.chunk_repository = repository.chunk_repo
        self.document_repository = repository.document_repo
        self.queue_manager = QueueManager()

    def get_chunk(self, chunk_id: UUID) -> Chunk:
        return self.queue_manager.enqueue_operation(
            "chunk",
            chunk_id,
            self.chunk_repository.get_chunk,
            chunk_id
        )

    def list_chunks(self) -> list[Chunk]:
        return self.chunk_repository.list_chunks()

    def create_chunk(self, chunk_create: ChunkCreate) -> Chunk:
        chunk = Chunk(
            text=chunk_create.text,
            document_id=chunk_create.document_id,
            metadata=chunk_create.metadata
        )
        return self.save_chunk(chunk)

    def update_chunk(self, chunk_id: UUID, chunk_update: ChunkUpdate) -> Optional[Chunk]:
        try:
            return self.queue_manager.enqueue_operation(
                "chunk",
                chunk_id,
                self.chunk_repository.update_chunk,
                chunk_id,
                chunk_update
            )
        except Exception as e:
            logger.error(f"Error updating chunk: {str(e)}")
            return None

    def save_chunk(self, chunk: Chunk) -> Chunk:
        try:
            saved_chunk = self.queue_manager.enqueue_operation(
                "chunk", chunk.get_chunk_id(), self.chunk_repository.save_chunk, chunk
            )

            # Update document in a separate operation
            document = self.document_repository.get_document(
                saved_chunk.get_document_id()
            )
            document.add_chunk(saved_chunk.get_chunk_id())
            self.document_repository.save_document(document)

            return saved_chunk
        except Exception as e:
            logger.error(f"Error saving chunk: {str(e)}")
            raise

    def delete_chunk(self, chunk_id: UUID) -> bool:
        chunk = self.get_chunk(chunk_id)
        document = self.document_repository.get_document(chunk.get_document_id())

        def delete_operation():
            try:
                # Update document
                document.delete_chunk(chunk_id)
                self.document_repository.save_document(document)

                # Delete chunk
                return self.chunk_repository.delete_chunk(chunk_id)
            except Exception as e:
                logger.error(f"Error in delete operation: {str(e)}")
                raise

        return self.queue_manager.enqueue_operation(
            "chunk",
            chunk_id,
            delete_operation
        )
