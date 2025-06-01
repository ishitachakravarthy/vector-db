from typing import Optional
from pymongo.collection import Collection
from pymongo.database import Database

class BaseRepository:
    """Base repository class that provides access to MongoDB collection."""
    
    def __init__(self, db: Database, collection_name: str):
        self.db = db
        self.collection: Collection = db[collection_name] 