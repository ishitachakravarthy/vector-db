from typing import List, Optional
from uuid import UUID
from datetime import datetime, timezone

from app.data_models.library import Library
from app.repository.mongo_repository import MongoRepository

class LibraryService:
    def __init__(self, repository: MongoRepository):
        self.repository = repository

    def create_library(self, library: Library) -> Library:
        library.metadata.created_at = datetime.now(timezone.utc)
        library.metadata.updated_at = datetime.now(timezone.utc)
        return self.repository.insert_library(library)

    def list_libraries(self) -> List[Library]:
        return self.repository.find_all_libraries()
