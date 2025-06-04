from uuid import UUID
import logging
from app.repository.mongo_repository import MongoRepository
from app.indexing.base_index import BaseIndex
from app.indexing.hnsw_index import HNSWIndex
from app.indexing.flat_index import FlatIndex
from app.indexing.ivf_index import IVFIndex

# Configure logging
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)


class IndexService:
    """Service for managing vector indices."""

    INDEX_TYPES = {"flat": FlatIndex, "ivf": IVFIndex, "hnsw": HNSWIndex}

    def __init__(self, repository: MongoRepository):
        self.library_repository = repository.library_repo

    def get_index_class(self, index_type: str) -> type[BaseIndex]:
        if index_type not in self.INDEX_TYPES:
            raise ValueError(f"Unsupported index type: {index_type}")
        return self.INDEX_TYPES[index_type]

    def get_index(self, library_id: UUID) -> BaseIndex:
        try:
            index_type = self.library_repository.get_index_type(library_id)
            index_class = self.get_index_class(index_type)
            index_data = self.library_repository.get_index_data(library_id)

            if index_data:
                index = index_class.deserialize(index_data)
            else:
                index = index_class()
            return index
        except Exception as e:
            raise ValueError(f"Error getting/initializing index: {str(e)}")

    def add_vector(self, library_id: UUID, chunk_id: UUID, vector: list[float]) -> None:
        try:
            index = self.get_index(library_id)
            index.add_vector(chunk_id, vector)
            self.save_new_index(library_id, None, index)
        except Exception as e:
            raise ValueError(f"Error adding vector to index: {str(e)}")

    def search_vectors(
        self, library_id: UUID, query_vector: list[float], k: int = 3
    ) -> list[UUID]:
        try:
            index = self.get_index(library_id)
            results = index.search(query_vector, k)
            if not results:
                logger.warning(f"No results found for query in library {library_id}")
            return results
        except Exception as e:
            logger.error(f"Error searching vectors: {str(e)}")
            raise

    def delete_vector(self, library_id: UUID, chunk_id: UUID) -> None:
        try:
            index = self.get_index(library_id)
            index.delete_vector(chunk_id)
            self.save_new_index(library_id, None, index)
        except Exception as e:
            logger.error(f"Error deleting vector from index: {str(e)}")
            raise

    def get_index_stats(self, library_id: UUID) -> dict:
        try:
            index = self.get_index(library_id)
            return index.get_stats()
        except Exception as e:
            raise ValueError(f"Error getting index stats: {str(e)}")

    def save_new_index(
        self, library_id: UUID, index_type: str | None, index: BaseIndex | None
    ) -> None:
        if index_type:
            self.library_repository.update_index_type(library_id, index_type)
        if index:
            self.library_repository.update_index_data(library_id, index.serialize())
