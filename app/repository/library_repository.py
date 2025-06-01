from typing import List, Dict, Any, Optional
from uuid import UUID
from pymongo.collection import Collection
import logging
from app.data_models.library import Library
from app.repository.base_repository import BaseRepository

logger = logging.getLogger(__name__)

class LibraryRepository(BaseRepository):
    """Repository for managing libraries in MongoDB."""
    def __init__(self):
        super().__init__()
        self.libraries: Collection = self.db.libraries
        self.init_indexes()

    def init_indexes(self) -> None:
        """Initialize indexes for the library collection."""
        try:
            # Create only the indexes we need
            self.libraries.create_index("title")
            self.libraries.create_index("index_type")

            logger.info("Successfully initialized library indexes")
        except Exception as e:
            logger.error(f"Error initializing library indexes: {str(e)}")
            raise

    def _serialize_library(self, library: Library) -> dict:
        """Convert a Library object to a dictionary for MongoDB."""
        lib_dict = library.model_dump()
        # Ensure we're using the id as _id and remove any library_id field
        lib_dict["_id"] = lib_dict["id"]
        return lib_dict

    def create_library(self, library: Library) -> Library:
        try:
            data = self._serialize_library(library)
            result = self.libraries.insert_one(data)
            library.id = result.inserted_id
            return library
        except Exception as e:
            logger.error(f"Error creating library: {str(e)}")
            raise

    def get_library(self, library_id: UUID) -> Optional[Library]:
        """Get a library by ID."""
        try:
            data = self.libraries.find_one({"_id": library_id})
            if data:
                return Library(**data)
            return None
        except Exception as e:
            logger.error(f"Error getting library: {str(e)}")
            raise

    def list_libraries(self) -> List[Library]:
        """List all libraries."""
        try:
            libraries = []
            for data in self.libraries.find():
                libraries.append(Library(**data))
            return libraries
        except Exception as e:
            logger.error(f"Error listing libraries: {str(e)}")
            raise

    def save_library(self, library: Library) -> Library:
        """Save or update a library in MongoDB."""
        try:
            library_dict = self._serialize_library(library)
            # Use upsert to create if not exists, update if exists
            result = self.libraries.update_one(
                {"_id": library_dict["_id"]}, 
                {"$set": library_dict}, 
                upsert=True
            )
            logger.info(f"Saved library with ID: {library.id}")
            return library
        except Exception as e:
            logger.error(f"Error saving library: {str(e)}")
            raise

    def delete_library(self, library_id: UUID) -> bool:
        """Delete a library."""
        try:
            result = self.libraries.delete_one({"_id": library_id})
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"Error deleting library: {str(e)}")
            raise

    def update_index_type(self, library_id: UUID, index_type: str) -> None:
        """Update the index type for a library."""
        try:
            self.libraries.update_one(
                {"_id": library_id},
                {"$set": {"index_type": index_type}}
            )
        except Exception as e:
            logger.error(f"Error updating library index type: {str(e)}")
            raise

    def get_index_type(self, library_id: UUID) -> Optional[str]:
        """Get the index type for a library."""
        try:
            library = self.libraries.find_one(
                {"_id": library_id},
                {"index_type": 1}
            )
            return library.get("index_type") if library else None
        except Exception as e:
            logger.error(f"Error getting library index type: {str(e)}")
            raise

    def save_index_data(self, library_id: UUID, index_data: Dict[str, Any]) -> None:
        """Save serialized index data in the library document."""
        try:
            self.libraries.update_one(
                {"_id": library_id},
                {"$set": {"index_data": index_data}}
            )
        except Exception as e:
            logger.error(f"Error saving index data for library {library_id}: {str(e)}")
            raise

    def get_index_data(self, library_id: UUID) -> Optional[Dict[str, Any]]:
        """Get serialized index data from the library document."""
        try:
            library = self.libraries.find_one(
                {"_id": library_id},
                {"index_data": 1}
            )
            return library.get("index_data") if library else None
        except Exception as e:
            logger.error(f"Error getting index data for library {library_id}: {str(e)}")
            return None

    def get_library_vectors(self, library_id: UUID) -> Dict[UUID, List[float]]:
        """Get all vectors for a library."""
        try:
            library = self.get_library(library_id)
            if not library:
                return {}

            # Get all chunks in the library
            chunks = self.db.chunks.find({"_id": library_id})

            # Extract vectors
            vectors = {}
            for chunk in chunks:
                if "embedding" in chunk and chunk["embedding"]:
                    vectors[chunk["_id"]] = chunk["embedding"]

            return vectors

        except Exception as e:
            logger.error(f"Error getting vectors for library {library_id}: {str(e)}")
            return {}
