from uuid import UUID
from pymongo.collection import Collection
from pymongo.database import Database
import logging
from app.data_models.library import Library, LibraryUpdate

logger = logging.getLogger(__name__)


class LibraryRepository:
    """Collection for libraries."""

    def __init__(self, db: Database):
        self.db = db
        self.libraries: Collection = self.db.libraries

    async def get_library(self, library_id: UUID) -> Library | None:
        try:
            data = self.libraries.find_one({"_id": library_id})
            if not data:
                raise ValueError(f"Library with ID {library_id} not found")
            return Library(**data)
        except Exception as e:
            raise ValueError(f"Database error: Failed to retrieve library: {str(e)}")

    async def list_libraries(self) -> list[Library]:
        try:
            return [Library(**library) for library in self.libraries.find()]
        except Exception as e:
            raise ValueError(f"Database error: Failed to list libraries: {str(e)}")

    async def save_library(self, library: Library) -> Library:
        try:
            library_dict = library.model_dump()
            result = self.libraries.find_one_and_update(
                {"_id": library.id},
                {"$set": library_dict},
                upsert=True,
                return_document=True
            )
            if not result:
                raise ValueError(f"Failed to save library with ID {library.id}")
            return Library(**result)
        except Exception as e:
            raise ValueError(f"Database error: Failed to save library: {str(e)}")

    async def update_library(self, library_id: UUID, library_update: LibraryUpdate) -> Library:
        try:
            update_library = await self.get_library(library_id)
            if library_update.get_title() is not None:
                update_library.update_library_title(library_update.get_title())
            if library_update.get_description() is not None:
                update_library.update_library_description(library_update.get_description())
            if library_update.get_index_type() is not None:
                update_library.update_index_type(library_update.get_index_type())
            if library_update.get_metadata() is not None:
                update_library.update_metadata(library_update.get_metadata())
            return await self.save_library(update_library)
        except Exception as e:
            raise ValueError(f"Database error: Failed to update library: {str(e)}")

    async def delete_library(self, library_id: UUID) -> bool:
        try:
            result = self.libraries.delete_one({"_id": library_id})
            if result.deleted_count == 0:
                raise ValueError(f"Library with ID {library_id} not found")
            return True
        except Exception as e:
            raise ValueError(f"Database error: Failed to delete library: {str(e)}")

    # Indexing methods
    async def get_index_type(self, library_id: UUID) -> str | None:
        library = await self.get_library(library_id)
        return library.index_type if library else None

    async def get_index_data(self, library_id: UUID) -> dict | None:
        library = await self.get_library(library_id)
        return library.index_data if library else None

    async def update_index_data(self, library_id: UUID, index_data: dict) -> None:
        try:
            result = self.libraries.find_one_and_update(
                {"_id": library_id},
                {"$set": {"index_data": index_data}},
                return_document=True
            )
            if not result:
                raise ValueError(f"Library with ID {library_id} not found")
        except Exception as e:
            raise ValueError(f"Database error: Failed to update index data: {str(e)}")

    async def update_index_type(self, library_id: UUID, index_type: str) -> None:
        try:
            result = self.libraries.find_one_and_update(
                {"_id": library_id},
                {"$set": {"index_type": index_type}},
                return_document=True
            )
            if not result:
                raise ValueError(f"Library with ID {library_id} not found")
        except Exception as e:
            raise ValueError(f"Database error: Failed to update index type: {str(e)}")
