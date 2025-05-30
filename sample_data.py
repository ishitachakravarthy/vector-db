from app.repository.mongo_repository import MongoRepository
from app.services.library_service import LibraryService
from app.data_models.library import Library
from app.data_models.document import Document
from app.data_models.chunk import Chunk
from app.data_models.metadata import ChunkMetadata
from uuid import uuid4
import logging
from datetime import datetime, timezone
import uuid

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_sample_data():
    try:
        repo = MongoRepository()
        service = LibraryService(repo)
        logger.info("Repository and service initialized")

        library = Library(
            id=uuid4(),
            title="Sample Library",
        )
        library = service.create_library(library)
        logger.info(f"Created library with ID: {library.get_library_id()}")

        # Create a document
        document = Document(
            id=uuid4(),
            title="Sample Document",
        )
        logger.info(f"Created document with ID: {document.id}")

        # Create some chunks
        chunk1 = Chunk(
            id=uuid4(),
            text="This is the first chunk of text. It contains some sample content.",
            metadata=ChunkMetadata(
                section="Introduction",
                order=1,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc)
            )
        )

        chunk2 = Chunk(
            id=uuid4(),
            text="This is the second chunk. It has different content for testing.",
            metadata=ChunkMetadata(
                section="Body",
                order=2,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc)
            )
        )
        logger.info(f"Created chunks with IDs: {chunk1.id}, {chunk2.id}")

        # TODO Move to service layer
        # Add chunks to document
        document.add_chunk(chunk1)
        document.add_chunk(chunk2)
        library.add_document(document)
        logger.info("Added document and chunks to library")

        # Save library
        service.save_library(library)
        logger.info("Saved library to database")

        # Verify data was inserted
        libraries = service.list_libraries()
        logger.info(f"Found {len(libraries)} libraries in database")
        if libraries:
            library = libraries[0]
            logger.info(f"Library has {len(library.get_all_docs())} documents")

    except Exception as e:
        logger.error(f"Error creating sample data: {str(e)}", exc_info=True)
        raise

if __name__ == "__main__":
    create_sample_data() 
