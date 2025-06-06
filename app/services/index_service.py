from uuid import UUID
import logging

from app.data_models.library import Library
from app.repository.mongo_repository import MongoRepository
from app.services.queue_manager import QueueManager
from app.indexing.base_index import BaseIndex
from app.indexing.hnsw_index import HNSWIndex
from app.indexing.flat_index import FlatIndex
from app.indexing.ivf_index import IVFIndex
from app.data_models.chunk import Chunk
import cohere
from app.config import co

# Configure logging
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)


class IndexService:
    """Service for managing vector indices."""

    INDEX_TYPES = {"flat": FlatIndex, "ivf": IVFIndex, "hnsw": HNSWIndex}

    def __init__(self, repository: MongoRepository):
        self.library_repository = repository.library_repo
        self.chunk_repository = repository.chunk_repo
        self.queue_manager = QueueManager()

    def get_index_class(self, index_type: str) -> type[BaseIndex]:
        if index_type not in self.INDEX_TYPES:
            raise ValueError(f"Unsupported index type: {index_type}")
        return self.INDEX_TYPES[index_type]

    def get_index(self, library_id: UUID) -> Library:
        return self.queue_manager.enqueue_operation(
            "index",
            library_id,
            self.library_repository.get_library,
            library_id
        )

    def add_vector(self, library_id: UUID, vector_id: UUID, vector: list[float]) -> bool:
        library = self.get_index(library_id)
        if not library:
            return False

        def add_vector_operation():
            try:
                library.add_vector(vector_id, vector)
                return self.library_repository.save_library(library)
            except Exception as e:
                logger.error(f"Error adding vector: {str(e)}")
                raise

        return self.queue_manager.enqueue_operation(
            "index",
            library_id,
            add_vector_operation
        )

    def search_vectors(self, library_id: UUID, query_vector: list[float], k: int = 5) -> list[UUID]:
        library = self.get_index(library_id)
        if not library:
            return []

        return library.search_vectors(query_vector, k)

    def search(self, library_id: UUID, query_text: str, k: int = 3) -> list[Chunk]:
        try:
            # Verify library exists
            if not self.library_repository.get_library(library_id):
                raise ValueError(f"Library {library_id} not found")

            query_embedding = self.generate_query_embedding(query_text)
            results = self.search_vectors(library_id, query_embedding, k=k)
            return [self.chunk_repository.get_chunk(chunk_id) for chunk_id in results]
        except ValueError as e:
            raise ValueError(f"Validation error in search: {str(e)}")

    def delete_vector(self, library_id: UUID, vector_id: UUID) -> bool:
        library = self.get_index(library_id)
        if not library:
            return False

        def delete_vector_operation():
            try:
                library.delete_vector(vector_id)
                return self.library_repository.save_library(library)
            except Exception as e:
                logger.error(f"Error deleting vector: {str(e)}")
                raise

        return self.queue_manager.enqueue_operation(
            "index",
            library_id,
            delete_vector_operation
        )

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

    def generate_query_embedding(self, text: str) -> list[float] | None:
        try:
            response = co.embed(
                texts=[text],
                model="embed-english-v3.0",
                input_type="search_document",
            )
            if response and response.embeddings:
                embedding = response.embeddings[0]
                return embedding
            else:
                raise ValueError("No embedding generated from Cohere API")
        except Exception as e:
            raise ValueError(f"Error generating query embedding: {str(e)}")
