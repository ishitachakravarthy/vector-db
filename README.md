# Vector-Database

A vector database system for storing and managing document chunks with semantic search capabilities.

## Overview
The goal of this project is to develop a REST API that allows users to **index** and **query** their documents within a Vector Database.

A Vector Database specializes in storing and indexing vector embeddings, enabling fast retrieval and similarity searches. This capability is crucial for applications involving natural language processing, recommendation systems, and many more…

The API does the following:
1. Allow the users to create, read, update, and delete libraries.
2. Allow the users to create, read, update and delete chunks within a library.
3. Index the contents of a library.
4. Do **k-Nearest Neighbor vector search** over the selected library with a given embedding query.

## Vector Indexes

The system supports three types of vector indexes for efficient similarity search:

1. **Flat Index**
   - Exhaustive search through all vectors
   - Highest accuracy but slower for large datasets
   - Best for small to medium-sized collections

2. **HNSW (Hierarchical Navigable Small World)**
   - Approximate nearest neighbor search
   - Fast and scalable for large datasets
   - Good balance between speed and accuracy
   - Uses graph-based structure for efficient traversal

3. **Inverted File Index**
   - Clusters vectors into cells
   - Fast approximate search
   - Memory-efficient

## API Endpoints
### Libraries

- `POST /library/` - Create a new library
- `GET /library/` - List all libraries
- `GET /library/{library_id}` - Get a specific library
- `PUT /library/{library_id}` - Update a library
- `DELETE /library/{library_id}` - Delete a library

### Documents

- `POST /document/` - Create a new document
- `GET /document/` - List all documents (with optional library filter)
- `GET /document/{document_id}` - Get a specific document
- `PUT /document/{document_id}` - Update a document
- `DELETE /document/{document_id}` - Delete a document

## Data Models

### Library
- LibraryBase
- LibraryCreate
- LibraryUpdate
- LibraryResponse

### Document
- DocumentBase
- DocumentCreate
- DocumentUpdate
- DocumentResponse

### Chunk
- ChunkBase
- ChunkCreate
- ChunkUpdate
- ChunkResponse

## Setup and Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/vector-db.git
cd vector-db
```

2. Create a `.env` file:
```bash
cp .env.example .env
# Edit .env with your configuration
```
Required environment variables in `.env`:
```env
COHERE_API_KEY=""
MONGODB_URL=mongodb://mongodb:27017/
MONGODB_DB=vector_db
```
1. Build and start the containers:
```bash
docker-compose up --build
```

The API will be available at `http://localhost:8000`


### Docker Compose Services

The application uses the following services:

- **vector-db**: The main FastAPI application
- **mongodb**: MongoDB database for storing documents, chunks, and their embeddings

