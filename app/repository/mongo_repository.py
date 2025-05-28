from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database
from typing import Any, Dict
from datetime import datetime, timezone
import logging

from app.data_models.library import Library
from app.data_models.metadata import LibraryMetadata

# Configure MongoDB logging
logging.getLogger('pymongo').setLevel(logging.WARNING)

class MongoRepository:
    def __init__(self, uri: str = "mongodb://mongodb:27017", db_name: str = "vector-db"):
        self.client = MongoClient(uri)
        self.db: Database = self.client[db_name]

        # Ensure collections exist
        if "libraries" not in self.db.list_collection_names():
            self.db.create_collection("libraries")

        self.libraries: Collection = self.db["libraries"]

    def _convert_metadata(self, data: Dict[str, Any], metadata_type: type) -> Dict[str, Any]:
        if not data: return data
        metadata = data["metadata"]
        if isinstance(metadata, dict):
            metadata["created_at"] = datetime.fromisoformat(metadata["created_at"]).replace(tzinfo=timezone.utc)
            metadata["updated_at"] = datetime.fromisoformat(metadata["updated_at"]).replace(tzinfo=timezone.utc)
            data["metadata"] = metadata_type(**metadata)
        return data

    def _convert_to_library(self, data: Dict[str, Any]) -> Library:
        """Convert MongoDB document to Library model."""
        if not data: return None
        data = self._convert_metadata(data, LibraryMetadata)
        return Library(**data)

    def find_all_libraries(self) -> list[Library]:
        """Find all libraries in the database."""
        all_libraries = self.libraries.find()
        return [self._convert_to_library(library) for library in all_libraries]
