from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from uuid import UUID
import numpy as np
class BaseIndex(ABC):
    """Base class for all vector indexing algorithms."""

    @abstractmethod
    def add_vector(self, vector_id: UUID, vector: List[float]) -> None:
        """Add a vector to the index."""
        pass

    @abstractmethod
    def search(self, query_vector: List[float], k: int = 5) -> List[UUID]:
        """Search for k nearest neighbors."""
        pass

    @abstractmethod
    def delete_vector(self, vector_id: UUID) -> None:
        """Delete a vector from the index."""
        pass

    def _cosine_similarity(self, a: list[float], b: list[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        a_norm = np.linalg.norm(a)
        b_norm = np.linalg.norm(b)
        if a_norm == 0 or b_norm == 0:
            return 0.0
        return np.dot(a, b) / (a_norm * b_norm)

    @abstractmethod
    def get_stats(self) -> Dict[str, Any]:
        """Get index statistics."""
        pass

    @abstractmethod
    def serialize(self) -> Dict[str, Any]:
        """Serialize the index for storage."""
        pass

    @classmethod
    @abstractmethod
    def deserialize(cls, data: Dict[str, Any]) -> 'BaseIndex':
        """Create an index from serialized data."""
        pass 
