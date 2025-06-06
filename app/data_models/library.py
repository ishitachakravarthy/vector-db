from uuid import UUID, uuid4
from pydantic import BaseModel, Field
from app.data_models.metadata import LibraryMetadata

class LibraryBase(BaseModel):
    title: str = Field(..., description="Title of the library")
    description:str|None = Field(None, description="Description of the library")
    index_type: str | None = Field(
        None, description="Type of index to use (flat, ivf or hnsw)"
    )

class LibraryCreate(LibraryBase):
    metadata: LibraryMetadata | None = None

class LibraryUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    index_type: str | None = None
    metadata: LibraryMetadata | None = Field(None, description="Library metadata")
    def get_title(self) -> str | None:
        return self.title
    def get_description(self) -> str | None:
        return self.description
    def get_index_type(self) -> str | None:
        return self.index_type
    def get_metadata(self) -> LibraryMetadata | None:
        return self.metadata

class LibraryResponse(LibraryBase):
    id: UUID = Field(..., description="Unique identifier for the library")
    documents: list[UUID] = Field(default_factory=list, description="List of document IDs in the library")
    metadata: LibraryMetadata | None = Field(None, description="Library metadata")
    class Config:
        from_attributes = True


class Library(BaseModel):
    """A library of documents with vector embeddings."""

    id: UUID = Field(default_factory=uuid4)
    title: str
    description: str | None = None
    index_type: str | None = None
    index_data: dict = Field(default_factory=dict)
    documents: list[UUID] = Field(default_factory=list)
    metadata: LibraryMetadata = Field(default_factory=LibraryMetadata)

    def get_library_id(self) -> UUID:
        return self.id

    def get_library_title(self) -> str:
        return self.title

    def get_library_description(self) -> str | None:
        return self.description

    def get_index_type(self) -> str | None:
        return self.index_type

    def get_index_data(self) -> dict:
        return self.index_data

    def get_all_doc_ids(self) -> list[UUID]:
        return self.documents

    def get_metadata(self) -> LibraryMetadata:
        return self.metadata

    def update_library_title(self, new_title: str) -> None:
        self.title = new_title
        self.metadata.update_timestamp()

    def update_library_description(self, new_description: str) -> None:
        self.description = new_description
        self.metadata.update_timestamp()

    def update_index_type(self, new_index_type: str) -> None:
        self.index_type = new_index_type
        self.metadata.update_timestamp()
        self.index_data = {}

    def update_index_data(self, new_index_data: dict) -> None:
        self.index_data = new_index_data
        self.metadata.update_timestamp()

    def update_metadata(self, new_metadata: LibraryMetadata) -> None:
        self.metadata = new_metadata
        self.metadata.update_timestamp()

    def add_document(self, document_id: UUID) -> None:
        if document_id not in self.documents:
            self.documents.append(document_id)
            self.metadata.update_timestamp()

    def delete_document(self, document_id: UUID) -> bool:
        if document_id in self.documents:
            self.documents.remove(document_id)
            self.metadata.update_timestamp()
            return True
        return False

    def delete_all_documents(self) -> None:
        self.documents = []
        self.metadata.update_timestamp()
