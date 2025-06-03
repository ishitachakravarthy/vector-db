from pymongo import MongoClient
from pymongo.database import Database
import logging
from app.config import MONGODB_URL, MONGODB_DB_NAME
from app.repository.library_repository import LibraryRepository
from app.repository.document_repository import DocumentRepository
from app.repository.chunk_repository import ChunkRepository

logger = logging.getLogger(__name__)


class MongoRepository:
    """Main repository class that coordinates all other repositories."""

    def __init__(self):
        self.client: MongoClient = None
        self.db: Database = None
        self._connect()

        # Initialize sub-repositories
        self.library_repo = LibraryRepository(self.db, "libraries")
        self.document_repo = DocumentRepository(self.db, "documents")
        self.chunk_repo = ChunkRepository(self.db, "chunks")

    def _connect(self) -> None:
        try:
            self.client = MongoClient(MONGODB_URL, uuidRepresentation="standard")
            self.db = self.client[MONGODB_DB_NAME]
            logger.info("Connected to MongoDB")
        except Exception as e:
            logger.error(f"Error connecting to MongoDB: {str(e)}")
            raise

    def close(self) -> None:
        if self.client:
            self.client.close()
            self.client = None
            self.db = None
            logger.info("Closed MongoDB connection")
