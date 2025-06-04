import logging
from uuid import UUID
from collections import defaultdict
from typing import Any
from .base_index import BaseIndex

logger = logging.getLogger(__name__)


class IVFIndex(BaseIndex):
    """Inverted File (IVF) index for vector similarity search."""

    def __init__(self, dimension: int = 1024, n_clusters: int = 100, n_probe: int = 10):
        super().__init__(dimension)
        self.n_clusters = n_clusters
        self.n_probe = n_probe
        self.vectors: dict[UUID, list[float]] = {}
        self.cluster_centers: list[list[float]] = []
        self.cluster_assignments: dict[int, set[UUID]] = defaultdict(set)

    def clear_clusters(self) -> None:
        self.cluster_assignments.clear()
        self.cluster_centers = []

    def create_clusters(self) -> None:
        self.clear_clusters()
        if not self.vectors:
            return
        center_ids = list(self.vectors.keys())[:min(len(self.vectors), self.n_clusters)]
        self.cluster_centers = [self.vectors[id] for id in center_ids]
        # Assign vectors to nearest clusters
        for vid, vector in self.vectors.items():
            try:
                cluster_id = self.get_closest_clusters(vector, n_clusters=1)[0]
                self.cluster_assignments[cluster_id].add(vid)
                logger.debug(f"Vector {vid} assigned to cluster {cluster_id}")
            except Exception as e:
                logger.error(f"Error assigning vector {vid} to cluster: {str(e)}")
                raise ValueError(f"Error creating clusters: {str(e)}")

    def get_closest_clusters(self, vector: list[float], n_clusters: int = 1) -> list[int]:
        try:
            if not self.cluster_centers:
                return [0] if n_clusters == 1 else []

            similarities = [self._cosine_similarity(vector, center) for center in self.cluster_centers]
            sorted_indices = sorted(range(len(similarities)), key=lambda i: similarities[i], reverse=True)
            return sorted_indices[:n_clusters]
        except Exception as e:
            raise ValueError(f"Error getting closest clusters")

    def add_vector(self, chunk_id: UUID, vector: list[float]) -> None:
        try:
            vector = self._normalize_vector(vector)
            self.vectors[chunk_id] = vector
            self.create_clusters()
        except Exception as e:
            raise ValueError(f"Error adding vector: {str(e)}")

    def search(self, query_vector: list[float], k: int = 3) -> list[UUID]:
        if not self.vectors:
            return []

        query_vector = self._normalize_vector(query_vector)
        closest_clusters = self.get_closest_clusters(query_vector, self.n_probe)

        candidates = []
        for cluster_id in closest_clusters:
            for vector_id in self.cluster_assignments[cluster_id]:
                sim = self._cosine_similarity(query_vector, self.vectors[vector_id])
                candidates.append((vector_id, sim))

        candidates.sort(key=lambda x: x[1], reverse=True)
        return [c[0] for c in candidates[:k]]

    def delete_vector(self, delete_chunk_id: UUID) -> None:
        if delete_chunk_id not in self.vectors:
            return
        try:
            for cluster_id in self.cluster_assignments:
                if delete_chunk_id in self.cluster_assignments[cluster_id]:
                    self.cluster_assignments[cluster_id].remove(delete_chunk_id)

            del self.vectors[delete_chunk_id]
            self.create_clusters()
        except Exception as e:
            logger.error(f"Error deleting vector {delete_chunk_id}: {str(e)}")
            raise ValueError(f"Error deleting vector: {str(e)}")

    def get_stats(self) -> dict[str, Any]:
        return {
            "dimension": self.dimension,
            "current_elements": len(self.vectors),
            "n_clusters": self.n_clusters,
            "n_probe": self.n_probe,
            "cluster_sizes": {
                cid: len(vids) for cid, vids in self.cluster_assignments.items()
            },
        }

    def serialize(self) -> dict[str, Any]:
        return {
            "vectors": {str(vid): vec for vid, vec in self.vectors.items()},
            "cluster_centers": self.cluster_centers,
            "cluster_assignments": {
                str(cid): [str(v) for v in vecs]
                for cid, vecs in self.cluster_assignments.items()
            },
            "n_clusters": self.n_clusters,
            "dimension": self.dimension,
            "n_probe": self.n_probe,
        }

    @classmethod
    def deserialize(cls, data: dict[str, Any]) -> "IVFIndex":
        index = cls(
            dimension=data["dimension"],
            n_clusters=data["n_clusters"],
            n_probe=data["n_probe"],
        )
        index.vectors = {UUID(vid): vec for vid, vec in data["vectors"].items()}
        index.cluster_centers = data["cluster_centers"]
        index.cluster_assignments = {
            int(cid): {UUID(v) for v in vecs}
            for cid, vecs in data["cluster_assignments"].items()
        }
        return index
