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
        self.mongo_client = None
        self.library_id = None

    def initialize(self, library_id: UUID, mongo_client) -> None:
        """Initialize the IVF index structure with MongoDB connection."""
        self.library_id = library_id
        self.mongo_client = mongo_client
        self.kmeans = KMeans(
            n_clusters=self.n_clusters,
            random_state=42,
            n_init=10
        )
        self.initialized = True
        self._load_from_mongo()

    def train(self) -> None:
        """Train the KMeans model if we have enough vectors."""
        if not self.initialized:
            raise ValueError("Index not initialized")

        if len(self.vectors) < self.n_clusters:
            logger.warning(f"Not enough vectors ({len(self.vectors)}) to train {self.n_clusters} clusters")
            return

        # Prepare data for training
        vectors_array = np.array(list(self.vectors.values()), dtype=np.float32)

        # Train KMeans
        self.kmeans.fit(vectors_array)
        self.cluster_centers = self.kmeans.cluster_centers_

        # Assign vectors to clusters
        self.cluster_assignments.clear()
        labels = self.kmeans.labels_
        for i, (vector_id, _) in enumerate(self.vectors.items()):
            cluster_id = labels[i]
            self.cluster_assignments[cluster_id].add(vector_id)

        # Save the trained model to MongoDB
        self._save_to_mongo()

        logger.info(f"Trained KMeans model with {self.n_clusters} clusters on {len(self.vectors)} vectors")

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
            self.initialize(None, None)

        if len(self.vectors) >= self.max_elements:
            raise ValueError("Index is full")

        # Convert and normalize vector
        vector_array = np.array(vector, dtype=np.float32)
        vector_array = vector_array / np.linalg.norm(vector_array)
        self.vectors[id] = vector_array

        # If we have enough vectors and haven't trained yet, train the model
        if len(self.vectors) >= self.n_clusters and not self.cluster_centers:
            self.train()
        # If model is trained, assign to nearest cluster
        elif self.cluster_centers is not None:
            cluster_id = self.kmeans.predict(vector_array.reshape(1, -1))[0]
            self.cluster_assignments[cluster_id].add(id)
        else:
            # If not trained yet, add to a temporary cluster
            self.cluster_assignments[0].add(id)

        # Save changes to MongoDB
        self._save_to_mongo()
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

    def search(self, query_vector: List[float], k: int = 3) -> List[UUID]:
        """Search for similar vectors."""
        logger.info(f"Searching with IVF index")
        if not self.initialized or not self.vectors:
            raise ValueError("Index not initialized or empty")

        # Ensure model is trained if we have enough vectors
        if len(self.vectors) >= self.n_clusters and not self.cluster_centers:
            logger.info("Training model before search as it hasn't been trained yet")
            self.train()
            if not self.cluster_centers:
                logger.warning("Training failed, falling back to linear search")
                return self._linear_search(query_vector, k)

        # Convert and normalize query vector
        query_array = np.array(query_vector, dtype=np.float32)
        query_array = query_array / np.linalg.norm(query_array)

        # If not trained or training failed, use linear search
        if not self.cluster_centers:
            return self._linear_search(query_array, k)

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

    def _linear_search(self, query_array: np.ndarray, k: int) -> List[UUID]:
        """Perform linear search when clustering is not available."""
        candidates = []
        for vector_id, vector in self.vectors.items():
            sim = self._cosine_similarity(query_array, vector)
            candidates.append((vector_id, sim))

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

    def serialize(self) -> dict[str, Any]:
        """Serialize the index data for storage."""
        try:
            # Convert numpy arrays to lists for serialization
            serialized_data = {
                "vectors": {
                    str(vector_id): vector.tolist()
                    for vector_id, vector in self.vectors.items()
                },
                "cluster_centers": self.cluster_centers.tolist() if self.cluster_centers is not None else None,
                "cluster_assignments": {
                    str(cluster_id): [str(v) for v in vectors]
                    for cluster_id, vectors in self.cluster_assignments.items()
                },
                "kmeans": {
                    "cluster_centers": self.kmeans.cluster_centers_.tolist() if hasattr(self.kmeans, 'cluster_centers_') else None,
                    "labels": self.kmeans.labels_.tolist() if hasattr(self.kmeans, 'labels_') else None
                } if self.kmeans and hasattr(self.kmeans, 'cluster_centers_') else None,
                "n_clusters": self.n_clusters,
                "dimension": self.dimension,
                "max_elements": self.max_elements,
                "n_probe": self.n_probe,
                "initialized": self.initialized
            }
            return serialized_data
        except Exception as e:
            logger.error(f"Error serializing IVF index: {str(e)}")
            raise

    @classmethod
    def deserialize(cls, data: dict[str, Any]) -> 'IVFIndex':
        """Deserialize the index data from storage."""
        try:
            # Create new index instance
            index = cls(
                dimension=data["dimension"],
                max_elements=data["max_elements"],
                n_clusters=data["n_clusters"],
                n_probe=data["n_probe"]
            )

            # Restore vectors
            index.vectors = {
                UUID(vector_id): np.array(vector, dtype=np.float32)
                for vector_id, vector in data["vectors"].items()
            }

            # Restore cluster centers
            if data["cluster_centers"]:
                index.cluster_centers = np.array(data["cluster_centers"], dtype=np.float32)

            # Restore cluster assignments
            index.cluster_assignments = {
                int(cluster_id): {UUID(v) for v in vectors}
                for cluster_id, vectors in data["cluster_assignments"].items()
            }

            # Restore kmeans if it exists and was trained
            if data["kmeans"] and data["kmeans"]["cluster_centers"]:
                index.kmeans = KMeans(n_clusters=index.n_clusters)
                index.kmeans.cluster_centers_ = np.array(data["kmeans"]["cluster_centers"], dtype=np.float32)
                if data["kmeans"]["labels"] is not None:
                    index.kmeans.labels_ = np.array(data["kmeans"]["labels"])

            index.initialized = data["initialized"]
            return index
        except Exception as e:
            logger.error(f"Error deserializing IVF index: {str(e)}")
            raise

    def _save_to_mongo(self) -> None:
        """Save the index data to MongoDB."""
        if not self.mongo_client or not self.library_id:
            logger.warning("MongoDB client or library_id not set, skipping save")
            return

        try:
            db = self.mongo_client.vector_db
            collection = db.ivf_indices

            # Serialize the index data
            index_data = self.serialize()
            index_data["library_id"] = str(self.library_id)

            # Upsert the index data
            collection.update_one(
                {"library_id": str(self.library_id)},
                {"$set": index_data},
                upsert=True
            )
            logger.info(f"Saved IVF index for library {self.library_id} to MongoDB")
        except Exception as e:
            logger.error(f"Error saving IVF index to MongoDB: {str(e)}")
            raise

    def _load_from_mongo(self) -> None:
        """Load the index data from MongoDB."""
        if not self.mongo_client or not self.library_id:
            logger.warning("MongoDB client or library_id not set, skipping load")
            return

        try:
            db = self.mongo_client.vector_db
            collection = db.ivf_indices

            # Get the index data
            index_data = collection.find_one({"library_id": str(self.library_id)})
            if index_data:
                # Remove MongoDB's _id field
                index_data.pop("_id", None)

                # Deserialize the index data
                loaded_index = self.deserialize(index_data)

                # Copy the loaded data to this instance
                self.vectors = loaded_index.vectors
                self.cluster_centers = loaded_index.cluster_centers
                self.cluster_assignments = loaded_index.cluster_assignments
                self.kmeans = loaded_index.kmeans
                self.initialized = loaded_index.initialized

                logger.info(f"Loaded IVF index for library {self.library_id} from MongoDB")
        except Exception as e:
            logger.error(f"Error loading IVF index from MongoDB: {str(e)}")
            raise
