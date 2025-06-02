from typing import List, Dict, Any, Optional, Set
import numpy as np
import logging
from uuid import UUID
import pickle
import os
from pathlib import Path
from sklearn.cluster import KMeans
from collections import defaultdict

logger = logging.getLogger(__name__)

class IVFIndex:
    """Inverted File (IVF) index for vector similarity search."""

    def __init__(self, dimension: int = 1024, max_elements: int = 10000, n_clusters: int = 100, n_probe: int = 10):
        """Initialize IVF index."""
        self.dimension = dimension
        self.max_elements = max_elements
        self.n_clusters = n_clusters
        self.n_probe = n_probe
        self.vectors: Dict[UUID, np.ndarray] = {}
        self.cluster_centers: Optional[np.ndarray] = None
        self.cluster_assignments: Dict[int, Set[UUID]] = defaultdict(set)
        self.initialized = False
        self.kmeans: Optional[KMeans] = None

    def initialize(self) -> None:
        """Initialize the IVF index structure."""
        self.kmeans = KMeans(
                n_clusters=self.n_clusters,
                random_state=42,
                n_init=10
            )
        self.initialized = True

    def _cosine_similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        """Calculate cosine similarity between two vectors."""
        a_norm = np.linalg.norm(a)
        b_norm = np.linalg.norm(b)
        if a_norm == 0 or b_norm == 0:
            return 0.0
        return np.dot(a, b) / (a_norm * b_norm)

    def _get_closest_clusters(self, query: np.ndarray, n_probe: int) -> List[int]:
        """Get the n_probe closest clusters to the query vector."""
        if self.cluster_centers is None:
            return []
        # Calculate distances to all cluster centers
        distances = np.array([
            self._cosine_similarity(query, center)
            for center in self.cluster_centers
        ])
        # Get indices of n_probe closest clusters
        return np.argsort(distances)[-n_probe:][::-1].tolist()

    def add_vector(self, id: UUID, vector: List[float]) -> None:
        """Add a vector to the index."""
        if not self.initialized:
            self.initialize()

        if len(self.vectors) >= self.max_elements:
            raise ValueError("Index is full")

        # Convert and normalize vector
        vector_array = np.array(vector)
        vector_array = vector_array / np.linalg.norm(vector_array)
        self.vectors[id] = vector_array

        # Assign to nearest cluster
        if self.cluster_centers is not None:
            cluster_id = self.kmeans.predict(vector_array.reshape(1, -1))[0]
            self.cluster_assignments[cluster_id].add(id)
        else:
            # If not trained yet, add to a temporary cluster
            self.cluster_assignments[0].add(id)
        logger.info(f"Added vector for ID {id} to IVF index")

    def delete_vector(self, id: UUID) -> None:
        """Delete a vector from the index."""

        if not self.initialized:
            raise ValueError("Index not initialized")

        # Remove vector from storage
        if id in self.vectors:
            del self.vectors[id]

        # Remove vector from cluster assignments
        for cluster_id in self.cluster_assignments:
            if id in self.cluster_assignments[cluster_id]:
                self.cluster_assignments[cluster_id].remove(id)

        # Save changes to MongoDB
        self._save_to_mongo()

        logger.info(f"Deleted vector {id} from IVF index")

    def search_vectors(self, query_vector: List[float], k: int = 3) -> List[UUID]:
        """Search for similar vectors. """
        if not self.initialized or not self.vectors:
            raise ValueError("Index not initialized or empty")

        # Convert and normalize query vector
        query_array = np.array(query_vector)
        query_array = query_array / np.linalg.norm(query_array)

        # Get closest clusters
        closest_clusters = self._get_closest_clusters(query_array, self.n_probe)

        # Search within closest clusters
        candidates = []
        for cluster_id in closest_clusters:
            for vector_id in self.cluster_assignments[cluster_id]:
                sim = self._cosine_similarity(query_array, self.vectors[vector_id])
                candidates.append((vector_id, sim))

        # Sort by similarity and return top k
        candidates.sort(key=lambda x: x[1], reverse=True)
        return [c[0] for c in candidates[:k]]

    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the index."""
        if not self.initialized:
            return {"initialized": False}
        cluster_sizes = {
            cluster_id: len(vector_ids)
            for cluster_id, vector_ids in self.cluster_assignments.items()
        }

        return {
            "initialized": True,
            "dimension": self.dimension,
            "max_elements": self.max_elements,
            "current_elements": len(self.vectors),
            "n_clusters": self.n_clusters,
            "n_probe": self.n_probe,
            "cluster_sizes": cluster_sizes,
            "is_trained": self.cluster_centers is not None
        }
