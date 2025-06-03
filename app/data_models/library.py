from uuid import UUID, uuid4
from pydantic import BaseModel, Field


class Library(BaseModel):
    """A library of documents with vector embeddings."""

    id: UUID = Field(default_factory=uuid4)
    title: str
    description: str | None = None
    index_type: str | None = None
    index_data: dict | None = None
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

    def get_library_description(self) -> str | None:
        return self.description

    def get_index_type(self) -> str | None:
        return self.index_type

    def get_index_data(self) -> dict | None:
        return self.index_data

    def get_all_doc_ids(self) -> list[UUID]:
        return self.documents

    def update_library_title(self, new_title: str) -> None:
        self.title = new_title

    def update_library_description(self, new_description: str) -> None:
        self.description = new_description

    def update_index_type(self, new_index_type: str) -> None:
        self.index_type = new_index_type
        # TODO some operation on reset index data

    def update_index_data(self, new_index_data: dict) -> None:
        self.index_data = new_index_data

    def add_document(self, document_id: UUID) -> None:
        if document_id not in self.documents:
            self.documents.append(document_id)

    def delete_document(self, document_id: UUID) -> bool:
        if document_id in self.documents:
            self.chunks.remove(document_id)
            return True
        return False

    def delete_all_documents(self) -> None:
        self.documents = []
