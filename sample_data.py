from app.repository.mongo_repository import MongoRepository
from app.services.library_service import LibraryService
from app.services.chunk_service import ChunkService
from app.services.document_service import DocumentService
from app.services.index_service import IndexService
from app.data_models.library import Library
from app.data_models.document import Document
from app.data_models.chunk import Chunk
from app.data_models.metadata import ChunkMetadata
from uuid import uuid4
import logging
from datetime import datetime, timezone
import uuid
import numpy as np
from typing import List
import cohere
from app.config import co

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def generate_query_embedding(text: str) -> List[float]:
    """Generate embedding for search query using Cohere's API."""
    try:
        logger.info(f"Generating query embedding for: {text[:100]}...")
        
        response = co.embed(
            texts=[text],
            model="embed-english-v3.0",
            input_type="search_document",  # Match the input type used for chunks
        )
        
        if response and response.embeddings:
            embedding = response.embeddings[0]
            logger.info(f"Successfully generated query embedding with dimension {len(embedding)}")
            return embedding
        else:
            logger.error("No embedding generated from Cohere API")
            return None
    except Exception as e:
        logger.error(f"Unexpected error generating query embedding: {str(e)}")
        return None


def create_sample_data():
    """Create sample data for testing."""
    try:
        repo = MongoRepository()
        library_service = LibraryService(repo)
        index_service = IndexService(repo)
        document_service = DocumentService(repo)
        chunk_service = ChunkService(repo)
        logger.info("Repository and services initialized")

        # Create a library
        library = Library(
            title="Sample Library",
            description="A library for testing",
            index_type="flat"  # Explicitly set index type to flat
        )
        library = library_service.create_library(library)

        # Initialize flat index for the library
        index_service.initialize_index(library.id, "flat")

        # Create a document
        document = Document(
            library_id=library.id,
            title="Sample Document"
        )
        document = document_service.create_document(document)

        # Create chunks with related content
        chunks = [
            "Machine learning is a subset of artificial intelligence that focuses on developing systems that can learn from data.",
            "Deep learning is a type of machine learning that uses neural networks with multiple layers to process complex patterns.",
            "Natural language processing is a field of AI that helps computers understand and process human language.",
            "Computer vision is another important area of AI that enables machines to interpret and understand visual information.",
            "Reinforcement learning is a type of machine learning where agents learn to make decisions by receiving rewards or penalties."
        ]

        # Create chunks and add their vectors to the index
        for i, text in enumerate(chunks):
            chunk = Chunk(
                document_id=document.id,
                text=text,
                metadata=ChunkMetadata(
                    section="Body",
                    order=i,
                    created_at=datetime.now(timezone.utc),
                    updated_at=datetime.now(timezone.utc)
                )
            )
            # The Chunk model will automatically generate the embedding
            chunk = chunk_service.create_chunk(chunk)

            # Add vector to index using the chunk's embedding
            try:
                index_service.add_vector(library.id, chunk.id, chunk.embedding)
            except Exception as e:
                logger.error(f"Error adding vector to flat index: {str(e)}")

        # Get index stats before search
        stats = index_service.get_index_stats(library.id)
        logger.info(f"Flat index stats before search: {stats}")

        # Perform a search
        query_text = "Reinforcement learning is a type of machine learning where agents learn to make decisions by receiving rewards or penalties."
        logger.info(f"Searching for: {query_text}")

        # Generate embedding for the query
        query_embedding = generate_query_embedding(query_text)
        if query_embedding is None:
            logger.error("Failed to generate query embedding")
            return

        logger.info(f"Generated query embedding with dimension {len(query_embedding)}")

        # Search for similar vectors using flat index
        try:
            results = index_service.search_vectors(library.id, query_embedding, k=3)
            if not results:
                logger.warning("No results found")

                stats = index_service.get_index_stats(library.id)
                logger.info(f"Flat index stats after search: {stats}")
            else:
                for i, result_id in enumerate(results):
                    chunk = chunk_service.get_chunk(result_id)
                    if chunk:
                        logger.info(f"Result {i + 1}: {chunk.text}")

        except Exception as e:
            logger.error(f"Error during flat index search: {str(e)}")

    except Exception as e:
        logger.error(f"Error creating sample data: {str(e)}")
        raise

if __name__ == "__main__":
    create_sample_data() 
