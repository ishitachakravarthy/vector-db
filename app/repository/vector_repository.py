from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime
from pymongo.collection import Collection
from app.data_models.chunk import Chunk
from app.repository.base_repository import BaseRepository
import logging

logger = logging.getLogger(__name__)

class VectorRepository(BaseRepository):
    """Repository for managing vector embeddings in MongoDB."""
    
    def __init__(self):
        super().__init__()
        self.vectors: Collection = self.db.vectors
        self.init_indexes()
        
    def init_indexes(self) -> None:
        """Initialize database indexes."""
        try:
            # First, clean up any documents with null chunk_ids
            self.vectors.delete_many({"chunk_id": None})
            
            # Drop existing indexes
            self.vectors.drop_indexes()
            
            # Create new indexes with sparse option
            self.vectors.create_index("document_id")
            self.vectors.create_index("chunk_id", unique=True, sparse=True)
            
            logger.info("Successfully initialized vector indexes")
        except Exception as e:
            logger.error(f"Error initializing indexes: {str(e)}")
            raise
        
    def save_embedding(self, chunk: Chunk) -> Chunk:
        """Save a chunk's embedding.
        
        Args:
            chunk: Chunk with embedding to save
            
        Returns:
            Updated chunk
        """
        try:
            if not chunk.id:
                raise ValueError("Chunk ID cannot be null")
                
            now = datetime.utcnow()
            
            # Prepare document
            doc = {
                "chunk_id": chunk.id,
                "document_id": chunk.document_id,
                "embedding": chunk.embedding,
                "index_type": chunk.index_type,
                "metadata": chunk.metadata,
                "created_at": now,
                "updated_at": now
            }
            
            # Insert or update document
            self.vectors.update_one(
                {"chunk_id": chunk.id},
                {"$set": doc},
                upsert=True
            )
            
            return chunk
        except Exception as e:
            logger.error(f"Error saving embedding: {str(e)}")
            raise
        
    def get_embedding(self, chunk_id: UUID) -> Optional[Chunk]:
        """Get a chunk's embedding.
        
        Args:
            chunk_id: ID of the chunk
            
        Returns:
            Chunk with embedding if found, None otherwise
        """
        try:
            if not chunk_id:
                raise ValueError("Chunk ID cannot be null")
                
            doc = self.vectors.find_one({"chunk_id": chunk_id})
            if not doc:
                return None
                
            return Chunk(
                id=doc["chunk_id"],
                document_id=doc["document_id"],
                text="",  # Text is stored in chunks collection
                embedding=doc["embedding"],
                index_type=doc["index_type"],
                metadata=doc["metadata"]
            )
        except Exception as e:
            logger.error(f"Error getting embedding: {str(e)}")
            raise
        
    def delete_embedding(self, chunk_id: UUID) -> bool:
        """Delete a chunk's embedding.
        
        Args:
            chunk_id: ID of the chunk
            
        Returns:
            True if deleted, False otherwise
        """
        try:
            if not chunk_id:
                raise ValueError("Chunk ID cannot be null")
                
            result = self.vectors.delete_one({"chunk_id": chunk_id})
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"Error deleting embedding: {str(e)}")
            raise
        
    def list_embeddings(self, document_id: UUID) -> List[Chunk]:
        """List all embeddings for a document.
        
        Args:
            document_id: ID of the document
            
        Returns:
            List of chunks with embeddings
        """
        try:
            if not document_id:
                raise ValueError("Document ID cannot be null")
                
            docs = self.vectors.find({"document_id": document_id})
            return [
                Chunk(
                    id=doc["chunk_id"],
                    document_id=doc["document_id"],
                    text="",  # Text is stored in chunks collection
                    embedding=doc["embedding"],
                    index_type=doc["index_type"],
                    metadata=doc["metadata"]
                )
                for doc in docs
            ]
        except Exception as e:
            logger.error(f"Error listing embeddings: {str(e)}")
            raise 