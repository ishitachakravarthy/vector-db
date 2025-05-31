from app.repository.library_repository import LibraryRepository
from app.repository.document_repository import DocumentRepository
from app.repository.vector_repository import VectorRepository
import logging

logger = logging.getLogger(__name__)

class MongoRepository:
    """Main repository class that coordinates all other repositories."""
    
    def __init__(self):
        # Initialize all repositories
        self.library_repo = LibraryRepository()
        self.document_repo = DocumentRepository()
        self.vector_repo = VectorRepository()
        # self.index_repo = IndexRepository()
        
    def close(self) -> None:
        """Close all repository connections."""
        # Close all repository connections
        self.library_repo.close()
        self.document_repo.close()
        self.vector_repo.close()
        # self.index_repo.close()

   