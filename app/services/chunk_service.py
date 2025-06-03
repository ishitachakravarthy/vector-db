from uuid import UUID
import logging

from app.data_models.chunk import Chunk
from app.repository.mongo_repository import MongoRepository

logger = logging.getLogger(__name__)


class ChunkService:
    def __init__(self, repository: MongoRepository):
        self.chunk_repository = repository.chunk_repo
        self.document_repository = repository.document_repo

    def get_chunk(self, chunk_id: UUID) -> Chunk:
        return self.chunk_repository.get_chunk(chunk_id)

    def list_chunks(self) -> list[Chunk]:
        return self.chunk_repository.list_chunks()

    def save_chunk(self, chunk: Chunk) -> Chunk:
        document = self.document_repository.get_document(chunk.get_document_id())
        saved_chunk = self.chunk_repository.save_chunk(chunk)
        try:
            document.add_chunk(saved_chunk.id)
            self.document_repository.save_document(document)
        except Exception as e:
            raise ValueError(
                f"Could not update document with ID {chunk.get_document_id()} with chunk"
            )
        return saved_chunk

    def delete_chunk(self, chunk_id: UUID) -> bool:
        delete_chunk = self.chunk_repository.get_chunk(chunk_id)
        new_doc = self.document_repository.get_document(delete_chunk.get_document_id())
        try:
            new_doc.remove_chunk(chunk_id)
            self.document_repository.save_document(new_doc)
        except Exception as e:
            raise ValueError(
                f"Could not update document with ID {delete_chunk.get_document_id()} to remove chunk"
            )
        return self.chunk_repository.delete_chunk(chunk_id)
