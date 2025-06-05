from typing import List, Dict, Any, Optional, Set, Tuple
import numpy as np
import logging
from uuid import UUID
import random
import math
from .base_index import BaseIndex

logger = logging.getLogger(__name__)


class HNSWIndex(BaseIndex):
    """Hierarchical Navigable Small World (HNSW) index for vector similarity search."""

    NUM_LAYERS = 10

    def __init__(self, M: int = 16, ef_construction: int = 5):
        self.M: int = M
        self.ef_construction: int = ef_construction
        self.vectors: Dict[UUID, list[float]] = {}
        self.layers = [{} for _ in range(self.NUM_LAYERS)]
        self.entry_points = [None] * self.NUM_LAYERS

    def _get_random_layer(self) -> int:
        scale = self.M / 4
        layer = min(int(-math.log(random.random()) * scale), len(self.layers) - 1)
        return layer

    def _search_layer(
        self,
        query_vector: list[float],
        layer: int,
        k: int,
        start_id: Optional[UUID] = None,
    ) -> List[Tuple[UUID, float]]:
        if not self.entry_points[layer]:
            return []
        # Start from provided start_id or layer's entry point
        start_id = start_id or self.entry_points[layer]
        start_similarity = self._cosine_similarity(query_vector, self.vectors[start_id])
        candidates = [(start_id, start_similarity)]
        visited = {start_id}
        result = []
        # Search for k neighbors in the layer
        while candidates:
            current_id, current_similarity = candidates.pop(0)
            result.append((current_id, current_similarity))
            # Check all neighbors of current vector
            for neighbor in self.layers[layer].get(current_id, set()):
                if neighbor not in visited:
                    visited.add(neighbor)
                    similarity = self._cosine_similarity(
                        query_vector, self.vectors[neighbor]
                    )
                    candidates.append((neighbor, similarity))
        # sort candidates by similarity and return top ef
        return sorted(result, key=lambda x: x[1], reverse=True)[:k]

    def add_vector(self, chunk_id: UUID, vector: List[float]) -> None:
        try:
            self.vectors[chunk_id] = vector
            layer = self._get_random_layer()
            # Process all layers from bottom to top
            for l in range(layer + 1):
                self.layers[l][chunk_id] = set()
                # Find M neighbors for each layer
                candidates = self._search_layer(vector, l, self.M)
                neighbors = {c[0] for c in candidates}
                # Create connections
                for neighbor in neighbors:
                    self.layers[l][chunk_id].add(neighbor)
                    self.layers[l][neighbor].add(chunk_id)
                # Set as entry point if layer is empty
                if not self.entry_points[l]:
                    self.entry_points[l] = chunk_id
        except Exception as e:
            raise ValueError(f"Failed to add HNSW index")

    def search(self, query_vector: List[float], k: int = 3) -> List[UUID]:
        if not self.vectors:
            return []
        current_layer = self.NUM_LAYERS - 1
        all_candidates = []
        try:
            # Start from highest layer's entry point
            current_id = self.entry_points[current_layer]
            # Search through layers with best candidate as entry point
            while current_layer > 0:
                candidates = self._search_layer(
                    query_vector, current_layer, self.ef_construction, current_id
                )
                if candidates:
                    current_id = candidates[0][0]
                current_layer -= 1
            # Final search in bottom layer
            bottom_layer_candidates = self._search_layer(
                query_vector, 0, max(k * 2, 10), current_id
            )
            all_candidates.extend(bottom_layer_candidates)
            # Return top k results
            sorted_candidates = sorted(
                all_candidates, key=lambda x: x[1], reverse=True
            )[:k]
            return [c[0] for c in sorted_candidates]
        except Exception as e:
            raise ValueError(f"Failed to search HNSW index")

    def delete_vector(self, chunk_id: UUID) -> None:
        # Remove vector from all layers
        for layer in self.layers:
            if chunk_id in layer:
                for neighbor in layer[chunk_id]:
                    if neighbor in layer:
                        layer[neighbor].remove(chunk_id)
                del layer[chunk_id]
        # Remove vector from vectors
        if chunk_id in self.vectors:
            del self.vectors[chunk_id]
        # Update entry points
        for i, entry_point in enumerate(self.entry_points):
            if entry_point == chunk_id:
                if self.layers[i]:
                    self.entry_points[i] = list(self.layers[i].keys())[0]
                else:
                    self.entry_points[i] = None

    def get_stats(self) -> Dict[str, Any]:
        return {
            "current_elements": len(self.vectors),
            "M": self.M,
            "ef_construction": self.ef_construction,
            "layers": [
                {str(chunk_id): len(neighbors) for chunk_id, neighbors in layer.items()}
                for layer in self.layers
            ],
        }

    def serialize(self) -> Dict[str, Any]:
        try:
            return {
                "vectors": {
                    str(chunk_id): vector for chunk_id, vector in self.vectors.items()
                },
                "layers": [
                    {
                        str(chunk_id): [str(n) for n in neighbors]
                        for chunk_id, neighbors in layer.items()
                    }
                    for layer in self.layers
                ],
                "entry_points": [str(ep) if ep else None for ep in self.entry_points],
                "M": self.M,
                "ef_construction": self.ef_construction,
            }
        except Exception as e:
            raise ValueError(f"Error serializing HNSW index: {str(e)}")

    @classmethod
    def deserialize(cls, data: Dict[str, Any]) -> "HNSWIndex":
        try:
            index = cls(M=data["M"], ef_construction=data["ef_construction"])
            index.vectors = {
                UUID(chunk_id): vector for chunk_id, vector in data["vectors"].items()
            }
            index.layers = [
                {
                    UUID(chunk_id): {UUID(n) for n in neighbors}
                    for chunk_id, neighbors in layer.items()
                }
                for layer in data["layers"]
            ]
            index.entry_points = [
                UUID(ep) if ep else None for ep in data["entry_points"]
            ]
            return index
        except Exception as e:
            raise ValueError(f"Error deserializing HNSW index: {str(e)}")
