from typing import List, Optional, Dict
from uuid import UUID, uuid4
from pydantic import BaseModel, Field

from data_models.document import Document
from data_models.chunk import Chunk
from data_models.metadata import LibraryMetadata

class Library(BaseModel):
    """A library containing multiple documents and their chunks."""
    id: UUID = Field(default_factory=uuid4)
    name: str
    description: Optional[str] = None
    documents: Dict[UUID, Document] = Field(default_factory=dict)
    metadata: LibraryMetadata

    def __init__(self, **data):
        super().__init__(**data)
        if not self.documents:
            self.documents = {}

    def add_document(self, document: Document) -> None:
        """Add a new document to the library."""
        self.documents[document.id] = document
    
    def get_document(self, document_id: UUID) -> Optional[Document]:
        """Get a document by its ID."""
        return self.documents.get(document_id)
    
    def update_document_title(self, document_id: UUID, title: str) -> bool:
        """Update a document's title."""
        document = self.get_document(document_id)
        if document is not None:
            document.title = title
            return True
        return False
    
    def delete_document(self, document_id: UUID) -> bool:
        """Delete a document from the library."""
        if document_id in self.documents:
            del self.documents[document_id]
            return True
        return False
    