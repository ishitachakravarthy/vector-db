from uuid import UUID
from pymongo.collection import Collection
from pymongo.database import Database
import logging
from app.data_models.library import Library

logger = logging.getLogger(__name__)


class LibraryRepository:
    """Collection for libraries."""

    def __init__(self, db: Database):
        self.db = db
        self.libraries: Collection = self.db.libraries

    def get_library(self, library_id: UUID) -> Library | None:
        try:
            data = self.libraries.find_one({"_id": library_id})
            if data:
                return Library(**data)
            raise ValueError(f"Library with ID {library_id} not found")
        except Exception as e:
            raise ValueError("Library database connection failed")

    def list_libraries(self) -> list[Library]:
        try:
            return [Library(**library) for library in self.libraries.find()]
        except Exception as e:
            raise ValueError("Library database connection failed")

    def save_library(self, library: Library) -> Library:
        try:
            library_dict = library.model_dump()
            result = self.libraries.update_one(
                {"_id": library.get_library_id()},
                {"$set": library_dict},
                upsert=True,
            )
            if not (result.matched_count == 1 or result.upserted_id is not None):
                raise ValueError(
                    f"Failed to save Library with ID {library.get_library_id()} to database"
                )
            return library
        except Exception as e:
            raise ValueError("Library database connection failed") from e

    def delete_library(self, library_id: UUID) -> bool:
        try:
            result = self.libraries.delete_one({"_id": library_id})
            if result.deleted_count == 0:
                raise ValueError(f"Library with ID {library_id} not found")
            return True
        except Exception as e:
            raise ValueError("Library database connection failed") from e

    # Indexing methods
    def get_index_type(self, library_id: UUID) -> str | None:
        library = self.get_library(library_id)
        return library.index_type if library else None

    def get_index_data(self, library_id: UUID) -> dict | None:
        library = self.get_library(library_id)
        return library.index_data if library else None

    def update_index_data(self, library_id: UUID, index_data: dict) -> None:
        library = self.get_library(library_id)
        if not library:
            raise ValueError(f"Library with ID {library_id} not found")
        library.update_index_data(index_data)
        self.save_library(library)

    def update_index_type(self, library_id: UUID, index_type: str) -> None:
        library = self.get_library(library_id)
        if not library:
            raise ValueError(f"Library with ID {library_id} not found")
        library.update_index_type(index_type)
        self.save_library(library)
