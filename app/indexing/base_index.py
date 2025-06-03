from abc import ABC, abstractmethod
from typing import Optional, Any
from uuid import UUID
import numpy as np

class BaseIndex(ABC):
    """Base class for all vector indexing algorithms."""

    def __init__(self, dimension: int = 1024):
        self.dimension = dimension

    @abstractmethod
    def add_vector(self, vector_id: UUID, vector: list[float]) -> None:
        """Add a vector to the index."""
        pass

    @abstractmethod
    def search(self, query_vector: list[float], k: int = 5) -> list[UUID]:
        """Search for k nearest neighbors."""
        pass

    @abstractmethod
    def delete_vector(self, vector_id: UUID) -> None:
        """Delete a vector from the index."""
        pass

    def _normalize_vector(self, vector: list[float]) -> list[float]:
        """Normalize a vector to unit length."""
        vector = np.array(vector, dtype=np.float32)
        if np.linalg.norm(vector) == 0:
            raise ValueError("Vector is zero")
        normalized_vector = vector / np.linalg.norm(vector)
        return normalized_vector.tolist()

    def _check_vector_dimension(self, vector: list[float]) -> None:
        """Check if vector dimension matches the expected dimension."""
        if len(vector) != self.dimension:
            raise ValueError(f"Vector dimension {len(vector)} does not match index dimension {self.dimension}")

    def _cosine_similarity(self, a: list[float], b: list[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        a_norm = np.linalg.norm(a)
        b_norm = np.linalg.norm(b)
        if a_norm == 0 or b_norm == 0:
            return 0.0
        return np.dot(a, b) / (a_norm * b_norm)

    @abstractmethod
    def get_stats(self) -> dict[str, Any]:
        """Get index statistics."""
        pass

    @abstractmethod
    def serialize(self) -> dict[str, Any]:
        """Serialize the index for storage."""
        pass

    @classmethod
    @abstractmethod
    def deserialize(cls, data: dict[str, Any]) -> 'BaseIndex':
        """Create an index from serialized data."""
        pass 
