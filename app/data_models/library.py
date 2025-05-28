from uuid import UUID, uuid4
from pydantic import BaseModel, Field
import numpy as np
from datetime import datetime,UTC


from data_models.document import Document
from data_models.metadata import LibraryMetadata

class Library(BaseModel):
    """A library containing multiple documents and their chunks."""
    id: UUID = Field(default_factory=uuid4)
    title: str
    documents: list[Document] = Field(default_factory=list)
    metadata: LibraryMetadata

    def __init__(self, **data):
        super().__init__(**data)
        if not self.documents:
            self.documents = []

    def _update_timestamp(self) -> None:
        """Helper method to update the metadata timestamp."""
        self.metadata.updated_at = datetime.now(UTC)

    def get_library_id(self) -> UUID:
        return self.id

    def get_library_title(self) -> str:
        return self.title

    def get_all_docs(self) -> list[Document]:
        return self.documents

    def search_document(self, document_id: UUID) -> Document | None:
        for document in self.documents:
            if document.get_doc_id() == document_id:
                return document
        return None

    def update_library_title(self, new_library_title: str) -> None:
        self.title = new_library_title
        self._update_timestamp()

    def update_metadata(self, new_metadata: LibraryMetadata):
        self.metadata = new_metadata
        self._update_timestamp()

    def add_document(self, document: Document) -> None:
        self.documents.append(document)
        self._update_timestamp()

    def delete_document(self, document_id: UUID) -> bool:
        for i, document in enumerate(self.documents):
            if document.get_doc_id() == document_id:
                self.documents.pop(i)
                self._update_timestamp()
                return True
        return False

    def delete_all_documents(self) -> None:
        self.documents = []
        self._update_timestamp()

    def add_chunk(self, document: Document) -> None:
        self.documents.append(document)
        self._update_timestamp()

    def delete_chunk(self, chunk_id: UUID) -> bool:
        for i, document in enumerate(self.documents):
            chunk_delete=document.delete_chunk(chunk_id)
            if chunk_delete: return True
        return False
