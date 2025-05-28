from pydantic import BaseModel, Field
from uuid import UUID, uuid4
from datetime import datetime, timezone


from app.data_models.chunk import Chunk
from data_models.metadata import DocumentMetadata

class Document(BaseModel):
    """A document containing multiple chunks of text."""
    id: UUID = Field(default_factory=uuid4)
    title: str
    chunks: list[Chunk] = Field(default_factory=list)
    metadata: DocumentMetadata

    def __init__(self, **data):
        super().__init__(**data)
        if not self.chunks:
            self.chunks = []

    def _update_timestamp(self) -> None:
        """Helper method to update the metadata timestamp."""
        self.metadata.updated_at = datetime.now(timezone.utc)

    def get_doc_id(self) -> UUID:
        return self.id

    def get_doc_title(self)->str:
        return self.title

    def get_all_chunks(self) -> list[Chunk]:
        return self.chunks

    def search_chunk(self, chunk_id: UUID) -> Chunk | None:
        for chunk in self.chunks:
            if chunk.get_chunk_id() == chunk_id:
                return chunk
        return None

    def update_doc_title(self, new_doc_title:str)->None:
        self.title = new_doc_title
        self._update_timestamp()

    def add_chunk(self, chunk: Chunk) -> None:
        self.chunks.append(chunk)
        self._update_timestamp()

    def delete_chunk(self, chunk_id: UUID) -> bool:
        for i, chunk in enumerate(self.chunks):
            if chunk.id == chunk_id:
                self.chunks.pop(i)
                self._update_timestamp()
                return True
        return False

    def update_metadata(self, new_metadata: DocumentMetadata):
        self.metadata = new_metadata
        self._update_timestamp()

    def delete_all_chunks(self)->None:
        self.chunks=[]
        self._update_timestamp()
