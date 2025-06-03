from pymongo.collection import Collection
from pymongo.database import Database

class BaseRepository:
    """Base repository that provides access to MongoDB."""
    
    def __init__(self, db: Database, collection_name: str):
        self.db = db
        self.collection: Collection = db[collection_name] 

