from uuid import UUID
import numpy as np
from .base_index import BaseIndex

class FlatIndex(BaseIndex):
    def __init__(self):
        self.vectors: dict[UUID, list[float]] = {}
        self.dimension: int|None = None

    def _check_vector_dimension(self, vector: list[float]) -> None:
        if self.dimension is None:
            self.dimension = len(vector)
        elif len(vector) != self.dimension:
            raise ValueError(f"Vector dimension {len(vector)} does not match index dimension {self.dimension}")

    def add_vector(self, chunk_id: UUID, vector: list[float]) -> None:
        self._check_vector_dimension(vector)
        self.vectors[chunk_id] = vector

    def search(self, query_vector: list[float], k: int = 5) -> list[UUID]:
        if not self.vectors:
            return []
        self._check_vector_dimension(query_vector)
        similarities = []
        for chunk_id, vector in self.vectors.items():
            similarity = self._cosine_similarity(query_vector, vector)
            similarities.append((chunk_id, similarity))
        similarities.sort(key=lambda x: x[1], reverse=True)
        return [vec_id for vec_id, _ in similarities[:k]]

    def delete_vector(self, chunk_id: UUID) -> None:
        if chunk_id in self.vectors:
            del self.vectors[chunk_id]

    def get_stats(self) -> dict[str, any]:
        return {
            "type": "flat",
            "num_vectors": len(self.vectors),
            "dimension": self.dimension,
        }

    def serialize(self) -> dict[str, any]:
        return {
            "type": "flat",
            "vectors": {k: v for k, v in self.vectors.items()},
            "dimension": self.dimension
        }

    @classmethod
    def deserialize(cls, data: dict[str, any]) -> 'FlatIndex':
        """Create an index from serialized data."""
        index = cls()
        index.dimension = data["dimension"]
        index.vectors = {UUID(k): v for k, v in data["vectors"].items()}
        return index
