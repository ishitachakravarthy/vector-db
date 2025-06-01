from typing import List, Dict, Any, Optional
from uuid import UUID
import logging
from app.repository.mongo_repository import MongoRepository
from app.indexing.hnsw_index import HNSWIndex
from app.indexing.flat_index import FlatIndex

logger = logging.getLogger(__name__)

class IndexService:
    """Service for managing vector indexes."""

    # Map of index type names to their classes
    INDEX_TYPES = {
        "flat": FlatIndex,
        "hnsw": HNSWIndex
    }

    def __init__(self, repository: MongoRepository):
        """Initialize the index service."""
        self.repository = repository
        self.loaded_indexes: Dict[UUID, Any] = {}  # Cache for loaded indexes

    def get_index_type(self, index_type: str) -> Any:
        """Get the index class for a given type."""
        if index_type not in self.INDEX_TYPES:
            raise ValueError(f"Unsupported index type: {index_type}")
        return self.INDEX_TYPES[index_type]

    def initialize_index(self, library_id: UUID, index_type: str = "flat") -> Any:
        """Initialize a new index for a library."""
        try:
            # Get the index class
            index_class = self.get_index_type(index_type)

            # Create new index
            index = index_class()

            # Update library's index type and data
            library = self.repository.library_repo.get_library(library_id)
            if library:
                library.index_type = index_type
                library.index_data = index.serialize()
                self.repository.library_repo.save_library(library)
            else:
                raise ValueError(f"Library with ID {library_id} not found")

            # Cache the index
            self.loaded_indexes[library_id] = index

            return index
        except Exception as e:
            logger.error(f"Error initializing index: {str(e)}")
            raise

    def get_index(self, library_id: UUID) -> Any:
        """Get the index for a library, loading it if necessary."""
        try:
            # Check if index is already loaded
            if library_id in self.loaded_indexes:
                return self.loaded_indexes[library_id]

            # Get library and its index type
            library = self.repository.library_repo.get_library(library_id)
            if not library:
                raise ValueError(f"Library with ID {library_id} not found")

            index_type = library.index_type or "flat"
            index_class = self.get_index_type(index_type)

            # Create new index
            index = index_class()

            # Load index data if it exists
            if library.index_data:
                index.deserialize(library.index_data)

            # Load vectors into index
            vectors = self.repository.library_repo.get_library_vectors(library_id)
            for vector_id, vector in vectors.items():
                index.add_vector(vector_id, vector)

            # Cache the index
            self.loaded_indexes[library_id] = index

            return index
        except Exception as e:
            logger.error(f"Error getting index: {str(e)}")
            raise

    def add_vector(self, library_id: UUID, vector_id: UUID, vector: List[float]) -> None:
        """Add a vector to the index."""
        try:
            index = self.get_index(library_id)
            index.add_vector(vector_id, vector)

            # Update library's index data
            library = self.repository.library_repo.get_library(library_id)
            if library:
                library.index_data = index.serialize()
                self.repository.library_repo.save_library(library)
        except Exception as e:
            logger.error(f"Error adding vector to index: {str(e)}")
            raise

    def search_vectors(self, library_id: UUID, query_vector: List[float], k: int = 5) -> List[UUID]:
        """Search for k nearest neighbors."""
        try:
            index = self.get_index(library_id)
            results = index.search(query_vector, k)
            
            return results
        except Exception as e:
            logger.error(f"Error searching vectors: {str(e)}")
            raise

    def delete_vector(self, library_id: UUID, vector_id: UUID) -> None:
        """Delete a vector from the index."""
        try:
            index = self.get_index(library_id)
            index.delete_vector(vector_id)

            # Update library's index data
            library = self.repository.library_repo.get_library(library_id)
            if library:
                library.index_data = index.serialize()
                self.repository.library_repo.save_library(library)
        except Exception as e:
            logger.error(f"Error deleting vector from index: {str(e)}")
            raise

    def get_index_stats(self, library_id: UUID) -> Dict[str, Any]:
        """Get statistics about the index."""
        try:
            index = self.get_index(library_id)
            return index.get_stats()
        except Exception as e:
            logger.error(f"Error getting index stats: {str(e)}")
            raise 
