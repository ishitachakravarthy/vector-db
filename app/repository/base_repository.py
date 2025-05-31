from typing import Optional
from pymongo import MongoClient
from pymongo.database import Database
from app.config import MONGODB_URL, MONGODB_DB_NAME
import logging

logger = logging.getLogger(__name__)

class BaseRepository:
    """Base repository class that handles MongoDB connection."""
    
    def __init__(self):
        self.client: Optional[MongoClient] = None
        self.db: Optional[Database] = None
        self._connect()
        
    def _connect(self) -> None:
        """Connect to MongoDB."""
        if not self.client:
            # Configure MongoDB to use standard UUID representation
            self.client = MongoClient(MONGODB_URL, uuidRepresentation="standard")
            self.db = self.client[MONGODB_DB_NAME]
            logger.info("Connected to MongoDB")
            
    def close(self) -> None:
        """Close the MongoDB connection."""
        if self.client:
            self.client.close()
            self.client = None
            self.db = None
            logger.info("Closed MongoDB connection") 