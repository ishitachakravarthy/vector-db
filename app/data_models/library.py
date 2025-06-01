from uuid import UUID, uuid4
from pydantic import BaseModel, Field
import numpy as np
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any

from app.data_models.document import Document
from app.data_models.chunk import Chunk

class Library(BaseModel):
    """A library of documents with vector embeddings."""

    id: UUID = Field(default_factory=uuid4)
    title: str
    description: Optional[str] = None
    index_type: str|None = "flat"  # Default to ball tree for high-dimensional spaces
    index_data: Optional[Dict[str, Any]] = None  # Serialized index data
    documents: list[UUID] = Field(default_factory=list)

    def __init__(self, **data):
        super().__init__(**data)
        if not self.documents:
            self.documents = []
        if not self.index_data:
            self.index_data = {}

    def get_library_id(self) -> UUID:
        return self.id

    def get_library_title(self) -> str:
        return self.title

    def get_library_description(self) -> Optional[str]:
        return self.description

    def get_index_type(self) -> str:
        return self.index_type

    def get_index_data(self) -> Optional[Dict[str, Any]]:
        return self.index_data

    def get_all_doc_ids(self) -> list[UUID]:
        return self.documents

    def search_document(self, document_id: UUID) -> Document | None:
        return self.documents.get(document_id)

    def update_library_title(self, new_title: str) -> None:
        self.title = new_title

    def update_library_description(self, new_description: str) -> None:
        self.description = new_description

    def update_index_type(self, new_index_type: str) -> None:
        self.index_type = new_index_type

    def update_index_data(self, new_index_data: Dict[str, Any]) -> None:
        """Update the index data and ensure consistency."""
        self.index_data = new_index_data

    def add_document(self, document_id: UUID) -> None:
        if document_id not in self.documents:
            self.documents.append(document_id)

    def delete_document(self, document_id: UUID) -> bool:
        if document_id in self.documents:
            self.documents.remove(document_id)
            return True
        return False

    def delete_all_documents(self) -> None:
        self.documents = []

    def add_chunk(self, document: Document) -> None:
        self.documents[document.get_doc_id()] = document

    def delete_chunk(self, chunk_id: UUID) -> bool:
        document = self.documents.get(chunk_id)
        if document:
            document.delete_chunk(chunk_id)
            return True
        return False
