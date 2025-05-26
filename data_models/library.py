from uuid import UUID, uuid4
from pydantic import BaseModel, Field
import numpy as np

from data_models.document import Document
from data_models.chunk import Chunk
from data_models.metadata import LibraryMetadata

class Library(BaseModel):
    """A library containing multiple documents and their chunks."""
    id: UUID = Field(default_factory=uuid4)
    name: str
    description: str | None = None
    documents: dict[UUID, Document] = Field(default_factory=dict)
    metadata: LibraryMetadata

    def __init__(self, **data):
        super().__init__(**data)
        if not self.documents:
            self.documents = {}

    def add_document(self, document: Document) -> None:
        """Add a new document to the library."""
        self.documents[document.id] = document
    
    def get_document(self, document_id: UUID) -> Document | None:
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

    def search_similar_chunks(self, query_vector: list[float], k: int = 5) -> list[tuple[Chunk, float, Document]]:
        """Find k nearest chunks to the query vector using Euclidean distance."""
        if not query_vector:
            return []
            
        # Collect all chunks with their vectors
        chunks_with_vectors = []
        for doc in self.documents.values():
            for chunk in doc.chunks:
                if chunk.vector is not None:
                    chunks_with_vectors.append((chunk, chunk.vector, doc))
        
        if not chunks_with_vectors:
            return []
            
        # Calculate distances for each chunk using numpy
        query_array = np.array(query_vector)
        distances = []
        for chunk, vec, doc in chunks_with_vectors:
            distance = np.sqrt(np.sum((query_array - np.array(vec)) ** 2))
            distances.append((distance, chunk, doc))
        
        distances.sort(key=lambda x: x[0])  # Sort by distance (ascending)
        results = [(chunk, dist, doc) for dist, chunk, doc in distances[:k]]
            
        return results
    