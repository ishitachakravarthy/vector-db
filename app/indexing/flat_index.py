from uuid import UUID
from .base_index import BaseIndex
from typing import Any
import logging

logger = logging.getLogger(__name__)


class FlatIndex(BaseIndex):
    def __init__(self):
        self.vectors: dict[UUID, list[float]] = {}
        self.dimension: int | None = None

    def add_vector(self, chunk_id: UUID, vector: list[float]) -> None:
        self.vectors[chunk_id] = vector

    def delete_vector(self, chunk_id: UUID) -> None:
        if chunk_id in self.vectors:
            del self.vectors[chunk_id]

    def search(self, query_vector: list[float], k: int = 5) -> list[UUID]:
        if not self.vectors:
            return []
        similarities = []
        for chunk_id, vector in self.vectors.items():
            similarity = self._cosine_similarity(query_vector, vector)
            similarities.append((chunk_id, similarity))
        similarities.sort(key=lambda x: x[1], reverse=True)
        return [vec_id for vec_id, _ in similarities[:k]]

    def get_stats(self) -> dict[str, any]:
        return {
            "type": "flat",
            "num_vectors": len(self.vectors),
            "dimension": self.dimension,
        }

    def serialize(self) -> dict[str, any]:
        try:
            vectors_dict = {
                str(vector_id): vector for vector_id, vector in self.vectors.items()
            }
            return {
                "type": "flat",
                "vectors": vectors_dict,
                "dimension": self.dimension,
            }
        except Exception as e:
            logger.error(f"Error serializing Flat index: {str(e)}")
            raise

    @classmethod
    def deserialize(cls, data: dict[str, any]) -> "FlatIndex":
        index = cls()
        index.dimension = data["dimension"]
        index.vectors = {UUID(k): v for k, v in data["vectors"].items()}
        return index