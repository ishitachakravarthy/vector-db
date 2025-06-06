from uuid import UUID
from typing import Optional

from app.data_models.chunk import Chunk, ChunkCreate, ChunkUpdate
from app.repository.mongo_repository import MongoRepository
from app.services.queue_manager import QueueManager

class ChunkService:
    def __init__(self, repository: MongoRepository):
        self.chunk_repository = repository.chunk_repo
        self.document_repository = repository.document_repo
        self.queue_manager = QueueManager()

    def get_chunk(self, chunk_id: UUID) -> Chunk:
        try:
            return self.queue_manager.enqueue_operation(
                "chunk",
                chunk_id,
                self.chunk_repository.get_chunk,
                chunk_id
            )
        except Exception as e:
            raise ValueError("Service error: Failed to queue chunk retrieval") from e

    def list_chunks(self) -> list[Chunk]:
        return self.chunk_repository.list_chunks()

    def create_chunk(self, chunk_create: ChunkCreate) -> Chunk:
        try:
            chunk = Chunk(
                text=chunk_create.text,
                document_id=chunk_create.document_id,
                metadata=chunk_create.metadata
            )
            return self.save_chunk(chunk)
        except Exception as e:
            raise ValueError("Service error: Failed to create chunk") from e

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
            raise ValueError("Service error: Failed to update chunk") from e

    def save_chunk(self, chunk: Chunk) -> Chunk:
        try:
            saved_chunk: Chunk = self.queue_manager.enqueue_operation(
                "chunk", chunk.get_chunk_id(), self.chunk_repository.save_chunk, chunk
            )
            document = self.document_repository.get_document(saved_chunk.get_document_id())
            if not document:
                raise ValueError(f"Document with ID {saved_chunk.get_document_id()} not found")
            document.add_chunk(saved_chunk.get_chunk_id())
            self.document_repository.save_document(document)
            return saved_chunk
        except Exception as e:
            raise ValueError("Service error: Failed to save chunk and update document") from e

    def delete_chunk(self, chunk_id: UUID) -> bool:
        try:
            chunk = self.get_chunk(chunk_id)
            document = self.document_repository.get_document(chunk.get_document_id())
            if not document:
                raise ValueError(f"Document with ID {chunk.get_document_id()} not found")
            document.delete_chunk(chunk_id)
            self.document_repository.save_document(document)
            return self.queue_manager.enqueue_operation(
                "chunk",
                chunk_id,
                self.chunk_repository.delete_chunk,
                chunk_id
            )
        except Exception as e:
            raise ValueError("Service error: Failed to delete chunk and update document") from e
