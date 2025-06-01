from typing import List, Optional
from uuid import UUID
import logging

from app.data_models.chunk import Chunk
from app.repository.mongo_repository import MongoRepository

logger = logging.getLogger(__name__)


class ChunkService:
    def __init__(self, repository: MongoRepository):
        self.repository = repository.chunk_repo
        self.document_repo = repository.document_repo

    def create_chunk(self, chunk: Chunk) -> Chunk:
        """Create a new chunk and add it to its document."""
        # Verify document exists
        document = self.document_repo.get_document(chunk.document_id)
        if not document:
            raise ValueError(f"Document with ID {chunk.document_id} does not exist")
        
        try:
            # Save the chunk to the database
            saved_chunk = self.repository.save_chunk(chunk)
            
            # Add chunk to document
            document.add_chunk(saved_chunk.id)
            self.document_repo.save_document(document)
            
            return saved_chunk
        except Exception as e:
            logger.error(f"Error creating chunk: {str(e)}")
            raise

    def get_chunk(self, chunk_id: UUID) -> Optional[Chunk]:
        """Get a chunk by its ID."""
        return self.repository.get_chunk(chunk_id)

    def list_chunks(self) -> list[Chunk]:
        """List all chunks."""
        return self.repository.list_chunks()

    def delete_chunk(self, chunk_id: UUID) -> bool:
        """Delete a chunk and remove it from its document."""
        chunk = self.get_chunk(chunk_id)
        if not chunk:
            return False
            
        document = self.document_repo.get_document(chunk.document_id)
        if document:
            document.remove_chunk(chunk_id)
            self.document_repo.save_document(document)
            
        return self.repository.delete_chunk(chunk_id)

