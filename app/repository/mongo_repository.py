from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime, timezone
from pymongo import MongoClient
from pymongo.database import Database
from pymongo.collection import Collection
from bson import Binary
import uuid
import logging
from app.data_models.library import Library
from app.data_models.document import Document

logger = logging.getLogger(__name__)

class MongoRepository:
    def __init__(self):
        self.client: MongoClient = None
        self.db: Database = None
        self.libraries: Collection = None
        self.documents: Collection = None
        self.vectors: Collection = None
        self._connect()

    def _connect(self) -> None:
        """Connect to MongoDB."""
        try:
            # Configure MongoDB to use UUID representation
            self.client = MongoClient('mongodb://localhost:27017/', uuidRepresentation='standard')
            self.db = self.client['vector_db']
            self.libraries = self.db.libraries
            self.documents = self.db.documents
            self.vectors = self.db.vectors
            logger.info("Connected to MongoDB")
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {str(e)}")
            raise

    def _serialize_document(self, document: Document) -> dict:
        """Convert a Document object to a dictionary for MongoDB."""
        doc_dict = document.model_dump()
        doc_dict['id'] = str(doc_dict['id'])
        if 'chunks' in doc_dict:
            doc_dict['chunks'] = {str(k): v.model_dump() for k, v in document.chunks.items()}
        return doc_dict

    def _serialize_library(self, library: Library) -> dict:
        """Convert a Library object to a dictionary for MongoDB."""
        lib_dict = library.model_dump()
        # Keep id field and use it as _id
        lib_dict['_id'] = str(lib_dict['id'])
        if 'documents' in lib_dict:
            lib_dict['documents'] = [str(doc_id) for doc_id in library.documents]
        return lib_dict

    def create_library(self, library: Library) -> Library:
        try:
            data = self._serialize_library(library)
            result = self.libraries.insert_one(data)
            # Update library with MongoDB's _id
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
                if 'documents' in data:
                    # Convert string UUIDs to UUID objects
                    data['documents'] = [UUID(str(doc_id)) for doc_id in data['documents']]
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
                if 'documents' in data:
                    # Extract UUID string from "UUID('...')" format
                    data['documents'] = [
                        uuid.UUID(doc_id.split("'")[1]) for doc_id in data['documents']
                    ]
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
                {"_id": library.id},
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

    def save_vector(self, chunk_id: UUID, embedding: List[float]) -> None:
        """Save a vector embedding for a chunk."""
        vector_dict = {
            '_id': str(chunk_id),
            'embedding': embedding,
            'created_at': datetime.now(timezone.utc),
            'updated_at': datetime.now(timezone.utc)
        }
        self.vectors.update_one(
            {'_id': str(chunk_id)},
            {'$set': vector_dict},
            upsert=True
        )

    def get_vector(self, chunk_id: UUID) -> Optional[List[float]]:
        """Get a vector embedding for a chunk."""
        vector_dict = self.vectors.find_one({'_id': str(chunk_id)})
        if vector_dict:
            return vector_dict['embedding']
        return None

    def delete_vector(self, chunk_id: UUID) -> bool:
        """Delete a vector embedding for a chunk."""
        result = self.vectors.delete_one({'_id': str(chunk_id)})
        return result.deleted_count > 0
