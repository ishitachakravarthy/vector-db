from pydantic import BaseModel, Field
from uuid import UUID

class SearchQuery(BaseModel):
    """Model for search query."""
    library_id: UUID = Field(..., description="Search library ID")
    query: str = Field(..., description="Search query text")
    k: int = Field(default=10, description="Number of results to return")