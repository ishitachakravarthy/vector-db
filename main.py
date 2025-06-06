from fastapi import FastAPI
import cohere
from app.api_layer.search_routes import search_router
from app.api_layer.library_routes import library_router
from app.api_layer.document_routes import document_router
from app.api_layer.chunk_routes import chunk_router

app = FastAPI(
    title="Vector Database API",
    description="A REST API for managing libraries, documents, and chunks with vector search capabilities",
)

co = cohere.Client("A1Fi5KBBNoekwBPIa833CBScs6Z2mHEtOXxr52KO")
app.include_router(search_router, tags=["Search"])

app.include_router(document_router, tags=["Document"])
app.include_router(library_router, tags=["Library"])
app.include_router(chunk_router, tags=["Chunk"])
