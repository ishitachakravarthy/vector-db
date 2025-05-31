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

    def _serialize_library(self, library: Library) -> dict:
        """Convert a Library object to a dictionary for MongoDB."""
        lib_dict = library.model_dump()
        lib_dict["_id"] = lib_dict["id"]
        return lib_dict

    def create_library(self, library: Library) -> Library:
        try:
            data = self._serialize_library(library)
            print('c')
            result = self.libraries.insert_one(data)
            library.id = result.inserted_id
            return library
        except Exception as e:
            logger.error(f"Error creating library: {str(e)}")
            raise

    def get_library(self, library_id: UUID) -> Library|None:
        """Get a library by ID."""
        try:
            data = self.libraries.find_one({"_id": library_id})
            if data:
                return Library(**data)
            return None
        except Exception as e:
            logger.error(f"Error getting library: {str(e)}")
            raise

    def list_libraries(self) -> list[Library]:
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
                {"_id": library_dict["_id"]}, {"$set": library_dict}, upsert=True
            )

            logger.info(f"Saved library with ID: {library.get_library_id()}")
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
