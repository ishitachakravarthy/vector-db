from uuid import UUID
import numpy as np
from .base_index import BaseIndex

class FlatIndex(BaseIndex):
    def __init__(self):
        self.vectors: dict[UUID, list[float]] = {}
        self.dimension: int|None = None

    def _check_vector_dimension(self, vector: list[float], operation: str) -> None:
        """Check if vector dimension matches the index dimension."""
        if self.dimension is None:
            self.dimension = len(vector)
        elif len(vector) != self.dimension:
            raise ValueError(f"Vector dimension {len(vector)} does not match index dimension {self.dimension} for {operation}")

    def _cosine_similarity(self, a: list[float], b: list[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        a_norm = np.linalg.norm(a)
        b_norm = np.linalg.norm(b)
        if a_norm == 0 or b_norm == 0:
            return 0.0
        return np.dot(a, b) / (a_norm * b_norm)

    def add_vector(self, vector_id: UUID, vector: list[float]) -> None:
        """Add a vector to the index."""
        self._check_vector_dimension(vector, "adding vector")
        self.vectors[vector_id] = vector

    def search(self, query_vector: list[float], k: int = 5) -> list[UUID]:
        """Search for k nearest neighbors using exhaustive search."""
        if not self.vectors:
            return []
        self._check_vector_dimension(query_vector, "searching")
        similarities = []
        for vec_id, vec in self.vectors.items():
            similarity = self._cosine_similarity(query_vector, vec)
            similarities.append((vec_id, similarity))
        similarities.sort(key=lambda x: x[1], reverse=True)
        return [vec_id for vec_id, _ in similarities[:k]]

    def delete_vector(self, vector_id: UUID) -> None:
        """Delete a vector from the index."""
        if vector_id in self.vectors:
            del self.vectors[vector_id]

    def get_stats(self) -> dict[str, any]:
        """Get statistics about the index."""
        return {
            "type": "flat",
            "num_vectors": len(self.vectors),
            "dimension": self.dimension,
        }

    def serialize(self) -> dict[str, any]:
        """Serialize the index for storage."""
        return {
            "type": "flat",
            "vectors": {str(k): v for k, v in self.vectors.items()},
            "dimension": self.dimension
        }

    @classmethod
    def deserialize(cls, data: dict[str, any]) -> 'FlatIndex':
        """Create an index from serialized data."""
        index = cls()
        index.dimension = data["dimension"]
        index.vectors = {UUID(k): v for k, v in data["vectors"].items()}
        return index
