from uuid import UUID, uuid4
from pydantic import BaseModel, Field
import numpy as np
from datetime import datetime, timezone

from app.data_models.document import Document
from app.data_models.chunk import Chunk

class Library(BaseModel):
    """A library containing multiple documents and their chunks."""
    id: UUID = Field(default_factory=uuid4)
    title: str
    documents: dict[UUID, Document] = Field(default_factory=dict)

    def __init__(self, **data):
        super().__init__(**data)
        if not self.documents:
            self.documents = {}

    def get_library_id(self) -> UUID:
        return self.id

    def get_library_title(self) -> str:
        return self.title

    def get_all_docs(self) -> list[Document]:
        return list(self.documents.values())

    def search_document(self, document_id: UUID) -> Document | None:
        return self.documents.get(document_id)

    def update_library_title(self, new_library_title: str) -> None:
        self.title = new_library_title

    def add_document(self, document: Document) -> None:
        self.documents[document.get_doc_id()] = document

    def delete_document(self, document_id: UUID) -> bool:
        return self.documents.pop(document_id, None) is not None

    def delete_all_documents(self) -> None:
        self.documents = {}

    def add_chunk(self, document: Document) -> None:
        self.documents[document.get_doc_id()] = document

    def delete_chunk(self, chunk_id: UUID) -> bool:
        document = self.documents.get(chunk_id)
        if document:
            document.delete_chunk(chunk_id)
            return True
        return False
